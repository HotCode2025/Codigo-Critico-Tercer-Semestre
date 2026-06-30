"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 4.5: Cola de Sincronización Persistente
==================================================
📌 USO: Cola para sincronización asíncrona con reintentos
📌 CARACTERÍSTICAS:
    - Persistencia en SQLite
    - Reintentos con backoff exponencial
    - Procesamiento en background
    - Log de operaciones
    - ✅ SIN columna priority
    - ✅ Thread-safe con conexiones por hilo
"""

from datetime import datetime
import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable

# ✅ Importar desde sync_utils
from utilidades.sync_utils import log_sync, get_turso_client


class SyncQueue:
    """
    Cola de sincronización persistente con reintentos.
    ✅ Thread-safe con conexiones independientes por hilo.
    """
    
    def __init__(self, db_path: str = None):
        """
        Inicializa la cola de sincronización.
        
        Args:
            db_path: Ruta a la base de datos (usa la principal por defecto)
        """
        self.db_path = db_path
        self._local = threading.local()  # ✅ Conexión por hilo
        self._crear_tablas()
        self._procesador_activo = False
        self._thread = None
        self._listeners: List[Callable] = []
    
    def _get_conn(self) -> sqlite3.Connection:
        """
        ✅ Obtiene una conexión específica para el hilo actual.
        Cada hilo tiene su propia conexión para evitar errores de SQLite.
        """
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            if self.db_path:
                self._local.conn = sqlite3.connect(self.db_path)
            else:
                from db.db_manager import obtener_conexion
                self._local.conn = obtener_conexion()
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA foreign_keys = ON")
        return self._local.conn
    
    def _crear_tablas(self):
        """✅ Crea las tablas necesarias para la cola (sin columna priority)."""
        conn = self._get_conn()
        
        # ✅ Tabla principal SIN columna priority
        conn.execute("""
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
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_queue_next_retry 
            ON sync_queue(next_retry)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_queue_created 
            ON sync_queue(created_at)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_log_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                args TEXT,
                success BOOLEAN,
                error TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_log_history_timestamp 
            ON sync_log_history(timestamp DESC)
        """)
        conn.commit()
    
    def agregar(self, query: str, args: List = None):
        """
        ✅ Agrega una operación a la cola.
        
        Args:
            query: Consulta SQL con ? como placeholders
            args: Lista de argumentos para la consulta
        """
        conn = self._get_conn()
        next_retry = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO sync_queue (query, args, next_retry)
            VALUES (?, ?, ?)
        """, (query, json.dumps(args) if args else None, next_retry))
        conn.commit()
        
        self._notificar('operacion_agregada', {
            'query': query[:100]
        })
        
        log_sync(f"📦 Operación encolada: {query[:80]}...", "WARNING")
    
    def agregar_muchas(self, operaciones: List[Dict[str, Any]]):
        """✅ Agrega múltiples operaciones a la cola."""
        if not operaciones:
            return
        
        conn = self._get_conn()
        ahora = datetime.now().isoformat()
        valores = []
        for op in operaciones:
            query = op.get('query')
            args = op.get('args')
            valores.append((query, json.dumps(args) if args else None, ahora))
        
        conn.executemany("""
            INSERT INTO sync_queue (query, args, next_retry)
            VALUES (?, ?, ?)
        """, valores)
        conn.commit()
        
        log_sync(f"📦 {len(operaciones)} operaciones encoladas", "WARNING")
    
    def contar_pendientes(self) -> int:
        """✅ Cuenta las operaciones pendientes."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sync_queue")
        return cur.fetchone()[0]
    
    def procesar_pendientes(self, max_retries: int = 5, 
                            backoff_seconds: int = 60,
                            batch_size: int = 50) -> Dict[str, int]:
        """
        ✅ Procesa las operaciones pendientes en la cola.
        """
        conn = self._get_conn()
        ahora = datetime.now().isoformat()
        cur = conn.cursor()
        
        # ✅ Obtener operaciones pendientes (ordenadas por fecha)
        cur.execute("""
            SELECT * FROM sync_queue 
            WHERE next_retry <= ? 
            ORDER BY created_at ASC
            LIMIT ?
        """, (ahora, batch_size))
        
        pendientes = cur.fetchall()
        
        if not pendientes:
            return {'success': 0, 'failed': 0, 'total': 0}
        
        log_sync(f"📦 Procesando {len(pendientes)} operaciones pendientes...", "INFO")
        
        exitosos = 0
        fallidos = 0
        
        for pend in pendientes:
            query = pend["query"]
            args = json.loads(pend["args"]) if pend["args"] else None
            retries = pend["retries"]
            
            try:
                # Ejecutar consulta
                cur.execute(query, args or [])
                conn.commit()
                
                # Registrar éxito
                conn.execute("""
                    INSERT INTO sync_log_history (query, args, success)
                    VALUES (?, ?, 1)
                """, (query, json.dumps(args) if args else None))
                conn.execute("DELETE FROM sync_queue WHERE id = ?", (pend["id"],))
                conn.commit()
                
                exitosos += 1
                self._notificar('operacion_exitosa', {
                    'query': query[:100],
                    'id': pend["id"]
                })
                
                log_sync(f"✅ Operación exitosa: {query[:80]}...", "SUCCESS")
                
            except Exception as e:
                error_msg = str(e)
                nuevo_retries = retries + 1
                
                if nuevo_retries >= max_retries:
                    # Fallo permanente
                    conn.execute("""
                        INSERT INTO sync_log_history (query, args, success, error)
                        VALUES (?, ?, 0, ?)
                    """, (query, json.dumps(args) if args else None, 
                         f"Max retries ({max_retries}): {error_msg}"))
                    conn.execute("DELETE FROM sync_queue WHERE id = ?", (pend["id"],))
                    conn.commit()
                    
                    fallidos += 1
                    self._notificar('operacion_fallida_permanente', {
                        'query': query[:100],
                        'id': pend["id"],
                        'error': error_msg
                    })
                    
                    log_sync(f"❌ Falló permanentemente: {query[:80]}... - {error_msg}", "ERROR")
                else:
                    # Reintentar con backoff exponencial
                    delay = backoff_seconds * (2 ** retries)
                    next_retry = (datetime.now() + timedelta(seconds=delay)).isoformat()
                    
                    conn.execute("""
                        UPDATE sync_queue 
                        SET retries = ?, last_error = ?, next_retry = ?
                        WHERE id = ?
                    """, (nuevo_retries, error_msg, next_retry, pend["id"]))
                    conn.commit()
                    
                    fallidos += 1
                    self._notificar('operacion_reintentada', {
                        'query': query[:100],
                        'id': pend["id"],
                        'retry': nuevo_retries,
                        'next_retry': next_retry
                    })
                    
                    log_sync(f"⚠️ Reintento {nuevo_retries}/{max_retries} en {delay}s: {error_msg}", "WARNING")
        
        return {
            'success': exitosos,
            'failed': fallidos,
            'total': len(pendientes),
            'pending': self.contar_pendientes()
        }
    
    def procesar_en_background(self, intervalo: int = 30, 
                              max_retries: int = 5,
                              batch_size: int = 50):
        """✅ Inicia el procesamiento en segundo plano."""
        if self._procesador_activo:
            log_sync("⚠️ El procesador ya está activo", "WARNING")
            return
        
        self._procesador_activo = True
        self._thread = threading.Thread(
            target=self._loop_procesamiento,
            args=(intervalo, max_retries, batch_size),
            daemon=True
        )
        self._thread.start()
        
        self._notificar('procesador_iniciado', {
            'intervalo': intervalo,
            'max_retries': max_retries
        })
        
        log_sync(f"🔄 Procesador de cola iniciado (intervalo: {intervalo}s)", "INFO")
    
    def _loop_procesamiento(self, intervalo: int, max_retries: int, batch_size: int):
        """Bucle principal del procesador en background."""
        while self._procesador_activo:
            try:
                client = get_turso_client()
                
                if client.is_connected():
                    resultado = self.procesar_pendientes(
                        max_retries=max_retries,
                        batch_size=batch_size
                    )
                    
                    if resultado['total'] > 0:
                        self._notificar('ciclo_completado', resultado)
                else:
                    log_sync("⏳ Sin conexión a Turso, esperando...", "WARNING")
                    
            except Exception as e:
                log_sync(f"❌ Error en procesador de cola: {e}", "ERROR")
                self._notificar('error_procesador', {'error': str(e)})
            
            for _ in range(intervalo):
                if not self._procesador_activo:
                    break
                time.sleep(1)
    
    def detener(self):
        """✅ Detiene el procesador en segundo plano."""
        self._procesador_activo = False
        if self._thread:
            self._thread.join(timeout=5)
        
        self._notificar('procesador_detenido', {})
        log_sync("⏹️ Procesador de cola detenido", "INFO")
        
        # ✅ Cerrar conexión del hilo principal
        if hasattr(self._local, 'conn') and self._local.conn:
            try:
                self._local.conn.close()
            except:
                pass
            self._local.conn = None
    
    def limpiar_exitosos(self, dias: int = 30):
        """✅ Limpia el historial de operaciones exitosas antiguas."""
        conn = self._get_conn()
        fecha_limite = (datetime.now() - timedelta(days=dias)).isoformat()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM sync_log_history 
            WHERE success = 1 AND timestamp < ?
        """, (fecha_limite,))
        conn.commit()
        
        log_sync(f"🧹 Historial limpiado (operaciones exitosas > {dias} días)", "INFO")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """✅ Obtiene estadísticas de la cola."""
        conn = self._get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM sync_queue")
        pendientes = cur.fetchone()[0]
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as exitosos,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as fallidos
            FROM sync_log_history
        """)
        row = cur.fetchone()
        
        cur.execute("""
            SELECT error, COUNT(*) as cantidad
            FROM sync_log_history
            WHERE success = 0 AND error IS NOT NULL
            GROUP BY error
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        errores_comunes = [dict(r) for r in cur.fetchall()]
        
        return {
            'pending': pendientes,
            'total_history': row['total'] if row else 0,
            'successful': row['exitosos'] if row else 0,
            'failed': row['fallidos'] if row else 0,
            'common_errors': errores_comunes,
            'running': self._procesador_activo
        }
    
    # ============================================================
    # EVENTOS Y LISTENERS
    # ============================================================
    
    def add_listener(self, callback: Callable):
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notificar(self, evento: str, datos: Any = None):
        for listener in self._listeners:
            try:
                listener(evento, datos)
            except Exception as e:
                log_sync(f"⚠️ Error en listener: {e}", "WARNING")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detener()


# ============================================================
# SINGLETON GLOBAL PARA LA COLA
# ============================================================

_sync_queue = None

def get_sync_queue() -> SyncQueue:
    """✅ Obtiene la instancia única de la cola de sincronización."""
    global _sync_queue
    if _sync_queue is None:
        _sync_queue = SyncQueue()
    return _sync_queue