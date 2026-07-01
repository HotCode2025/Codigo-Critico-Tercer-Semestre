"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Vista de Dashboard con UUID
==================================================
📌 USO: Panel principal de métricas y pedidos
"""

import sqlite3
from datetime import date, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QGridLayout, QPushButton, QComboBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QTabWidget, QDialog, QGridLayout,
                               QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controladores.controlador_ventas import ControladorVentas
from modelos.cliente import Cliente
from modelos.producto import Producto
from modelos.nota_venta import NotaVenta
from utilidades import sincronizar_ahora


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


class TarjetaMetrica(QFrame):
    def __init__(self, titulo, valor, color="#1565C0", parent=None):
        super().__init__(parent)
        self.setFixedSize(170, 85)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: #666666; font-size: 10px; font-weight: bold; background-color: transparent;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_valor = QLabel(str(valor))
        lbl_valor.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold; background-color: transparent;")
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)


class VistaDashboard(QWidget):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.controlador_ventas = ControladorVentas(db)
        self.cliente_modelo = Cliente(db)
        self.producto_modelo = Producto(db)
        self.nota_modelo = NotaVenta(db)
        
        # Timer para parpadeo de la solapa (cada 2 segundos)
        self.parpadeo_activo = False
        self.timer_parpadeo = QTimer()
        self.timer_parpadeo.timeout.connect(self._toggle_parpadeo_tab)
        self.timer_parpadeo.setInterval(2000)
        
        self.setStyleSheet("""
            QWidget {
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
            QComboBox {
                background-color: white;
                color: #000000;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
            }
            QFrame {
                background-color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ========== BARRA DE HERRAMIENTAS ==========
        frame_toolbar = QFrame()
        frame_toolbar.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        toolbar_layout = QHBoxLayout(frame_toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(10)

        toolbar_layout.addWidget(QLabel("Período:"))
        self.cmb_periodo = QComboBox()
        self.cmb_periodo.addItems(["Mes Actual", "Mes Anterior", "Año Actual", "Año Anterior"])
        self.cmb_periodo.setFixedWidth(130)
        self.cmb_periodo.currentIndexChanged.connect(self.actualizar_dashboard)
        toolbar_layout.addWidget(self.cmb_periodo)

        toolbar_layout.addStretch()

        self.btn_exportar = QPushButton("📎 Exportar")
        self.btn_exportar.setFixedWidth(90)
        self.btn_exportar.clicked.connect(self.exportar_datos)

        self.btn_refrescar = QPushButton("🔄 Actualizar")
        self.btn_refrescar.setFixedWidth(90)
        self.btn_refrescar.clicked.connect(self.actualizar_dashboard)

        self.btn_sincronizar = QPushButton("🔄 Sincronizar")
        self.btn_sincronizar.setFixedWidth(90)
        self.btn_sincronizar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 5px 12px; font-weight: bold; font-size: 10px; border: none;")
        self.btn_sincronizar.clicked.connect(self.sincronizar_dashboard)

        toolbar_layout.addWidget(self.btn_exportar)
        toolbar_layout.addWidget(self.btn_refrescar)
        toolbar_layout.addWidget(self.btn_sincronizar)

        layout.addWidget(frame_toolbar)

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        # Solapa 0: Métricas
        self.tab_metricas = self._crear_tab_metricas()
        self.tabs.addTab(self.tab_metricas, "📊 MÉTRICAS")
        
        # Solapa 1: Preventistas
        self.tab_preventistas = self._crear_tab_preventistas()
        self.tabs.addTab(self.tab_preventistas, "👥 PREVENTISTAS")
        
        # Solapa 2: Productos
        self.tab_productos = self._crear_tab_productos()
        self.tabs.addTab(self.tab_productos, "📦 PRODUCTOS")
        
        # Solapa 3: PEDIDOS PENDIENTES
        self.tab_pendientes = self._crear_tab_pedidos_pendientes()
        self.tabs.addTab(self.tab_pendientes, "📦 PENDIENTES")
        
        # Solapa 4: PEDIDOS ARMADOS
        self.tab_armados = self._crear_tab_pedidos_armados()
        self.tabs.addTab(self.tab_armados, "📜 ARMADOS")
        
        layout.addWidget(self.tabs)

        # Timer de actualización (cada 30 segundos)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_dashboard)
        self.timer.start(30000)
        
        # Variables
        self.fecha_desde = None
        self.fecha_hasta = None
        
        # Cargar datos
        self.actualizar_dashboard()

    # ==================== PESTAÑA 0: MÉTRICAS ====================
    
    def _crear_tab_metricas(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Grid de tarjetas
        frame_tarjetas = QFrame()
        frame_tarjetas.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tarjetas_layout = QVBoxLayout(frame_tarjetas)
        tarjetas_layout.setContentsMargins(12, 12, 12, 12)
        tarjetas_layout.setSpacing(10)

        tarjetas_layout.addWidget(LabelSeccionAzul("📈 RESUMEN DEL PERÍODO"))

        self.grid_metricas = QGridLayout()
        self.grid_metricas.setSpacing(15)
        self.grid_metricas.setAlignment(Qt.AlignmentFlag.AlignTop)
        tarjetas_layout.addLayout(self.grid_metricas)

        layout.addWidget(frame_tarjetas)

        # Gráfico
        frame_grafico = QFrame()
        frame_grafico.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        grafico_layout = QVBoxLayout(frame_grafico)
        grafico_layout.setContentsMargins(12, 12, 12, 12)
        grafico_layout.setSpacing(10)

        grafico_layout.addWidget(LabelSeccionAzul("📊 VENTAS DIARIAS"))

        self.figure = Figure(figsize=(8, 3.5), tight_layout=True, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(280)
        grafico_layout.addWidget(self.canvas)

        layout.addWidget(frame_grafico)

        return tab

    # ==================== PESTAÑA 1: PREVENTISTAS ====================
    
    def _crear_tab_preventistas(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        frame_layout.setSpacing(10)

        frame_layout.addWidget(LabelSeccionAzul("👥 VENTAS POR PREVENTISTA"))

        self.tabla_preventistas = QTableWidget()
        self.tabla_preventistas.setColumnCount(4)
        self.tabla_preventistas.setHorizontalHeaderLabels(["ID", "Preventista", "Facturas", "Ventas"])
        self.tabla_preventistas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_preventistas.setColumnWidth(0, 100)
        self.tabla_preventistas.setColumnWidth(2, 100)
        self.tabla_preventistas.setColumnWidth(3, 120)
        self.tabla_preventistas.setShowGrid(True)
        self.tabla_preventistas.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_preventistas.setAlternatingRowColors(True)
        self.tabla_preventistas.setMinimumHeight(420)
        frame_layout.addWidget(self.tabla_preventistas)

        layout.addWidget(frame)

        return tab

    # ==================== PESTAÑA 2: PRODUCTOS ====================
    
    def _crear_tab_productos(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        frame_layout.setSpacing(10)

        frame_layout.addWidget(LabelSeccionAzul("📦 PRODUCTOS MÁS VENDIDOS"))

        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Total Ventas"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setColumnWidth(0, 100)
        self.tabla_productos.setColumnWidth(2, 100)
        self.tabla_productos.setColumnWidth(3, 120)
        self.tabla_productos.setShowGrid(True)
        self.tabla_productos.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_productos.setAlternatingRowColors(True)
        self.tabla_productos.setMinimumHeight(420)
        frame_layout.addWidget(self.tabla_productos)

        layout.addWidget(frame)

        return tab

    # ==================== PESTAÑA 3: PEDIDOS PENDIENTES ====================
    
    def _crear_tab_pedidos_pendientes(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        frame_layout.setSpacing(10)

        # Título con contador
        self.lbl_pedidos_titulo = LabelSeccionAzul("📦 PEDIDOS PENDIENTES (0)")
        frame_layout.addWidget(self.lbl_pedidos_titulo)

        # Tabla de pedidos pendientes
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(6)
        self.tabla_pedidos.setHorizontalHeaderLabels(["ID", "Factura", "Cliente", "Fecha", "Total", "Tipo"])
        
        self.tabla_pedidos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_pedidos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_pedidos.setColumnWidth(0, 100)
        self.tabla_pedidos.setColumnWidth(1, 120)
        self.tabla_pedidos.setColumnWidth(3, 100)
        self.tabla_pedidos.setColumnWidth(4, 120)
        self.tabla_pedidos.setColumnWidth(5, 80)
        
        self.tabla_pedidos.setShowGrid(True)
        self.tabla_pedidos.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_pedidos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_pedidos.setAlternatingRowColors(True)
        self.tabla_pedidos.setMinimumHeight(400)
        frame_layout.addWidget(self.tabla_pedidos)

        layout.addWidget(frame)

        # Botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(12, 8, 12, 8)
        botones_layout.setSpacing(10)

        btn_procesar = QPushButton("📦 Procesar Pedido")
        btn_procesar.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_procesar.clicked.connect(self.procesar_pedido)

        btn_ver_detalle = QPushButton("📄 Ver Detalle")
        btn_ver_detalle.setStyleSheet("background-color: #1565C0; color: white;")
        btn_ver_detalle.clicked.connect(self.ver_detalle_pedido)

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setStyleSheet("background-color: #1565C0; color: white;")
        btn_refrescar.clicked.connect(self.cargar_pedidos)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_procesar)
        botones_layout.addWidget(btn_ver_detalle)
        botones_layout.addWidget(btn_refrescar)

        layout.addWidget(frame_botones)

        return tab

    # ==================== PESTAÑA 4: PEDIDOS ARMADOS ====================
    
    def _crear_tab_pedidos_armados(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 12, 12, 12)
        frame_layout.setSpacing(10)

        frame_layout.addWidget(LabelSeccionAzul("📜 HISTORIAL DE PEDIDOS ARMADOS"))

        # Tabla de pedidos armados
        self.tabla_armados = QTableWidget()
        self.tabla_armados.setColumnCount(7)
        self.tabla_armados.setHorizontalHeaderLabels(["ID", "Factura", "Cliente", "Fecha", "Total", "Procesado", "Observaciones"])
        
        self.tabla_armados.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_armados.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_armados.setColumnWidth(0, 100)
        self.tabla_armados.setColumnWidth(1, 120)
        self.tabla_armados.setColumnWidth(3, 100)
        self.tabla_armados.setColumnWidth(4, 120)
        self.tabla_armados.setColumnWidth(5, 150)
        self.tabla_armados.setColumnWidth(6, 150)
        
        self.tabla_armados.setShowGrid(True)
        self.tabla_armados.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_armados.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_armados.setAlternatingRowColors(True)
        self.tabla_armados.setMinimumHeight(420)
        frame_layout.addWidget(self.tabla_armados)

        layout.addWidget(frame)

        # Botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(12, 8, 12, 8)
        botones_layout.setSpacing(10)

        btn_ver_detalle = QPushButton("📄 Ver Detalle")
        btn_ver_detalle.setStyleSheet("background-color: #1565C0; color: white;")
        btn_ver_detalle.clicked.connect(self.ver_detalle_armado)

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setStyleSheet("background-color: #1565C0; color: white;")
        btn_refrescar.clicked.connect(self.cargar_armados)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_ver_detalle)
        botones_layout.addWidget(btn_refrescar)

        layout.addWidget(frame_botones)

        return tab

    # =================== FUNCIONES PRINCIPALES ===================
    
    def obtener_periodo(self):
        """Obtiene las fechas según el período seleccionado."""
        seleccion = self.cmb_periodo.currentText()
        hoy = date.today()
        
        if seleccion == "Mes Actual":
            self.fecha_desde = hoy.replace(day=1).isoformat()
            self.fecha_hasta = hoy.isoformat()
        elif seleccion == "Mes Anterior":
            primer_dia = hoy.replace(day=1)
            ultimo = primer_dia - timedelta(days=1)
            primero = ultimo.replace(day=1)
            self.fecha_desde = primero.isoformat()
            self.fecha_hasta = ultimo.isoformat()
        elif seleccion == "Año Actual":
            self.fecha_desde = hoy.replace(month=1, day=1).isoformat()
            self.fecha_hasta = hoy.isoformat()
        elif seleccion == "Año Anterior":
            self.fecha_desde = hoy.replace(year=hoy.year-1, month=1, day=1).isoformat()
            self.fecha_hasta = hoy.replace(year=hoy.year-1, month=12, day=31).isoformat()
    
    def actualizar_dashboard(self):
        """Actualiza todo el dashboard."""
        self.obtener_periodo()
        self._actualizar_metricas()
        self._actualizar_grafico()
        self._actualizar_preventistas()
        self._actualizar_productos()
        self.cargar_pedidos()
        self.cargar_armados()
        self.verificar_notas_pendientes()
    
    def _actualizar_metricas(self):
        """Actualiza las tarjetas de métricas."""
        # Limpiar grid
        for i in reversed(range(self.grid_metricas.count())):
            widget = self.grid_metricas.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        cur = self.db.cursor()
        
        # Ventas del período
        cur.execute("SELECT COALESCE(SUM(total), 0) FROM facturas WHERE fecha BETWEEN ? AND ?", 
                   (self.fecha_desde, self.fecha_hasta))
        ventas = cur.fetchone()[0]
        
        # Cantidad de facturas
        cur.execute("SELECT COUNT(*) FROM facturas WHERE fecha BETWEEN ? AND ?", 
                   (self.fecha_desde, self.fecha_hasta))
        facturas = cur.fetchone()[0]
        
        # Clientes activos
        cur.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
        clientes = cur.fetchone()[0]
        
        # Stock bajo
        cur.execute("SELECT COUNT(*) FROM productos WHERE activo = 1 AND stock_actual <= stock_critico")
        stock_bajo = cur.fetchone()[0]
        
        # Notas pendientes
        notas = len(self.nota_modelo.listar_por_estado('PENDIENTE'))
        
        # Pedidos pendientes
        pedidos_pendientes = self.controlador_ventas.contar_pedidos_pendientes()
        
        # Ticket promedio
        ticket = ventas / facturas if facturas > 0 else 0
        
        metricas = [
            ("💰 Ventas", f"${ventas:,.0f}", "#4CAF50" if ventas > 0 else "#666666"),
            ("📄 Facturas", str(facturas), "#2196F3"),
            ("👥 Clientes", str(clientes), "#1565C0"),
            ("⚠️ Stock Bajo", str(stock_bajo), "#D32F2F" if stock_bajo > 0 else "#4CAF50"),
            ("📋 Notas Pend.", str(notas), "#FF9800" if notas > 0 else "#4CAF50"),
            ("📦 Pedidos", str(pedidos_pendientes), "#FF6F00" if pedidos_pendientes > 0 else "#4CAF50"),
        ]
        
        for i, (titulo, valor, color) in enumerate(metricas):
            tarjeta = TarjetaMetrica(titulo, valor, color)
            self.grid_metricas.addWidget(tarjeta, i // 3, i % 3)
    
    def _actualizar_grafico(self):
        """Actualiza el gráfico de ventas."""
        cur = self.db.cursor()
        
        cur.execute("""
            SELECT fecha, SUM(total) as total
            FROM facturas
            WHERE fecha BETWEEN ? AND ?
            GROUP BY fecha
            ORDER BY fecha
        """, (self.fecha_desde, self.fecha_hasta))
        
        datos = cur.fetchall()
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#F8F9FA')
        
        if datos:
            fechas = [d['fecha'][5:] for d in datos]
            montos = [d['total'] for d in datos]
            
            bars = ax.bar(fechas, montos, color='#1565C0', alpha=0.8, edgecolor='#0D47A1')
            ax.set_ylabel("Ventas ($)", color='#000000', fontsize=9)
            ax.set_xlabel("Fecha", color='#000000', fontsize=9)
            ax.set_title(f"Ventas Diarias - {self.cmb_periodo.currentText()}", 
                        fontsize=11, fontweight='bold', color='#1A237E')
            ax.tick_params(axis='x', rotation=45, colors='#000000', labelsize=8)
            ax.tick_params(axis='y', colors='#000000', labelsize=8)
            ax.grid(axis='y', alpha=0.3, color='#CCCCCC')
            
            # Agregar valores en las barras
            for bar, valor in zip(bars, montos):
                if valor > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                           f'${valor:,.0f}', ha='center', va='bottom', fontsize=7, color='#000000')
        else:
            ax.text(0.5, 0.5, "Sin datos de ventas en el período", 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=11, color='#666666')
            ax.set_title("No hay datos", color='#666666', fontsize=11)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _actualizar_preventistas(self):
        """Actualiza la tabla de preventistas."""
        cur = self.db.cursor()
        
        cur.execute("""
            SELECT p.id, p.nombre || ' ' || p.apellido as preventista,
                   COUNT(f.id) as facturas,
                   COALESCE(SUM(f.total), 0) as ventas
            FROM facturas f
            JOIN preventistas p ON f.preventista_id = p.id
            WHERE f.fecha BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY ventas DESC
        """, (self.fecha_desde, self.fecha_hasta))
        
        datos = cur.fetchall()
        
        if datos:
            self.tabla_preventistas.setRowCount(len(datos))
            for i, row in enumerate(datos):
                self.tabla_preventistas.setItem(i, 0, QTableWidgetItem(row['id'][:8] + "..."))
                self.tabla_preventistas.setItem(i, 1, QTableWidgetItem(row['preventista']))
                self.tabla_preventistas.setItem(i, 2, QTableWidgetItem(str(row['facturas'])))
                item_ventas = QTableWidgetItem(f"${row['ventas']:,.2f}")
                item_ventas.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.tabla_preventistas.setItem(i, 3, item_ventas)
        else:
            self.tabla_preventistas.setRowCount(1)
            self.tabla_preventistas.setSpan(0, 0, 1, 4)
            item = QTableWidgetItem("No hay datos en el período seleccionado")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_preventistas.setItem(0, 0, item)
    
    def _actualizar_productos(self):
        """Actualiza la tabla de productos más vendidos."""
        cur = self.db.cursor()
        
        cur.execute("""
            SELECT p.id, p.descripcion as producto,
                   SUM(fd.cantidad) as cantidad,
                   COALESCE(SUM(fd.cantidad * fd.precio_unitario), 0) as total
            FROM factura_detalle fd
            JOIN facturas f ON fd.factura_id = f.id
            JOIN productos p ON fd.producto_id = p.id
            WHERE f.fecha BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY total DESC
            LIMIT 20
        """, (self.fecha_desde, self.fecha_hasta))
        
        datos = cur.fetchall()
        
        if datos:
            self.tabla_productos.setRowCount(len(datos))
            for i, row in enumerate(datos):
                self.tabla_productos.setItem(i, 0, QTableWidgetItem(row['id'][:8] + "..."))
                self.tabla_productos.setItem(i, 1, QTableWidgetItem(row['producto'][:40]))
                self.tabla_productos.setItem(i, 2, QTableWidgetItem(f"{row['cantidad']:.0f}"))
                item_total = QTableWidgetItem(f"${row['total']:,.2f}")
                item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.tabla_productos.setItem(i, 3, item_total)
        else:
            self.tabla_productos.setRowCount(1)
            self.tabla_productos.setSpan(0, 0, 1, 4)
            item = QTableWidgetItem("No hay datos en el período seleccionado")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_productos.setItem(0, 0, item)
    
    def exportar_datos(self):
        """Exporta los datos actuales a CSV."""
        from PyQt6.QtWidgets import QFileDialog
        import csv
        from datetime import datetime
        
        tab_actual = self.tabs.currentIndex()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if tab_actual == 1:  # Preventistas
            if self.tabla_preventistas.rowCount() == 0 or \
               (self.tabla_preventistas.rowCount() == 1 and 
                self.tabla_preventistas.item(0, 0).text() == "No hay datos en el período seleccionado"):
                QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar archivo", 
                f"preventistas_{self.cmb_periodo.currentText()}_{timestamp}.csv", 
                "CSV (*.csv)"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Preventista", "Facturas", "Ventas"])
                    
                    for row in range(self.tabla_preventistas.rowCount()):
                        if self.tabla_preventistas.item(row, 0).text() == "No hay datos en el período seleccionado":
                            break
                        row_data = []
                        for col in range(4):
                            item = self.tabla_preventistas.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Exportar", f"Datos exportados a:\n{filename}")
        
        elif tab_actual == 2:  # Productos
            if self.tabla_productos.rowCount() == 0 or \
               (self.tabla_productos.rowCount() == 1 and 
                self.tabla_productos.item(0, 0).text() == "No hay datos en el período seleccionado"):
                QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar archivo", 
                f"productos_{self.cmb_periodo.currentText()}_{timestamp}.csv", 
                "CSV (*.csv)"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Producto", "Cantidad", "Total Ventas"])
                    
                    for row in range(self.tabla_productos.rowCount()):
                        if self.tabla_productos.item(row, 0).text() == "No hay datos en el período seleccionado":
                            break
                        row_data = []
                        for col in range(4):
                            item = self.tabla_productos.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Exportar", f"Datos exportados a:\n{filename}")
        else:
            QMessageBox.information(self, "Exportar", "Para exportar, vaya a la pestaña de Preventistas o Productos.")

    def sincronizar_dashboard(self):
        """Sincroniza datos con Turso"""
        try:
            resultado = sincronizar_ahora(self.db)
            self.actualizar_dashboard()
            QMessageBox.information(self, "Sincronización", "✅ Datos sincronizados con Turso")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en sincronización: {e}")

    # ==================== FUNCIONES DE PEDIDOS ====================
    
    def cargar_pedidos(self):
        """Carga los pedidos pendientes (facturas no procesadas)."""
        pedidos = self.controlador_ventas.obtener_pedidos_pendientes()
        
        self.tabla_pedidos.setRowCount(len(pedidos))
        for i, p in enumerate(pedidos):
            self.tabla_pedidos.setItem(i, 0, QTableWidgetItem(p['id'][:8] + "..."))
            self.tabla_pedidos.setItem(i, 1, QTableWidgetItem(p['numero_factura']))
            self.tabla_pedidos.setItem(i, 2, QTableWidgetItem(p['cliente_nombre']))
            self.tabla_pedidos.setItem(i, 3, QTableWidgetItem(p['fecha']))
            
            item_total = QTableWidgetItem(f"${p['total']:,.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_pedidos.setItem(i, 4, item_total)
            
            self.tabla_pedidos.setItem(i, 5, QTableWidgetItem(p['tipo_comprobante']))
            
            # Guardar ID de la factura
            self.tabla_pedidos.item(i, 0).setData(Qt.ItemDataRole.UserRole, p['id'])
        
        # Actualizar contador
        cantidad = len(pedidos)
        self.lbl_pedidos_titulo.setText(f"📦 PEDIDOS PENDIENTES ({cantidad})")
        
        # Actualizar título de la solapa con contador y parpadeo
        if cantidad > 0:
            self.tabs.setTabText(3, f"📦 PENDIENTES ({cantidad})")
            self.iniciar_parpadeo_pedidos()
        else:
            self.tabs.setTabText(3, "📦 PENDIENTES")
            self.timer_parpadeo.stop()
            self.parpadeo_activo = False
            self.tabs.tabBar().setTabTextColor(3, QColor(255, 255, 255))

    # ✅ FUNCIÓN CARGAR ARMADOS CORREGIDA
    def cargar_armados(self):
        """Carga el historial de pedidos armados."""
        historial = self.controlador_ventas.obtener_historial_pedidos(100)
        
        self.tabla_armados.setRowCount(len(historial))
        for i, p in enumerate(historial):
            # ✅ CORREGIDO: Usar factura_id en lugar de id
            factura_id = p.get('factura_id', '')
            self.tabla_armados.setItem(i, 0, QTableWidgetItem(factura_id[:8] + "..."))
            self.tabla_armados.setItem(i, 1, QTableWidgetItem(p.get('numero_factura', '')))
            self.tabla_armados.setItem(i, 2, QTableWidgetItem(p.get('cliente_nombre', '')))
            self.tabla_armados.setItem(i, 3, QTableWidgetItem(p.get('fecha', '')))
            
            item_total = QTableWidgetItem(f"${p.get('total', 0):,.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_armados.setItem(i, 4, item_total)
            
            fecha_procesado = p.get('fecha_procesado', '')[:16] if p.get('fecha_procesado') else ''
            self.tabla_armados.setItem(i, 5, QTableWidgetItem(fecha_procesado))
            self.tabla_armados.setItem(i, 6, QTableWidgetItem(p.get('observaciones', '') or '-'))
            
            # Guardar factura_id en el UserRole
            self.tabla_armados.item(i, 0).setData(Qt.ItemDataRole.UserRole, factura_id)

    def _toggle_parpadeo_tab(self):
        """Alterna el color de la solapa cada 2 segundos."""
        try:
            pedidos_pendientes = self.controlador_ventas.contar_pedidos_pendientes()
            
            if pedidos_pendientes > 0:
                if self.parpadeo_activo:
                    self.tabs.tabBar().setTabTextColor(3, QColor(200, 0, 0))
                else:
                    self.tabs.tabBar().setTabTextColor(3, QColor(255, 255, 255))
                self.parpadeo_activo = not self.parpadeo_activo
            else:
                self.tabs.tabBar().setTabTextColor(3, QColor(255, 255, 255))
                self.timer_parpadeo.stop()
                self.parpadeo_activo = False
        except Exception as e:
            print(f"Error en parpadeo: {e}")

    def iniciar_parpadeo_pedidos(self):
        """Inicia el parpadeo si hay pedidos pendientes."""
        pedidos_pendientes = self.controlador_ventas.contar_pedidos_pendientes()
        if pedidos_pendientes > 0:
            self.timer_parpadeo.stop()
            self.parpadeo_activo = False
            self.tabs.tabBar().setTabTextColor(3, QColor(200, 0, 0))
            self.timer_parpadeo.start(2000)

    def procesar_pedido(self):
        """Procesa un pedido (marca como armado)."""
        fila = self.tabla_pedidos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un pedido para procesar.")
            return
        
        factura_id = self.tabla_pedidos.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_factura = self.tabla_pedidos.item(fila, 1).text()
        cliente_nombre = self.tabla_pedidos.item(fila, 2).text()
        total = self.tabla_pedidos.item(fila, 4).text()
        fecha = self.tabla_pedidos.item(fila, 3).text()
        
        confirm = QMessageBox.question(
            self, "Confirmar Procesamiento",
            f"¿Procesar pedido de {cliente_nombre} (Factura {numero_factura})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            detalles = self.controlador_ventas.obtener_detalle_pedido(factura_id)
            
            self.controlador_ventas.marcar_pedido_procesado(
                factura_id, 
                procesado_por="Usuario", 
                observaciones=f"Pedido armado manualmente"
            )
            
            self._mostrar_detalle_pedido(detalles, numero_factura, cliente_nombre, fecha, total)
            
            self.cargar_pedidos()
            self.cargar_armados()
            self.iniciar_parpadeo_pedidos()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo procesar el pedido:\n{str(e)}")

    def ver_detalle_pedido(self):
        """Muestra el detalle del pedido."""
        fila = self.tabla_pedidos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un pedido para ver el detalle.")
            return
        
        factura_id = self.tabla_pedidos.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_factura = self.tabla_pedidos.item(fila, 1).text()
        cliente_nombre = self.tabla_pedidos.item(fila, 2).text()
        total = self.tabla_pedidos.item(fila, 4).text()
        fecha = self.tabla_pedidos.item(fila, 3).text()
        
        detalles = self.controlador_ventas.obtener_detalle_pedido(factura_id)
        
        self._mostrar_detalle_pedido_sin_imprimir(detalles, numero_factura, cliente_nombre, fecha, total)

    # ✅ FUNCIÓN MOSTRAR DETALLE PEDIDO CORREGIDA
    def _mostrar_detalle_pedido_sin_imprimir(self, detalles, numero_factura, cliente_nombre, fecha, total):
        """Muestra el detalle del pedido SIN botón imprimir."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle Pedido - {numero_factura}")
        dialog.setFixedSize(800, 650)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("📦 DETALLE DE PEDIDO")
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E; text-align: center;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_titulo)
        
        lbl_factura = QLabel(f"Factura: {numero_factura}")
        lbl_factura.setStyleSheet("font-size: 14px; color: #1565C0; text-align: center;")
        lbl_factura.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_factura)
        
        frame_layout.addWidget(QLabel(" " * 50))
        
        datos = QGridLayout()
        datos.setSpacing(5)
        
        # ✅ CORREGIDO: Usar número de factura como identificador
        datos.addWidget(QLabel("<b>Factura:</b>"), 0, 0)
        datos.addWidget(QLabel(numero_factura), 0, 1)
        datos.addWidget(QLabel("<b>Cliente:</b>"), 0, 2)
        datos.addWidget(QLabel(cliente_nombre), 0, 3)
        
        datos.addWidget(QLabel("<b>Fecha:</b>"), 1, 0)
        datos.addWidget(QLabel(fecha), 1, 1)
        datos.addWidget(QLabel("<b>Total:</b>"), 1, 2)
        lbl_total = QLabel(total)
        lbl_total.setStyleSheet("font-weight: bold; color: #1A237E;")
        datos.addWidget(lbl_total, 1, 3)
        
        frame_layout.addLayout(datos)
        frame_layout.addWidget(QLabel(" " * 20))
        
        lbl_productos = QLabel("<b>PRODUCTOS</b>")
        lbl_productos.setStyleSheet("font-size: 12px; color: #1A237E;")
        frame_layout.addWidget(lbl_productos)
        
        tabla = QTableWidget()
        tabla.setColumnCount(5)
        tabla.setHorizontalHeaderLabels(["ID", "Código", "Producto", "Cantidad", "Precio"])
        tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        tabla.setColumnWidth(0, 100)
        tabla.setShowGrid(True)
        tabla.setGridStyle(Qt.PenStyle.SolidLine)
        tabla.setAlternatingRowColors(True)
        tabla.setMinimumHeight(200)
        
        tabla.setRowCount(len(detalles))
        for i, det in enumerate(detalles):
            producto_id = det.get('producto_id', '')
            tabla.setItem(i, 0, QTableWidgetItem(producto_id[:8] + "..." if producto_id else "-"))
            tabla.setItem(i, 1, QTableWidgetItem(det.get('codigo', det.get('codigo_producto', ''))))
            tabla.setItem(i, 2, QTableWidgetItem(det.get('descripcion', '')))
            item_cant = QTableWidgetItem(f"{det.get('cantidad', 0):.0f}")
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla.setItem(i, 3, item_cant)
            item_precio = QTableWidgetItem(f"${det.get('precio_unitario', 0):,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla.setItem(i, 4, item_precio)
        
        frame_layout.addWidget(tabla)
        
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

    def _mostrar_detalle_pedido(self, detalles, numero_factura, cliente_nombre, fecha, total):
        """Muestra el detalle del pedido en formato tipo factura."""
        self._mostrar_detalle_pedido_sin_imprimir(detalles, numero_factura, cliente_nombre, fecha, total)

    def ver_detalle_armado(self):
        """Muestra el detalle de un pedido armado desde el historial."""
        fila = self.tabla_armados.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un pedido para ver el detalle.")
            return
        
        factura_id = self.tabla_armados.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_factura = self.tabla_armados.item(fila, 1).text()
        cliente_nombre = self.tabla_armados.item(fila, 2).text()
        total = self.tabla_armados.item(fila, 4).text()
        fecha = self.tabla_armados.item(fila, 3).text()
        fecha_procesado = self.tabla_armados.item(fila, 5).text()
        observaciones = self.tabla_armados.item(fila, 6).text()
        
        detalles = self.controlador_ventas.obtener_detalle_pedido(factura_id)
        
        self._mostrar_detalle_armado(detalles, numero_factura, cliente_nombre, fecha, total, fecha_procesado, observaciones)

    def _mostrar_detalle_armado(self, detalles, numero_factura, cliente_nombre, fecha, total, fecha_procesado, observaciones):
        """Muestra el detalle de un pedido armado."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle Pedido Armado - {numero_factura}")
        dialog.setFixedSize(800, 650)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("📦 DETALLE DE PEDIDO ARMADO")
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E; text-align: center;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_titulo)
        
        lbl_factura = QLabel(f"Factura: {numero_factura}")
        lbl_factura.setStyleSheet("font-size: 14px; color: #1565C0; text-align: center;")
        lbl_factura.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_factura)
        
        lbl_estado = QLabel("✅ PEDIDO ARMADO")
        lbl_estado.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50; text-align: center;")
        lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_estado)
        
        frame_layout.addWidget(QLabel(" " * 50))
        
        datos = QGridLayout()
        datos.setSpacing(5)
        
        datos.addWidget(QLabel("<b>ID:</b>"), 0, 0)
        datos.addWidget(QLabel(factura_id[:8] + "..."), 0, 1)
        datos.addWidget(QLabel("<b>Cliente:</b>"), 0, 2)
        datos.addWidget(QLabel(cliente_nombre), 0, 3)
        
        datos.addWidget(QLabel("<b>Fecha:</b>"), 1, 0)
        datos.addWidget(QLabel(fecha), 1, 1)
        datos.addWidget(QLabel("<b>Total:</b>"), 1, 2)
        lbl_total = QLabel(total)
        lbl_total.setStyleSheet("font-weight: bold; color: #1A237E;")
        datos.addWidget(lbl_total, 1, 3)
        
        datos.addWidget(QLabel("<b>Armado el:</b>"), 2, 0)
        datos.addWidget(QLabel(fecha_procesado), 2, 1, 1, 3)
        
        if observaciones and observaciones != '-':
            datos.addWidget(QLabel("<b>Observaciones:</b>"), 3, 0)
            datos.addWidget(QLabel(observaciones), 3, 1, 1, 3)
        
        frame_layout.addLayout(datos)
        frame_layout.addWidget(QLabel(" " * 20))
        
        lbl_productos = QLabel("<b>PRODUCTOS</b>")
        lbl_productos.setStyleSheet("font-size: 12px; color: #1A237E;")
        frame_layout.addWidget(lbl_productos)
        
        tabla = QTableWidget()
        tabla.setColumnCount(5)
        tabla.setHorizontalHeaderLabels(["ID", "Código", "Producto", "Cantidad", "Precio"])
        tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        tabla.setColumnWidth(0, 100)
        tabla.setShowGrid(True)
        tabla.setGridStyle(Qt.PenStyle.SolidLine)
        tabla.setAlternatingRowColors(True)
        tabla.setMinimumHeight(200)
        
        tabla.setRowCount(len(detalles))
        for i, det in enumerate(detalles):
            producto_id = det.get('producto_id', '')
            tabla.setItem(i, 0, QTableWidgetItem(producto_id[:8] + "..." if producto_id else "-"))
            tabla.setItem(i, 1, QTableWidgetItem(det.get('codigo', det.get('codigo_producto', ''))))
            tabla.setItem(i, 2, QTableWidgetItem(det.get('descripcion', '')))
            item_cant = QTableWidgetItem(f"{det.get('cantidad', 0):.0f}")
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla.setItem(i, 3, item_cant)
            item_precio = QTableWidgetItem(f"${det.get('precio_unitario', 0):,.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla.setItem(i, 4, item_precio)
        
        frame_layout.addWidget(tabla)
        
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

    def verificar_notas_pendientes(self):
        """Verifica y actualiza el contador de notas pendientes en el dashboard."""
        try:
            pendientes = self.nota_modelo.listar_por_estado('PENDIENTE')
            cantidad = len(pendientes)
            
            # Actualizar el título de la solapa de pedidos
            if hasattr(self, 'lbl_pedidos_titulo'):
                self.lbl_pedidos_titulo.setText(f"📦 PEDIDOS PENDIENTES ({cantidad})")
            
            # Actualizar el título de la pestaña
            if hasattr(self, 'tabs'):
                if cantidad > 0:
                    self.tabs.setTabText(3, f"📦 PENDIENTES ({cantidad})")
                    self.iniciar_parpadeo_pedidos()
                else:
                    self.tabs.setTabText(3, "📦 PENDIENTES")
                    self.timer_parpadeo.stop()
                    self.parpadeo_activo = False
                    self.tabs.tabBar().setTabTextColor(3, QColor(255, 255, 255))
            
            return cantidad
        except Exception as e:
            print(f"⚠️ Error verificando notas pendientes: {e}")
            return 0


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaDashboard(db)
    ventana.show()
    sys.exit(app.exec())