"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Vista de Preventistas con UUID - BOTONES AZULES
==================================================
📌 USO: Gestión de preventistas y usuarios asociados
📌 CARACTERÍSTICAS:
    - CRUD completo con UUID
    - Gestión de usuarios asociados
    - Sincronización con Turso
"""

import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QFrame, QTabWidget,
                               QWidget, QInputDialog, QComboBox, QSplitter,
                               QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from controladores.controlador_preventistas import ControladorPreventistas
from modelos.usuario import Usuario
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


class VistaPreventistas(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.controlador = ControladorPreventistas(db)
        self.usuario_modelo = Usuario(db)
        
        self.setWindowTitle("Gestión de Preventistas")
        self.setFixedSize(950, 700)

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
            QPushButton#btnEliminar {
                background-color: #D32F2F;
                color: white;
            }
            QPushButton#btnEliminar:hover {
                background-color: #B71C1C;
            }
            QPushButton#btnSincronizar {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#btnSincronizar:hover {
                background-color: #43A047;
            }
            QPushButton#btnCrearUsuario {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#btnCrearUsuario:hover {
                background-color: #43A047;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(10, 10, 10, 10)
        tarjeta_layout.setSpacing(8)

        tarjeta_layout.addWidget(LabelSeccionAzul("👥 GESTIÓN DE PREVENTISTAS"))

        # ========== TABLA DE PREVENTISTAS ==========
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Legajo", "Zona", "Teléfono", "Estado"])
        
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.tabla.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        self.tabla.setColumnWidth(0, 100)
        self.tabla.setShowGrid(True)
        self.tabla.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setMinimumHeight(250)
        self.tabla.selectionModel().selectionChanged.connect(self.seleccionar_preventista)
        tabla_layout.addWidget(self.tabla)

        tarjeta_layout.addWidget(frame_tabla)

        # ========== FORMULARIO ==========
        frame_formulario = QFrame()
        frame_formulario.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        form_layout = QVBoxLayout(frame_formulario)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(8)

        form_layout.addWidget(LabelSeccionAzul("📋 DATOS DEL PREVENTISTA"))

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setHorizontalSpacing(10)

        # Fila 1
        grid.addWidget(LabelCampoAzul("Nombre *"), 0, 0)
        self.txt_nombre = LineEditBlanco()
        grid.addWidget(self.txt_nombre, 0, 1)
        
        grid.addWidget(LabelCampoAzul("Apellido *"), 0, 2)
        self.txt_apellido = LineEditBlanco()
        grid.addWidget(self.txt_apellido, 0, 3)

        # Fila 2
        grid.addWidget(LabelCampoAzul("Legajo"), 1, 0)
        self.txt_legajo = LineEditBlanco()
        grid.addWidget(self.txt_legajo, 1, 1)
        
        grid.addWidget(LabelCampoAzul("Zona"), 1, 2)
        self.txt_zona = LineEditBlanco()
        grid.addWidget(self.txt_zona, 1, 3)

        # Fila 3
        grid.addWidget(LabelCampoAzul("Teléfono"), 2, 0)
        self.txt_telefono = LineEditBlanco()
        grid.addWidget(self.txt_telefono, 2, 1)
        
        grid.addWidget(LabelCampoAzul("Email"), 2, 2)
        self.txt_email = LineEditBlanco()
        grid.addWidget(self.txt_email, 2, 3)

        # Fila 4: Usuario asociado
        grid.addWidget(LabelCampoAzul("Usuario"), 3, 0)
        self.lbl_usuario = QLabel("Sin usuario")
        self.lbl_usuario.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                color: #666666;
            }
        """)
        grid.addWidget(self.lbl_usuario, 3, 1)
        
        self.btn_crear_usuario = QPushButton("➕ Crear Usuario")
        self.btn_crear_usuario.setObjectName("btnCrearUsuario")
        self.btn_crear_usuario.setFixedWidth(120)
        self.btn_crear_usuario.clicked.connect(self.crear_usuario_asociado)
        grid.addWidget(self.btn_crear_usuario, 3, 2, 1, 2)

        form_layout.addLayout(grid)

        # ========== BOTONES CRUD ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_nuevo = QPushButton("➕ Nuevo")
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_modificar = QPushButton("✏️ Modificar")
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.setObjectName("btnEliminar")
        self.btn_limpiar = QPushButton("🧹 Limpiar")
        self.btn_sincronizar = QPushButton("🔄 Sincronizar")
        self.btn_sincronizar.setObjectName("btnSincronizar")

        # Estilos específicos
        self.btn_nuevo.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_guardar.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_modificar.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_eliminar.setStyleSheet("background-color: #D32F2F; color: white;")
        self.btn_limpiar.setStyleSheet("background-color: #1565C0; color: white;")
        self.btn_sincronizar.setStyleSheet("background-color: #4CAF50; color: white;")

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

        tarjeta_layout.addWidget(frame_formulario)
        layout.addWidget(tarjeta)

        # ========== CONEXIONES ==========
        self.btn_nuevo.clicked.connect(self.limpiar_formulario)
        self.btn_guardar.clicked.connect(self.guardar_preventista)
        self.btn_modificar.clicked.connect(self.modificar_preventista)
        self.btn_eliminar.clicked.connect(self.eliminar_preventista)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_sincronizar.clicked.connect(self.sincronizar_preventistas)

        # Variables
        self.preventista_seleccionado_id = None
        
        # Cargar datos
        self.cargar_tabla_preventistas()

    def cargar_tabla_preventistas(self):
        """Carga la tabla de preventistas"""
        preventistas = self.controlador.listar_preventistas(solo_activos=False)
        self.tabla.setRowCount(len(preventistas))
        
        for fila, p in enumerate(preventistas):
            self.tabla.setItem(fila, 0, QTableWidgetItem(p["id"][:8] + "..."))
            self.tabla.setItem(fila, 1, QTableWidgetItem(p["nombre"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(p["apellido"]))
            self.tabla.setItem(fila, 3, QTableWidgetItem(p.get("legajo") or "-"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(p.get("zona") or "-"))
            self.tabla.setItem(fila, 5, QTableWidgetItem(p.get("telefono") or "-"))
            
            item_estado = QTableWidgetItem("✅ Activo" if p["activo"] else "❌ Inactivo")
            if p["activo"]:
                item_estado.setForeground(QColor(40, 167, 69))
            else:
                item_estado.setForeground(QColor(158, 158, 158))
            self.tabla.setItem(fila, 6, item_estado)
            
            self.tabla.item(fila, 0).setData(Qt.ItemDataRole.UserRole, p["id"])

    def seleccionar_preventista(self):
        """Carga los datos del preventista seleccionado"""
        indices = self.tabla.selectedItems()
        if not indices:
            self.preventista_seleccionado_id = None
            self.lbl_usuario.setText("Sin usuario")
            return
        
        fila = indices[0].row()
        preventista_id = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        self.preventista_seleccionado_id = preventista_id
        
        p = self.controlador.obtener_preventista(preventista_id)
        if p:
            self.txt_nombre.setText(p["nombre"])
            self.txt_apellido.setText(p["apellido"])
            self.txt_legajo.setText(p.get("legajo") or "")
            self.txt_zona.setText(p.get("zona") or "")
            self.txt_telefono.setText(p.get("telefono") or "")
            self.txt_email.setText(p.get("email") or "")
            
            # Mostrar usuario asociado
            usuario = self.controlador.obtener_usuario_preventista(preventista_id)
            if usuario:
                self.lbl_usuario.setText(f"{usuario['username']} ({usuario['rol']})")
                self.lbl_usuario.setStyleSheet("""
                    QLabel {
                        background-color: #E8F5E9;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                        padding: 4px 6px;
                        color: #2E7D32;
                    }
                """)
                self.btn_crear_usuario.setText("👤 Usuario Creado")
                self.btn_crear_usuario.setEnabled(False)
            else:
                self.lbl_usuario.setText("Sin usuario")
                self.lbl_usuario.setStyleSheet("""
                    QLabel {
                        background-color: #F5F5F5;
                        border: 1px solid #000000;
                        border-radius: 4px;
                        padding: 4px 6px;
                        color: #666666;
                    }
                """)
                self.btn_crear_usuario.setText("➕ Crear Usuario")
                self.btn_crear_usuario.setEnabled(True)

    def limpiar_formulario(self):
        self.txt_nombre.clear()
        self.txt_apellido.clear()
        self.txt_legajo.clear()
        self.txt_zona.clear()
        self.txt_telefono.clear()
        self.txt_email.clear()
        self.lbl_usuario.setText("Sin usuario")
        self.lbl_usuario.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                color: #666666;
            }
        """)
        self.btn_crear_usuario.setText("➕ Crear Usuario")
        self.btn_crear_usuario.setEnabled(True)
        self.preventista_seleccionado_id = None
        self.tabla.clearSelection()

    def guardar_preventista(self):
        """Guarda un nuevo preventista"""
        try:
            nombre = self.txt_nombre.text().strip()
            apellido = self.txt_apellido.text().strip()
            
            if not nombre:
                raise ValueError("El nombre es obligatorio.")
            if not apellido:
                raise ValueError("El apellido es obligatorio.")
            
            resultado = self.controlador.crear_preventista(
                nombre=nombre,
                apellido=apellido,
                legajo=self.txt_legajo.text().strip() or None,
                telefono=self.txt_telefono.text().strip() or None,
                email=self.txt_email.text().strip() or None,
                zona=self.txt_zona.text().strip() or None,
                crear_usuario=False
            )
            
            self.limpiar_formulario()
            self.cargar_tabla_preventistas()
            QMessageBox.information(self, "Éxito", 
                f"✅ Preventista guardado correctamente (UUID: {resultado['preventista_id'][:8]}...)")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def modificar_preventista(self):
        """Modifica un preventista existente"""
        if not self.preventista_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un preventista para modificar")
            return
        
        nombre = self.txt_nombre.text().strip()
        apellido = self.txt_apellido.text().strip()
        
        if not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios")
            return
        
        confirm = QMessageBox.question(
            self, "Confirmar Modificación",
            f"¿Modificar preventista {nombre} {apellido}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            resultado = self.controlador.modificar_preventista(
                self.preventista_seleccionado_id,
                nombre=nombre,
                apellido=apellido,
                legajo=self.txt_legajo.text().strip() or None,
                telefono=self.txt_telefono.text().strip() or None,
                email=self.txt_email.text().strip() or None,
                zona=self.txt_zona.text().strip() or None
            )
            
            if resultado:
                QMessageBox.information(self, "Éxito", "✅ Preventista modificado correctamente")
                self.limpiar_formulario()
                self.cargar_tabla_preventistas()
            else:
                QMessageBox.warning(self, "Error", "No se pudo modificar el preventista")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {e}")

    def eliminar_preventista(self):
        """Elimina un preventista"""
        if not self.preventista_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un preventista para eliminar")
            return
        
        p = self.controlador.obtener_preventista(self.preventista_seleccionado_id)
        if not p:
            return
        
        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar preventista {p['nombre']} {p['apellido']}?\n\n"
            "⚠️ Esta acción desactivará al preventista (baja lógica).\n"
            "No se eliminarán los datos asociados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.controlador.eliminar_preventista(self.preventista_seleccionado_id)
            self.limpiar_formulario()
            self.cargar_tabla_preventistas()
            QMessageBox.information(self, "Éxito", "✅ Preventista eliminado")

    def crear_usuario_asociado(self):
        """Crea un usuario para el preventista seleccionado"""
        if not self.preventista_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un preventista primero")
            return
        
        usuario = self.controlador.obtener_usuario_preventista(self.preventista_seleccionado_id)
        if usuario:
            QMessageBox.information(self, "Aviso", "Este preventista ya tiene un usuario asociado")
            return
        
        username, ok1 = QInputDialog.getText(self, "Crear Usuario", "Nombre de usuario:")
        if not ok1 or not username.strip():
            return
        
        password, ok2 = QInputDialog.getText(self, "Crear Usuario", "Contraseña:", 
                                             QLineEdit.EchoMode.Password)
        if not ok2 or not password:
            return
        
        try:
            usuario_id = self.usuario_modelo.crear(
                username=username.strip(),
                password=password,
                rol='preventista',
                preventista_id=self.preventista_seleccionado_id
            )
            
            self.seleccionar_preventista()
            self.cargar_tabla_preventistas()
            QMessageBox.information(self, "Éxito", 
                f"✅ Usuario {username} creado para el preventista")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el usuario: {e}")

    def sincronizar_preventistas(self):
        """Sincroniza preventistas con Turso"""
        try:
            resultado = sincronizar_ahora(self.db)
            if resultado:
                self.cargar_tabla_preventistas()
                QMessageBox.information(self, "Sincronización", "✅ Preventistas sincronizados con Turso")
            else:
                QMessageBox.warning(self, "Sincronización", "⚠️ No se pudo sincronizar")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en sincronización: {e}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaPreventistas(db)
    ventana.show()
    sys.exit(app.exec())