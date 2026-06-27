"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Factura con UUID.
Soporta transacciones externas mediante el parámetro 'commit'.
"""

import sqlite3
import uuid
from datetime import date
from typing import List, Optional, Dict, Any

class Factura:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, cliente_id: int, numero_factura: str,
              tipo_comprobante: str = 'B', preventista_id: int = None,
              observaciones: str = None, nota_venta_id: str = None,
              commit: bool = True) -> str:
        """
        Crea una factura fiscal (sin detalles).
        :param commit: Si es True, hace commit inmediato.
        """
        nuevo_id = str(uuid.uuid4())
        query = """INSERT INTO facturas (id, cliente_id, preventista_id, tipo_comprobante,
                    numero_factura, fecha, subtotal, iva, tasa_municipal, total,
                    observaciones, nota_venta_id, estado)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0, ?, ?, 'EMITIDA')"""
        cur = self.db.cursor()
        cur.execute(query, (nuevo_id, cliente_id, preventista_id, tipo_comprobante,
                            numero_factura, date.today().isoformat(),
                            observaciones, nota_venta_id))
        if commit:
            self.db.commit()
        return nuevo_id

    def agregar_detalle(self, factura_id: str, producto_id: int,
                        cantidad: float, precio_unitario: float,
                        commit: bool = True) -> str:
        """
        Agrega una línea al detalle de la factura y recalcula totales.
        :param commit: Si es True, hace commit inmediato.
        """
        detalle_id = str(uuid.uuid4())
        query = """INSERT INTO factura_detalle (id, factura_id, producto_id,
                    cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (detalle_id, factura_id, producto_id, cantidad, precio_unitario))
        if commit:
            self.db.commit()
        self._recalcular_totales(factura_id, cliente_id=None, commit=commit)
        return detalle_id

    def _recalcular_totales(self, factura_id: str, cliente_id: int = None, commit: bool = True):
        """Calcula subtotal, IVA, tasa municipal y total de la factura."""
        cur = self.db.cursor()
        cur.execute("SELECT cliente_id FROM facturas WHERE id = ?", (factura_id,))
        row = cur.fetchone()
        if not row:
            return
        if cliente_id is None:
            cliente_id = row['cliente_id']

        cur.execute("""SELECT SUM(cantidad * precio_unitario)
                        FROM factura_detalle WHERE factura_id = ?""", (factura_id,))
        subtotal = cur.fetchone()[0] or 0.0

        cur.execute("SELECT condicion_iva FROM clientes WHERE id = ?", (cliente_id,))
        cli = cur.fetchone()
        iva_porcent = 0.21 if (cli and cli['condicion_iva'] == 'RI') else 0.0
        iva = subtotal * iva_porcent

        cur.execute("SELECT aplica_tasa_municipal FROM clientes WHERE id = ?", (cliente_id,))
        cli2 = cur.fetchone()
        tasa_pct = 0.0
        if cli2 and cli2['aplica_tasa_municipal']:
            cur.execute("SELECT tasa_municipal_porcentaje FROM parametros WHERE id = 1")
            param = cur.fetchone()
            if param:
                tasa_pct = param['tasa_municipal_porcentaje'] / 100.0
        tasa_municipal = subtotal * tasa_pct

        total = subtotal + iva + tasa_municipal

        cur.execute("""UPDATE facturas SET subtotal = ?, iva = ?, tasa_municipal = ?,
                        total = ? WHERE id = ?""",
                    (subtotal, iva, tasa_municipal, total, factura_id))
        if commit:
            self.db.commit()

        self._registrar_movimiento_cc(factura_id, cliente_id, total, commit=commit)

    def _registrar_movimiento_cc(self, factura_id: str, cliente_id: int, importe: float,
                                 commit: bool = True):
        """Registra el movimiento en cuenta corriente y actualiza el saldo del cliente."""
        cur = self.db.cursor()
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        if not row:
            return
        nuevo_saldo = row['saldo_cuenta_corriente'] + importe
        cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?",
                    (nuevo_saldo, cliente_id))

        mov_id = str(uuid.uuid4())
        cur.execute("""INSERT INTO cuenta_corriente_movimientos
                       (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe,
                        saldo_resultante)
                       VALUES (?, ?, ?, 'FACTURA', ?, ?, ?)""",
                    (mov_id, cliente_id, date.today().isoformat(), factura_id, importe, nuevo_saldo))
        if commit:
            self.db.commit()

    def obtener_por_id(self, factura_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM facturas WHERE id = ?", (factura_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM facturas WHERE cliente_id = ? ORDER BY fecha", (cliente_id,))
        return [dict(row) for row in cur.fetchall()]