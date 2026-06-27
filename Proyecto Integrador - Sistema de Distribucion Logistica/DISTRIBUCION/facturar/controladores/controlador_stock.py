"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Stock – ahora sincroniza lotes directamente con Turso.
"""

import sqlite3
from datetime import date, timedelta
from typing import List, Dict, Any
from modelos.lote import Lote
from modelos.producto import Producto
from utilidades.central_sync import enviar_a_turso


class ControladorStock:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.lote_modelo = Lote(db)
        self.producto_modelo = Producto(db)

    def crear_lote(self, producto_id: int, numero_lote: str = None,
                   fecha_vencimiento: str = None, cantidad_inicial: float = 0.0) -> str:
        """Crea un nuevo lote y lo replica en Turso."""
        if not producto_id or not self.producto_modelo.obtener_por_id(producto_id):
            raise ValueError("Producto no válido.")
        if cantidad_inicial <= 0:
            raise ValueError("La cantidad inicial debe ser mayor que cero.")
        if not fecha_vencimiento:
            raise ValueError("La fecha de vencimiento es obligatoria.")
        try:
            date.fromisoformat(fecha_vencimiento)
        except ValueError:
            raise ValueError("Formato de fecha inválido (use AAAA-MM-DD).")

        lote_id = self.lote_modelo.crear(
            producto_id=producto_id,
            numero_lote=numero_lote.strip() if numero_lote else None,
            fecha_vencimiento=fecha_vencimiento,
            cantidad_inicial=cantidad_inicial
        )

        enviar_a_turso(
            """INSERT INTO lotes (id, producto_id, numero_lote, fecha_vencimiento,
               cantidad_inicial, cantidad_actual, fecha_ingreso)
               VALUES (?, ?, ?, ?, ?, ?, date('now'))""",
            [lote_id, producto_id,
             numero_lote.strip() if numero_lote else None,
             fecha_vencimiento, cantidad_inicial, cantidad_inicial]
        )

        return lote_id

    def descontar_stock(self, producto_id: int, cantidad: float) -> bool:
        """Reduce el stock del producto (FIFO) y replica los cambios en Turso."""
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
            # Replicar actualización en Turso
            enviar_a_turso(
                "UPDATE lotes SET cantidad_actual = cantidad_actual - ? WHERE id = ?",
                [a_restar, lote['id']]
            )
            restante -= a_restar

        if restante > 0:
            raise ValueError(f"Stock insuficiente. Faltan {restante} unidades.")
        return True

    def obtener_lotes_por_vencer(self, dias: int = 14) -> List[Dict[str, Any]]:
        return self.lote_modelo.lotes_por_vencer(dias_anticipacion=dias)

    def stock_actual_producto(self, producto_id: int) -> float:
        prod = self.producto_modelo.obtener_por_id(producto_id)
        return prod['stock_actual'] if prod else 0.0

    # ============================================================
    # MÉTODOS ADICIONALES PARA COMPATIBILIDAD
    # ============================================================

    def obtener_producto_por_codigo(self, codigo_producto: str) -> Dict[str, Any]:
        """
        Obtiene un producto por su código.
        :param codigo_producto: Código del producto.
        :return: Diccionario con los datos del producto.
        """
        return self.producto_modelo.obtener_por_codigo(codigo_producto)

    def listar_productos_con_stock(self) -> List[Dict[str, Any]]:
        """
        Lista todos los productos activos con su stock actual.
        :return: Lista de productos.
        """
        return self.producto_modelo.listar_todos(solo_activos=True)

    def ajustar_stock(self, producto_id: int, cantidad: float, operacion: str = 'sumar') -> bool:
        """
        Ajusta el stock de un producto manualmente.
        :param producto_id: ID del producto.
        :param cantidad: Cantidad a sumar o restar.
        :param operacion: 'sumar' o 'restar'.
        :return: True si se realizó el ajuste.
        """
        if operacion not in ['sumar', 'restar']:
            raise ValueError("Operación debe ser 'sumar' o 'restar'")
        
        producto = self.producto_modelo.obtener_por_id(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado")
        
        nuevo_stock = producto['stock_actual'] + cantidad if operacion == 'sumar' else producto['stock_actual'] - cantidad
        
        if nuevo_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        
        self.producto_modelo.actualizar(producto_id, stock_actual=nuevo_stock)
        
        # Si es una suma, crear un lote de ingreso
        if operacion == 'sumar' and cantidad > 0:
            import uuid
            lote_id = str(uuid.uuid4())
            fecha_vencimiento = (date.today() + timedelta(days=365)).isoformat()
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO lotes (id, producto_id, numero_lote, fecha_vencimiento,
                                   cantidad_inicial, cantidad_actual, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, date('now'))
            """, (lote_id, producto_id, f"AJUSTE-{producto_id}-001", fecha_vencimiento, cantidad, cantidad))
            self.db.commit()
            
            enviar_a_turso(
                """INSERT INTO lotes (id, producto_id, numero_lote, fecha_vencimiento,
                   cantidad_inicial, cantidad_actual, fecha_ingreso)
                   VALUES (?, ?, ?, ?, ?, ?, date('now'))""",
                [lote_id, producto_id, f"AJUSTE-{producto_id}-001", fecha_vencimiento, cantidad, cantidad]
            )
        
        return True