"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Reportes.
Genera los datos necesarios para los distintos reportes predefinidos.
"""
import sqlite3
from typing import List, Dict, Any


class ControladorReportes:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

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