"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.6: Controlador de Cuenta Corriente con UUID
==================================================
📌 USO: Gestiona cuenta corriente de clientes
📌 CARACTERÍSTICAS:
    - Saldos y movimientos
    - Alertas de límite de crédito
"""

import sqlite3
from typing import List, Dict, Any

from modelos.cuenta_corriente import CuentaCorriente
from modelos.cobro import Cobro


class ControladorCuentaCorriente:
    """
    Controlador para gestionar cuenta corriente.
    
    Ejemplo:
        ctrl = ControladorCuentaCorriente(db)
        saldo = ctrl.obtener_saldo(cliente_id)
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el controlador de cuenta corriente"""
        self.db = db
        self.cc_modelo = CuentaCorriente(db)
        self.cobro_modelo = Cobro(db)
    
    def obtener_saldo(self, cliente_id: str) -> float:
        """Obtiene el saldo de un cliente"""
        return self.cc_modelo.saldo_actual(cliente_id)
    
    def listar_movimientos(self, cliente_id: str, desde: str = None,
                           hasta: str = None) -> List[Dict[str, Any]]:
        """Lista movimientos de un cliente"""
        return self.cc_modelo.movimientos(cliente_id, desde, hasta)
    
    def registrar_cobro(self, cliente_id: str, importe: float,
                        medio_pago: str = None, observaciones: str = None) -> str:
        """
        Registra un cobro y actualiza la cuenta corriente.
        
        Returns:
            str: UUID del cobro creado
        """
        if importe <= 0:
            raise ValueError("El importe del cobro debe ser positivo.")
        return self.cobro_modelo.registrar(cliente_id, importe, medio_pago, observaciones)
    
    def clientes_al_limite(self, porcentaje: float = 80.0) -> List[Dict[str, Any]]:
        """
        Lista clientes que superan el porcentaje de su límite de crédito.
        
        Args:
            porcentaje: Porcentaje del límite (ej: 80 = 80%)
        
        Returns:
            Lista de clientes con su saldo y porcentaje de uso
        """
        return self.cc_modelo.limite_alcanzado(porcentaje_limite=porcentaje)