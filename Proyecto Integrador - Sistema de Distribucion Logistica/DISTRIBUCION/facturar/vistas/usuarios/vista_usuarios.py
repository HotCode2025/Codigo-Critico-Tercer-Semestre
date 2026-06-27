"""
Código Crítico - Tercer Semestre Año 2026
Vista de Gestión de Usuarios - Solo para administradores.
Rediseñada 800x600.
"""

import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QFrame, QComboBox,
                               QInputDialog, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from modelos.usuario import Usuario
from modelos.preventista import Preventista
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


# ==================== VISTA PRINCIPAL ====================

class VistaUsuarios(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.usuario_modelo = Usuario(db)
        self.preventista_modelo = Preventista(db)
        self.cliente_modelo = Cliente(db)
        
        self.setWindowTitle("Gestión de Usuarios")
        self.setFixedSize(800, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-size: 9px;
                gridline-color: #E0E0E0;
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
                padding: 4px;
                font-weight: 600;
                border: none;
            }
            QFrame {
                background-color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
            QDialog {
                background-color: #F0F2F5;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(10, 10, 10, 10)
        tarjeta_layout.setSpacing(8)

        # ========== FILTROS ==========
        frame_filtros = QFrame()
        frame_filtros.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtros_layout = QHBoxLayout(frame_filtros)
        filtros_layout.setContentsMargins(8, 6, 8, 6)
        filtros_layout.setSpacing(8)

        filtros_layout.addWidget(QLabel("Rol:"))
        self.cmb_filtro_rol = ComboBlanco()
        self.cmb_filtro_rol.addItems(["Todos", "admin", "preventista", "cliente"])
        self.cmb_filtro_rol.setFixedWidth(100)
        self.cmb_filtro_rol.currentIndexChanged.connect(self.cargar_usuarios)
        filtros_layout.addWidget(self.cmb_filtro_rol)

        filtros_layout.addWidget(QLabel("Estado:"))
        self.cmb_filtro_estado = ComboBlanco()
        self.cmb_filtro_estado.addItems(["Todos", "Activos", "Inactivos"])
        self.cmb_filtro_estado.setFixedWidth(100)
        self.cmb_filtro_estado.currentIndexChanged.connect(self.cargar_usuarios)
        filtros_layout.addWidget(self.cmb_filtro_estado)

        self.txt_buscar = LineEditBlanco()
        self.txt_buscar.setPlaceholderText("🔍 Buscar por usuario...")
        filtros_layout.addWidget(self.txt_buscar, 1)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedWidth(70)
        btn_buscar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px;")
        btn_buscar.clicked.connect(self.cargar_usuarios)
        filtros_layout.addWidget(btn_buscar)

        tarjeta_layout.addWidget(frame_filtros)

        # ========== TABLA DE USUARIOS ==========
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Usuario", "Rol", "Asociado a", "Estado", "Acciones"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setMinimumHeight(350)
        tabla_layout.addWidget(self.tabla)

        tarjeta_layout.addWidget(frame_tabla)

        # ========== BOTONES ==========
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(8, 6, 8, 6)
        botones_layout.setSpacing(10)

        self.btn_nuevo = QPushButton("➕ Nuevo Usuario")
        self.btn_reset_pass = QPushButton("🔑 Resetear Contraseña")
        self.btn_activar = QPushButton("✅ Activar")
        self.btn_desactivar = QPushButton("⛔ Desactivar")
        self.btn_eliminar = QPushButton("🗑️ Eliminar")

        btn_style_azul = "background-color: #1565C0; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold; font-size: 10px;"
        btn_style_rojo = "background-color: #D32F2F; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold; font-size: 10px;"
        btn_style_verde = "background-color: #4CAF50; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold; font-size: 10px;"

        self.btn_nuevo.setStyleSheet(btn_style_azul)
        self.btn_reset_pass.setStyleSheet(btn_style_azul)
        self.btn_activar.setStyleSheet(btn_style_verde)
        self.btn_desactivar.setStyleSheet(btn_style_rojo)
        self.btn_eliminar.setStyleSheet(btn_style_rojo)

        self.btn_nuevo.clicked.connect(self.nuevo_usuario)
        self.btn_reset_pass.clicked.connect(self.resetear_password)
        self.btn_activar.clicked.connect(self.activar_usuario)
        self.btn_desactivar.clicked.connect(self.desactivar_usuario)
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)

        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_reset_pass)
        botones_layout.addWidget(self.btn_activar)
        botones_layout.addWidget(self.btn_desactivar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addStretch()

        tarjeta_layout.addWidget(frame_botones)

        layout.addWidget(tarjeta)

        # Cargar datos
        self.cargar_usuarios()

    # =================== FUNCIONES PRINCIPALES ===================
    
    def cargar_usuarios(self):
        rol_filtro = self.cmb_filtro_rol.currentText()
        estado_filtro = self.cmb_filtro_estado.currentText()
        busqueda = self.txt_buscar.text().strip()
        
        usuarios = self.usuario_modelo.listar_todos(solo_activos=False)
        
        # Aplicar filtros
        if rol_filtro != "Todos":
            usuarios = [u for u in usuarios if u['rol'] == rol_filtro]
        
        if estado_filtro == "Activos":
            usuarios = [u for u in usuarios if u['activo'] == 1]
        elif estado_filtro == "Inactivos":
            usuarios = [u for u in usuarios if u['activo'] == 0]
        
        if busqueda:
            usuarios = [u for u in usuarios if busqueda.lower() in u['username'].lower()]
        
        self.tabla.setRowCount(len(usuarios))
        
        for i, u in enumerate(usuarios):
            # ID
            self.tabla.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            
            # Usuario
            self.tabla.setItem(i, 1, QTableWidgetItem(u['username']))
            
            # Rol
            item_rol = QTableWidgetItem(u['rol'])
            if u['rol'] == 'admin':
                item_rol.setForeground(QColor(220, 53, 69))
            elif u['rol'] == 'preventista':
                item_rol.setForeground(QColor(33, 150, 243))
            elif u['rol'] == 'cliente':
                item_rol.setForeground(QColor(76, 175, 80))
            self.tabla.setItem(i, 2, item_rol)
            
            # Asociado a
            asociado = ""
            if u['preventista_id']:
                p = self.preventista_modelo.obtener_por_id(u['preventista_id'])
                if p:
                    asociado = f"Preventista: {p['nombre']} {p['apellido']}"
            elif u['cliente_id']:
                c = self.cliente_modelo.obtener_por_id(u['cliente_id'])
                if c:
                    asociado = f"Cliente: {c['razon_social']}"
            self.tabla.setItem(i, 3, QTableWidgetItem(asociado or "-"))
            
            # Estado
            item_estado = QTableWidgetItem("✅ Activo" if u['activo'] else "❌ Inactivo")
            if u['activo']:
                item_estado.setForeground(QColor(76, 175, 80))
            else:
                item_estado.setForeground(QColor(158, 158, 158))
            self.tabla.setItem(i, 4, item_estado)
            
            # Botón de acción (ver detalle)
            btn_ver = QPushButton("👁️ Ver")
            btn_ver.setFixedSize(50, 22)
            btn_ver.setStyleSheet("background-color: #1565C0; color: white; border-radius: 3px; font-size: 9px;")
            btn_ver.clicked.connect(lambda checked, x=u: self.ver_detalle_usuario(x))
            self.tabla.setCellWidget(i, 5, btn_ver)
            
            # Guardar ID del usuario
            self.tabla.item(i, 0).setData(Qt.ItemDataRole.UserRole, u['id'])

    # =================== DIÁLOGO NUEVO USUARIO ===================
    
    def nuevo_usuario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nuevo Usuario")
        dialog.setFixedSize(500, 450)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(15)
        
        frame_layout.addWidget(LabelSeccionAzul("DATOS DEL USUARIO"))
        
        form = QGridLayout()
        form.setSpacing(10)
        form.setHorizontalSpacing(15)
        
        # Usuario
        form.addWidget(LabelCampoAzul("Usuario *"), 0, 0)
        txt_username = LineEditBlanco()
        txt_username.setPlaceholderText("Nombre de usuario")
        form.addWidget(txt_username, 0, 1)
        
        # Contraseña
        form.addWidget(LabelCampoAzul("Contraseña *"), 1, 0)
        txt_password = LineEditBlanco()
        txt_password.setPlaceholderText("Contraseña")
        txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addWidget(txt_password, 1, 1)
        
        # Confirmar contraseña
        form.addWidget(LabelCampoAzul("Confirmar *"), 2, 0)
        txt_confirm = LineEditBlanco()
        txt_confirm.setPlaceholderText("Confirmar contraseña")
        txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        form.addWidget(txt_confirm, 2, 1)
        
        # Rol
        form.addWidget(LabelCampoAzul("Rol *"), 3, 0)
        cmb_rol = ComboBlanco()
        cmb_rol.addItems(["preventista", "cliente", "admin"])
        form.addWidget(cmb_rol, 3, 1)
        
        # Preventista (visible solo si rol = preventista)
        form.addWidget(LabelCampoAzul("Preventista"), 4, 0)
        cmb_preventista = ComboBlanco()
        cmb_preventista.addItem("-- Ninguno --", None)
        for p in self.preventista_modelo.listar_todos(solo_activos=True):
            cmb_preventista.addItem(f"{p['nombre']} {p['apellido']}", p['id'])
        form.addWidget(cmb_preventista, 4, 1)
        
        # Cliente (visible solo si rol = cliente)
        form.addWidget(LabelCampoAzul("Cliente"), 5, 0)
        cmb_cliente = ComboBlanco()
        cmb_cliente.addItem("-- Ninguno --", None)
        for c in self.cliente_modelo.listar_todos(solo_activos=True):
            cmb_cliente.addItem(c['razon_social'], c['id'])
        form.addWidget(cmb_cliente, 5, 1)
        
        # Ocultar/mostrar según rol
        def toggle_asociacion():
            rol = cmb_rol.currentText()
            # Preventista
            lbl_prev = form.itemAtPosition(4, 0).widget()
            cmb_prev = form.itemAtPosition(4, 1).widget()
            # Cliente
            lbl_cli = form.itemAtPosition(5, 0).widget()
            cmb_cli = form.itemAtPosition(5, 1).widget()
            
            if rol == "preventista":
                lbl_prev.setVisible(True)
                cmb_prev.setVisible(True)
                lbl_cli.setVisible(False)
                cmb_cli.setVisible(False)
            elif rol == "cliente":
                lbl_prev.setVisible(False)
                cmb_prev.setVisible(False)
                lbl_cli.setVisible(True)
                cmb_cli.setVisible(True)
            else:  # admin
                lbl_prev.setVisible(False)
                cmb_prev.setVisible(False)
                lbl_cli.setVisible(False)
                cmb_cli.setVisible(False)
        
        cmb_rol.currentIndexChanged.connect(toggle_asociacion)
        toggle_asociacion()
        
        frame_layout.addLayout(form)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 8px 16px; font-weight: bold;")
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setStyleSheet("background-color: #D32F2F; color: white; border-radius: 4px; padding: 8px 16px; font-weight: bold;")
        
        def guardar():
            username = txt_username.text().strip()
            password = txt_password.text()
            confirm = txt_confirm.text()
            rol = cmb_rol.currentText()
            preventista_id = cmb_preventista.currentData() if rol == "preventista" else None
            cliente_id = cmb_cliente.currentData() if rol == "cliente" else None
            
            if not username:
                QMessageBox.warning(dialog, "Error", "Complete el nombre de usuario.")
                return
            if not password:
                QMessageBox.warning(dialog, "Error", "Complete la contraseña.")
                return
            if password != confirm:
                QMessageBox.warning(dialog, "Error", "Las contraseñas no coinciden.")
                return
            if rol == "preventista" and not preventista_id:
                QMessageBox.warning(dialog, "Error", "Seleccione un preventista.")
                return
            if rol == "cliente" and not cliente_id:
                QMessageBox.warning(dialog, "Error", "Seleccione un cliente.")
                return
            
            try:
                self.usuario_modelo.crear(
                    username=username,
                    password=password,
                    rol=rol,
                    preventista_id=preventista_id,
                    cliente_id=cliente_id
                )
                self.cargar_usuarios()
                QMessageBox.information(dialog, "Éxito", f"Usuario {username} creado correctamente.")
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", str(e))
        
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        
        frame_layout.addLayout(btn_layout)
        
        layout.addWidget(frame)
        dialog.exec()

    # =================== DETALLE DE USUARIO ===================
    
    def ver_detalle_usuario(self, usuario):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle de Usuario - {usuario['username']}")
        dialog.setFixedSize(450, 350)
        dialog.setStyleSheet("background-color: #F0F2F5;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #D0D0D0;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(15, 15, 15, 15)
        frame_layout.setSpacing(10)
        
        lbl_titulo = QLabel(f"DETALLE DE USUARIO")
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A237E;")
        frame_layout.addWidget(lbl_titulo)
        
        datos = QGridLayout()
        datos.setSpacing(8)
        
        datos.addWidget(QLabel("<b>ID:</b>"), 0, 0)
        datos.addWidget(QLabel(str(usuario['id'])), 0, 1)
        datos.addWidget(QLabel("<b>Usuario:</b>"), 0, 2)
        datos.addWidget(QLabel(usuario['username']), 0, 3)
        
        datos.addWidget(QLabel("<b>Rol:</b>"), 1, 0)
        lbl_rol = QLabel(usuario['rol'])
        if usuario['rol'] == 'admin':
            lbl_rol.setStyleSheet("color: #D32F2F; font-weight: bold;")
        elif usuario['rol'] == 'preventista':
            lbl_rol.setStyleSheet("color: #2196F3; font-weight: bold;")
        elif usuario['rol'] == 'cliente':
            lbl_rol.setStyleSheet("color: #4CAF50; font-weight: bold;")
        datos.addWidget(lbl_rol, 1, 1)
        
        datos.addWidget(QLabel("<b>Estado:</b>"), 1, 2)
        lbl_estado = QLabel("Activo" if usuario['activo'] else "Inactivo")
        lbl_estado.setStyleSheet("color: #4CAF50; font-weight: bold;" if usuario['activo'] else "color: #999;")
        datos.addWidget(lbl_estado, 1, 3)
        
        # Asociado a
        if usuario.get('preventista_id'):
            p = self.preventista_modelo.obtener_por_id(usuario['preventista_id'])
            if p:
                datos.addWidget(QLabel("<b>Preventista:</b>"), 2, 0)
                datos.addWidget(QLabel(f"{p['nombre']} {p['apellido']}"), 2, 1, 1, 3)
        elif usuario.get('cliente_id'):
            c = self.cliente_modelo.obtener_por_id(usuario['cliente_id'])
            if c:
                datos.addWidget(QLabel("<b>Cliente:</b>"), 2, 0)
                datos.addWidget(QLabel(c['razon_social']), 2, 1, 1, 3)
        
        datos.addWidget(QLabel("<b>Creado:</b>"), 3, 0)
        datos.addWidget(QLabel(usuario.get('created_at', '-')), 3, 1, 1, 3)
        
        frame_layout.addLayout(datos)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 4px; padding: 8px 16px;")
        btn_cerrar.clicked.connect(dialog.accept)
        
        frame_layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(frame)
        dialog.exec()

    # =================== ACCIONES ===================
    
    def resetear_password(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario.")
            return
        
        usuario_id = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla.item(fila, 1).text()
        
        nueva_pass, ok = QInputDialog.getText(self, "Resetear Contraseña", 
                                              f"Nueva contraseña para {username}:",
                                              QLineEdit.EchoMode.Password)
        
        if ok and nueva_pass:
            if self.usuario_modelo.resetear_contrasena(usuario_id, nueva_pass):
                QMessageBox.information(self, "Éxito", f"Contraseña de {username} reseteada correctamente.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo resetear la contraseña.")

    def activar_usuario(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario.")
            return
        
        usuario_id = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla.item(fila, 1).text()
        
        if username == 'admin':
            QMessageBox.warning(self, "Error", "No se puede desactivar/activar el usuario admin.")
            return
        
        confirm = QMessageBox.question(self, "Confirmar", 
                                       f"¿Activar usuario {username}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.usuario_modelo.activar(usuario_id):
                self.cargar_usuarios()
                QMessageBox.information(self, "Éxito", f"Usuario {username} activado.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo activar el usuario.")

    def desactivar_usuario(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario.")
            return
        
        usuario_id = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla.item(fila, 1).text()
        
        if username == 'admin':
            QMessageBox.warning(self, "Error", "No se puede desactivar el usuario admin.")
            return
        
        confirm = QMessageBox.question(self, "Confirmar", 
                                       f"¿Desactivar usuario {username}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.usuario_modelo.desactivar(usuario_id):
                self.cargar_usuarios()
                QMessageBox.information(self, "Éxito", f"Usuario {username} desactivado.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo desactivar el usuario.")

    def eliminar_usuario(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un usuario.")
            return
        
        usuario_id = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        username = self.tabla.item(fila, 1).text()
        
        if username == 'admin':
            QMessageBox.warning(self, "Error", "No se puede eliminar el usuario admin.")
            return
        
        confirm = QMessageBox.question(self, "Confirmar", 
                                       f"¿Eliminar usuario {username}?\nEsta acción no se puede deshacer.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.usuario_modelo.eliminar(usuario_id):
                self.cargar_usuarios()
                QMessageBox.information(self, "Éxito", f"Usuario {username} eliminado.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el usuario.")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaUsuarios(db)
    ventana.show()
    sys.exit(app.exec())