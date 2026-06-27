"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Cuenta Corriente: consulta de movimientos y saldo.
"""
import sqlite3
from datetime import date
from typing import List, Optional, Dict, Any

class CuentaCorriente:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def saldo_actual(self, cliente_id: int) -> float:
        cur = self.db.cursor()
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        return row['saldo_cuenta_corriente'] if row else 0.0

    def movimientos(self, cliente_id: int, desde: str = None, hasta: str = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cuenta_corriente_movimientos WHERE cliente_id = ?"
        params = [cliente_id]
        if desde:
            query += " AND fecha >= ?"
            params.append(desde)
        if hasta:
            query += " AND fecha <= ?"
            params.append(hasta)
        query += " ORDER BY fecha DESC"
        cur = self.db.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def limite_alcanzado(self, porcentaje_limite: float = 80.0) -> List[Dict[str, Any]]:
        """Clientes cuyo saldo supera el porcentaje dado de su límite de crédito."""
        cur = self.db.cursor()
        cur.execute("""SELECT * FROM clientes WHERE activo = 1 AND limite_credito > 0
                        AND saldo_cuenta_corriente >= (limite_credito * ? / 100)""",
                    (porcentaje_limite,))
        return [dict(row) for row in cur.fetchall()]