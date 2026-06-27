"""
Código Crítico - Tercer Semestre Año 2026
Vista de Rentabilidad - Ganancias, gastos y proyecciones.
Con solapas AZULES.
"""

import sqlite3
from datetime import date, timedelta
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QHeaderView,
                               QFrame, QComboBox, QDateEdit, QTabWidget,
                               QWidget, QScrollArea, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controladores.controlador_rentabilidad import ControladorRentabilidad


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


class DoubleSpinBoxBlanco(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 1000000)
        self.setDecimals(2)
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
        """)


class SpinBoxBlanco(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(1, 24)
        self.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
        """)


# ==================== VISTA PRINCIPAL ====================

class VistaRentabilidad(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.ctrl = ControladorRentabilidad(db)
        
        self.setWindowTitle("Rentabilidad - Ganancias y Proyecciones")
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

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        self.tab_resumen = self._crear_tab_resumen()
        self.tabs.addTab(self.tab_resumen, "📊 RESUMEN")
        
        self.tab_gastos = self._crear_tab_gastos()
        self.tabs.addTab(self.tab_gastos, "💸 GASTOS")
        
        self.tab_proyecciones = self._crear_tab_proyecciones()
        self.tabs.addTab(self.tab_proyecciones, "📈 PROYECCIONES")
        
        tarjeta_layout.addWidget(self.tabs)
        layout.addWidget(tarjeta)

        # Cargar datos
        self.cargar_resumen()
        self.cargar_tabla_gastos()
        self.cargar_proyecciones()

    # ==================== PESTAÑA 1: RESUMEN ====================
    
    def _crear_tab_resumen(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Filtro de período
        frame_filtro = QFrame()
        frame_filtro.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtro_layout = QHBoxLayout(frame_filtro)
        filtro_layout.setContentsMargins(8, 6, 8, 6)
        filtro_layout.setSpacing(8)

        filtro_layout.addWidget(QLabel("Período:"))
        self.cmb_periodo = ComboBlanco()
        self.cmb_periodo.addItems(["Mes Actual", "Mes Anterior", "Año Actual", "Personalizado"])
        self.cmb_periodo.setFixedWidth(120)
        self.cmb_periodo.currentIndexChanged.connect(self.on_periodo_changed)
        filtro_layout.addWidget(self.cmb_periodo)

        self.fecha_desde = DateEditBlanco()
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_hasta = DateEditBlanco()
        self.fecha_hasta.setDate(QDate.currentDate())

        filtro_layout.addWidget(QLabel("Desde:"))
        filtro_layout.addWidget(self.fecha_desde)
        filtro_layout.addWidget(QLabel("Hasta:"))
        filtro_layout.addWidget(self.fecha_hasta)

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setFixedWidth(80)
        btn_actualizar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px;")
        btn_actualizar.clicked.connect(self.cargar_resumen)
        filtro_layout.addWidget(btn_actualizar)

        layout.addWidget(frame_filtro)

        # Tarjetas de métricas
        frame_metricas = QFrame()
        frame_metricas.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        metricas_layout = QGridLayout(frame_metricas)
        metricas_layout.setContentsMargins(10, 10, 10, 10)
        metricas_layout.setSpacing(12)

        self.lbl_ventas = QLabel("Ventas: $0")
        self.lbl_ganancia_bruta = QLabel("Ganancia Bruta: $0")
        self.lbl_gastos = QLabel("Gastos: $0")
        self.lbl_ganancia_neta = QLabel("Ganancia Neta: $0")
        self.lbl_margen = QLabel("Margen Neto: 0%")

        estilo_metricas = "font-size: 13px; font-weight: bold; padding: 10px; background-color: #F8F9FA; border-radius: 6px;"
        self.lbl_ventas.setStyleSheet(estilo_metricas + "color: #2196F3;")
        self.lbl_ganancia_bruta.setStyleSheet(estilo_metricas + "color: #4CAF50;")
        self.lbl_gastos.setStyleSheet(estilo_metricas + "color: #D32F2F;")
        self.lbl_ganancia_neta.setStyleSheet(estilo_metricas + "color: #FF9800;")
        self.lbl_margen.setStyleSheet(estilo_metricas + "color: #9C27B0;")

        metricas_layout.addWidget(self.lbl_ventas, 0, 0)
        metricas_layout.addWidget(self.lbl_ganancia_bruta, 0, 1)
        metricas_layout.addWidget(self.lbl_gastos, 1, 0)
        metricas_layout.addWidget(self.lbl_ganancia_neta, 1, 1)
        metricas_layout.addWidget(self.lbl_margen, 0, 2, 2, 1)

        layout.addWidget(frame_metricas)

        # Gráfico de ganancia mensual
        frame_grafico = QFrame()
        frame_grafico.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        grafico_layout = QVBoxLayout(frame_grafico)
        grafico_layout.setContentsMargins(10, 10, 10, 10)

        grafico_layout.addWidget(LabelSeccionAzul("GANANCIA MENSUAL"))

        self.figure = Figure(figsize=(7, 2.5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(200)
        grafico_layout.addWidget(self.canvas)

        layout.addWidget(frame_grafico)

        return tab

    def on_periodo_changed(self):
        es_personalizado = self.cmb_periodo.currentText() == "Personalizado"
        self.fecha_desde.setEnabled(es_personalizado)
        self.fecha_hasta.setEnabled(es_personalizado)
        
        if not es_personalizado:
            hoy = QDate.currentDate()
            periodo = self.cmb_periodo.currentText()
            if periodo == "Mes Actual":
                self.fecha_desde.setDate(QDate(hoy.year(), hoy.month(), 1))
                self.fecha_hasta.setDate(hoy)
            elif periodo == "Mes Anterior":
                fecha_anterior = hoy.addMonths(-1)
                self.fecha_desde.setDate(QDate(fecha_anterior.year(), fecha_anterior.month(), 1))
                self.fecha_hasta.setDate(QDate(fecha_anterior.year(), fecha_anterior.month(), 
                                               fecha_anterior.daysInMonth()))
            elif periodo == "Año Actual":
                self.fecha_desde.setDate(QDate(hoy.year(), 1, 1))
                self.fecha_hasta.setDate(hoy)
            self.cargar_resumen()

    def cargar_resumen(self):
        desde = self.fecha_desde.date().toString("yyyy-MM-dd")
        hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")
        
        data = self.ctrl.obtener_ganancia_por_periodo(desde, hasta)
        
        self.lbl_ventas.setText(f"💰 Ventas: ${data['ventas_totales']:,.2f}")
        self.lbl_ganancia_bruta.setText(f"📈 Ganancia Bruta: ${data['ganancia_bruta']:,.2f}")
        self.lbl_gastos.setText(f"💸 Gastos: ${data['total_gastos']:,.2f}")
        self.lbl_ganancia_neta.setText(f"🎯 Ganancia Neta: ${data['ganancia_neta']:,.2f}")
        self.lbl_margen.setText(f"📊 Margen Neto: {data['margen_neto']:.1f}%")
        
        # Colores según valor
        if data['ganancia_neta'] >= 0:
            self.lbl_ganancia_neta.setStyleSheet(self.lbl_ganancia_neta.styleSheet() + "color: #4CAF50;")
        else:
            self.lbl_ganancia_neta.setStyleSheet(self.lbl_ganancia_neta.styleSheet() + "color: #D32F2F;")
        
        # Gráfico mensual
        self._actualizar_grafico_mensual()

    def _actualizar_grafico_mensual(self):
        resultados = self.ctrl.obtener_ganancia_mensual()
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        meses = [r['nombre_mes'][:3] for r in resultados]
        ganancias = [r['ganancia_neta'] for r in resultados]
        
        colors = ['#4CAF50' if g >= 0 else '#D32F2F' for g in ganancias]
        bars = ax.bar(meses, ganancias, color=colors, alpha=0.8)
        
        ax.axhline(y=0, color='black', linewidth=0.5)
        ax.set_ylabel("Ganancia Neta ($)", fontsize=9)
        ax.set_xlabel("Mes", fontsize=9)
        ax.set_title("Ganancia Neta por Mes", fontsize=11, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        
        for bar, valor in zip(bars, ganancias):
            if valor != 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (100 if valor >= 0 else -200),
                       f'${valor:,.0f}', ha='center', va='bottom' if valor >= 0 else 'top', fontsize=7)
        
        self.figure.tight_layout()
        self.canvas.draw()

    # ==================== PESTAÑA 2: GASTOS ====================
    
    def _crear_tab_gastos(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Formulario de gastos
        frame_form = QFrame()
        frame_form.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        form_layout = QGridLayout(frame_form)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(8)

        form_layout.addWidget(LabelCampoAzul("Fecha *"), 0, 0)
        self.gasto_fecha = DateEditBlanco()
        form_layout.addWidget(self.gasto_fecha, 0, 1)

        form_layout.addWidget(LabelCampoAzul("Categoría *"), 0, 2)
        self.gasto_categoria = ComboBlanco()
        self.gasto_categoria.addItems(["Alquiler", "Sueldos", "Servicios", "Impuestos", "Mantenimiento", "Publicidad", "Logística", "Otros"])
        form_layout.addWidget(self.gasto_categoria, 0, 3)

        form_layout.addWidget(LabelCampoAzul("Descripción"), 1, 0)
        self.gasto_descripcion = LineEditBlanco()
        form_layout.addWidget(self.gasto_descripcion, 1, 1, 1, 3)

        form_layout.addWidget(LabelCampoAzul("Importe *"), 2, 0)
        self.gasto_importe = DoubleSpinBoxBlanco()
        self.gasto_importe.setPrefix("$ ")
        form_layout.addWidget(self.gasto_importe, 2, 1)

        form_layout.addWidget(LabelCampoAzul("Tipo"), 2, 2)
        self.gasto_tipo = ComboBlanco()
        self.gasto_tipo.addItems(["OPERATIVO", "ADMINISTRATIVO", "EXTRAORDINARIO"])
        form_layout.addWidget(self.gasto_tipo, 2, 3)

        btn_agregar = QPushButton("➕ Agregar Gasto")
        btn_agregar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 6px;")
        btn_agregar.clicked.connect(self.agregar_gasto)
        form_layout.addWidget(btn_agregar, 3, 0, 1, 4)

        layout.addWidget(frame_form)

        # Tabla de gastos
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setColumnCount(6)
        self.tabla_gastos.setHorizontalHeaderLabels(["ID", "Fecha", "Categoría", "Descripción", "Importe", "Acciones"])
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_gastos.setShowGrid(True)
        self.tabla_gastos.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_gastos.setAlternatingRowColors(True)
        self.tabla_gastos.setMinimumHeight(250)
        tabla_layout.addWidget(self.tabla_gastos)

        layout.addWidget(frame_tabla)

        return tab

    def agregar_gasto(self):
        fecha = self.gasto_fecha.date().toString("yyyy-MM-dd")
        categoria = self.gasto_categoria.currentText()
        importe = self.gasto_importe.value()
        descripcion = self.gasto_descripcion.text().strip()
        tipo = self.gasto_tipo.currentText()

        if importe <= 0:
            QMessageBox.warning(self, "Error", "El importe debe ser mayor a cero.")
            return

        try:
            self.ctrl.agregar_gasto(fecha, categoria, importe, descripcion or None, tipo)
            self.limpiar_form_gasto()
            self.cargar_tabla_gastos()
            self.cargar_resumen()
            QMessageBox.information(self, "Éxito", "Gasto agregado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def limpiar_form_gasto(self):
        self.gasto_fecha.setDate(QDate.currentDate())
        self.gasto_categoria.setCurrentIndex(0)
        self.gasto_descripcion.clear()
        self.gasto_importe.setValue(0)
        self.gasto_tipo.setCurrentIndex(0)

    def cargar_tabla_gastos(self):
        desde = "2000-01-01"
        hasta = "2099-12-31"
        gastos = self.ctrl.obtener_gastos_por_periodo(desde, hasta)
        
        self.tabla_gastos.setRowCount(len(gastos))
        
        for i, g in enumerate(gastos):
            self.tabla_gastos.setItem(i, 0, QTableWidgetItem(str(g['id'])))
            self.tabla_gastos.setItem(i, 1, QTableWidgetItem(g['fecha']))
            self.tabla_gastos.setItem(i, 2, QTableWidgetItem(g['categoria']))
            self.tabla_gastos.setItem(i, 3, QTableWidgetItem(g.get('descripcion', '-')[:40]))
            item_importe = QTableWidgetItem(f"${g['importe']:,.2f}")
            item_importe.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_gastos.setItem(i, 4, item_importe)
            
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setFixedSize(30, 22)
            btn_eliminar.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 3px;")
            btn_eliminar.clicked.connect(lambda checked, x=g['id']: self.eliminar_gasto(x))
            self.tabla_gastos.setCellWidget(i, 5, btn_eliminar)
            
            self.tabla_gastos.item(i, 0).setData(Qt.ItemDataRole.UserRole, g['id'])

    def eliminar_gasto(self, gasto_id):
        confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar este gasto?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if self.ctrl.eliminar_gasto(gasto_id):
                self.cargar_tabla_gastos()
                self.cargar_resumen()
                QMessageBox.information(self, "Éxito", "Gasto eliminado.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el gasto.")

    # ==================== PESTAÑA 3: PROYECCIONES ====================
    
    def _crear_tab_proyecciones(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Configuración
        frame_config = QFrame()
        frame_config.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        config_layout = QHBoxLayout(frame_config)
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(10)

        config_layout.addWidget(LabelCampoAzul("Crecimiento mensual:"))
        self.spin_crecimiento = DoubleSpinBoxBlanco()
        self.spin_crecimiento.setRange(0, 50)
        self.spin_crecimiento.setSuffix("%")
        self.spin_crecimiento.setValue(5.0)
        config_layout.addWidget(self.spin_crecimiento)

        config_layout.addWidget(LabelCampoAzul("Meses a proyectar:"))
        self.spin_meses = SpinBoxBlanco()
        self.spin_meses.setRange(1, 24)
        self.spin_meses.setValue(6)
        config_layout.addWidget(self.spin_meses)

        btn_guardar_config = QPushButton("💾 Guardar Configuración")
        btn_guardar_config.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px;")
        btn_guardar_config.clicked.connect(self.guardar_config_proyecciones)
        config_layout.addWidget(btn_guardar_config)

        layout.addWidget(frame_config)

        # Tabla de proyecciones
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(10, 10, 10, 10)

        tabla_layout.addWidget(LabelSeccionAzul("📈 PROYECCIÓN DE GANANCIAS"))

        self.tabla_proyecciones = QTableWidget()
        self.tabla_proyecciones.setColumnCount(3)
        self.tabla_proyecciones.setHorizontalHeaderLabels(["Mes", "Proyección", "Crecimiento"])
        self.tabla_proyecciones.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_proyecciones.setShowGrid(True)
        self.tabla_proyecciones.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_proyecciones.setAlternatingRowColors(True)
        self.tabla_proyecciones.setMinimumHeight(350)
        tabla_layout.addWidget(self.tabla_proyecciones)

        layout.addWidget(frame_tabla)

        # Gráfico de proyección
        frame_grafico = QFrame()
        frame_grafico.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        grafico_layout = QVBoxLayout(frame_grafico)
        grafico_layout.setContentsMargins(10, 10, 10, 10)

        self.figure_proy = Figure(figsize=(7, 2), tight_layout=True)
        self.canvas_proy = FigureCanvas(self.figure_proy)
        self.canvas_proy.setMinimumHeight(150)
        grafico_layout.addWidget(self.canvas_proy)

        layout.addWidget(frame_grafico)

        return tab

    def guardar_config_proyecciones(self):
        crecimiento = self.spin_crecimiento.value()
        meses = self.spin_meses.value()
        
        self.ctrl.actualizar_config_proyecciones(crecimiento, meses)
        self.cargar_proyecciones()
        QMessageBox.information(self, "Éxito", "Configuración guardada.")

    def cargar_proyecciones(self):
        config = self.ctrl.obtener_config_proyecciones()
        self.spin_crecimiento.setValue(config['porcentaje_crecimiento_mensual'])
        self.spin_meses.setValue(config['meses_proyeccion'])
        
        data = self.ctrl.obtener_proyeccion()
        proyecciones = data['proyecciones']
        
        self.tabla_proyecciones.setRowCount(len(proyecciones))
        
        for i, p in enumerate(proyecciones):
            self.tabla_proyecciones.setItem(i, 0, QTableWidgetItem(p['mes']))
            item_proy = QTableWidgetItem(f"${p['proyeccion']:,.2f}")
            item_proy.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tabla_proyecciones.setItem(i, 1, item_proy)
            self.tabla_proyecciones.setItem(i, 2, QTableWidgetItem(f"+{p['crecimiento_aplicado']:.1f}%"))
        
        self._actualizar_grafico_proyecciones(proyecciones)

    def _actualizar_grafico_proyecciones(self, proyecciones):
        self.figure_proy.clear()
        ax = self.figure_proy.add_subplot(111)
        
        meses = [p['mes'] for p in proyecciones]
        valores = [p['proyeccion'] for p in proyecciones]
        
        ax.plot(meses, valores, marker='o', linewidth=2, color='#1565C0', markersize=8)
        ax.fill_between(range(len(meses)), valores, alpha=0.3, color='#1565C0')
        ax.set_ylabel("Ganancia Proyectada ($)", fontsize=9)
        ax.set_xlabel("Mes", fontsize=9)
        ax.set_title("Tendencia de Ganancias", fontsize=11, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.grid(True, alpha=0.3)
        
        for i, (mes, valor) in enumerate(zip(meses, valores)):
            ax.annotate(f'${valor:,.0f}', (i, valor), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=7)
        
        self.figure_proy.tight_layout()
        self.canvas_proy.draw()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaRentabilidad(db)
    ventana.show()
    sys.exit(app.exec())