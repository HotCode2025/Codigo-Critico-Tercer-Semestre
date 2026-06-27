"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Producto – incluye campos para catálogo (categoría, foto, detalle, etc.)
y soporte para imágenes como BLOB.
"""

import sqlite3
from typing import List, Optional, Dict, Any


class Producto:
    """Clase para gestionar la tabla 'productos'."""

    def __init__(self, db: sqlite3.Connection):
        """
        Inicializa el modelo con una conexión a la base de datos.
        :param db: Conexión activa a SQLite.
        """
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, codigo_producto: str, descripcion: str,
              precio_costo: float = 0.0, precio_venta: float = 0.0,
              stock_critico: float = 0.0, unidad_medida: str = 'unidad',
              categoria_id: int = None, url_foto: str = None,
              detalle: str = None, precio_oferta: float = None,
              destacado: int = 0, foto: bytes = None) -> int:
        """
        Crea un nuevo producto.
        :param codigo_producto: Código único del producto.
        :param descripcion: Nombre o descripción breve.
        :param precio_costo: Precio de costo.
        :param precio_venta: Precio de venta actual.
        :param stock_critico: Nivel mínimo de stock antes de alertar.
        :param unidad_medida: Unidad de medida (ej: 'unidad', 'kg').
        :param categoria_id: ID de la categoría (opcional).
        :param url_foto: Ruta relativa o URL de la foto del producto (opcional).
        :param detalle: Descripción larga o adicional.
        :param precio_oferta: Precio de oferta temporal.
        :param destacado: 1 si el producto es destacado, 0 en caso contrario.
        :param foto: Bytes de la imagen del producto (BLOB).
        :return: ID del producto creado.
        """
        query = """INSERT INTO productos (codigo_producto, descripcion, precio_costo, precio_venta,
                    stock_actual, stock_critico, unidad_medida, categoria_id, url_foto,
                    detalle, precio_oferta, destacado, foto)
                    VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (codigo_producto, descripcion, precio_costo, precio_venta,
                            stock_critico, unidad_medida, categoria_id, url_foto,
                            detalle, precio_oferta, destacado, foto))
        self.db.commit()
        return cur.lastrowid

    def obtener_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto por su ID.
        :param producto_id: ID del producto.
        :return: Diccionario con los datos del producto, o None si no existe.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def obtener_por_codigo(self, codigo_producto: str) -> Optional[Dict[str, Any]]:
        """
        Busca un producto por su código único.
        :param codigo_producto: Código del producto.
        :return: Diccionario con los datos del producto, o None si no existe.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE codigo_producto = ?", (codigo_producto,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista todos los productos.
        :param solo_activos: Si es True, solo devuelve productos con activo=1.
        :return: Lista de diccionarios con los datos de cada producto.
        """
        cur = self.db.cursor()
        if solo_activos:
            cur.execute("SELECT * FROM productos WHERE activo = 1")
        else:
            cur.execute("SELECT * FROM productos")
        return [dict(row) for row in cur.fetchall()]

    def actualizar(self, producto_id: int, **campos) -> bool:
        """
        Actualiza campos específicos de un producto.
        :param producto_id: ID del producto a modificar.
        :param campos: Diccionario con los campos a actualizar.
        :return: True si se modificó al menos una fila.
        """
        if not campos:
            return False
        sets = ", ".join(f"{k} = ?" for k in campos.keys())
        valores = list(campos.values())
        valores.append(producto_id)
        cur = self.db.cursor()
        cur.execute(f"UPDATE productos SET {sets} WHERE id = ?", valores)
        self.db.commit()
        return cur.rowcount > 0

    def eliminar(self, producto_id: int) -> bool:
        """
        Da de baja lógica al producto (activo=0).
        :param producto_id: ID del producto a eliminar.
        :return: True si se realizó la baja.
        """
        return self.actualizar(producto_id, activo=0)

    def stock_bajo_minimo(self) -> List[Dict[str, Any]]:
        """
        Devuelve los productos activos cuyo stock actual es menor o igual al stock crítico.
        :return: Lista de productos en estado crítico.
        """
        cur = self.db.cursor()
        cur.execute("""SELECT * FROM productos WHERE activo = 1
                        AND stock_actual <= stock_critico""")
        return [dict(row) for row in cur.fetchall()]

    # --------------- Métodos específicos para el catálogo ---------------
    def listar_por_categoria(self, categoria_id: int, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista los productos que pertenecen a una categoría.
        :param categoria_id: ID de la categoría.
        :param solo_activos: Si es True, solo devuelve productos activos.
        :return: Lista de productos.
        """
        cur = self.db.cursor()
        if solo_activos:
            cur.execute("SELECT * FROM productos WHERE categoria_id = ? AND activo = 1", (categoria_id,))
        else:
            cur.execute("SELECT * FROM productos WHERE categoria_id = ?", (categoria_id,))
        return [dict(row) for row in cur.fetchall()]

    def listar_destacados(self) -> List[Dict[str, Any]]:
        """
        Devuelve los productos marcados como destacados.
        :return: Lista de productos destacados.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE destacado = 1 AND activo = 1")
        return [dict(row) for row in cur.fetchall()]