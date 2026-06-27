"""
Código Crítico - Tercer Semestre Año 2026
Vista Unificada de Productos, Stock y Catálogo.
Tamaño 1000x650 - Columnas redimensionables - Tabs azules.
"""

import sqlite3
from datetime import date, timedelta
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QFrame, QComboBox,
                               QFileDialog, QCheckBox, QSplitter, QWidget,
                               QTabWidget, QScrollArea, QGridLayout,
                               QTextEdit, QInputDialog, QDateEdit)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

from controladores.controlador_productos import ControladorProductos
from modelos.categoria import Categoria
from modelos.lote import Lote

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


class CheckBoxBlanco(QCheckBox):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: #000000;
                background-color: #FFFFFF;
                spacing: 6px;
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #000000;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 2px solid #1565C0;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #1565C0;
            }
        """)


class TarjetaProducto(QFrame):
    def __init__(self, producto, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 230)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        lbl_foto = QLabel()
        lbl_foto.setFixedSize(140, 85)
        lbl_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_foto.setStyleSheet("border: 1px solid #B0BEC5; background-color: #F5F5F5;")
        foto_blob = producto.get('foto')
        pixmap = QPixmap()
        if foto_blob and isinstance(foto_blob, bytes) and pixmap.loadFromData(foto_blob):
            lbl_foto.setPixmap(pixmap.scaled(140, 85, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_foto.setText("Sin foto")
        layout.addWidget(lbl_foto)

        lbl_codigo = QLabel(producto.get('codigo_producto', ''))
        lbl_codigo.setStyleSheet("font-weight: bold; font-size: 9px; color: #000000;")
        layout.addWidget(lbl_codigo)

        lbl_desc = QLabel(producto.get('descripcion', '')[:35])
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 8px; color: #333;")
        layout.addWidget(lbl_desc)

        precio = producto.get('precio_oferta') or producto.get('precio_venta', 0)
        lbl_precio = QLabel(f"${precio:,.2f}")
        lbl_precio.setStyleSheet("font-size: 10px; font-weight: bold; color: #1565C0;")
        layout.addWidget(lbl_precio)

        stock = producto.get('stock_actual', 0)
        lbl_stock = QLabel(f"Stock: {stock:.0f}")
        lbl_stock.setStyleSheet("font-size: 8px; color: #555;")
        layout.addWidget(lbl_stock)

        warnings = []
        if not producto.get('foto'):
            warnings.append("Sin foto")
        if producto.get('precio_venta', 0) <= 0:
            warnings.append("Precio no válido")
        if warnings:
            self.setStyleSheet(self.styleSheet() + " QFrame { border: 2px solid #D32F2F; }")
            lbl_warn = QLabel("⚠️ " + ", ".join(warnings))
            lbl_warn.setStyleSheet("color: #D32F2F; font-size: 7px;")
            layout.addWidget(lbl_warn)


# ==================== VISTA PRINCIPAL ====================

class VistaProductosUnificada(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.controlador_productos = ControladorProductos(db)
        self.categoria_modelo = Categoria(db)
        self.lote_modelo = Lote(db)
        self.setWindowTitle("Gestión de Productos, Stock y Catálogo")
        
        # ✅ NUEVO TAMAÑO: 1000 x 650
        self.setFixedSize(1000, 650)

        # ✅ ESTILO GENERAL CON TABS AZULES
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
            QGroupBox {
                border: none;
                background-color: transparent;
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
            QSplitter::handle {
                background-color: #B0BEC5;
                width: 2px;
                height: 2px;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
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
        
        self.tab_productos = self._crear_tab_productos()
        self.tabs.addTab(self.tab_productos, "📦 PRODUCTOS")
        
        self.tab_stock = self._crear_tab_stock()
        self.tabs.addTab(self.tab_stock, "📊 STOCK")
        
        self.tab_mas_vendidos = self._crear_tab_mas_vendidos()
        self.tabs.addTab(self.tab_mas_vendidos, "🏆 MÁS VENDIDOS")
        
        self.tab_ultimas_ventas = self._crear_tab_ultimas_ventas()
        self.tabs.addTab(self.tab_ultimas_ventas, "🕐 ÚLTIMAS VENTAS")
        
        self.tab_catalogo = self._crear_tab_catalogo()
        self.tabs.addTab(self.tab_catalogo, "🖼️ CATÁLOGO")
        
        tarjeta_layout.addWidget(self.tabs)
        layout.addWidget(tarjeta)

        # ✅ CARGAR CATEGORÍAS PARA EL CATÁLOGO
        self._cargar_categorias_catalogo()

        self.foto_bytes = None
        self.producto_seleccionado_id = None
        
        self.cargar_productos()
        self.cargar_stock()
        self.cargar_mas_vendidos()
        self.cargar_ultimas_ventas()
        self.cargar_catalogo()

    # ==================== PESTAÑA 1: PRODUCTOS ====================
    
    def _crear_tab_productos(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        # Búsqueda
        busqueda_layout = QHBoxLayout()
        self.txt_buscar = LineEditBlanco()
        self.txt_buscar.setPlaceholderText("🔍 Código o descripción...")
        self.txt_buscar.setMinimumWidth(350)
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedWidth(80)
        btn_buscar.setStyleSheet(self._estilo_boton_azul())
        btn_buscar.clicked.connect(self.cargar_productos)
        busqueda_layout.addWidget(QLabel("Buscar:"))
        busqueda_layout.addWidget(self.txt_buscar, 1)
        busqueda_layout.addWidget(btn_buscar)
        layout.addLayout(busqueda_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo
        panel_izq = QFrame()
        panel_izq.setStyleSheet("QFrame { background-color: #E8E8E8; border-radius: 8px; }")
        izq_layout = QVBoxLayout(panel_izq)
        izq_layout.setContentsMargins(5, 5, 5, 5)
        izq_layout.setSpacing(5)

        # ✅ TABLA CON COLUMNAS REDIMENSIONABLES
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Código", "Descripción", "Costo", "Venta", "Stock"])
        
        # ✅ Configurar redimensionamiento
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        
        # ✅ Anchos iniciales
        self.tabla.setColumnWidth(0, 100)
        self.tabla.setColumnWidth(2, 80)
        self.tabla.setColumnWidth(3, 80)
        self.tabla.setColumnWidth(4, 60)
        
        # ✅ Líneas de grid visibles
        self.tabla.setShowGrid(True)
        self.tabla.setGridStyle(Qt.PenStyle.SolidLine)
        
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setMinimumHeight(180)
        self.tabla.selectionModel().selectionChanged.connect(self.seleccionar_producto)
        izq_layout.addWidget(self.tabla)

        # Formulario
        form_group = QFrame()
        form_group.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        form_group_layout = QVBoxLayout(form_group)
        form_group_layout.setContentsMargins(8, 5, 8, 5)
        form_group_layout.setSpacing(4)

        form_group_layout.addWidget(LabelSeccionAzul("DATOS DEL PRODUCTO"))

        form_layout = QGridLayout()
        form_layout.setSpacing(4)
        form_layout.setHorizontalSpacing(8)

        form_layout.addWidget(LabelCampoAzul("Código *"), 0, 0)
        self.txt_codigo = LineEditBlanco()
        form_layout.addWidget(self.txt_codigo, 0, 1)
        
        form_layout.addWidget(LabelCampoAzul("Unidad"), 0, 2)
        self.txt_unidad = LineEditBlanco()
        self.txt_unidad.setText("unidad")
        form_layout.addWidget(self.txt_unidad, 0, 3)

        form_layout.addWidget(LabelCampoAzul("Descripción *"), 1, 0)
        self.txt_descripcion = LineEditBlanco()
        form_layout.addWidget(self.txt_descripcion, 1, 1, 1, 3)

        form_layout.addWidget(LabelCampoAzul("Costo"), 2, 0)
        self.txt_costo = LineEditBlanco()
        form_layout.addWidget(self.txt_costo, 2, 1)
        
        form_layout.addWidget(LabelCampoAzul("Venta"), 2, 2)
        self.txt_venta = LineEditBlanco()
        form_layout.addWidget(self.txt_venta, 2, 3)

        form_layout.addWidget(LabelCampoAzul("Stock Crítico"), 3, 0)
        self.txt_stock_critico = LineEditBlanco()
        form_layout.addWidget(self.txt_stock_critico, 3, 1)
        
        form_layout.addWidget(LabelCampoAzul("Stock Inicial"), 3, 2)
        self.txt_stock_inicial = LineEditBlanco()
        self.txt_stock_inicial.setPlaceholderText("0")
        form_layout.addWidget(self.txt_stock_inicial, 3, 3)

        form_layout.addWidget(LabelCampoAzul("Categoría"), 4, 0)
        self.cmb_categoria = ComboBlanco()
        form_layout.addWidget(self.cmb_categoria, 4, 1)
        
        form_layout.addWidget(LabelCampoAzul("Precio Oferta"), 4, 2)
        self.txt_precio_oferta = LineEditBlanco()
        form_layout.addWidget(self.txt_precio_oferta, 4, 3)

        form_layout.addWidget(LabelCampoAzul("Detalle"), 5, 0)
        self.txt_detalle = LineEditBlanco()
        form_layout.addWidget(self.txt_detalle, 5, 1, 1, 3)

        self.chk_destacado = CheckBoxBlanco("Destacado")
        form_layout.addWidget(self.chk_destacado, 6, 0, 1, 2)

        self.lbl_foto = QLabel("Sin foto")
        self.lbl_foto.setFixedSize(40, 40)
        self.lbl_foto.setStyleSheet("border: 1px solid #000000; background-color: white; border-radius: 4px;")
        self.lbl_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.lbl_foto, 6, 2)
        
        btn_cargar_foto = QPushButton("📷 Foto")
        btn_cargar_foto.setFixedWidth(60)
        btn_cargar_foto.setStyleSheet(self._estilo_boton_azul())
        btn_cargar_foto.clicked.connect(self.cargar_foto)
        form_layout.addWidget(btn_cargar_foto, 6, 3)

        btn_gestionar_cat = QPushButton("📁 Categorías")
        btn_gestionar_cat.setFixedWidth(90)
        btn_gestionar_cat.setStyleSheet(self._estilo_boton_azul())
        btn_gestionar_cat.clicked.connect(self.gestionar_categorias)
        form_layout.addWidget(btn_gestionar_cat, 7, 0, 1, 2)

        form_group_layout.addLayout(form_layout)
        izq_layout.addWidget(form_group)

        # Botones CRUD
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.btn_nuevo = QPushButton("➕ Nuevo")
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_modificar = QPushButton("✏️ Modificar")
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_limpiar = QPushButton("🧹 Limpiar")

        self.btn_nuevo.setStyleSheet(self._estilo_boton_azul())
        self.btn_guardar.setStyleSheet(self._estilo_boton_verde())
        self.btn_modificar.setStyleSheet(self._estilo_boton_azul())
        self.btn_eliminar.setStyleSheet(self._estilo_boton_rojo())
        self.btn_limpiar.setStyleSheet(self._estilo_boton_azul())

        for btn in [self.btn_nuevo, self.btn_guardar, self.btn_modificar, self.btn_eliminar, self.btn_limpiar]:
            btn.setMinimumHeight(28)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        izq_layout.addLayout(btn_layout)

        splitter.addWidget(panel_izq)

        # Panel derecho: lotes
        panel_der = QFrame()
        panel_der.setStyleSheet("QFrame { background-color: #E8E8E8; border-radius: 8px; }")
        der_layout = QVBoxLayout(panel_der)
        der_layout.setContentsMargins(5, 5, 5, 5)
        der_layout.setSpacing(5)

        # ✅ Tabla de lotes con columnas redimensionables
        self.tabla_lotes = QTableWidget()
        self.tabla_lotes.setColumnCount(4)
        self.tabla_lotes.setHorizontalHeaderLabels(["N° Lote", "Fecha Venc.", "Inicial", "Actual"])
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_lotes.setShowGrid(True)
        self.tabla_lotes.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_lotes.setColumnWidth(0, 100)
        self.tabla_lotes.setColumnWidth(1, 100)
        self.tabla_lotes.setColumnWidth(2, 80)
        self.tabla_lotes.setAlternatingRowColors(True)
        self.tabla_lotes.setMinimumHeight(120)
        der_layout.addWidget(self.tabla_lotes)

        lote_frame = QFrame()
        lote_frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        lote_frame_layout = QVBoxLayout(lote_frame)
        lote_frame_layout.setContentsMargins(5, 5, 5, 5)
        lote_frame_layout.setSpacing(4)

        lote_frame_layout.addWidget(LabelSeccionAzul("NUEVO LOTE"))

        lote_form = QHBoxLayout()
        self.txt_numero_lote = LineEditBlanco()
        self.txt_numero_lote.setPlaceholderText("Lote")
        self.txt_fecha_venc = LineEditBlanco()
        self.txt_fecha_venc.setPlaceholderText("AAAA-MM-DD")
        self.txt_cantidad_lote = LineEditBlanco()
        self.txt_cantidad_lote.setPlaceholderText("Cant.")
        btn_crear_lote = QPushButton("➕ Crear")
        btn_crear_lote.setFixedWidth(70)
        btn_crear_lote.setStyleSheet(self._estilo_boton_verde())
        btn_crear_lote.clicked.connect(self.crear_lote)

        lote_form.addWidget(self.txt_numero_lote)
        lote_form.addWidget(self.txt_fecha_venc)
        lote_form.addWidget(self.txt_cantidad_lote)
        lote_form.addWidget(btn_crear_lote)
        lote_form.addStretch()

        lote_frame_layout.addLayout(lote_form)
        der_layout.addWidget(lote_frame)

        splitter.addWidget(panel_der)
        # ✅ Ajuste de proporciones del splitter para 1000px
        splitter.setSizes([580, 380])
        layout.addWidget(splitter)

        self.btn_nuevo.clicked.connect(self.limpiar_formulario)
        self.btn_guardar.clicked.connect(self.guardar_producto)
        self.btn_modificar.clicked.connect(self.modificar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self._cargar_categorias()

        return tab

    # ==================== PESTAÑA 2: STOCK ====================
    
    def _crear_tab_stock(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        frame_stock = QFrame()
        frame_stock.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        stock_layout = QVBoxLayout(frame_stock)
        stock_layout.setContentsMargins(5, 5, 5, 5)
        stock_layout.setSpacing(5)

        stock_layout.addWidget(LabelSeccionAzul("📦 STOCK REAL"))

        # ✅ Tabla de stock con columnas redimensionables
        self.tabla_stock = QTableWidget()
        self.tabla_stock.setColumnCount(7)
        self.tabla_stock.setHorizontalHeaderLabels(["Código", "Producto", "Stock", "Crítico", "Unidad", "Próx. Venc.", "Estado"])
        
        self.tabla_stock.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.tabla_stock.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        
        self.tabla_stock.setShowGrid(True)
        self.tabla_stock.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_stock.setColumnWidth(0, 80)
        self.tabla_stock.setColumnWidth(2, 60)
        self.tabla_stock.setColumnWidth(3, 60)
        self.tabla_stock.setColumnWidth(4, 60)
        self.tabla_stock.setColumnWidth(5, 90)
        self.tabla_stock.setColumnWidth(6, 70)
        
        self.tabla_stock.setAlternatingRowColors(True)
        self.tabla_stock.setMinimumHeight(400)
        stock_layout.addWidget(self.tabla_stock)

        layout.addWidget(frame_stock)

        btn_layout = QHBoxLayout()
        btn_refrescar = QPushButton("🔄 Actualizar Stock")
        btn_refrescar.setStyleSheet(self._estilo_boton_azul())
        btn_refrescar.clicked.connect(self.cargar_stock)

        btn_imprimir_stock = QPushButton("🖨️ Imprimir Stock")
        btn_imprimir_stock.setStyleSheet(self._estilo_boton_azul())
        btn_imprimir_stock.clicked.connect(self.imprimir_stock)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_refrescar)
        btn_layout.addWidget(btn_imprimir_stock)
        layout.addLayout(btn_layout)

        return tab

    # ==================== PESTAÑA 3: MÁS VENDIDOS ====================
    
    def _crear_tab_mas_vendidos(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(5)

        frame_layout.addWidget(LabelSeccionAzul("🏆 PRODUCTOS MÁS VENDIDOS"))

        self.figure = Figure(figsize=(7, 3.5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(280)
        frame_layout.addWidget(self.canvas)

        # ✅ Tabla con columnas redimensionables
        self.tabla_mas_vendidos = QTableWidget()
        self.tabla_mas_vendidos.setColumnCount(3)
        self.tabla_mas_vendidos.setHorizontalHeaderLabels(["Producto", "Cantidad Vendida", "Total Vendido"])
        self.tabla_mas_vendidos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_mas_vendidos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_mas_vendidos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_mas_vendidos.setShowGrid(True)
        self.tabla_mas_vendidos.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_mas_vendidos.setAlternatingRowColors(True)
        self.tabla_mas_vendidos.setMaximumHeight(150)
        frame_layout.addWidget(self.tabla_mas_vendidos)

        layout.addWidget(frame)

        btn_layout = QHBoxLayout()
        btn_imprimir = QPushButton("🖨️ Imprimir Reporte")
        btn_imprimir.setStyleSheet(self._estilo_boton_azul())
        btn_imprimir.clicked.connect(self.imprimir_mas_vendidos)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        layout.addLayout(btn_layout)

        return tab

    # ==================== PESTAÑA 4: ÚLTIMAS VENTAS ====================
    
    def _crear_tab_ultimas_ventas(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(5)

        frame_layout.addWidget(LabelSeccionAzul("🕐 ÚLTIMAS VENTAS"))

        # ✅ Tabla con columnas redimensionables
        self.tabla_ultimas_ventas = QTableWidget()
        self.tabla_ultimas_ventas.setColumnCount(5)
        self.tabla_ultimas_ventas.setHorizontalHeaderLabels(["Fecha", "Factura", "Cliente", "Producto", "Cantidad"])
        self.tabla_ultimas_ventas.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla_ultimas_ventas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_ultimas_ventas.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_ultimas_ventas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_ultimas_ventas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.tabla_ultimas_ventas.setShowGrid(True)
        self.tabla_ultimas_ventas.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_ultimas_ventas.setColumnWidth(0, 90)
        self.tabla_ultimas_ventas.setColumnWidth(1, 100)
        self.tabla_ultimas_ventas.setColumnWidth(2, 150)
        self.tabla_ultimas_ventas.setColumnWidth(4, 70)
        self.tabla_ultimas_ventas.setAlternatingRowColors(True)
        self.tabla_ultimas_ventas.setMinimumHeight(380)
        frame_layout.addWidget(self.tabla_ultimas_ventas)

        layout.addWidget(frame)

        btn_layout = QHBoxLayout()
        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setStyleSheet(self._estilo_boton_azul())
        btn_refrescar.clicked.connect(self.cargar_ultimas_ventas)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_refrescar)
        layout.addLayout(btn_layout)

        return tab

    # ==================== PESTAÑA 5: CATÁLOGO ====================
    
    def _crear_tab_catalogo(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        filtro_layout = QHBoxLayout()
        self.cmb_filtro_cat = ComboBlanco()
        self.cmb_filtro_cat.setMinimumWidth(200)
        self.cmb_filtro_cat.currentIndexChanged.connect(self.cargar_catalogo)
        filtro_layout.addWidget(QLabel("Categoría:"))
        filtro_layout.addWidget(self.cmb_filtro_cat)
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        self.scroll_catalogo = QScrollArea()
        self.scroll_catalogo.setWidgetResizable(True)
        self.scroll_catalogo.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        
        self.scroll_catalogo.setWidget(self.grid_widget)
        layout.addWidget(self.scroll_catalogo)

        return tab

    # ==================== ESTILOS DE BOTONES ====================
    
    def _estilo_boton_azul(self):
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

    def _estilo_boton_rojo(self):
        return """
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """

    # ==================== FUNCIONES COMPARTIDAS ====================
    
    def _cargar_categorias(self):
        self.cmb_categoria.clear()
        self.cmb_categoria.addItem("-- Sin categoría --", None)
        for c in self.categoria_modelo.listar_todas():
            self.cmb_categoria.addItem(c['nombre'], c['id'])
    
    def _cargar_categorias_catalogo(self):
        self.cmb_filtro_cat.clear()
        self.cmb_filtro_cat.addItem("Todas las categorías", None)
        for c in self.categoria_modelo.listar_todas():
            self.cmb_filtro_cat.addItem(c['nombre'], c['id'])
    
    def cargar_foto(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if not archivo:
            return
        try:
            with open(archivo, 'rb') as f:
                self.foto_bytes = f.read()
            pixmap = QPixmap()
            pixmap.loadFromData(self.foto_bytes)
            self.lbl_foto.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen:\n{e}")
    
    def gestionar_categorias(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Gestionar categorías")
        dialogo.setFixedSize(400, 350)
        dialogo.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                color: black;
            }
            QTableWidget::item {
                color: black;
            }
            QHeaderView::section {
                background-color: #1565C0;
                color: white;
                padding: 5px;
            }
            QLabel {
                color: black;
                background-color: transparent;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton#btnEliminar {
                background-color: #D32F2F;
            }
            QPushButton#btnEliminar:hover {
                background-color: #B71C1C;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                padding: 5px;
                color: black;
            }
        """)
        
        layout = QVBoxLayout(dialogo)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        lista = QTableWidget()
        lista.setColumnCount(1)
        lista.setHorizontalHeaderLabels(["Nombre"])
        lista.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lista.setAlternatingRowColors(True)
        self._refrescar_lista_categorias(lista)
        layout.addWidget(lista)

        form_layout = QHBoxLayout()
        form_layout.setSpacing(8)
        
        txt_nueva = QLineEdit()
        txt_nueva.setPlaceholderText("Nueva categoría...")
        txt_nueva.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                padding: 5px;
                color: black;
            }
            QLineEdit:focus {
                border-color: #1565C0;
            }
        """)
        
        btn_agregar = QPushButton("➕ Agregar")
        btn_agregar.setStyleSheet(self._estilo_boton_azul())
        
        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.setObjectName("btnEliminar")
        btn_eliminar.setStyleSheet(self._estilo_boton_rojo())

        def agregar_categoria():
            nombre = txt_nueva.text().strip()
            if nombre:
                try:
                    self.categoria_modelo.crear(nombre)
                    self._cargar_categorias()
                    self._refrescar_lista_categorias(lista)
                    self._cargar_categorias_catalogo()
                    txt_nueva.clear()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(dialogo, "Error", "La categoría ya existe.")

        def eliminar_categoria():
            fila = lista.currentRow()
            if fila >= 0:
                nombre = lista.item(fila, 0).text()
                categorias = self.categoria_modelo.listar_todas()
                for c in categorias:
                    if c['nombre'] == nombre:
                        self.categoria_modelo.eliminar(c['id'])
                        self._cargar_categorias()
                        self._refrescar_lista_categorias(lista)
                        self._cargar_categorias_catalogo()
                        break

        btn_agregar.clicked.connect(agregar_categoria)
        btn_eliminar.clicked.connect(eliminar_categoria)
        
        form_layout.addWidget(txt_nueva)
        form_layout.addWidget(btn_agregar)
        form_layout.addWidget(btn_eliminar)
        layout.addLayout(form_layout)

        dialogo.exec()
    
    def _refrescar_lista_categorias(self, lista):
        categorias = self.categoria_modelo.listar_todas()
        lista.setRowCount(len(categorias))
        for i, c in enumerate(categorias):
            item = QTableWidgetItem(c['nombre'])
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item.setForeground(QColor(0, 0, 0))
            lista.setItem(i, 0, item)
    
    # ==================== CRUD PRODUCTOS ====================
    
    def cargar_productos(self):
        texto = self.txt_buscar.text().strip()
        cur = self.db.cursor()
        if texto:
            cur.execute("SELECT id, codigo_producto, descripcion, precio_costo, precio_venta, stock_actual FROM productos WHERE activo=1 AND (codigo_producto LIKE ? OR descripcion LIKE ?) LIMIT 100", 
                       (f"%{texto}%", f"%{texto}%"))
        else:
            cur.execute("SELECT id, codigo_producto, descripcion, precio_costo, precio_venta, stock_actual FROM productos WHERE activo=1 LIMIT 100")
        registros = [dict(row) for row in cur.fetchall()]
        self.tabla.setRowCount(len(registros))
        for fila, prod in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(prod["codigo_producto"]))
            self.tabla.setItem(fila, 1, QTableWidgetItem(prod["descripcion"][:35]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(f"${prod['precio_costo']:,.2f}"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"${prod['precio_venta']:,.2f}"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"{prod['stock_actual']:.2f}"))
            self.tabla.item(fila, 0).setData(Qt.ItemDataRole.UserRole, prod["id"])
    
    def seleccionar_producto(self):
        indices = self.tabla.selectedItems()
        if not indices:
            self.producto_seleccionado_id = None
            self.tabla_lotes.setRowCount(0)
            return
        fila = indices[0].row()
        id_prod = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.producto_seleccionado_id = id_prod
        prod = self.controlador_productos.obtener_producto(id_prod)
        if prod:
            self.txt_codigo.setText(prod["codigo_producto"])
            self.txt_descripcion.setText(prod["descripcion"])
            self.txt_costo.setText(str(prod["precio_costo"]))
            self.txt_venta.setText(str(prod["precio_venta"]))
            self.txt_stock_critico.setText(str(prod["stock_critico"]))
            self.txt_unidad.setText(prod["unidad_medida"])
            idx = self.cmb_categoria.findData(prod.get("categoria_id"))
            self.cmb_categoria.setCurrentIndex(idx if idx >= 0 else 0)
            self.txt_detalle.setText(prod.get("detalle", ""))
            precio_oferta = prod.get("precio_oferta")
            self.txt_precio_oferta.setText(str(precio_oferta) if precio_oferta else "")
            self.chk_destacado.setChecked(bool(prod.get("destacado", 0)))
            stock_actual = prod.get("stock_actual", 0)
            self.txt_stock_inicial.setPlaceholderText(f"Stock actual: {stock_actual}")
            self.txt_stock_inicial.clear()
            foto_blob = prod.get("foto")
            if foto_blob:
                pixmap = QPixmap()
                pixmap.loadFromData(foto_blob)
                self.lbl_foto.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.foto_bytes = foto_blob
            else:
                self.lbl_foto.setText("Sin foto")
                self.foto_bytes = None
            self.cargar_lotes()
    
    def cargar_lotes(self):
        if not self.producto_seleccionado_id:
            self.tabla_lotes.setRowCount(0)
            return
        lotes = self.lote_modelo.listar_por_producto(self.producto_seleccionado_id)
        self.tabla_lotes.setRowCount(len(lotes))
        for fila, lote in enumerate(lotes):
            self.tabla_lotes.setItem(fila, 0, QTableWidgetItem(lote['numero_lote'] or ""))
            self.tabla_lotes.setItem(fila, 1, QTableWidgetItem(lote['fecha_vencimiento']))
            self.tabla_lotes.setItem(fila, 2, QTableWidgetItem(f"{lote['cantidad_inicial']:.2f}"))
            self.tabla_lotes.setItem(fila, 3, QTableWidgetItem(f"{lote['cantidad_actual']:.2f}"))
    
    def crear_lote(self):
        if not self.producto_seleccionado_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto primero.")
            return
        fecha = self.txt_fecha_venc.text().strip()
        cantidad = self.txt_cantidad_lote.text().strip()
        if not fecha or not cantidad:
            QMessageBox.warning(self, "Error", "Complete fecha y cantidad.")
            return
        try:
            date.fromisoformat(fecha)
            cantidad_valida = float(cantidad)
            if cantidad_valida <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Error", "Fecha o cantidad inválida.")
            return
        try:
            self.lote_modelo.crear(
                producto_id=self.producto_seleccionado_id,
                numero_lote=self.txt_numero_lote.text().strip() or None,
                fecha_vencimiento=fecha,
                cantidad_inicial=cantidad_valida
            )
            self.cargar_lotes()
            self.txt_numero_lote.clear()
            self.txt_fecha_venc.clear()
            self.txt_cantidad_lote.clear()
            self.cargar_productos()
            self.cargar_stock()
            QMessageBox.information(self, "Éxito", "Lote creado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el lote: {e}")
    
    def limpiar_formulario(self):
        self.txt_codigo.clear()
        self.txt_descripcion.clear()
        self.txt_costo.clear()
        self.txt_venta.clear()
        self.txt_stock_critico.clear()
        self.txt_unidad.clear()
        self.txt_detalle.clear()
        self.txt_precio_oferta.clear()
        self.txt_stock_inicial.clear()
        self.cmb_categoria.setCurrentIndex(0)
        self.chk_destacado.setChecked(False)
        self.lbl_foto.setText("Sin foto")
        self.foto_bytes = None
        self.tabla_lotes.setRowCount(0)
        self.producto_seleccionado_id = None
    
    def guardar_producto(self):
        try:
            codigo = self.txt_codigo.text().strip()
            if not codigo:
                raise ValueError("El código es obligatorio.")
            
            existente = self.controlador_productos.obtener_producto_por_codigo(codigo)
            if existente:
                raise ValueError("Ya existe un producto con ese código.")
            
            stock_inicial = float(self.txt_stock_inicial.text() or 0)
            
            producto_id = self.controlador_productos.crear_producto(
                codigo_producto=codigo,
                descripcion=self.txt_descripcion.text().strip(),
                precio_costo=float(self.txt_costo.text() or 0),
                precio_venta=float(self.txt_venta.text() or 0),
                stock_critico=float(self.txt_stock_critico.text() or 0),
                unidad_medida=self.txt_unidad.text().strip() or "unidad",
                categoria_id=self.cmb_categoria.currentData(),
                foto=self.foto_bytes,
                detalle=self.txt_detalle.text().strip() or None,
                precio_oferta=float(self.txt_precio_oferta.text() or 0) if self.txt_precio_oferta.text() else None,
                destacado=1 if self.chk_destacado.isChecked() else 0,
            )
            
            if stock_inicial > 0:
                fecha_vencimiento = (date.today() + timedelta(days=365)).isoformat()
                self.lote_modelo.crear(
                    producto_id=producto_id,
                    numero_lote=f"LOTE-{codigo}-001",
                    fecha_vencimiento=fecha_vencimiento,
                    cantidad_inicial=stock_inicial
                )
            
            self.cargar_productos()
            self.cargar_stock()
            self.cargar_catalogo()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", f"Producto creado. Stock inicial: {stock_inicial}")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
    
    def modificar_producto(self):
        if not self.producto_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto para modificar.")
            return
        try:
            self.controlador_productos.modificar_producto(
                self.producto_seleccionado_id,
                codigo_producto=self.txt_codigo.text().strip(),
                descripcion=self.txt_descripcion.text().strip(),
                precio_costo=float(self.txt_costo.text() or 0),
                precio_venta=float(self.txt_venta.text() or 0),
                stock_critico=float(self.txt_stock_critico.text() or 0),
                unidad_medida=self.txt_unidad.text().strip(),
                categoria_id=self.cmb_categoria.currentData(),
                foto=self.foto_bytes,
                detalle=self.txt_detalle.text().strip() or None,
                precio_oferta=float(self.txt_precio_oferta.text() or 0) if self.txt_precio_oferta.text() else None,
                destacado=1 if self.chk_destacado.isChecked() else 0,
            )
            
            stock_agregar = self.txt_stock_inicial.text().strip()
            if stock_agregar:
                try:
                    cantidad = float(stock_agregar)
                    if cantidad > 0:
                        codigo = self.txt_codigo.text().strip()
                        fecha_vencimiento = (date.today() + timedelta(days=365)).isoformat()
                        self.lote_modelo.crear(
                            producto_id=self.producto_seleccionado_id,
                            numero_lote=f"ADD-{codigo}-{date.today().strftime('%Y%m%d')}",
                            fecha_vencimiento=fecha_vencimiento,
                            cantidad_inicial=cantidad
                        )
                        QMessageBox.information(self, "Stock", f"Se agregaron {cantidad} unidades.")
                except:
                    pass
            
            self.cargar_productos()
            self.cargar_stock()
            self.cargar_catalogo()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto actualizado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo modificar: {e}")
    
    def eliminar_producto(self):
        if not self.producto_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto.")
            return
        if QMessageBox.question(self, "Confirmar", "¿Eliminar producto seleccionado?") == QMessageBox.StandardButton.Yes:
            self.controlador_productos.eliminar_producto(self.producto_seleccionado_id)
            self.cargar_productos()
            self.cargar_stock()
            self.cargar_catalogo()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto eliminado.")
    
    # ==================== STOCK ====================
    
    def cargar_stock(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.codigo_producto, p.descripcion, p.stock_actual, p.stock_critico,
                   p.unidad_medida,
                   (SELECT MIN(l.fecha_vencimiento) FROM lotes l
                    WHERE l.producto_id = p.id AND l.cantidad_actual > 0) as prox_venc
            FROM productos p
            WHERE p.activo = 1
            ORDER BY prox_venc ASC NULLS LAST, p.descripcion ASC
            LIMIT 100
        """)
        productos = cur.fetchall()
        self.tabla_stock.setRowCount(len(productos))
        for fila, prod in enumerate(productos):
            self.tabla_stock.setItem(fila, 0, QTableWidgetItem(prod['codigo_producto']))
            self.tabla_stock.setItem(fila, 1, QTableWidgetItem(prod['descripcion'][:35]))
            self.tabla_stock.setItem(fila, 2, QTableWidgetItem(f"{prod['stock_actual']:.2f}"))
            self.tabla_stock.setItem(fila, 3, QTableWidgetItem(f"{prod['stock_critico']:.2f}"))
            self.tabla_stock.setItem(fila, 4, QTableWidgetItem(prod['unidad_medida']))
            self.tabla_stock.setItem(fila, 5, QTableWidgetItem(prod['prox_venc'] or "N/A"))
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
            self.tabla_stock.setItem(fila, 6, item)
    
    def imprimir_stock(self):
        html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Stock</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                h1 { color: #1A237E; text-align: center; font-size: 16px; }
                table { border-collapse: collapse; width: 100%; margin-top: 15px; }
                th { background-color: #1565C0; color: white; padding: 8px; font-size: 11px; }
                td { border: 1px solid #ddd; padding: 6px; font-size: 10px; }
                .fecha { text-align: center; color: #666; margin-bottom: 15px; font-size: 10px; }
            </style>
        </head>
        <body>
            <h1>REPORTE DE STOCK</h1>
            <div class="fecha">Fecha: """ + date.today().isoformat() + """</div>
            <table>
                <tr>
                    <th>Código</th>
                    <th>Producto</th>
                    <th>Stock</th>
                    <th>Crítico</th>
                    <th>Unidad</th>
                    <th>Próx. Venc.</th>
                    <th>Estado</th>
                </tr>
        """
        
        for row in range(self.tabla_stock.rowCount()):
            codigo = self.tabla_stock.item(row, 0).text()
            producto = self.tabla_stock.item(row, 1).text()
            stock = self.tabla_stock.item(row, 2).text()
            critico = self.tabla_stock.item(row, 3).text()
            unidad = self.tabla_stock.item(row, 4).text()
            venc = self.tabla_stock.item(row, 5).text()
            estado = self.tabla_stock.item(row, 6).text()
            
            html += f"""
                <tr>
                    <td>{codigo}</td>
                    <td>{producto}</td>
                    <td style="text-align:right">{stock}</td>
                    <td style="text-align:right">{critico}</td>
                    <td>{unidad}</td>
                    <td>{venc}</td>
                    <td>{estado}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            doc = QTextEdit()
            doc.setHtml(html)
            doc.print_(printer)
    
    # ==================== MÁS VENDIDOS ====================
    
    def cargar_mas_vendidos(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion, SUM(fd.cantidad) as total_cantidad, SUM(fd.cantidad * fd.precio_unitario) as total_venta
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            GROUP BY p.id
            ORDER BY total_cantidad DESC
            LIMIT 20
        """)
        top = cur.fetchall()
        
        if not top:
            self.tabla_mas_vendidos.setRowCount(1)
            self.tabla_mas_vendidos.setSpan(0, 0, 1, 3)
            item = QTableWidgetItem("No hay ventas registradas")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_mas_vendidos.setItem(0, 0, item)
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Sin datos de ventas", ha='center', va='center', fontsize=12)
            self.figure.tight_layout()
            self.canvas.draw()
            return
        
        self.tabla_mas_vendidos.setRowCount(len(top))
        for i, row in enumerate(top):
            self.tabla_mas_vendidos.setItem(i, 0, QTableWidgetItem(row['descripcion'][:40]))
            self.tabla_mas_vendidos.setItem(i, 1, QTableWidgetItem(f"{row['total_cantidad']:.0f}"))
            self.tabla_mas_vendidos.setItem(i, 2, QTableWidgetItem(f"${row['total_venta']:,.2f}"))
        
        nombres = [row['descripcion'][:25] for row in top[:10]]
        cantidades = [row['total_cantidad'] for row in top[:10]]
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.barh(nombres[::-1], cantidades[::-1], color='#1565C0', height=0.6)
        ax.set_xlabel("Unidades vendidas", fontsize=9)
        ax.set_title("Top 10 productos más vendidos", fontsize=11)
        ax.tick_params(axis='both', labelsize=8)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def imprimir_mas_vendidos(self):
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
            </style>
        </head>
        <body>
            <h1>PRODUCTOS MÁS VENDIDOS</h1>
            <div class="fecha">Fecha: """ + date.today().isoformat() + """</div>
            <table>
                <tr>
                    <th>#</th>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Total Vendido</th>
                </tr>
        """
        
        for row in range(self.tabla_mas_vendidos.rowCount()):
            if self.tabla_mas_vendidos.item(row, 0).text() == "No hay ventas registradas":
                break
            producto = self.tabla_mas_vendidos.item(row, 0).text()
            cantidad = self.tabla_mas_vendidos.item(row, 1).text()
            total = self.tabla_mas_vendidos.item(row, 2).text()
            html += f"""
                <tr>
                    <td style="text-align:center">{row + 1}</td>
                    <td>{producto}</td>
                    <td style="text-align:right">{cantidad}</td>
                    <td style="text-align:right">{total}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            doc = QTextEdit()
            doc.setHtml(html)
            doc.print_(printer)
    
    # ==================== ÚLTIMAS VENTAS ====================
    
    def cargar_ultimas_ventas(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT f.fecha, f.numero_factura, c.razon_social, p.descripcion, fd.cantidad
            FROM factura_detalle fd
            JOIN facturas f ON fd.factura_id = f.id
            JOIN productos p ON fd.producto_id = p.id
            JOIN clientes c ON f.cliente_id = c.id
            ORDER BY f.fecha DESC, f.numero_factura DESC
            LIMIT 50
        """)
        ventas = cur.fetchall()
        self.tabla_ultimas_ventas.setRowCount(len(ventas))
        for fila, v in enumerate(ventas):
            self.tabla_ultimas_ventas.setItem(fila, 0, QTableWidgetItem(v['fecha']))
            self.tabla_ultimas_ventas.setItem(fila, 1, QTableWidgetItem(v['numero_factura']))
            self.tabla_ultimas_ventas.setItem(fila, 2, QTableWidgetItem(v['razon_social'][:25]))
            self.tabla_ultimas_ventas.setItem(fila, 3, QTableWidgetItem(v['descripcion'][:35]))
            self.tabla_ultimas_ventas.setItem(fila, 4, QTableWidgetItem(f"{v['cantidad']:.2f}"))
    
    # ==================== CATÁLOGO ====================
    
    def cargar_catalogo(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        cat_id = self.cmb_filtro_cat.currentData()
        cur = self.db.cursor()
        if cat_id:
            cur.execute("SELECT * FROM productos WHERE activo=1 AND categoria_id=? ORDER BY descripcion", (cat_id,))
        else:
            cur.execute("SELECT * FROM productos WHERE activo=1 ORDER BY descripcion")
        productos = [dict(row) for row in cur.fetchall()]

        columnas = 5
        for i, prod in enumerate(productos):
            tarjeta = TarjetaProducto(prod)
            fila = i // columnas
            col = i % columnas
            self.grid_layout.addWidget(tarjeta, fila, col)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaProductosUnificada(db)
    ventana.show()
    sys.exit(app.exec())