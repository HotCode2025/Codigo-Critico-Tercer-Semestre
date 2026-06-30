"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.12: Modelo de Cuenta Corriente con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'cuenta_corriente_movimientos'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Tipos de movimiento: FACTURA, COBRO, NOTA_CREDITO, AJUSTE, ANULACION, REVERSO_COBRO
"""

from typing import List, Optional, Dict, Any
from datetime import date
from modelos.base import ModeloBase


class CuentaCorriente(ModeloBase):
    """
    Modelo para gestionar cuenta corriente.
    
    Ejemplo:
        cc = CuentaCorriente(db)
        movimientos = cc.movimientos(cliente_id)
        saldo = cc.saldo_actual(cliente_id)
    """
    
    def __init__(self, db):
        """Inicializa el modelo de cuenta corriente"""
        super().__init__(db)
        self._tabla = "cuenta_corriente_movimientos"
    
    def saldo_actual(self, cliente_id: str) -> float:
        """Obtiene el saldo actual de un cliente"""
        cur = self.db.cursor()
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        return row['saldo_cuenta_corriente'] if row else 0.0
    
    def movimientos(self, cliente_id: str, desde: str = None,
                    hasta: str = None) -> List[Dict[str, Any]]:
        """Lista movimientos de un cliente en un período"""
        query = """
            SELECT * FROM cuenta_corriente_movimientos
            WHERE cliente_id = ?
        """
        params = [cliente_id]
        
        if desde:
            query += " AND fecha >= ?"
            params.append(desde)
        if hasta:
            query += " AND fecha <= ?"
            params.append(hasta)
        
        query += " ORDER BY fecha DESC, created_at DESC"
        
        cur = self.db.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    
    def registrar_movimiento(self, cliente_id: str, tipo_movimiento: str,
                             importe: float, referencia_id: str = None,
                             observaciones: str = None) -> str:
        """
        Registra un movimiento en cuenta corriente.
        
        Args:
            cliente_id: UUID del cliente
            tipo_movimiento: FACTURA, COBRO, etc.
            importe: Monto (puede ser positivo o negativo)
            referencia_id: ID del documento relacionado (factura, cobro, etc.)
            observaciones: Observaciones del movimiento
        
        Returns:
            str: UUID del movimiento creado
        """
        mov_id = self.generar_uuid()
        
        # Obtener saldo actual
        saldo_actual = self.saldo_actual(cliente_id)
        nuevo_saldo = saldo_actual + importe
        
        query = """
            INSERT INTO cuenta_corriente_movimientos (
                id, cliente_id, fecha, tipo_movimiento, referencia_id,
                importe, saldo_resultante, observaciones
            ) VALUES (?, ?, date('now'), ?, ?, ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            mov_id,
            cliente_id,
            tipo_movimiento,
            referencia_id,
            importe,
            nuevo_saldo,
            observaciones
        ))
        
        # Actualizar saldo del cliente
        cur.execute("""
            UPDATE clientes 
            SET saldo_cuenta_corriente = ? 
            WHERE id = ?
        """, (nuevo_saldo, cliente_id))
        
        self.db.commit()
        return mov_id
    
    def limite_alcanzado(self, porcentaje_limite: float = 80.0) -> List[Dict[str, Any]]:
        """
        Lista clientes que superan el porcentaje de su límite de crédito.
        
        Args:
            porcentaje_limite: Porcentaje del límite (ej: 80 = 80%)
        
        Returns:
            Lista de clientes con su saldo y porcentaje de uso
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT 
                id, razon_social, cuit, limite_credito, saldo_cuenta_corriente,
                ROUND(saldo_cuenta_corriente * 100.0 / limite_credito, 1) as porcentaje_uso
            FROM clientes
            WHERE activo = 1 
            AND limite_credito > 0
            AND saldo_cuenta_corriente >= (limite_credito * ? / 100.0)
            ORDER BY porcentaje_uso DESC
        """, (porcentaje_limite,))
        return [dict(row) for row in cur.fetchall()]
    
    def clientes_con_saldo(self, saldo_minimo: float = 0) -> List[Dict[str, Any]]:
        """Lista clientes con saldo mayor o igual a saldo_minimo"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, razon_social, cuit, saldo_cuenta_corriente, limite_credito
            FROM clientes
            WHERE activo = 1 AND saldo_cuenta_corriente >= ?
            ORDER BY saldo_cuenta_corriente DESC
        """, (saldo_minimo,))
        return [dict(row) for row in cur.fetchall()]