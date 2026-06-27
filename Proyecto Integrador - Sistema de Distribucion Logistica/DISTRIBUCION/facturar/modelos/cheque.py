"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Cheque con UUID.
"""

import sqlite3
import uuid
from datetime import date
from typing import List, Optional, Dict, Any


class Cheque:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, cobro_id: str, cliente_id: int, banco: str,
              numero_cheque: str, fecha_emision: str, fecha_vencimiento: str,
              importe: float, factura_ids: str = None, observaciones: str = None) -> str:
        """Crea un nuevo cheque en cartera (devuelve UUID)."""
        cheque_id = str(uuid.uuid4())
        cur = self.db.cursor()
        cur.execute("""INSERT INTO cheques (id, cobro_id, cliente_id, banco, numero_cheque,
                       fecha_emision, fecha_vencimiento, importe, estado, factura_ids, observaciones)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EN_CARTERA', ?, ?)""",
                    (cheque_id, cobro_id, cliente_id, banco, numero_cheque,
                     fecha_emision, fecha_vencimiento, importe, factura_ids, observaciones))
        self.db.commit()
        return cheque_id

    def obtener_por_id(self, cheque_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM cheques WHERE id = ?", (cheque_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_en_cartera(self) -> List[Dict[str, Any]]:
        """Cheques que aún no fueron acreditados ni vendidos."""
        cur = self.db.cursor()
        cur.execute("""SELECT c.*, cl.razon_social as cliente_nombre
                       FROM cheques c
                       JOIN clientes cl ON c.cliente_id = cl.id
                       WHERE c.estado IN ('EN_CARTERA', 'DEPOSITADO')
                       ORDER BY c.fecha_vencimiento""")
        return [dict(row) for row in cur.fetchall()]

    def listar_vendidos(self) -> List[Dict[str, Any]]:
        """Cheques que fueron negociados (vendidos a terceros)."""
        cur = self.db.cursor()
        cur.execute("""SELECT c.*, cl.razon_social as cliente_nombre
                       FROM cheques c
                       JOIN clientes cl ON c.cliente_id = cl.id
                       WHERE c.estado = 'VENDIDO'
                       ORDER BY c.fecha_vencimiento""")
        return [dict(row) for row in cur.fetchall()]

    def cambiar_estado(self, cheque_id: str, nuevo_estado: str,
                       fecha_acreditacion: str = None, vendido_a: str = None) -> bool:
        """Actualiza el estado del cheque y datos relacionados."""
        cur = self.db.cursor()
        if nuevo_estado == 'ACREDITADO' and fecha_acreditacion:
            cur.execute("""UPDATE cheques SET estado = ?, fecha_acreditacion = ?
                           WHERE id = ?""", (nuevo_estado, fecha_acreditacion, cheque_id))
        elif nuevo_estado == 'VENDIDO' and vendido_a:
            cur.execute("""UPDATE cheques SET estado = ?, vendido_a = ?
                           WHERE id = ?""", (nuevo_estado, vendido_a, cheque_id))
        else:
            cur.execute("UPDATE cheques SET estado = ? WHERE id = ?", (nuevo_estado, cheque_id))
        self.db.commit()
        return cur.rowcount > 0

    def listar_por_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        """Todos los cheques de un cliente específico."""
        cur = self.db.cursor()
        cur.execute("""SELECT * FROM cheques WHERE cliente_id = ?
                       ORDER BY fecha_vencimiento DESC""", (cliente_id,))
        return [dict(row) for row in cur.fetchall()]