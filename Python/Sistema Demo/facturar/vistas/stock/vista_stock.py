"""
Código Crítico - Tercer Semestre Año 2026
Vista para la gestión de Stock y Lotes.
Permite visualizar el stock actual, crear lotes, y ver productos con stock crítico.
"""

import sqlite3
from datetime import date, timedelta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QComboBox)
from PySide6.QtCore import Qt
from modelos.lote import Lote
from modelos.producto import Producto


class VistaStock(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.lote_modelo = Lote(db)
        self.producto_modelo = Producto(db)
        self.setWindowTitle("Gestión de Stock y Lotes")
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        # Sección superior: productos con stock bajo
        grupo_critico = QGroupBox("Productos con stock bajo mínimo")
        critico_layout = QVBoxLayout()
        self.tabla_criticos = QTableWidget()
        self.tabla_criticos.setColumnCount(3)
        self.tabla_criticos.setHorizontalHeaderLabels(["Producto", "Stock Actual", "Stock Crítico"])
        self.tabla_criticos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        critico_layout.addWidget(self.tabla_criticos)
        grupo_critico.setLayout(critico_layout)
        layout.addWidget(grupo_critico)

        # Sección de lotes
        grupo_lotes = QGroupBox("Lotes por producto")
        lotes_layout = QVBoxLayout()
        self.cmb_producto = QComboBox()
        self.cmb_producto.currentIndexChanged.connect(self.cargar_lotes)
        lotes_layout.addWidget(QLabel("Seleccionar producto:"))
        lotes_layout.addWidget(self.cmb_producto)

        self.tabla_lotes = QTableWidget()
        self.tabla_lotes.setColumnCount(5)
        self.tabla_lotes.setHorizontalHeaderLabels(["ID Lote", "N° Lote", "Fecha Venc.",
                                                    "Cant. Inicial", "Cant. Actual"])
        self.tabla_lotes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lotes_layout.addWidget(self.tabla_lotes)

        # Formulario para crear nuevo lote
        form_lote_layout = QFormLayout()
        self.txt_numero_lote = QLineEdit()
        self.txt_fecha_venc = QLineEdit()
        self.txt_fecha_venc.setPlaceholderText("AAAA-MM-DD")
        self.txt_cantidad = QLineEdit()
        self.btn_crear_lote = QPushButton("Crear Lote")
        self.btn_crear_lote.clicked.connect(self.crear_lote)
        form_lote_layout.addRow("Número de Lote:", self.txt_numero_lote)
        form_lote_layout.addRow("Fecha Vencimiento:", self.txt_fecha_venc)
        form_lote_layout.addRow("Cantidad Inicial:", self.txt_cantidad)
        form_lote_layout.addRow("", self.btn_crear_lote)
        lotes_layout.addLayout(form_lote_layout)

        grupo_lotes.setLayout(lotes_layout)
        layout.addWidget(grupo_lotes)

        # Cargar datos iniciales
        self.cargar_productos()
        self.cargar_stock_critico()
        if self.cmb_producto.count() > 0:
            self.cmb_producto.setCurrentIndex(0)

    def cargar_productos(self):
        self.cmb_producto.clear()
        productos = self.producto_modelo.listar_todos(solo_activos=True)
        for p in productos:
            self.cmb_producto.addItem(f"{p['codigo']} - {p['descripcion']}", p['id'])

    def cargar_stock_critico(self):
        criticos = self.producto_modelo.stock_bajo_minimo()
        self.tabla_criticos.setRowCount(len(criticos))
        for fila, prod in enumerate(criticos):
            self.tabla_criticos.setItem(fila, 0, QTableWidgetItem(prod['descripcion']))
            self.tabla_criticos.setItem(fila, 1, QTableWidgetItem(str(prod['stock_actual'])))
            self.tabla_criticos.setItem(fila, 2, QTableWidgetItem(str(prod['stock_critico'])))

    def cargar_lotes(self):
        id_producto = self.cmb_producto.currentData()
        if id_producto is None:
            self.tabla_lotes.setRowCount(0)
            return
        lotes = self.lote_modelo.listar_por_producto(id_producto)
        self.tabla_lotes.setRowCount(len(lotes))
        for fila, lote in enumerate(lotes):
            self.tabla_lotes.setItem(fila, 0, QTableWidgetItem(str(lote['id'])))
            self.tabla_lotes.setItem(fila, 1, QTableWidgetItem(lote['numero_lote'] or ""))
            self.tabla_lotes.setItem(fila, 2, QTableWidgetItem(lote['fecha_vencimiento']))
            self.tabla_lotes.setItem(fila, 3, QTableWidgetItem(f"{lote['cantidad_inicial']:.2f}"))
            self.tabla_lotes.setItem(fila, 4, QTableWidgetItem(f"{lote['cantidad_actual']:.2f}"))

    def crear_lote(self):
        id_producto = self.cmb_producto.currentData()
        if not id_producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto.")
            return
        numero = self.txt_numero_lote.text().strip()
        fecha_venc = self.txt_fecha_venc.text().strip()
        cantidad = self.txt_cantidad.text().strip()
        if not fecha_venc or not cantidad:
            QMessageBox.warning(self, "Error", "Complete fecha de vencimiento y cantidad.")
            return
        try:
            fecha_valida = date.fromisoformat(fecha_venc)
            cantidad_valida = float(cantidad)
        except ValueError:
            QMessageBox.critical(self, "Error", "Formato de fecha o cantidad inválido.")
            return
        try:
            self.lote_modelo.crear(producto_id=id_producto, numero_lote=numero,
                                   fecha_vencimiento=fecha_venc, cantidad_inicial=cantidad_valida)
            self.cargar_lotes()
            self.cargar_stock_critico()
            self.txt_numero_lote.clear()
            self.txt_fecha_venc.clear()
            self.txt_cantidad.clear()
            QMessageBox.information(self, "Éxito", "Lote creado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el lote: {e}")