"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.8: Modelo de Nota de Venta con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'notas_venta'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - codigo_producto en detalle (NO producto_id)
    - Sincronización: App → Turso → Central
"""

from datetime import date
from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class NotaVenta(ModeloBase):
    """
    Modelo para gestionar notas de venta.
    
    Ejemplo:
        nota = NotaVenta(db)
        nota_id = nota.crear(
            preventista_id=preventista_id,
            cliente_id=cliente_id,
            numero_nota="N-001"
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de nota de venta"""
        super().__init__(db)
        self._tabla = "notas_venta"
    
    def crear(self, preventista_id: str, cliente_id: str, 
              numero_nota: str, observaciones: str = None) -> str:
        """
        Crea una nueva nota de venta con UUID.
        
        Returns:
            str: UUID de la nota creada
        """
        nota_id = self.generar_uuid()
        
        query = """
            INSERT INTO notas_venta (
                id, preventista_id, cliente_id, fecha, numero_nota,
                total, observaciones, estado, procesado_central
            ) VALUES (?, ?, ?, ?, ?, 0, ?, 'PENDIENTE', 0)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            nota_id,
            preventista_id,
            cliente_id,
            date.today().isoformat(),
            numero_nota,
            observaciones
        ))
        self.db.commit()
        return nota_id
    
    def agregar_detalle(self, nota_venta_id: str, codigo_producto: str,
                        cantidad: float, precio_unitario: float,
                        producto_id: str = None) -> str:
        """
        Agrega un detalle a una nota de venta.
        
        IMPORTANTE: Siempre se usa codigo_producto, producto_id es opcional.
        
        Args:
            nota_venta_id: UUID de la nota
            codigo_producto: Código del producto (obligatorio)
            cantidad: Cantidad
            precio_unitario: Precio unitario
            producto_id: UUID del producto (opcional, se resuelve en Central)
        
        Returns:
            str: UUID del detalle creado
        """
        detalle_id = self.generar_uuid()
        
        query = """
            INSERT INTO nota_venta_detalle (
                id, nota_venta_id, producto_id, codigo_producto,
                cantidad, precio_unitario
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            detalle_id,
            nota_venta_id,
            producto_id,
            codigo_producto,
            cantidad,
            precio_unitario
        ))
        self.db.commit()
        
        # Actualizar total de la nota
        self._actualizar_total(nota_venta_id)
        
        return detalle_id
    
    def _actualizar_total(self, nota_venta_id: str):
        """Recalcula el total de la nota sumando sus detalles"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT SUM(cantidad * precio_unitario) as total
            FROM nota_venta_detalle
            WHERE nota_venta_id = ?
        """, (nota_venta_id,))
        row = cur.fetchone()
        total = row['total'] if row and row['total'] else 0.0
        
        cur.execute("UPDATE notas_venta SET total = ? WHERE id = ?", (total, nota_venta_id))
        self.db.commit()
    
    def obtener_por_id(self, nota_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una nota por su UUID"""
        return super().obtener_por_id(self._tabla, nota_id)
    
    def obtener_detalles(self, nota_id: str) -> List[Dict[str, Any]]:
        """Obtiene los detalles de una nota"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM nota_venta_detalle
            WHERE nota_venta_id = ?
            ORDER BY created_at
        """, (nota_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def listar_por_estado(self, estado: str = 'PENDIENTE') -> List[Dict[str, Any]]:
        """Lista notas por estado"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM notas_venta
            WHERE estado = ?
            ORDER BY fecha DESC
        """, (estado,))
        return [dict(row) for row in cur.fetchall()]
    
    def listar_por_preventista(self, preventista_id: str) -> List[Dict[str, Any]]:
        """Lista notas de un preventista"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM notas_venta
            WHERE preventista_id = ?
            ORDER BY fecha DESC
        """, (preventista_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def cambiar_estado(self, nota_id: str, nuevo_estado: str) -> bool:
        """Cambia el estado de una nota"""
        if nuevo_estado not in ('PENDIENTE', 'FACTURADA', 'ANULADA', 'PROCESADA'):
            return False
        
        return self.actualizar(nota_id, estado=nuevo_estado)
    
    def actualizar(self, nota_id: str, **campos) -> bool:
        """Actualiza una nota"""
        return super().actualizar(self._tabla, nota_id, **campos)
    
    def marcar_procesada(self, nota_id: str) -> bool:
        """Marca una nota como procesada por Central"""
        return self.actualizar(nota_id, procesado_central=1)