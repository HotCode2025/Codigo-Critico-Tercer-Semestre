"""
Código Crítico - Tercer Semestre Año 2026
Vista para la gestión de Clientes.
Permite altas, bajas, modificaciones y búsqueda.
"""

import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QCheckBox, QHeaderView, QWidget, QGroupBox)
from PySide6.QtCore import Qt
from modelos.cliente import Cliente


class VistaClientes(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.cliente_modelo = Cliente(db)
        self.setWindowTitle("Gestión de Clientes")
        self.resize(900, 600)

        # Layout principal
        layout = QVBoxLayout(self)

        # Grupo de búsqueda
        grupo_busqueda = QGroupBox("Búsqueda")
        busqueda_layout = QHBoxLayout()
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar por CUIT o razón social...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.cargar_clientes)
        busqueda_layout.addWidget(QLabel("Buscar:"))
        busqueda_layout.addWidget(self.txt_buscar)
        busqueda_layout.addWidget(btn_buscar)
        grupo_busqueda.setLayout(busqueda_layout)
        layout.addWidget(grupo_busqueda)

        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Razón Social", "CUIT", "Cond. IVA",
                                              "Límite Créd.", "Saldo CC"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.selectionModel().selectionChanged.connect(self.seleccionar_cliente)
        layout.addWidget(self.tabla)

        # Grupo de formulario
        grupo_form = QGroupBox("Datos del Cliente")
        form_layout = QFormLayout()
        self.txt_razon_social = QLineEdit()
        self.txt_cuit = QLineEdit()
        self.cmb_iva = QLineEdit()  # simplificado, se podría usar QComboBox
        self.txt_domicilio = QLineEdit()
        self.txt_telefono = QLineEdit()
        self.txt_email = QLineEdit()
        self.chk_tasa = QCheckBox("Aplica tasa municipal")
        self.txt_limite = QLineEdit()
        form_layout.addRow("Razón Social:", self.txt_razon_social)
        form_layout.addRow("CUIT:", self.txt_cuit)
        form_layout.addRow("Cond. IVA:", self.cmb_iva)
        form_layout.addRow("Domicilio:", self.txt_domicilio)
        form_layout.addRow("Teléfono:", self.txt_telefono)
        form_layout.addRow("Email:", self.txt_email)
        form_layout.addRow("", self.chk_tasa)
        form_layout.addRow("Límite Crédito:", self.txt_limite)
        grupo_form.setLayout(form_layout)
        layout.addWidget(grupo_form)

        # Botones CRUD
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

        # Conexiones
        self.btn_nuevo.clicked.connect(self.limpiar_formulario)
        self.btn_guardar.clicked.connect(self.guardar_cliente)
        self.btn_modificar.clicked.connect(self.modificar_cliente)
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        # Cargar datos iniciales
        self.cargar_clientes()
        self.cliente_seleccionado_id = None

    def cargar_clientes(self):
        """Carga todos los clientes (o según búsqueda) en la tabla."""
        texto = self.txt_buscar.text().strip()
        if texto:
            # Búsqueda simple
            cur = self.db.cursor()
            cur.execute("SELECT * FROM clientes WHERE razon_social LIKE ? OR cuit LIKE ?",
                        (f"%{texto}%", f"%{texto}%"))
            registros = [dict(row) for row in cur.fetchall()]
        else:
            registros = self.cliente_modelo.listar_todos(solo_activos=False)

        self.tabla.setRowCount(len(registros))
        for fila, cliente in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(cliente['id'])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(cliente['razon_social']))
            self.tabla.setItem(fila, 2, QTableWidgetItem(cliente['cuit'] or ""))
            self.tabla.setItem(fila, 3, QTableWidgetItem(cliente['condicion_iva']))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"${cliente['limite_credito']:,.2f}"))
            self.tabla.setItem(fila, 5, QTableWidgetItem(f"${cliente['saldo_cuenta_corriente']:,.2f}"))

    def seleccionar_cliente(self):
        """Rellena el formulario con los datos del cliente seleccionado."""
        indices = self.tabla.selectedItems()
        if not indices:
            return
        fila = indices[0].row()
        id_cliente = int(self.tabla.item(fila, 0).text())
        self.cliente_seleccionado_id = id_cliente
        cliente = self.cliente_modelo.obtener_por_id(id_cliente)
        if cliente:
            self.txt_razon_social.setText(cliente['razon_social'])
            self.txt_cuit.setText(cliente['cuit'] or "")
            self.cmb_iva.setText(cliente['condicion_iva'])
            self.txt_domicilio.setText(cliente['domicilio'] or "")
            self.txt_telefono.setText(cliente['telefono'] or "")
            self.txt_email.setText(cliente['email'] or "")
            self.chk_tasa.setChecked(bool(cliente['aplica_tasa_municipal']))
            self.txt_limite.setText(str(cliente['limite_credito']))

    def limpiar_formulario(self):
        self.txt_razon_social.clear()
        self.txt_cuit.clear()
        self.cmb_iva.clear()
        self.txt_domicilio.clear()
        self.txt_telefono.clear()
        self.txt_email.clear()
        self.chk_tasa.setChecked(False)
        self.txt_limite.clear()
        self.cliente_seleccionado_id = None

    def guardar_cliente(self):
        """Inserta un nuevo cliente a partir de los campos."""
        try:
            datos = {
                'razon_social': self.txt_razon_social.text().strip(),
                'cuit': self.txt_cuit.text().strip(),
                'condicion_iva': self.cmb_iva.text().strip() or 'RI',
                'domicilio': self.txt_domicilio.text().strip(),
                'telefono': self.txt_telefono.text().strip(),
                'email': self.txt_email.text().strip(),
                'aplica_tasa_municipal': int(self.chk_tasa.isChecked()),
                'limite_credito': float(self.txt_limite.text() or 0)
            }
            if not datos['razon_social']:
                raise ValueError("Razón social es obligatoria.")
            self.cliente_modelo.crear(**datos)
            self.cargar_clientes()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Cliente creado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def modificar_cliente(self):
        """Actualiza el cliente seleccionado."""
        if not self.cliente_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente para modificar.")
            return
        try:
            campos = {
                'razon_social': self.txt_razon_social.text().strip(),
                'cuit': self.txt_cuit.text().strip(),
                'condicion_iva': self.cmb_iva.text().strip(),
                'domicilio': self.txt_domicilio.text().strip(),
                'telefono': self.txt_telefono.text().strip(),
                'email': self.txt_email.text().strip(),
                'aplica_tasa_municipal': int(self.chk_tasa.isChecked()),
                'limite_credito': float(self.txt_limite.text() or 0)
            }
            self.cliente_modelo.actualizar(self.cliente_seleccionado_id, **campos)
            self.cargar_clientes()
            QMessageBox.information(self, "Éxito", "Cliente actualizado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo modificar: {e}")

    def eliminar_cliente(self):
        """Da de baja lógica al cliente."""
        if not self.cliente_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente.")
            return
        confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar cliente seleccionado?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.cliente_modelo.eliminar(self.cliente_seleccionado_id)
            self.cargar_clientes()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Cliente eliminado (baja lógica).")