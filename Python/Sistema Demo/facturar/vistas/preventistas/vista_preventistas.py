"""
Código Crítico - Tercer Semestre Año 2026
Vista para la gestión de Preventistas.
"""

import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox)
from PySide6.QtCore import Qt
from modelos.preventista import Preventista


class VistaPreventistas(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.preventista_modelo = Preventista(db)
        self.setWindowTitle("Gestión de Preventistas")
        self.resize(800, 500)

        layout = QVBoxLayout(self)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Legajo", "Zona"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.selectionModel().selectionChanged.connect(self.seleccionar_preventista)
        layout.addWidget(self.tabla)

        # Formulario
        grupo_form = QGroupBox("Datos del Preventista")
        form_layout = QFormLayout()
        self.txt_nombre = QLineEdit()
        self.txt_apellido = QLineEdit()
        self.txt_legajo = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_zona = QLineEdit()
        form_layout.addRow("Nombre:", self.txt_nombre)
        form_layout.addRow("Apellido:", self.txt_apellido)
        form_layout.addRow("Legajo:", self.txt_legajo)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Email:", self.txt_email)
        form_layout.addRow("Zona:", self.txt_zona)
        grupo_form.setLayout(form_layout)
        layout.addWidget(grupo_form)

        botones_layout = QHBoxLayout()
        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_guardar = QPushButton("Guardar")
        self.btn_modificar = QPushButton("Modificar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_limpiar = QPushButton("Limpiar")
        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_guardar)
        botones_layout.addWidget(self.btn_modificar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addWidget(self.btn_limpiar)
        layout.addLayout(botones_layout)

        self.btn_nuevo.clicked.connect(self.limpiar_formulario)
        self.btn_guardar.clicked.connect(self.guardar_preventista)
        self.btn_modificar.clicked.connect(self.modificar_preventista)
        self.btn_eliminar.clicked.connect(self.eliminar_preventista)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self.preventista_seleccionado_id = None
        self.cargar_preventistas()

    def cargar_preventistas(self):
        preventistas = self.preventista_modelo.listar_todos(solo_activos=False)
        self.tabla.setRowCount(len(preventistas))
        for fila, p in enumerate(preventistas):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(p['id'])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(p['nombre']))
            self.tabla.setItem(fila, 2, QTableWidgetItem(p['apellido']))
            self.tabla.setItem(fila, 3, QTableWidgetItem(p['legajo'] or ""))
            self.tabla.setItem(fila, 4, QTableWidgetItem(p['zona'] or ""))

    def seleccionar_preventista(self):
        indices = self.tabla.selectedItems()
        if not indices:
            return
        fila = indices[0].row()
        id_prev = int(self.tabla.item(fila, 0).text())
        self.preventista_seleccionado_id = id_prev
        prev = self.preventista_modelo.obtener_por_id(id_prev)
        if prev:
            self.txt_nombre.setText(prev['nombre'])
            self.txt_apellido.setText(prev['apellido'])
            self.txt_legajo.setText(prev['legajo'] or "")
            self.txt_telefono.setText(prev['telefono'] or "")
            self.txt_email.setText(prev['email'] or "")
            self.txt_zona.setText(prev['zona'] or "")

    def limpiar_formulario(self):
        self.txt_nombre.clear()
        self.txt_apellido.clear()
        self.txt_legajo.clear()
        self.txt_telefono.clear()
        self.txt_email.clear()
        self.txt_zona.clear()
        self.preventista_seleccionado_id = None

    def guardar_preventista(self):
        try:
            datos = {
                'nombre': self.txt_nombre.text().strip(),
                'apellido': self.txt_apellido.text().strip(),
                'legajo': self.txt_legajo.text().strip(),
                'telefono': self.txt_telefono.text().strip(),
                'email': self.txt_email.text().strip(),
                'zona': self.txt_zona.text().strip()
            }
            if not datos['nombre'] or not datos['apellido']:
                raise ValueError("Nombre y apellido son obligatorios.")
            self.preventista_modelo.crear(**datos)
            self.cargar_preventistas()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Preventista creado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def modificar_preventista(self):
        if not self.preventista_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un preventista.")
            return
        try:
            campos = {
                'nombre': self.txt_nombre.text().strip(),
                'apellido': self.txt_apellido.text().strip(),
                'legajo': self.txt_legajo.text().strip(),
                'telefono': self.txt_telefono.text().strip(),
                'email': self.txt_email.text().strip(),
                'zona': self.txt_zona.text().strip()
            }
            self.preventista_modelo.actualizar(self.preventista_seleccionado_id, **campos)
            self.cargar_preventistas()
            QMessageBox.information(self, "Éxito", "Preventista actualizado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo modificar: {e}")

    def eliminar_preventista(self):
        if not self.preventista_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un preventista.")
            return
        confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar preventista?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.preventista_modelo.eliminar(self.preventista_seleccionado_id)
            self.cargar_preventistas()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Preventista eliminado.")