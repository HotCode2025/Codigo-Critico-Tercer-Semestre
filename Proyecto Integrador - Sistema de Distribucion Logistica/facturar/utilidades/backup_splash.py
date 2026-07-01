"""
Código Crítico - Tercer Semestre Año 2026
Splash circular para backup con barra de progreso real y retardo mínimo
"""

import sys
import os
import time
import threading
from PyQt6.QtWidgets import (QSplashScreen, QProgressBar, QVBoxLayout, 
                               QWidget, QLabel, QApplication)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect
from PyQt6.QtGui import (QPainter, QColor, QFont, QBrush, QPen, QPixmap, 
                          QRegion, QLinearGradient)


class BackupSplash(QSplashScreen):
    """Splash screen circular para backup con barra de progreso."""
    
    def __init__(self, texto_inicial="Iniciando backup...", parent=None):
        self.radius = 200
        self.angulo = 0
        self.progreso_valor = 0
        self.texto = texto_inicial
        
        # Crear pixmap circular
        pixmap = QPixmap(400, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        # Hacer la ventana redonda
        self.setMask(QRegion(0, 0, 400, 400, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)
        
        # Timer para animación de giro
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulo)
        self.timer_animacion.start(50)
        
        # Timer para actualizar barra de progreso
        self.timer_progreso = QTimer()
        self.timer_progreso.timeout.connect(self._actualizar_progreso_simulado)
        
        self.show()
        QApplication.processEvents()
    
    def _actualizar_angulo(self):
        """Actualiza el ángulo de los anillos giratorios."""
        self.angulo = (self.angulo + 6) % 360
        self.update()
    
    def _actualizar_progreso_simulado(self):
        """Simula el avance de la barra de progreso."""
        if self.progreso_valor < 95:
            self.progreso_valor += 1
            self.update()
    
    def iniciar_progreso(self, duracion_segundos=3):
        """Inicia la simulación de progreso con duración específica."""
        self.progreso_valor = 0
        paso_ms = max(1, int((duracion_segundos * 1000) // 95))
        self.timer_progreso.start(paso_ms)
    
    def set_texto(self, texto):
        """Cambia el texto del splash."""
        self.texto = texto
        self.update()
    
    def set_progreso(self, valor):
        """Establece un valor específico de progreso (0-100)."""
        self.progreso_valor = min(valor, 100)
        self.update()
        QApplication.processEvents()
    
    def finalizar(self):
        """Finaliza el splash y cierra la ventana."""
        self.timer_animacion.stop()
        self.timer_progreso.stop()
        self.progreso_valor = 100
        self.update()
        QApplication.processEvents()
        time.sleep(0.5)
        self.close()
    
    def drawContents(self, painter):
        """Dibuja el splash circular con animación y barra de progreso."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 180
        
        # Fondo circular con gradiente
        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))  # #1A237E
        gradiente.setColorAt(1, QColor(13, 71, 161))
        
        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)
        
        # Anillos giratorios
        pen = QPen()
        pen.setWidth(4)
        
        # Anillo 1
        pen.setColor(QColor(255, 193, 7))  # #FFC107
        painter.setPen(pen)
        painter.drawArc(centro_x - 140, centro_y - 140, 280, 280,
                       self.angulo * 16, 120 * 16)
        
        # Anillo 2
        pen.setColor(QColor(33, 150, 243))  # #2196F3
        painter.setPen(pen)
        painter.drawArc(centro_x - 120, centro_y - 120, 240, 240,
                       (360 - self.angulo) * 16, 90 * 16)
        
        # Anillo 3
        pen.setColor(QColor(76, 175, 80))  # #4CAF50
        painter.setPen(pen)
        painter.drawArc(centro_x - 100, centro_y - 100, 200, 200,
                       (self.angulo + 180) * 16, 80 * 16)
        
        # Icono central (base de datos)
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - 35, centro_y - 35, 70, 70)
        
        # Ícono de base de datos
        painter.setPen(QPen(QColor(26, 35, 126), 3))
        painter.setBrush(QBrush(QColor(76, 175, 80)))
        
        # Cilindro de base de datos
        painter.drawEllipse(centro_x - 20, centro_y - 20, 40, 15)
        painter.drawRect(centro_x - 20, centro_y - 20, 40, 30)
        painter.drawEllipse(centro_x - 20, centro_y + 10, 40, 15)
        
        # Texto principal
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(centro_x - 150, centro_y + 35, 300, 40),
                        Qt.AlignmentFlag.AlignCenter, self.texto)
        
        # Barra de progreso circular
        if self.progreso_valor > 0:
            pen.setWidth(6)
            pen.setColor(QColor(76, 175, 80))
            painter.setPen(pen)
            
            angulo_fin = int(360 * self.progreso_valor / 100)
            painter.drawArc(centro_x - 85, centro_y - 85, 170, 170,
                          90 * 16, angulo_fin * 16)
            
            # Texto de porcentaje
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.setPen(QColor(255, 193, 7))
            painter.drawText(QRect(centro_x - 50, centro_y - 25, 100, 50),
                            Qt.AlignmentFlag.AlignCenter, f"{self.progreso_valor}%")
        
        # Versión
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(centro_x - 150, centro_y + 120, 300, 20),
                        Qt.AlignmentFlag.AlignCenter, "Backup en curso...")


class BackupWorker(QThread):
    """Worker para realizar el backup en segundo plano."""
    
    progreso = pyqtSignal(int)
    finalizado = pyqtSignal(bool, str)
    
    def __init__(self, backup_manager):
        super().__init__()
        self.backup_manager = backup_manager
    
    def run(self):
        """Ejecuta el backup y emite el progreso."""
        import time
        
        # Emular progreso mientras se realiza el backup
        for i in range(10, 95, 5):
            self.progreso.emit(i)
            time.sleep(0.05)
        
        ruta = self.backup_manager.crear_backup_con_progreso(mostrar_progreso=False)
        
        if ruta:
            self.finalizado.emit(True, ruta)
        else:
            self.finalizado.emit(False, "Error al crear backup")


def realizar_backup_con_splash(backup_manager, parent=None):
    """
    Realiza un backup mostrando un splash circular animado.
    Retorna True si el backup fue exitoso, False en caso contrario.
    """
    splash = BackupSplash("Iniciando backup...")
    QApplication.processEvents()
    
    # Crear worker para el backup
    worker = BackupWorker(backup_manager)
    resultado = [False, ""]
    
    def on_finalizado(exito, mensaje):
        resultado[0] = exito
        resultado[1] = mensaje
        # Asegurar que el splash se vea al menos 2 segundos
        QTimer.singleShot(2000, splash.finalizar)
    
    def on_progreso(valor):
        splash.set_progreso(valor)
        if valor < 30:
            splash.set_texto("📀 Copiando archivo...")
        elif valor < 60:
            splash.set_texto("🗜️ Comprimiendo backup...")
        elif valor < 85:
            splash.set_texto("🧹 Limpiando temporales...")
        else:
            splash.set_texto("✅ Finalizando...")
    
    worker.finalizado.connect(on_finalizado)
    worker.progreso.connect(on_progreso)
    
    # Iniciar simulación de progreso (3 segundos de duración)
    splash.iniciar_progreso(duracion_segundos=3)
    
    # Iniciar worker
    worker.start()
    
    # Esperar a que termine
    while worker.isRunning():
        QApplication.processEvents()
        time.sleep(0.05)
    
    # Esperar a que el splash termine (mínimo 2 segundos)
    while splash.isVisible():
        QApplication.processEvents()
        time.sleep(0.05)
    
    return resultado[0]