"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Lote con UUID.
Soporta transacciones externas mediante el parámetro 'commit'.
"""

import sqlite3
import uuid
from datetime import date, timedelta
from typing import List, Optional, Dict, Any

class Lote:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, producto_id: int, numero_lote: str = None,
              fecha_vencimiento: str = None, cantidad_inicial: float = 0.0,
              fecha_ingreso: str = None) -> str:
        """Crea un nuevo lote y actualiza el stock del producto."""
        lote_id = str(uuid.uuid4())
        if not fecha_ingreso:
            fecha_ingreso = date.today().isoformat()
        query = """INSERT INTO lotes (id, producto_id, numero_lote, fecha_vencimiento,
                    cantidad_inicial, cantidad_actual, fecha_ingreso)
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (lote_id, producto_id, numero_lote, fecha_vencimiento,
                            cantidad_inicial, cantidad_inicial, fecha_ingreso))
        self.db.commit()
        self._actualizar_stock_producto(producto_id)
        return lote_id

    def _actualizar_stock_producto(self, producto_id: int, commit: bool = True):
        """Recalcula el stock_actual del producto sumando las cantidades actuales de sus lotes."""
        cur = self.db.cursor()
        cur.execute("""SELECT SUM(cantidad_actual) FROM lotes
                        WHERE producto_id = ? AND cantidad_actual > 0""", (producto_id,))
        stock = cur.fetchone()[0] or 0.0
        cur.execute("UPDATE productos SET stock_actual = ? WHERE id = ?", (stock, producto_id))
        if commit:
            self.db.commit()

    def obtener_por_id(self, lote_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM lotes WHERE id = ?", (lote_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_producto(self, producto_id: int) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM lotes WHERE producto_id = ? ORDER BY fecha_vencimiento",
                    (producto_id,))
        return [dict(row) for row in cur.fetchall()]

    def reducir_cantidad(self, lote_id: str, cantidad_a_restar: float, commit: bool = True) -> bool:
        """
        Descarga stock de un lote (FIFO) y actualiza el stock del producto.
        :param commit: Si es True, hace commit de los cambios. False delega el commit a la transacción.
        """
        cur = self.db.cursor()
        cur.execute("SELECT cantidad_actual FROM lotes WHERE id = ?", (lote_id,))
        row = cur.fetchone()
        if not row or row['cantidad_actual'] < cantidad_a_restar:
            return False
        nueva_cantidad = row['cantidad_actual'] - cantidad_a_restar
        cur.execute("UPDATE lotes SET cantidad_actual = ? WHERE id = ?", (nueva_cantidad, lote_id))
        if commit:
            self.db.commit()
        cur.execute("SELECT producto_id FROM lotes WHERE id = ?", (lote_id,))
        prod_row = cur.fetchone()
        if prod_row:
            self._actualizar_stock_producto(prod_row['producto_id'], commit=commit)
        return True

    def lotes_por_vencer(self, dias_anticipacion: int = 14) -> List[Dict[str, Any]]:
        hoy = date.today()
        limite = hoy + timedelta(days=dias_anticipacion)
        cur = self.db.cursor()
        cur.execute("""SELECT lotes.*, productos.descripcion as producto_desc
                        FROM lotes JOIN productos ON lotes.producto_id = productos.id
                        WHERE lotes.fecha_vencimiento BETWEEN ? AND ?
                        AND lotes.cantidad_actual > 0""",
                    (hoy.isoformat(), limite.isoformat()))
        return [dict(row) for row in cur.fetchall()]