"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Ventas.
Coordina notas de venta, facturación, actualización de stock y cuenta corriente.
"""
import sqlite3
from datetime import date
from typing import List, Dict, Any, Optional
from modelos.nota_venta import NotaVenta
from modelos.factura import Factura
from modelos.producto import Producto
from modelos.cliente import Cliente
from controladores.controlador_stock import ControladorStock


class ControladorVentas:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.nota_venta_modelo = NotaVenta(db)
        self.factura_modelo = Factura(db)
        self.producto_modelo = Producto(db)
        self.cliente_modelo = Cliente(db)
        self.stock_ctrl = ControladorStock(db)

    # --- Notas de Venta ---
    def crear_nota_venta(self, preventista_id: int, cliente_id: int,
                         numero_nota: str, observaciones: str = None) -> int:
        """Crea una nota de venta pendiente."""
        if not preventista_id or not cliente_id:
            raise ValueError("Preventista y cliente son obligatorios.")
        return self.nota_venta_modelo.crear(preventista_id, cliente_id,
                                            numero_nota, observaciones)

    def agregar_detalle_nota(self, nota_venta_id: int, producto_id: int,
                             cantidad: float, precio_unitario: float = None) -> int:
        """Agrega un producto a la nota de venta. Si no se da precio, se usa el de venta del producto."""
        producto = self.producto_modelo.obtener_por_id(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado.")
        if precio_unitario is None:
            precio_unitario = producto['precio_venta']
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        return self.nota_venta_modelo.agregar_detalle(nota_venta_id, producto_id,
                                                      cantidad, precio_unitario)

    # --- Facturación ---
    def facturar_desde_nota(self, nota_venta_id: int) -> int:
        """Convierte una nota de venta en factura fiscal, descontando stock."""
        nota = self.nota_venta_modelo.obtener_por_id(nota_venta_id)
        if not nota or nota['estado'] != 'PENDIENTE':
            raise ValueError("La nota de venta no existe o ya fue procesada.")

        # Crear factura asociada
        factura_id = self.factura_modelo.crear(
            cliente_id=nota['cliente_id'],
            preventista_id=nota['preventista_id'],
            numero_factura=f"FV-{nota['numero_nota']}",   # ejemplo de numeración
            tipo_comprobante='B',
            observaciones=f"Generada desde nota {nota['numero_nota']}",
            nota_venta_id=nota_venta_id
        )

        # Obtener detalles de la nota
        cur = self.db.cursor()
        cur.execute("SELECT * FROM nota_venta_detalle WHERE nota_venta_id = ?",
                    (nota_venta_id,))
        detalles = [dict(row) for row in cur.fetchall()]

        # Agregar detalles a factura y descontar stock
        for det in detalles:
            self.factura_modelo.agregar_detalle(factura_id,
                                                det['producto_id'],
                                                det['cantidad'],
                                                det['precio_unitario'])
            self.stock_ctrl.descontar_stock(det['producto_id'], det['cantidad'])

        # Marcar nota como facturada
        self.nota_venta_modelo.cambiar_estado(nota_venta_id, 'FACTURADA')
        return factura_id

    def emitir_factura_directa(self, cliente_id: int, preventista_id: int,
                               tipo_comprobante: str, numero_factura: str,
                               items: List[Dict[str, Any]],
                               observaciones: str = None) -> int:
        """
        Emite una factura directamente con una lista de items.
        Cada item es un dict: {'producto_id': int, 'cantidad': float, 'precio_unitario': float (opcional)}
        """
        if not items:
            raise ValueError("Debe incluir al menos un producto.")

        factura_id = self.factura_modelo.crear(
            cliente_id=cliente_id,
            preventista_id=preventista_id,
            numero_factura=numero_factura,
            tipo_comprobante=tipo_comprobante,
            observaciones=observaciones
        )

        for item in items:
            prod_id = item['producto_id']
            cantidad = item['cantidad']
            precio = item.get('precio_unitario')
            producto = self.producto_modelo.obtener_por_id(prod_id)
            if not producto:
                raise ValueError(f"Producto ID {prod_id} no existe.")
            if precio is None:
                precio = producto['precio_venta']
            self.factura_modelo.agregar_detalle(factura_id, prod_id, cantidad, precio)
            self.stock_ctrl.descontar_stock(prod_id, cantidad)

        return factura_id