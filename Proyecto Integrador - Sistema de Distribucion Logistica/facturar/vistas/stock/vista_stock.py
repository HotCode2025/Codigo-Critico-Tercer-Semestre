"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Vista de Stock con UUID
==================================================
📌 USO: Control de stock, lotes y alertas
📌 CARACTERÍSTICAS:
    - Stock real con UUID
    - Gestión de lotes con UUID
    - Productos más vendidos
    - Últimas ventas
    - Reporte imprimible
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
from modelos.lote import Lote
from utilidades import sincronizar_ahora

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ==================== CLASES DE ESTILO ====================

class LabelSeccionAzul(QLabel):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)
        self.setStyleSheet("""
            QLabel {
                background-color: #1A237E;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 10px;
            }
        """)

class LabelCampoAzul(QLabel):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                padding: 4px 6px;
            }
        """)

class LineEditBlanco(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #1565C0;
            }
        """)


class VistaStock(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.stock_ctrl = ControladorStock(db)
        self.producto_modelo = Producto(db)
        self.lote_modelo = Lote(db)
        
        self.setWindowTitle("Control de Stock y Ventas")
        self.setFixedSize(800, 650)

        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                margin-top: 5px;
                padding-top: 10px;
                background-color: #FFFFFF;
                color: #000000;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #1A237E;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-size: 9px;
                gridline-color: #A0A0A0;
                alternate-background-color: #F8F9FA;
            }
            QTableWidget::item {
                background-color: transparent;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #1565C0;
                color: white;
            }
            QHeaderView::section {
                background-color: #1565C0;
                color: white;
                padding: 4px;
                font-weight: 600;
                border: none;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #0D47A1;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QFrame {
                background-color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #1565C0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(8, 8, 8, 8)
        tarjeta_layout.setSpacing(8)

        # ============================================================
        # 1. SECCIÓN: Stock Real
        # ============================================================
        grupo_stock = QGroupBox("Stock Real (ordenado por fecha de vencimiento)")
        stock_layout = QVBoxLayout()

        self.tabla_stock = QTableWidget()
        self.tabla_stock.setColumnCount(8)
        self.tabla_stock.setHorizontalHeaderLabels(
            ["ID", "Código", "Producto", "Stock", "Crítico", "Unidad", "Próx. Venc.", "Estado"]
        )
        self.tabla_stock.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_stock.setColumnWidth(0, 100)
        self.tabla_stock.setColumnWidth(1, 80)
        self.tabla_stock.setColumnWidth(3, 60)
        self.tabla_stock.setColumnWidth(4, 60)
        self.tabla_stock.setColumnWidth(5, 60)
        self.tabla_stock.setColumnWidth(6, 90)
        self.tabla_stock.setColumnWidth(7, 70)
        self.tabla_stock.setShowGrid(True)
        self.tabla_stock.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_stock.setAlternatingRowColors(True)
        self.tabla_stock.setMaximumHeight(150)
        self.tabla_stock.selectionModel().selectionChanged.connect(self.seleccionar_producto)
        stock_layout.addWidget(self.tabla_stock)

        btn_refrescar = QPushButton("🔄 Actualizar Stock")
        btn_refrescar.setStyleSheet(self._estilo_boton())
        btn_refrescar.clicked.connect(self.cargar_stock)

        btn_sincronizar = QPushButton("🔄 Sincronizar")
        btn_sincronizar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold; font-size: 10px; border: none;")
        btn_sincronizar.clicked.connect(self.sincronizar_stock)

        stock_btn_layout = QHBoxLayout()
        stock_btn_layout.addStretch()
        stock_btn_layout.addWidget(btn_refrescar)
        stock_btn_layout.addWidget(btn_sincronizar)
        stock_layout.addLayout(stock_btn_layout)

        grupo_stock.setLayout(stock_layout)
        tarjeta_layout.addWidget(grupo_stock)

        # ============================================================
        # 2. SECCIÓN: Gráfico + Lista + Reporte
        # ============================================================
        grupo_grafico = QGroupBox("Productos Más Vendidos")
        grafico_container = QVBoxLayout()

        contenido_top = QHBoxLayout()
        self.figure = Figure(figsize=(3.5, 2.5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(300, 200)
        contenido_top.addWidget(self.canvas)

        self.lbl_top = QLabel("Cargando...")
        self.lbl_top.setStyleSheet(
            "font-size: 9px; color: #000000; background-color: white; "
            "border: 1px solid #B0BEC5; border-radius: 4px; padding: 8px;"
        )
        self.lbl_top.setWordWrap(True)
        self.lbl_top.setFixedWidth(220)
        contenido_top.addWidget(self.lbl_top)
        grafico_container.addLayout(contenido_top)

        btn_reporte = QPushButton("🖨️ Imprimir Reporte Top 10")
        btn_reporte.setStyleSheet(self._estilo_boton())
        btn_reporte.clicked.connect(self.mostrar_reporte)
        grafico_container.addWidget(btn_reporte)

        grupo_grafico.setLayout(grafico_container)
        tarjeta_layout.addWidget(grupo_grafico)

        # ============================================================
        # 3. SECCIÓN: Últimas Ventas
        # ============================================================
        grupo_ventas = QGroupBox("Últimas Ventas Registradas")
        ventas_layout = QVBoxLayout()

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(6)
        self.tabla_ventas.setHorizontalHeaderLabels(
            ["ID", "Fecha", "Factura", "Cliente", "Producto", "Cantidad"]
        )
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_ventas.setColumnWidth(0, 100)
        self.tabla_ventas.setShowGrid(True)
        self.tabla_ventas.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_ventas.setAlternatingRowColors(True)
        self.tabla_ventas.setMaximumHeight(80)
        ventas_layout.addWidget(self.tabla_ventas)

        grupo_ventas.setLayout(ventas_layout)
        tarjeta_layout.addWidget(grupo_ventas)

        # ============================================================
        # 4. SECCIÓN: Lotes
        # ============================================================
        grupo_lotes = QGroupBox("Lotes del Producto Seleccionado")
        lotes_layout = QVBoxLayout()

        self.tabla_lotes = QTableWidget()
        self.tabla_lotes.setColumnCount(5)
        self.tabla_lotes.setHorizontalHeaderLabels(
            ["ID", "N° Lote", "Fecha Venc.", "Cant. Inicial", "Cant. Actual"]
        )
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_lotes.setColumnWidth(0, 100)
        self.tabla_lotes.setShowGrid(True)
        self.tabla_lotes.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_lotes.setAlternatingRowColors(True)
        self.tabla_lotes.setMaximumHeight(80)
        lotes_layout.addWidget(self.tabla_lotes)

        lote_form = QHBoxLayout()
        self.txt_numero_lote = LineEditBlanco()
        self.txt_numero_lote.setPlaceholderText("N° Lote")
        self.txt_numero_lote.setFixedWidth(100)
        self.txt_fecha_venc = LineEditBlanco()
        self.txt_fecha_venc.setPlaceholderText("AAAA-MM-DD")
        self.txt_fecha_venc.setFixedWidth(100)
        self.txt_cantidad_lote = LineEditBlanco()
        self.txt_cantidad_lote.setPlaceholderText("Cant.")
        self.txt_cantidad_lote.setFixedWidth(70)
        btn_crear_lote = QPushButton("➕ Crear Lote")
        btn_crear_lote.setStyleSheet(self._estilo_boton_verde())
        btn_crear_lote.clicked.connect(self.crear_lote)

        lote_form.addWidget(QLabel("Nuevo:"))
        lote_form.addWidget(self.txt_numero_lote)
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

    def _estilo_boton(self):
        return """
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """

    def _estilo_boton_verde(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
        """

    def _mostrar_mensaje(self, titulo, texto, icono=QMessageBox.Icon.Information, botones=QMessageBox.StandardButton.Ok):
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setIcon(icono)
        msg.setStandardButtons(botones)
        msg.setStyleSheet("""
            QMessageBox { background-color: white; color: black; font-size: 11px; }
            QLabel { color: black; background-color: transparent; font-size: 11px; }
            QPushButton { background-color: #1565C0; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
        """)
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
            self.tabla_stock.setItem(fila, 0, QTableWidgetItem(prod['id'][:8] + "..."))
            self.tabla_stock.setItem(fila, 1, QTableWidgetItem(prod['codigo_producto']))
            self.tabla_stock.setItem(fila, 2, QTableWidgetItem(prod['descripcion'][:35]))
            self.tabla_stock.setItem(fila, 3, QTableWidgetItem(f"{prod['stock_actual']:.2f}"))
            self.tabla_stock.setItem(fila, 4, QTableWidgetItem(f"{prod['stock_critico']:.2f}"))
            self.tabla_stock.setItem(fila, 5, QTableWidgetItem(prod['unidad_medida']))
            self.tabla_stock.setItem(fila, 6, QTableWidgetItem(prod['prox_venc'] or "N/A"))

            stock = prod['stock_actual']
            critico = prod['stock_critico']
            if stock <= 0:
                estado = "SIN STOCK"
                color = QColor(220, 53, 69)
            elif stock <= critico:
                estado = "BAJO"
                color = QColor(255, 165, 0)
            else:
                estado = "OK"
                color = QColor(40, 167, 69)
            item = QTableWidgetItem(estado)
            item.setForeground(color)
            self.tabla_stock.setItem(fila, 7, item)

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
            lista_texto += f"{i}. {desc[:30]}: {total:.0f} unid.\n"
        self.lbl_top.setText(lista_texto)

        nombres = [t['descripcion'][:25] for t in top]
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
            SELECT fd.id, f.fecha, f.numero_factura, c.razon_social, p.descripcion, fd.cantidad
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
            self.tabla_ventas.setItem(fila, 0, QTableWidgetItem(v['id'][:8] + "..."))
            self.tabla_ventas.setItem(fila, 1, QTableWidgetItem(v['fecha']))
            self.tabla_ventas.setItem(fila, 2, QTableWidgetItem(v['numero_factura']))
            self.tabla_ventas.setItem(fila, 3, QTableWidgetItem(v['razon_social'][:25]))
            self.tabla_ventas.setItem(fila, 4, QTableWidgetItem(v['descripcion'][:30]))
            self.tabla_ventas.setItem(fila, 5, QTableWidgetItem(f"{v['cantidad']:.2f}"))

    def seleccionar_producto(self):
        indices = self.tabla_stock.selectedItems()
        if not indices:
            self.producto_seleccionado_id = None
            self.tabla_lotes.setRowCount(0)
            return
        
        fila = indices[0].row()
        producto_id = self.tabla_stock.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.producto_seleccionado_id = producto_id
        self.cargar_lotes()

    def cargar_lotes(self):
        if not self.producto_seleccionado_id:
            self.tabla_lotes.setRowCount(0)
            return
        
        lotes = self.lote_modelo.listar_por_producto(self.producto_seleccionado_id)
        self.tabla_lotes.setRowCount(len(lotes))
        for fila, lote in enumerate(lotes):
            self.tabla_lotes.setItem(fila, 0, QTableWidgetItem(lote['id'][:8] + "..."))
            self.tabla_lotes.setItem(fila, 1, QTableWidgetItem(lote['numero_lote'] or ""))
            self.tabla_lotes.setItem(fila, 2, QTableWidgetItem(lote['fecha_vencimiento']))
            self.tabla_lotes.setItem(fila, 3, QTableWidgetItem(f"{lote['cantidad_inicial']:.2f}"))
            self.tabla_lotes.setItem(fila, 4, QTableWidgetItem(f"{lote['cantidad_actual']:.2f}"))

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
            lote_id = self.stock_ctrl.crear_lote(
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
            self._mostrar_mensaje("Éxito", f"✅ Lote creado correctamente.\nID: {lote_id[:8]}...")
            
        except Exception as e:
            self._mostrar_mensaje("Error", f"No se pudo crear el lote: {e}", QMessageBox.Icon.Critical)

    def sincronizar_stock(self):
        """Sincroniza stock con Turso"""
        try:
            resultado = sincronizar_ahora(self.db)
            self.cargar_stock()
            self._mostrar_mensaje("Sincronización", "✅ Stock sincronizado con Turso")
        except Exception as e:
            self._mostrar_mensaje("Error", f"Error en sincronización: {e}", QMessageBox.Icon.Critical)

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

        html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Productos Más Vendidos</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                h1 { color: #1A237E; text-align: center; font-size: 16px; }
                table { border-collapse: collapse; width: 100%; margin-top: 15px; }
                th { background-color: #1565C0; color: white; padding: 8px; font-size: 11px; }
                td { border: 1px solid #ddd; padding: 6px; font-size: 10px; }
                .fecha { text-align: center; color: #666; margin-bottom: 15px; font-size: 10px; }
                .numero { text-align: right; }
            </style>
        </head>
        <body>
            <h1>PRODUCTOS MÁS VENDIDOS</h1>
            <div class="fecha">Fecha: """ + date.today().isoformat() + """</div>
            <table>
                <tr>
                    <th>#</th>
                    <th>Producto</th>
                    <th>Unidades Vendidas</th>
                </tr>
        """
        
        for i, (desc, total) in enumerate(top, 1):
            html += f"""
                <tr>
                    <td class="numero">{i}</td>
                    <td>{desc}</td>
                    <td class="numero">{total:.0f}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """

        preview = QDialog(self)
        preview.setWindowTitle("Vista previa del reporte - Productos más vendidos")
        preview.resize(500, 400)
        preview.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(preview)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        
        visor = QTextEdit()
        visor.setReadOnly(True)
        visor.setHtml(html)
        frame_layout.addWidget(visor)
        
        layout.addWidget(frame)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_imprimir = QPushButton("🖨️ Imprimir")
        btn_imprimir.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 20px; font-weight: bold;")
        btn_imprimir.setMinimumWidth(120)
        
        btn_cerrar = QPushButton("❌ Cerrar")
        btn_cerrar.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 8px 20px; font-weight: bold;")
        btn_cerrar.setMinimumWidth(120)
        
        def imprimir():
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, preview)
            dialog.setWindowTitle("Imprimir Reporte")
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                visor.print_(printer)
        
        btn_imprimir.clicked.connect(imprimir)
        btn_cerrar.clicked.connect(preview.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        
        preview.exec()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaStock(db)
    ventana.show()
    sys.exit(app.exec())