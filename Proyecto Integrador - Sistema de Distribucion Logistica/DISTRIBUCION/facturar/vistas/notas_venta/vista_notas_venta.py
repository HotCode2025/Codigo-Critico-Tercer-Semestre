"""
Código Crítico - Tercer Semestre Año 2026
Vista de Notas de Venta – Rediseñada con tabs azules y grid visible.
Botones: Facturar (VERDE), Actualizar (AZUL), Eliminar (ROJO)
Tamaño: 950x800
"""

import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QFrame, QTabWidget,
                               QWidget, QSplitter, QTextEdit, QComboBox,
                               QSpinBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont

from modelos.nota_venta import NotaVenta
from modelos.producto import Producto
from modelos.cliente import Cliente
from modelos.preventista import Preventista
from controladores.controlador_ventas import ControladorVentas


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


class ComboBlanco(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #000000;
                selection-background-color: #1565C0;
                selection-color: white;
            }
        """)


class SpinBoxBlanco(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
            QSpinBox:focus {
                border-color: #1565C0;
            }
        """)


class DateEditBlanco(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())
        self.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
            QDateEdit:focus {
                border-color: #1565C0;
            }
        """)


# ==================== VISTA PRINCIPAL ====================

class VistaNotasVenta(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.nota_venta_modelo = NotaVenta(db)
        self.producto_modelo = Producto(db)
        self.cliente_modelo = Cliente(db)
        self.preventista_modelo = Preventista(db)
        self.controlador_ventas = ControladorVentas(db)

        self.setWindowTitle("Notas de Venta")
        self.setFixedSize(950, 800)

        # ✅ ESTILO CON TABS AZULES Y GRID VISIBLE
        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QTabWidget::pane {
                border: 1px solid #B0BEC5;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1565C0;
                color: white;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 10px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0D47A1;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #1976D2;
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
                padding: 5px;
                font-weight: 600;
                border: none;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #0D47A1;
            }
            QHeaderView::section:vertical {
                border-bottom: 1px solid #0D47A1;
            }
            QFrame {
                background-color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QPushButton {
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(8, 8, 8, 8)
        tarjeta_layout.setSpacing(5)

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        self.tab_pendientes = self._crear_tab_notas_pendientes()
        self.tabs.addTab(self.tab_pendientes, "📋 NOTAS PENDIENTES")
        
        self.tab_facturadas = self._crear_tab_notas_facturadas()
        self.tabs.addTab(self.tab_facturadas, "✅ NOTAS FACTURADAS")
        
        tarjeta_layout.addWidget(self.tabs)
        layout.addWidget(tarjeta)

        # Contador en el título
        self.actualizar_titulo()
        
        # Cargar datos
        self.cargar_notas_pendientes()
        self.cargar_notas_facturadas()

    # ==================== PESTAÑA 1: NOTAS PENDIENTES ====================
    
    def _crear_tab_notas_pendientes(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Tabla de notas
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        tabla = QTableWidget()
        tabla.setColumnCount(6)
        tabla.setHorizontalHeaderLabels(["Número", "Cliente", "Preventista", "Fecha", "Total", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setAlternatingRowColors(True)
        tabla.setMaximumHeight(220)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.doubleClicked.connect(lambda: self.ver_detalle_nota(tabla, "PENDIENTE"))
        tabla_layout.addWidget(tabla)

        layout.addWidget(frame_tabla)

        # Detalle de la nota seleccionada
        frame_detalle = QFrame()
        frame_detalle.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        detalle_layout = QVBoxLayout(frame_detalle)
        detalle_layout.setContentsMargins(5, 5, 5, 5)

        detalle_layout.addWidget(LabelSeccionAzul("DETALLE DE LA NOTA"))

        tabla_detalle = QTableWidget()
        tabla_detalle.setColumnCount(4)
        tabla_detalle.setHorizontalHeaderLabels(["Código", "Producto", "Cantidad", "Precio Unit."])
        tabla_detalle.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla_detalle.setAlternatingRowColors(True)
        tabla_detalle.setMinimumHeight(200)
        detalle_layout.addWidget(tabla_detalle)

        layout.addWidget(frame_detalle)

        # Botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(8)

        btn_facturar = QPushButton("💰 Facturar Nota")
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_eliminar = QPushButton("🗑️ Eliminar Nota")

        btn_facturar.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_actualizar.setStyleSheet("background-color: #1565C0; color: white;")
        btn_eliminar.setStyleSheet("background-color: #D32F2F; color: white;")

        btn_facturar.setMinimumHeight(30)
        btn_actualizar.setMinimumHeight(30)
        btn_eliminar.setMinimumHeight(30)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_facturar)
        botones_layout.addWidget(btn_actualizar)
        botones_layout.addWidget(btn_eliminar)

        layout.addWidget(frame_botones)

        # Guardar referencias
        tab.tabla = tabla
        tab.tabla_detalle = tabla_detalle
        tab.estado = "PENDIENTE"
        tab.btn_facturar = btn_facturar
        tab.btn_actualizar = btn_actualizar
        tab.btn_eliminar = btn_eliminar

        # Conexiones
        tabla.selectionModel().selectionChanged.connect(
            lambda: self.cargar_detalle_nota(tab)
        )
        btn_facturar.clicked.connect(
            lambda: self.facturar_nota(tab)
        )
        btn_actualizar.clicked.connect(
            lambda: self.actualizar_tab_notas(tab)
        )
        btn_eliminar.clicked.connect(
            lambda: self.eliminar_nota(tab)
        )

        return tab

    # ==================== PESTAÑA 2: NOTAS FACTURADAS ====================
    
    def _crear_tab_notas_facturadas(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Tabla de notas
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        tabla = QTableWidget()
        tabla.setColumnCount(6)
        tabla.setHorizontalHeaderLabels(["Número", "Cliente", "Preventista", "Fecha", "Total", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla.setAlternatingRowColors(True)
        tabla.setMinimumHeight(380)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.doubleClicked.connect(lambda: self.ver_detalle_nota_facturada(tabla))
        tabla_layout.addWidget(tabla)

        layout.addWidget(frame_tabla)

        # Botones (SOLO Ver Nota y Eliminar)
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(8)

        btn_ver_nota = QPushButton("📄 Ver Nota")
        btn_eliminar = QPushButton("🗑️ Eliminar Nota")
        btn_actualizar = QPushButton("🔄 Actualizar")

        btn_ver_nota.setStyleSheet("background-color: #1565C0; color: white;")
        btn_eliminar.setStyleSheet("background-color: #D32F2F; color: white;")
        btn_actualizar.setStyleSheet("background-color: #4CAF50; color: white;")

        btn_ver_nota.setMinimumHeight(30)
        btn_eliminar.setMinimumHeight(30)
        btn_actualizar.setMinimumHeight(30)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_ver_nota)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addWidget(btn_actualizar)

        layout.addWidget(frame_botones)

        # Guardar referencias
        tab.tabla = tabla
        tab.estado = "FACTURADA"
        tab.btn_ver_nota = btn_ver_nota
        tab.btn_eliminar = btn_eliminar
        tab.btn_actualizar = btn_actualizar

        # Conexiones
        btn_ver_nota.clicked.connect(
            lambda: self.ver_detalle_nota_facturada(tabla)
        )
        btn_eliminar.clicked.connect(
            lambda: self.eliminar_nota_facturada(tab)
        )
        btn_actualizar.clicked.connect(
            lambda: self.actualizar_tab_notas(tab)
        )

        return tab

    # ==================== CARGA DE DATOS ====================
    
    def cargar_notas_pendientes(self):
        self._cargar_notas_en_tabla(self.tab_pendientes, "PENDIENTE")

    def cargar_notas_facturadas(self):
        self._cargar_notas_en_tabla(self.tab_facturadas, "FACTURADA")

    def _cargar_notas_en_tabla(self, tab, estado):
        notas = self.nota_venta_modelo.listar_por_estado(estado)
        tabla = tab.tabla
        
        tabla.setRowCount(len(notas))
        for fila, nota in enumerate(notas):
            cliente = self.cliente_modelo.obtener_por_id(nota['cliente_id'])
            preventista = self.preventista_modelo.obtener_por_id(nota['preventista_id'])
            
            tabla.setItem(fila, 0, QTableWidgetItem(nota['numero_nota']))
            tabla.setItem(fila, 1, QTableWidgetItem(cliente['razon_social'] if cliente else 'N/A'))
            tabla.setItem(fila, 2, QTableWidgetItem(f"{preventista['nombre']} {preventista['apellido']}" if preventista else 'N/A'))
            tabla.setItem(fila, 3, QTableWidgetItem(nota['fecha']))
            
            item_total = QTableWidgetItem(f"${nota['total']:,.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla.setItem(fila, 4, item_total)
            
            item_estado = QTableWidgetItem(nota['estado'])
            if nota['estado'] == 'PENDIENTE':
                item_estado.setForeground(QColor(255, 165, 0))
            elif nota['estado'] == 'FACTURADA':
                item_estado.setForeground(QColor(40, 167, 69))
            tabla.setItem(fila, 5, item_estado)
            
            # Guardar ID de la nota
            tabla.item(fila, 0).setData(Qt.ItemDataRole.UserRole, nota['id'])

    def actualizar_tab_notas(self, tab):
        if tab.estado == "PENDIENTE":
            self.cargar_notas_pendientes()
            tab.tabla_detalle.setRowCount(0)
        else:
            self.cargar_notas_facturadas()
        self.actualizar_titulo()

    def actualizar_titulo(self):
        pendientes = self.nota_venta_modelo.listar_por_estado('PENDIENTE')
        cantidad = len(pendientes)
        
        if cantidad > 0:
            self.setWindowTitle(f"Notas de Venta ({cantidad} pendientes) 🔔")
            self.tabs.tabBar().setTabTextColor(0, QColor(255, 100, 100))
        else:
            self.setWindowTitle("Notas de Venta")
            self.tabs.tabBar().setTabTextColor(0, QColor(255, 255, 255))

    # ==================== DETALLE DE NOTA (PENDIENTES) ====================
    
    def cargar_detalle_nota(self, tab):
        indices = tab.tabla.selectedItems()
        if not indices:
            tab.tabla_detalle.setRowCount(0)
            return

        fila = indices[0].row()
        nota_id = tab.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        
        if not nota_id:
            return

        cur = self.db.cursor()
        cur.execute("""
            SELECT p.codigo, p.descripcion, nd.cantidad, nd.precio_unitario, p.stock_actual
            FROM nota_venta_detalle nd
            JOIN productos p ON nd.producto_id = p.id
            WHERE nd.nota_venta_id = ?
        """, (nota_id,))
        detalles = cur.fetchall()
        
        tabla_detalle = tab.tabla_detalle
        tabla_detalle.setRowCount(len(detalles))
        
        hay_stock_insuficiente = False
        
        for i, det in enumerate(detalles):
            tabla_detalle.setItem(i, 0, QTableWidgetItem(det['codigo']))
            tabla_detalle.setItem(i, 1, QTableWidgetItem(det['descripcion']))
            item_cantidad = QTableWidgetItem(f"{det['cantidad']:.0f}")
            item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 2, item_cantidad)
            item_precio = QTableWidgetItem(f"${det['precio_unitario']:,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 3, item_precio)
            
            if det['cantidad'] > det['stock_actual']:
                for col in range(4):
                    item = tabla_detalle.item(i, col)
                    if item:
                        item.setBackground(QColor(255, 200, 200))
                hay_stock_insuficiente = True
        
        # Habilitar/deshabilitar botón facturar según stock
        if tab.estado == 'PENDIENTE':
            if hay_stock_insuficiente:
                tab.btn_facturar.setEnabled(False)
                tab.btn_facturar.setToolTip("Stock insuficiente para facturar")
            else:
                tab.btn_facturar.setEnabled(True)
                tab.btn_facturar.setToolTip("")

    def ver_detalle_nota(self, tabla, estado):
        """Ver detalle completo de la nota en un diálogo"""
        indices = tabla.selectedItems()
        if not indices:
            return
        
        fila = indices[0].row()
        nota_id = tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        
        if not nota_id:
            return
        
        nota = self.nota_venta_modelo.obtener_por_id(nota_id)
        if not nota:
            return
        
        cliente = self.cliente_modelo.obtener_por_id(nota['cliente_id'])
        preventista = self.preventista_modelo.obtener_por_id(nota['preventista_id'])
        
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.codigo, p.descripcion, nd.cantidad, nd.precio_unitario
            FROM nota_venta_detalle nd
            JOIN productos p ON nd.producto_id = p.id
            WHERE nd.nota_venta_id = ?
        """, (nota_id,))
        detalles = cur.fetchall()
        
        # Diálogo de detalle
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle de Nota - {nota['numero_nota']}")
        dialog.setFixedSize(650, 480)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        
        # Datos de la nota
        lbl_titulo = QLabel(f"<b>NOTA DE VENTA</b>")
        lbl_titulo.setStyleSheet("font-size: 14px; color: #1A237E;")
        frame_layout.addWidget(lbl_titulo)
        
        datos = QGridLayout()
        datos.setSpacing(5)
        
        datos.addWidget(QLabel("<b>Número:</b>"), 0, 0)
        datos.addWidget(QLabel(nota['numero_nota']), 0, 1)
        datos.addWidget(QLabel("<b>Fecha:</b>"), 0, 2)
        datos.addWidget(QLabel(nota['fecha']), 0, 3)
        
        datos.addWidget(QLabel("<b>Cliente:</b>"), 1, 0)
        datos.addWidget(QLabel(cliente['razon_social'] if cliente else 'N/A'), 1, 1)
        datos.addWidget(QLabel("<b>Preventista:</b>"), 1, 2)
        datos.addWidget(QLabel(f"{preventista['nombre']} {preventista['apellido']}" if preventista else 'N/A'), 1, 3)
        
        datos.addWidget(QLabel("<b>Estado:</b>"), 2, 0)
        lbl_estado = QLabel(nota['estado'])
        if nota['estado'] == 'PENDIENTE':
            lbl_estado.setStyleSheet("color: #FF9800; font-weight: bold;")
        else:
            lbl_estado.setStyleSheet("color: #4CAF50; font-weight: bold;")
        datos.addWidget(lbl_estado, 2, 1)
        
        datos.addWidget(QLabel("<b>Total:</b>"), 2, 2)
        datos.addWidget(QLabel(f"<b>${nota['total']:,.2f}</b>"), 2, 3)
        
        frame_layout.addLayout(datos)
        
        if nota.get('observaciones'):
            frame_layout.addWidget(QLabel("<b>Observaciones:</b>"))
            frame_layout.addWidget(QLabel(nota['observaciones']))
        
        # Tabla de productos
        frame_layout.addWidget(QLabel("<b>Productos:</b>"))
        tabla_detalle = QTableWidget()
        tabla_detalle.setColumnCount(4)
        tabla_detalle.setHorizontalHeaderLabels(["Código", "Producto", "Cantidad", "Precio Unit."])
        tabla_detalle.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla_detalle.setAlternatingRowColors(True)
        tabla_detalle.setMaximumHeight(200)
        tabla_detalle.setShowGrid(True)
        tabla_detalle.setGridStyle(Qt.PenStyle.SolidLine)
        
        tabla_detalle.setRowCount(len(detalles))
        for i, det in enumerate(detalles):
            tabla_detalle.setItem(i, 0, QTableWidgetItem(det['codigo']))
            tabla_detalle.setItem(i, 1, QTableWidgetItem(det['descripcion']))
            item_cantidad = QTableWidgetItem(f"{det['cantidad']:.0f}")
            item_cantidad.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 2, item_cantidad)
            item_precio = QTableWidgetItem(f"${det['precio_unitario']:,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 3, item_precio)
        
        frame_layout.addWidget(tabla_detalle)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 16px; font-weight: bold;")
        btn_cerrar.clicked.connect(dialog.accept)
        
        frame_layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(frame)
        dialog.exec()

    # ==================== DETALLE DE NOTA FACTURADA ====================
    
    def ver_detalle_nota_facturada(self, tabla):
        """Ver detalle de la nota facturada en formato similar a factura impresa"""
        indices = tabla.selectedItems()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una nota de venta.")
            return
        
        fila = indices[0].row()
        nota_id = tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_nota = tabla.item(fila, 0).text()
        
        nota = self.nota_venta_modelo.obtener_por_id(nota_id)
        if not nota:
            QMessageBox.critical(self, "Error", "Nota de venta no encontrada.")
            return
        
        cliente = self.cliente_modelo.obtener_por_id(nota['cliente_id'])
        preventista = self.preventista_modelo.obtener_por_id(nota['preventista_id'])
        
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.codigo, p.descripcion, nd.cantidad, nd.precio_unitario
            FROM nota_venta_detalle nd
            JOIN productos p ON nd.producto_id = p.id
            WHERE nd.nota_venta_id = ?
        """, (nota_id,))
        detalles = cur.fetchall()
        
        # Crear diálogo estilo factura
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Nota de Venta - {numero_nota}")
        dialog.setFixedSize(800, 700)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== ENCABEZADO ==========
        lbl_empresa = QLabel("SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA")
        lbl_empresa.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E; text-align: center;")
        lbl_empresa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_empresa)
        
        lbl_titulo = QLabel(f"NOTA DE VENTA")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #1565C0; text-align: center;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_titulo)
        
        lbl_numero = QLabel(f"N° {numero_nota}")
        lbl_numero.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E; text-align: center;")
        lbl_numero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_numero)
        
        # Línea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("background-color: #1565C0; max-height: 2px;")
        frame_layout.addWidget(linea)
        
        frame_layout.addWidget(QLabel(" " * 50))
        
        # ========== DATOS DEL CLIENTE ==========
        datos_cliente = QGridLayout()
        datos_cliente.setSpacing(5)
        
        datos_cliente.addWidget(QLabel("<b>Cliente:</b>"), 0, 0)
        datos_cliente.addWidget(QLabel(cliente['razon_social'] if cliente else 'N/A'), 0, 1)
        datos_cliente.addWidget(QLabel("<b>CUIT:</b>"), 0, 2)
        datos_cliente.addWidget(QLabel(cliente.get('cuit', 'N/A') if cliente else 'N/A'), 0, 3)
        
        datos_cliente.addWidget(QLabel("<b>Condición IVA:</b>"), 1, 0)
        datos_cliente.addWidget(QLabel(cliente.get('condicion_iva', 'N/A') if cliente else 'N/A'), 1, 1)
        datos_cliente.addWidget(QLabel("<b>Fecha:</b>"), 1, 2)
        datos_cliente.addWidget(QLabel(nota['fecha']), 1, 3)
        
        datos_cliente.addWidget(QLabel("<b>Preventista:</b>"), 2, 0)
        datos_cliente.addWidget(QLabel(f"{preventista['nombre']} {preventista['apellido']}" if preventista else 'N/A'), 2, 1)
        
        if nota.get('observaciones'):
            datos_cliente.addWidget(QLabel("<b>Observaciones:</b>"), 2, 2)
            datos_cliente.addWidget(QLabel(nota['observaciones']), 2, 3)
        
        frame_layout.addLayout(datos_cliente)
        
        frame_layout.addWidget(QLabel(" " * 30))
        
        # ========== TABLA DE PRODUCTOS ==========
        lbl_productos = QLabel("<b>DETALLE DE PRODUCTOS</b>")
        lbl_productos.setStyleSheet("font-size: 12px; color: #1A237E;")
        frame_layout.addWidget(lbl_productos)
        
        tabla_detalle = QTableWidget()
        tabla_detalle.setColumnCount(4)
        tabla_detalle.setHorizontalHeaderLabels(["Código", "Producto", "Cantidad", "Precio Unit."])
        tabla_detalle.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla_detalle.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        tabla_detalle.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        tabla_detalle.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        tabla_detalle.setShowGrid(True)
        tabla_detalle.setGridStyle(Qt.PenStyle.SolidLine)
        tabla_detalle.setAlternatingRowColors(True)
        tabla_detalle.setMinimumHeight(150)
        
        tabla_detalle.setRowCount(len(detalles))
        total = 0
        for i, det in enumerate(detalles):
            subtotal = det['cantidad'] * det['precio_unitario']
            total += subtotal
            tabla_detalle.setItem(i, 0, QTableWidgetItem(det['codigo']))
            tabla_detalle.setItem(i, 1, QTableWidgetItem(det['descripcion']))
            item_cant = QTableWidgetItem(f"{det['cantidad']:.0f}")
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 2, item_cant)
            item_precio = QTableWidgetItem(f"${det['precio_unitario']:,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 3, item_precio)
        
        frame_layout.addWidget(tabla_detalle)
        
        # ========== TOTALES ==========
        iva = total * 0.21
        total_final = total + iva
        
        frame_totales = QFrame()
        frame_totales.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
            QLabel {
                font-size: 12px;
                padding: 2px 0;
            }
        """)
        totales_layout = QVBoxLayout(frame_totales)
        totales_layout.setSpacing(4)
        
        lbl_subtotal = QLabel(f"<b>Subtotal:</b> $ {total:,.2f}")
        lbl_iva = QLabel(f"<b>IVA (21%):</b> $ {iva:,.2f}")
        lbl_total = QLabel(f"<b>TOTAL:</b> $ {total_final:,.2f}")
        lbl_total.setStyleSheet("font-size: 15px; font-weight: bold; color: #1A237E; padding-top: 5px; border-top: 2px solid #1A237E;")
        
        totales_layout.addWidget(lbl_subtotal, alignment=Qt.AlignmentFlag.AlignRight)
        totales_layout.addWidget(lbl_iva, alignment=Qt.AlignmentFlag.AlignRight)
        totales_layout.addWidget(lbl_total, alignment=Qt.AlignmentFlag.AlignRight)
        
        frame_layout.addWidget(frame_totales)
        
        # ========== PIE DE PÁGINA ==========
        lbl_pie = QLabel("Nota de Venta - Documento no fiscal")
        lbl_pie.setStyleSheet("text-align: center; color: #666666; font-size: 10px; margin-top: 15px;")
        lbl_pie.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_pie)
        
        # ========== BOTONES ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 20px; font-weight: bold;")
        btn_cerrar.clicked.connect(dialog.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        
        frame_layout.addLayout(btn_layout)
        
        layout.addWidget(frame)
        dialog.exec()

    # ==================== ACCIONES ====================
    
    def facturar_nota(self, tab):
        """Factura una nota de venta y actualiza ambas pestañas"""
        indices = tab.tabla.selectedItems()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una nota de venta.")
            return
        
        fila = indices[0].row()
        nota_id = tab.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_nota = tab.tabla.item(fila, 0).text()
        
        confirm = QMessageBox.question(
            self, "Confirmar Facturación",
            f"¿Facturar nota {numero_nota}?\nSe generará la factura y se descontará el stock.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            factura_id = self.controlador_ventas.facturar_desde_nota(nota_id)
            QMessageBox.information(self, "Éxito", f"✅ Nota facturada correctamente.\nID Factura: {factura_id[:8]}...")
            
            # ✅ FORZAR ACTUALIZACIÓN DE AMBAS PESTAÑAS
            self.cargar_notas_pendientes()   # Actualizar pestaña PENDIENTES
            self.cargar_notas_facturadas()   # Actualizar pestaña FACTURADAS
            self.actualizar_titulo()         # Actualizar contador en título
            
            # Limpiar detalle
            tab.tabla_detalle.setRowCount(0)
            
            # ✅ FORZAR REFRESCO VISUAL DE LA TABLA
            tab.tabla.repaint()
            tab.tabla.viewport().update()
            
            # ✅ ACTUALIZAR DASHBOARD (si está abierto)
            self._actualizar_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo facturar:\n{str(e)}")

    def _actualizar_dashboard(self):
        """Actualiza el dashboard si está abierto."""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'area_central') and hasattr(parent.area_central, 'cargar_pedidos'):
                    parent.area_central.cargar_pedidos()
                    parent.area_central.verificar_notas_pendientes()
                    print("✅ Dashboard actualizado después de facturar")
                    break
                # También verificar si es el Dashboard directamente
                if hasattr(parent, 'cargar_pedidos') and hasattr(parent, 'verificar_notas_pendientes'):
                    parent.cargar_pedidos()
                    parent.verificar_notas_pendientes()
                    print("✅ Dashboard actualizado después de facturar")
                    break
                parent = getattr(parent, 'parent', lambda: None)()
        except Exception as e:
            print(f"⚠️ Error actualizando dashboard: {e}")

    def eliminar_nota(self, tab):
        indices = tab.tabla.selectedItems()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una nota de venta.")
            return
        
        fila = indices[0].row()
        nota_id = tab.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_nota = tab.tabla.item(fila, 0).text()
        
        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar nota {numero_nota}?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM nota_venta_detalle WHERE nota_venta_id = ?", (nota_id,))
            cur.execute("DELETE FROM notas_venta WHERE id = ?", (nota_id,))
            self.db.commit()
            
            QMessageBox.information(self, "Éxito", "✅ Nota eliminada correctamente.")
            
            self.actualizar_tab_notas(tab)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{str(e)}")

    def eliminar_nota_facturada(self, tab):
        """Eliminar nota facturada (solo en pestaña facturadas)"""
        indices = tab.tabla.selectedItems()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una nota de venta.")
            return
        
        fila = indices[0].row()
        nota_id = tab.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_nota = tab.tabla.item(fila, 0).text()
        
        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar nota facturada {numero_nota}?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM nota_venta_detalle WHERE nota_venta_id = ?", (nota_id,))
            cur.execute("DELETE FROM notas_venta WHERE id = ?", (nota_id,))
            self.db.commit()
            
            QMessageBox.information(self, "Éxito", "✅ Nota facturada eliminada correctamente.")
            
            self.cargar_notas_facturadas()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{str(e)}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaNotasVenta(db)
    ventana.show()
    sys.exit(app.exec())