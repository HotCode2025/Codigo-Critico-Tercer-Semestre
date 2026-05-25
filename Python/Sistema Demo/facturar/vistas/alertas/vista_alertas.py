"""
Código Crítico - Tercer Semestre Año 2026
Vista de Alertas. Muestra productos por vencer y clientes con cuenta corriente al límite.
"""

import sqlite3
from datetime import date, timedelta
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QGroupBox)
from PySide6.QtCore import Qt
from modelos.lote import Lote
from modelos.cuenta_corriente import CuentaCorriente


class VistaAlertas(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.lote_modelo = Lote(db)
        self.cc_modelo = CuentaCorriente(db)
        self.setWindowTitle("Alertas del Sistema")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        # Grupo: productos por vencer
        grupo_vencer = QGroupBox("Productos próximos a vencer (14 días)")
        v_layout = QVBoxLayout()
        self.tabla_vencer = QTableWidget()
        self.tabla_vencer.setColumnCount(4)
        self.tabla_vencer.setHorizontalHeaderLabels(["Producto", "N° Lote", "Fecha Venc.", "Stock"])
        self.tabla_vencer.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        v_layout.addWidget(self.tabla_vencer)
        grupo_vencer.setLayout(v_layout)
        layout.addWidget(grupo_vencer)

        # Grupo: clientes al límite
        grupo_limite = QGroupBox("Clientes con cuenta corriente al límite (>80%)")
        l_layout = QVBoxLayout()
        self.tabla_limite = QTableWidget()
        self.tabla_limite.setColumnCount(4)
        self.tabla_limite.setHorizontalHeaderLabels(["Cliente", "Límite", "Saldo", "% Uso"])
        self.tabla_limite.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l_layout.addWidget(self.tabla_limite)
        grupo_limite.setLayout(l_layout)
        layout.addWidget(grupo_limite)

        btn_actualizar = QPushButton("Actualizar Alertas")
        btn_actualizar.clicked.connect(self.cargar_alertas)
        layout.addWidget(btn_actualizar)

        self.cargar_alertas()

    def cargar_alertas(self):
        # Lotes por vencer
        lotes = self.lote_modelo.lotes_por_vencer(dias_anticipacion=14)
        self.tabla_vencer.setRowCount(len(lotes))
        for fila, lote in enumerate(lotes):
            self.tabla_vencer.setItem(fila, 0, QTableWidgetItem(lote['producto_desc']))
            self.tabla_vencer.setItem(fila, 1, QTableWidgetItem(lote['numero_lote'] or ""))
            self.tabla_vencer.setItem(fila, 2, QTableWidgetItem(lote['fecha_vencimiento']))
            self.tabla_vencer.setItem(fila, 3, QTableWidgetItem(f"{lote['cantidad_actual']:.2f}"))

        # Clientes al límite
        clientes = self.cc_modelo.limite_alcanzado(porcentaje_limite=80)
        self.tabla_limite.setRowCount(len(clientes))
        for fila, c in enumerate(clientes):
            self.tabla_limite.setItem(fila, 0, QTableWidgetItem(c['razon_social']))
            self.tabla_limite.setItem(fila, 1, QTableWidgetItem(f"${c['limite_credito']:,.2f}"))
            self.tabla_limite.setItem(fila, 2, QTableWidgetItem(f"${c['saldo_cuenta_corriente']:,.2f}"))
            if c['limite_credito'] > 0:
                porc = (c['saldo_cuenta_corriente'] / c['limite_credito']) * 100
                self.tabla_limite.setItem(fila, 3, QTableWidgetItem(f"{porc:.1f}%"))
            else:
                self.tabla_limite.setItem(fila, 3, QTableWidgetItem("N/A"))