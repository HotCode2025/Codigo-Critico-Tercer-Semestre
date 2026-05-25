"""
Código Crítico - Tercer Semestre Año 2026
Vista para la importación de catálogos PDF del proveedor.
Permite seleccionar un archivo PDF, extraer los datos tabulares,
previsualizarlos y cargarlos en la base de datos de forma manual
o aplicando un porcentaje de incremento automático sobre el costo.
"""

import sqlite3
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QFileDialog, QMessageBox, QHeaderView,
                               QGroupBox, QFormLayout, QLineEdit,
                               QDoubleSpinBox, QCheckBox, QSpinBox,
                               QProgressBar, QWidget)
from PySide6.QtCore import Qt, QThread, Signal

from pdf.lector_pdf import LectorPDF
from pdf.extractor_datos import ExtractorDatos
from controladores.controlador_pdf import ControladorPDF
from db.db_manager import obtener_conexion  # para que el hilo abra su propia conexión


class HiloImportacion(QThread):
    """Hilo para no bloquear la interfaz durante la importación.
    Crea su propia conexión a la BD para evitar conflictos con SQLite."""
    progreso = Signal(int)
    finalizado = Signal(dict)
    error = Signal(str)

    def __init__(self, datos, modo, porcentaje):
        super().__init__()
        self.datos = datos
        self.modo = modo          # 'manual' o 'porcentaje'
        self.porcentaje = porcentaje

    def run(self):
        db = None
        try:
            # Abrir una conexión independiente dentro del hilo
            db = obtener_conexion()
            ctrl_pdf = ControladorPDF(db)

            if self.modo == 'manual':
                resumen = ctrl_pdf.procesar_catalogo_manual(self.datos)
            else:
                resumen = ctrl_pdf.procesar_catalogo_con_porcentaje(
                    self.datos, self.porcentaje)

            self.finalizado.emit(resumen)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if db:
                db.close()


class VistaPDF(QDialog):
    def __init__(self, db: sqlite3.Connection, parent=None):
        super().__init__(parent)
        self.db = db
        self.ctrl_pdf = ControladorPDF(db)   # Se usa solo para registrar el historial
        self.datos_extraidos = []
        self.ruta_pdf = ""

        self.setWindowTitle("Importar Catálogo PDF del Proveedor")
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        # ---- Grupo: Selección de archivo ----
        grupo_archivo = QGroupBox("Archivo PDF")
        arch_layout = QHBoxLayout()
        self.lbl_ruta = QLineEdit()
        self.lbl_ruta.setReadOnly(True)
        self.lbl_ruta.setPlaceholderText("Seleccione un archivo PDF...")
        btn_examinar = QPushButton("Examinar")
        btn_examinar.clicked.connect(self.examinar_pdf)
        arch_layout.addWidget(self.lbl_ruta)
        arch_layout.addWidget(btn_examinar)
        grupo_archivo.setLayout(arch_layout)
        layout.addWidget(grupo_archivo)

        # ---- Grupo: Configuración de columnas ----
        grupo_conf = QGroupBox("Mapeo de columnas del PDF")
        conf_layout = QFormLayout()
        self.spin_codigo = QSpinBox()
        self.spin_codigo.setRange(0, 10)
        self.spin_codigo.setValue(0)
        self.spin_descripcion = QSpinBox()
        self.spin_descripcion.setRange(0, 10)
        self.spin_descripcion.setValue(1)
        self.spin_costo = QSpinBox()
        self.spin_costo.setRange(0, 10)
        self.spin_costo.setValue(2)
        self.spin_stock = QSpinBox()
        self.spin_stock.setRange(-1, 10)
        self.spin_stock.setValue(3)
        self.spin_stock.setSpecialValueText("No tiene")
        self.spin_venc = QSpinBox()
        self.spin_venc.setRange(-1, 10)
        self.spin_venc.setValue(4)
        self.spin_venc.setSpecialValueText("No tiene")
        conf_layout.addRow("Columna Código:", self.spin_codigo)
        conf_layout.addRow("Columna Descripción:", self.spin_descripcion)
        conf_layout.addRow("Columna Precio Costo:", self.spin_costo)
        conf_layout.addRow("Columna Stock:", self.spin_stock)
        conf_layout.addRow("Columna Fecha Venc.:", self.spin_venc)
        self.chk_encabezado = QCheckBox("El PDF tiene fila de encabezado")
        self.chk_encabezado.setChecked(True)
        conf_layout.addRow("", self.chk_encabezado)
        grupo_conf.setLayout(conf_layout)
        layout.addWidget(grupo_conf)

        # ---- Botón Extraer ----
        btn_extraer = QPushButton("Extraer datos del PDF")
        btn_extraer.clicked.connect(self.extraer_datos)
        layout.addWidget(btn_extraer)

        # ---- Tabla de previsualización ----
        grupo_prev = QGroupBox("Datos extraídos")
        prev_layout = QVBoxLayout()
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Código", "Descripción", "Precio Costo", "Stock", "Fecha Venc."])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        prev_layout.addWidget(self.tabla)
        grupo_prev.setLayout(prev_layout)
        layout.addWidget(grupo_prev)

        # ---- Grupo: Procesamiento ----
        grupo_proc = QGroupBox("Cargar en el sistema")
        proc_layout = QVBoxLayout()
        modo_layout = QHBoxLayout()
        self.chk_porcentaje = QCheckBox("Aplicar porcentaje de incremento al costo")
        self.spin_porcentaje = QDoubleSpinBox()
        self.spin_porcentaje.setRange(0, 500)
        self.spin_porcentaje.setValue(30.0)
        self.spin_porcentaje.setSuffix(" %")
        self.spin_porcentaje.setEnabled(False)
        self.chk_porcentaje.toggled.connect(self.spin_porcentaje.setEnabled)
        modo_layout.addWidget(self.chk_porcentaje)
        modo_layout.addWidget(self.spin_porcentaje)
        proc_layout.addLayout(modo_layout)

        self.btn_procesar = QPushButton("Procesar e importar a la base de datos")
        self.btn_procesar.clicked.connect(self.procesar_importacion)
        self.btn_procesar.setEnabled(False)
        proc_layout.addWidget(self.btn_procesar)

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setVisible(False)
        proc_layout.addWidget(self.barra_progreso)

        grupo_proc.setLayout(proc_layout)
        layout.addWidget(grupo_proc)

    # ---------- Métodos ----------
    def examinar_pdf(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar catálogo PDF", "",
            "Archivos PDF (*.pdf);;Todos los archivos (*)")
        if archivo:
            self.ruta_pdf = archivo
            self.lbl_ruta.setText(archivo)

    def extraer_datos(self):
        if not self.ruta_pdf:
            QMessageBox.warning(self, "Aviso", "Primero seleccione un archivo PDF.")
            return
        try:
            lector = LectorPDF(self.ruta_pdf)
            lector.abrir_pdf()
            filas = lector.extraer_tablas()
            lector.cerrar_pdf()

            # Configurar extractor según los spinboxes
            stock_col = self.spin_stock.value()
            venc_col = self.spin_venc.value()
            extractor = ExtractorDatos(
                codigo_col=self.spin_codigo.value(),
                descripcion_col=self.spin_descripcion.value(),
                precio_costo_col=self.spin_costo.value(),
                stock_col=None if stock_col == -1 else stock_col,
                fecha_venc_col=None if venc_col == -1 else venc_col,
                tiene_encabezado=self.chk_encabezado.isChecked()
            )
            self.datos_extraidos = extractor.extraer(filas)
            self._mostrar_datos()
            self.btn_procesar.setEnabled(len(self.datos_extraidos) > 0)
            QMessageBox.information(
                self, "Extracción completada",
                f"Se extrajeron {len(self.datos_extraidos)} productos del PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el PDF:\n{e}")

    def _mostrar_datos(self):
        self.tabla.setRowCount(len(self.datos_extraidos))
        for fila, item in enumerate(self.datos_extraidos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(item.get('codigo', '')))
            self.tabla.setItem(fila, 1, QTableWidgetItem(item.get('descripcion', '')))
            self.tabla.setItem(fila, 2, QTableWidgetItem(f"{item.get('precio_costo', 0):.2f}"))
            stock = item.get('stock')
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(stock) if stock else ""))
            self.tabla.setItem(fila, 4, QTableWidgetItem(item.get('fecha_vencimiento') or ""))

    def procesar_importacion(self):
        if not self.datos_extraidos:
            QMessageBox.warning(self, "Aviso", "No hay datos para importar.")
            return

        modo = 'porcentaje' if self.chk_porcentaje.isChecked() else 'manual'
        porcentaje = self.spin_porcentaje.value()

        self.btn_procesar.setEnabled(False)
        self.barra_progreso.setVisible(True)
        self.barra_progreso.setRange(0, 0)  # indeterminada

        # Se pasa solo los datos y parámetros; el hilo crea su propia conexión
        self.hilo = HiloImportacion(self.datos_extraidos, modo, porcentaje)
        self.hilo.finalizado.connect(self._importacion_finalizada)
        self.hilo.error.connect(self._importacion_error)
        self.hilo.start()

    def _importacion_finalizada(self, resumen):
        self.barra_progreso.setVisible(False)
        self.btn_procesar.setEnabled(True)

        # Registrar en historial (usando el controlador del hilo principal)
        nombre_archivo = os.path.basename(self.ruta_pdf)
        self.ctrl_pdf.registrar_importacion(
            nombre_archivo=nombre_archivo,
            procesado_por="Usuario",
            total_nuevos=resumen['nuevos'],
            total_actualizados=resumen['actualizados']
        )

        QMessageBox.information(
            self, "Importación exitosa",
            f"Productos nuevos: {resumen['nuevos']}\n"
            f"Productos actualizados: {resumen['actualizados']}")
        self.accept()

    def _importacion_error(self, mensaje):
        self.barra_progreso.setVisible(False)
        self.btn_procesar.setEnabled(True)
        QMessageBox.critical(self, "Error en la importación", mensaje)