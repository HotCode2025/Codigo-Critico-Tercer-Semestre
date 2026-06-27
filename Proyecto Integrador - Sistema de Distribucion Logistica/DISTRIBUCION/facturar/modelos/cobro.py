"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Cobro con UUID.
"""
import sqlite3
import uuid
from datetime import date
from typing import List, Optional, Dict, Any

class Cobro:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def registrar(self, cliente_id: int, importe: float,
                  medio_pago: str = None, observaciones: str = None) -> str:
        cobro_id = str(uuid.uuid4())
        cur = self.db.cursor()
        cur.execute("""INSERT INTO cobros (id, cliente_id, fecha, importe, medio_pago, observaciones)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (cobro_id, cliente_id, date.today().isoformat(), importe, medio_pago, observaciones))
        self.db.commit()

        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        if row:
            nuevo_saldo = row['saldo_cuenta_corriente'] - importe
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?",
                        (nuevo_saldo, cliente_id))

            mov_id = str(uuid.uuid4())
            cur.execute("""INSERT INTO cuenta_corriente_movimientos
                           (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe,
                            saldo_resultante)
                           VALUES (?, ?, ?, 'COBRO', ?, ?, ?)""",
                        (mov_id, cliente_id, date.today().isoformat(), cobro_id, importe, nuevo_saldo))
            self.db.commit()
        return cobro_id

    def obtener_por_id(self, cobro_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM cobros WHERE id = ?", (cobro_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM cobros WHERE cliente_id = ? ORDER BY fecha DESC", (cliente_id,))
        return [dict(row) for row in cur.fetchall()]