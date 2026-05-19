"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Catálogo PDF.
Permite leer un catálogo en PDF enviado por el proveedor, extraer datos de productos,
y actualizar stock y precios de forma manual o automática (aplicando un porcentaje).
"""

import sqlite3
from typing import List, Dict, Any, Optional
from modelos.catalogo import Catalogo
from modelos.producto import Producto
from modelos.lote import Lote


class ControladorPDF:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.catalogo_modelo = Catalogo(db)
        self.producto_modelo = Producto(db)
        self.lote_modelo = Lote(db)

    def procesar_catalogo_manual(self, datos_extraidos: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Procesa los datos extraídos bajo confirmación manual del usuario.
        Cada elemento debe tener al menos: 'codigo', 'descripcion', 'precio_costo'.
        Puede tener 'precio_venta', 'stock' y 'fecha_vencimiento'.
        Retorna un resumen con 'nuevos' y 'actualizados'.
        """
        nuevos = 0
        actualizados = 0
        for item in datos_extraidos:
            codigo = item.get('codigo')
            if not codigo:
                continue
            prod_existente = self.producto_modelo.obtener_por_codigo(codigo)
            if not prod_existente:
                # Crear producto nuevo
                producto_id = self.producto_modelo.crear(
                    codigo=codigo,
                    descripcion=item.get('descripcion', ''),
                    precio_costo=float(item.get('precio_costo', 0)),
                    precio_venta=float(item.get('precio_venta', 0)),
                    stock_critico=0
                )
                # Si hay stock inicial y fecha de vencimiento, crear lote
                stock_valor = item.get('stock')
                if stock_valor is not None:                     # <- CORRECCIÓN
                    try:
                        cantidad = float(stock_valor)
                        if cantidad > 0:
                            fecha_venc = item.get('fecha_vencimiento')
                            if fecha_venc:
                                self.lote_modelo.crear(producto_id=producto_id,
                                                       numero_lote=None,
                                                       fecha_vencimiento=fecha_venc,
                                                       cantidad_inicial=cantidad)
                    except (ValueError, TypeError):
                        pass  # ignora si no se puede convertir
                nuevos += 1
            else:
                # Actualizar precios
                updates = {}
                if 'precio_costo' in item:
                    updates['precio_costo'] = float(item['precio_costo'])
                if 'precio_venta' in item:
                    updates['precio_venta'] = float(item['precio_venta'])
                if updates:
                    self.producto_modelo.actualizar(prod_existente['id'], **updates)
                    actualizados += 1
        return {'nuevos': nuevos, 'actualizados': actualizados}

    def procesar_catalogo_con_porcentaje(self, datos_extraidos: List[Dict[str, Any]],
                                         porcentaje_incremento: float) -> Dict[str, int]:
        """
        Igual que el manual, pero calcula el precio_venta aplicando un porcentaje
        sobre el precio_costo (precio_venta = precio_costo * (1 + porcentaje/100)).
        """
        nuevos = 0
        actualizados = 0
        for item in datos_extraidos:
            codigo = item.get('codigo')
            if not codigo:
                continue
            precio_costo = float(item.get('precio_costo', 0))
            precio_venta = precio_costo * (1 + porcentaje_incremento / 100.0)

            prod_existente = self.producto_modelo.obtener_por_codigo(codigo)
            if not prod_existente:
                producto_id = self.producto_modelo.crear(
                    codigo=codigo,
                    descripcion=item.get('descripcion', ''),
                    precio_costo=precio_costo,
                    precio_venta=precio_venta,
                    stock_critico=0
                )
                stock_valor = item.get('stock')
                if stock_valor is not None:                     # <- CORRECCIÓN
                    try:
                        cantidad = float(stock_valor)
                        if cantidad > 0:
                            fecha_venc = item.get('fecha_vencimiento')
                            if fecha_venc:
                                self.lote_modelo.crear(producto_id=producto_id,
                                                       numero_lote=None,
                                                       fecha_vencimiento=fecha_venc,
                                                       cantidad_inicial=cantidad)
                    except (ValueError, TypeError):
                        pass
                nuevos += 1
            else:
                # Actualizar costo y recalcular venta con el porcentaje
                self.producto_modelo.actualizar(prod_existente['id'],
                                                precio_costo=precio_costo,
                                                precio_venta=precio_venta)
                actualizados += 1
        return {'nuevos': nuevos, 'actualizados': actualizados}

    def registrar_importacion(self, nombre_archivo: str, procesado_por: str,
                              total_nuevos: int, total_actualizados: int,
                              observaciones: str = None) -> int:
        """Guarda un registro de la importación en la tabla catalogo_importaciones."""
        return self.catalogo_modelo.registrar_importacion(
            nombre_archivo=nombre_archivo,
            procesado_por=procesado_por,
            total_productos_nuevos=total_nuevos,
            total_actualizaciones=total_actualizados,
            observaciones=observaciones
        )