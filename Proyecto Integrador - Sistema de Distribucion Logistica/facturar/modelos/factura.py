"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.9: Modelo de Factura con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'facturas'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Sincronización: Central → Turso (solo lectura)
"""

from datetime import date
from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Factura(ModeloBase):
    """
    Modelo para gestionar facturas.
    
    Ejemplo:
        factura = Factura(db)
        factura_id = factura.crear(
            cliente_id=cliente_id,
            numero_factura="0001-00000001"
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de factura"""
        super().__init__(db)
        self._tabla = "facturas"
    
    def crear(self, cliente_id: str, numero_factura: str,
              tipo_comprobante: str = 'B', preventista_id: str = None,
              observaciones: str = None, nota_venta_id: str = None) -> str:
        """
        Crea una nueva factura con UUID.
        
        Returns:
            str: UUID de la factura creada
        """
        factura_id = self.generar_uuid()
        
        query = """
            INSERT INTO facturas (
                id, cliente_id, preventista_id, tipo_comprobante,
                numero_factura, fecha, subtotal, iva, tasa_municipal, total,
                observaciones, nota_venta_id, estado, saldo_anterior_cliente
            ) VALUES (?, ?, ?, ?, ?, date('now'), 0, 0, 0, 0, ?, ?, 'EMITIDA', 0)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            factura_id,
            cliente_id,
            preventista_id,
            tipo_comprobante,
            numero_factura,
            observaciones,
            nota_venta_id
        ))
        self.db.commit()
        return factura_id
    
    def agregar_detalle(self, factura_id: str, producto_id: str,
                        codigo_producto: str, cantidad: float,
                        precio_unitario: float) -> str:
        """
        Agrega un detalle a una factura.
        
        Returns:
            str: UUID del detalle creado
        """
        detalle_id = self.generar_uuid()
        
        query = """
            INSERT INTO factura_detalle (
                id, factura_id, producto_id, codigo_producto,
                cantidad, precio_unitario
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            detalle_id,
            factura_id,
            producto_id,
            codigo_producto,
            cantidad,
            precio_unitario
        ))
        self.db.commit()
        
        # Recalcular totales
        self._recalcular_totales(factura_id)
        
        return detalle_id
    
    def _recalcular_totales(self, factura_id: str):
        """
        Recalcula subtotal, IVA, tasa municipal y total de la factura.
        """
        cur = self.db.cursor()
        
        # Obtener cliente_id
        cur.execute("SELECT cliente_id FROM facturas WHERE id = ?", (factura_id,))
        row = cur.fetchone()
        if not row:
            return
        cliente_id = row['cliente_id']
        
        # Calcular subtotal
        cur.execute("""
            SELECT SUM(cantidad * precio_unitario) as subtotal
            FROM factura_detalle
            WHERE factura_id = ?
        """, (factura_id,))
        row = cur.fetchone()
        subtotal = row['subtotal'] if row and row['subtotal'] else 0.0
        
        # Calcular IVA según condición del cliente
        cur.execute("SELECT condicion_iva FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        iva_porcent = 0.21 if (row and row['condicion_iva'] == 'RI') else 0.0
        iva = subtotal * iva_porcent
        
        # Calcular tasa municipal
        cur.execute("SELECT aplica_tasa_municipal FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        tasa_pct = 0.0
        if row and row['aplica_tasa_municipal']:
            cur.execute("SELECT tasa_municipal_porcentaje FROM parametros WHERE id = 1")
            param = cur.fetchone()
            if param:
                tasa_pct = param['tasa_municipal_porcentaje'] / 100.0
        
        tasa_municipal = subtotal * tasa_pct
        total = subtotal + iva + tasa_municipal
        
        # Actualizar factura
        cur.execute("""
            UPDATE facturas 
            SET subtotal = ?, iva = ?, tasa_municipal = ?, total = ?
            WHERE id = ?
        """, (subtotal, iva, tasa_municipal, total, factura_id))
        self.db.commit()
    
    def obtener_por_id(self, factura_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una factura por su UUID"""
        return super().obtener_por_id(self._tabla, factura_id)
    
    def obtener_detalles(self, factura_id: str) -> List[Dict[str, Any]]:
        """Obtiene los detalles de una factura"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM factura_detalle
            WHERE factura_id = ?
            ORDER BY created_at
        """, (factura_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def listar_por_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Lista facturas de un cliente"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM facturas
            WHERE cliente_id = ?
            ORDER BY fecha DESC
        """, (cliente_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def listar_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """Lista facturas por estado"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM facturas
            WHERE estado = ?
            ORDER BY fecha DESC
        """, (estado,))
        return [dict(row) for row in cur.fetchall()]
    
    def actualizar(self, factura_id: str, **campos) -> bool:
        """Actualiza una factura"""
        return super().actualizar(self._tabla, factura_id, **campos)
    
    def anular(self, factura_id: str) -> bool:
        """Anula una factura"""
        return self.actualizar(factura_id, estado='ANULADA')