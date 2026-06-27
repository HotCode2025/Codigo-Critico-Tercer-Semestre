"""
Código Crítico - Tercer Semestre Año 2026
Vista de Cuenta Corriente – Rediseñada con solapas AZULES.
Incluye pestaña de deudores simplificada.
"""

import sqlite3
from datetime import date, timedelta
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QHeaderView,
                               QGroupBox, QFrame, QComboBox, QDateEdit,
                               QTabWidget, QWidget, QFileDialog, QScrollArea,
                               QTextEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

from controladores.controlador_ventas import ControladorVentas
from modelos.cliente import Cliente


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

class VistaCuentaCorriente(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.controlador = ControladorVentas(db)
        self.cliente_modelo = Cliente(db)
        
        self.setWindowTitle("Cuenta Corriente")
        self.setFixedSize(800, 600)

        # ✅ ESTILO CON TABS AZULES
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

        # ========== SELECCIÓN DE CLIENTE ==========
        frame_cliente = QFrame()
        frame_cliente.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        cliente_layout = QHBoxLayout(frame_cliente)
        cliente_layout.setContentsMargins(8, 6, 8, 6)
        cliente_layout.setSpacing(8)

        cliente_layout.addWidget(LabelCampoAzul("Cliente:"))
        self.cmb_cliente = ComboBlanco()
        self.cmb_cliente.setMinimumWidth(300)
        self.cmb_cliente.currentIndexChanged.connect(self.cargar_datos_cliente)
        cliente_layout.addWidget(self.cmb_cliente, 1)

        btn_refrescar = QPushButton("🔄")
        btn_refrescar.setFixedSize(30, 28)
        btn_refrescar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px;")
        btn_refrescar.clicked.connect(self.cargar_clientes)
        cliente_layout.addWidget(btn_refrescar)

        tarjeta_layout.addWidget(frame_cliente)

        # ========== RESÚMEN DEL CLIENTE ==========
        frame_resumen = QFrame()
        frame_resumen.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        resumen_layout = QHBoxLayout(frame_resumen)
        resumen_layout.setContentsMargins(8, 6, 8, 6)
        resumen_layout.setSpacing(15)

        self.lbl_saldo = QLabel("💰 Saldo: $0.00")
        self.lbl_limite = QLabel("📊 Límite: $0.00")
        self.lbl_disponible = QLabel("✅ Disponible: $0.00")

        self.lbl_saldo.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.lbl_limite.setStyleSheet("font-size: 12px;")
        self.lbl_disponible.setStyleSheet("font-size: 12px; font-weight: bold;")

        resumen_layout.addWidget(self.lbl_saldo)
        resumen_layout.addWidget(self.lbl_limite)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_disponible)

        tarjeta_layout.addWidget(frame_resumen)

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        self.tab_movimientos = self._crear_tab_movimientos()
        self.tabs.addTab(self.tab_movimientos, "📋 MOVIMIENTOS")
        
        self.tab_cobros = self._crear_tab_cobros()
        self.tabs.addTab(self.tab_cobros, "💰 REGISTRAR COBRO")
        
        self.tab_deudores = self._crear_tab_deudores()
        self.tabs.addTab(self.tab_deudores, "⚠️ DEUDORES")
        
        tarjeta_layout.addWidget(self.tabs)

        layout.addWidget(tarjeta)

        # Variables
        self.cliente_actual_id = None
        
        # Cargar datos
        self.cargar_clientes()
        self.cargar_tabla_deudores()

    # ==================== PESTAÑA 1: MOVIMIENTOS ====================
    
    def _crear_tab_movimientos(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Filtros
        frame_filtros = QFrame()
        frame_filtros.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtros_layout = QHBoxLayout(frame_filtros)
        filtros_layout.setContentsMargins(8, 6, 8, 6)
        filtros_layout.setSpacing(8)

        filtros_layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = DateEditBlanco()
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(self.fecha_desde)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = DateEditBlanco()
        self.fecha_hasta.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.fecha_hasta)

        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.setFixedWidth(70)
        btn_filtrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px;")
        btn_filtrar.clicked.connect(self.cargar_movimientos)
        filtros_layout.addWidget(btn_filtrar)

        filtros_layout.addStretch()

        btn_exportar = QPushButton("📎 Exportar CSV")
        btn_exportar.setFixedWidth(100)
        btn_exportar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px;")
        btn_exportar.clicked.connect(self.exportar_movimientos)
        filtros_layout.addWidget(btn_exportar)

        layout.addWidget(frame_filtros)

        # Tabla de movimientos
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(6)
        self.tabla_movimientos.setHorizontalHeaderLabels(
            ["Fecha", "Tipo", "Referencia", "Importe", "Saldo", "Observaciones"]
        )
        self.tabla_movimientos.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.tabla_movimientos.setShowGrid(True)
        self.tabla_movimientos.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_movimientos.setAlternatingRowColors(True)
        self.tabla_movimientos.setMinimumHeight(380)
        tabla_layout.addWidget(self.tabla_movimientos)

        layout.addWidget(frame_tabla)

        return tab

    # ==================== PESTAÑA 2: REGISTRAR COBRO ====================
    
    def _crear_tab_cobros(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(8)

        # Datos del cobro
        frame_datos = QFrame()
        frame_datos.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        datos_layout = QVBoxLayout(frame_datos)
        datos_layout.setContentsMargins(8, 8, 8, 8)
        datos_layout.setSpacing(8)

        datos_layout.addWidget(LabelSeccionAzul("DATOS DEL COBRO"))

        form_layout = QGridLayout()
        form_layout.setSpacing(8)
        form_layout.setHorizontalSpacing(10)

        form_layout.addWidget(LabelCampoAzul("Medio de Pago *"), 0, 0)
        self.cmb_medio_pago = ComboBlanco()
        self.cmb_medio_pago.addItems(["EFECTIVO", "TRANSFERENCIA", "CHEQUE", "DEBITO", "CREDITO"])
        form_layout.addWidget(self.cmb_medio_pago, 0, 1)

        form_layout.addWidget(LabelCampoAzul("Importe *"), 1, 0)
        self.txt_importe_cobro = LineEditBlanco()
        self.txt_importe_cobro.setPlaceholderText("0.00")
        form_layout.addWidget(self.txt_importe_cobro, 1, 1)

        form_layout.addWidget(LabelCampoAzul("Observaciones"), 2, 0)
        self.txt_observaciones_cobro = LineEditBlanco()
        self.txt_observaciones_cobro.setPlaceholderText("Observaciones del cobro...")
        form_layout.addWidget(self.txt_observaciones_cobro, 2, 1)

        datos_layout.addLayout(form_layout)
        scroll_layout.addWidget(frame_datos)

        # Facturas pendientes
        frame_facturas = QFrame()
        frame_facturas.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        facturas_layout = QVBoxLayout(frame_facturas)
        facturas_layout.setContentsMargins(8, 8, 8, 8)
        facturas_layout.setSpacing(8)

        facturas_layout.addWidget(LabelSeccionAzul("FACTURAS PENDIENTES"))

        self.tabla_facturas_pendientes = QTableWidget()
        self.tabla_facturas_pendientes.setColumnCount(4)
        self.tabla_facturas_pendientes.setHorizontalHeaderLabels(
            ["Factura", "Fecha", "Total", "Pendiente"]
        )
        self.tabla_facturas_pendientes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_facturas_pendientes.setShowGrid(True)
        self.tabla_facturas_pendientes.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_facturas_pendientes.setAlternatingRowColors(True)
        self.tabla_facturas_pendientes.setMaximumHeight(150)
        self.tabla_facturas_pendientes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        facturas_layout.addWidget(self.tabla_facturas_pendientes)

        scroll_layout.addWidget(frame_facturas)

        # Botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(10)

        self.btn_registrar_cobro = QPushButton("💰 Registrar Cobro")
        self.btn_limpiar = QPushButton("🧹 Limpiar")

        self.btn_registrar_cobro.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_limpiar.setStyleSheet("background-color: #1565C0; color: white;")

        self.btn_registrar_cobro.clicked.connect(self.registrar_cobro)
        self.btn_limpiar.clicked.connect(self.limpiar_cobro)

        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_registrar_cobro)
        botones_layout.addWidget(self.btn_limpiar)

        scroll_layout.addWidget(frame_botones)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        return tab

    # ==================== PESTAÑA 3: DEUDORES (SIMPLIFICADA) ====================
    
    def _crear_tab_deudores(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Filtros
        frame_filtros = QFrame()
        frame_filtros.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtros_layout = QHBoxLayout(frame_filtros)
        filtros_layout.setContentsMargins(8, 6, 8, 6)
        filtros_layout.setSpacing(8)

        lbl_filtro = QLabel("Mostrar:")
        lbl_filtro.setStyleSheet("color: #000000; font-size: 10px;")
        filtros_layout.addWidget(lbl_filtro)
        
        self.cmb_filtro_deuda = ComboBlanco()
        self.cmb_filtro_deuda.addItems(["Todos", "Con deuda (>$0)", "Sin deuda ($0)", "A favor (<$0)"])
        self.cmb_filtro_deuda.setFixedWidth(150)
        self.cmb_filtro_deuda.currentIndexChanged.connect(self.cargar_tabla_deudores)
        filtros_layout.addWidget(self.cmb_filtro_deuda)

        self.txt_filtro_nombre = LineEditBlanco()
        self.txt_filtro_nombre.setPlaceholderText("🔍 Buscar por nombre o CUIT...")
        filtros_layout.addWidget(self.txt_filtro_nombre, 1)

        btn_buscar = QPushButton("🔍 Buscar")
        btn_buscar.setFixedWidth(70)
        btn_buscar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px;")
        btn_buscar.clicked.connect(self.cargar_tabla_deudores)
        filtros_layout.addWidget(btn_buscar)

        filtros_layout.addStretch()

        layout.addWidget(frame_filtros)

        # Tabla de deudores (solo 3 columnas)
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_deudores = QTableWidget()
        self.tabla_deudores.setColumnCount(3)
        self.tabla_deudores.setHorizontalHeaderLabels(
            ["Razón Social", "Teléfono", "Saldo"]
        )
        # Ajustar anchos
        self.tabla_deudores.setColumnWidth(0, 380)
        self.tabla_deudores.setColumnWidth(1, 120)
        self.tabla_deudores.setColumnWidth(2, 120)
        self.tabla_deudores.horizontalHeader().setStretchLastSection(False)
        self.tabla_deudores.setShowGrid(True)
        self.tabla_deudores.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_deudores.setAlternatingRowColors(True)
        self.tabla_deudores.setMinimumHeight(380)
        self.tabla_deudores.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla_layout.addWidget(self.tabla_deudores)

        layout.addWidget(frame_tabla)

        # Totales
        frame_totales = QFrame()
        frame_totales.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        totales_layout = QHBoxLayout(frame_totales)
        totales_layout.setContentsMargins(8, 6, 8, 6)

        self.lbl_total_deuda = QLabel("💰 Deuda total: $0.00")
        self.lbl_total_deuda.setStyleSheet("font-weight: bold; font-size: 11px; color: #000000;")
        self.lbl_cantidad_clientes = QLabel("👥 Clientes: 0")
        self.lbl_cantidad_clientes.setStyleSheet("font-size: 11px; color: #000000;")

        totales_layout.addWidget(self.lbl_total_deuda)
        totales_layout.addStretch()
        totales_layout.addWidget(self.lbl_cantidad_clientes)

        layout.addWidget(frame_totales)

        # Botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(10)

        btn_exportar_csv = QPushButton("📎 Exportar CSV")
        btn_exportar_csv.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
        btn_exportar_csv.clicked.connect(self.exportar_deudores_csv)

        btn_imprimir = QPushButton("🖨️ Imprimir Listado")
        btn_imprimir.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
        btn_imprimir.clicked.connect(self.imprimir_listado_deudores)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_exportar_csv)
        botones_layout.addWidget(btn_imprimir)

        layout.addWidget(frame_botones)

        return tab

    # =================== FUNCIONES PRINCIPALES ===================
    
    def cargar_clientes(self):
        clientes = self.cliente_modelo.listar_todos(solo_activos=True)
        self.cmb_cliente.clear()
        
        for c in clientes:
            saldo = c.get('saldo_cuenta_corriente', 0) or 0
            self.cmb_cliente.addItem(f"{c['razon_social']} - Saldo: ${saldo:,.2f}", c['id'])
        
        if clientes:
            self.cmb_cliente.setCurrentIndex(0)

    def cargar_datos_cliente(self):
        index = self.cmb_cliente.currentIndex()
        if index < 0:
            return
        
        self.cliente_actual_id = self.cmb_cliente.itemData(index)
        
        if not self.cliente_actual_id:
            return
        
        self.cargar_resumen_cliente()
        self.cargar_movimientos()
        self.cargar_facturas_pendientes()

    def cargar_resumen_cliente(self):
        if not self.cliente_actual_id:
            return
        
        cliente = self.cliente_modelo.obtener_por_id(self.cliente_actual_id)
        if cliente:
            saldo = cliente.get('saldo_cuenta_corriente', 0) or 0
            limite = cliente.get('limite_credito', 0) or 0
            disponible = limite - saldo if limite > 0 else float('inf')
            
            self.lbl_saldo.setText(f"💰 Saldo: ${saldo:,.2f}")
            
            if saldo > 0:
                self.lbl_saldo.setStyleSheet("font-size: 12px; font-weight: bold; color: #D32F2F;")
            elif saldo < 0:
                self.lbl_saldo.setStyleSheet("font-size: 12px; font-weight: bold; color: #4CAF50;")
            else:
                self.lbl_saldo.setStyleSheet("font-size: 12px; font-weight: bold; color: #000000;")
            
            self.lbl_limite.setText(f"📊 Límite: ${limite:,.2f}")
            
            if limite > 0:
                if disponible < 0:
                    self.lbl_disponible.setText(f"⚠️ Excede límite en ${-disponible:,.2f}")
                    self.lbl_disponible.setStyleSheet("font-size: 12px; font-weight: bold; color: #D32F2F;")
                else:
                    self.lbl_disponible.setText(f"✅ Disponible: ${disponible:,.2f}")
                    self.lbl_disponible.setStyleSheet("font-size: 12px; font-weight: bold; color: #4CAF50;")
            else:
                self.lbl_disponible.setText(f"📈 Sin límite definido")
                self.lbl_disponible.setStyleSheet("font-size: 12px; font-weight: bold; color: #FF9800;")

    def cargar_movimientos(self):
        if not self.cliente_actual_id:
            return
        
        desde = self.fecha_desde.date().toString("yyyy-MM-dd")
        hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")
        
        movimientos = self.controlador.obtener_movimientos_cliente(
            self.cliente_actual_id, desde, hasta
        )
        
        self.tabla_movimientos.setRowCount(len(movimientos))
        
        for i, mov in enumerate(movimientos):
            self.tabla_movimientos.setItem(i, 0, QTableWidgetItem(mov['fecha']))
            
            tipo = mov['tipo_movimiento']
            tipo_color = {
                'FACTURA': '#D32F2F',
                'COBRO': '#4CAF50',
                'ANULACION': '#FF9800',
                'REVERSO_COBRO': '#9C27B0',
                'AJUSTE': '#2196F3'
            }.get(tipo, '#000000')
            
            item_tipo = QTableWidgetItem(tipo)
            item_tipo.setForeground(QColor(tipo_color))
            self.tabla_movimientos.setItem(i, 1, item_tipo)
            
            ref = mov['referencia_id']
            self.tabla_movimientos.setItem(i, 2, QTableWidgetItem(ref[:12] + "..." if len(ref) > 12 else ref))
            
            importe = mov['importe']
            item_importe = QTableWidgetItem(f"${importe:,.2f}")
            if importe > 0:
                item_importe.setForeground(QColor('#D32F2F'))
            else:
                item_importe.setForeground(QColor('#4CAF50'))
            self.tabla_movimientos.setItem(i, 3, item_importe)
            
            self.tabla_movimientos.setItem(i, 4, QTableWidgetItem(f"${mov['saldo_resultante']:,.2f}"))
            self.tabla_movimientos.setItem(i, 5, QTableWidgetItem(mov.get('observaciones', '')))

    def cargar_facturas_pendientes(self):
        if not self.cliente_actual_id:
            return
        
        facturas = self.controlador.obtener_facturas_pendientes_cliente(self.cliente_actual_id)
        
        self.tabla_facturas_pendientes.setRowCount(len(facturas))
        
        for i, fact in enumerate(facturas):
            self.tabla_facturas_pendientes.setItem(i, 0, QTableWidgetItem(fact['numero_factura']))
            self.tabla_facturas_pendientes.setItem(i, 1, QTableWidgetItem(fact['fecha']))
            self.tabla_facturas_pendientes.setItem(i, 2, QTableWidgetItem(f"${fact['total']:,.2f}"))
            self.tabla_facturas_pendientes.setItem(i, 3, QTableWidgetItem(f"${fact['saldo_pendiente']:,.2f}"))
            
            self.tabla_facturas_pendientes.item(i, 0).setData(Qt.ItemDataRole.UserRole, fact['id'])

    # =================== DEUDORES ===================
    
    def cargar_tabla_deudores(self):
        filtro = self.cmb_filtro_deuda.currentText()
        busqueda = self.txt_filtro_nombre.text().strip()
        
        query = """
            SELECT id, razon_social, telefono, saldo_cuenta_corriente
            FROM clientes WHERE activo = 1
        """
        params = []
        
        if filtro == "Con deuda (>$0)":
            query += " AND saldo_cuenta_corriente > 0"
        elif filtro == "Sin deuda ($0)":
            query += " AND saldo_cuenta_corriente = 0"
        elif filtro == "A favor (<$0)":
            query += " AND saldo_cuenta_corriente < 0"
        
        if busqueda:
            query += " AND (razon_social LIKE ? OR telefono LIKE ?)"
            params.append(f"%{busqueda}%")
            params.append(f"%{busqueda}%")
        
        query += " ORDER BY saldo_cuenta_corriente DESC"
        
        cur = self.db.cursor()
        cur.execute(query, params)
        clientes = cur.fetchall()
        
        self.tabla_deudores.setRowCount(len(clientes))
        total_deuda = 0
        total_favor = 0
        
        for i, cli in enumerate(clientes):
            self.tabla_deudores.setItem(i, 0, QTableWidgetItem(cli['razon_social']))
            self.tabla_deudores.setItem(i, 1, QTableWidgetItem(cli['telefono'] or "-"))
            
            saldo = cli['saldo_cuenta_corriente'] or 0
            if saldo > 0:
                total_deuda += saldo
            else:
                total_favor += abs(saldo)
            
            item_saldo = QTableWidgetItem(f"${saldo:,.2f}")
            if saldo > 0:
                item_saldo.setForeground(QColor('#D32F2F'))
                item_saldo.setBackground(QColor(255, 240, 240))
            elif saldo < 0:
                item_saldo.setForeground(QColor('#4CAF50'))
                item_saldo.setBackground(QColor(240, 255, 240))
            self.tabla_deudores.setItem(i, 2, item_saldo)
            
            self.tabla_deudores.item(i, 0).setData(Qt.ItemDataRole.UserRole, cli['id'])
        
        self.lbl_total_deuda.setText(f"💰 Deuda total: ${total_deuda:,.2f}")
        self.lbl_cantidad_clientes.setText(f"👥 Clientes: {len(clientes)}")
    
    def exportar_deudores_csv(self):
        import csv
        from datetime import datetime
        
        filtro = self.cmb_filtro_deuda.currentText()
        busqueda = self.txt_filtro_nombre.text().strip()
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar listado", 
            f"deudores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        
        if filename:
            query = """
                SELECT razon_social, telefono, saldo_cuenta_corriente
                FROM clientes WHERE activo = 1
            """
            params = []
            
            if filtro == "Con deuda (>$0)":
                query += " AND saldo_cuenta_corriente > 0"
            elif filtro == "Sin deuda ($0)":
                query += " AND saldo_cuenta_corriente = 0"
            elif filtro == "A favor (<$0)":
                query += " AND saldo_cuenta_corriente < 0"
            
            if busqueda:
                query += " AND (razon_social LIKE ? OR telefono LIKE ?)"
                params.append(f"%{busqueda}%")
                params.append(f"%{busqueda}%")
            
            query += " ORDER BY saldo_cuenta_corriente DESC"
            
            cur = self.db.cursor()
            cur.execute(query, params)
            clientes = cur.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Razón Social", "Teléfono", "Saldo"])
                for cli in clientes:
                    writer.writerow([
                        cli['razon_social'],
                        cli['telefono'] or "",
                        f"{cli['saldo_cuenta_corriente'] or 0:.2f}"
                    ])
            
            self._mostrar_mensaje("Exportar", f"✅ Listado exportado a:\n{filename}")

    def imprimir_listado_deudores(self):
        filtro = self.cmb_filtro_deuda.currentText()
        busqueda = self.txt_filtro_nombre.text().strip()
        
        query = """
            SELECT razon_social, telefono, saldo_cuenta_corriente
            FROM clientes WHERE activo = 1
        """
        params = []
        
        if filtro == "Con deuda (>$0)":
            query += " AND saldo_cuenta_corriente > 0"
        elif filtro == "Sin deuda ($0)":
            query += " AND saldo_cuenta_corriente = 0"
        elif filtro == "A favor (<$0)":
            query += " AND saldo_cuenta_corriente < 0"
        
        if busqueda:
            query += " AND (razon_social LIKE ? OR telefono LIKE ?)"
            params.append(f"%{busqueda}%")
            params.append(f"%{busqueda}%")
        
        query += " ORDER BY saldo_cuenta_corriente DESC"
        
        cur = self.db.cursor()
        cur.execute(query, params)
        clientes = cur.fetchall()
        
        total_deuda = sum(c['saldo_cuenta_corriente'] or 0 for c in clientes if (c['saldo_cuenta_corriente'] or 0) > 0)
        
        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Listado de Deudores</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #1A237E; text-align: center; font-size: 18px; }}
                h2 {{ color: #1565C0; font-size: 14px; }}
                .fecha {{ text-align: center; color: #666; margin-bottom: 20px; font-size: 11px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
                th {{ background-color: #1A237E; color: white; padding: 10px; font-size: 12px; text-align: left; }}
                td {{ border: 1px solid #ddd; padding: 8px; font-size: 11px; }}
                .total {{ font-weight: bold; font-size: 13px; margin-top: 20px; text-align: right; padding-top: 10px; border-top: 2px solid #1A237E; }}
                .deuda {{ color: #D32F2F; font-weight: bold; }}
                .numero {{ text-align: right; }}
            </style>
        </head>
        <body>
            <h1>SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA</h1>
            <h2>LISTADO DE CLIENTES CON CUENTA CORRIENTE</h2>
            <div class="fecha">Fecha de emisión: {date.today().strftime('%d/%m/%Y')}</div>
            <div class="fecha">Filtro aplicado: {filtro}</div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Razón Social</th>
                        <th>Teléfono</th>
                        <th>Saldo</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, cli in enumerate(clientes, 1):
            saldo = cli['saldo_cuenta_corriente'] or 0
            saldo_text = f"${saldo:,.2f}"
            saldo_class = "deuda" if saldo > 0 else ""
            
            html += f"""
                <tr>
                    <td class="numero">{i}</td>
                    <td>{cli['razon_social']}</td>
                    <td>{cli['telefono'] or '-'}</td>
                    <td class="numero {saldo_class}">{saldo_text}</td>
                </tr>
            """
        
        html += f"""
                </tbody>
            </table>
            <div class="total">
                💰 <span class="deuda">Deuda total: ${total_deuda:,.2f}</span>
            </div>
            <div style="margin-top: 30px; text-align: center; font-size: 9px; color: #999;">
                Documento generado por Sistema de Distribución - Código Crítico
            </div>
        </body>
        </html>
        """
        
        preview = QDialog(self)
        preview.setWindowTitle("Vista previa - Listado de Clientes")
        preview.resize(700, 500)
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
            dialog.setWindowTitle("Imprimir")
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                visor.print_(printer)
        
        btn_imprimir.clicked.connect(imprimir)
        btn_cerrar.clicked.connect(preview.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_imprimir)
        btn_layout.addWidget(btn_cerrar)
        layout.addLayout(btn_layout)
        
        preview.exec()

    def registrar_cobro(self):
        if not self.cliente_actual_id:
            self._mostrar_mensaje("Error", "Seleccione un cliente.", QMessageBox.Icon.Warning)
            return
        
        try:
            importe = float(self.txt_importe_cobro.text() or 0)
            if importe <= 0:
                raise ValueError("El importe debe ser mayor a cero.")
        except ValueError:
            self._mostrar_mensaje("Error", "Ingrese un importe válido.", QMessageBox.Icon.Warning)
            return
        
        medio_pago = self.cmb_medio_pago.currentText()
        observaciones = self.txt_observaciones_cobro.text().strip()
        
        facturas_ids = []
        for item in self.tabla_facturas_pendientes.selectedItems():
            if item.column() == 0:
                factura_id = self.tabla_facturas_pendientes.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
                if factura_id and factura_id not in facturas_ids:
                    facturas_ids.append(factura_id)
        
        try:
            self.controlador.registrar_cobro(
                cliente_id=self.cliente_actual_id,
                importe=importe,
                medio_pago=medio_pago,
                observaciones=observaciones,
                factura_ids=facturas_ids if facturas_ids else None
            )
            
            self._mostrar_mensaje("Éxito", f"Cobro por ${importe:,.2f} registrado correctamente.")
            
            self.limpiar_cobro()
            self.cargar_datos_cliente()
            self.cargar_tabla_deudores()
            
        except Exception as e:
            self._mostrar_mensaje("Error", str(e), QMessageBox.Icon.Critical)

    def limpiar_cobro(self):
        self.txt_importe_cobro.clear()
        self.txt_observaciones_cobro.clear()
        self.cmb_medio_pago.setCurrentIndex(0)
        self.tabla_facturas_pendientes.clearSelection()

    def exportar_movimientos(self):
        if not self.cliente_actual_id:
            self._mostrar_mensaje("Error", "Seleccione un cliente.", QMessageBox.Icon.Warning)
            return
        
        import csv
        from datetime import datetime
        
        cliente = self.cliente_modelo.obtener_por_id(self.cliente_actual_id)
        nombre_cliente = cliente['razon_social'].replace(" ", "_")[:30]
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo", 
            f"movimientos_{nombre_cliente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        
        if filename:
            desde = self.fecha_desde.date().toString("yyyy-MM-dd")
            hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")
            
            movimientos = self.controlador.obtener_movimientos_cliente(self.cliente_actual_id, desde, hasta)
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Tipo", "Referencia", "Importe", "Saldo", "Observaciones"])
                
                for mov in movimientos:
                    writer.writerow([
                        mov['fecha'],
                        mov['tipo_movimiento'],
                        mov['referencia_id'],
                        f"{mov['importe']:.2f}",
                        f"{mov['saldo_resultante']:.2f}",
                        mov.get('observaciones', '')
                    ])
            
            self._mostrar_mensaje("Exportar", f"Movimientos exportados a:\n{filename}")

    # =================== MENSAJES ===================
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


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaCuentaCorriente(db)
    ventana.show()
    sys.exit(app.exec())