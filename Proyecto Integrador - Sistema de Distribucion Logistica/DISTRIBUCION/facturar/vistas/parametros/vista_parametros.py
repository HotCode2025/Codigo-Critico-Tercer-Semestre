"""
Código Crítico - Tercer Semestre Año 2026
Vista de Parámetros – Con solapas AZULES.
"""

import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QGroupBox, QFrame, QFileDialog, 
                               QMessageBox, QTabWidget, QWidget, QGridLayout)
from PyQt6.QtCore import Qt

from utilidades.geocodificar import obtener_coordenadas


class LabelSeccionAzul(QLabel):
    """Título de sección - Azul marino, blanco, centrado"""
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(36)
        self.setStyleSheet("""
            QLabel {
                background-color: #1A237E;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 16px;
            }
        """)


class LabelCampoAzul(QLabel):
    """Etiqueta de campo - Azul intenso, blanco, alineado a la izquierda"""
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #1565C0;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 6px 12px;
            }
        """)


class LineEditBlanco(QLineEdit):
    """Campo de texto - Blanco con borde negro"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 11px;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #1565C0;
            }
        """)


class VistaParametros(QDialog):
    """Diálogo modal para editar los parámetros del sistema."""

    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Parámetros del Sistema")
        self.resize(700, 650)
        self.setMinimumSize(650, 600)

        # ✅ ESTILO CON TABS AZULES
        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QGroupBox {
                border: none;
                background-color: transparent;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 11px;
                border: none;
                min-height: 34px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTabWidget::pane {
                border: 1px solid #B0BEC5;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1565C0;
                color: white;
                padding: 8px 22px;
                font-weight: bold;
                font-size: 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0D47A1;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #1976D2;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Tarjeta contenedora
        tarjeta = QFrame()
        tarjeta.setStyleSheet(
            "QFrame { background-color: #E0E0E0; border-radius: 10px; border: 1px solid #D0D0D0; }"
        )
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(12, 12, 12, 12)

        # ========== PESTAÑAS ==========
        tabs = QTabWidget()
        
        # ----- PESTAÑA 1: DATOS DE LA EMPRESA -----
        tab_empresa = QWidget()
        empresa_layout = QVBoxLayout(tab_empresa)
        empresa_layout.setContentsMargins(15, 15, 15, 15)
        empresa_layout.setSpacing(15)

        empresa_layout.addWidget(LabelSeccionAzul("🏢 DATOS DE LA EMPRESA"))

        form_empresa = QGridLayout()
        form_empresa.setSpacing(12)
        form_empresa.setHorizontalSpacing(15)

        self.txt_nombre = LineEditBlanco()
        self.txt_telefono1 = LineEditBlanco()
        self.txt_telefono2 = LineEditBlanco()
        self.txt_whatsapp = LineEditBlanco()
        self.txt_email = LineEditBlanco()
        self.txt_moneda = LineEditBlanco()
        self.txt_moneda.setText("ARS")

        form_empresa.addWidget(LabelCampoAzul("Nombre:"), 0, 0)
        form_empresa.addWidget(self.txt_nombre, 0, 1)
        
        form_empresa.addWidget(LabelCampoAzul("Teléfono 1:"), 1, 0)
        form_empresa.addWidget(self.txt_telefono1, 1, 1)
        
        form_empresa.addWidget(LabelCampoAzul("Teléfono 2:"), 2, 0)
        form_empresa.addWidget(self.txt_telefono2, 2, 1)
        
        form_empresa.addWidget(LabelCampoAzul("WhatsApp:"), 3, 0)
        form_empresa.addWidget(self.txt_whatsapp, 3, 1)
        
        form_empresa.addWidget(LabelCampoAzul("Email:"), 4, 0)
        form_empresa.addWidget(self.txt_email, 4, 1)
        
        form_empresa.addWidget(LabelCampoAzul("Moneda:"), 5, 0)
        form_empresa.addWidget(self.txt_moneda, 5, 1)

        empresa_layout.addLayout(form_empresa)

        # ----- PESTAÑA 2: DIRECCIÓN -----
        tab_direccion = QWidget()
        direccion_layout = QVBoxLayout(tab_direccion)
        direccion_layout.setContentsMargins(15, 15, 15, 15)
        direccion_layout.setSpacing(15)

        direccion_layout.addWidget(LabelSeccionAzul("📍 DIRECCIÓN"))

        form_direccion = QGridLayout()
        form_direccion.setSpacing(12)
        form_direccion.setHorizontalSpacing(15)

        self.txt_calle = LineEditBlanco()
        self.txt_numero = LineEditBlanco()
        self.txt_localidad = LineEditBlanco()
        self.txt_provincia = LineEditBlanco()
        self.txt_pais = LineEditBlanco()
        self.txt_pais.setText("Argentina")

        form_direccion.addWidget(LabelCampoAzul("Calle:"), 0, 0)
        form_direccion.addWidget(self.txt_calle, 0, 1)
        
        form_direccion.addWidget(LabelCampoAzul("Número:"), 1, 0)
        form_direccion.addWidget(self.txt_numero, 1, 1)
        
        form_direccion.addWidget(LabelCampoAzul("Localidad:"), 2, 0)
        form_direccion.addWidget(self.txt_localidad, 2, 1)
        
        form_direccion.addWidget(LabelCampoAzul("Provincia:"), 3, 0)
        form_direccion.addWidget(self.txt_provincia, 3, 1)
        
        form_direccion.addWidget(LabelCampoAzul("País:"), 4, 0)
        form_direccion.addWidget(self.txt_pais, 4, 1)

        direccion_layout.addLayout(form_direccion)

        btn_geolocalizar = QPushButton("📍 Geolocalizar Dirección")
        btn_geolocalizar.setMinimumHeight(34)
        btn_geolocalizar.clicked.connect(self.geolocalizar_direccion)
        direccion_layout.addWidget(btn_geolocalizar)

        # Coordenadas
        grupo_coords = QGroupBox()
        grupo_coords.setStyleSheet("""
            QGroupBox {
                border: 1px solid #B0BEC5;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #1A237E;
                left: 10px;
            }
        """)
        grupo_coords.setTitle("Coordenadas (automáticas)")
        coords_layout = QGridLayout()
        coords_layout.setSpacing(12)
        coords_layout.setHorizontalSpacing(15)
        
        self.txt_latitud = LineEditBlanco()
        self.txt_latitud.setReadOnly(True)
        self.txt_longitud = LineEditBlanco()
        self.txt_longitud.setReadOnly(True)
        
        coords_layout.addWidget(LabelCampoAzul("Latitud:"), 0, 0)
        coords_layout.addWidget(self.txt_latitud, 0, 1)
        coords_layout.addWidget(LabelCampoAzul("Longitud:"), 1, 0)
        coords_layout.addWidget(self.txt_longitud, 1, 1)
        
        grupo_coords.setLayout(coords_layout)
        direccion_layout.addWidget(grupo_coords)

        tabs.addTab(tab_empresa, "🏢 DATOS DE LA EMPRESA")
        tabs.addTab(tab_direccion, "📍 DIRECCIÓN")

        # ----- PESTAÑA 3: FACTURACIÓN -----
        tab_facturacion = QWidget()
        facturacion_layout = QVBoxLayout(tab_facturacion)
        facturacion_layout.setContentsMargins(15, 15, 15, 15)
        facturacion_layout.setSpacing(15)

        facturacion_layout.addWidget(LabelSeccionAzul("📄 FACTURACIÓN"))

        form_facturacion = QGridLayout()
        form_facturacion.setSpacing(12)
        form_facturacion.setHorizontalSpacing(15)

        self.txt_enc_factura = LineEditBlanco()
        self.txt_enc_reporte = LineEditBlanco()
        self.txt_tasa = LineEditBlanco()
        self.txt_punto_venta = LineEditBlanco()
        self.txt_punto_venta.setInputMask("9999")
        self.txt_ultimo_numero = LineEditBlanco()
        self.txt_ultimo_numero.setInputMask("99999999")

        form_facturacion.addWidget(LabelCampoAzul("Encabezado Factura:"), 0, 0)
        form_facturacion.addWidget(self.txt_enc_factura, 0, 1)
        
        form_facturacion.addWidget(LabelCampoAzul("Encabezado Reportes:"), 1, 0)
        form_facturacion.addWidget(self.txt_enc_reporte, 1, 1)
        
        form_facturacion.addWidget(LabelCampoAzul("Tasa Municipal (%):"), 2, 0)
        form_facturacion.addWidget(self.txt_tasa, 2, 1)
        
        form_facturacion.addWidget(LabelCampoAzul("Punto de Venta:"), 3, 0)
        form_facturacion.addWidget(self.txt_punto_venta, 3, 1)
        
        form_facturacion.addWidget(LabelCampoAzul("Próximo N° Factura:"), 4, 0)
        form_facturacion.addWidget(self.txt_ultimo_numero, 4, 1)

        facturacion_layout.addLayout(form_facturacion)

        tabs.addTab(tab_facturacion, "📄 FACTURACIÓN")

        tarjeta_layout.addWidget(tabs)

        # ========== LOGO ==========
        btn_logo = QPushButton("🖼️ Cargar Logo")
        btn_logo.setMinimumHeight(34)
        btn_logo.clicked.connect(self.cargar_logo)
        tarjeta_layout.addWidget(btn_logo)

        # ========== BOTONES ==========
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setMinimumHeight(38)
        btn_guardar.clicked.connect(self.guardar_parametros)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setMinimumHeight(38)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addStretch()
        
        tarjeta_layout.addLayout(botones_layout)

        layout.addWidget(tarjeta)

        self.cargar_datos()

    def _mostrar_mensaje(self, titulo, texto, icono=QMessageBox.Icon.Information, botones=QMessageBox.StandardButton.Ok):
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setIcon(icono)
        msg.setStandardButtons(botones)
        msg.exec()

    def cargar_datos(self):
        cur = self.db.cursor()
        
        cur.execute("SELECT COUNT(*) FROM parametros WHERE id = 1")
        if cur.fetchone()[0] == 0:
            self.db.execute("INSERT INTO parametros (id, moneda, nombre_distribuidora) VALUES (1, 'ARS', 'Mi Distribuidora')")
            self.db.commit()
        
        cur.execute("SELECT * FROM parametros WHERE id = 1")
        row = cur.fetchone()
        
        if row:
            self.txt_nombre.setText(row['nombre_distribuidora'] or '')
            self.txt_telefono1.setText(row['telefono1'] or '')
            self.txt_telefono2.setText(row['telefono2'] or '')
            self.txt_whatsapp.setText(row['whatsapp'] or '')
            self.txt_email.setText(row['email'] or '')
            self.txt_moneda.setText(row['moneda'] or 'ARS')
            
            self.txt_calle.setText(row['calle'] or '')
            self.txt_numero.setText(row['numero'] or '')
            self.txt_localidad.setText(row['localidad'] or '')
            self.txt_provincia.setText(row['provincia'] or '')
            self.txt_pais.setText(row['pais'] or 'Argentina')
            
            self.txt_latitud.setText(str(row['latitud']) if row['latitud'] else '')
            self.txt_longitud.setText(str(row['longitud']) if row['longitud'] else '')
            
            self.txt_enc_factura.setText(row['encabezado_factura'] or '')
            self.txt_enc_reporte.setText(row['encabezado_reporte'] or '')
            self.txt_tasa.setText(str(row['tasa_municipal_porcentaje'] or 0))
            self.txt_punto_venta.setText(row['punto_venta'] or '0001')
            self.txt_ultimo_numero.setText(str(row['ultimo_numero_factura'] or 1))

    def geolocalizar_direccion(self):
        calle = self.txt_calle.text().strip()
        numero = self.txt_numero.text().strip()
        localidad = self.txt_localidad.text().strip()
        provincia = self.txt_provincia.text().strip()
        
        if not calle or not localidad:
            self._mostrar_mensaje("Error", "Complete calle y localidad.", QMessageBox.Icon.Warning)
            return
        
        lat, lon = obtener_coordenadas(calle, numero, localidad, provincia)
        
        if lat and lon:
            self.txt_latitud.setText(f"{lat:.6f}")
            self.txt_longitud.setText(f"{lon:.6f}")
            self._mostrar_mensaje("Éxito", "Dirección geolocalizada correctamente.")
        else:
            self._mostrar_mensaje("Error", "No se pudo geolocalizar.", QMessageBox.Icon.Warning)

    def cargar_logo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.bmp)")
        if archivo:
            with open(archivo, 'rb') as f:
                datos = f.read()
            self.db.execute("UPDATE parametros SET logo = ? WHERE id = 1", (datos,))
            self.db.commit()
            self._mostrar_mensaje("Éxito", "Logo cargado correctamente.")

    def guardar_parametros(self):
        try:
            lat = None
            lon = None
            if self.txt_latitud.text().strip():
                try:
                    lat = float(self.txt_latitud.text().strip())
                    lon = float(self.txt_longitud.text().strip())
                except:
                    pass
            
            if not lat and self.txt_calle.text().strip() and self.txt_localidad.text().strip():
                calle = self.txt_calle.text().strip()
                numero = self.txt_numero.text().strip()
                localidad = self.txt_localidad.text().strip()
                provincia = self.txt_provincia.text().strip()
                lat, lon = obtener_coordenadas(calle, numero, localidad, provincia)
                if lat and lon:
                    self.txt_latitud.setText(f"{lat:.6f}")
                    self.txt_longitud.setText(f"{lon:.6f}")
            
            self.db.execute("""
                UPDATE parametros SET
                    nombre_distribuidora = ?,
                    telefono1 = ?,
                    telefono2 = ?,
                    whatsapp = ?,
                    email = ?,
                    moneda = ?,
                    calle = ?,
                    numero = ?,
                    localidad = ?,
                    provincia = ?,
                    pais = ?,
                    latitud = ?,
                    longitud = ?,
                    encabezado_factura = ?,
                    encabezado_reporte = ?,
                    tasa_municipal_porcentaje = ?,
                    punto_venta = ?,
                    ultimo_numero_factura = ?
                WHERE id = 1
            """, (
                self.txt_nombre.text().strip(),
                self.txt_telefono1.text().strip(),
                self.txt_telefono2.text().strip(),
                self.txt_whatsapp.text().strip(),
                self.txt_email.text().strip(),
                self.txt_moneda.text().strip() or 'ARS',
                self.txt_calle.text().strip(),
                self.txt_numero.text().strip(),
                self.txt_localidad.text().strip(),
                self.txt_provincia.text().strip(),
                self.txt_pais.text().strip() or 'Argentina',
                lat,
                lon,
                self.txt_enc_factura.text().strip(),
                self.txt_enc_reporte.text().strip(),
                float(self.txt_tasa.text() or 0),
                self.txt_punto_venta.text().strip() or '0001',
                int(self.txt_ultimo_numero.text() or 1),
            ))
            self.db.commit()
            
            self._mostrar_mensaje("Éxito", "Parámetros guardados correctamente.")
            self.accept()
            
        except Exception as e:
            self._mostrar_mensaje("Error", f"No se pudo guardar: {e}", QMessageBox.Icon.Critical)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaParametros(db)
    ventana.show()
    sys.exit(app.exec())