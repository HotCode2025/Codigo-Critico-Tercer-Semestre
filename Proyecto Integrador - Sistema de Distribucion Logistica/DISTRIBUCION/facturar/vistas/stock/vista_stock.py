"""
Código Crítico - Tercer Semestre Año 2026
Vista de Stock – Rediseño profesional 700x600 con gráfico, lista y reporte imprimible.
Ahora utiliza el ControladorStock para la creación de lotes.
"""

import sqlite3
from datetime import date
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QMessageBox, QHeaderView, QGroupBox, QFrame,
                               QLineEdit, QWidget, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from controladores.controlador_stock import ControladorStock
from modelos.producto import Producto

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class VistaStock(QDialog):
    """Diálogo modal para el control de stock, lotes y ventas."""

    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.stock_ctrl = ControladorStock(db)
        self.producto_modelo = Producto(db)
        self.setWindowTitle("Control de Stock y Ventas")
        self.resize(700, 600)

        self.setStyleSheet("QDialog { background-color: #F5F5F5; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Tarjeta contenedora gris
        tarjeta = QFrame()
        tarjeta.setStyleSheet(
            "QFrame { background-color: #E0E0E0; border-radius: 8px; border: 1px solid #D0D0D0; }"
        )
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(8, 8, 8, 8)

        # ====================================================
        # 1. SECCIÓN: Stock Real
        # ====================================================
        grupo_stock = QGroupBox("Stock Real (ordenado por fecha de vencimiento)")
        grupo_stock.setStyleSheet(self._estilo_groupbox())
        stock_layout = QVBoxLayout()

        self.tabla_stock = QTableWidget()
        self.tabla_stock.setColumnCount(7)
        self.tabla_stock.setHorizontalHeaderLabels(
            ["Código", "Producto", "Stock", "Crítico", "Unidad", "Próx. Venc.", "Estado"]
        )
        self.tabla_stock.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_stock.setStyleSheet(self._estilo_tabla())
        self.tabla_stock.setMaximumHeight(130)
        self.tabla_stock.selectionModel().selectionChanged.connect(self.seleccionar_producto)
        stock_layout.addWidget(self.tabla_stock)

        btn_refrescar = QPushButton("Actualizar Stock")
        btn_refrescar.setStyleSheet(self._estilo_boton())
        btn_refrescar.clicked.connect(self.cargar_stock)
        stock_layout.addWidget(btn_refrescar)

        grupo_stock.setLayout(stock_layout)
        tarjeta_layout.addWidget(grupo_stock)

        # ====================================================
        # 2. SECCIÓN: Gráfico + Lista + Reporte
        # ====================================================
        grupo_grafico = QGroupBox("Productos Más Vendidos")
        grupo_grafico.setStyleSheet(self._estilo_groupbox())
        grafico_container = QVBoxLayout()

        contenido_top = QHBoxLayout()
        self.figure = Figure(figsize=(3.0, 2.2), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(250, 180)
        contenido_top.addWidget(self.canvas)

        self.lbl_top = QLabel("Cargando...")
        self.lbl_top.setStyleSheet(
            "font-size: 8px; color: #000000; background-color: white; "
            "border: 1px solid #E0E0E0; padding: 4px;"
        )
        self.lbl_top.setWordWrap(True)
        self.lbl_top.setFixedWidth(220)
        contenido_top.addWidget(self.lbl_top)
        grafico_container.addLayout(contenido_top)

        btn_reporte = QPushButton("Imprimir Reporte Top 10")
        btn_reporte.setStyleSheet(self._estilo_boton())
        btn_reporte.clicked.connect(self.mostrar_reporte)
        grafico_container.addWidget(btn_reporte)

        grupo_grafico.setLayout(grafico_container)
        tarjeta_layout.addWidget(grupo_grafico)

        # ====================================================
        # 3. SECCIÓN: Últimas Ventas
        # ====================================================
        grupo_ventas = QGroupBox("Últimas Ventas Registradas")
        grupo_ventas.setStyleSheet(self._estilo_groupbox())
        ventas_layout = QVBoxLayout()

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(5)
        self.tabla_ventas.setHorizontalHeaderLabels(
            ["Fecha", "Factura", "Cliente", "Producto", "Cantidad"]
        )
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ventas.setStyleSheet(self._estilo_tabla())
        self.tabla_ventas.setMaximumHeight(70)
        ventas_layout.addWidget(self.tabla_ventas)

        grupo_ventas.setLayout(ventas_layout)
        tarjeta_layout.addWidget(grupo_ventas)

        # ====================================================
        # 4. SECCIÓN: Lotes
        # ====================================================
        grupo_lotes = QGroupBox("Lotes del Producto Seleccionado")
        grupo_lotes.setStyleSheet(self._estilo_groupbox())
        lotes_layout = QVBoxLayout()

        self.tabla_lotes = QTableWidget()
        self.tabla_lotes.setColumnCount(4)
        self.tabla_lotes.setHorizontalHeaderLabels(
            ["N° Lote", "Fecha Venc.", "Cant. Inicial", "Cant. Actual"]
        )
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_lotes.setStyleSheet(self._estilo_tabla())
        self.tabla_lotes.setMaximumHeight(70)
        lotes_layout.addWidget(self.tabla_lotes)

        lote_form = QHBoxLayout()
        self.txt_numero_lote = QLineEdit(); self.txt_numero_lote.setPlaceholderText("N° Lote")
        self.txt_numero_lote.setFixedWidth(90); self.txt_numero_lote.setStyleSheet(self._estilo_input())
        self.txt_fecha_venc = QLineEdit(); self.txt_fecha_venc.setPlaceholderText("AAAA-MM-DD")
        self.txt_fecha_venc.setFixedWidth(85); self.txt_fecha_venc.setStyleSheet(self._estilo_input())
        self.txt_cantidad_lote = QLineEdit(); self.txt_cantidad_lote.setPlaceholderText("Cant.")
        self.txt_cantidad_lote.setFixedWidth(55); self.txt_cantidad_lote.setStyleSheet(self._estilo_input())
        btn_crear_lote = QPushButton("+ Lote"); btn_crear_lote.setStyleSheet(self._estilo_boton())
        btn_crear_lote.clicked.connect(self.crear_lote)

        lote_form.addWidget(QLabel("Nuevo:")); lote_form.addWidget(self.txt_numero_lote)
        lote_form.addWidget(self.txt_fecha_venc)
        lote_form.addWidget(self.txt_cantidad_lote)
        lote_form.addWidget(btn_crear_lote)
        lote_form.addStretch()
        lotes_layout.addLayout(lote_form)

        grupo_lotes.setLayout(lotes_layout)
        tarjeta_layout.addWidget(grupo_lotes)

        layout.addWidget(tarjeta)

        self.producto_seleccionado_id = None
        self.cargar_stock()
        self.cargar_grafico_top()
        self.cargar_ventas()

    # =================== ESTILOS ===================
    def _estilo_input(self):
        return """
            QLineEdit {
                background-color: #FFFFFF; border: 1px solid #B0BEC5;
                border-radius: 3px; padding: 2px; font-size: 9px; color: #000000;
            }
            QLineEdit:focus { border-color: #1565C0; }
        """

    def _estilo_boton(self):
        return """
            QPushButton {
                background-color: #1565C0; color: white; border-radius: 4px;
                padding: 3px 8px; font-weight: bold; font-size: 10px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """

    def _estilo_tabla(self):
        return """
            QTableWidget {
                background-color: #FFFFFF; gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0; color: #000000; font-size: 9px;
            }
            QHeaderView::section {
                background-color: #ECEFF1; border: none; padding: 2px;
                font-weight: bold; color: #000000; font-size: 9px;
            }
            QTableWidget::item { padding: 2px; color: #000000; }
        """

    def _estilo_groupbox(self):
        return """
            QGroupBox {
                font-weight: bold; border: 1px solid #E0E0E0; border-radius: 4px;
                margin-top: 2px; padding-top: 5px; background-color: #F8F8F8;
                color: #000000; font-size: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 2px; color: #000000; }
            QGroupBox QLabel {
                background-color: black; color: white; padding: 1px 4px; border-radius: 2px;
                font-size: 9px;
            }
        """

    def _mostrar_mensaje(self, titulo, texto, icono=QMessageBox.Icon.Information, botones=QMessageBox.StandardButton.Ok):
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setIcon(icono)
        msg.setStandardButtons(botones)
        msg.setStyleSheet("""QMessageBox { background-color: white; color: black; font-size: 11px; } QLabel { color: black; background-color: transparent; font-size: 11px; } QPushButton { background-color: #1565C0; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold; } QPushButton:hover { background-color: #1976D2; }""")
        return msg.exec()

    # =================== CARGA DE DATOS ===================
    def cargar_stock(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.id, p.codigo_producto, p.descripcion, p.stock_actual, p.stock_critico,
                   p.unidad_medida,
                   (SELECT MIN(l.fecha_vencimiento) FROM lotes l
                    WHERE l.producto_id = p.id AND l.cantidad_actual > 0) as prox_venc
            FROM productos p
            WHERE p.activo = 1
            ORDER BY CASE WHEN prox_venc IS NULL THEN 1 ELSE 0 END,
                     prox_venc ASC,
                     p.descripcion ASC
        """)
        productos = cur.fetchall()
        self.tabla_stock.setRowCount(len(productos))
        for fila, prod in enumerate(productos):
            self.tabla_stock.setItem(fila, 0, QTableWidgetItem(prod['codigo_producto']))
            self.tabla_stock.setItem(fila, 1, QTableWidgetItem(prod['descripcion']))
            self.tabla_stock.setItem(fila, 2, QTableWidgetItem(f"{prod['stock_actual']:.2f}"))
            self.tabla_stock.setItem(fila, 3, QTableWidgetItem(f"{prod['stock_critico']:.2f}"))
            self.tabla_stock.setItem(fila, 4, QTableWidgetItem(prod['unidad_medida']))
            self.tabla_stock.setItem(fila, 5, QTableWidgetItem(prod['prox_venc'] or "N/A"))

            stock = prod['stock_actual']
            critico = prod['stock_critico']
            if stock <= 0:
                estado = "SIN STOCK"
                color = QColor(255, 0, 0)
            elif stock <= critico:
                estado = "BAJO"
                color = QColor(255, 165, 0)
            else:
                estado = "OK"
                color = QColor(0, 128, 0)
            item = QTableWidgetItem(estado)
            item.setForeground(color)
            self.tabla_stock.setItem(fila, 6, item)

    def cargar_grafico_top(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion, SUM(fd.cantidad) as total_vendido
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            GROUP BY p.id
            ORDER BY total_vendido DESC
            LIMIT 10
        """)
        top = cur.fetchall()
        if not top:
            self.lbl_top.setText("Sin ventas registradas.")
            self.figure.clear()
            self.canvas.draw()
            return

        lista_texto = ""
        for i, (desc, total) in enumerate(top, 1):
            lista_texto += f"{i}. {desc}: {total:.0f} unid.\n"
        self.lbl_top.setText(lista_texto)

        nombres = [t['descripcion'] for t in top]
        cantidades = [t['total_vendido'] for t in top]
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.barh(nombres[::-1], cantidades[::-1], color='#1565C0', height=0.6)
        ax.set_xlabel("Unidades vendidas", fontsize=8)
        ax.set_title("Top 10 productos más vendidos", fontsize=10)
        ax.tick_params(axis='both', labelsize=7)
        self.figure.tight_layout()
        self.canvas.draw()

    def cargar_ventas(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT f.fecha, f.numero_factura, c.razon_social, p.descripcion, fd.cantidad
            FROM factura_detalle fd
            JOIN facturas f ON fd.factura_id = f.id
            JOIN productos p ON fd.producto_id = p.id
            JOIN clientes c ON f.cliente_id = c.id
            ORDER BY f.fecha DESC, f.numero_factura DESC
            LIMIT 15
        """)
        ventas = cur.fetchall()
        self.tabla_ventas.setRowCount(len(ventas))
        for fila, v in enumerate(ventas):
            self.tabla_ventas.setItem(fila, 0, QTableWidgetItem(v['fecha']))
            self.tabla_ventas.setItem(fila, 1, QTableWidgetItem(v['numero_factura']))
            self.tabla_ventas.setItem(fila, 2, QTableWidgetItem(v['razon_social']))
            self.tabla_ventas.setItem(fila, 3, QTableWidgetItem(v['descripcion']))
            self.tabla_ventas.setItem(fila, 4, QTableWidgetItem(f"{v['cantidad']:.2f}"))

    def seleccionar_producto(self):
        indices = self.tabla_stock.selectedItems()
        if not indices:
            self.producto_seleccionado_id = None
            self.tabla_lotes.setRowCount(0)
            return
        fila = indices[0].row()
        codigo = self.tabla_stock.item(fila, 0).text()
        prod = self.producto_modelo.obtener_por_codigo(codigo)
        if prod:
            self.producto_seleccionado_id = prod['id']
            self.cargar_lotes()
        else:
            self.tabla_lotes.setRowCount(0)

    def cargar_lotes(self):
        if not self.producto_seleccionado_id:
            self.tabla_lotes.setRowCount(0)
            return
        from modelos.lote import Lote
        lote_modelo = Lote(self.db)
        lotes = lote_modelo.listar_por_producto(self.producto_seleccionado_id)
        self.tabla_lotes.setRowCount(len(lotes))
        for fila, lote in enumerate(lotes):
            self.tabla_lotes.setItem(fila, 0, QTableWidgetItem(lote['numero_lote'] or ""))
            self.tabla_lotes.setItem(fila, 1, QTableWidgetItem(lote['fecha_vencimiento']))
            self.tabla_lotes.setItem(fila, 2, QTableWidgetItem(f"{lote['cantidad_inicial']:.2f}"))
            self.tabla_lotes.setItem(fila, 3, QTableWidgetItem(f"{lote['cantidad_actual']:.2f}"))

    def crear_lote(self):
        if not self.producto_seleccionado_id:
            self._mostrar_mensaje("Error", "Seleccione un producto de la tabla de stock primero.", QMessageBox.Icon.Warning)
            return
        fecha = self.txt_fecha_venc.text().strip()
        cantidad = self.txt_cantidad_lote.text().strip()
        if not fecha or not cantidad:
            self._mostrar_mensaje("Error", "Complete fecha y cantidad.", QMessageBox.Icon.Warning)
            return
        try:
            date.fromisoformat(fecha)
            cantidad_valida = float(cantidad)
            if cantidad_valida <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self._mostrar_mensaje("Error", "Fecha o cantidad inválida.", QMessageBox.Icon.Warning)
            return
        try:
            self.stock_ctrl.crear_lote(
                producto_id=self.producto_seleccionado_id,
                numero_lote=self.txt_numero_lote.text().strip() or None,
                fecha_vencimiento=fecha,
                cantidad_inicial=cantidad_valida
            )
            self.cargar_lotes()
            self.txt_numero_lote.clear()
            self.txt_fecha_venc.clear()
            self.txt_cantidad_lote.clear()
            self.cargar_stock()
            self._mostrar_mensaje("Éxito", "Lote creado correctamente.")
        except Exception as e:
            self._mostrar_mensaje("Error", f"No se pudo crear el lote: {e}", QMessageBox.Icon.Critical)

    # =================== REPORTE IMPRIMIBLE ===================
    def mostrar_reporte(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion, SUM(fd.cantidad) as total_vendido
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            GROUP BY p.id
            ORDER BY total_vendido DESC
            LIMIT 10
        """)
        top = cur.fetchall()
        if not top:
            self._mostrar_mensaje("Sin datos", "No hay ventas registradas para generar el reporte.")
            return

        html = "<h2 style='text-align:center;'>Productos Más Vendidos</h2>"
        html += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
        html += "<tr style='background-color:#1565C0; color:white;'><th>#</th><th>Producto</th><th>Unidades Vendidas</th></tr>"
        for i, (desc, total) in enumerate(top, 1):
            html += f"<tr><td>{i}</td><td>{desc}</td><td style='text-align:right;'>{total:.0f}</td></tr>"
        html += "</table>"

        preview = QDialog(self)
        preview.setWindowTitle("Vista previa del reporte - Productos más vendidos")
        preview.resize(500, 400)
        layout = QVBoxLayout(preview)
        visor = QTextEdit(); visor.setReadOnly(True); visor.setHtml(html)
        layout.addWidget(visor)

        btn_layout = QHBoxLayout()
        btn_imprimir = QPushButton("Imprimir"); btn_imprimir.setStyleSheet(self._estilo_boton())
        btn_cerrar = QPushButton("Cerrar"); btn_cerrar.setStyleSheet(self._estilo_boton())

        def imprimir_reporte():
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, preview)
            if dialog.exec() == QPrintDialog.Accepted:
                visor.print_(printer)

        btn_imprimir.clicked.connect(imprimir_reporte)
        btn_cerrar.clicked.connect(preview.close)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        preview.exec()