"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Stock.
Gestiona lotes, movimientos de stock, vencimientos y alertas.
"""
import sqlite3
from datetime import date, timedelta
from typing import List, Dict, Any
from modelos.lote import Lote
from modelos.producto import Producto


class ControladorStock:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.lote_modelo = Lote(db)
        self.producto_modelo = Producto(db)

    def crear_lote(self, producto_id: int, numero_lote: str = None,
                   fecha_vencimiento: str = None, cantidad_inicial: float = 0.0) -> int:
        """Crea un nuevo lote para un producto, validando cantidad y fecha."""
        if not producto_id or not self.producto_modelo.obtener_por_id(producto_id):
            raise ValueError("Producto no válido.")
        if cantidad_inicial <= 0:
            raise ValueError("La cantidad inicial debe ser mayor que cero.")
        if not fecha_vencimiento:
            raise ValueError("La fecha de vencimiento es obligatoria.")
        # Intentar parsear la fecha
        try:
            date.fromisoformat(fecha_vencimiento)
        except ValueError:
            raise ValueError("Formato de fecha inválido (use AAAA-MM-DD).")

        return self.lote_modelo.crear(producto_id=producto_id,
                                      numero_lote=numero_lote.strip() if numero_lote else None,
                                      fecha_vencimiento=fecha_vencimiento,
                                      cantidad_inicial=cantidad_inicial)

    def descontar_stock(self, producto_id: int, cantidad: float) -> bool:
        """Reduce el stock del producto descontando de los lotes más próximos a vencer (FIFO)."""
        # Buscar lotes con stock, ordenados por fecha de vencimiento ascendente
        lotes = self.lote_modelo.listar_por_producto(producto_id)
        lotes_con_stock = [l for l in lotes if l['cantidad_actual'] > 0]
        lotes_con_stock.sort(key=lambda l: l['fecha_vencimiento'])

        restante = cantidad
        for lote in lotes_con_stock:
            if restante <= 0:
                break
            disponible = lote['cantidad_actual']
            a_restar = min(disponible, restante)
            self.lote_modelo.reducir_cantidad(lote['id'], a_restar)
            restante -= a_restar

        if restante > 0:
            raise ValueError(f"Stock insuficiente. Faltan {restante} unidades.")
        return True

    def obtener_lotes_por_vencer(self, dias: int = 14) -> List[Dict[str, Any]]:
        """Lotes con vencimiento dentro de los próximos 'dias' días."""
        return self.lote_modelo.lotes_por_vencer(dias_anticipacion=dias)

    def stock_actual_producto(self, producto_id: int) -> float:
        prod = self.producto_modelo.obtener_por_id(producto_id)
        return prod['stock_actual'] if prod else 0.0