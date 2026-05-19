"""
Código Crítico - Tercer Semestre Año 2026
Vista para la gestión de Productos.
Incluye alta, modificación, baja y búsqueda.
"""

import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox)
from PySide6.QtCore import Qt
from modelos.producto import Producto


class VistaProductos(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.producto_modelo = Producto(db)
        self.setWindowTitle("Gestión de Productos")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        # Búsqueda
        grupo_busqueda = QGroupBox("Búsqueda")
        bus_layout = QHBoxLayout()
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Código o descripción...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.cargar_productos)
        bus_layout.addWidget(QLabel("Buscar:"))
        bus_layout.addWidget(self.txt_buscar)
        bus_layout.addWidget(btn_buscar)
        grupo_busqueda.setLayout(bus_layout)
        layout.addWidget(grupo_busqueda)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Código", "Descripción",
                                              "Costo", "Venta", "Stock"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.selectionModel().selectionChanged.connect(self.seleccionar_producto)
        layout.addWidget(self.tabla)

        # Formulario
        grupo_form = QGroupBox("Datos del Producto")
        form_layout = QFormLayout()
        self.txt_codigo = QLineEdit()
        self.txt_descripcion = QLineEdit()
        self.txt_costo = QLineEdit()
        self.txt_venta = QLineEdit()
        self.txt_stock_critico = QLineEdit()
        self.txt_unidad = QLineEdit()
        form_layout.addRow("Código:", self.txt_codigo)
        form_layout.addRow("Descripción:", self.txt_descripcion)
        form_layout.addRow("Precio Costo:", self.txt_costo)
        form_layout.addRow("Precio Venta:", self.txt_venta)
        form_layout.addRow("Stock Crítico:", self.txt_stock_critico)
        form_layout.addRow("Unidad:", self.txt_unidad)
        grupo_form.setLayout(form_layout)
        layout.addWidget(grupo_form)

        # Botones
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
        self.btn_guardar.clicked.connect(self.guardar_producto)
        self.btn_modificar.clicked.connect(self.modificar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)

        self.producto_seleccionado_id = None
        self.cargar_productos()

    def cargar_productos(self):
        texto = self.txt_buscar.text().strip()
        cur = self.db.cursor()
        if texto:
            cur.execute("""SELECT * FROM productos WHERE activo=1 AND
                           (codigo LIKE ? OR descripcion LIKE ?)""",
                        (f"%{texto}%", f"%{texto}%"))
        else:
            cur.execute("SELECT * FROM productos WHERE activo=1")
        registros = [dict(row) for row in cur.fetchall()]
        self.tabla.setRowCount(len(registros))
        for fila, prod in enumerate(registros):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(prod['id'])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(prod['codigo']))
            self.tabla.setItem(fila, 2, QTableWidgetItem(prod['descripcion']))
            self.tabla.setItem(fila, 3, QTableWidgetItem(f"${prod['precio_costo']:,.2f}"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"${prod['precio_venta']:,.2f}"))
            self.tabla.setItem(fila, 5, QTableWidgetItem(f"{prod['stock_actual']:.2f}"))

    def seleccionar_producto(self):
        indices = self.tabla.selectedItems()
        if not indices:
            return
        fila = indices[0].row()
        id_prod = int(self.tabla.item(fila, 0).text())
        self.producto_seleccionado_id = id_prod
        prod = self.producto_modelo.obtener_por_id(id_prod)
        if prod:
            self.txt_codigo.setText(prod['codigo'])
            self.txt_descripcion.setText(prod['descripcion'])
            self.txt_costo.setText(str(prod['precio_costo']))
            self.txt_venta.setText(str(prod['precio_venta']))
            self.txt_stock_critico.setText(str(prod['stock_critico']))
            self.txt_unidad.setText(prod['unidad_medida'])

    def limpiar_formulario(self):
        self.txt_codigo.clear()
        self.txt_descripcion.clear()
        self.txt_costo.clear()
        self.txt_venta.clear()
        self.txt_stock_critico.clear()
        self.txt_unidad.clear()
        self.producto_seleccionado_id = None

    def guardar_producto(self):
        try:
            datos = {
                'codigo': self.txt_codigo.text().strip(),
                'descripcion': self.txt_descripcion.text().strip(),
                'precio_costo': float(self.txt_costo.text() or 0),
                'precio_venta': float(self.txt_venta.text() or 0),
                'stock_critico': float(self.txt_stock_critico.text() or 0),
                'unidad_medida': self.txt_unidad.text().strip() or 'unidad'
            }
            if not datos['codigo']:
                raise ValueError("El código es obligatorio.")
            self.producto_modelo.crear(**datos)
            self.cargar_productos()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto creado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")

    def modificar_producto(self):
        if not self.producto_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto.")
            return
        try:
            campos = {
                'codigo': self.txt_codigo.text().strip(),
                'descripcion': self.txt_descripcion.text().strip(),
                'precio_costo': float(self.txt_costo.text() or 0),
                'precio_venta': float(self.txt_venta.text() or 0),
                'stock_critico': float(self.txt_stock_critico.text() or 0),
                'unidad_medida': self.txt_unidad.text().strip()
            }
            self.producto_modelo.actualizar(self.producto_seleccionado_id, **campos)
            self.cargar_productos()
            QMessageBox.information(self, "Éxito", "Producto actualizado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo modificar: {e}")

    def eliminar_producto(self):
        if not self.producto_seleccionado_id:
            QMessageBox.warning(self, "Aviso", "Seleccione un producto.")
            return
        confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar producto?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.producto_modelo.eliminar(self.producto_seleccionado_id)
            self.cargar_productos()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Producto eliminado.")