"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.2: Controlador de Productos con UUID
==================================================
📌 USO: Gestiona productos con sincronización a Turso
📌 CARACTERÍSTICAS:
    - CRUD completo con UUID
    - Sincronización SIN fotos (para ahorrar ancho de banda)
    - Gestión de categorías
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any, BinaryIO

from modelos.producto import Producto
from modelos.categoria import Categoria
from utilidades.turso_client import get_turso_client
from utilidades.sync_manager import SyncDirection, SyncManager


class ControladorProductos:
    """
    Controlador para gestionar productos.
    
    Ejemplo:
        ctrl = ControladorProductos(db)
        producto_id = ctrl.crear_producto(
            codigo_producto="PROD-001",
            descripcion="Producto de prueba"
        )
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el controlador de productos"""
        self.db = db
        self.modelo = Producto(db)
        self.categoria_modelo = Categoria(db)
        self.sync_manager = SyncManager()
        
        # Registrar tabla para sincronización
        if 'productos' not in self.sync_manager.tables:
            self.sync_manager.register_table(
                name='productos',
                direction=SyncDirection.FROM_LOCAL,
                id_field='id',
                timestamp_field='updated_at'
            )
    
    def crear_producto(self, codigo_producto: str, descripcion: str,
                       precio_costo: float = 0.0, precio_venta: float = 0.0,
                       stock_critico: float = 0.0, unidad_medida: str = 'unidad',
                       categoria_id: str = None, foto: bytes = None,
                       detalle: str = None, precio_oferta: float = None,
                       destacado: int = 0, url_foto: str = None) -> str:
        """
        Crea un nuevo producto.
        
        Returns:
            str: UUID del producto creado
        """
        codigo_producto = codigo_producto.strip()
        if not codigo_producto:
            raise ValueError("El código del producto es obligatorio.")
        
        if self.modelo.obtener_por_codigo(codigo_producto):
            raise ValueError("El código de producto ya existe.")
        
        if precio_costo < 0 or precio_venta < 0:
            raise ValueError("Los precios no pueden ser negativos.")
        
        # Crear producto
        producto_id = self.modelo.crear(
            codigo_producto=codigo_producto,
            descripcion=descripcion.strip(),
            precio_costo=precio_costo,
            precio_venta=precio_venta,
            stock_critico=stock_critico,
            unidad_medida=unidad_medida,
            categoria_id=categoria_id,
            foto=foto,
            detalle=detalle,
            precio_oferta=precio_oferta,
            destacado=destacado,
            url_foto=url_foto
        )
        
        # Sincronizar a Turso (SIN FOTO)
        self._sincronizar_producto(producto_id)
        
        return producto_id
    
    def _sincronizar_producto(self, producto_id: str):
        """
        Sincroniza un producto específico a Turso (SIN FOTO).
        """
        try:
            producto = self.modelo.obtener_por_id(producto_id)
            if not producto:
                return
            
            # Eliminar foto para sincronización
            producto_sync = producto.copy()
            producto_sync.pop('foto', None)
            producto_sync.pop('url_foto', None)
            
            client = get_turso_client()
            if client.is_connected():
                client.insert('productos', producto_sync)
                print(f"✅ Producto {producto['codigo_producto']} sincronizado a Turso (sin foto)")
            else:
                self.sync_manager.sync_from_local('productos', self.db)
                
        except Exception as e:
            print(f"⚠️ Error sincronizando producto: {e}")
    
    def modificar_producto(self, producto_id: str, **campos) -> bool:
        """
        Modifica un producto existente.
        
        Args:
            producto_id: UUID del producto
            **campos: Campos a modificar
        
        Returns:
            bool: True si se modificó correctamente
        """
        if 'codigo_producto' in campos:
            nuevo_codigo = campos['codigo_producto'].strip()
            existente = self.modelo.obtener_por_codigo(nuevo_codigo)
            if existente and existente['id'] != producto_id:
                raise ValueError("El código ya está en uso por otro producto.")
        
        # No sincronizar foto
        campos_sync = {k: v for k, v in campos.items() if k not in ('foto', 'url_foto')}
        
        resultado = self.modelo.actualizar(producto_id, **campos)
        
        if resultado and campos_sync:
            self._sincronizar_producto(producto_id)
        
        return resultado
    
    def eliminar_producto(self, producto_id: str) -> bool:
        """
        Elimina lógicamente un producto (activo=0).
        
        Args:
            producto_id: UUID del producto
        
        Returns:
            bool: True si se eliminó correctamente
        """
        resultado = self.modelo.eliminar(producto_id)
        
        if resultado:
            try:
                client = get_turso_client()
                if client.is_connected():
                    client.update('productos', {'activo': 0}, 'id = ?', [producto_id])
            except Exception as e:
                print(f"⚠️ Error sincronizando eliminación: {e}")
        
        return resultado
    
    def obtener_producto(self, producto_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su UUID"""
        return self.modelo.obtener_por_id(producto_id)
    
    def obtener_producto_por_codigo(self, codigo_producto: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código"""
        return self.modelo.obtener_por_codigo(codigo_producto)
    
    def listar_productos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los productos"""
        return self.modelo.listar_todos(solo_activos=solo_activos)
    
    def listar_por_categoria(self, categoria_id: str) -> List[Dict[str, Any]]:
        """Lista productos por categoría"""
        return self.modelo.listar_por_categoria(categoria_id)
    
    def listar_destacados(self) -> List[Dict[str, Any]]:
        """Lista productos destacados"""
        return self.modelo.listar_destacados()
    
    def obtener_stock_critico(self) -> List[Dict[str, Any]]:
        """Lista productos con stock bajo el crítico"""
        return self.modelo.stock_bajo_minimo()
    
    # ============================================================
    # MÉTODOS PARA CATEGORÍAS
    # ============================================================
    
    def crear_categoria(self, nombre: str, descripcion: str = None) -> str:
        """Crea una nueva categoría"""
        return self.categoria_modelo.crear(nombre, descripcion)
    
    def listar_categorias(self) -> List[Dict[str, Any]]:
        """Lista todas las categorías"""
        return self.categoria_modelo.listar_todas()
    
    def eliminar_categoria(self, categoria_id: str) -> bool:
        """Elimina una categoría"""
        return self.categoria_modelo.eliminar(categoria_id)