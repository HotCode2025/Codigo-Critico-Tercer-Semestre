"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Catálogo: guarda el historial de importaciones de catálogos PDF.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

class Catalogo:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def registrar_importacion(self, nombre_archivo: str, procesado_por: str,
                              total_productos_nuevos: int = 0,
                              total_actualizaciones: int = 0,
                              observaciones: str = None) -> int:
        cur = self.db.cursor()
        cur.execute("""INSERT INTO catalogo_importaciones
                       (fecha_importacion, nombre_archivo, procesado_por,
                        total_productos_nuevos, total_actualizaciones, observaciones)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (datetime.now().isoformat(), nombre_archivo, procesado_por,
                     total_productos_nuevos, total_actualizaciones, observaciones))
        self.db.commit()
        return cur.lastrowid

    def historial(self, limite: int = 20) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("""SELECT * FROM catalogo_importaciones
                        ORDER BY fecha_importacion DESC LIMIT ?""", (limite,))
        return [dict(row) for row in cur.fetchall()]

    def obtener_por_id(self, import_id: int) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM catalogo_importaciones WHERE id = ?", (import_id,))
        row = cur.fetchone()
        return dict(row) if row else None