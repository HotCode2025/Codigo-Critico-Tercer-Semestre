"""
Código Crítico - Tercer Semestre Año 2026
Vista de Mapa - Clientes y rutas óptimas
Rediseñada 1100x700 con solapas AZULES.
3 Solapas: Mapa, Lista de Clientes, Ruta Óptima.
SIN BOTONES DE IMPRIMIR.
"""

import sqlite3
import os
import csv
import math
import json
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QComboBox, QGroupBox, QMessageBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFileDialog, QProgressBar, QWidget, QApplication,
                               QCheckBox, QTabWidget, QTextEdit, QFrame,
                               QLineEdit)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QColor
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter

from modelos.cliente import Cliente
from modelos.preventista import Preventista
from utilidades.geocodificar import obtener_coordenadas


# ==================== CLASES DE ESTILO ====================

class LabelSeccionAzul(QLabel):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(28)
        self.setStyleSheet("""
            QLabel {
                background-color: #1A237E;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 4px 10px;
            }
        """)


class LabelCampoAzul(QLabel):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10px;
                padding: 4px 6px;
            }
        """)


class LineEditBlanco(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
            QLineEdit:focus {
                border-color: #1565C0;
            }
        """)


class ComboBlanco(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #000000;
                selection-background-color: #1565C0;
                selection-color: white;
            }
        """)


class CheckBoxBlanco(QCheckBox):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: #000000;
                background-color: #FFFFFF;
                spacing: 6px;
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #000000;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 2px solid #1565C0;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #1565C0;
            }
        """)


# ==================== HILO DE GEOLOCALIZACIÓN ====================

class GeocodingThread(QThread):
    finished = pyqtSignal(object, object, int)
    
    def __init__(self, cliente_id, calle, numero, localidad, provincia):
        super().__init__()
        self.cliente_id = cliente_id
        self.calle = calle
        self.numero = numero
        self.localidad = localidad
        self.provincia = provincia
    
    def run(self):
        lat, lon = obtener_coordenadas(self.calle, self.numero, self.localidad, self.provincia)
        self.finished.emit(lat, lon, self.cliente_id)


class DialogoGeolocalizacion(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geolocalizando clientes")
        self.setFixedSize(400, 150)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                height: 20px;
                background-color: #E0E0E0;
            }
            QProgressBar::chunk {
                background-color: #1565C0;
                border-radius: 5px;
            }
            QLabel {
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        self.lbl_mensaje = QLabel("🌍 Procesando clientes...")
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mensaje.setStyleSheet("color: #000000; font-size: 12px;")
        layout.addWidget(self.lbl_mensaje)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, total)
        layout.addWidget(self.progress)
        
        self.lbl_contador = QLabel(f"0 / {total}")
        self.lbl_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_contador.setStyleSheet("color: #000000;")
        layout.addWidget(self.lbl_contador)
    
    def actualizar(self, actual, total, cliente_nombre):
        self.progress.setValue(actual)
        self.lbl_contador.setText(f"{actual} / {total}")
        self.lbl_mensaje.setText(f"📍 Procesando: {cliente_nombre[:40]}...")
        self.repaint()
    
    def cerrar(self):
        QTimer.singleShot(500, self.accept)


# ==================== VISTA PRINCIPAL ====================

class VistaMapa(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.cliente_modelo = Cliente(db)
        self.preventista_modelo = Preventista(db)
        
        self.setWindowTitle("Mapa de Clientes - Rutas Óptimas")
        self.setFixedSize(1100, 700)

        # ✅ ESTILO CON TABS AZULES
        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QTabWidget::pane {
                border: 1px solid #B0BEC5;
                background: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1565C0;
                color: white;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 10px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0D47A1;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #1976D2;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-size: 9px;
                gridline-color: #A0A0A0;
                alternate-background-color: #F8F9FA;
            }
            QTableWidget::item {
                background-color: transparent;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #1565C0;
                color: white;
            }
            QHeaderView::section {
                background-color: #1565C0;
                color: white;
                padding: 5px;
                font-weight: 600;
                border: none;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #0D47A1;
            }
            QHeaderView::section:vertical {
                border-bottom: 1px solid #0D47A1;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QFrame {
                background-color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
            QWebEngineView {
                background-color: white;
                border-radius: 6px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 10px;
                color: #000000;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #000000;
                selection-background-color: #1565C0;
                selection-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(8, 8, 8, 8)
        tarjeta_layout.setSpacing(5)

        # ========== FILTROS ==========
        frame_filtros = QFrame()
        frame_filtros.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        filtros_layout = QHBoxLayout(frame_filtros)
        filtros_layout.setContentsMargins(10, 8, 10, 8)
        filtros_layout.setSpacing(10)

        filtros_layout.addWidget(QLabel("Preventista:"))
        self.cmb_preventista = ComboBlanco()
        self.cmb_preventista.setMinimumWidth(200)
        self.cmb_preventista.currentIndexChanged.connect(self.filtrar_clientes)
        filtros_layout.addWidget(self.cmb_preventista)

        filtros_layout.addStretch()

        self.chk_ruta_optima = CheckBoxBlanco("🗺️ Ruta desde distribuidora")
        self.chk_ruta_optima.setChecked(False)
        self.chk_ruta_optima.toggled.connect(self.filtrar_clientes)
        filtros_layout.addWidget(self.chk_ruta_optima)

        self.btn_geolocalizar = QPushButton("📍 Geolocalizar Pendientes")
        self.btn_geolocalizar.setFixedWidth(170)
        self.btn_geolocalizar.setStyleSheet("background-color: #FF9800; color: white;")
        self.btn_geolocalizar.clicked.connect(self.geolocalizar_pendientes)
        filtros_layout.addWidget(self.btn_geolocalizar)

        tarjeta_layout.addWidget(frame_filtros)

        # ========== PESTAÑAS ==========
        self.tabs = QTabWidget()
        
        # Solapa 1: Mapa
        tab_mapa = QWidget()
        tab_mapa.setStyleSheet("background-color: transparent;")
        mapa_layout = QVBoxLayout(tab_mapa)
        mapa_layout.setContentsMargins(5, 5, 5, 5)
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(380)
        mapa_layout.addWidget(self.web_view)
        self.tabs.addTab(tab_mapa, "🗺️ MAPA")
        
        # Solapa 2: Lista de Clientes
        tab_lista = self._crear_tab_lista()
        self.tabs.addTab(tab_lista, "📋 LISTA DE CLIENTES")
        
        # Solapa 3: Ruta Óptima
        tab_ruta = self._crear_tab_ruta()
        self.tabs.addTab(tab_ruta, "🗺️ RUTA ÓPTIMA")
        
        tarjeta_layout.addWidget(self.tabs)
        layout.addWidget(tarjeta)

        # Variables
        self.clientes = []
        self.distribuidora = None
        self.cargar_preventistas()
        self.cargar_distribuidora()
        self.filtrar_clientes()

    # ==================== PESTAÑA 1: MAPA ====================
    # (El mapa ya está creado arriba)

    # ==================== PESTAÑA 2: LISTA DE CLIENTES ====================
    
    def _crear_tab_lista(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Tabla
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(7)
        self.tabla_clientes.setHorizontalHeaderLabels([
            "Ord", "Razón Social", "CUIT", "Localidad", "Teléfono", "Saldo", "Estado"
        ])
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_clientes.setShowGrid(True)
        self.tabla_clientes.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_clientes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_clientes.setAlternatingRowColors(True)
        self.tabla_clientes.setMinimumHeight(380)
        tabla_layout.addWidget(self.tabla_clientes)

        layout.addWidget(frame_tabla)

        # Botones (SOLO Exportar CSV)
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(10, 8, 10, 8)
        botones_layout.setSpacing(10)

        btn_exportar_csv = QPushButton("📎 Exportar CSV")
        btn_exportar_csv.setStyleSheet("background-color: #4CAF50; color: white;")
        btn_exportar_csv.clicked.connect(self.exportar_csv)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_exportar_csv)

        layout.addWidget(frame_botones)

        return tab

    # ==================== PESTAÑA 3: RUTA ÓPTIMA ====================
    
    def _crear_tab_ruta(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Tabla de ruta
        frame_tabla = QFrame()
        frame_tabla.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(5, 5, 5, 5)

        self.tabla_ruta = QTableWidget()
        self.tabla_ruta.setColumnCount(6)
        self.tabla_ruta.setHorizontalHeaderLabels([
            "Ord", "Cliente", "Dirección", "Localidad", "Teléfono", "Dist. al siguiente"
        ])
        self.tabla_ruta.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_ruta.setShowGrid(True)
        self.tabla_ruta.setGridStyle(Qt.PenStyle.SolidLine)
        self.tabla_ruta.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ruta.setAlternatingRowColors(True)
        self.tabla_ruta.setMinimumHeight(380)
        tabla_layout.addWidget(self.tabla_ruta)

        layout.addWidget(frame_tabla)

        # Resumen
        frame_resumen = QFrame()
        frame_resumen.setStyleSheet("QFrame { background-color: #E8F5E9; border-radius: 8px; border: 1px solid #A5D6A7; }")
        resumen_layout = QHBoxLayout(frame_resumen)
        resumen_layout.setContentsMargins(10, 8, 10, 8)
        resumen_layout.setSpacing(20)

        self.lbl_total_clientes = QLabel("👥 Clientes: 0")
        self.lbl_distancia_total = QLabel("📏 Distancia total: 0.0 km")
        self.lbl_punto_partida = QLabel("🏁 Partida: -")

        resumen_layout.addWidget(self.lbl_total_clientes)
        resumen_layout.addWidget(self.lbl_distancia_total)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_punto_partida)

        layout.addWidget(frame_resumen)

        return tab

    # =================== FUNCIONES PRINCIPALES ===================
    
    def cargar_preventistas(self):
        preventistas = self.preventista_modelo.listar_todos(solo_activos=True)
        self.cmb_preventista.clear()
        self.cmb_preventista.addItem("-- Todos --", None)
        
        for p in preventistas:
            zona = p.get('zona', '')
            texto = f"{p['nombre']} {p['apellido']}"
            if zona:
                texto += f" - {zona}"
            self.cmb_preventista.addItem(texto, p['id'])
    
    def cargar_distribuidora(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT direccion, localidad, provincia, latitud, longitud, nombre_distribuidora
            FROM parametros WHERE id = 1
        """)
        row = cur.fetchone()
        
        if row:
            self.distribuidora = {
                'id': 0,
                'razon_social': row['nombre_distribuidora'] or 'DISTRIBUIDORA',
                'direccion': row['direccion'] or '',
                'localidad': row['localidad'] or '',
                'provincia': row['provincia'] or '',
                'latitud': row['latitud'],
                'longitud': row['longitud']
            }
            
            if not (row['latitud'] and row['longitud']) and row['direccion'] and row['localidad']:
                self.geolocalizar_distribuidora()
    
    def geolocalizar_distribuidora(self):
        if not self.distribuidora:
            return
        
        direccion = self.distribuidora.get('direccion', '')
        localidad = self.distribuidora.get('localidad', '')
        provincia = self.distribuidora.get('provincia', '')
        
        if direccion and localidad:
            partes = direccion.split(' ', 1)
            calle = partes[0] if partes else ''
            numero = partes[1] if len(partes) > 1 else ''
            
            lat, lon = obtener_coordenadas(calle, numero, localidad, provincia)
            if lat and lon:
                self.distribuidora['latitud'] = lat
                self.distribuidora['longitud'] = lon
                cur = self.db.cursor()
                cur.execute("UPDATE parametros SET latitud = ?, longitud = ? WHERE id = 1", (lat, lon))
                self.db.commit()
    
    def obtener_distribuidora_para_ruta(self):
        if self.distribuidora and self.distribuidora.get('latitud') and self.distribuidora.get('longitud'):
            return {
                'latitud': self.distribuidora['latitud'],
                'longitud': self.distribuidora['longitud'],
                'razon_social': self.distribuidora['razon_social'],
                'id': 0,
                'es_distribuidora': True
            }
        return None
    
    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def ordenar_por_cercania(self, clientes):
        if len(clientes) <= 1:
            return clientes
        
        con_coords = [c for c in clientes if c.get('latitud') and c.get('longitud')]
        sin_coords = [c for c in clientes if not (c.get('latitud') and c.get('longitud'))]
        
        if not con_coords:
            return clientes
        
        punto_partida = self.obtener_distribuidora_para_ruta()
        
        ordenados = []
        no_visitados = con_coords.copy()
        
        if punto_partida:
            actual = punto_partida
            mas_cercano_idx = 0
            distancia_minima = float('inf')
            for i, cliente in enumerate(no_visitados):
                dist = self.calcular_distancia(
                    actual['latitud'], actual['longitud'],
                    cliente['latitud'], cliente['longitud']
                )
                if dist < distancia_minima:
                    distancia_minima = dist
                    mas_cercano_idx = i
            
            primer_cliente = no_visitados.pop(mas_cercano_idx)
            ordenados.append(primer_cliente)
            actual = primer_cliente
        else:
            actual = no_visitados.pop(0)
            ordenados.append(actual)
        
        while no_visitados:
            mas_cercano = None
            distancia_minima = float('inf')
            
            for cliente in no_visitados:
                dist = self.calcular_distancia(
                    actual['latitud'], actual['longitud'],
                    cliente['latitud'], cliente['longitud']
                )
                if dist < distancia_minima:
                    distancia_minima = dist
                    mas_cercano = cliente
            
            if mas_cercano:
                ordenados.append(mas_cercano)
                no_visitados.remove(mas_cercano)
                actual = mas_cercano
        
        ordenados.extend(sin_coords)
        return ordenados
    
    def filtrar_clientes(self):
        preventista_id = self.cmb_preventista.currentData()
        
        if preventista_id:
            cur = self.db.cursor()
            cur.execute("""
                SELECT c.id, c.razon_social, c.cuit, c.localidad, c.telefono,
                       c.latitud, c.longitud, c.calle, c.numero,
                       c.saldo_cuenta_corriente, c.provincia
                FROM clientes c
                WHERE c.preventista_id = ? AND c.activo = 1
                ORDER BY c.razon_social
            """, (preventista_id,))
        else:
            cur = self.db.cursor()
            cur.execute("""
                SELECT c.id, c.razon_social, c.cuit, c.localidad, c.telefono,
                       c.latitud, c.longitud, c.calle, c.numero,
                       c.saldo_cuenta_corriente, c.provincia
                FROM clientes c
                WHERE c.activo = 1
                ORDER BY c.razon_social
            """)
        
        clientes_original = [dict(row) for row in cur.fetchall()]
        
        if self.chk_ruta_optima.isChecked():
            self.clientes = self.ordenar_por_cercania(clientes_original)
        else:
            self.clientes = clientes_original
        
        self.cargar_tabla()
        self.cargar_tabla_ruta()
        self.actualizar_mapa()
    
    def cargar_tabla(self):
        self.tabla_clientes.setRowCount(len(self.clientes))
        
        for i, cliente in enumerate(self.clientes):
            if self.chk_ruta_optima.isChecked():
                item_orden = QTableWidgetItem(str(i + 1))
                item_orden.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_clientes.setItem(i, 0, item_orden)
            else:
                item_orden = QTableWidgetItem("-")
                item_orden.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_clientes.setItem(i, 0, item_orden)
            
            self.tabla_clientes.setItem(i, 1, QTableWidgetItem(cliente['razon_social'][:45]))
            self.tabla_clientes.setItem(i, 2, QTableWidgetItem(cliente.get('cuit', '') or '-'))
            self.tabla_clientes.setItem(i, 3, QTableWidgetItem(cliente.get('localidad', '') or '-'))
            self.tabla_clientes.setItem(i, 4, QTableWidgetItem(cliente.get('telefono', '') or '-'))
            
            saldo = cliente.get('saldo_cuenta_corriente', 0) or 0
            item_saldo = QTableWidgetItem(f"${saldo:,.2f}")
            item_saldo.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            if saldo > 0:
                item_saldo.setForeground(QColor(220, 53, 69))
            elif saldo < 0:
                item_saldo.setForeground(QColor(40, 167, 69))
            self.tabla_clientes.setItem(i, 5, item_saldo)
            
            lat = cliente.get('latitud')
            lon = cliente.get('longitud')
            if lat and lon:
                item_estado = QTableWidgetItem("📍 Geo")
                item_estado.setForeground(QColor(0, 128, 0))
            else:
                item_estado = QTableWidgetItem("⚠️ Pend")
                item_estado.setForeground(QColor(255, 165, 0))
            self.tabla_clientes.setItem(i, 6, item_estado)
            
            self.tabla_clientes.item(i, 1).setData(Qt.ItemDataRole.UserRole, cliente['id'])
        
        self.tabla_clientes.resizeRowsToContents()
    
    def cargar_tabla_ruta(self):
        """Carga la tabla de ruta óptima (solo visible si chk_ruta_optima está activo)."""
        if not self.chk_ruta_optima.isChecked():
            self.tabla_ruta.setRowCount(0)
            self.lbl_total_clientes.setText("👥 Clientes: 0")
            self.lbl_distancia_total.setText("📏 Distancia total: 0.0 km")
            self.lbl_punto_partida.setText("🏁 Partida: -")
            return
        
        clientes_con_mapa = [c for c in self.clientes if c.get('latitud') and c.get('longitud')]
        distribuidora = self.obtener_distribuidora_para_ruta()
        
        puntos_ruta = []
        if distribuidora:
            puntos_ruta.append(distribuidora)
        puntos_ruta.extend(clientes_con_mapa)
        
        # Calcular distancias
        distancia_total = 0
        for i in range(len(puntos_ruta) - 1):
            distancia_total += self.calcular_distancia(
                puntos_ruta[i]['latitud'], puntos_ruta[i]['longitud'],
                puntos_ruta[i + 1]['latitud'], puntos_ruta[i + 1]['longitud']
            )
        
        # Actualizar resumen
        self.lbl_total_clientes.setText(f"👥 Clientes: {len(clientes_con_mapa)}")
        self.lbl_distancia_total.setText(f"📏 Distancia total: {distancia_total:.1f} km")
        if distribuidora:
            self.lbl_punto_partida.setText(f"🏁 Partida: {distribuidora['razon_social']}")
        else:
            self.lbl_punto_partida.setText("🏁 Partida: Primer cliente")
        
        # Cargar tabla
        self.tabla_ruta.setRowCount(len(puntos_ruta))
        for i, cliente in enumerate(puntos_ruta):
            es_distribuidora = cliente.get('es_distribuidora', False) or cliente['id'] == 0
            
            orden = "0" if es_distribuidora else str(i)
            nombre = cliente['razon_social']
            if es_distribuidora:
                nombre = f"🏭 {nombre} (PARTIDA)"
            
            direccion = f"{cliente.get('calle', '')} {cliente.get('numero', '')}".strip() if cliente.get('calle') else '-'
            if es_distribuidora and not direccion:
                direccion = cliente.get('direccion', '-')
            
            dist_siguiente = ""
            if i < len(puntos_ruta) - 1:
                dist = self.calcular_distancia(
                    puntos_ruta[i]['latitud'], puntos_ruta[i]['longitud'],
                    puntos_ruta[i + 1]['latitud'], puntos_ruta[i + 1]['longitud']
                )
                dist_siguiente = f"{dist:.1f} km"
            else:
                dist_siguiente = "Fin"
            
            self.tabla_ruta.setItem(i, 0, QTableWidgetItem(orden))
            self.tabla_ruta.setItem(i, 1, QTableWidgetItem(nombre))
            self.tabla_ruta.setItem(i, 2, QTableWidgetItem(direccion))
            self.tabla_ruta.setItem(i, 3, QTableWidgetItem(cliente.get('localidad', '-')))
            self.tabla_ruta.setItem(i, 4, QTableWidgetItem(cliente.get('telefono', '-')))
            
            item_dist = QTableWidgetItem(dist_siguiente)
            item_dist.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_ruta.setItem(i, 5, item_dist)
            
            # Resaltar fila de partida
            if es_distribuidora:
                for col in range(6):
                    item = self.tabla_ruta.item(i, col)
                    if item:
                        item.setBackground(QColor(200, 230, 255))
                        item.setForeground(QColor(13, 71, 161))
    
    def actualizar_mapa(self):
        if not self.web_view:
            return
        
        clientes_con_mapa = [c for c in self.clientes if c.get('latitud') and c.get('longitud')]
        distribuidora_punto = self.obtener_distribuidora_para_ruta()
        
        html = self._generar_html_mapa(clientes_con_mapa, distribuidora_punto)
        self.web_view.setHtml(html)
    
    def _generar_html_mapa(self, clientes_con_mapa, distribuidora_punto):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mapa de Clientes</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map { height: 100%; width: 100%; position: absolute; top: 0; left: 0; }
                body { margin: 0; padding: 0; }
                .leaflet-popup-content { font-size: 12px; }
                .ruta-info {
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    background: white;
                    padding: 8px;
                    border-radius: 6px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    font-family: Arial;
                    font-size: 11px;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
        """
        
        todos_con_coords = clientes_con_mapa.copy()
        if distribuidora_punto:
            todos_con_coords.append(distribuidora_punto)
        
        if todos_con_coords:
            lat_center = sum(c['latitud'] for c in todos_con_coords) / len(todos_con_coords)
            lon_center = sum(c['longitud'] for c in todos_con_coords) / len(todos_con_coords)
            
            html += f"""
            <script>
                var map = L.map('map').setView([{lat_center}, {lon_center}], 12);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap'
                }}).addTo(map);
            """
            
            if distribuidora_punto:
                html += f"""
                L.marker([{distribuidora_punto['latitud']}, {distribuidora_punto['longitud']}], {{
                    icon: L.divIcon({{html: '<div style="background-color: #1565C0; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px;">🏭</div>', iconSize: [32, 32], className: 'custom-div-icon'}})
                }}).addTo(map).bindPopup('<b>🏭 {distribuidora_punto['razon_social']}</b><br>Punto de partida');
                """
            
            for i, cliente in enumerate(clientes_con_mapa):
                saldo = cliente.get('saldo_cuenta_corriente', 0) or 0
                if saldo > 0:
                    color = 'red'
                elif saldo < 0:
                    color = 'green'
                else:
                    color = 'blue'
                
                orden_texto = f"<b>Orden: {i + 1}</b><br>" if self.chk_ruta_optima.isChecked() else ""
                
                html += f"""
                var marker = L.marker([{cliente['latitud']}, {cliente['longitud']}]).addTo(map);
                marker.bindPopup(`
                    <b>{cliente['razon_social']}</b><br>
                    {orden_texto}
                    <b>Dir:</b> {cliente.get('calle', '')} {cliente.get('numero', '')}<br>
                    <b>Localidad:</b> {cliente.get('localidad', '')}<br>
                    <b>Saldo:</b> ${saldo:,.0f}
                `);
                """
            
            if self.chk_ruta_optima.isChecked() and len(clientes_con_mapa) > 0:
                html += "var latlngs = ["
                
                if distribuidora_punto:
                    html += f"[{distribuidora_punto['latitud']}, {distribuidora_punto['longitud']}],"
                
                for cliente in clientes_con_mapa:
                    html += f"[{cliente['latitud']}, {cliente['longitud']}],"
                html += "];"
                
                html += """
                var polyline = L.polyline(latlngs, {
                    color: '#E74C3C',
                    weight: 3,
                    opacity: 0.8,
                    dashArray: '5, 10'
                }).addTo(map);
                
                map.fitBounds(polyline.getBounds());
                """
                
                info_text = f"{len(clientes_con_mapa)} clientes"
                if distribuidora_punto:
                    info_text = f"Desde distribuidora | {info_text}"
                
                html += f"""
                var infoDiv = L.control({{position: 'bottomright'}});
                infoDiv.onAdd = function(map) {{
                    var div = L.DomUtil.create('div', 'ruta-info');
                    div.innerHTML = '<b>🗺️ Ruta Óptima</b><br>{info_text}';
                    return div;
                }};
                infoDiv.addTo(map);
                """
            
            html += """
            </script>
            """
        else:
            html += """
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #2C3E50; color: white; font-family: Arial;">
                <div style="text-align: center;">
                    <div style="font-size: 48px;">📍</div>
                    <h3>No hay clientes con coordenadas</h3>
                    <p>Haga clic en "Geolocalizar Pendientes"</p>
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def exportar_csv(self):
        if not self.clientes:
            QMessageBox.warning(self, "Exportar", "No hay clientes para exportar.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar lista", 
            f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if self.chk_ruta_optima.isChecked():
                    writer.writerow(["Orden", "Razón Social", "CUIT", "Localidad", "Teléfono", "Saldo", "Estado"])
                else:
                    writer.writerow(["Razón Social", "CUIT", "Localidad", "Teléfono", "Saldo", "Estado"])
                
                for i, cliente in enumerate(self.clientes):
                    saldo = cliente.get('saldo_cuenta_corriente', 0) or 0
                    estado = "Geo" if cliente.get('latitud') else "Pend"
                    if self.chk_ruta_optima.isChecked():
                        writer.writerow([
                            i + 1, cliente['razon_social'],
                            cliente.get('cuit', ''), cliente.get('localidad', ''),
                            cliente.get('telefono', ''), f"{saldo:.2f}", estado
                        ])
                    else:
                        writer.writerow([
                            cliente['razon_social'],
                            cliente.get('cuit', ''), cliente.get('localidad', ''),
                            cliente.get('telefono', ''), f"{saldo:.2f}", estado
                        ])
            
            QMessageBox.information(self, "Exportar", f"✅ Exportado:\n{filename}")
    
    def geolocalizar_pendientes(self):
        pendientes = [c for c in self.clientes if not (c.get('latitud') and c.get('longitud'))]
        
        if not pendientes:
            QMessageBox.information(self, "Geolocalización", "✅ Todos los clientes ya tienen coordenadas.")
            return
        
        confirm = QMessageBox.question(self, "Geolocalización", 
                                       f"📍 Se geolocalizarán {len(pendientes)} clientes.\n¿Desea continuar?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        dialog_progreso = DialogoGeolocalizacion(len(pendientes), self)
        dialog_progreso.show()
        QApplication.processEvents()
        
        geolocalizados = 0
        actual = 0
        
        for cliente in pendientes:
            actual += 1
            calle = cliente.get('calle') or ''
            numero = cliente.get('numero') or ''
            localidad = cliente.get('localidad') or ''
            provincia = cliente.get('provincia') or ''
            
            dialog_progreso.actualizar(actual, len(pendientes), cliente['razon_social'])
            QApplication.processEvents()
            
            if calle and localidad:
                lat, lon = obtener_coordenadas(calle, numero, localidad, provincia)
                if lat and lon:
                    cur = self.db.cursor()
                    cur.execute("UPDATE clientes SET latitud = ?, longitud = ? WHERE id = ?",
                               (lat, lon, cliente['id']))
                    geolocalizados += 1
                    self.db.commit()
        
        dialog_progreso.cerrar()
        self.filtrar_clientes()
        
        QMessageBox.information(self, "Geolocalización", 
                               f"✅ {geolocalizados} clientes geolocalizados.\n"
                               f"⚠️ {len(pendientes) - geolocalizados} no pudieron ser localizados.")


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from db.db_manager import obtener_conexion
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    ventana = VistaMapa(db)
    ventana.show()
    sys.exit(app.exec())