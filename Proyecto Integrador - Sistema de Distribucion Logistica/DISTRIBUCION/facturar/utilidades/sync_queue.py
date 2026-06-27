"""
Código Crítico - Tercer Semestre Año 2026
Cola de sincronización persistente para Turso
"""

import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from db.db_manager import obtener_conexion
from utilidades.central_sync import _pipeline_turso, _escape, _log_sync


class SyncQueue:
    def __init__(self):
        self.conn = obtener_conexion()
        self._crear_tablas()
        self._procesador_activo = False
        self._thread = None

    def _crear_tablas(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                args TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                retries INTEGER DEFAULT 0,
                last_error TEXT,
                next_retry TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_log_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                args TEXT,
                success BOOLEAN,
                error TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_queue_next_retry 
            ON sync_queue(next_retry)
        """)
        self.conn.commit()

    def agregar(self, query: str, args: List = None):
        next_retry = datetime.now().isoformat()
        self.conn.execute("""
            INSERT INTO sync_queue (query, args, next_retry)
            VALUES (?, ?, ?)
        """, (query, json.dumps(args) if args else None, next_retry))
        self.conn.commit()
        _log_sync(f"📦 Operación encolada: {query[:80]}", "WARNING")

    def _build_query(self, query: str, args: List) -> str:
        if not args:
            return query
        parts = query.split("?")
        if len(parts) - 1 != len(args):
            return query
        full_query = parts[0]
        for i, val in enumerate(args):
            full_query += _escape(val) + parts[i + 1]
        return full_query

    def procesar_pendientes(self, max_retries: int = 5, backoff_seconds: int = 60):
        ahora = datetime.now().isoformat()
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM sync_queue 
            WHERE next_retry <= ? 
            ORDER BY created_at ASC
        """, (ahora,))

        pendientes = cur.fetchall()
        exitosos = 0
        fallidos = 0

        for pend in pendientes:
            query = pend["query"]
            args = json.loads(pend["args"]) if pend["args"] else None
            retries = pend["retries"]
            full_query = self._build_query(query, args)

            resultado = _pipeline_turso([
                {"type": "execute", "stmt": {"sql": full_query}},
                {"type": "close"}
            ])

            ok = resultado and not resultado.get("results", [{}])[0].get("error")

            if ok:
                self.conn.execute("DELETE FROM sync_queue WHERE id = ?", (pend["id"],))
                self.conn.execute(
                    "INSERT INTO sync_log_history (query, args, success) VALUES (?, ?, 1)",
                    (query, json.dumps(args) if args else None)
                )
                exitosos += 1
                _log_sync(f"✅ Pendiente sincronizado: {query[:80]}")
            else:
                error_msg = resultado.get("results", [{}])[0].get("error", "Error desconocido")
                nuevo_retries = retries + 1

                if nuevo_retries >= max_retries:
                    self.conn.execute("DELETE FROM sync_queue WHERE id = ?", (pend["id"],))
                    self.conn.execute(
                        "INSERT INTO sync_log_history (query, args, success, error) VALUES (?, ?, 0, ?)",
                        (query, json.dumps(args) if args else None, f"Max retries: {error_msg}")
                    )
                    fallidos += 1
                    _log_sync(f"❌ Falló permanentemente: {query[:80]}", "ERROR")
                else:
                    delay = backoff_seconds * (2 ** retries)
                    next_retry = (datetime.now() + timedelta(seconds=delay)).isoformat()
                    self.conn.execute("""
                        UPDATE sync_queue 
                        SET retries = ?, last_error = ?, next_retry = ?
                        WHERE id = ?
                    """, (nuevo_retries, error_msg, next_retry, pend["id"]))
                    fallidos += 1
                    _log_sync(f"⚠️ Reintento {nuevo_retries}/{max_retries} en {delay}s", "WARNING")

        self.conn.commit()
        return exitosos, fallidos

    def procesar_en_background(self, intervalo: int = 30):
        if self._procesador_activo:
            return
        self._procesador_activo = True

        def _loop():
            while self._procesador_activo:
                try:
                    self.procesar_pendientes()
                except Exception as e:
                    _log_sync(f"Error en procesador de cola: {e}", "ERROR")
                time.sleep(intervalo)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
        _log_sync("🔄 Procesador de cola iniciado")

    def detener(self):
        self._procesador_activo = False
        if self._thread:
            self._thread.join(timeout=5)
            