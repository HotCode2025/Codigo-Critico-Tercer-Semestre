"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 9.0: Vista Base con Paginación
==================================================
📌 USO: Clase base para vistas con listados paginados
📌 CARACTERÍSTICAS:
    - Paginación automática
    - Búsqueda y filtrado
    - Carga perezosa de datos
"""

import sqlite3
from typing import List, Dict, Any, Optional, Callable
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QComboBox, QWidget,
                               QFrame, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer


class VistaPaginada(QDialog):
    """
    Clase base para vistas con listados paginados.
    
    Ejemplo:
        class VistaClientes(VistaPaginada):
            def __init__(self, db):
                super().__init__(db, 'clientes', 
                                 ['id', 'razon_social', 'cuit', 'telefono'],
                                 'razon_social')
    """
    
    def __init__(self, db: sqlite3.Connection, 
                 tabla: str,
                 columnas: List[str],
                 columna_orden: str = 'nombre',
                 titulo: str = "Listado",
                 parent=None):
        """
        Inicializa la vista paginada.
        
        Args:
            db: Conexión a SQLite
            tabla: Nombre de la tabla
            columnas: Lista de columnas a mostrar
            columna_orden: Columna por la que ordenar
            titulo: Título de la ventana
            parent: Widget padre
        """
        super().__init__(parent)
        self.db = db
        self.tabla = tabla
        self.columnas = columnas
        self.columna_orden = columna_orden
        self.pagina_actual = 1
        self.por_pagina = 50
        self.total_registros = 0
        self.filtro_actual = ""
        self.campo_filtro = columnas[1] if len(columnas) > 1 else columnas[0]
        
        self.setWindowTitle(titulo)
        self.resize(900, 600)
        
        self._inicializar_ui()
        self.cargar_pagina()
    
    def _inicializar_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-size: 9px;
                gridline-color: #A0A0A0;
                alternate-background-color: #F8F9FA;
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
            QPushButton:disabled {
                background-color: #90CAF9;
                color: #E3F2FD;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 10px;
            }
            QComboBox {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 10px;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #D0D0D0;
            }
            QLabel {
                color: #333333;
                font-size: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Contenedor principal
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(8)
        
        # Barra de búsqueda
        frame_busqueda = QFrame()
        frame_busqueda.setStyleSheet("QFrame { background-color: #F8F9FA; }")
        busqueda_layout = QHBoxLayout(frame_busqueda)
        busqueda_layout.setContentsMargins(8, 6, 8, 6)
        busqueda_layout.setSpacing(8)
        
        busqueda_layout.addWidget(QLabel("🔍 Buscar:"))
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar...")
        self.txt_buscar.returnPressed.connect(self.buscar)
        busqueda_layout.addWidget(self.txt_buscar, 1)
        
        busqueda_layout.addWidget(QLabel("Campo:"))
        self.cmb_campo = QComboBox()
        for col in self.columnas:
            self.cmb_campo.addItem(col)
        busqueda_layout.addWidget(self.cmb_campo)
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar)
        busqueda_layout.addWidget(btn_buscar)
        
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setStyleSheet("background-color: #FF9800;")
        btn_limpiar.clicked.connect(self.limpiar_busqueda)
        busqueda_layout.addWidget(btn_limpiar)
        
        frame_layout.addWidget(frame_busqueda)
        
        # Tabla
        frame_tabla = QFrame()
        tabla_layout = QVBoxLayout(frame_tabla)
        tabla_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(len(self.columnas))
        self.tabla.setHorizontalHeaderLabels(self.columnas)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setMinimumHeight(350)
        tabla_layout.addWidget(self.tabla)
        
        frame_layout.addWidget(frame_tabla)
        
        # Barra de paginación
        frame_paginacion = QFrame()
        frame_paginacion.setStyleSheet("QFrame { background-color: #F8F9FA; }")
        paginacion_layout = QHBoxLayout(frame_paginacion)
        paginacion_layout.setContentsMargins(8, 6, 8, 6)
        paginacion_layout.setSpacing(8)
        
        self.lbl_info = QLabel("Mostrando 0-0 de 0")
        paginacion_layout.addWidget(self.lbl_info)
        
        paginacion_layout.addStretch()
        
        self.btn_primero = QPushButton("⏮")
        self.btn_primero.setFixedWidth(30)
        self.btn_primero.clicked.connect(self.ir_primera_pagina)
        paginacion_layout.addWidget(self.btn_primero)
        
        self.btn_anterior = QPushButton("◀")
        self.btn_anterior.setFixedWidth(30)
        self.btn_anterior.clicked.connect(self.ir_pagina_anterior)
        paginacion_layout.addWidget(self.btn_anterior)
        
        self.lbl_pagina = QLabel("Pág. 1")
        paginacion_layout.addWidget(self.lbl_pagina)
        
        self.btn_siguiente = QPushButton("▶")
        self.btn_siguiente.setFixedWidth(30)
        self.btn_siguiente.clicked.connect(self.ir_pagina_siguiente)
        paginacion_layout.addWidget(self.btn_siguiente)
        
        self.btn_ultimo = QPushButton("⏭")
        self.btn_ultimo.setFixedWidth(30)
        self.btn_ultimo.clicked.connect(self.ir_ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultimo)
        
        paginacion_layout.addWidget(QLabel("Por página:"))
        self.spin_por_pagina = QSpinBox()
        self.spin_por_pagina.setRange(10, 200)
        self.spin_por_pagina.setValue(50)
        self.spin_por_pagina.valueChanged.connect(self.cambiar_por_pagina)
        paginacion_layout.addWidget(self.spin_por_pagina)
        
        frame_layout.addWidget(frame_paginacion)
        
        layout.addWidget(frame)
    
    def cargar_pagina(self):
        """Carga la página actual de datos."""
        try:
            offset = (self.pagina_actual - 1) * self.por_pagina
            
            cur = self.db.cursor()
            
            # Construir consulta con filtro
            where_clause = ""
            params = []
            
            if self.filtro_actual:
                campo = self.cmb_campo.currentText()
                where_clause = f" WHERE {campo} LIKE ?"
                params.append(f"%{self.filtro_actual}%")
            
            # Contar total
            count_query = f"SELECT COUNT(*) FROM {self.tabla}{where_clause}"
            cur.execute(count_query, params)
            self.total_registros = cur.fetchone()[0]
            
            # Obtener datos paginados
            query = f"""
                SELECT * FROM {self.tabla}
                {where_clause}
                ORDER BY {self.columna_orden}
                LIMIT ? OFFSET ?
            """
            params.extend([self.por_pagina, offset])
            cur.execute(query, params)
            
            registros = [dict(row) for row in cur.fetchall()]
            
            # Actualizar tabla
            self.tabla.setRowCount(len(registros))
            
            for fila, reg in enumerate(registros):
                for col, campo in enumerate(self.columnas):
                    valor = reg.get(campo, "")
                    item = QTableWidgetItem(str(valor) if valor is not None else "")
                    self.tabla.setItem(fila, col, item)
                    self.tabla.item(fila, col).setData(Qt.ItemDataRole.UserRole, reg.get('id'))
            
            # Actualizar controles de paginación
            self._actualizar_controles()
            
        except Exception as e:
            self.tabla.setRowCount(1)
            self.tabla.setSpan(0, 0, 1, len(self.columnas))
            item = QTableWidgetItem(f"Error al cargar datos: {e}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla.setItem(0, 0, item)
            print(f"Error cargando página: {e}")
    
    def _actualizar_controles(self):
        """Actualiza el estado de los controles de paginación."""
        total_paginas = max(1, (self.total_registros + self.por_pagina - 1) // self.por_pagina)
        
        inicio = (self.pagina_actual - 1) * self.por_pagina + 1
        fin = min(self.pagina_actual * self.por_pagina, self.total_registros)
        
        if self.total_registros == 0:
            self.lbl_info.setText("Mostrando 0 registros")
        else:
            self.lbl_info.setText(f"Mostrando {inicio}-{fin} de {self.total_registros}")
        
        self.lbl_pagina.setText(f"Pág. {self.pagina_actual} de {total_paginas}")
        
        self.btn_primero.setEnabled(self.pagina_actual > 1)
        self.btn_anterior.setEnabled(self.pagina_actual > 1)
        self.btn_siguiente.setEnabled(self.pagina_actual < total_paginas)
        self.btn_ultimo.setEnabled(self.pagina_actual < total_paginas)
    
    def buscar(self):
        """Ejecuta una búsqueda con el texto actual."""
        self.filtro_actual = self.txt_buscar.text().strip()
        self.pagina_actual = 1
        self.cargar_pagina()
    
    def limpiar_busqueda(self):
        """Limpia el filtro de búsqueda."""
        self.txt_buscar.clear()
        self.filtro_actual = ""
        self.pagina_actual = 1
        self.cargar_pagina()
    
    def ir_primera_pagina(self):
        """Va a la primera página."""
        self.pagina_actual = 1
        self.cargar_pagina()
    
    def ir_pagina_anterior(self):
        """Va a la página anterior."""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_pagina()
    
    def ir_pagina_siguiente(self):
        """Va a la página siguiente."""
        total_paginas = (self.total_registros + self.por_pagina - 1) // self.por_pagina
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.cargar_pagina()
    
    def ir_ultima_pagina(self):
        """Va a la última página."""
        total_paginas = (self.total_registros + self.por_pagina - 1) // self.por_pagina
        self.pagina_actual = total_paginas
        self.cargar_pagina()
    
    def cambiar_por_pagina(self):
        """Cambia la cantidad de registros por página."""
        self.por_pagina = self.spin_por_pagina.value()
        self.pagina_actual = 1
        self.cargar_pagina()
    
    def obtener_registro_seleccionado(self) -> Optional[str]:
        """Obtiene el ID del registro seleccionado."""
        fila = self.tabla.currentRow()
        if fila >= 0:
            return self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        return None
    
    def obtener_todos_los_ids(self) -> List[str]:
        """Obtiene todos los IDs de la página actual."""
        ids = []
        for fila in range(self.tabla.rowCount()):
            item = self.tabla.item(fila, 0)
            if item:
                ids.append(item.data(Qt.ItemDataRole.UserRole))
        return ids
    
    def refrescar(self):
        """Refresca la página actual."""
        self.cargar_pagina()