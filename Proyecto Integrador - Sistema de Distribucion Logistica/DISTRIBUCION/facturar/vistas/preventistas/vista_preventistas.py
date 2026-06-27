"""
Código Crítico - Tercer Semestre Año 2026
Gestor de Contraseñas - Vista unificada de Usuarios y Preventistas.
Roles: admin, usuario, preventista.
SIN TABLAS NUEVAS - usa las existentes en el script.
"""

import sqlite3
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QFrame, QWidget, QTabWidget,
                               QInputDialog, QComboBox, QSplitter, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from controladores.controlador_preventistas import ControladorPreventistas
from modelos.usuario import Usuario
from utilidades.central_sync import enviar_a_turso


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


# ==================== VISTA PRINCIPAL ====================

class VistaPreventistas(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.controlador = ControladorPreventistas(db)
        self.usuario_modelo = Usuario(db)
        self.setWindowTitle("Gestor de Contraseñas")
        self.setFixedSize(1000, 750)
        
        # Directorio para logs de auditoría
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

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
            QTextEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-family: monospace;
                font-size: 10px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(8, 8, 8, 8)
        tarjeta_layout.setSpacing(5)

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        # Solapa 1: Gestor de Contraseñas (unificada)
        self.tab_gestor = self._crear_tab_gestor()
        self.tabs.addTab(self.tab_gestor, "🔐 GESTOR DE CONTRASEÑAS")
        
        # Solapa 2: Roles y Auditoría
        self.tab_auditoria = self._crear_tab_auditoria()
        self.tabs.addTab(self.tab_auditoria, "📊 ROLES Y AUDITORÍA")
        
        tarjeta_layout.addWidget(self.tabs)
        layout.addWidget(tarjeta)

        self.preventista_seleccionado_id = None
        self.cargar_tabla_gestor()
        self.cargar_auditoria()

    def _registrar_login(self, usuario_id, username):
        """Registra un inicio de sesión en el archivo de logs."""
        try:
            log_file = os.path.join(self.log_dir, "auditoria_logins.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | LOGIN | {usuario_id} | {username}\n")
        except Exception as e:
            print(f"⚠️ Error registrando login: {e}")

    def _registrar_cambio_password(self, usuario_id, username, motivo=None):
        """Registra un cambio de contraseña en el archivo de logs."""
        try:
            log_file = os.path.join(self.log_dir, "auditoria_password.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | CAMBIO PASS | {usuario_id} | {username} | {motivo or 'Sin motivo'}\n")
        except Exception as e:
            print(f"⚠️ Error registrando cambio de password: {e}")

    def _obtener_historial_logins(self, usuario_id):
        """Obtiene el historial de logins de un usuario desde el archivo de logs."""
        historial = []
        log_file = os.path.join(self.log_dir, "auditoria_logins.log")
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        partes = line.strip().split(" | ")
                        if len(partes) >= 4 and partes[2] == str(usuario_id):
                            historial.append({
                                'fecha': partes[0],
                                'tipo': 'LOGIN',
                                'usuario': partes[3],
                                'detalle': 'Inicio de sesión'
                            })
            except Exception as e:
                print(f"⚠️ Error leyendo logins: {e}")
        return historial

    def _obtener_historial_password(self, usuario_id):
        """Obtiene el historial de cambios de contraseña de un usuario desde el archivo de logs."""
        historial = []
        log_file = os.path.join(self.log_dir, "auditoria_password.log")
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        partes = line.strip().split(" | ")
                        if len(partes) >= 5 and partes[2] == str(usuario_id):
                            historial.append({
                                'fecha': partes[0],
                                'tipo': 'CAMBIO PASS',
                                'usuario': partes[3],
                                'detalle': partes[4] if len(partes) > 4 else 'Cambio de contraseña'
                            })
            except Exception as e:
                print(f"⚠️ Error leyendo cambios de password: {e}")
        return historial

    # ==================== PESTAÑA 1: GESTOR DE CONTRASEÑAS ====================
    
    def _crear_tab_gestor(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # ========== SELECTOR DE TIPO ==========
        frame_selector = QFrame()
        frame_selector.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        selector_layout = QHBoxLayout(frame_selector)
        selector_layout.setContentsMargins(10, 8, 10, 8)
        selector_layout.setSpacing(10)

        selector_layout.addWidget(QLabel("Mostrar:"))
        self.cmb_tipo = ComboBlanco()
        self.cmb_tipo.addItems(["Usuarios del Sistema", "Preventistas (Tablet)"])
        self.cmb_tipo.setFixedWidth(200)
        self.cmb_tipo.currentIndexChanged.connect(self.cargar_tabla_gestor)
        selector_layout.addWidget(self.cmb_tipo)

        selector_layout.addStretch()

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setStyleSheet("background-color: #1565C0; color: white;")
        btn_refrescar.clicked.connect(self.cargar_tabla_gestor)
        selector_layout.addWidget(btn_refrescar)

        layout.addWidget(frame_selector)

        # ========== TABLA ==========
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_gestor = QTableWidget()
        self.tabla_gestor.setColumnCount(7)
        self.tabla_gestor.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre", "Rol", "Estado", "Creado/Zona", "Acciones"])
        self.tabla_gestor.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_gestor.setShowGrid(True)
        self.tabla_gestor.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_gestor.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_gestor.setAlternatingRowColors(True)
        self.tabla_gestor.setMinimumHeight(300)
        tabla_layout.addWidget(self.tabla_gestor)

        layout.addWidget(frame_tabla)

        # ========== FORMULARIO DE CREACIÓN ==========
        frame_form = QFrame()
        frame_form.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        form_layout = QVBoxLayout(frame_form)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(8)

        form_layout.addWidget(LabelSeccionAzul("CREAR NUEVO USUARIO / PREVENTISTA"))

        grid_form = QGridLayout()
        grid_form.setSpacing(8)
        grid_form.setHorizontalSpacing(10)

        # Fila 1: Usuario y Contraseña
        grid_form.addWidget(LabelCampoAzul("Usuario *"), 0, 0)
        self.txt_username = LineEditBlanco()
        self.txt_username.setPlaceholderText("Nombre de usuario")
        grid_form.addWidget(self.txt_username, 0, 1)
        
        grid_form.addWidget(LabelCampoAzul("Contraseña *"), 0, 2)
        self.txt_password = LineEditBlanco()
        self.txt_password.setPlaceholderText("********")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        grid_form.addWidget(self.txt_password, 0, 3)

        # Fila 2: Nombre y Apellido (solo para preventistas)
        grid_form.addWidget(LabelCampoAzul("Nombre"), 1, 0)
        self.txt_nombre = LineEditBlanco()
        self.txt_nombre.setPlaceholderText("(solo para preventistas)")
        grid_form.addWidget(self.txt_nombre, 1, 1)
        
        grid_form.addWidget(LabelCampoAzul("Apellido"), 1, 2)
        self.txt_apellido = LineEditBlanco()
        self.txt_apellido.setPlaceholderText("(solo para preventistas)")
        grid_form.addWidget(self.txt_apellido, 1, 3)

        # Fila 3: Rol y Legajo
        grid_form.addWidget(LabelCampoAzul("Rol *"), 2, 0)
        self.cmb_rol = ComboBlanco()
        self.cmb_rol.addItems(["preventista", "usuario", "admin"])
        grid_form.addWidget(self.cmb_rol, 2, 1)
        
        grid_form.addWidget(LabelCampoAzul("Legajo"), 2, 2)
        self.txt_legajo = LineEditBlanco()
        self.txt_legajo.setPlaceholderText("(solo para preventistas)")
        grid_form.addWidget(self.txt_legajo, 2, 3)

        # Fila 4: Zona y Teléfono
        grid_form.addWidget(LabelCampoAzul("Zona"), 3, 0)
        self.txt_zona = LineEditBlanco()
        self.txt_zona.setPlaceholderText("(solo para preventistas)")
        grid_form.addWidget(self.txt_zona, 3, 1)
        
        grid_form.addWidget(LabelCampoAzul("Teléfono"), 3, 2)
        self.txt_telefono = LineEditBlanco()
        self.txt_telefono.setPlaceholderText("(solo para preventistas)")
        grid_form.addWidget(self.txt_telefono, 3, 3)

        # Fila 5: Email
        grid_form.addWidget(LabelCampoAzul("Email"), 4, 0)
        self.txt_email = LineEditBlanco()
        self.txt_email.setPlaceholderText("(solo para preventistas)")
        grid_form.addWidget(self.txt_email, 4, 1, 1, 3)

        form_layout.addLayout(grid_form)

        # Botones CRUD
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_crear = QPushButton("➕ Crear Usuario")
        self.btn_crear.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_crear.clicked.connect(self.crear_usuario)

        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setStyleSheet("background-color: #D32F2F; color: white;")
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)

        self.btn_limpiar = QPushButton("🧹 Limpiar")
        self.btn_limpiar.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_crear)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_limpiar)

        form_layout.addLayout(btn_layout)

        layout.addWidget(frame_form)

        return tab

    # ==================== PESTAÑA 2: ROLES Y AUDITORÍA ====================
    
    def _crear_tab_auditoria(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # ========== FILTROS ==========
        frame_filtros = QFrame()
        frame_filtros.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtros_layout = QHBoxLayout(frame_filtros)
        filtros_layout.setContentsMargins(10, 8, 10, 8)
        filtros_layout.setSpacing(10)

        filtros_layout.addWidget(QLabel("Rol:"))
        self.cmb_filtro_rol = ComboBlanco()
        self.cmb_filtro_rol.addItems(["Todos", "admin", "usuario", "preventista"])
        self.cmb_filtro_rol.setFixedWidth(100)
        self.cmb_filtro_rol.currentIndexChanged.connect(self.cargar_auditoria)
        filtros_layout.addWidget(self.cmb_filtro_rol)

        filtros_layout.addWidget(QLabel("Estado:"))
        self.cmb_filtro_estado = ComboBlanco()
        self.cmb_filtro_estado.addItems(["Todos", "Activos", "Inactivos"])
        self.cmb_filtro_estado.setFixedWidth(100)
        self.cmb_filtro_estado.currentIndexChanged.connect(self.cargar_auditoria)
        filtros_layout.addWidget(self.cmb_filtro_estado)

        filtros_layout.addStretch()

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.setStyleSheet("background-color: #1565C0; color: white;")
        btn_refrescar.clicked.connect(self.cargar_auditoria)
        filtros_layout.addWidget(btn_refrescar)

        # ✅ BOTONES ACTIVAR / DESACTIVAR
        btn_activar = QPushButton("✅ Activar Usuario")
        btn_activar.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_activar.clicked.connect(self.activar_usuario_desde_auditoria)

        btn_desactivar = QPushButton("⛔ Desactivar Usuario")
        btn_desactivar.setStyleSheet("background-color: #D32F2F; color: white;")
        btn_desactivar.clicked.connect(self.desactivar_usuario_desde_auditoria)

        filtros_layout.addWidget(btn_activar)
        filtros_layout.addWidget(btn_desactivar)

        layout.addWidget(frame_filtros)

        # ========== TABLA DE USUARIOS ==========
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_auditoria = QTableWidget()
        self.tabla_auditoria.setColumnCount(6)
        self.tabla_auditoria.setHorizontalHeaderLabels(["ID", "Usuario", "Rol", "Asociado a", "Estado", "Último Login"])
        self.tabla_auditoria.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_auditoria.setShowGrid(True)
        self.tabla_auditoria.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_auditoria.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_auditoria.setAlternatingRowColors(True)
        self.tabla_auditoria.setMinimumHeight(200)
        self.tabla_auditoria.doubleClicked.connect(self._ver_historial_usuario)
        tabla_layout.addWidget(self.tabla_auditoria)

        layout.addWidget(frame_tabla)

        # ========== HISTORIAL DETALLADO ==========
        frame_historial = QFrame()
        frame_historial.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        historial_layout = QVBoxLayout(frame_historial)
        historial_layout.setContentsMargins(5, 5, 5, 5)

        historial_layout.addWidget(LabelSeccionAzul("📋 HISTORIAL DE LOGINS Y CAMBIOS DE CONTRASEÑA"))

        self.tabla_historial_detalle = QTableWidget()
        self.tabla_historial_detalle.setColumnCount(4)
        self.tabla_historial_detalle.setHorizontalHeaderLabels(["Fecha", "Tipo", "Usuario", "Detalle"])
        self.tabla_historial_detalle.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_historial_detalle.setShowGrid(True)
        self.tabla_historial_detalle.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_historial_detalle.setAlternatingRowColors(True)
        self.tabla_historial_detalle.setMinimumHeight(150)
        historial_layout.addWidget(self.tabla_historial_detalle)

        layout.addWidget(frame_historial)

        return tab

    # ==================== FUNCIONES DEL GESTOR ====================
    
    def cargar_tabla_gestor(self):
        """Carga la tabla según el tipo seleccionado (usuarios o preventistas)."""
        tipo = self.cmb_tipo.currentText()
        
        if tipo == "Usuarios del Sistema":
            self._cargar_usuarios()
        else:
            self._cargar_preventistas()
    
    def _cargar_usuarios(self):
        """Carga los usuarios del sistema."""
        usuarios = self.usuario_modelo.listar_todos(solo_activos=False)
        self.tabla_gestor.setRowCount(len(usuarios))
        
        self.tabla_gestor.setColumnCount(7)
        self.tabla_gestor.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre", "Rol", "Estado", "Creado", "Acciones"])
        
        for i, u in enumerate(usuarios):
            self.tabla_gestor.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            self.tabla_gestor.setItem(i, 1, QTableWidgetItem(u['username']))
            
            nombre = ""
            if u['preventista_id']:
                p = self.controlador.obtener_preventista(u['preventista_id'])
                if p:
                    nombre = f"{p['nombre']} {p['apellido']}"
            elif u['cliente_id']:
                cur = self.db.cursor()
                cur.execute("SELECT razon_social FROM clientes WHERE id = ?", (u['cliente_id'],))
                row = cur.fetchone()
                if row:
                    nombre = row['razon_social']
            self.tabla_gestor.setItem(i, 2, QTableWidgetItem(nombre))
            
            item_rol = QTableWidgetItem(u['rol'])
            if u['rol'] == 'admin':
                item_rol.setForeground(QColor(220, 53, 69))
            elif u['rol'] == 'preventista':
                item_rol.setForeground(QColor(33, 150, 243))
            else:
                item_rol.setForeground(QColor(76, 175, 80))
            self.tabla_gestor.setItem(i, 3, item_rol)
            
            item_estado = QTableWidgetItem("✅ Activo" if u['activo'] else "❌ Inactivo")
            if u['activo']:
                item_estado.setForeground(QColor(76, 175, 80))
            else:
                item_estado.setForeground(QColor(158, 158, 158))
            self.tabla_gestor.setItem(i, 4, item_estado)
            
            self.tabla_gestor.setItem(i, 5, QTableWidgetItem(u.get('created_at', '')[:10] if u.get('created_at') else ''))
            
            btn_reset = QPushButton("🔑 Reset Pass")
            btn_reset.setFixedSize(80, 22)
            btn_reset.setStyleSheet("background-color: #1565C0; color: white; border-radius: 3px; font-size: 9px;")
            btn_reset.clicked.connect(lambda checked, uid=u['id'], uname=u['username']: self.resetear_password(uid, uname))
            self.tabla_gestor.setCellWidget(i, 6, btn_reset)
            
            self.tabla_gestor.item(i, 0).setData(Qt.ItemDataRole.UserRole, u['id'])
    
    def _cargar_preventistas(self):
        """Carga los preventistas (para tablet)."""
        preventistas = self.controlador.listar_preventistas(solo_activos=False)
        self.tabla_gestor.setRowCount(len(preventistas))
        
        self.tabla_gestor.setColumnCount(7)
        self.tabla_gestor.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre", "Rol", "Estado", "Zona", "Acciones"])
        
        for i, p in enumerate(preventistas):
            self.tabla_gestor.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            
            usuario = self.usuario_modelo.obtener_por_preventista_id(p["id"])
            self.tabla_gestor.setItem(i, 1, QTableWidgetItem(usuario['username'] if usuario else "Sin usuario"))
            
            self.tabla_gestor.setItem(i, 2, QTableWidgetItem(f"{p['nombre']} {p['apellido']}"))
            
            item_rol = QTableWidgetItem("preventista")
            item_rol.setForeground(QColor(33, 150, 243))
            self.tabla_gestor.setItem(i, 3, item_rol)
            
            item_estado = QTableWidgetItem("✅ Activo" if p['activo'] else "❌ Inactivo")
            if p['activo']:
                item_estado.setForeground(QColor(76, 175, 80))
            else:
                item_estado.setForeground(QColor(158, 158, 158))
            self.tabla_gestor.setItem(i, 4, item_estado)
            
            self.tabla_gestor.setItem(i, 5, QTableWidgetItem(p.get('zona', '') or '-'))
            
            btn_reset = QPushButton("🔑 Reset Pass")
            btn_reset.setFixedSize(80, 22)
            btn_reset.setStyleSheet("background-color: #1565C0; color: white; border-radius: 3px; font-size: 9px;")
            if usuario:
                btn_reset.clicked.connect(lambda checked, uid=usuario['id'], uname=usuario['username']: self.resetear_password(uid, uname))
            else:
                btn_reset.setEnabled(False)
            self.tabla_gestor.setCellWidget(i, 6, btn_reset)
            
            self.tabla_gestor.item(i, 0).setData(Qt.ItemDataRole.UserRole, p["id"])
    
    def crear_usuario(self):
        """Crea un nuevo usuario o preventista."""
        try:
            username = self.txt_username.text().strip()
            password = self.txt_password.text().strip()
            rol = self.cmb_rol.currentText()
            nombre = self.txt_nombre.text().strip()
            apellido = self.txt_apellido.text().strip()
            legajo = self.txt_legajo.text().strip()
            zona = self.txt_zona.text().strip()
            telefono = self.txt_telefono.text().strip()
            email = self.txt_email.text().strip()
            
            if not username or not password:
                raise ValueError("Usuario y contraseña son obligatorios.")
            
            if self.usuario_modelo.obtener_por_username(username):
                raise ValueError(f"El usuario '{username}' ya existe.")
            
            # Si es preventista, crear preventista primero
            if rol == 'preventista':
                if not nombre or not apellido:
                    raise ValueError("Para preventistas, nombre y apellido son obligatorios.")
                
                preventista_id = self.controlador.crear_preventista(
                    nombre=nombre,
                    apellido=apellido,
                    legajo=legajo or None,
                    telefono=telefono or None,
                    email=email or None,
                    zona=zona or None
                )
                
                usuario_id = self.usuario_modelo.crear(
                    username=username,
                    password=password,
                    rol=rol,
                    preventista_id=preventista_id
                )
                
                mensaje = f"Preventista {nombre} {apellido} creado con usuario {username}"
            else:
                # Crear solo usuario
                usuario_id = self.usuario_modelo.crear(
                    username=username,
                    password=password,
                    rol=rol
                )
                mensaje = f"Usuario {username} ({rol}) creado correctamente"
            
            self._registrar_cambio_password(usuario_id, username, "Usuario creado")
            
            # Sincronizar con Turso
            enviar_a_turso(
                "INSERT INTO usuarios (username, password_hash, rol, activo) VALUES (?, ?, ?, 1)",
                [username, self.usuario_modelo._hash_password(password), rol]
            )
            
            self.limpiar_formulario()
            self.cargar_tabla_gestor()
            self.cargar_auditoria()
            QMessageBox.information(self, "Éxito", mensaje)
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear: {e}")

    def eliminar_usuario(self):
        """Elimina el usuario seleccionado."""
        fila = self.tabla_gestor.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario para eliminar.")
            return
        
        usuario_id = self.tabla_gestor.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla_gestor.item(fila, 1).text()
        
        if username == 'admin':
            QMessageBox.warning(self, "Error", "No se puede eliminar el usuario admin.")
            return
        
        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar usuario '{username}'?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.usuario_modelo.eliminar(usuario_id)
                self.cargar_tabla_gestor()
                self.cargar_auditoria()
                QMessageBox.information(self, "Éxito", f"Usuario {username} eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    def resetear_password(self, usuario_id, username):
        """Resetea la contraseña de un usuario."""
        nueva_pass, ok = QInputDialog.getText(
            self, "Resetear Contraseña",
            f"Nueva contraseña para {username}:",
            QLineEdit.EchoMode.Password
        )
        
        if ok and nueva_pass:
            try:
                self.usuario_modelo.resetear_contrasena(usuario_id, nueva_pass)
                self._registrar_cambio_password(usuario_id, username, "Reset por administrador")
                self.cargar_auditoria()
                QMessageBox.information(self, "Éxito", f"Contraseña de {username} reseteada.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo resetear: {e}")

    def limpiar_formulario(self):
        """Limpia el formulario."""
        self.txt_username.clear()
        self.txt_password.clear()
        self.txt_nombre.clear()
        self.txt_apellido.clear()
        self.txt_legajo.clear()
        self.txt_zona.clear()
        self.txt_telefono.clear()
        self.txt_email.clear()
        self.cmb_rol.setCurrentIndex(0)

    # ==================== FUNCIONES AUDITORÍA ====================
    
    def cargar_auditoria(self):
        """Carga la tabla de usuarios con información de auditoría."""
        rol_filtro = self.cmb_filtro_rol.currentText()
        estado_filtro = self.cmb_filtro_estado.currentText()
        
        usuarios = self.usuario_modelo.listar_todos(solo_activos=False)
        
        if rol_filtro != "Todos":
            usuarios = [u for u in usuarios if u['rol'] == rol_filtro]
        
        if estado_filtro == "Activos":
            usuarios = [u for u in usuarios if u['activo'] == 1]
        elif estado_filtro == "Inactivos":
            usuarios = [u for u in usuarios if u['activo'] == 0]
        
        self.tabla_auditoria.setRowCount(len(usuarios))
        
        for i, u in enumerate(usuarios):
            self.tabla_auditoria.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            self.tabla_auditoria.setItem(i, 1, QTableWidgetItem(u['username']))
            
            item_rol = QTableWidgetItem(u['rol'])
            if u['rol'] == 'admin':
                item_rol.setForeground(QColor(220, 53, 69))
            elif u['rol'] == 'preventista':
                item_rol.setForeground(QColor(33, 150, 243))
            else:
                item_rol.setForeground(QColor(76, 175, 80))
            self.tabla_auditoria.setItem(i, 2, item_rol)
            
            asociado = ""
            if u['preventista_id']:
                p = self.controlador.obtener_preventista(u['preventista_id'])
                if p:
                    asociado = f"{p['nombre']} {p['apellido']}"
            elif u['cliente_id']:
                cur = self.db.cursor()
                cur.execute("SELECT razon_social FROM clientes WHERE id = ?", (u['cliente_id'],))
                row = cur.fetchone()
                if row:
                    asociado = row['razon_social']
            self.tabla_auditoria.setItem(i, 3, QTableWidgetItem(asociado or "-"))
            
            item_estado = QTableWidgetItem("✅ Activo" if u['activo'] else "❌ Inactivo")
            if u['activo']:
                item_estado.setForeground(QColor(76, 175, 80))
            else:
                item_estado.setForeground(QColor(158, 158, 158))
            self.tabla_auditoria.setItem(i, 4, item_estado)
            
            # Último login (desde el archivo de logs)
            logins = self._obtener_historial_logins(u['id'])
            ultimo_login = "Nunca"
            if logins:
                ultimo_login = logins[0]['fecha'][:16]
            self.tabla_auditoria.setItem(i, 5, QTableWidgetItem(ultimo_login))
            
            self.tabla_auditoria.item(i, 0).setData(Qt.ItemDataRole.UserRole, u['id'])
        
        self.tabla_historial_detalle.setRowCount(0)

    def _ver_historial_usuario(self):
        """Muestra el historial detallado del usuario seleccionado."""
        fila = self.tabla_auditoria.currentRow()
        if fila < 0:
            return
        
        usuario_id = self.tabla_auditoria.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla_auditoria.item(fila, 1).text()
        
        # Obtener historial desde archivos de logs
        historial = []
        historial.extend(self._obtener_historial_logins(usuario_id))
        historial.extend(self._obtener_historial_password(usuario_id))
        
        historial.sort(key=lambda x: x['fecha'], reverse=True)
        
        self.tabla_historial_detalle.setRowCount(len(historial))
        for i, h in enumerate(historial):
            fecha = h['fecha'][:16] if h['fecha'] else ''
            self.tabla_historial_detalle.setItem(i, 0, QTableWidgetItem(fecha))
            
            item_tipo = QTableWidgetItem(h['tipo'])
            if h['tipo'] == 'LOGIN':
                item_tipo.setForeground(QColor(33, 150, 243))
            else:
                item_tipo.setForeground(QColor(255, 165, 0))
            self.tabla_historial_detalle.setItem(i, 1, item_tipo)
            
            self.tabla_historial_detalle.setItem(i, 2, QTableWidgetItem(h['usuario']))
            self.tabla_historial_detalle.setItem(i, 3, QTableWidgetItem(h['detalle']))

    def activar_usuario_desde_auditoria(self):
        """Activa un usuario desde la pestaña de auditoría."""
        fila = self.tabla_auditoria.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario para activar.")
            return
        
        usuario_id = self.tabla_auditoria.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla_auditoria.item(fila, 1).text()
        
        if username == 'admin':
            QMessageBox.warning(self, "Error", "El usuario admin ya está activo.")
            return
        
        confirm = QMessageBox.question(
            self, "Confirmar",
            f"¿Activar usuario {username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.usuario_modelo.activar(usuario_id)
                self.cargar_auditoria()
                self.cargar_tabla_gestor()
                QMessageBox.information(self, "Éxito", f"Usuario {username} activado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo activar: {e}")

    def desactivar_usuario_desde_auditoria(self):
        """Desactiva un usuario desde la pestaña de auditoría."""
        fila = self.tabla_auditoria.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario para desactivar.")
            return
        
        usuario_id = self.tabla_auditoria.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla_auditoria.item(fila, 1).text()
        
        if username == 'admin':
            QMessageBox.warning(self, "Error", "No se puede desactivar el usuario admin.")
            return
        
        confirm = QMessageBox.question(
            self, "Confirmar",
            f"¿Desactivar usuario {username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.usuario_modelo.desactivar(usuario_id)
                self.cargar_auditoria()
                self.cargar_tabla_gestor()
                QMessageBox.information(self, "Éxito", f"Usuario {username} desactivado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo desactivar: {e}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaPreventistas(db)
    ventana.show()
    sys.exit(app.exec())