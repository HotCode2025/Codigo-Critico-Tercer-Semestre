"""
Código Crítico - Tercer Semestre Año 2026
Vista de Parámetros Generales. Permite editar la configuración única del sistema.
"""

import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFormLayout,
                               QGroupBox, QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class VistaParametros(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Parámetros del Sistema")
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        grupo = QGroupBox("Configuración General")
        form = QFormLayout()

        # Cargar registro existente (id=1)
        cur = self.db.cursor()
        cur.execute("SELECT * FROM parametros WHERE id = 1")
        row = cur.fetchone()
        if row is None:
            # Insertar fila por defecto
            self.db.execute("""INSERT INTO parametros (id, moneda, nombre_distribuidora)
                               VALUES (1, 'ARS', 'Distribuidora Ejemplo')""")
            self.db.commit()
            cur.execute("SELECT * FROM parametros WHERE id = 1")
            row = cur.fetchone()
        params = dict(row)

        self.txt_nombre = QLineEdit(params.get('nombre_distribuidora', ''))
        self.txt_moneda = QLineEdit(params.get('moneda', 'ARS'))
        self.txt_telefono1 = QLineEdit(params.get('telefono1', ''))
        self.txt_telefono2 = QLineEdit(params.get('telefono2', ''))
        self.txt_whatsapp = QLineEdit(params.get('whatsapp', ''))
        self.txt_email = QLineEdit(params.get('email', ''))
        self.txt_enc_factura = QLineEdit(params.get('encabezado_factura', ''))
        self.txt_enc_reporte = QLineEdit(params.get('encabezado_reporte', ''))
        self.txt_tasa = QLineEdit(str(params.get('tasa_municipal_porcentaje', 0.0)))

        form.addRow("Nombre Distribuidora:", self.txt_nombre)
        form.addRow("Moneda:", self.txt_moneda)
        form.addRow("Teléfono 1:", self.txt_telefono1)
        form.addRow("Teléfono 2:", self.txt_telefono2)
        form.addRow("WhatsApp:", self.txt_whatsapp)
        form.addRow("Email:", self.txt_email)
        form.addRow("Encabezado Factura:", self.txt_enc_factura)
        form.addRow("Encabezado Reportes:", self.txt_enc_reporte)
        form.addRow("Tasa Municipal (%):", self.txt_tasa)

        grupo.setLayout(form)
        layout.addWidget(grupo)

        # Botón para cambiar logo (no implementado completamente)
        btn_logo = QPushButton("Cargar Logo")
        btn_logo.clicked.connect(self.cargar_logo)
        layout.addWidget(btn_logo)

        # Botón guardar
        btn_guardar = QPushButton("Guardar Configuración")
        btn_guardar.clicked.connect(self.guardar_parametros)
        layout.addWidget(btn_guardar)

    def cargar_logo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo",
                                                  "", "Imágenes (*.png *.jpg *.bmp)")
        if archivo:
            with open(archivo, 'rb') as f:
                datos = f.read()
            self.db.execute("UPDATE parametros SET logo = ? WHERE id = 1", (datos,))
            self.db.commit()
            QMessageBox.information(self, "Éxito", "Logo cargado correctamente.")

    def guardar_parametros(self):
        try:
            self.db.execute("""UPDATE parametros SET
                                moneda = ?,
                                nombre_distribuidora = ?,
                                telefono1 = ?,
                                telefono2 = ?,
                                whatsapp = ?,
                                email = ?,
                                encabezado_factura = ?,
                                encabezado_reporte = ?,
                                tasa_municipal_porcentaje = ?
                               WHERE id = 1""",
                            (self.txt_moneda.text().strip(),
                             self.txt_nombre.text().strip(),
                             self.txt_telefono1.text().strip(),
                             self.txt_telefono2.text().strip(),
                             self.txt_whatsapp.text().strip(),
                             self.txt_email.text().strip(),
                             self.txt_enc_factura.text().strip(),
                             self.txt_enc_reporte.text().strip(),
                             float(self.txt_tasa.text() or 0)))
            self.db.commit()
            QMessageBox.information(self, "Éxito", "Parámetros guardados.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")