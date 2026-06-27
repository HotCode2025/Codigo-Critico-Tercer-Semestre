"""
Código Crítico - Tercer Semestre Año 2026
Vista de Cheques – Rediseñada con solapas AZULES.
"""

import sqlite3
from datetime import date
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QFrame, QComboBox,
                               QDateEdit, QTabWidget, QWidget, QScrollArea,
                               QTextEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from modelos.cheque import Cheque
from modelos.cliente import Cliente
from controladores.controlador_cheques import ControladorCheques


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

class VistaCheques(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.ctrl_cheques = ControladorCheques(db)
        self.cliente_modelo = Cliente(db)
        self.cheque_modelo = Cheque(db)
        
        self.setWindowTitle("Gestión de Cheques")
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
        
        self.tab_cartera = self._crear_tab_cheques("cartera")
        self.tabs.addTab(self.tab_cartera, "🏦 EN CARTERA")
        
        self.tab_vendidos = self._crear_tab_cheques("vendidos")
        self.tabs.addTab(self.tab_vendidos, "💰 VENDIDOS")
        
        tarjeta_layout.addWidget(self.tabs)

        # Formulario para registrar cheque (abajo de las pestañas)
        frame_form = QFrame()
        frame_form.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        form_layout = QVBoxLayout(frame_form)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setSpacing(8)

        form_layout.addWidget(LabelSeccionAzul("REGISTRAR NUEVO CHEQUE"))

        form_grid = QGridLayout()
        form_grid.setSpacing(8)
        form_grid.setHorizontalSpacing(10)

        # Fila 1
        form_grid.addWidget(LabelCampoAzul("Cliente *"), 0, 0)
        self.cmb_cliente = ComboBlanco()
        self.cmb_cliente.setMinimumWidth(200)
        form_grid.addWidget(self.cmb_cliente, 0, 1)

        form_grid.addWidget(LabelCampoAzul("Banco *"), 0, 2)
        self.txt_banco = LineEditBlanco()
        form_grid.addWidget(self.txt_banco, 0, 3)

        # Fila 2
        form_grid.addWidget(LabelCampoAzul("N° Cheque *"), 1, 0)
        self.txt_numero_cheque = LineEditBlanco()
        form_grid.addWidget(self.txt_numero_cheque, 1, 1)

        form_grid.addWidget(LabelCampoAzul("Importe *"), 1, 2)
        self.txt_importe = LineEditBlanco()
        self.txt_importe.setPlaceholderText("0.00")
        form_grid.addWidget(self.txt_importe, 1, 3)

        # Fila 3
        form_grid.addWidget(LabelCampoAzul("F. Emisión"), 2, 0)
        self.date_emision = DateEditBlanco()
        self.date_emision.setDate(QDate.currentDate())
        form_grid.addWidget(self.date_emision, 2, 1)

        form_grid.addWidget(LabelCampoAzul("F. Vencimiento"), 2, 2)
        self.date_vencimiento = DateEditBlanco()
        self.date_vencimiento.setDate(QDate.currentDate().addMonths(1))
        form_grid.addWidget(self.date_vencimiento, 2, 3)

        # Fila 4
        form_grid.addWidget(LabelCampoAzul("Facturas Asociadas"), 3, 0)
        self.txt_facturas = LineEditBlanco()
        self.txt_facturas.setPlaceholderText("IDs separados por comas (opcional)")
        form_grid.addWidget(self.txt_facturas, 3, 1, 1, 3)

        form_layout.addLayout(form_grid)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_registrar = QPushButton("💾 Registrar Cheque")
        self.btn_limpiar = QPushButton("🧹 Limpiar")

        self.btn_registrar.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_limpiar.setStyleSheet("background-color: #1565C0; color: white;")

        self.btn_registrar.clicked.connect(self.registrar_cheque)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_registrar)
        btn_layout.addWidget(self.btn_limpiar)

        form_layout.addLayout(btn_layout)

        tarjeta_layout.addWidget(frame_form)
        layout.addWidget(tarjeta)

        # Cargar datos
        self.cargar_clientes()
        self.cargar_cheques_cartera()
        self.cargar_cheques_vendidos()

    # ==================== PESTAÑA DE CHEQUES ====================
    
    def _crear_tab_cheques(self, tipo):
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

        filtros_layout.addWidget(QLabel("Filtrar:"))
        cmb_filtro = ComboBlanco()
        if tipo == "cartera":
            cmb_filtro.addItems(["Todos", "En cartera", "Depositados", "Próximos a vencer (7 días)"])
        else:
            cmb_filtro.addItems(["Todos", "Vendidos", "Acreditados"])
        cmb_filtro.setFixedWidth(180)
        cmb_filtro.currentIndexChanged.connect(lambda: self.filtrar_cheques(tab, tipo, cmb_filtro))
        filtros_layout.addWidget(cmb_filtro)

        filtros_layout.addStretch()

        btn_consultar_bcra = QPushButton("🔍 Consultar BCRA")
        btn_consultar_bcra.setFixedWidth(120)
        btn_consultar_bcra.setStyleSheet("background-color: #FF9800; color: white; border-radius: 4px;")
        btn_consultar_bcra.clicked.connect(lambda: self.consultar_bcra(tab))
        filtros_layout.addWidget(btn_consultar_bcra)

        layout.addWidget(frame_filtros)

        # Tabla
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        tabla = QTableWidget()
        if tipo == "cartera":
            tabla.setColumnCount(8)
            tabla.setHorizontalHeaderLabels(["N° Cheque", "Cliente", "Banco", "Emisión", "Vencimiento", "Importe", "Estado", "Acciones"])
        else:
            tabla.setColumnCount(9)
            tabla.setHorizontalHeaderLabels(["N° Cheque", "Cliente", "Banco", "Emisión", "Vencimiento", "Importe", "Estado", "Vendido a", "Acciones"])
        
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setShowGrid(True)
        tabla.setGridStyle(Qt.PenStyle.SolidLine)
        tabla.setAlternatingRowColors(True)
        tabla.setMinimumHeight(200)
        tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabla_layout.addWidget(tabla)

        layout.addWidget(frame_tabla)

        # Botones de acción
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(10)

        btn_acreditar = QPushButton("✅ Acreditar")
        btn_vender = QPushButton("💰 Vender")
        btn_actualizar = QPushButton("🔄 Actualizar")

        btn_acreditar.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_vender.setStyleSheet("background-color: #FF9800; color: white;")
        btn_actualizar.setStyleSheet("background-color: #1565C0; color: white;")

        if tipo == "cartera":
            btn_acreditar.clicked.connect(lambda: self.acreditar_cheque(tab, tipo))
            btn_vender.clicked.connect(lambda: self.vender_cheque(tab, tipo))
        else:
            btn_acreditar.setEnabled(False)
            btn_vender.setEnabled(False)
            btn_acreditar.setStyleSheet("background-color: #cccccc; color: white;")
            btn_vender.setStyleSheet("background-color: #cccccc; color: white;")

        btn_actualizar.clicked.connect(lambda: self.actualizar_tab_cheques(tab, tipo))

        botones_layout.addStretch()
        botones_layout.addWidget(btn_acreditar)
        botones_layout.addWidget(btn_vender)
        botones_layout.addWidget(btn_actualizar)

        layout.addWidget(frame_botones)

        # Guardar referencias
        tab.tabla = tabla
        tab.tipo = tipo
        tab.cmb_filtro = cmb_filtro
        tab.btn_acreditar = btn_acreditar
        tab.btn_vender = btn_vender

        return tab

    # =================== FUNCIONES PRINCIPALES ===================
    
    def cargar_clientes(self):
        clientes = self.cliente_modelo.listar_todos(solo_activos=True)
        self.cmb_cliente.clear()
        for c in clientes:
            self.cmb_cliente.addItem(f"{c['razon_social']} (CUIT: {c['cuit']})", c['id'])

    def cargar_cheques_cartera(self):
        self._cargar_cheques_en_tabla(self.tab_cartera, "cartera")

    def cargar_cheques_vendidos(self):
        self._cargar_cheques_en_tabla(self.tab_vendidos, "vendidos")

    def _cargar_cheques_en_tabla(self, tab, tipo):
        filtro = tab.cmb_filtro.currentText()
        
        if tipo == "cartera":
            cheques = self.ctrl_cheques.listar_en_cartera()
            
            if filtro == "En cartera":
                cheques = [c for c in cheques if c['estado'] == 'EN_CARTERA']
            elif filtro == "Depositados":
                cheques = [c for c in cheques if c['estado'] == 'DEPOSITADO']
            elif filtro == "Próximos a vencer (7 días)":
                from datetime import datetime, timedelta
                hoy = datetime.now().date()
                limite = hoy + timedelta(days=7)
                cheques = [c for c in cheques if c['estado'] == 'EN_CARTERA' and 
                          datetime.strptime(c['fecha_vencimiento'], '%Y-%m-%d').date() <= limite]
        else:
            cheques = self.ctrl_cheques.listar_vendidos()
            
            if filtro == "Vendidos":
                cheques = [c for c in cheques if c['estado'] == 'VENDIDO']
            elif filtro == "Acreditados":
                cheques = [c for c in cheques if c['estado'] == 'ACREDITADO']
        
        tabla = tab.tabla
        tabla.setRowCount(len(cheques))
        
        for i, ch in enumerate(cheques):
            tabla.setItem(i, 0, QTableWidgetItem(ch['numero_cheque']))
            tabla.setItem(i, 1, QTableWidgetItem(ch.get('cliente_nombre', ch.get('cliente_id', ''))))
            tabla.setItem(i, 2, QTableWidgetItem(ch['banco']))
            tabla.setItem(i, 3, QTableWidgetItem(ch['fecha_emision']))
            tabla.setItem(i, 4, QTableWidgetItem(ch['fecha_vencimiento']))
            
            item_importe = QTableWidgetItem(f"${ch['importe']:,.2f}")
            item_importe.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            tabla.setItem(i, 5, item_importe)
            
            item_estado = QTableWidgetItem(ch['estado'])
            if ch['estado'] == 'EN_CARTERA':
                item_estado.setForeground(QColor('#FF9800'))
            elif ch['estado'] == 'VENDIDO':
                item_estado.setForeground(QColor('#9C27B0'))
            elif ch['estado'] == 'ACREDITADO':
                item_estado.setForeground(QColor('#4CAF50'))
            tabla.setItem(i, 6, item_estado)
            
            if tipo == "vendidos":
                tabla.setItem(i, 7, QTableWidgetItem(ch.get('vendido_a', '')))
                # Botón de acción (ícono)
                btn_ver = QPushButton("👁️ Ver")
                btn_ver.setFixedSize(50, 22)
                btn_ver.setStyleSheet("background-color: #1565C0; color: white; border-radius: 3px; font-size: 9px;")
                btn_ver.clicked.connect(lambda checked, x=ch: self.ver_detalle_cheque(x))
                tabla.setCellWidget(i, 8, btn_ver)
            else:
                btn_accion = QPushButton("✏️ Acción")
                btn_accion.setFixedSize(60, 22)
                btn_accion.setStyleSheet("background-color: #1565C0; color: white; border-radius: 3px; font-size: 9px;")
                btn_accion.clicked.connect(lambda checked, x=ch: self.mostrar_acciones_cheque(x))
                tabla.setCellWidget(i, 7, btn_accion)
            
            tabla.item(i, 0).setData(Qt.ItemDataRole.UserRole, ch['id'])

    def filtrar_cheques(self, tab, tipo, cmb_filtro):
        self._cargar_cheques_en_tabla(tab, tipo)

    def actualizar_tab_cheques(self, tab, tipo):
        if tipo == "cartera":
            self.cargar_cheques_cartera()
        else:
            self.cargar_cheques_vendidos()

    # =================== ACCIONES DE CHEQUES ===================
    
    def registrar_cheque(self):
        try:
            cliente_id = self.cmb_cliente.currentData()
            banco = self.txt_banco.text().strip()
            numero = self.txt_numero_cheque.text().strip()
            emision = self.date_emision.date().toString("yyyy-MM-dd")
            vencimiento = self.date_vencimiento.date().toString("yyyy-MM-dd")
            importe = float(self.txt_importe.text() or 0)
            facturas = self.txt_facturas.text().strip() or None

            if not cliente_id:
                raise ValueError("Seleccione un cliente.")
            if not banco:
                raise ValueError("Ingrese el banco.")
            if not numero:
                raise ValueError("Ingrese el número de cheque.")
            if importe <= 0:
                raise ValueError("El importe debe ser mayor a cero.")
            if vencimiento < emision:
                raise ValueError("La fecha de vencimiento no puede ser anterior a la fecha de emisión.")

            # Verificar si ya existe un cheque con el mismo número
            cur = self.db.cursor()
            cur.execute("SELECT id FROM cheques WHERE numero_cheque = ?", (numero,))
            if cur.fetchone():
                raise ValueError(f"Ya existe un cheque con el número {numero}.")

            self.ctrl_cheques.crear_cheque(
                cobro_id="00000000-0000-0000-0000-000000000000",
                cliente_id=cliente_id,
                banco=banco,
                numero_cheque=numero,
                fecha_emision=emision,
                fecha_vencimiento=vencimiento,
                importe=importe,
                factura_ids=facturas
            )
            
            self._mostrar_mensaje("Éxito", "Cheque registrado correctamente.")
            self.limpiar_formulario()
            self.cargar_cheques_cartera()
            
        except ValueError as e:
            self._mostrar_mensaje("Error de validación", str(e), QMessageBox.Icon.Warning)
        except Exception as e:
            self._mostrar_mensaje("Error", str(e), QMessageBox.Icon.Critical)

    def limpiar_formulario(self):
        self.cmb_cliente.setCurrentIndex(0)
        self.txt_banco.clear()
        self.txt_numero_cheque.clear()
        self.txt_importe.clear()
        self.txt_facturas.clear()
        self.date_emision.setDate(QDate.currentDate())
        self.date_vencimiento.setDate(QDate.currentDate().addMonths(1))

    def acreditar_cheque(self, tab, tipo):
        tabla = tab.tabla
        fila = tabla.currentRow()
        if fila < 0:
            self._mostrar_mensaje("Aviso", "Seleccione un cheque en la tabla.", QMessageBox.Icon.Warning)
            return
        
        cheque_id = tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_cheque = tabla.item(fila, 0).text()
        
        confirm = QMessageBox.question(self, "Confirmar", 
                                       f"¿Acreditar cheque N° {numero_cheque}?\nEsta acción no se puede deshacer.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.ctrl_cheques.acreditar(cheque_id, date.today().isoformat())
            self._mostrar_mensaje("Éxito", "Cheque marcado como acreditado.")
            self.cargar_cheques_cartera()
            self.cargar_cheques_vendidos()

    def vender_cheque(self, tab, tipo):
        from PyQt6.QtWidgets import QInputDialog
        
        tabla = tab.tabla
        fila = tabla.currentRow()
        if fila < 0:
            self._mostrar_mensaje("Aviso", "Seleccione un cheque en la tabla.", QMessageBox.Icon.Warning)
            return
        
        cheque_id = tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        numero_cheque = tabla.item(fila, 0).text()
        
        vendido_a, ok = QInputDialog.getText(self, "Vender cheque", "Nombre de la persona/entidad que compra:")
        
        if ok and vendido_a.strip():
            confirm = QMessageBox.question(self, "Confirmar", 
                                           f"¿Vender cheque N° {numero_cheque} a {vendido_a.strip()}?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.ctrl_cheques.vender(cheque_id, vendido_a.strip())
                self._mostrar_mensaje("Éxito", f"Cheque vendido a {vendido_a}.")
                self.cargar_cheques_cartera()
                self.cargar_cheques_vendidos()

    def ver_detalle_cheque(self, cheque):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle de Cheque - {cheque['numero_cheque']}")
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(10)
        
        # Título
        lbl_titulo = QLabel(f"DETALLE DE CHEQUE")
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A237E;")
        frame_layout.addWidget(lbl_titulo)
        
        # Datos
        datos = QGridLayout()
        datos.setSpacing(8)
        
        datos.addWidget(QLabel("<b>N° Cheque:</b>"), 0, 0)
        datos.addWidget(QLabel(cheque['numero_cheque']), 0, 1)
        datos.addWidget(QLabel("<b>Cliente:</b>"), 0, 2)
        datos.addWidget(QLabel(cheque.get('cliente_nombre', '')), 0, 3)
        
        datos.addWidget(QLabel("<b>Banco:</b>"), 1, 0)
        datos.addWidget(QLabel(cheque['banco']), 1, 1)
        datos.addWidget(QLabel("<b>Importe:</b>"), 1, 2)
        datos.addWidget(QLabel(f"${cheque['importe']:,.2f}"), 1, 3)
        
        datos.addWidget(QLabel("<b>F. Emisión:</b>"), 2, 0)
        datos.addWidget(QLabel(cheque['fecha_emision']), 2, 1)
        datos.addWidget(QLabel("<b>F. Vencimiento:</b>"), 2, 2)
        datos.addWidget(QLabel(cheque['fecha_vencimiento']), 2, 3)
        
        datos.addWidget(QLabel("<b>Estado:</b>"), 3, 0)
        lbl_estado = QLabel(cheque['estado'])
        if cheque['estado'] == 'EN_CARTERA':
            lbl_estado.setStyleSheet("color: #FF9800; font-weight: bold;")
        elif cheque['estado'] == 'VENDIDO':
            lbl_estado.setStyleSheet("color: #9C27B0; font-weight: bold;")
        elif cheque['estado'] == 'ACREDITADO':
            lbl_estado.setStyleSheet("color: #4CAF50; font-weight: bold;")
        datos.addWidget(lbl_estado, 3, 1)
        
        if cheque.get('vendido_a'):
            datos.addWidget(QLabel("<b>Vendido a:</b>"), 3, 2)
            datos.addWidget(QLabel(cheque['vendido_a']), 3, 3)
        
        if cheque.get('fecha_acreditacion'):
            datos.addWidget(QLabel("<b>Fecha Acreditación:</b>"), 4, 0)
            datos.addWidget(QLabel(cheque['fecha_acreditacion']), 4, 1)
        
        if cheque.get('factura_ids'):
            datos.addWidget(QLabel("<b>Facturas:</b>"), 4, 2)
            datos.addWidget(QLabel(cheque['factura_ids']), 4, 3)
        
        frame_layout.addLayout(datos)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 16px;")
        btn_cerrar.clicked.connect(dialog.accept)
        
        frame_layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(frame)
        dialog.exec()

    def mostrar_acciones_cheque(self, cheque):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Acciones - Cheque {cheque['numero_cheque']}")
        dialog.setFixedSize(400, 250)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(15)
        
        lbl_titulo = QLabel(f"Cheque N° {cheque['numero_cheque']}")
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A237E;")
        frame_layout.addWidget(lbl_titulo)
        
        lbl_info = QLabel(f"Cliente: {cheque.get('cliente_nombre', '')}<br>Importe: ${cheque['importe']:,.2f}<br>Vencimiento: {cheque['fecha_vencimiento']}")
        lbl_info.setStyleSheet("font-size: 11px;")
        frame_layout.addWidget(lbl_info)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_acreditar = QPushButton("✅ Acreditar")
        btn_acreditar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 8px 12px;")
        btn_acreditar.clicked.connect(lambda: self._acreditar_desde_dialogo(cheque['id'], cheque['numero_cheque'], dialog))
        
        btn_vender = QPushButton("💰 Vender")
        btn_vender.setStyleSheet("background-color: #FF9800; color: white; border-radius: 4px; padding: 8px 12px;")
        btn_vender.clicked.connect(lambda: self._vender_desde_dialogo(cheque['id'], cheque['numero_cheque'], dialog))
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 12px;")
        btn_cerrar.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(btn_acreditar)
        btn_layout.addWidget(btn_vender)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        
        frame_layout.addLayout(btn_layout)
        layout.addWidget(frame)
        dialog.exec()

    def _acreditar_desde_dialogo(self, cheque_id, numero_cheque, dialog):
        confirm = QMessageBox.question(self, "Confirmar", 
                                       f"¿Acreditar cheque N° {numero_cheque}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.ctrl_cheques.acreditar(cheque_id, date.today().isoformat())
            self._mostrar_mensaje("Éxito", "Cheque marcado como acreditado.")
            dialog.accept()
            self.cargar_cheques_cartera()
            self.cargar_cheques_vendidos()

    def _vender_desde_dialogo(self, cheque_id, numero_cheque, dialog):
        from PyQt6.QtWidgets import QInputDialog
        vendido_a, ok = QInputDialog.getText(self, "Vender cheque", "Nombre de la persona/entidad que compra:")
        if ok and vendido_a.strip():
            confirm = QMessageBox.question(self, "Confirmar", 
                                           f"¿Vender cheque N° {numero_cheque} a {vendido_a.strip()}?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.ctrl_cheques.vender(cheque_id, vendido_a.strip())
                self._mostrar_mensaje("Éxito", f"Cheque vendido a {vendido_a}.")
                dialog.accept()
                self.cargar_cheques_cartera()
                self.cargar_cheques_vendidos()

    def consultar_bcra(self, tab):
        tabla = tab.tabla
        fila = tabla.currentRow()
        if fila < 0:
            self._mostrar_mensaje("Aviso", "Seleccione un cheque para consultar en el BCRA.", QMessageBox.Icon.Warning)
            return
        
        numero_cheque = tabla.item(fila, 0).text()
        banco = tabla.item(fila, 2).text()
        
        self._mostrar_mensaje("Consulta BCRA", 
                              f"Consultando cheque N° {numero_cheque} del banco {banco}...\n\n"
                              f"Esta funcionalidad requiere conexión con la API del BCRA.\n"
                              f"Por ahora, se muestra un mensaje informativo.\n\n"
                              f"En producción, aquí se mostraría si el cheque fue denunciado.",
                              QMessageBox.Icon.Information)

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
    ventana = VistaCheques(db)
    ventana.show()
    sys.exit(app.exec())