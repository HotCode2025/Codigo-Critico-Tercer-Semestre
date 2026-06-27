"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Nota de Venta con UUID.
"""

import sqlite3
import uuid
from datetime import date
from typing import List, Optional, Dict, Any

class NotaVenta:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, preventista_id: int, cliente_id: int, numero_nota: str,
              observaciones: str = None) -> str:
        """Crea una nota de venta (desde central = procesado_central = 1)."""
        nuevo_id = str(uuid.uuid4())
        query = """INSERT INTO notas_venta (id, preventista_id, cliente_id, fecha,
                    numero_nota, total, observaciones, estado, procesado_central)
                    VALUES (?, ?, ?, ?, ?, 0, ?, 'PENDIENTE', 1)"""
        cur = self.db.cursor()
        cur.execute(query, (nuevo_id, preventista_id, cliente_id,
                            date.today().isoformat(), numero_nota, observaciones))
        self.db.commit()
        return nuevo_id

    def agregar_detalle(self, nota_venta_id: str, producto_id: int,
                        cantidad: float, precio_unitario: float) -> str:
        detalle_id = str(uuid.uuid4())
        query = """INSERT INTO nota_venta_detalle (id, nota_venta_id, producto_id,
                    cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (detalle_id, nota_venta_id, producto_id, cantidad, precio_unitario))
        self.db.commit()
        self._actualizar_total(nota_venta_id)
        return detalle_id

    def _actualizar_total(self, nota_venta_id: str):
        cur = self.db.cursor()
        cur.execute("SELECT SUM(cantidad * precio_unitario) FROM nota_venta_detalle WHERE nota_venta_id = ?", (nota_venta_id,))
        total = cur.fetchone()[0] or 0.0
        cur.execute("UPDATE notas_venta SET total = ? WHERE id = ?", (total, nota_venta_id))
        self.db.commit()

    def obtener_por_id(self, nota_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM notas_venta WHERE id = ?", (nota_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_estado(self, estado: str = 'PENDIENTE') -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM notas_venta WHERE estado = ? ORDER BY fecha DESC", (estado,))
        return [dict(row) for row in cur.fetchall()]

    def cambiar_estado(self, nota_id: str, nuevo_estado: str, commit: bool = True) -> bool:
        if nuevo_estado not in ('PENDIENTE', 'FACTURADA', 'ANULADA'):
            return False
        cur = self.db.cursor()
        if nuevo_estado == 'FACTURADA':
            cur.execute("UPDATE notas_venta SET estado = ?, procesado_central = 1 WHERE id = ?",
                        (nuevo_estado, nota_id))
        else:
            cur.execute("UPDATE notas_venta SET estado = ? WHERE id = ?", (nuevo_estado, nota_id))
        if commit:
            self.db.commit()
        return cur.rowcount > 0