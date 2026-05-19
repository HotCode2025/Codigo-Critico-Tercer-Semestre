"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Lote: representa y gestiona la tabla 'lotes' y actualiza el stock del producto.
"""
import sqlite3
from datetime import date, datetime
from typing import List, Optional, Dict, Any

class Lote:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, producto_id: int, numero_lote: str, fecha_vencimiento: str,
              cantidad_inicial: float, fecha_ingreso: str = None) -> int:
        """Inserta un lote y suma al stock_actual del producto."""
        if not fecha_ingreso:
            fecha_ingreso = date.today().isoformat()
        query = """INSERT INTO lotes (producto_id, numero_lote, fecha_vencimiento,
                    cantidad_inicial, cantidad_actual, fecha_ingreso)
                    VALUES (?, ?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (producto_id, numero_lote, fecha_vencimiento,
                            cantidad_inicial, cantidad_inicial, fecha_ingreso))
        self.db.commit()
        lote_id = cur.lastrowid

        # Actualizar stock del producto
        self._actualizar_stock_producto(producto_id)
        return lote_id

    def _actualizar_stock_producto(self, producto_id: int):
        cur = self.db.cursor()
        cur.execute("""SELECT SUM(cantidad_actual) FROM lotes
                        WHERE producto_id = ? AND cantidad_actual > 0""", (producto_id,))
        stock = cur.fetchone()[0] or 0.0
        cur.execute("UPDATE productos SET stock_actual = ? WHERE id = ?",
                    (stock, producto_id))
        self.db.commit()

    def obtener_por_id(self, lote_id: int) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM lotes WHERE id = ?", (lote_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_producto(self, producto_id: int) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM lotes WHERE producto_id = ? ORDER BY fecha_vencimiento",
                    (producto_id,))
        return [dict(row) for row in cur.fetchall()]

    def reducir_cantidad(self, lote_id: int, cantidad_a_restar: float) -> bool:
        """Descarga stock de un lote (por venta/rotura) y actualiza el producto."""
        cur = self.db.cursor()
        cur.execute("SELECT cantidad_actual FROM lotes WHERE id = ?", (lote_id,))
        row = cur.fetchone()
        if not row or row['cantidad_actual'] < cantidad_a_restar:
            return False

        nueva_cantidad = row['cantidad_actual'] - cantidad_a_restar
        cur.execute("UPDATE lotes SET cantidad_actual = ? WHERE id = ?",
                    (nueva_cantidad, lote_id))
        self.db.commit()

        # Recalcular stock del producto asociado
        cur.execute("SELECT producto_id FROM lotes WHERE id = ?", (lote_id,))
        prod_row = cur.fetchone()
        if prod_row:
            self._actualizar_stock_producto(prod_row['producto_id'])
        return True

    def lotes_por_vencer(self, dias_anticipacion: int = 14) -> List[Dict[str, Any]]:
        """Lotes con fecha de vencimiento entre hoy y hoy + dias_anticipacion y con stock."""
        hoy = date.today()
        limite = hoy.replace(day=hoy.day + dias_anticipacion)  # simplificación, usar timedelta
        from datetime import timedelta
        limite = hoy + timedelta(days=dias_anticipacion)
        cur = self.db.cursor()
        cur.execute("""SELECT lotes.*, productos.descripcion as producto_desc
                        FROM lotes JOIN productos ON lotes.producto_id = productos.id
                        WHERE lotes.fecha_vencimiento BETWEEN ? AND ?
                        AND lotes.cantidad_actual > 0""",
                    (hoy.isoformat(), limite.isoformat()))
        return [dict(row) for row in cur.fetchall()]