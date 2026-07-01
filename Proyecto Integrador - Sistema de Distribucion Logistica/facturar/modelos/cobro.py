"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.10: Modelo de Cobro con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'cobros'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Sincronización: Central → Turso
"""

from datetime import date
from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Cobro(ModeloBase):
    """
    Modelo para gestionar cobros.
    
    Ejemplo:
        cobro = Cobro(db)
        cobro_id = cobro.registrar(
            cliente_id=cliente_id,
            importe=100.0,
            medio_pago="EFECTIVO"
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de cobro"""
        super().__init__(db)
        self._tabla = "cobros"
    
    def registrar(self, cliente_id: str, importe: float,
                  medio_pago: str = 'EFECTIVO', observaciones: str = None) -> str:
        """
        Registra un nuevo cobro con UUID.
        
        Returns:
            str: UUID del cobro creado
        """
        cobro_id = self.generar_uuid()
        
        query = """
            INSERT INTO cobros (
                id, cliente_id, fecha, importe, medio_pago, observaciones
            ) VALUES (?, ?, date('now'), ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            cobro_id,
            cliente_id,
            importe,
            medio_pago,
            observaciones
        ))
        self.db.commit()
        
        # Actualizar saldo del cliente
        self._actualizar_saldo_cliente(cliente_id, -importe, cobro_id, 'COBRO')
        
        return cobro_id
    
    def _actualizar_saldo_cliente(self, cliente_id: str, importe: float,
                                   referencia_id: str, tipo_mov: str):
        """
        Actualiza el saldo del cliente y registra el movimiento.
        """
        cur = self.db.cursor()
        
        # Obtener saldo actual
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        saldo_actual = row['saldo_cuenta_corriente'] if row else 0.0
        
        nuevo_saldo = saldo_actual + importe
        
        # Actualizar cliente
        cur.execute("""
            UPDATE clientes 
            SET saldo_cuenta_corriente = ? 
            WHERE id = ?
        """, (nuevo_saldo, cliente_id))
        
        # Registrar movimiento
        mov_id = self.generar_uuid()
        cur.execute("""
            INSERT INTO cuenta_corriente_movimientos (
                id, cliente_id, fecha, tipo_movimiento, referencia_id,
                importe, saldo_resultante
            ) VALUES (?, ?, date('now'), ?, ?, ?, ?)
        """, (
            mov_id,
            cliente_id,
            tipo_mov,
            referencia_id,
            importe,
            nuevo_saldo
        ))
        self.db.commit()
    
    def obtener_por_id(self, cobro_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cobro por su UUID"""
        return super().obtener_por_id(self._tabla, cobro_id)
    
    def listar_por_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Lista cobros de un cliente"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM cobros
            WHERE cliente_id = ?
            ORDER BY fecha DESC
        """, (cliente_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def listar_por_periodo(self, desde: str, hasta: str) -> List[Dict[str, Any]]:
        """Lista cobros en un período"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM cobros
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """, (desde, hasta))
        return [dict(row) for row in cur.fetchall()]