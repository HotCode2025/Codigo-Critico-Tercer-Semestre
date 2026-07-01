"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.6: Modelo de Lote con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'lotes'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Trazabilidad FIFO (First In, First Out)
    - Sincronización: Central → Turso → App
"""

from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Lote(ModeloBase):
    """
    Modelo para gestionar lotes de productos.
    
    Ejemplo:
        lote = Lote(db)
        lote_id = lote.crear(
            producto_id=producto_id,
            fecha_vencimiento="2026-12-31",
            cantidad_inicial=100.0
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de lote"""
        super().__init__(db)
        self._tabla = "lotes"
    
    def crear(self, producto_id: str, fecha_vencimiento: str,
              cantidad_inicial: float, numero_lote: str = None) -> str:
        """
        Crea un nuevo lote con UUID.
        
        Returns:
            str: UUID del lote creado
        """
        lote_id = self.generar_uuid()
        
        # Obtener codigo_producto para el lote
        cur = self.db.cursor()
        cur.execute("SELECT codigo_producto FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        codigo_producto = row['codigo_producto'] if row else None
        
        query = """
            INSERT INTO lotes (
                id, producto_id, codigo_producto, numero_lote,
                fecha_vencimiento, cantidad_inicial, cantidad_actual, fecha_ingreso
            ) VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))
        """
        
        cur.execute(query, (
            lote_id,
            producto_id,
            codigo_producto,
            numero_lote,
            fecha_vencimiento,
            cantidad_inicial,
            cantidad_inicial
        ))
        self.db.commit()
        
        # Actualizar stock del producto
        self._actualizar_stock_producto(producto_id)
        
        return lote_id
    
    def obtener_por_id(self, lote_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un lote por su UUID"""
        return super().obtener_por_id(self._tabla, lote_id)
    
    def listar_por_producto(self, producto_id: str) -> List[Dict[str, Any]]:
        """Lista lotes de un producto, ordenados por vencimiento"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM lotes 
            WHERE producto_id = ? 
            ORDER BY fecha_vencimiento
        """, (producto_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def reducir_cantidad(self, lote_id: str, cantidad: float) -> bool:
        """
        Reduce la cantidad disponible de un lote.
        
        Args:
            lote_id: UUID del lote
            cantidad: Cantidad a restar
        
        Returns:
            bool: True si se redujo correctamente
        """
        cur = self.db.cursor()
        
        # Verificar que hay suficiente stock
        cur.execute("SELECT cantidad_actual, producto_id FROM lotes WHERE id = ?", (lote_id,))
        row = cur.fetchone()
        if not row or row['cantidad_actual'] < cantidad:
            return False
        
        nueva_cantidad = row['cantidad_actual'] - cantidad
        producto_id = row['producto_id']
        
        cur.execute("UPDATE lotes SET cantidad_actual = ? WHERE id = ?", (nueva_cantidad, lote_id))
        self.db.commit()
        
        # Actualizar stock del producto
        self._actualizar_stock_producto(producto_id)
        
        return True
    
    def _actualizar_stock_producto(self, producto_id: str):
        """
        Recalcula el stock_actual del producto sumando las cantidades de sus lotes.
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT SUM(cantidad_actual) as total
            FROM lotes 
            WHERE producto_id = ? AND cantidad_actual > 0
        """, (producto_id,))
        row = cur.fetchone()
        stock = row['total'] if row and row['total'] else 0.0
        
        cur.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (stock, producto_id))
        self.db.commit()
    
    def lotes_por_vencer(self, dias_anticipacion: int = 14) -> List[Dict[str, Any]]:
        """
        Lista lotes que vencen en los próximos X días.
        
        Args:
            dias_anticipacion: Días de anticipación para la alerta
        
        Returns:
            Lista de lotes con cantidad > 0
        """
        hoy = date.today()
        limite = hoy + timedelta(days=dias_anticipacion)
        
        cur = self.db.cursor()
        cur.execute("""
            SELECT l.*, p.descripcion as producto_desc
            FROM lotes l
            JOIN productos p ON l.producto_id = p.id
            WHERE l.fecha_vencimiento BETWEEN ? AND ?
            AND l.cantidad_actual > 0
            ORDER BY l.fecha_vencimiento
        """, (hoy.isoformat(), limite.isoformat()))
        return [dict(row) for row in cur.fetchall()]