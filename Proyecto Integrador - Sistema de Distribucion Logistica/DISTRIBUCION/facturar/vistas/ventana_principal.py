"""
Código Crítico - Tercer Semestre Año 2026
Ventana Principal - Sistema de Distribución y Logística
CON ESCALADO GLOBAL NATIVO (QT_SCALE_FACTOR)
Tamaño: 1300x800
"""

import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFrame, QMenuBar, QMessageBox,
                               QDialog, QLineEdit, QFormLayout, QApplication,
                               QStatusBar, QSpacerItem, QSizePolicy, QCheckBox)
from PyQt6.QtGui import QAction, QFont, QColor, QKeyEvent
from PyQt6.QtCore import Qt, QTimer, QEvent

from db.db_manager import obtener_conexion
from modelos.nota_venta import NotaVenta
from modelos.usuario import Usuario

# Importaciones de vistas
from vistas.clientes.vista_clientes import VistaClientes
from vistas.productos.vista_productos_unificada import VistaProductosUnificada
from vistas.preventistas.vista_preventistas import VistaPreventistas
from vistas.facturacion.vista_facturacion import VistaFacturacion
from vistas.notas_venta.vista_notas_venta import VistaNotasVenta
from vistas.cheques.vista_cheques import VistaCheques
from vistas.parametros.vista_parametros import VistaParametros
from vistas.dashboard.vista_dashboard import VistaDashboard
from vistas.cuenta_corriente.vista_cuenta_corriente import VistaCuentaCorriente
from vistas.rentabilidad.vista_rentabilidad import VistaRentabilidad
from vistas.acerca_de import DialogoAcercaDe
from utilidades.backup_profesional import BackupManagerProfesional, BackupScheduler


# ============================================================
# BOTÓN CON PARPADEO
# ============================================================

class BotonRedondoConParpadeo(QPushButton):
    """Botón circular con capacidad de parpadeo en rojo."""

    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setFixedSize(80, 80)  # ✅ Más grande para 1300x800
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._parpadeando = False
        self._color_normal = "#1565C0"
        self._color_parpadeo = "#D32F2F"
        self._timer_parpadeo = QTimer()
        self._timer_parpadeo.timeout.connect(self._toggle_color)
        self._alternar = False
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color_normal};
                color: white;
                border-radius: 40px;
                font-size: 11px;
                font-weight: bold;
                border: 2px solid #FFC107;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
                border: 2px solid #FFD54F;
            }}
            QPushButton:pressed {{
                background-color: #0D47A1;
            }}
        """)

    def iniciar_parpadeo(self):
        if not self._parpadeando:
            self._parpadeando = True
            self._timer_parpadeo.start(500)

    def detener_parpadeo(self):
        if self._parpadeando:
            self._parpadeando = False
            self._timer_parpadeo.stop()
            self._alternar = False
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._color_normal};
                    color: white;
                    border-radius: 40px;
                    font-size: 11px;
                    font-weight: bold;
                    border: 2px solid #FFC107;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                    border: 2px solid #FFD54F;
                }}
                QPushButton:pressed {{
                    background-color: #0D47A1;
                }}
            """)

    def _toggle_color(self):
        self._alternar = not self._alternar
        if self._alternar:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._color_parpadeo};
                    color: white;
                    border-radius: 40px;
                    font-size: 11px;
                    font-weight: bold;
                    border: 2px solid #FFC107;
                }}
                QPushButton:hover {{
                    background-color: #B71C1C;
                    border: 2px solid #FFD54F;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._color_normal};
                    color: white;
                    border-radius: 40px;
                    font-size: 11px;
                    font-weight: bold;
                    border: 2px solid #FFC107;
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                    border: 2px solid #FFD54F;
                }}
                QPushButton:pressed {{
                    background-color: #0D47A1;
                }}
            """)

    def esta_parpadeando(self):
        return self._parpadeando


class BotonSalir(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("🚪\nSalir")
        self.setFixedSize(70, 70)  # ✅ Más grande
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border-radius: 35px;
                font-size: 11px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)


# ============================================================
# DIÁLOGO DE LOGIN
# ============================================================

class DialogoLogin(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.usuario_modelo = Usuario(db)
        self.setWindowTitle("Iniciar Sesión")
        self.setFixedSize(420, 540)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #1565C0;
                border-radius: 20px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #FFC107;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QPushButton {
                background-color: #FFC107;
                color: #1A237E;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #FFD54F;
            }
            QPushButton:pressed {
                background-color: #FFA000;
            }
            QCheckBox {
                color: #FFFFFF;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid #FFC107;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #FFC107;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(35, 35, 35, 35)

        icono = QLabel("🏢")
        icono.setStyleSheet("font-size: 52px; background-color: transparent; color: #FFC107;")
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icono)

        titulo = QLabel("SISTEMA DE DISTRIBUCIÓN")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFC107; background-color: transparent;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("y Logística")
        subtitulo.setStyleSheet("font-size: 14px; color: #FFFFFF; background-color: transparent;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)
        layout.addSpacing(15)

        lbl_usuario = QLabel("👤 USUARIO")
        lbl_usuario.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 5px; color: #FFFFFF;")
        layout.addWidget(lbl_usuario)
        self.txt_usuario = QLineEdit()
        self.txt_usuario.setPlaceholderText("Ingrese su usuario")
        layout.addWidget(self.txt_usuario)

        lbl_password = QLabel("🔒 CONTRASEÑA")
        lbl_password.setStyleSheet("font-weight: bold; font-size: 12px; margin-top: 10px; color: #FFFFFF;")
        layout.addWidget(lbl_password)
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Ingrese su contraseña")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.txt_password)

        self.chk_ver_password = QCheckBox("👁 Mostrar contraseña")
        self.chk_ver_password.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_ver_password.toggled.connect(self.mostrar_ocultar_password)
        layout.addWidget(self.chk_ver_password)
        layout.addSpacing(20)

        self.btn_login = QPushButton("INGRESAR")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.autenticar)
        layout.addWidget(self.btn_login)

        ayuda = QLabel("📌 Usuario: admin | Contraseña: admin")
        ayuda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ayuda.setStyleSheet("color: #FFC107; font-size: 11px; margin-top: 15px; background-color: transparent;")
        layout.addWidget(ayuda)
        self.usuario_actual = None

    def mostrar_ocultar_password(self, checked):
        if checked:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)

    def autenticar(self):
        username = self.txt_usuario.text().strip()
        password = self.txt_password.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "⚠️ Ingrese usuario y contraseña.")
            return
        usuario = self.usuario_modelo.autenticar(username, password)
        if usuario:
            self.usuario_actual = usuario
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "❌ Usuario o contraseña incorrectos.")
            self.txt_password.clear()
            self.txt_password.setFocus()


# ============================================================
# VENTANA PRINCIPAL
# ============================================================

class VentanaPrincipal(QMainWindow):
    def __init__(self, usuario=None, gif_acerca=None):
        super().__init__()
        print("🚀 Iniciando VentanaPrincipal...")

        self.db = obtener_conexion()
        self.usuario_actual = usuario
        self.nota_modelo = NotaVenta(self.db)
        self.gif_acerca = gif_acerca

        # ========== BACKUP PROFESIONAL ==========
        self.backup_manager = BackupManagerProfesional("distribuidora.db", "backups")
        self.backup_scheduler = BackupScheduler(self.backup_manager)
        self.backup_scheduler.iniciar(hora=3, minuto=0)

        # ========== TÍTULO ==========
        rol_nombre = {
            'admin': 'Administrador',
            'preventista': 'Preventista',
            'cliente': 'Cliente'
        }.get(self.usuario_actual['rol'] if self.usuario_actual else 'admin', 'Usuario')

        self.setWindowTitle(f"Sistema de Distribución y Logística - {rol_nombre}")

        # ✅ NUEVO TAMAÑO: 1300 x 800
        self.resize(1300, 800)
        self.setMinimumSize(1100, 700)

        # ========== ESTILO GENERAL ==========
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F2F5;
            }
            QLabel {
                color: #333333;
            }
            QMenuBar {
                background-color: #1A237E;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QMenuBar::item:selected {
                background-color: #1565C0;
            }
            QMenu {
                background-color: #1A237E;
                color: white;
            }
            QMenu::item:selected {
                background-color: #1565C0;
            }
            QStatusBar {
                background-color: #1A237E;
                color: white;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
            }
        """)

        # ========== MENÚ SUPERIOR ==========
        menu_bar = self.menuBar()

        # Archivo
        menu_archivo = menu_bar.addMenu("📁 Archivo")
        accion_salir = QAction("🚪 Salir", self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)
        menu_archivo.addSeparator()
        accion_cambiar_pass = QAction("🔑 Cambiar Contraseña", self)
        accion_cambiar_pass.triggered.connect(self.cambiar_contrasena)
        menu_archivo.addAction(accion_cambiar_pass)

        # Gestión
        menu_gestion = menu_bar.addMenu("⚙️ Gestión")
        accion_preventistas = QAction("👥 Preventistas", self)
        accion_preventistas.triggered.connect(self.abrir_preventistas)
        menu_gestion.addAction(accion_preventistas)
        accion_cheques = QAction("🏦 Cheques", self)
        accion_cheques.triggered.connect(self.abrir_cheques)
        menu_gestion.addAction(accion_cheques)
        accion_cta_cte = QAction("💰 Cuenta Corriente", self)
        accion_cta_cte.triggered.connect(self.abrir_cuenta_corriente)
        menu_gestion.addAction(accion_cta_cte)

        # Finanzas
        menu_finanzas = menu_bar.addMenu("📊 Finanzas")
        accion_rentabilidad = QAction("📈 Rentabilidad", self)
        accion_rentabilidad.triggered.connect(self.abrir_rentabilidad)
        menu_finanzas.addAction(accion_rentabilidad)

        # Informes
        menu_informes = menu_bar.addMenu("📊 Informes")
        accion_mapa = QAction("🗺️ Mapa de Clientes", self)
        accion_mapa.triggered.connect(self.abrir_mapa)
        menu_informes.addAction(accion_mapa)

        # Configuración
        menu_config = menu_bar.addMenu("🔧 Configuración")
        accion_parametros = QAction("📝 Parámetros", self)
        accion_parametros.triggered.connect(self.abrir_parametros)
        menu_config.addAction(accion_parametros)

        # Herramientas
        menu_herramientas = menu_bar.addMenu("🛠️ Herramientas")
        accion_gestion_backups = QAction("📦 Gestionar Backups", self)
        accion_gestion_backups.triggered.connect(self.abrir_gestion_backups)
        menu_herramientas.addAction(accion_gestion_backups)

        # Ayuda
        menu_ayuda = menu_bar.addMenu("❓ Ayuda")
        accion_acerca = QAction("ℹ️ Acerca de...", self)
        accion_acerca.triggered.connect(self.acerca_de)
        menu_ayuda.addAction(accion_acerca)

        # ========== WIDGET CENTRAL ==========
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QHBoxLayout(central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ========== PANEL LATERAL ==========
        panel = QWidget()
        panel.setFixedWidth(110)  # ✅ Más ancho para 1300x800
        panel.setStyleSheet("background-color: #1A237E;")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        panel_layout.setSpacing(15)
        panel_layout.setContentsMargins(15, 30, 15, 20)

        btn_clientes = BotonRedondoConParpadeo("👥\nClientes")
        btn_productos = BotonRedondoConParpadeo("📦\nProductos")
        self.btn_notas = BotonRedondoConParpadeo("📋\nNotas")
        btn_facturar = BotonRedondoConParpadeo("💰\nFacturar")

        btn_clientes.clicked.connect(self.abrir_clientes)
        btn_productos.clicked.connect(self.abrir_productos)
        self.btn_notas.clicked.connect(self.abrir_notas_venta)
        btn_facturar.clicked.connect(self.abrir_facturacion)
        self.btn_notas.clicked.connect(self.btn_notas.detener_parpadeo)

        panel_layout.addWidget(btn_clientes)
        panel_layout.addWidget(btn_productos)
        panel_layout.addWidget(self.btn_notas)
        panel_layout.addWidget(btn_facturar)

        panel_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        lbl_usuario = QLabel(f"👤\n{self.usuario_actual['username'] if self.usuario_actual else 'admin'}")
        lbl_usuario.setStyleSheet("color: white; background-color: #0D47A1; padding: 10px; border-radius: 10px; font-size: 10px;")
        lbl_usuario.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(lbl_usuario)

        lbl_rol = QLabel(f"🎭\n{rol_nombre}")
        lbl_rol.setStyleSheet("color: #FFC107; font-size: 9px; padding: 5px;")
        lbl_rol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(lbl_rol)

        btn_salir = BotonSalir()
        btn_salir.clicked.connect(self.close)
        panel_layout.addWidget(btn_salir, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout_principal.addWidget(panel)

        # ========== ÁREA CENTRAL ==========
        self.area_central = VistaDashboard(self.db)
        layout_principal.addWidget(self.area_central)

        # ========== BARRA DE ESTADO ==========
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #1A237E; color: white; font-size: 12px; padding: 4px;")
        self.setStatusBar(self.status_bar)
        self.actualizar_barra_estado()

        self.timer_estado = QTimer()
        self.timer_estado.timeout.connect(self.actualizar_estado_completo)
        self.timer_estado.start(10000)

        # Capturar tecla Escape
        self.installEventFilter(self)

        print("✅ VentanaPrincipal inicializada correctamente")
        print(f"📐 Escala activa: {os.environ.get('QT_SCALE_FACTOR', '1.0')}")

    # ============================================================
    # EVENTOS
    # ============================================================

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.timer_estado.stop()
        self.btn_notas.detener_parpadeo()
        reply = QMessageBox.question(
            self, "Backup al salir",
            "¿Desea crear una copia de seguridad antes de salir?\n\n"
            "Se generará un archivo ZIP comprimido con la base de datos.\n"
            "El proceso tomará unos segundos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            from utilidades.backup_splash import realizar_backup_con_splash
            exito = realizar_backup_con_splash(self.backup_manager, self)
            if exito:
                print("✅ Backup realizado exitosamente")
            else:
                print("❌ Error al realizar backup")
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()

    # ============================================================
    # ESTADO Y NOTIFICACIONES
    # ============================================================

    def actualizar_estado_completo(self):
        self.actualizar_barra_estado()
        self.verificar_notas_pendientes()

    def actualizar_barra_estado(self):
        try:
            pendientes = self.nota_modelo.listar_por_estado('PENDIENTE')
            cantidad = len(pendientes)
            if cantidad > 0:
                self.status_bar.showMessage(f"🔔 {cantidad} nota(s) pendiente(s) de facturar")
                self.status_bar.setStyleSheet("background-color: #D32F2F; color: white; font-size: 12px;")
            else:
                self.status_bar.showMessage("✅ Sistema operativo - Sin notas pendientes")
                self.status_bar.setStyleSheet("background-color: #1A237E; color: white; font-size: 12px;")
        except Exception:
            self.status_bar.showMessage("✅ Sistema operativo")

    def verificar_notas_pendientes(self):
        try:
            pendientes = self.nota_modelo.listar_por_estado('PENDIENTE')
            cantidad = len(pendientes)
            if cantidad > 0:
                if not self.btn_notas.esta_parpadeando():
                    self.btn_notas.iniciar_parpadeo()
            else:
                if self.btn_notas.esta_parpadeando():
                    self.btn_notas.detener_parpadeo()
            
            # ✅ También actualizar el dashboard
            if hasattr(self, 'area_central') and hasattr(self.area_central, 'verificar_notas_pendientes'):
                self.area_central.verificar_notas_pendientes()
                
        except Exception:
            pass

    # ============================================================
    # ACTUALIZAR DASHBOARD DESDE VISTAS EXTERNAS
    # ============================================================

    def actualizar_dashboard_desde_vista(self):
        """Actualiza el dashboard cuando se factura una nota desde otra vista."""
        try:
            if hasattr(self, 'area_central') and hasattr(self.area_central, 'cargar_pedidos'):
                self.area_central.cargar_pedidos()
                if hasattr(self.area_central, 'verificar_notas_pendientes'):
                    self.area_central.verificar_notas_pendientes()
                print("✅ Dashboard actualizado desde vista externa")
            
            # También actualizar la barra de estado
            self.actualizar_barra_estado()
            self.verificar_notas_pendientes()
        except Exception as e:
            print(f"⚠️ Error actualizando dashboard: {e}")

    # ============================================================
    # ACCIONES DEL MENÚ
    # ============================================================

    def cambiar_contrasena(self):
        from modelos.usuario import Usuario
        usuario_modelo = Usuario(self.db)
        dialog = QDialog(self)
        dialog.setWindowTitle("Cambiar Contraseña")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 15px;
            }
            QLabel {
                color: #000000;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                padding: 8px;
                color: #000000;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        titulo = QLabel("🔑 Cambiar Contraseña")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        txt_actual = QLineEdit()
        txt_actual.setEchoMode(QLineEdit.EchoMode.Password)
        txt_nueva = QLineEdit()
        txt_nueva.setEchoMode(QLineEdit.EchoMode.Password)
        txt_confirmar = QLineEdit()
        txt_confirmar.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Contraseña actual:", txt_actual)
        form_layout.addRow("Nueva contraseña:", txt_nueva)
        form_layout.addRow("Confirmar nueva:", txt_confirmar)
        layout.addLayout(form_layout)
        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(lambda: self._guardar_contrasena(
            txt_actual.text(), txt_nueva.text(), txt_confirmar.text(), dialog, usuario_modelo
        ))
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)
        dialog.exec()

    def _guardar_contrasena(self, actual, nueva, confirmar, dialog, usuario_modelo):
        if not actual or not nueva:
            QMessageBox.warning(self, "Error", "Complete todos los campos.")
            return
        if nueva != confirmar:
            QMessageBox.warning(self, "Error", "Las contraseñas nuevas no coinciden.")
            return
        if usuario_modelo.cambiar_contrasena(self.usuario_actual['id'], actual, nueva):
            QMessageBox.information(self, "Éxito", "✅ Contraseña cambiada correctamente.")
            dialog.accept()
        else:
            QMessageBox.critical(self, "Error", "❌ Contraseña actual incorrecta.")

    def abrir_gestion_backups(self):
        from vistas.backup.vista_backup import VistaBackup
        dialog = VistaBackup(self.backup_manager, self)
        dialog.exec()

    def acerca_de(self):
        dialog = DialogoAcercaDe(self.gif_acerca, self)
        dialog.exec()

    # ============================================================
    # MÉTODOS PARA ABRIR MÓDULOS
    # ============================================================

    def abrir_clientes(self):
        try:
            dialogo = VistaClientes(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Clientes:\n{str(e)}")

    def abrir_productos(self):
        try:
            dialogo = VistaProductosUnificada(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Productos:\n{str(e)}")

    def abrir_preventistas(self):
        try:
            dialogo = VistaPreventistas(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Preventistas:\n{str(e)}")

    def abrir_facturacion(self):
        try:
            dialogo = VistaFacturacion(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Facturación:\n{str(e)}")

    def abrir_notas_venta(self):
        try:
            dialogo = VistaNotasVenta(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Notas de Venta:\n{str(e)}")

    def abrir_cheques(self):
        try:
            dialogo = VistaCheques(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Cheques:\n{str(e)}")

    def abrir_cuenta_corriente(self):
        try:
            dialogo = VistaCuentaCorriente(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Cuenta Corriente:\n{str(e)}")

    def abrir_rentabilidad(self):
        try:
            dialogo = VistaRentabilidad(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Rentabilidad:\n{str(e)}")

    def abrir_parametros(self):
        try:
            dialogo = VistaParametros(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Parámetros:\n{str(e)}")

    def abrir_mapa(self):
        try:
            from vistas.mapa.vista_mapa import VistaMapa
            dialogo = VistaMapa(self.db, self)
            dialogo.exec()
            self.verificar_notas_pendientes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el mapa:\n{str(e)}")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    
    # Login
    login = DialogoLogin(db)
    if login.exec() == QDialog.DialogCode.Accepted:
        ventana = VentanaPrincipal(login.usuario_actual)
        ventana.show()
        sys.exit(app.exec())
    else:
        sys.exit()