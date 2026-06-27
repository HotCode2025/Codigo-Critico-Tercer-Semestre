"""
Código Crítico - Tercer Semestre Año 2026
Diálogo Acerca de... con GIF animado y logo
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie, QPixmap


class DialogoAcercaDe(QDialog):
    """Diálogo Acerca de... con logo y GIF animado"""
    
    def __init__(self, gif_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de...")
        self.setFixedSize(550, 520)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #F0F2F5;
                border-radius: 15px;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #D0D0D0;
            }
            QLabel {
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(12)
        
        # ========== LOGO ==========
        # Buscar logo en assets/codigocritico.jpg
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "codigocritico.jpg")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Escalar manteniendo proporción
                pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, 
                                      Qt.TransformationMode.SmoothTransformation)
                lbl_logo = QLabel()
                lbl_logo.setPixmap(pixmap)
                lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                frame_layout.addWidget(lbl_logo)
            else:
                self._agregar_logo_default(frame_layout)
        else:
            self._agregar_logo_default(frame_layout)
        
        # ========== GIF animado (opcional) ==========
        if gif_path and os.path.exists(gif_path):
            try:
                self.movie = QMovie(gif_path)
                self.movie.setScaledSize(QSize(150, 150))
                lbl_gif = QLabel()
                lbl_gif.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_gif.setMovie(self.movie)
                self.movie.start()
                frame_layout.addWidget(lbl_gif)
            except Exception as e:
                print(f"Error al cargar GIF: {e}")
        
        # Título
        lbl_titulo = QLabel("Sistema de Distribución y Logística")
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_titulo)
        
        # Versión
        lbl_version = QLabel("Versión 3.0.0 - Código Crítico")
        lbl_version.setStyleSheet("font-size: 12px; color: #666;")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(lbl_version)
        
        # Línea separadora
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("background-color: #D0D0D0; max-height: 1px;")
        frame_layout.addWidget(linea)
        
        # Información
        info = QLabel("""
        <b>Desarrollado por:</b> Código Crítico<br>
        <b>Año:</b> Tercer Semestre 2026<br>
        <b>Tecnologías:</b> Python 3.12, PyQt6, SQLite, Turso<br>
        <br>
        <b>Funcionalidades:</b><br>
        • Gestión de Clientes, Productos y Preventistas<br>
        • Facturación con PDF y QR<br>
        • Cuenta Corriente y Cheques<br>
        • Notas de Venta<br>
        • Dashboard con gráficos<br>
        • Mapa de clientes<br>
        • Sincronización con Turso<br>
        <br>
        <b>© 2026 - Todos los derechos reservados</b>
        """)
        info.setStyleSheet("font-size: 10px;")
        info.setWordWrap(True)
        frame_layout.addWidget(info)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #1565C0; color: white; border-radius: 5px; padding: 8px 16px; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        frame_layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(frame)
    
    def _agregar_logo_default(self, layout):
        """Agrega el logo por defecto (emoji) si no hay imagen."""
        lbl_logo = QLabel("🏢")
        lbl_logo.setStyleSheet("font-size: 48px;")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_logo)
    
    def closeEvent(self, event):
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
        event.accept()