"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Productos.
Maneja la creación, actualización y consulta de productos.
"""
import sqlite3
from typing import List, Optional, Dict, Any
from modelos.producto import Producto


class ControladorProductos:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.modelo = Producto(db)

    def crear_producto(self, codigo: str, descripcion: str,
                       precio_costo: float = 0.0, precio_venta: float = 0.0,
                       stock_critico: float = 0.0, unidad_medida: str = 'unidad') -> int:
        """Crea un producto con validación de código único y precios no negativos."""
        codigo = codigo.strip()
        if not codigo:
            raise ValueError("El código del producto es obligatorio.")
        if self.modelo.obtener_por_codigo(codigo):
            raise ValueError("El código de producto ya existe.")
        if precio_costo < 0 or precio_venta < 0:
            raise ValueError("Los precios no pueden ser negativos.")
        return self.modelo.crear(codigo=codigo,
                                 descripcion=descripcion.strip(),
                                 precio_costo=precio_costo,
                                 precio_venta=precio_venta,
                                 stock_critico=stock_critico,
                                 unidad_medida=unidad_medida.strip() or 'unidad')

    def modificar_producto(self, producto_id: int, **campos) -> bool:
        """Actualiza un producto. Si se cambia el código, verifica unicidad."""
        if 'codigo' in campos:
            nuevo_codigo = campos['codigo'].strip()
            existente = self.modelo.obtener_por_codigo(nuevo_codigo)
            if existente and existente['id'] != producto_id:
                raise ValueError("El código ya está en uso por otro producto.")
        return self.modelo.actualizar(producto_id, **campos)

    def eliminar_producto(self, producto_id: int) -> bool:
        return self.modelo.eliminar(producto_id)

    def obtener_producto(self, producto_id: int) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_id(producto_id)

    def listar_productos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        return self.modelo.listar_todos(solo_activos=solo_activos)

    def obtener_stock_critico(self) -> List[Dict[str, Any]]:
        return self.modelo.stock_bajo_minimo()