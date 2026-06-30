"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 9.1: Vista de Clientes con UUID
==================================================
📌 USO: Gestión de clientes con UUID
📌 CARACTERÍSTICAS:
    - CRUD completo con UUID
    - Geolocalización automática
    - Exportación a CSV
"""

import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QWidget, QComboBox, QCheckBox,
                               QApplication, QFrame, QLabel, QLineEdit,
                               QPushButton, QFileDialog, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

from modelos.cliente import Cliente
from modelos.preventista import Preventista
from utilidades.geocodificar import obtener_coordenadas
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

class LabelCampoAzul(QLabel):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setFixedWidth(90)
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

class LineEditCUIT(LineEditBlanco):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("99-99999999-9")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaxLength(13)


# ==================== HILO DE GEOLOCALIZACIÓN ====================

class GeocodingThread(QThread):
    finished = pyqtSignal(object, object)
    
    def __init__(self, calle, numero, localidad, provincia):
        super().__init__()
        self.calle = calle
        self.numero = numero
        self.localidad = localidad
        self.provincia = provincia
    
    def run(self):
        lat, lon = obtener_coordenadas(self.calle, self.numero, self.localidad, self.provincia)
        self.finished.emit(lat, lon)


# ==================== VISTA PRINCIPAL ====================

class VistaClientes(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.cliente_modelo = Cliente(db)
        self.preventista_modelo = Preventista(db)
        
        self.setWindowTitle("Gestión de Clientes")
        self.setFixedSize(950, 700)

        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
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
            QFrame {
                background-color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
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
            QSplitter::handle {
                background-color: #B0BEC5;
                height: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(10, 10, 10, 10)
        tarjeta_layout.setSpacing(8)

        # ========== TÍTULO ==========
        tarjeta_layout.addWidget(LabelSeccionAzul("🏢 GESTIÓN DE CLIENTES"))

        # ========== BUSCADOR ==========
        frame_buscador = QFrame()
        frame_buscador.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        buscador_layout = QHBoxLayout(frame_buscador)
        buscador_layout.setContentsMargins(10, 8, 10, 8)
        buscador_layout.setSpacing(10)

        buscador_layout.addWidget(QLabel("🔍 Buscar:"))
        self.txt_buscar = LineEditBlanco()
        self.txt_buscar.setPlaceholderText("Razón Social o CUIT...")
        self.txt_buscar.setMinimumWidth(300)
        self.txt_buscar.returnPressed.connect(self.cargar_tabla_clientes)
        buscador_layout.addWidget(self.txt_buscar)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedWidth(80)
        btn_buscar.clicked.connect(self.cargar_tabla_clientes)
        buscador_layout.addWidget(btn_buscar)

        btn_limpiar_busqueda = QPushButton("Limpiar")
        btn_limpiar_busqueda.setFixedWidth(80)
        btn_limpiar_busqueda.setStyleSheet("background-color: #FF9800;")
        btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)
        buscador_layout.addWidget(btn_limpiar_busqueda)

        btn_exportar = QPushButton("📎 Exportar CSV")
        btn_exportar.setFixedWidth(110)
        btn_exportar.setStyleSheet("background-color: #4CAF50;")
        btn_exportar.clicked.connect(self.exportar_csv)
        buscador_layout.addWidget(btn_exportar)

        tarjeta_layout.addWidget(frame_buscador)

        # ========== SPLITTER ==========
        splitter = QSplitter(Qt.Orientation.Vertical)

        # ----- TABLA DE CLIENTES -----
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Razón Social", "CUIT", "Localidad", "Teléfono", "Preventista"])
        
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        
        self.tabla.setColumnWidth(0, 250)  # UUID más ancho
        self.tabla.setColumnWidth(2, 120)
        self.tabla.setColumnWidth(3, 150)
        self.tabla.setColumnWidth(4, 120)
        self.tabla.setColumnWidth(5, 120)
        
        self.tabla.setShowGrid(True)
        self.tabla.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setMinimumHeight(180)
        self.tabla.setMaximumHeight(240)
        self.tabla.doubleClicked.connect(self.seleccionar_cliente_desde_tabla)
        self.tabla.selectionModel().selectionChanged.connect(self.seleccionar_cliente_desde_tabla)
        tabla_layout.addWidget(self.tabla)

        splitter.addWidget(frame_tabla)

        # ----- FORMULARIO -----
        frame_formulario = QFrame()
        frame_formulario.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        form_layout = QVBoxLayout(frame_formulario)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(8)

        form_layout.addWidget(LabelSeccionAzul("📋 DATOS DEL CLIENTE"))

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setHorizontalSpacing(10)

        # FILA 1: Razón Social + CUIT
        grid.addWidget(LabelCampoAzul("Razón Social *"), 0, 0)
        self.txt_razon_social = LineEditBlanco()
        self.txt_razon_social.setMinimumWidth(200)
        grid.addWidget(self.txt_razon_social, 0, 1)
        
        grid.addWidget(LabelCampoAzul("CUIT *"), 0, 2)
        self.txt_cuit = LineEditCUIT()
        grid.addWidget(self.txt_cuit, 0, 3)

        # FILA 2: Condición IVA + Teléfono
        grid.addWidget(LabelCampoAzul("Condición IVA"), 1, 0)
        self.cmb_iva = ComboBlanco()
        self.cmb_iva.addItems(["RI", "M", "EX", "CF"])
        grid.addWidget(self.cmb_iva, 1, 1)
        
        grid.addWidget(LabelCampoAzul("Teléfono *"), 1, 2)
        self.txt_telefono = LineEditBlanco()
        self.txt_telefono.setMaxLength(20)
        grid.addWidget(self.txt_telefono, 1, 3)

        # FILA 3: Email + WhatsApp
        grid.addWidget(LabelCampoAzul("Email *"), 2, 0)
        self.txt_email = LineEditBlanco()
        self.txt_email.setMaxLength(100)
        grid.addWidget(self.txt_email, 2, 1)
        
        grid.addWidget(LabelCampoAzul("WhatsApp"), 2, 2)
        self.txt_whatsapp = LineEditBlanco()
        self.txt_whatsapp.setMaxLength(20)
        grid.addWidget(self.txt_whatsapp, 2, 3)

        # FILA 4: Calle + Número
        grid.addWidget(LabelCampoAzul("Calle *"), 3, 0)
        self.txt_calle = LineEditBlanco()
        self.txt_calle.setMaxLength(100)
        grid.addWidget(self.txt_calle, 3, 1)
        
        grid.addWidget(LabelCampoAzul("Número *"), 3, 2)
        self.txt_numero = LineEditBlanco()
        self.txt_numero.setMaxLength(10)
        grid.addWidget(self.txt_numero, 3, 3)

        # FILA 5: Localidad + Provincia
        grid.addWidget(LabelCampoAzul("Localidad *"), 4, 0)
        self.txt_localidad = LineEditBlanco()
        self.txt_localidad.setMaxLength(100)
        grid.addWidget(self.txt_localidad, 4, 1)
        
        grid.addWidget(LabelCampoAzul("Provincia *"), 4, 2)
        self.txt_provincia = LineEditBlanco()
        self.txt_provincia.setMaxLength(100)
        grid.addWidget(self.txt_provincia, 4, 3)

        # FILA 6: Preventista + Límite crédito
        grid.addWidget(LabelCampoAzul("Preventista"), 5, 0)
        self.cmb_preventista = ComboBlanco()
        grid.addWidget(self.cmb_preventista, 5, 1)
        
        grid.addWidget(LabelCampoAzul("Límite crédito"), 5, 2)
        self.txt_limite = LineEditBlanco()
        self.txt_limite.setPlaceholderText("0.00")
        self.txt_limite.setMaxLength(15)
        grid.addWidget(self.txt_limite, 5, 3)

        # FILA 7: Tasa municipal
        self.chk_tasa = CheckBoxBlanco("Aplica tasa municipal")
        grid.addWidget(self.chk_tasa, 6, 0, 1, 2)

        # FILA 8: Latitud + Longitud
        grid.addWidget(LabelCampoAzul("Latitud"), 7, 0)
        self.txt_latitud = LineEditBlanco()
        self.txt_latitud.setReadOnly(True)
        self.txt_latitud.setStyleSheet("""
            QLineEdit {
                background-color: #F5F5F5;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #666666;
            }
        """)
        grid.addWidget(self.txt_latitud, 7, 1)
        
        grid.addWidget(LabelCampoAzul("Longitud"), 7, 2)
        self.txt_longitud = LineEditBlanco()
        self.txt_longitud.setReadOnly(True)
        self.txt_longitud.setStyleSheet("""
            QLineEdit {
                background-color: #F5F5F5;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #666666;
            }
        """)
        grid.addWidget(self.txt_longitud, 7, 3)

        form_layout.addLayout(grid)

        # ========== BOTONES CRUD ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_nuevo = QPushButton("➕ Nuevo")
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_modificar = QPushButton("✏️ Modificar")
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_limpiar = QPushButton("🧹 Limpiar")
        self.btn_sincronizar = QPushButton("🔄 Sincronizar")

        self.btn_eliminar.setStyleSheet("background-color: #D32F2F;")
        self.btn_sincronizar.setStyleSheet("background-color: #4CAF50;")

        for btn in [self.btn_nuevo, self.btn_guardar, self.btn_modificar, 
                    self.btn_eliminar, self.btn_limpiar, self.btn_sincronizar]:
            btn.setMinimumHeight(32)
            btn.setMinimumWidth(90)

        btn_layout.addWidget(self.btn_nuevo)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_modificar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_limpiar)
        btn_layout.addWidget(self.btn_sincronizar)
        btn_layout.addStretch()

        form_layout.addLayout(btn_layout)

        splitter.addWidget(frame_formulario)
        splitter.setSizes([240, 380])

        tarjeta_layout.addWidget(splitter)
        layout.addWidget(tarjeta)

        # ========== CONEXIONES ==========
        self.btn_nuevo.clicked.connect(self.limpiar_formulario)
        self.btn_guardar.clicked.connect(self.guardar_cliente)
        self.btn_modificar.clicked.connect(self.modificar_cliente)
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_sincronizar.clicked.connect(self.sincronizar_clientes)

        self.txt_calle.editingFinished.connect(self.geolocalizar_auto)
        self.txt_numero.editingFinished.connect(self.geolocalizar_auto)
        self.txt_localidad.editingFinished.connect(self.geolocalizar_auto)
        self.txt_provincia.editingFinished.connect(self.geolocalizar_auto)

        self._cargar_preventistas()
        self.cargar_tabla_clientes()

        self.cliente_seleccionado_id = None
        self.geo_thread = None

    def _cargar_preventistas(self):
        """Carga preventistas en el combo (con UUID)"""
        self.cmb_preventista.clear()
        self.cmb_preventista.addItem("-- Seleccionar --", None)
        preventistas = self.preventista_modelo.listar_todos(solo_activos=True)
        for p in preventistas:
            self.cmb_preventista.addItem(f"{p['apellido']}, {p['nombre']}", p['id'])

    def cargar_tabla_clientes(self):
        """Carga la tabla de clientes"""
        busqueda = self.txt_buscar.text().strip()
        cur = self.db.cursor()
        
        if busqueda:
            cur.execute("""
                SELECT c.id, c.razon_social, c.cuit, c.localidad, c.telefono,
                       p.nombre || ' ' || p.apellido as preventista_nombre
                FROM clientes c
                LEFT JOIN preventistas p ON c.preventista_id = p.id
                WHERE (c.razon_social LIKE ? OR c.cuit LIKE ?) AND c.activo = 1
                ORDER BY c.razon_social
                LIMIT 100
            """, (f"%{busqueda}%", f"%{busqueda}%"))
        else:
            cur.execute("""
                SELECT c.id, c.razon_social, c.cuit, c.localidad, c.telefono,
                       p.nombre || ' ' || p.apellido as preventista_nombre
                FROM clientes c
                LEFT JOIN preventistas p ON c.preventista_id = p.id
                WHERE c.activo = 1
                ORDER BY c.razon_social
                LIMIT 100
            """)
        
        registros = [dict(row) for row in cur.fetchall()]
        self.tabla.setRowCount(len(registros))
        
        for fila, c in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(c["id"][:8] + "..."))
            self.tabla.setItem(fila, 1, QTableWidgetItem(c["razon_social"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(c["cuit"] or ""))
            self.tabla.setItem(fila, 3, QTableWidgetItem(c.get("localidad") or ""))
            self.tabla.setItem(fila, 4, QTableWidgetItem(c.get("telefono") or ""))
            self.tabla.setItem(fila, 5, QTableWidgetItem(c.get("preventista_nombre") or "-"))
            self.tabla.item(fila, 0).setData(Qt.ItemDataRole.UserRole, c["id"])

    def seleccionar_cliente_desde_tabla(self):
        """Carga los datos del cliente seleccionado en el formulario"""
        indices = self.tabla.selectedItems()
        if not indices:
            return
        
        fila = indices[0].row()
        cliente_id = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.cliente_seleccionado_id = cliente_id
        
        cliente = self.cliente_modelo.obtener_por_id(cliente_id)
        if not cliente:
            return
        
        self.txt_razon_social.setText(cliente["razon_social"])
        cuit_raw = cliente["cuit"] or ""
        if len(cuit_raw) == 11:
            cuit_raw = f"{cuit_raw[:2]}-{cuit_raw[2:10]}-{cuit_raw[10]}"
        self.txt_cuit.setText(cuit_raw)
        self.cmb_iva.setCurrentText(cliente["condicion_iva"])
        self.txt_calle.setText(cliente.get("calle") or "")
        self.txt_numero.setText(cliente.get("numero") or "")
        self.txt_localidad.setText(cliente.get("localidad") or "")
        self.txt_provincia.setText(cliente.get("provincia") or "")
        self.txt_telefono.setText(cliente["telefono"] or "")
        self.txt_whatsapp.setText(cliente.get("whatsapp") or "")
        self.txt_email.setText(cliente["email"] or "")
        self.txt_latitud.setText(str(cliente.get("latitud") or ""))
        self.txt_longitud.setText(str(cliente.get("longitud") or ""))
        self.chk_tasa.setChecked(bool(cliente.get("aplica_tasa_municipal")))
        self.txt_limite.setText(str(cliente.get("limite_credito", 0)))
        
        preventista_id = cliente.get("preventista_id")
        if preventista_id:
            for i in range(self.cmb_preventista.count()):
                if self.cmb_preventista.itemData(i) == preventista_id:
                    self.cmb_preventista.setCurrentIndex(i)
                    break

    def limpiar_busqueda(self):
        self.txt_buscar.clear()
        self.cargar_tabla_clientes()

    def limpiar_formulario(self):
        self.txt_razon_social.clear()
        self.txt_cuit.clear()
        self.txt_calle.clear()
        self.txt_numero.clear()
        self.txt_localidad.clear()
        self.txt_provincia.clear()
        self.txt_telefono.clear()
        self.txt_whatsapp.clear()
        self.txt_email.clear()
        self.txt_latitud.clear()
        self.txt_longitud.clear()
        self.txt_limite.clear()
        self.cmb_iva.setCurrentIndex(0)
        self.cmb_preventista.setCurrentIndex(0)
        self.chk_tasa.setChecked(False)
        self.cliente_seleccionado_id = None

    def geolocalizar_auto(self):
        calle = self.txt_calle.text().strip()
        numero = self.txt_numero.text().strip()
        localidad = self.txt_localidad.text().strip()
        provincia = self.txt_provincia.text().strip()
        
        if not calle or not localidad:
            return
        
        self.geo_thread = GeocodingThread(calle, numero, localidad, provincia)
        def on_finished(lat, lon):
            if lat and lon:
                self.txt_latitud.setText(f"{lat:.6f}")
                self.txt_longitud.setText(f"{lon:.6f}")
        self.geo_thread.finished.connect(on_finished)
        self.geo_thread.start()

    def guardar_cliente(self):
        """Guarda un nuevo cliente (con UUID)"""
        try:
            # Validaciones
            if not self.txt_razon_social.text().strip():
                raise ValueError("Complete la Razón Social")
            if not self.txt_cuit.text().strip().replace("-", ""):
                raise ValueError("Complete el CUIT")
            if not self.txt_calle.text().strip():
                raise ValueError("Complete la Calle")
            if not self.txt_numero.text().strip():
                raise ValueError("Complete el Número")
            if not self.txt_localidad.text().strip():
                raise ValueError("Complete la Localidad")
            if not self.txt_provincia.text().strip():
                raise ValueError("Complete la Provincia")
            if not self.txt_telefono.text().strip():
                raise ValueError("Complete el Teléfono")
            if not self.txt_email.text().strip():
                raise ValueError("Complete el Email")
            
            calle = self.txt_calle.text().strip()
            numero = self.txt_numero.text().strip()
            localidad = self.txt_localidad.text().strip()
            provincia = self.txt_provincia.text().strip()
            
            lat = float(self.txt_latitud.text()) if self.txt_latitud.text() else None
            lon = float(self.txt_longitud.text()) if self.txt_longitud.text() else None
            cuit_raw = self.txt_cuit.text().strip().replace("-", "")
            preventista_id = self.cmb_preventista.currentData()
            
            # Crear cliente con UUID
            cliente_id = self.cliente_modelo.crear(
                razon_social=self.txt_razon_social.text().strip(),
                cuit=cuit_raw or None,
                condicion_iva=self.cmb_iva.currentText(),
                telefono=self.txt_telefono.text().strip(),
                email=self.txt_email.text().strip(),
                aplica_tasa_municipal=self.chk_tasa.isChecked(),
                limite_credito=float(self.txt_limite.text() or 0),
                calle=calle,
                numero=numero,
                localidad=localidad,
                provincia=provincia,
                latitud=lat,
                longitud=lon,
                preventista_id=preventista_id,
                whatsapp=self.txt_whatsapp.text().strip() or None
            )
            
            self.limpiar_formulario()
            self.cargar_tabla_clientes()
            QMessageBox.information(self, "Éxito", f"✅ Cliente guardado correctamente (UUID: {cliente_id[:8]}...)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def modificar_cliente(self):
        """Modifica un cliente existente"""
        if not self.cliente_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente de la tabla para modificar")
            return
        
        try:
            calle = self.txt_calle.text().strip()
            numero = self.txt_numero.text().strip()
            localidad = self.txt_localidad.text().strip()
            provincia = self.txt_provincia.text().strip()
            
            lat = float(self.txt_latitud.text()) if self.txt_latitud.text() else None
            lon = float(self.txt_longitud.text()) if self.txt_longitud.text() else None
            cuit_raw = self.txt_cuit.text().strip().replace("-", "")
            preventista_id = self.cmb_preventista.currentData()
            
            self.cliente_modelo.actualizar(
                self.cliente_seleccionado_id,
                razon_social=self.txt_razon_social.text().strip(),
                cuit=cuit_raw or None,
                condicion_iva=self.cmb_iva.currentText(),
                telefono=self.txt_telefono.text().strip(),
                email=self.txt_email.text().strip(),
                aplica_tasa_municipal=self.chk_tasa.isChecked(),
                limite_credito=float(self.txt_limite.text() or 0),
                calle=calle,
                numero=numero,
                localidad=localidad,
                provincia=provincia,
                latitud=lat,
                longitud=lon,
                preventista_id=preventista_id,
                whatsapp=self.txt_whatsapp.text().strip() or None
            )
            
            self.limpiar_formulario()
            self.cargar_tabla_clientes()
            QMessageBox.information(self, "Éxito", "✅ Cliente actualizado correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def eliminar_cliente(self):
        if not self.cliente_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente para eliminar")
            return
        
        confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar cliente seleccionado?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.cliente_modelo.eliminar(self.cliente_seleccionado_id)
            self.limpiar_formulario()
            self.cargar_tabla_clientes()
            QMessageBox.information(self, "Éxito", "✅ Cliente eliminado")

    def sincronizar_clientes(self):
        """Sincroniza clientes con Turso"""
        try:
            from utilidades import sincronizar_ahora
            db_conn = self.db
            resultado = sincronizar_ahora(db_conn)
            QMessageBox.information(self, "Sincronización", "✅ Clientes sincronizados con Turso")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en sincronización: {e}")

    def exportar_csv(self):
        import csv
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar listado", 
            f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        
        if filename:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id, razon_social, cuit, localidad, provincia, telefono, email, saldo_cuenta_corriente
                FROM clientes WHERE activo = 1
                ORDER BY razon_social
            """)
            
            registros = cur.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Razón Social", "CUIT", "Localidad", "Provincia", "Teléfono", "Email", "Saldo CC"])
                for c in registros:
                    writer.writerow([
                        c["id"][:8], c["razon_social"], c["cuit"] or "", 
                        c.get("localidad") or "", c.get("provincia") or "",
                        c.get("telefono") or "", c.get("email") or "",
                        f"{c.get('saldo_cuenta_corriente', 0):.2f}"
                    ])
            
            QMessageBox.information(self, "Exportar", f"✅ Exportado:\n{filename}")