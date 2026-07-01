"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Reportes.
Genera los datos necesarios para los distintos reportes predefinidos
y permite exportar a Excel/CSV.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any


class ControladorReportes:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def productos_mas_vendidos_por_mes(self) -> List[Dict[str, Any]]:
        """Productos más vendidos agrupados por mes."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion as producto,
                   strftime('%Y-%m', f.fecha) as mes,
                   SUM(fd.cantidad) as total_vendido
            FROM factura_detalle fd
            JOIN facturas f ON fd.factura_id = f.id
            JOIN productos p ON fd.producto_id = p.id
            GROUP BY p.id, mes
            ORDER BY mes DESC, total_vendido DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def clientes_con_cc_al_limite(self) -> List[Dict[str, Any]]:
        """Clientes con saldo >= 80% del límite de crédito."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT razon_social, cuit, limite_credito, saldo_cuenta_corriente,
                   ROUND(saldo_cuenta_corriente*100.0/limite_credito, 1) as porcentaje
            FROM clientes
            WHERE activo=1 AND limite_credito > 0
              AND saldo_cuenta_corriente >= 0.8 * limite_credito
            ORDER BY porcentaje DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def ganancia_por_producto(self) -> List[Dict[str, Any]]:
        """Ganancia total (venta - costo) por producto basado en facturas emitidas."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion as producto,
                   p.precio_costo,
                   AVG(fd.precio_unitario) as precio_venta_promedio,
                   SUM(fd.cantidad) as cantidad_vendida,
                   SUM((fd.precio_unitario - p.precio_costo) * fd.cantidad) as ganancia_total
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            GROUP BY p.id
            ORDER BY ganancia_total DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def mercaderia_vendida_sin_cobrar(self) -> List[Dict[str, Any]]:
        """Facturas cuyo monto no ha sido completamente cubierto por cobros."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT c.razon_social, f.numero_factura, f.total,
                   (f.total - COALESCE(SUM(ccm.importe), 0)) as pendiente
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            LEFT JOIN cuenta_corriente_movimientos ccm
                   ON ccm.referencia_id = f.id AND ccm.tipo_movimiento = 'COBRO'
            WHERE f.estado = 'EMITIDA'
            GROUP BY f.id
            HAVING pendiente > 0
            ORDER BY pendiente DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def ventas_por_preventista(self) -> List[Dict[str, Any]]:
        """Total de ventas por preventista en el período completo."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.nombre || ' ' || p.apellido as preventista,
                   COUNT(f.id) as cantidad_facturas,
                   SUM(f.total) as total_ventas
            FROM facturas f
            JOIN preventistas p ON f.preventista_id = p.id
            GROUP BY p.id
            ORDER BY total_ventas DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def ventas_por_periodo(self, fecha_desde: str = None, fecha_hasta: str = None) -> List[Dict[str, Any]]:
        """Ventas filtradas por período."""
        query = """
            SELECT f.fecha, f.numero_factura, c.razon_social, 
                   f.total, f.tipo_comprobante
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE 1=1
        """
        params = []
        
        if fecha_desde:
            query += " AND f.fecha >= ?"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND f.fecha <= ?"
            params.append(fecha_hasta)
        
        query += " ORDER BY f.fecha DESC"
        
        cur = self.db.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def resumen_ventas_diarias(self, dias: int = 30) -> List[Dict[str, Any]]:
        """Resumen de ventas de los últimos N días."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT fecha, 
                   COUNT(*) as cantidad_facturas,
                   SUM(total) as total_ventas,
                   AVG(total) as promedio_venta
            FROM facturas
            WHERE fecha >= date('now', ?)
            GROUP BY fecha
            ORDER BY fecha DESC
        """, (f'-{dias} days',))
        return [dict(row) for row in cur.fetchall()]

    def productos_stock_critico(self) -> List[Dict[str, Any]]:
        """Productos con stock por debajo del mínimo."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT codigo, descripcion, stock_actual, stock_critico,
                   unidad_medida, precio_venta
            FROM productos
            WHERE activo = 1 AND stock_actual <= stock_critico
            ORDER BY (stock_critico - stock_actual) DESC
        """)
        return [dict(row) for row in cur.fetchall()]

    def exportar_a_excel(self, datos: List[Dict[str, Any]], nombre_reporte: str, columnas: List[str] = None) -> str:
        """
        Exporta datos a un archivo Excel.
        
        Args:
            datos: Lista de diccionarios con los datos a exportar
            nombre_reporte: Nombre base del archivo
            columnas: Lista de columnas a incluir (si es None, usa todas)
        
        Returns:
            Ruta del archivo generado
        """
        try:
            import pandas as pd
            
            # Si no se especifican columnas, usar todas las keys del primer elemento
            if not columnas and datos:
                columnas = list(datos[0].keys())
            
            # Crear DataFrame
            df = pd.DataFrame(datos)
            
            # Filtrar columnas si es necesario
            if columnas:
                df = df[columnas]
            
            # Crear directorio si no existe
            os.makedirs("reportes", exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{nombre_reporte}_{timestamp}.xlsx"
            ruta = os.path.join("reportes", nombre_archivo)
            
            # Exportar a Excel
            df.to_excel(ruta, index=False, sheet_name=nombre_reporte[:31])
            
            return ruta
            
        except ImportError:
            # Fallback a CSV si no hay pandas
            import csv
            
            os.makedirs("reportes", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{nombre_reporte}_{timestamp}.csv"
            ruta = os.path.join("reportes", nombre_archivo)
            
            if not columnas and datos:
                columnas = list(datos[0].keys())
            
            with open(ruta, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=columnas)
                writer.writeheader()
                writer.writerows(datos)
            
            return ruta

    def exportar_reporte(self, tipo_reporte: str) -> str:
        """
        Exporta un reporte predefinido a Excel.
        
        Args:
            tipo_reporte: Tipo de reporte ('productos', 'clientes', 'ganancia', 'ventas', 'stock')
        
        Returns:
            Ruta del archivo generado
        """
        reportes = {
            'productos': (self.productos_mas_vendidos_por_mes, 
                         "productos_mas_vendidos",
                         ["producto", "mes", "total_vendido"]),
            'clientes': (self.clientes_con_cc_al_limite,
                        "clientes_limite_credito",
                        ["razon_social", "cuit", "limite_credito", "saldo_cuenta_corriente", "porcentaje"]),
            'ganancia': (self.ganancia_por_producto,
                        "ganancia_por_producto",
                        ["producto", "precio_costo", "precio_venta_promedio", "cantidad_vendida", "ganancia_total"]),
            'ventas': (self.ventas_por_preventista,
                      "ventas_por_preventista",
                      ["preventista", "cantidad_facturas", "total_ventas"]),
            'stock': (self.productos_stock_critico,
                     "productos_stock_critico",
                     ["codigo", "descripcion", "stock_actual", "stock_critico", "unidad_medida", "precio_venta"])
        }
        
        if tipo_reporte not in reportes:
            raise ValueError(f"Tipo de reporte no válido: {tipo_reporte}")
        
        func, nombre, columnas = reportes[tipo_reporte]
        datos = func()
        
        return self.exportar_a_excel(datos, nombre, columnas)