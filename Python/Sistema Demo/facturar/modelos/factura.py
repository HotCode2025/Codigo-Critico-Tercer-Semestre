"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Factura: gestiona facturas fiscales y sus detalles, con movimiento en cuenta corriente.
"""
import sqlite3
from datetime import date
from typing import List, Optional, Dict, Any

class Factura:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, cliente_id: int, numero_factura: str,
              tipo_comprobante: str = 'B', preventista_id: int = None,
              observaciones: str = None, nota_venta_id: int = None) -> int:
        query = """INSERT INTO facturas (cliente_id, preventista_id, tipo_comprobante,
                    numero_factura, fecha, subtotal, iva, tasa_municipal, total,
                    observaciones, nota_venta_id, estado)
                    VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0, ?, ?, 'EMITIDA')"""
        cur = self.db.cursor()
        cur.execute(query, (cliente_id, preventista_id, tipo_comprobante,
                            numero_factura, date.today().isoformat(),
                            observaciones, nota_venta_id))
        self.db.commit()
        return cur.lastrowid

    def agregar_detalle(self, factura_id: int, producto_id: int,
                        cantidad: float, precio_unitario: float) -> int:
        query = """INSERT INTO factura_detalle (factura_id, producto_id,
                    cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (factura_id, producto_id, cantidad, precio_unitario))
        self.db.commit()
        # Recalcular totales de la factura
        self._recalcular_totales(factura_id, cliente_id=None)  # cliente_id se obtiene después
        return cur.lastrowid

    def _recalcular_totales(self, factura_id: int, cliente_id: int = None):
        """Calcula subtotal, iva, tasa municipal y total, luego actualiza."""
        cur = self.db.cursor()
        # Obtener datos de la factura y cliente si no se pasó
        cur.execute("SELECT cliente_id FROM facturas WHERE id = ?", (factura_id,))
        row = cur.fetchone()
        if not row:
            return
        if cliente_id is None:
            cliente_id = row['cliente_id']

        cur.execute("""SELECT SUM(cantidad * precio_unitario)
                        FROM factura_detalle WHERE factura_id = ?""", (factura_id,))
        subtotal = cur.fetchone()[0] or 0.0

        # Determinar alícuota de IVA según cliente
        cur.execute("SELECT condicion_iva FROM clientes WHERE id = ?", (cliente_id,))
        cli = cur.fetchone()
        if cli:
            cond_iva = cli['condicion_iva']
            # Simplificación: RI paga 21%, EX no paga, etc.
            iva_porcent = 0.21 if cond_iva == 'RI' else 0.0
        else:
            iva_porcent = 0.21

        iva = subtotal * iva_porcent

        # Tasa municipal si corresponde
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
        self.db.commit()

        # Registrar movimiento en cuenta corriente (débito)
        self._registrar_movimiento_cc(factura_id, cliente_id, total)

    def _registrar_movimiento_cc(self, factura_id: int, cliente_id: int, importe: float):
        cur = self.db.cursor()
        # Obtener saldo actual
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        if row:
            nuevo_saldo = row['saldo_cuenta_corriente'] + importe
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?",
                        (nuevo_saldo, cliente_id))
            # Insertar movimiento
            cur.execute("""INSERT INTO cuenta_corriente_movimientos
                           (cliente_id, fecha, tipo_movimiento, referencia_id, importe,
                            saldo_resultante)
                           VALUES (?, ?, 'FACTURA', ?, ?, ?)""",
                        (cliente_id, date.today().isoformat(), factura_id, importe, nuevo_saldo))
            self.db.commit()

    def obtener_por_id(self, factura_id: int) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM facturas WHERE id = ?", (factura_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_por_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM facturas WHERE cliente_id = ? ORDER BY fecha", (cliente_id,))
        return [dict(row) for row in cur.fetchall()]