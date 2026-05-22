"""
Código Crítico - Tercer Semestre Año 2026
Vista de Reportes. Muestra reportes predefinidos: ganancias, deuda, ventas por preventista, etc.
"""

import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QComboBox, QFormLayout)
from PySide6.QtCore import Qt
from datetime import date


class VistaReportes(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Reportes")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Selección de tipo de reporte
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems([
            "Productos más vendidos por mes",
            "Clientes con cuenta corriente al límite",
            "Ganancia por producto (costo vs venta)",
            "Mercadería vendida sin cobrar",
            "Ventas por preventista"
        ])
        layout.addWidget(QLabel("Seleccione reporte:"))
        layout.addWidget(self.cmb_tipo)

        btn_generar = QPushButton("Generar Reporte")
        btn_generar.clicked.connect(self.generar_reporte)
        layout.addWidget(btn_generar)

        self.tabla = QTableWidget()
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla)

    def generar_reporte(self):
        indice = self.cmb_tipo.currentIndex()
        if indice == 0:
            self.reporte_productos_mes()
        elif indice == 1:
            self.reporte_cc_al_limite()
        elif indice == 2:
            self.reporte_ganancia()
        elif indice == 3:
            self.reporte_deuda_sin_cobrar()
        elif indice == 4:
            self.reporte_ventas_por_preventista()

    def reporte_productos_mes(self):
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
        self._mostrar_resultados(cur, ["Producto", "Mes", "Cantidad Vendida"])

    def reporte_cc_al_limite(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT razon_social, cuit, limite_credito, saldo_cuenta_corriente,
                   ROUND(saldo_cuenta_corriente*100.0/limite_credito, 1) as porcentaje
            FROM clientes
            WHERE activo=1 AND limite_credito > 0
              AND saldo_cuenta_corriente >= 0.8 * limite_credito
            ORDER BY porcentaje DESC
        """)
        self._mostrar_resultados(cur, ["Cliente", "CUIT", "Límite", "Saldo CC", "% utilizado"])

    def reporte_ganancia(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion,
                   p.precio_costo,
                   AVG(fd.precio_unitario) as precio_venta_promedio,
                   SUM(fd.cantidad) as cantidad_vendida,
                   SUM((fd.precio_unitario - p.precio_costo) * fd.cantidad) as ganancia_total
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            GROUP BY p.id
            ORDER BY ganancia_total DESC
        """)
        self._mostrar_resultados(cur, ["Producto", "Costo", "Precio Vta. Prom.",
                                       "Cantidad", "Ganancia Total"])

    def reporte_deuda_sin_cobrar(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT c.razon_social, f.numero_factura, f.total,
                   (f.total - COALESCE(SUM(cob.importe), 0)) as pendiente
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            LEFT JOIN cuenta_corriente_movimientos ccm
                   ON ccm.referencia_id = f.id AND ccm.tipo_movimiento = 'COBRO'
            WHERE f.estado = 'EMITIDA'
            GROUP BY f.id
            HAVING pendiente > 0
            ORDER BY pendiente DESC
        """)
        self._mostrar_resultados(cur, ["Cliente", "Factura", "Total", "Pendiente"])

    def reporte_ventas_por_preventista(self):
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
        self._mostrar_resultados(cur, ["Preventista", "Cant. Facturas", "Total Vendido"])

    def _mostrar_resultados(self, cursor, encabezados):
        resultados = [dict(row) for row in cursor.fetchall()]
        self.tabla.clear()
        self.tabla.setColumnCount(len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        self.tabla.setRowCount(len(resultados))
        for fila, res in enumerate(resultados):
            for col, key in enumerate(res.keys()):
                self.tabla.setItem(fila, col, QTableWidgetItem(str(res[key])))