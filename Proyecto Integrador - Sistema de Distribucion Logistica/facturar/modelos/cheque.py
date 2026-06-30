"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.11: Modelo de Cheque con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'cheques'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Estados: EN_CARTERA, DEPOSITADO, VENDIDO, ACREDITADO, RECHAZADO
"""

from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Cheque(ModeloBase):
    """
    Modelo para gestionar cheques.
    
    Ejemplo:
        cheque = Cheque(db)
        cheque_id = cheque.crear(
            cobro_id=cobro_id,
            cliente_id=cliente_id,
            banco="Banco Provincia",
            numero_cheque="12345678",
            fecha_emision="2026-01-01",
            fecha_vencimiento="2026-06-01",
            importe=1000.0
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de cheque"""
        super().__init__(db)
        self._tabla = "cheques"
    
    def crear(self, cobro_id: str, cliente_id: str, banco: str,
              numero_cheque: str, fecha_emision: str, fecha_vencimiento: str,
              importe: float, factura_ids: str = None, observaciones: str = None) -> str:
        """
        Crea un nuevo cheque con UUID.
        
        Returns:
            str: UUID del cheque creado
        """
        cheque_id = self.generar_uuid()
        
        query = """
            INSERT INTO cheques (
                id, cobro_id, cliente_id, banco, numero_cheque,
                fecha_emision, fecha_vencimiento, importe, estado,
                factura_ids, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EN_CARTERA', ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            cheque_id,
            cobro_id,
            cliente_id,
            banco,
            numero_cheque,
            fecha_emision,
            fecha_vencimiento,
            importe,
            factura_ids,
            observaciones
        ))
        self.db.commit()
        return cheque_id
    
    def obtener_por_id(self, cheque_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cheque por su UUID"""
        return super().obtener_por_id(self._tabla, cheque_id)
    
    def obtener_por_numero(self, numero_cheque: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cheque por su número"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM cheques WHERE numero_cheque = ?", (numero_cheque,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_en_cartera(self) -> List[Dict[str, Any]]:
        """Lista cheques en cartera (no acreditados ni vendidos)"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT c.*, cl.razon_social as cliente_nombre
            FROM cheques c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.estado IN ('EN_CARTERA', 'DEPOSITADO')
            ORDER BY c.fecha_vencimiento
        """)
        return [dict(row) for row in cur.fetchall()]
    
    def listar_vendidos(self) -> List[Dict[str, Any]]:
        """Lista cheques vendidos"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT c.*, cl.razon_social as cliente_nombre
            FROM cheques c
            JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.estado = 'VENDIDO'
            ORDER BY c.fecha_vencimiento
        """)
        return [dict(row) for row in cur.fetchall()]
    
    def listar_por_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Lista cheques de un cliente"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM cheques
            WHERE cliente_id = ?
            ORDER BY fecha_vencimiento DESC
        """, (cliente_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def acreditar(self, cheque_id: str, fecha_acreditacion: str) -> bool:
        """Marca un cheque como acreditado"""
        return self.actualizar(cheque_id, estado='ACREDITADO', fecha_acreditacion=fecha_acreditacion)
    
    def vender(self, cheque_id: str, vendido_a: str) -> bool:
        """Marca un cheque como vendido"""
        return self.actualizar(cheque_id, estado='VENDIDO', vendido_a=vendido_a)
    
    def rechazar(self, cheque_id: str, observaciones: str = None) -> bool:
        """Marca un cheque como rechazado"""
        return self.actualizar(cheque_id, estado='RECHAZADO', observaciones=observaciones)
    
    def actualizar(self, cheque_id: str, **campos) -> bool:
        """Actualiza un cheque"""
        return super().actualizar(self._tabla, cheque_id, **campos)