"""
Código Crítico - Tercer Semestre Año 2026
Motor de alertas. Centraliza la verificación de:
- Productos con stock por debajo del mínimo.
- Lotes próximos a vencer (por defecto 14 días).
- Clientes con cuenta corriente cerca o sobre su límite de crédito.
Devuelve listas de alertas para mostrar en la interfaz o registrar.
"""

import sqlite3
from datetime import date, timedelta
from typing import List, Dict, Any

class AlertasManager:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def productos_stock_critico(self) -> List[Dict[str, Any]]:
        """Productos activos cuyo stock_actual <= stock_critico."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, codigo, descripcion, stock_actual, stock_critico
            FROM productos
            WHERE activo = 1 AND stock_actual <= stock_critico
        """)
        return [dict(row) for row in cur.fetchall()]

    def lotes_por_vencer(self, dias_anticipacion: int = 14) -> List[Dict[str, Any]]:
        """
        Lotes con cantidad actual > 0 y fecha de vencimiento entre hoy
        y hoy + dias_anticipacion.
        """
        hoy = date.today()
        limite = hoy + timedelta(days=dias_anticipacion)
        cur = self.db.cursor()
        cur.execute("""
            SELECT l.id, l.producto_id, p.descripcion as producto_desc,
                   l.numero_lote, l.fecha_vencimiento, l.cantidad_actual
            FROM lotes l
            JOIN productos p ON l.producto_id = p.id
            WHERE l.cantidad_actual > 0
              AND l.fecha_vencimiento BETWEEN ? AND ?
        """, (hoy.isoformat(), limite.isoformat()))
        return [dict(row) for row in cur.fetchall()]

    def clientes_limite_credito(self, porcentaje_min: float = 80.0) -> List[Dict[str, Any]]:
        """
        Clientes activos con límite > 0 cuyo saldo_cc supera el porcentaje_min % del límite.
        Incluye el porcentaje utilizado.
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, razon_social, cuit, limite_credito, saldo_cuenta_corriente,
                   ROUND(saldo_cuenta_corriente * 100.0 / limite_credito, 1) as porcentaje_uso
            FROM clientes
            WHERE activo = 1 AND limite_credito > 0
              AND saldo_cuenta_corriente >= (limite_credito * ? / 100.0)
            ORDER BY porcentaje_uso DESC
        """, (porcentaje_min,))
        return [dict(row) for row in cur.fetchall()]

    def obtener_todas_alertas(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna un diccionario con las tres categorías de alertas.
        """
        return {
            'stock_critico': self.productos_stock_critico(),
            'lotes_por_vencer': self.lotes_por_vencer(),
            'clientes_al_limite': self.clientes_limite_credito()
        }