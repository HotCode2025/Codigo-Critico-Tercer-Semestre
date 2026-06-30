"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.3: Modelo de Producto con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'productos'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - codigo_producto: identificador GLOBAL (usado por la App)
    - Sincronización: Central → Turso → App (SIN fotos)
"""

from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Producto(ModeloBase):
    """
    Modelo para gestionar productos.
    
    Ejemplo:
        producto = Producto(db)
        producto_id = producto.crear(
            codigo_producto="PROD-001",
            descripcion="Producto de prueba",
            precio_venta=100.0
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de producto"""
        super().__init__(db)
        self._tabla = "productos"
    
    def crear(self, codigo_producto: str, descripcion: str,
              precio_costo: float = 0.0, precio_venta: float = 0.0,
              stock_critico: float = 0.0, unidad_medida: str = 'unidad',
              categoria_id: str = None, foto: bytes = None,
              detalle: str = None, precio_oferta: float = None,
              destacado: int = 0, url_foto: str = None) -> str:
        """
        Crea un nuevo producto con UUID.
        
        Returns:
            str: UUID del producto creado
        """
        producto_id = self.generar_uuid()
        
        query = """
            INSERT INTO productos (
                id, codigo_producto, descripcion, precio_costo, precio_venta,
                stock_actual, stock_critico, unidad_medida, categoria_id,
                foto, url_foto, detalle, precio_oferta, destacado
            ) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            producto_id,
            codigo_producto,
            descripcion,
            precio_costo,
            precio_venta,
            stock_critico,
            unidad_medida,
            categoria_id,
            foto,
            url_foto,
            detalle,
            precio_oferta,
            destacado
        ))
        self.db.commit()
        return producto_id
    
    def obtener_por_id(self, producto_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su UUID"""
        return super().obtener_por_id(self._tabla, producto_id)
    
    def obtener_por_codigo(self, codigo_producto: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código (identificador global)"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE codigo_producto = ?", (codigo_producto,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los productos"""
        return super().listar_todos(self._tabla, solo_activos)
    
    def listar_por_categoria(self, categoria_id: str) -> List[Dict[str, Any]]:
        """Lista productos por categoría"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM productos 
            WHERE categoria_id = ? AND activo = 1
            ORDER BY descripcion
        """, (categoria_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def listar_destacados(self) -> List[Dict[str, Any]]:
        """Lista productos destacados"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM productos 
            WHERE destacado = 1 AND activo = 1
            ORDER BY descripcion
        """)
        return [dict(row) for row in cur.fetchall()]
    
    def actualizar(self, producto_id: str, **campos) -> bool:
        """Actualiza un producto"""
        return super().actualizar(self._tabla, producto_id, **campos)
    
    def eliminar(self, producto_id: str) -> bool:
        """Elimina lógicamente un producto (activo=0)"""
        return super().eliminar(self._tabla, producto_id)
    
    def stock_bajo_minimo(self) -> List[Dict[str, Any]]:
        """Lista productos con stock bajo el crítico"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM productos 
            WHERE activo = 1 AND stock_actual <= stock_critico
            ORDER BY (stock_critico - stock_actual) DESC
        """)
        return [dict(row) for row in cur.fetchall()]
    
    def actualizar_stock(self, producto_id: str, cantidad: float) -> bool:
        """Actualiza el stock de un producto"""
        return self.actualizar(producto_id, stock_actual=cantidad)