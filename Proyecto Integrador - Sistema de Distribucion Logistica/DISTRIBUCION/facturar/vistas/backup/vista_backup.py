"""
Código Crítico - Tercer Semestre Año 2026
Vista de Gestión de Backups - Profesional
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QFrame, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from utilidades.backup_profesional import BackupManagerProfesional


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


class VistaBackup(QDialog):
    def __init__(self, backup_manager: BackupManagerProfesional, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.setWindowTitle("Gestión de Backups")
        self.setFixedSize(700, 500)

        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-size: 9px;
                gridline-color: #E0E0E0;
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
                padding: 4px;
                font-weight: 600;
                border: none;
            }
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
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
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        tarjeta = QFrame()
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_layout.setContentsMargins(10, 10, 10, 10)
        tarjeta_layout.setSpacing(8)

        # Título
        tarjeta_layout.addWidget(LabelSeccionAzul("📦 GESTIÓN DE BACKUPS"))

        # Estadísticas
        frame_stats = QFrame()
        frame_stats.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        stats_layout = QHBoxLayout(frame_stats)
        stats_layout.setContentsMargins(10, 8, 10, 8)
        stats_layout.setSpacing(20)

        self.lbl_total_backups = QLabel("📁 Total: 0")
        self.lbl_espacio = QLabel("💾 Espacio: 0 MB")
        self.lbl_ultimo = QLabel("🕐 Último: -")

        stats_layout.addWidget(self.lbl_total_backups)
        stats_layout.addWidget(self.lbl_espacio)
        stats_layout.addWidget(self.lbl_ultimo)
        stats_layout.addStretch()

        tarjeta_layout.addWidget(frame_stats)

        # Tabla de backups
        self.tabla_backups = QTableWidget()
        self.tabla_backups.setColumnCount(3)
        self.tabla_backups.setHorizontalHeaderLabels(["Nombre", "Fecha", "Tamaño"])
        self.tabla_backups.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_backups.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_backups.setMinimumHeight(280)
        tarjeta_layout.addWidget(self.tabla_backups)

        # Botones
        frame_botones = QFrame()
        frame_botones.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #D0D0D0; }")
        botones_layout = QHBoxLayout(frame_botones)
        botones_layout.setContentsMargins(10, 8, 10, 8)
        botones_layout.setSpacing(10)

        btn_crear = QPushButton("➕ Crear Backup")
        btn_crear.setStyleSheet("background-color: #4CAF50;")
        btn_crear.clicked.connect(self.crear_backup)

        btn_restaurar = QPushButton("🔄 Restaurar Backup")
        btn_restaurar.setStyleSheet("background-color: #FF9800;")
        btn_restaurar.clicked.connect(self.restaurar_backup)

        btn_eliminar = QPushButton("🗑️ Eliminar Backup")
        btn_eliminar.setStyleSheet("background-color: #D32F2F;")
        btn_eliminar.clicked.connect(self.eliminar_backup)

        btn_refrescar = QPushButton("🔄 Refrescar")
        btn_refrescar.clicked.connect(self.cargar_backups)

        botones_layout.addWidget(btn_crear)
        botones_layout.addWidget(btn_restaurar)
        botones_layout.addWidget(btn_eliminar)
        botones_layout.addStretch()
        botones_layout.addWidget(btn_refrescar)

        tarjeta_layout.addWidget(frame_botones)
        layout.addWidget(tarjeta)

        self.cargar_backups()

    def cargar_backups(self):
        backups = self.backup_manager.listar_backups()
        stats = self.backup_manager.obtener_estadisticas()

        self.lbl_total_backups.setText(f"📁 Total: {stats['total_backups']}")
        self.lbl_espacio.setText(f"💾 Espacio: {stats['espacio_total_mb']:.2f} MB")
        self.lbl_ultimo.setText(f"🕐 Último: {stats['ultimo_backup']['fecha'] if stats['ultimo_backup'] else '-'}")

        self.tabla_backups.setRowCount(len(backups))
        for i, b in enumerate(backups):
            self.tabla_backups.setItem(i, 0, QTableWidgetItem(b['nombre']))
            self.tabla_backups.setItem(i, 1, QTableWidgetItem(b['fecha']))
            self.tabla_backups.setItem(i, 2, QTableWidgetItem(b['tamaño']))
            self.tabla_backups.item(i, 0).setData(Qt.ItemDataRole.UserRole, b['ruta'])

    def crear_backup(self):
        ruta = self.backup_manager.crear_backup_con_progreso(self)
        if ruta:
            QMessageBox.information(self, "Backup", f"✅ Backup creado exitosamente:\n{ruta}")
            self.cargar_backups()
        else:
            QMessageBox.critical(self, "Error", "❌ No se pudo crear el backup")

    def restaurar_backup(self):
        fila = self.tabla_backups.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un backup para restaurar.")
            return

        backup_path = self.tabla_backups.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        backup_nombre = self.tabla_backups.item(fila, 0).text()

        confirm = QMessageBox.question(
            self, "Confirmar Restauración",
            f"¿Restaurar backup '{backup_nombre}'?\n\n"
            "⚠️ Se perderán los cambios no guardados en la base actual.\n"
            "Se creará un backup de seguridad antes de restaurar.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if self.backup_manager.restaurar_backup(backup_path, self):
                QMessageBox.information(self, "Éxito", "✅ Base de datos restaurada correctamente.\nReinicie la aplicación para ver los cambios.")
            else:
                QMessageBox.critical(self, "Error", "❌ No se pudo restaurar el backup")

    def eliminar_backup(self):
        fila = self.tabla_backups.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un backup para eliminar.")
            return

        backup_path = self.tabla_backups.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        backup_nombre = self.tabla_backups.item(fila, 0).text()

        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar backup '{backup_nombre}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                os.remove(backup_path)
                self.cargar_backups()
                QMessageBox.information(self, "Éxito", "Backup eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")