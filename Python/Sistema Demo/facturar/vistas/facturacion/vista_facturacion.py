"""
Código Crítico - Tercer Semestre Año 2026
Vista de Facturación. Permite crear facturas a partir de notas de venta o manualmente,
agregar detalles y emitir factura fiscal (actualizando cuenta corriente).
"""

import sqlite3
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QTableWidget,
                               QTableWidgetItem, QMessageBox, QFormLayout,
                               QHeaderView, QGroupBox, QComboBox, QSpinBox)
from PySide6.QtCore import Qt
from modelos.factura import Factura
from modelos.nota_venta import NotaVenta
from modelos.producto import Producto
from modelos.cliente import Cliente
from modelos.preventista import Preventista


class VistaFacturacion(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.factura_modelo = Factura(db)
        self.nota_venta_modelo = NotaVenta(db)
        self.producto_modelo = Producto(db)
        self.cliente_modelo = Cliente(db)
        self.preventista_modelo = Preventista(db)
        self.setWindowTitle("Facturación Fiscal")
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        # Encabezado de factura
        grupo_encabezado = QGroupBox("Encabezado de Factura")
        enc_layout = QFormLayout()
        self.cmb_cliente = QComboBox()
        self.cmb_preventista = QComboBox()
        self.cmb_tipo_comprobante = QComboBox()
        self.cmb_tipo_comprobante.addItems(["A", "B", "C", "X"])
        self.txt_numero_factura = QLineEdit()
        self.cmb_nota_venta = QComboBox()
        self.cmb_nota_venta.addItem("-- Sin nota --", None)
        self._cargar_notas_pendientes()
        self.txt_observaciones = QLineEdit()
        enc_layout.addRow("Cliente:", self.cmb_cliente)
        enc_layout.addRow("Preventista:", self.cmb_preventista)
        enc_layout.addRow("Tipo Comprobante:", self.cmb_tipo_comprobante)
        enc_layout.addRow("Número Factura:", self.txt_numero_factura)
        enc_layout.addRow("Nota de Venta:", self.cmb_nota_venta)
        enc_layout.addRow("Obs.:", self.txt_observaciones)
        grupo_encabezado.setLayout(enc_layout)
        layout.addWidget(grupo_encabezado)

        # Detalle de productos en la factura
        grupo_detalle = QGroupBox("Detalle de Productos")
        det_layout = QVBoxLayout()
        self.tabla_detalle = QTableWidget()
        self.tabla_detalle.setColumnCount(3)
        self.tabla_detalle.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit."])
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        det_layout.addWidget(self.tabla_detalle)

        # Agregar producto al detalle
        agg_layout = QHBoxLayout()
        self.cmb_producto_fact = QComboBox()
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 99999)
        self.btn_agregar_producto = QPushButton("Agregar Producto")
        self.btn_agregar_producto.clicked.connect(self.agregar_producto_detalle)
        agg_layout.addWidget(QLabel("Producto:"))
        agg_layout.addWidget(self.cmb_producto_fact)
        agg_layout.addWidget(QLabel("Cantidad:"))
        agg_layout.addWidget(self.spin_cantidad)
        agg_layout.addWidget(self.btn_agregar_producto)
        det_layout.addLayout(agg_layout)
        grupo_detalle.setLayout(det_layout)
        layout.addWidget(grupo_detalle)

        # Botones finales
        botones_layout = QHBoxLayout()
        self.btn_emitir_factura = QPushButton("Emitir Factura")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_emitir_factura.clicked.connect(self.emitir_factura)
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_emitir_factura)
        botones_layout.addWidget(self.btn_cancelar)
        layout.addLayout(botones_layout)

        # Cargar combos
        self._cargar_clientes()
        self._cargar_preventistas()
        self._cargar_productos()
        self.detalle_temporal = []  # lista de tuplas (id_producto, cantidad, precio)

    def _cargar_clientes(self):
        clientes = self.cliente_modelo.listar_todos(solo_activos=True)
        self.cmb_cliente.clear()
        for c in clientes:
            self.cmb_cliente.addItem(f"{c['razon_social']} (CUIT: {c['cuit']})", c['id'])

    def _cargar_preventistas(self):
        preventistas = self.preventista_modelo.listar_todos(solo_activos=True)
        self.cmb_preventista.clear()
        for p in preventistas:
            self.cmb_preventista.addItem(f"{p['nombre']} {p['apellido']}", p['id'])

    def _cargar_notas_pendientes(self):
        notas = self.nota_venta_modelo.listar_por_estado('PENDIENTE')
        self.cmb_nota_venta.clear()
        self.cmb_nota_venta.addItem("-- Sin nota --", None)
        for n in notas:
            self.cmb_nota_venta.addItem(f"Nota {n['numero_nota']} (ID {n['id']})", n['id'])

    def _cargar_productos(self):
        productos = self.producto_modelo.listar_todos(solo_activos=True)
        self.cmb_producto_fact.clear()
        for prod in productos:
            self.cmb_producto_fact.addItem(f"{prod['codigo']} - {prod['descripcion']}", prod['id'])

    def agregar_producto_detalle(self):
        id_prod = self.cmb_producto_fact.currentData()
        if not id_prod:
            return
        cantidad = self.spin_cantidad.value()
        prod = self.producto_modelo.obtener_por_id(id_prod)
        precio = prod['precio_venta'] if prod else 0.0
        self.detalle_temporal.append((id_prod, cantidad, precio))
        self._refrescar_tabla_detalle()

    def _refrescar_tabla_detalle(self):
        self.tabla_detalle.setRowCount(len(self.detalle_temporal))
        for fila, (id_prod, cant, precio) in enumerate(self.detalle_temporal):
            prod = self.producto_modelo.obtener_por_id(id_prod)
            desc = prod['descripcion'] if prod else "???"
            self.tabla_detalle.setItem(fila, 0, QTableWidgetItem(desc))
            self.tabla_detalle.setItem(fila, 1, QTableWidgetItem(str(cant)))
            self.tabla_detalle.setItem(fila, 2, QTableWidgetItem(f"${precio:,.2f}"))

    def emitir_factura(self):
        try:
            cliente_id = self.cmb_cliente.currentData()
            preventista_id = self.cmb_preventista.currentData()
            tipo = self.cmb_tipo_comprobante.currentText()
            numero = self.txt_numero_factura.text().strip()
            nota_id = self.cmb_nota_venta.currentData()
            observaciones = self.txt_observaciones.text().strip()

            if not cliente_id or not numero:
                raise ValueError("Cliente y número de factura son obligatorios.")
            if not self.detalle_temporal:
                raise ValueError("Debe agregar al menos un producto al detalle.")

            # Crear factura
            factura_id = self.factura_modelo.crear(
                cliente_id=cliente_id,
                numero_factura=numero,
                tipo_comprobante=tipo,
                preventista_id=preventista_id,
                observaciones=observaciones,
                nota_venta_id=nota_id
            )

            # Agregar detalles
            for id_prod, cantidad, precio in self.detalle_temporal:
                self.factura_modelo.agregar_detalle(factura_id, id_prod, cantidad, precio)

            # Recalcular totales (se llama internamente en agregar_detalle, pero se podría forzar)
            # Actualizar estado de nota de venta si corresponde
            if nota_id:
                self.nota_venta_modelo.cambiar_estado(nota_id, 'FACTURADA')

            # También se debería descontar stock (no implementado aquí por simplicidad)
            QMessageBox.information(self, "Éxito", f"Factura {numero} emitida correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo emitir la factura: {e}")