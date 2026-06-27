"""
Código Crítico - Tercer Semestre Año 2026
Vista de Facturación – Rediseñada con dos solapas azules.
Solapa 1: Facturación Fiscal
Solapa 2: Historial de Facturas (con detalle impreso)
"""

import sqlite3
import os
import sys
import tempfile
import subprocess
from datetime import date, datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QHeaderView,
                               QFrame, QComboBox, QSpinBox, QTabWidget,
                               QWidget, QSplitter, QTextEdit, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PyQt6.QtCore import QRect

from controladores.controlador_ventas import ControladorVentas
from modelos.nota_venta import NotaVenta
from modelos.producto import Producto
from modelos.cliente import Cliente
from modelos.preventista import Preventista
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle,
                                Spacer, Image)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.pdfgen import canvas


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

class VistaFacturacion(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.controlador_ventas = ControladorVentas(db)
        self.nota_venta_modelo = NotaVenta(db)
        self.producto_modelo = Producto(db)
        self.cliente_modelo = Cliente(db)
        self.preventista_modelo = Preventista(db)
        self.setWindowTitle("Facturación Fiscal")
        self.setFixedSize(1000, 650)

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
            QPushButton {
                border-radius: 4px;
                padding: 5px 14px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        
        self._cargar_parametros()
        self.detalle_temporal = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(8, 8, 8, 8)
        tarjeta_layout.setSpacing(5)

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        # Solapa 1: Facturación Fiscal
        self.tab_facturacion = self._crear_tab_facturacion()
        self.tabs.addTab(self.tab_facturacion, "💰 FACTURACIÓN FISCAL")
        
        # Solapa 2: Historial de Facturas
        self.tab_historial = self._crear_tab_historial()
        self.tabs.addTab(self.tab_historial, "📄 HISTORIAL DE FACTURAS")
        
        tarjeta_layout.addWidget(self.tabs)
        layout.addWidget(tarjeta)

        # Cargar datos
        self._cargar_clientes()
        self._cargar_preventistas()
        self._cargar_productos()
        self.cargar_historial()

    # ==================== PESTAÑA 1: FACTURACIÓN FISCAL ====================
    
    def _crear_tab_facturacion(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # ---------- ENCABEZADO ----------
        frame_encabezado = QFrame()
        frame_encabezado.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        enc_layout = QVBoxLayout(frame_encabezado)
        enc_layout.setContentsMargins(8, 8, 8, 8)
        enc_layout.setSpacing(8)

        enc_layout.addWidget(LabelSeccionAzul("DATOS DE LA FACTURA"))

        form_enc = QGridLayout()
        form_enc.setSpacing(6)
        form_enc.setHorizontalSpacing(10)

        form_enc.addWidget(LabelCampoAzul("Cliente *"), 0, 0)
        self.cmb_cliente = ComboBlanco()
        self.cmb_cliente.setMinimumWidth(200)
        form_enc.addWidget(self.cmb_cliente, 0, 1)
        
        form_enc.addWidget(LabelCampoAzul("Preventista *"), 0, 2)
        self.cmb_preventista = ComboBlanco()
        form_enc.addWidget(self.cmb_preventista, 0, 3)

        form_enc.addWidget(LabelCampoAzul("Tipo Comprobante"), 1, 0)
        self.cmb_tipo_comprobante = ComboBlanco()
        self.cmb_tipo_comprobante.addItems(["A", "B", "C"])
        form_enc.addWidget(self.cmb_tipo_comprobante, 1, 1)
        
        form_enc.addWidget(LabelCampoAzul("Número Factura"), 1, 2)
        self.txt_numero_factura = LineEditBlanco()
        self.txt_numero_factura.setText(self._generar_numero_factura())
        self.txt_numero_factura.setReadOnly(True)
        form_enc.addWidget(self.txt_numero_factura, 1, 3)

        enc_layout.addLayout(form_enc)
        layout.addWidget(frame_encabezado)

        # ---------- PRODUCTOS ----------
        frame_productos = QFrame()
        frame_productos.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        prod_layout = QVBoxLayout(frame_productos)
        prod_layout.setContentsMargins(8, 8, 8, 8)
        prod_layout.setSpacing(8)

        prod_layout.addWidget(LabelSeccionAzul("PRODUCTOS"))

        self.tabla_detalle = QTableWidget()
        self.tabla_detalle.setColumnCount(4)
        self.tabla_detalle.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla_detalle.setShowGrid(True)
        self.tabla_detalle.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_detalle.setAlternatingRowColors(True)
        self.tabla_detalle.setMinimumHeight(180)
        prod_layout.addWidget(self.tabla_detalle)

        agg_layout = QHBoxLayout()
        agg_layout.setSpacing(6)

        self.cmb_producto = ComboBlanco()
        self.cmb_producto.setMinimumWidth(250)
        self.spin_cantidad = SpinBoxBlanco()
        self.spin_cantidad.setRange(1, 99999)
        self.spin_cantidad.setFixedWidth(70)
        self.btn_agregar = QPushButton("➕ Agregar")
        self.btn_agregar.setFixedWidth(90)
        self.btn_quitar = QPushButton("➖ Quitar Último")
        self.btn_quitar.setFixedWidth(100)

        self.btn_agregar.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_quitar.setStyleSheet("background-color: #FF9800; color: white;")

        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_quitar.clicked.connect(self.quitar_ultimo)

        agg_layout.addWidget(QLabel("Producto:"))
        agg_layout.addWidget(self.cmb_producto, 1)
        agg_layout.addWidget(QLabel("Cantidad:"))
        agg_layout.addWidget(self.spin_cantidad)
        agg_layout.addWidget(self.btn_agregar)
        agg_layout.addWidget(self.btn_quitar)
        agg_layout.addStretch()

        prod_layout.addLayout(agg_layout)
        layout.addWidget(frame_productos)

        # ---------- TOTALES ----------
        frame_totales = QFrame()
        frame_totales.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        totales_layout = QHBoxLayout(frame_totales)
        totales_layout.setContentsMargins(8, 6, 8, 6)
        totales_layout.setSpacing(20)

        self.lbl_subtotal = QLabel("Subtotal: $ 0.00")
        self.lbl_iva = QLabel("IVA (21%): $ 0.00")
        self.lbl_total = QLabel("TOTAL: $ 0.00")

        label_style = "font-weight: bold; font-size: 11px; padding: 4px 8px; background-color: #F8F9FA; border-radius: 4px;"
        self.lbl_subtotal.setStyleSheet(label_style + "color: #000000;")
        self.lbl_iva.setStyleSheet(label_style + "color: #000000;")
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px 8px; background-color: #1565C0; border-radius: 4px; color: white;")

        totales_layout.addWidget(self.lbl_subtotal)
        totales_layout.addWidget(self.lbl_iva)
        totales_layout.addStretch()
        totales_layout.addWidget(self.lbl_total)

        layout.addWidget(frame_totales)

        # ---------- OBSERVACIONES ----------
        frame_obs = QFrame()
        frame_obs.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        obs_layout = QVBoxLayout(frame_obs)
        obs_layout.setContentsMargins(8, 6, 8, 6)

        obs_layout.addWidget(LabelCampoAzul("Observaciones"))
        self.txt_observaciones = LineEditBlanco()
        self.txt_observaciones.setPlaceholderText("Observaciones (opcional)...")
        obs_layout.addWidget(self.txt_observaciones)

        layout.addWidget(frame_obs)

        # ---------- BOTONES ----------
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(10)

        self.btn_emitir = QPushButton("💰 Emitir Factura")
        self.btn_limpiar = QPushButton("🗑️ Limpiar Todo")
        self.btn_cancelar = QPushButton("❌ Cancelar")

        self.btn_emitir.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_limpiar.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_cancelar.setStyleSheet("background-color: #D32F2F; color: white;")

        self.btn_emitir.setMinimumHeight(32)
        self.btn_limpiar.setMinimumHeight(32)
        self.btn_cancelar.setMinimumHeight(32)

        self.btn_emitir.clicked.connect(self.emitir_factura)
        self.btn_limpiar.clicked.connect(self.limpiar_todo)
        self.btn_cancelar.clicked.connect(self.reject)

        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_emitir)
        botones_layout.addWidget(self.btn_limpiar)
        botones_layout.addWidget(self.btn_cancelar)

        layout.addWidget(frame_botones)

        return tab

    # ==================== PESTAÑA 2: HISTORIAL DE FACTURAS ====================
    
    def _crear_tab_historial(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # ---------- FILTROS ----------
        frame_filtros = QFrame()
        frame_filtros.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtros_layout = QHBoxLayout(frame_filtros)
        filtros_layout.setContentsMargins(10, 8, 10, 8)
        filtros_layout.setSpacing(10)

        filtros_layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = DateEditBlanco()
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(self.fecha_desde)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = DateEditBlanco()
        self.fecha_hasta.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.fecha_hasta)

        filtros_layout.addWidget(QLabel("Cliente:"))
        self.cmb_filtro_cliente = ComboBlanco()
        self.cmb_filtro_cliente.setMinimumWidth(150)
        self.cmb_filtro_cliente.addItem("-- Todos --", None)
        filtros_layout.addWidget(self.cmb_filtro_cliente)

        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.setFixedWidth(80)
        btn_filtrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold;")
        btn_filtrar.clicked.connect(self.cargar_historial)
        filtros_layout.addWidget(btn_filtrar)

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setFixedWidth(80)
        btn_refrescar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold;")
        btn_refrescar.clicked.connect(self.cargar_historial)
        filtros_layout.addWidget(btn_refrescar)

        filtros_layout.addStretch()

        layout.addWidget(frame_filtros)

        # ---------- TABLA DE FACTURAS ----------
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(6)
        self.tabla_historial.setHorizontalHeaderLabels(["N° Factura", "Fecha", "Cliente", "Tipo", "Total", "Estado"])
        
        self.tabla_historial.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla_historial.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_historial.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_historial.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla_historial.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.tabla_historial.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        
        self.tabla_historial.setColumnWidth(0, 120)
        self.tabla_historial.setColumnWidth(1, 100)
        self.tabla_historial.setColumnWidth(3, 60)
        self.tabla_historial.setColumnWidth(4, 100)
        self.tabla_historial.setColumnWidth(5, 80)
        
        self.tabla_historial.setShowGrid(True)
        self.tabla_historial.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_historial.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_historial.setAlternatingRowColors(True)
        self.tabla_historial.setMinimumHeight(220)
        self.tabla_historial.doubleClicked.connect(self.ver_detalle_factura_impresa)
        tabla_layout.addWidget(self.tabla_historial)

        layout.addWidget(frame_tabla)

        # ---------- BOTONES DE ACCIÓN ----------
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(10)

        btn_ver_detalle = QPushButton("📄 Ver Detalle Impreso")
        btn_ver_detalle.setStyleSheet("background-color: #1565C0; color: white;")
        btn_ver_detalle.clicked.connect(self.ver_detalle_factura_impresa)
        botones_layout.addWidget(btn_ver_detalle)

        btn_anular = QPushButton("❌ Anular Factura")
        btn_anular.setStyleSheet("background-color: #D32F2F; color: white;")
        btn_anular.clicked.connect(self.anular_factura)
        botones_layout.addWidget(btn_anular)

        btn_reimprimir = QPushButton("🖨️ Reimprimir")
        btn_reimprimir.setStyleSheet("background-color: #FF9800; color: white;")
        btn_reimprimir.clicked.connect(self.reimprimir_factura)
        botones_layout.addWidget(btn_reimprimir)

        botones_layout.addStretch()

        layout.addWidget(frame_botones)

        # Cargar clientes para el filtro
        self._cargar_clientes_filtro()

        return tab

    # ==================== FUNCIONES DE FACTURACIÓN ====================
    
    def _cargar_parametros(self):
        cur = self.db.cursor()
        cur.execute("SELECT moneda, punto_venta, ultimo_numero_factura FROM parametros WHERE id = 1")
        row = cur.fetchone()
        if row:
            self.moneda = row['moneda'] if row['moneda'] else 'ARS'
            self.punto_venta = row['punto_venta'] if row['punto_venta'] else '0001'
            self.ultimo_numero = row['ultimo_numero_factura'] if row['ultimo_numero_factura'] else 1
        else:
            self.moneda = 'ARS'
            self.punto_venta = '0001'
            self.ultimo_numero = 1

    def _generar_numero_factura(self):
        return f"{self.punto_venta}-{self.ultimo_numero:08d}"

    def _actualizar_numero_factura(self):
        self.ultimo_numero += 1
        self.db.execute("UPDATE parametros SET ultimo_numero_factura = ? WHERE id = 1", (self.ultimo_numero,))
        self.db.commit()
        self.txt_numero_factura.setText(self._generar_numero_factura())

    def _cargar_clientes(self):
        clientes = self.cliente_modelo.listar_todos(solo_activos=True)
        self.cmb_cliente.clear()
        for c in clientes:
            nombre = c['razon_social'][:40] if len(c['razon_social']) > 40 else c['razon_social']
            self.cmb_cliente.addItem(f"{nombre} - {c.get('cuit', '')}", c['id'])

    def _cargar_clientes_filtro(self):
        clientes = self.cliente_modelo.listar_todos(solo_activos=True)
        self.cmb_filtro_cliente.clear()
        self.cmb_filtro_cliente.addItem("-- Todos --", None)
        for c in clientes:
            self.cmb_filtro_cliente.addItem(c['razon_social'][:40], c['id'])

    def _cargar_preventistas(self):
        preventistas = self.preventista_modelo.listar_todos(solo_activos=True)
        self.cmb_preventista.clear()
        for p in preventistas:
            self.cmb_preventista.addItem(f"{p['nombre']} {p['apellido']}", p['id'])

    def _cargar_productos(self):
        productos = self.producto_modelo.listar_todos(solo_activos=True)
        self.cmb_producto.clear()
        for prod in productos[:100]:
            nombre = f"{prod['codigo'][:10]} - {prod['descripcion'][:30]}"
            self.cmb_producto.addItem(nombre, prod['id'])

    def agregar_producto(self):
        id_prod = self.cmb_producto.currentData()
        if not id_prod:
            self._mostrar_mensaje("Aviso", "Seleccione un producto.", QMessageBox.Icon.Warning)
            return
        
        cantidad = self.spin_cantidad.value()
        prod = self.producto_modelo.obtener_por_id(id_prod)
        
        if not prod:
            return
        
        if cantidad > prod['stock_actual']:
            self._mostrar_mensaje("Stock insuficiente", 
                                 f"Stock disponible: {prod['stock_actual']:.0f} unidades",
                                 QMessageBox.Icon.Warning)
            return
        
        precio = prod['precio_venta'] if prod else 0.0
        self.detalle_temporal.append((id_prod, cantidad, precio, prod['descripcion']))
        self._refrescar_tabla()
        self._calcular_totales()
        self.spin_cantidad.setValue(1)

    def quitar_ultimo(self):
        if self.detalle_temporal:
            self.detalle_temporal.pop()
            self._refrescar_tabla()
            self._calcular_totales()

    def _refrescar_tabla(self):
        self.tabla_detalle.setRowCount(len(self.detalle_temporal))
        for fila, (id_prod, cant, precio, desc) in enumerate(self.detalle_temporal):
            subtotal = cant * precio
            self.tabla_detalle.setItem(fila, 0, QTableWidgetItem(desc[:35]))
            item_cant = QTableWidgetItem(str(cant))
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_detalle.setItem(fila, 1, item_cant)
            item_precio = QTableWidgetItem(f"${precio:,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_detalle.setItem(fila, 2, item_precio)
            item_subtotal = QTableWidgetItem(f"${subtotal:,.2f}")
            item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_detalle.setItem(fila, 3, item_subtotal)

    def _calcular_totales(self):
        total_general = 0.0
        for _, cant, precio, _ in self.detalle_temporal:
            total_general += cant * precio
        
        iva = total_general * 0.21
        total = total_general + iva
        
        self.lbl_subtotal.setText(f"Subtotal: $ {total_general:,.2f}")
        self.lbl_iva.setText(f"IVA (21%): $ {iva:,.2f}")
        self.lbl_total.setText(f"TOTAL: $ {total:,.2f}")

    def limpiar_todo(self):
        if self.detalle_temporal:
            confirm = self._confirmar_dialogo("Limpiar", "¿Eliminar todos los productos agregados?")
            if confirm == QMessageBox.StandardButton.Yes:
                self.detalle_temporal.clear()
                self._refrescar_tabla()
                self._calcular_totales()
                self.txt_observaciones.clear()
        else:
            self.detalle_temporal.clear()
            self._refrescar_tabla()
            self._calcular_totales()
            self.txt_observaciones.clear()

    def emitir_factura(self):
        cliente_id = self.cmb_cliente.currentData()
        preventista_id = self.cmb_preventista.currentData()
        numero = self.txt_numero_factura.text().strip()
        tipo = self.cmb_tipo_comprobante.currentText()
        observaciones = self.txt_observaciones.text().strip()

        if not cliente_id:
            self._mostrar_mensaje("Error", "Debe seleccionar un cliente.", QMessageBox.Icon.Warning)
            return
        
        if not preventista_id:
            self._mostrar_mensaje("Error", "Debe seleccionar un preventista.", QMessageBox.Icon.Warning)
            return
        
        if not self.detalle_temporal:
            self._mostrar_mensaje("Error", "Debe agregar al menos un producto.", QMessageBox.Icon.Warning)
            return

        confirm = self._confirmar_dialogo(
            "Confirmar Factura",
            f"¿Emitir factura {numero} por {self.lbl_total.text()}?"
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            items = []
            for id_prod, cant, precio, _ in self.detalle_temporal:
                items.append({
                    "producto_id": id_prod,
                    "cantidad": cant,
                    "precio_unitario": precio
                })
            
            self.controlador_ventas.emitir_factura_directa(
                cliente_id=cliente_id,
                preventista_id=preventista_id,
                tipo_comprobante=tipo,
                numero_factura=numero,
                items=items,
                observaciones=observaciones
            )
            
            self._actualizar_numero_factura()
            
            self._mostrar_mensaje(
                "Factura Emitida",
                f"✅ Factura {numero} emitida correctamente.\nSe abrirá el comprobante PDF."
            )
            
            self._generar_pdf_factura(cliente_id, numero, tipo, observaciones)
            
            self.limpiar_todo()
            self.cargar_historial()
            
        except Exception as e:
            self._mostrar_mensaje("Error", f"No se pudo emitir la factura:\n{str(e)}", QMessageBox.Icon.Critical)

    # ==================== HISTORIAL DE FACTURAS ====================
    
    def cargar_historial(self):
        desde = self.fecha_desde.date().toString("yyyy-MM-dd")
        hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")
        cliente_id = self.cmb_filtro_cliente.currentData()
        
        query = """
            SELECT f.id, f.numero_factura, f.fecha, f.tipo_comprobante, f.total, f.estado,
                   c.razon_social as cliente
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.fecha BETWEEN ? AND ?
        """
        params = [desde, hasta]
        
        if cliente_id:
            query += " AND f.cliente_id = ?"
            params.append(cliente_id)
        
        query += " ORDER BY f.fecha DESC, f.numero_factura DESC"
        
        cur = self.db.cursor()
        cur.execute(query, params)
        facturas = cur.fetchall()
        
        self.tabla_historial.setRowCount(len(facturas))
        
        for i, f in enumerate(facturas):
            self.tabla_historial.setItem(i, 0, QTableWidgetItem(f['numero_factura']))
            self.tabla_historial.setItem(i, 1, QTableWidgetItem(f['fecha']))
            self.tabla_historial.setItem(i, 2, QTableWidgetItem(f['cliente']))
            self.tabla_historial.setItem(i, 3, QTableWidgetItem(f['tipo_comprobante']))
            
            item_total = QTableWidgetItem(f"${f['total']:,.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_historial.setItem(i, 4, item_total)
            
            item_estado = QTableWidgetItem(f['estado'])
            if f['estado'] == 'EMITIDA':
                item_estado.setForeground(QColor(40, 167, 69))
            elif f['estado'] == 'ANULADA':
                item_estado.setForeground(QColor(220, 53, 69))
            self.tabla_historial.setItem(i, 5, item_estado)
            
            self.tabla_historial.item(i, 0).setData(Qt.ItemDataRole.UserRole, f['id'])

    def ver_detalle_factura_impresa(self):
        fila = self.tabla_historial.currentRow()
        if fila < 0:
            self._mostrar_mensaje("Aviso", "Seleccione una factura.", QMessageBox.Icon.Warning)
            return
        
        factura_id = self.tabla_historial.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_factura = self.tabla_historial.item(fila, 0).text()
        
        self._mostrar_factura_impresa(factura_id, numero_factura)

    def _mostrar_factura_impresa(self, factura_id, numero_factura):
        """Muestra el detalle de la factura como si fuera impresa."""
        cur = self.db.cursor()
        
        # Obtener datos de la factura
        cur.execute("""
            SELECT f.*, c.razon_social, c.cuit, c.condicion_iva, c.domicilio
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.id = ?
        """, (factura_id,))
        factura = cur.fetchone()
        
        if not factura:
            self._mostrar_mensaje("Error", "Factura no encontrada.", QMessageBox.Icon.Critical)
            return
        
        # Obtener detalles
        cur.execute("""
            SELECT p.descripcion, fd.cantidad, fd.precio_unitario,
                   (fd.cantidad * fd.precio_unitario) as subtotal
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            WHERE fd.factura_id = ?
        """, (factura_id,))
        detalles = cur.fetchall()
        
        # ✅ NUEVO TAMAÑO: 800 x 700
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Factura {numero_factura}")
        dialog.setFixedSize(800, 700)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== MARCA DE AGUA ==========
        lbl_marca_agua = QLabel("SOLO A MODO DE PRUEBA")
        lbl_marca_agua.setStyleSheet("""
            QLabel {
                color: rgba(200, 0, 0, 40);
                font-size: 28px;
                font-weight: bold;
                font-family: Arial;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-30deg);
                background-color: transparent;
                border: none;
            }
        """)
        lbl_marca_agua.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_marca_agua)
        
        # ========== ENCABEZADO ==========
        lbl_empresa = QLabel("SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA")
        lbl_empresa.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E; text-align: center;")
        lbl_empresa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_empresa)
        
        lbl_factura = QLabel(f"FACTURA {factura['tipo_comprobante']} N° {factura['numero_factura']}")
        lbl_factura.setStyleSheet("font-size: 18px; font-weight: bold; color: #1565C0; text-align: center;")
        lbl_factura.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_factura)
        
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
        datos_cliente.addWidget(QLabel(factura['razon_social']), 0, 1)
        datos_cliente.addWidget(QLabel("<b>CUIT:</b>"), 0, 2)
        datos_cliente.addWidget(QLabel(factura['cuit'] or 'N/A'), 0, 3)
        
        datos_cliente.addWidget(QLabel("<b>Condición IVA:</b>"), 1, 0)
        datos_cliente.addWidget(QLabel(factura['condicion_iva']), 1, 1)
        datos_cliente.addWidget(QLabel("<b>Fecha:</b>"), 1, 2)
        datos_cliente.addWidget(QLabel(factura['fecha']), 1, 3)
        
        if factura['domicilio']:
            datos_cliente.addWidget(QLabel("<b>Domicilio:</b>"), 2, 0)
            datos_cliente.addWidget(QLabel(factura['domicilio']), 2, 1, 1, 3)
        
        frame_layout.addLayout(datos_cliente)
        
        frame_layout.addWidget(QLabel(" " * 30))
        
        # ========== TABLA DE PRODUCTOS ==========
        lbl_productos = QLabel("<b>DETALLE DE PRODUCTOS</b>")
        lbl_productos.setStyleSheet("font-size: 12px; color: #1A237E;")
        frame_layout.addWidget(lbl_productos)
        
        tabla_detalle = QTableWidget()
        tabla_detalle.setColumnCount(4)
        tabla_detalle.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
        tabla_detalle.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tabla_detalle.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        tabla_detalle.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        tabla_detalle.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        tabla_detalle.setShowGrid(True)
        tabla_detalle.setGridStyle(Qt.PenStyle.SolidLine)
        tabla_detalle.setAlternatingRowColors(True)
        tabla_detalle.setMinimumHeight(150)
        
        tabla_detalle.setRowCount(len(detalles))
        total = 0
        for i, det in enumerate(detalles):
            tabla_detalle.setItem(i, 0, QTableWidgetItem(det['descripcion']))
            item_cant = QTableWidgetItem(f"{det['cantidad']:.0f}")
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 1, item_cant)
            item_precio = QTableWidgetItem(f"${det['precio_unitario']:,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 2, item_precio)
            item_subtotal = QTableWidgetItem(f"${det['subtotal']:,.2f}")
            item_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla_detalle.setItem(i, 3, item_subtotal)
            total += det['subtotal']
        
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
        
        # ========== OBSERVACIONES ==========
        if factura['observaciones']:
            frame_layout.addWidget(QLabel("<b>Observaciones:</b>"))
            frame_layout.addWidget(QLabel(factura['observaciones']))
        
        # ========== PIE DE PÁGINA ==========
        lbl_pie = QLabel("Gracias por su compra")
        lbl_pie.setStyleSheet("text-align: center; color: #666666; font-size: 10px; margin-top: 15px;")
        lbl_pie.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_pie)
        
        # ========== BOTONES ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 20px; font-weight: bold;")
        btn_cerrar.clicked.connect(dialog.accept)
        
        btn_imprimir = QPushButton("🖨️ Imprimir")
        btn_imprimir.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 8px 20px; font-weight: bold;")
        btn_imprimir.clicked.connect(lambda: self._generar_pdf_factura_desde_id(factura_id, numero_factura))
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        btn_layout.addWidget(btn_cerrar)
        
        frame_layout.addLayout(btn_layout)
        
        layout.addWidget(frame)
        dialog.exec()

    def _generar_pdf_factura_desde_id(self, factura_id, numero):
        """Genera PDF de una factura existente."""
        cur = self.db.cursor()
        
        cur.execute("""
            SELECT f.*, c.razon_social, c.cuit, c.condicion_iva
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.id = ?
        """, (factura_id,))
        factura = cur.fetchone()
        
        if not factura:
            self._mostrar_mensaje("Error", "Factura no encontrada.", QMessageBox.Icon.Critical)
            return
        
        cur.execute("""
            SELECT p.descripcion, fd.cantidad, fd.precio_unitario
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            WHERE fd.factura_id = ?
        """, (factura_id,))
        detalles = cur.fetchall()
        
        # Guardar en detalle temporal para generar PDF
        self.detalle_temporal = []
        for det in detalles:
            self.detalle_temporal.append((
                None,  # id no necesario
                det['cantidad'],
                det['precio_unitario'],
                det['descripcion']
            ))
        
        self._generar_pdf_factura(
            factura['cliente_id'],
            factura['numero_factura'],
            factura['tipo_comprobante'],
            factura['observaciones'] if factura['observaciones'] else ''
        )
        
        self.detalle_temporal = []

    def anular_factura(self):
        fila = self.tabla_historial.currentRow()
        if fila < 0:
            self._mostrar_mensaje("Aviso", "Seleccione una factura.", QMessageBox.Icon.Warning)
            return
        
        factura_id = self.tabla_historial.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_factura = self.tabla_historial.item(fila, 0).text()
        estado = self.tabla_historial.item(fila, 5).text()
        
        if estado == 'ANULADA':
            self._mostrar_mensaje("Aviso", "La factura ya está anulada.", QMessageBox.Icon.Warning)
            return
        
        confirm = self._confirmar_dialogo(
            "Anular Factura",
            f"¿Anular factura {numero_factura}?\nEsta acción no se puede deshacer."
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            self.controlador_ventas.anular_factura(factura_id, "Anulación manual desde sistema")
            self._mostrar_mensaje("Éxito", f"✅ Factura {numero_factura} anulada correctamente.")
            self.cargar_historial()
        except Exception as e:
            self._mostrar_mensaje("Error", f"No se pudo anular:\n{str(e)}", QMessageBox.Icon.Critical)

    def reimprimir_factura(self):
        fila = self.tabla_historial.currentRow()
        if fila < 0:
            self._mostrar_mensaje("Aviso", "Seleccione una factura.", QMessageBox.Icon.Warning)
            return
        
        factura_id = self.tabla_historial.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_factura = self.tabla_historial.item(fila, 0).text()
        estado = self.tabla_historial.item(fila, 5).text()
        
        if estado == 'ANULADA':
            self._mostrar_mensaje("Aviso", "No se puede reimprimir una factura anulada.", QMessageBox.Icon.Warning)
            return
        
        self._generar_pdf_factura_desde_id(factura_id, numero_factura)

    # ==================== GENERACIÓN DE PDF CON MARCA DE AGUA DIAGONAL ====================
    
    def _generar_pdf_factura(self, cliente_id, numero, tipo, observaciones):
        """Genera el PDF de la factura con QR y marca de agua diagonal."""
        try:
            cliente = self.cliente_modelo.obtener_por_id(cliente_id)
            if not cliente:
                return
            
            ruta_temp = os.path.join(tempfile.gettempdir(), f"factura_{numero}.pdf")
            doc = SimpleDocTemplate(ruta_temp, pagesize=A4,
                                    leftMargin=15*mm, rightMargin=15*mm,
                                    topMargin=20*mm, bottomMargin=20*mm)
            elementos = []
            styles = getSampleStyleSheet()
            
            estilo_titulo = ParagraphStyle(
                'TituloFactura',
                parent=styles['Title'],
                fontSize=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#1A237E"),
                spaceAfter=10
            )
            
            estilo_empresa = ParagraphStyle(
                'DatosEmpresa',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER
            )
            
            # ========== ENCABEZADO ==========
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph("<b>SISTEMA DE DISTRIBUCIÓN</b>", estilo_empresa))
            elementos.append(Paragraph("Código Crítico - Tercer Semestre 2026", estilo_empresa))
            elementos.append(Spacer(1, 5))
            
            elementos.append(Paragraph(f"<b>FACTURA {tipo}</b>", estilo_titulo))
            elementos.append(Paragraph(f"Nº {numero}", estilo_titulo))
            elementos.append(Spacer(1, 10))
            
            # ========== DATOS DEL CLIENTE ==========
            elementos.append(Paragraph("<b>DATOS DEL CLIENTE</b>", styles['Heading4']))
            elementos.append(Paragraph(f"<b>Razón Social:</b> {cliente['razon_social']}", styles['Normal']))
            elementos.append(Paragraph(f"<b>CUIT:</b> {cliente.get('cuit', 'N/A')}", styles['Normal']))
            elementos.append(Paragraph(f"<b>Condición IVA:</b> {cliente.get('condicion_iva', 'N/A')}", styles['Normal']))
            elementos.append(Spacer(1, 5))
            
            elementos.append(Paragraph(f"<b>Fecha de emisión:</b> {date.today().isoformat()}", styles['Normal']))
            elementos.append(Spacer(1, 10))
            
            # ========== TABLA DE PRODUCTOS ==========
            data = [["Producto", "Cantidad", "Precio Unit.", "Subtotal"]]
            total_general = 0.0
            
            for id_prod, cant, precio, desc in self.detalle_temporal:
                subtotal = cant * precio
                total_general += subtotal
                data.append([desc[:40], f"{cant:.1f}", f"${precio:,.2f}", f"${subtotal:,.2f}"])
            
            tabla = Table(data, colWidths=[200, 60, 80, 80])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1565C0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elementos.append(tabla)
            
            # ========== ESPACIO ANTES DE TOTALES ==========
            elementos.append(Spacer(1, 10))
            
            # ========== TOTALES (COMO TEXTO, NO COMO TABLA) ==========
            iva = total_general * 0.21
            total = total_general + iva
            
            # Crear un estilo para los totales alineados a la derecha
            estilo_total = ParagraphStyle(
                'EstiloTotal',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_RIGHT,
                fontName='Helvetica-Bold'
            )
            
            estilo_total_negrita = ParagraphStyle(
                'EstiloTotalNegrita',
                parent=styles['Normal'],
                fontSize=13,
                alignment=TA_RIGHT,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#1A237E")
            )
            
            # Agregar totales como párrafos alineados a la derecha
            elementos.append(Paragraph(f"<b>SUBTOTAL:</b> $ {total_general:,.2f}", estilo_total))
            elementos.append(Paragraph(f"<b>IVA (21%):</b> $ {iva:,.2f}", estilo_total))
            elementos.append(Spacer(1, 3))
            elementos.append(Paragraph(f"<b>TOTAL:</b> $ {total:,.2f}", estilo_total_negrita))
            
            # ========== ESPACIO ANTES DE OBSERVACIONES ==========
            elementos.append(Spacer(1, 15))
            
            if observaciones:
                elementos.append(Paragraph(f"<b>Observaciones:</b> {observaciones}", styles['Normal']))
                elementos.append(Spacer(1, 10))
            
            # ========== QR ==========
            qr_data = f"FACTURA {tipo} Nº {numero}|{date.today().isoformat()}|Cliente: {cliente['razon_social']}|Total: ${total:,.2f}"
            
            try:
                qr_code = qr.QrCodeWidget(qr_data)
                qr_drawing = Drawing(50*mm, 50*mm)
                qr_drawing.add(qr_code)
                elementos.append(qr_drawing)
            except Exception as qr_error:
                print(f"⚠️ Error generando QR: {qr_error}")
                qr_simbolico = Paragraph("""
                    <font size="7" face="Courier">
                    ████████████████████████████████████████<br/>
                    ██                                    ██<br/>
                    ██  ┌─────────────────────────────┐   ██<br/>
                    ██  │  CÓDIGO QR SIMBÓLICO        │   ██<br/>
                    ██  │                             │   ██<br/>
                    ██  │  FACTURA DIGITAL            │   ██<br/>
                    ██  │  Verifique en               │   ██<br/>
                    ██  │  www.distribuidora.com      │   ██<br/>
                    ██  └─────────────────────────────┘   ██<br/>
                    ██                                    ██<br/>
                    ████████████████████████████████████████
                    </font>
                """, styles['Normal'])
                elementos.append(qr_simbolico)
            
            elementos.append(Spacer(1, 5))
            elementos.append(Paragraph("<i>Escanee el código QR para verificar la autenticidad</i>", 
                                       ParagraphStyle('QRInfo', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
            
            # ========== PIE DE PÁGINA ==========
            elementos.append(Spacer(1, 20))
            elementos.append(Paragraph("<hr/>", styles['Normal']))
            elementos.append(Paragraph("<b>Gracias por su compra</b>", estilo_empresa))
            elementos.append(Paragraph("Este comprobante es válido como factura fiscal", 
                                       ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER)))
            
            # ========== CONSTRUIR EL PDF CON MARCA DE AGUA DIAGONAL ==========
            from reportlab.pdfgen import canvas
            
            def add_watermark(canvas_obj, doc_obj):
                """Agrega la marca de agua en diagonal a cada página."""
                canvas_obj.saveState()
                
                # Configurar fuente y color
                canvas_obj.setFont('Helvetica-Bold', 28)
                canvas_obj.setFillColor(colors.Color(0.6, 0.6, 0.6, alpha=0.15))
                
                # Obtener dimensiones de la página
                page_width = doc_obj.pagesize[0]
                page_height = doc_obj.pagesize[1]
                
                # Rotar 45 grados y centrar
                canvas_obj.translate(page_width / 2, page_height / 2)
                canvas_obj.rotate(45)
                
                # Texto de la marca de agua
                texto = "SOLO A MODO DE PRUEBA"
                canvas_obj.drawCentredString(0, 0, texto)
                
                # Segunda línea (más abajo)
                canvas_obj.setFont('Helvetica-Bold', 22)
                texto2 = "LA FACTURA CARECE DE VALIDEZ"
                canvas_obj.drawCentredString(0, -35, texto2)
                
                canvas_obj.restoreState()
            
            # Construir el documento con la marca de agua
            doc.build(elementos, onFirstPage=add_watermark, onLaterPages=add_watermark)
            
            # Abrir el PDF
            if sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', ruta_temp], check=False)
            elif sys.platform.startswith('win32'):
                os.startfile(ruta_temp)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', ruta_temp], check=False)
                
        except Exception as e:
            self._mostrar_mensaje("Error", f"No se pudo generar el PDF:\n{str(e)}", QMessageBox.Icon.Warning)

    # ==================== MENSAJES ====================
    
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

    def _confirmar_dialogo(self, titulo, texto):
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: white; color: black; font-size: 11px; }
            QLabel { color: black; background-color: transparent; font-size: 11px; }
            QPushButton { background-color: #1565C0; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
        """)
        return msg.exec()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaFacturacion(db)
    ventana.show()
    sys.exit(app.exec())