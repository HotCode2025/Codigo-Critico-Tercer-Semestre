"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Cuenta Corriente.
Manejo de saldos, movimientos y cobros.
"""
import sqlite3
from typing import List, Dict, Any
from modelos.cuenta_corriente import CuentaCorriente
from modelos.cobro import Cobro


class ControladorCuentaCorriente:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.cc_modelo = CuentaCorriente(db)
        self.cobro_modelo = Cobro(db)

    def obtener_saldo(self, cliente_id: int) -> float:
        return self.cc_modelo.saldo_actual(cliente_id)

    def listar_movimientos(self, cliente_id: int, desde: str = None,
                           hasta: str = None) -> List[Dict[str, Any]]:
        return self.cc_modelo.movimientos(cliente_id, desde, hasta)

    def registrar_cobro(self, cliente_id: int, importe: float,
                        medio_pago: str = None, observaciones: str = None) -> int:
        """Registra un cobro y actualiza la cuenta corriente."""
        if importe <= 0:
            raise ValueError("El importe del cobro debe ser positivo.")
        return self.cobro_modelo.registrar(cliente_id, importe,
                                           medio_pago, observaciones)

    def clientes_al_limite(self, porcentaje: float = 80.0) -> List[Dict[str, Any]]:
        """Devuelve clientes que superan el porcentaje de su límite de crédito."""
        return self.cc_modelo.limite_alcanzado(porcentaje_limite=porcentaje)