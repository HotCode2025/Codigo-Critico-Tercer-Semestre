"""
Código Crítico - Tercer Semestre Año 2026
Ventana Principal de la Aplicación.
Interfaz con panel lateral azul oscuro y botones redondos grises.
"""

import sys
from PySide6.QtWidgets import (QMainWindow, QApplication, QStatusBar,
                               QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QSizePolicy, QSpacerItem, QMessageBox)
from PySide6.QtGui import QIcon, QPixmap, QFont, QAction
from PySide6.QtCore import Qt, QSize
from db.db_manager import obtener_conexion
from vistas.clientes.vista_clientes import VistaClientes
from vistas.productos.vista_productos import VistaProductos
from vistas.stock.vista_stock import VistaStock
from vistas.preventistas.vista_preventistas import VistaPreventistas
from vistas.facturacion.vista_facturacion import VistaFacturacion
from vistas.parametros.vista_parametros import VistaParametros
from vistas.reportes.vista_reportes import VistaReportes
from vistas.alertas.vista_alertas import VistaAlertas
from vistas.pdf.vista_pdf import VistaPDF


class BotonRedondo(QPushButton):
    """Botón circular con estilo gris para el panel lateral."""
    def __init__(self, texto, icono=None, parent=None):
        super().__init__(parent)
        self.setText(texto)
        if icono:
            self.setIcon(QIcon(icono))
            self.setIconSize(QSize(32, 32))
        self.setFixedSize(80, 80)
        self.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 40px;
                font-size: 9px;
                font-weight: bold;
                border: 2px solid #7f8c8d;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7d;
            }
        """)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = obtener_conexion()
        self.setWindowTitle("Sistema de Gestión - Distribuidora")
        self.resize(1100, 750)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QHBoxLayout(central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ----- Panel izquierdo (fondo azul oscuro) -----
        panel = QWidget()
        panel.setFixedWidth(100)
        panel.setStyleSheet("background-color: #2c3e50;")   # Azul oscuro
        panel_layout = QVBoxLayout(panel)
        panel_layout.setAlignment(Qt.AlignTop)
        panel_layout.setSpacing(10)
        panel_layout.setContentsMargins(10, 20, 10, 20)

        # Botones de módulos (grises)
        btn_clientes = BotonRedondo("Clientes")
        btn_productos = BotonRedondo("Productos")
        btn_stock = BotonRedondo("Stock")
        btn_preventistas = BotonRedondo("Prevent.")
        btn_facturacion = BotonRedondo("Facturar")
        btn_parametros = BotonRedondo("Parámetros")
        btn_reportes = BotonRedondo("Reportes")
        btn_alertas = BotonRedondo("Alertas")
        btn_pdf = BotonRedondo("Importar\nPDF")

        # Conexiones
        btn_clientes.clicked.connect(self.abrir_clientes)
        btn_productos.clicked.connect(self.abrir_productos)
        btn_stock.clicked.connect(self.abrir_stock)
        btn_preventistas.clicked.connect(self.abrir_preventistas)
        btn_facturacion.clicked.connect(self.abrir_facturacion)
        btn_parametros.clicked.connect(self.abrir_parametros)
        btn_reportes.clicked.connect(self.abrir_reportes)
        btn_alertas.clicked.connect(self.abrir_alertas)
        btn_pdf.clicked.connect(self.abrir_pdf)

        # Agregar al panel
        panel_layout.addWidget(btn_clientes)
        panel_layout.addWidget(btn_productos)
        panel_layout.addWidget(btn_stock)
        panel_layout.addWidget(btn_preventistas)
        panel_layout.addWidget(btn_facturacion)
        panel_layout.addWidget(btn_parametros)
        panel_layout.addWidget(btn_reportes)
        panel_layout.addWidget(btn_alertas)
        panel_layout.addWidget(btn_pdf)

        # Espacio flexible y botón de salida (rojo, para destacar)
        panel_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        btn_salir = QPushButton("Salir")
        btn_salir.setFixedSize(80, 30)
        btn_salir.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_salir.clicked.connect(self.close)
        panel_layout.addWidget(btn_salir, alignment=Qt.AlignHCenter)

        layout_principal.addWidget(panel)

        # ----- Área central (bienvenida y logo) -----
        area_central = QWidget()
        area_central.setStyleSheet("background-color: #ecf0f1;")
        central_layout = QVBoxLayout(area_central)
        central_layout.setAlignment(Qt.AlignCenter)

        # Intentar cargar el logo desde assets
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaledToWidth(250, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("Distribuidora")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
            logo_label.setStyleSheet("color: #2c3e50;")
        logo_label.setAlignment(Qt.AlignCenter)
        central_layout.addWidget(logo_label)

        titulo = QLabel("Sistema de Gestión Integral")
        titulo.setFont(QFont("Arial", 16))
        titulo.setStyleSheet("color: #7f8c8d; margin-top: 20px;")
        titulo.setAlignment(Qt.AlignCenter)
        central_layout.addWidget(titulo)

        layout_principal.addWidget(area_central)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Seleccione un módulo en el panel izquierdo")

    # Slots para abrir cada módulo
    def abrir_clientes(self):
        dialogo = VistaClientes(self.db, self)
        dialogo.exec()

    def abrir_productos(self):
        dialogo = VistaProductos(self.db, self)
        dialogo.exec()

    def abrir_stock(self):
        dialogo = VistaStock(self.db, self)
        dialogo.exec()

    def abrir_preventistas(self):
        dialogo = VistaPreventistas(self.db, self)
        dialogo.exec()

    def abrir_facturacion(self):
        dialogo = VistaFacturacion(self.db, self)
        dialogo.exec()

    def abrir_parametros(self):
        dialogo = VistaParametros(self.db, self)
        dialogo.exec()

    def abrir_reportes(self):
        dialogo = VistaReportes(self.db, self)
        dialogo.exec()

    def abrir_alertas(self):
        dialogo = VistaAlertas(self.db, self)
        dialogo.exec()

    def abrir_pdf(self):
        dialogo = VistaPDF(self.db, self)
        dialogo.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())