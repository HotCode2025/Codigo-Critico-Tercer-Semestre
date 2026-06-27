"""
Código Crítico - Tercer Semestre Año 2026
Punto de entrada principal - Splash redondo y login redondeado
CON ESCALADO GLOBAL NATIVO (QT_SCALE_FACTOR)
CON SELECTOR CIRCULAR DE RESOLUCIÓN MEJORADO
"""

import sys
import os
import math
import time
import threading

# Forzar X11 (Wayland no escala bien)
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Forzar escala antes de importar PyQt6
os.environ["QT_SCALE_FACTOR"] = "1.0"

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QBrush, QPen, QRegion, QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QDialog

# Asegurar el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_manager import inicializar_bd, obtener_conexion
from modelos.usuario import crear_usuario_admin


# ============================================================
# SELECTOR CIRCULAR CON PROGRESO - MEJORADO CON FOCUS ÓPTIMO
# ============================================================

class SelectorCircularEscala(QSplashScreen):
    def __init__(self):
        self.radius = 280
        pixmap = QPixmap(600, 600)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setMask(QRegion(0, 0, 600, 600, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)

        self.angulo = 0
        self.progreso = 0
        self.escala_seleccionada = 1.0
        self.seleccionado = False
        self.texto = "🖥️ SELECCIONE RESOLUCIÓN"
        
        self.opciones = [
            {"texto": "MEDIANO\n100%", "escala": 1.0, "color": "#2196F3", "color_hover": "#1565C0"},
            {"texto": "GRANDE\n130%", "escala": 1.3, "color": "#4CAF50", "color_hover": "#2E7D32"},
            {"texto": "MUY GRANDE\n160%", "escala": 1.6, "color": "#FF9800", "color_hover": "#E65100"}
        ]
        self.opcion_seleccionada = None
        self.opcion_hover = None
        
        self.animacion_clic = 0
        self.clic_pos = None
        self.timer_clic = QTimer()
        self.timer_clic.timeout.connect(self._actualizar_animacion_clic)
        self.timer_clic.setInterval(30)

        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulo)
        self.timer_animacion.start(50)

        self.timer_progreso = QTimer()
        self.timer_progreso.timeout.connect(self._actualizar_progreso)

        self.setMouseTracking(True)

        self.show()
        QApplication.processEvents()

    def _actualizar_angulo(self):
        self.angulo = (self.angulo + 4) % 360
        self.update()

    def _actualizar_progreso(self):
        if self.progreso < 100:
            self.progreso += 2
            self.update()
        else:
            self.timer_progreso.stop()
            self.timer_animacion.stop()
            QTimer.singleShot(300, self.close)

    def _actualizar_animacion_clic(self):
        self.animacion_clic += 2
        if self.animacion_clic > 30:
            self.timer_clic.stop()
            self.animacion_clic = 0
            self.clic_pos = None
        self.update()

    def iniciar_progreso(self):
        self.progreso = 0
        self.timer_progreso.start(30)

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        
        radio_interno = 70
        radio_externo = 260

        dist = ((x - centro_x) ** 2 + (y - centro_y) ** 2) ** 0.5
        
        idx_encontrado = None
        
        if radio_interno < dist < radio_externo:
            ang = (math.atan2(y - centro_y, x - centro_x) * 180 / math.pi + 90) % 360
            
            if 0 <= ang < 120:
                idx_encontrado = 0
            elif 120 <= ang < 240:
                idx_encontrado = 1
            else:
                idx_encontrado = 2
            
            angulo_boton = -90 + idx_encontrado * 120
            rad_boton = math.radians(angulo_boton)
            boton_x = centro_x + 155 * math.cos(rad_boton)
            boton_y = centro_y + 155 * math.sin(rad_boton)
            
            dist_boton = ((x - boton_x) ** 2 + (y - boton_y) ** 2) ** 0.5
            
            if dist_boton < 85:
                if self.opcion_hover != idx_encontrado:
                    self.opcion_hover = idx_encontrado
                    self.setCursor(Qt.CursorShape.PointingHandCursor)
                    self.update()
            else:
                distancias = []
                for i in range(3):
                    ang_b = -90 + i * 120
                    rad_b = math.radians(ang_b)
                    bx = centro_x + 155 * math.cos(rad_b)
                    by = centro_y + 155 * math.sin(rad_b)
                    d = ((x - bx) ** 2 + (y - by) ** 2) ** 0.5
                    distancias.append(d)
                
                min_dist = min(distancias)
                if min_dist < 100:
                    idx_cercano = distancias.index(min_dist)
                    if self.opcion_hover != idx_cercano:
                        self.opcion_hover = idx_cercano
                        self.setCursor(Qt.CursorShape.PointingHandCursor)
                        self.update()
                else:
                    if self.opcion_hover is not None:
                        self.opcion_hover = None
                        self.setCursor(Qt.CursorShape.ArrowCursor)
                        self.update()
        else:
            if self.opcion_hover is not None:
                self.opcion_hover = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
            
        x = event.pos().x()
        y = event.pos().y()
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        
        radio_interno = 60
        radio_externo = 270

        dist = ((x - centro_x) ** 2 + (y - centro_y) ** 2) ** 0.5
        
        idx_seleccionado = None
        
        if radio_interno < dist < radio_externo:
            ang = (math.atan2(y - centro_y, x - centro_x) * 180 / math.pi + 90) % 360
            
            if 0 <= ang < 120:
                idx_seleccionado = 0
            elif 120 <= ang < 240:
                idx_seleccionado = 1
            else:
                idx_seleccionado = 2
            
            angulo_boton = -90 + idx_seleccionado * 120
            rad_boton = math.radians(angulo_boton)
            boton_x = centro_x + 155 * math.cos(rad_boton)
            boton_y = centro_y + 155 * math.sin(rad_boton)
            
            dist_boton = ((x - boton_x) ** 2 + (y - boton_y) ** 2) ** 0.5
            
            if dist_boton < 85:
                self._seleccionar_opcion(idx_seleccionado, x, y)
                return
            
            distancias = []
            for i in range(3):
                ang_b = -90 + i * 120
                rad_b = math.radians(ang_b)
                bx = centro_x + 155 * math.cos(rad_b)
                by = centro_y + 155 * math.sin(rad_b)
                d = ((x - bx) ** 2 + (y - by) ** 2) ** 0.5
                distancias.append(d)
            
            min_dist = min(distancias)
            if min_dist < 110:
                idx_cercano = distancias.index(min_dist)
                self._seleccionar_opcion(idx_cercano, x, y)

    def _seleccionar_opcion(self, idx, x, y):
        self.opcion_seleccionada = idx
        self.escala_seleccionada = self.opciones[idx]["escala"]
        self.seleccionado = True
        self.texto = f"✅ {self.opciones[idx]['texto']}"
        
        self.clic_pos = (x, y)
        self.animacion_clic = 0
        self.timer_clic.start()
        
        self.update()
        
        QTimer.singleShot(200, self.iniciar_progreso)

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 250

        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))
        gradiente.setColorAt(0.5, QColor(21, 101, 192))
        gradiente.setColorAt(1, QColor(13, 71, 161))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        pen_zona = QPen()
        pen_zona.setWidth(1)
        pen_zona.setColor(QColor(255, 255, 255, 15))
        painter.setPen(pen_zona)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        for i in range(3):
            angulo = -90 + i * 120
            rad = math.radians(angulo)
            x1 = centro_x + 70 * math.cos(rad)
            y1 = centro_y + 70 * math.sin(rad)
            x2 = centro_x + 250 * math.cos(rad)
            y2 = centro_y + 250 * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        pen = QPen()
        pen.setWidth(4)

        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        painter.drawArc(centro_x - 200, centro_y - 200, 400, 400,
                       self.angulo * 16, 120 * 16)

        pen.setColor(QColor(33, 150, 243))
        painter.setPen(pen)
        painter.drawArc(centro_x - 175, centro_y - 175, 350, 350,
                       (360 - self.angulo) * 16, 90 * 16)

        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(centro_x - 150, centro_y - 150, 300, 300,
                       (self.angulo + 180) * 16, 80 * 16)

        painter.setPen(Qt.PenStyle.NoPen)
        op_radio = 155
        
        for i, op in enumerate(self.opciones):
            angulo = -90 + i * 120
            rad = math.radians(angulo)
            x = centro_x + op_radio * math.cos(rad)
            y = centro_y + op_radio * math.sin(rad)
            
            es_seleccionado = (self.opcion_seleccionada == i)
            es_hover = (self.opcion_hover == i)
            
            if es_seleccionado:
                radio_op = 72
                color = QColor(255, 193, 7)
                borde_color = QColor(255, 255, 255)
                borde_ancho = 5
            elif es_hover:
                radio_op = 66
                color = QColor(op["color_hover"])
                borde_color = QColor(255, 255, 255, 200)
                borde_ancho = 4
            else:
                radio_op = 58
                color = QColor(op["color"])
                borde_color = QColor(255, 255, 255, 100)
                borde_ancho = 3
            
            painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
            painter.drawEllipse(int(x - radio_op + 4), int(y - radio_op + 4), 
                               int(radio_op * 2), int(radio_op * 2))
            
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x - radio_op), int(y - radio_op), 
                               int(radio_op * 2), int(radio_op * 2))
            
            if not es_seleccionado:
                painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
                painter.drawEllipse(int(x - radio_op + 6), int(y - radio_op + 6), 
                                   int((radio_op - 8) * 2), int((radio_op - 12) * 2))
            
            if borde_ancho > 0:
                pen.setWidth(borde_ancho)
                pen.setColor(borde_color)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(int(x - radio_op), int(y - radio_op), 
                                   int(radio_op * 2), int(radio_op * 2))
                painter.setPen(Qt.PenStyle.NoPen)
            
            if es_seleccionado:
                painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            elif es_hover:
                painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            else:
                painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            
            painter.setPen(QColor(255, 255, 255))
            
            lineas = op["texto"].split("\n")
            for j, linea in enumerate(lineas):
                rect = QRect(int(x - 60), int(y - 24 + j * 24), 120, 30)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, linea)

        if self.clic_pos and self.animacion_clic > 0 and self.animacion_clic < 30:
            x, y = self.clic_pos
            radio_rizo = 5 + self.animacion_clic * 2
            
            pen_rizo = QPen()
            pen_rizo.setWidth(3)
            pen_rizo.setColor(QColor(255, 255, 255, int(120 - self.animacion_clic * 4)))
            painter.setPen(pen_rizo)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(int(x - radio_rizo), int(y - radio_rizo), 
                               int(radio_rizo * 2), int(radio_rizo * 2))
            
            pen_rizo2 = QPen()
            pen_rizo2.setWidth(2)
            pen_rizo2.setColor(QColor(255, 255, 255, int(200 - self.animacion_clic * 6)))
            painter.setPen(pen_rizo2)
            painter.drawEllipse(int(x - radio_rizo/2), int(y - radio_rizo/2), 
                               int(radio_rizo), int(radio_rizo))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        painter.drawEllipse(centro_x - 65, centro_y - 65, 130, 130)

        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(26, 35, 126))
        
        if self.seleccionado:
            texto_mostrar = self.texto
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        else:
            texto_mostrar = "🖥️\nToca\nuna opción"
            painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        rect_centro = QRect(centro_x - 60, centro_y - 40, 120, 80)
        painter.drawText(rect_centro, Qt.AlignmentFlag.AlignCenter, texto_mostrar)

        if self.progreso > 0:
            pen.setWidth(10)
            pen.setColor(QColor(76, 175, 80))
            painter.setPen(pen)
            
            angulo_fin = int(360 * self.progreso / 100)
            painter.drawArc(centro_x - 115, centro_y - 115, 230, 230,
                          90 * 16, angulo_fin * 16)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(76, 175, 80, 200)))
            painter.drawEllipse(centro_x - 32, centro_y + 65, 64, 38)
            
            painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255))
            rect_pct = QRect(centro_x - 32, centro_y + 65, 64, 38)
            painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, f"{self.progreso}%")
        
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(centro_x - 180, centro_y + 170, 360, 25),
                        Qt.AlignmentFlag.AlignCenter, "Seleccione una resolución")
        
        if self.seleccionado:
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor(255, 193, 7))
            painter.drawText(QRect(centro_x - 180, centro_y + 195, 360, 25),
                            Qt.AlignmentFlag.AlignCenter, "⏳ Aplicando configuración...")


# ============================================================
# SPLASH DE SINCRONIZACIÓN
# ============================================================

class SplashSincronizacion(QSplashScreen):
    """Splash que muestra el progreso de sincronización con la nube."""
    
    def __init__(self):
        pixmap = QPixmap(500, 500)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        self.setMask(QRegion(0, 0, 500, 500, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)
        self.setStyleSheet("background: transparent;")
        
        self.angulo = 0
        self.progreso = 0
        self.texto_estado = "Conectando con Turso..."
        self.detalle_estado = "Iniciando sincronización..."
        self._tiempo_inicio = time.time()
        
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulo)
        self.timer_animacion.start(50)
        
        self.timer_progreso = QTimer()
        self.timer_progreso.timeout.connect(self._actualizar_progreso_simulado)
        self.timer_progreso.start(100)
        
        self.show()
        QApplication.processEvents()
    
    def _actualizar_angulo(self):
        self.angulo = (self.angulo + 5) % 360
        self.update()
    
    def _actualizar_progreso_simulado(self):
        if self.progreso < 95:
            self.progreso += 1
            self.update()
    
    def set_estado(self, texto, detalle="", progreso=None):
        """Actualiza el estado mostrado en el splash."""
        self.texto_estado = texto
        if detalle:
            self.detalle_estado = detalle
        if progreso is not None:
            self.progreso = min(progreso, 95)
        self.update()
        QApplication.processEvents()
    
    def finalizar(self):
        """Finaliza el splash y cierra la ventana."""
        self.progreso = 100
        self.texto_estado = "✅ ¡Sincronización completada!"
        self.detalle_estado = "Datos actualizados correctamente"
        self.update()
        QApplication.processEvents()
        time.sleep(0.3)
        self.timer_animacion.stop()
        self.timer_progreso.stop()
        self.close()
    
    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 220
        
        # Fondo con gradiente
        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))
        gradiente.setColorAt(0.5, QColor(21, 101, 192))
        gradiente.setColorAt(1, QColor(13, 71, 161))
        
        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)
        
        # Anillos giratorios
        pen = QPen()
        pen.setWidth(4)
        
        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        painter.drawArc(centro_x - 170, centro_y - 170, 340, 340,
                       self.angulo * 16, 110 * 16)
        
        pen.setColor(QColor(33, 150, 243))
        painter.setPen(pen)
        painter.drawArc(centro_x - 150, centro_y - 150, 300, 300,
                       (360 - self.angulo) * 16, 80 * 16)
        
        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(centro_x - 130, centro_y - 130, 260, 260,
                       (self.angulo + 180) * 16, 70 * 16)
        
        # Icono de nube
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.drawEllipse(centro_x - 45, centro_y - 45, 90, 90)
        
        # Nube ☁️
        painter.setBrush(QBrush(QColor(33, 150, 243, 200)))
        painter.drawEllipse(centro_x - 25, centro_y - 25, 30, 22)
        painter.drawEllipse(centro_x + 5, centro_y - 30, 28, 24)
        painter.drawEllipse(centro_x - 10, centro_y - 35, 35, 26)
        painter.drawRoundedRect(centro_x - 30, centro_y - 18, 65, 22, 5, 5)
        
        # Flecha de sincronización
        pen.setWidth(3)
        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        
        painter.drawArc(centro_x - 20, centro_y - 20, 40, 40,
                       self.angulo * 16, 200 * 16)
        
        ang_flecha = math.radians(self.angulo + 200)
        fx = centro_x + 20 * math.cos(ang_flecha)
        fy = centro_y + 20 * math.sin(ang_flecha)
        painter.drawLine(int(fx), int(fy), int(fx - 8 * math.cos(ang_flecha - 0.5)), 
                        int(fy - 8 * math.sin(ang_flecha - 0.5)))
        painter.drawLine(int(fx), int(fy), int(fx - 8 * math.cos(ang_flecha + 0.5)), 
                        int(fy - 8 * math.sin(ang_flecha + 0.5)))
        
        # TEXTO - Estado principal
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawRoundedRect(centro_x - 160, centro_y + 55, 320, 30, 8, 8)
        
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QColor(26, 35, 126))
        painter.drawText(QRect(centro_x - 160, centro_y + 55, 320, 30),
                        Qt.AlignmentFlag.AlignCenter, self.texto_estado)
        
        # Detalle del estado
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(centro_x - 180, centro_y + 90, 360, 25),
                        Qt.AlignmentFlag.AlignCenter, self.detalle_estado)
        
        # Barra de progreso circular
        if self.progreso > 0:
            pen.setWidth(8)
            pen.setColor(QColor(76, 175, 80))
            painter.setPen(pen)
            
            angulo_fin = int(360 * self.progreso / 100)
            painter.drawArc(centro_x - 100, centro_y - 100, 200, 200,
                          90 * 16, angulo_fin * 16)
            
            # Porcentaje
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(76, 175, 80, 200)))
            painter.drawEllipse(centro_x - 28, centro_y + 125, 56, 34)
            
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255))
            rect_pct = QRect(centro_x - 28, centro_y + 125, 56, 34)
            painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, f"{self.progreso}%")
        
        # Versión
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(QRect(centro_x - 180, centro_y + 175, 360, 20),
                        Qt.AlignmentFlag.AlignCenter, "v3.0.0 - Código Crítico")


# ============================================================
# SPLASH DE INICIO - MEJORADO (texto más visible, 8 segundos)
# ============================================================

class SplashScreenConAnimacion(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(600, 600)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        self.setMask(QRegion(0, 0, 600, 600, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)
        self.setStyleSheet("background: transparent;")
        
        self.angulo = 0
        self.brillo = 0
        self.brillo_direccion = 1
        
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.actualizar_angulo)
        self.timer_animacion.start(40)
        
        self.timer_brillo = QTimer()
        self.timer_brillo.timeout.connect(self._actualizar_brillo)
        self.timer_brillo.start(50)

    def _actualizar_brillo(self):
        self.brillo += self.brillo_direccion * 8
        if self.brillo > 50:
            self.brillo = 50
            self.brillo_direccion = -1
        elif self.brillo < 0:
            self.brillo = 0
            self.brillo_direccion = 1
        self.update()

    def actualizar_angulo(self):
        self.angulo = (self.angulo + 6) % 360
        self.update()

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 250

        # Fondo con gradiente
        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(26, 35, 126))
        gradiente.setColorAt(0.5, QColor(21, 101, 192))
        gradiente.setColorAt(1, QColor(13, 71, 161))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        # Anillos giratorios
        pen = QPen()
        pen.setWidth(5)

        pen.setColor(QColor(255, 193, 7))
        painter.setPen(pen)
        painter.drawArc(centro_x - 200, centro_y - 200, 400, 400,
                       self.angulo * 16, 130 * 16)

        pen.setColor(QColor(33, 150, 243))
        painter.setPen(pen)
        painter.drawArc(centro_x - 175, centro_y - 175, 350, 350,
                       (360 - self.angulo) * 16, 100 * 16)

        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(centro_x - 150, centro_y - 150, 300, 300,
                       (self.angulo + 180) * 16, 90 * 16)

        # Círculo central
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - 60, centro_y - 60, 120, 120)

        pen.setWidth(3)
        pen.setColor(QColor(255, 193, 7, 180))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(centro_x - 60, centro_y - 60, 120, 120)
        painter.setPen(Qt.PenStyle.NoPen)

        # Logo
        painter.setBrush(QBrush(QColor(26, 35, 126)))
        painter.drawRect(centro_x - 35, centro_y - 40, 60, 30)
        
        painter.setBrush(QBrush(QColor(255, 193, 7)))
        painter.drawRect(centro_x - 40, centro_y - 45, 70, 12)
        
        pen.setWidth(2)
        pen.setColor(QColor(255, 255, 255, 150))
        painter.setPen(pen)
        painter.drawLine(centro_x - 25, centro_y - 30, centro_x + 25, centro_y - 30)
        painter.drawLine(centro_x - 25, centro_y - 20, centro_x + 25, centro_y - 20)
        painter.drawLine(centro_x - 15, centro_y - 10, centro_x + 15, centro_y - 10)
        painter.setPen(Qt.PenStyle.NoPen)

        # ============================================================
        # TEXTO PRINCIPAL - MÁS VISIBLE (blanco con sombra)
        # ============================================================
        
        # Sombra del texto
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QColor(0, 0, 0, 60))
        painter.drawText(QRect(centro_x - 178, centro_y + 47, 360, 35),
                        Qt.AlignmentFlag.AlignCenter, "Sistema de")
        
        # Texto principal "Sistema de" (blanco)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(centro_x - 180, centro_y + 45, 360, 35),
                        Qt.AlignmentFlag.AlignCenter, "Sistema de")

        # Sombra del título principal
        painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        painter.setPen(QColor(0, 0, 0, 60))
        painter.drawText(QRect(centro_x - 218, centro_y + 77, 440, 45),
                        Qt.AlignmentFlag.AlignCenter, "Distribución y Logística")
        
        # Texto principal "Distribución y Logística" (dorado con brillo)
        brillo = 200 + self.brillo
        painter.setPen(QColor(255, 193, 7, min(brillo, 255)))
        painter.drawText(QRect(centro_x - 220, centro_y + 75, 440, 45),
                        Qt.AlignmentFlag.AlignCenter, "Distribución y Logística")

        # Versión
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRect(centro_x - 180, centro_y + 120, 360, 25),
                        Qt.AlignmentFlag.AlignCenter, "v3.0.0 - Código Crítico")

        # Estado de carga
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        
        puntos = "." * (int(self.angulo / 60) % 4)
        painter.drawText(QRect(centro_x - 180, centro_y + 155, 360, 30),
                        Qt.AlignmentFlag.AlignCenter, f"Iniciando sistema{puntos}")

        # Barra de progreso circular decorativa
        pen.setWidth(6)
        pen.setColor(QColor(76, 175, 80, 180))
        painter.setPen(pen)
        
        angulo_progreso = int(360 * (self.angulo % 360) / 360)
        painter.drawArc(centro_x - 85, centro_y - 85, 170, 170,
                       90 * 16, angulo_progreso * 16)

        # Pie de página
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(QRect(centro_x - 180, centro_y + 195, 360, 20),
                        Qt.AlignmentFlag.AlignCenter, "Preparando el sistema...")

    def cerrar(self):
        self.timer_animacion.stop()
        self.timer_brillo.stop()
        self.hide()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("=" * 60)
    print("   SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA")
    print("   Código Crítico - Tercer Semestre 2026")
    print("=" * 60)

    # ============================================================
    # 1. INICIALIZAR BASE DE DATOS
    # ============================================================
    print("\n📁 Inicializando base de datos...")
    inicializar_bd()
    print("✅ Base de datos lista.")

    db = obtener_conexion()
    crear_usuario_admin(db)
    db.close()

    # ============================================================
    # 2. MOSTRAR SELECTOR CIRCULAR DE ESCALA
    # ============================================================
    app_temp = QApplication(sys.argv)
    app_temp.setStyle("Fusion")

    selector = SelectorCircularEscala()
    
    while not selector.seleccionado:
        app_temp.processEvents()
        if selector.isHidden():
            break
    
    while selector.progreso < 100 and not selector.isHidden():
        app_temp.processEvents()
    
    factor_escala = selector.escala_seleccionada
    print(f"📐 Factor de escala seleccionado: {factor_escala}")

    selector.close()
    app_temp.quit()
    app_temp = None

    # ============================================================
    # 3. APLICAR ESCALA GLOBAL
    # ============================================================
    os.environ["QT_SCALE_FACTOR"] = str(factor_escala)
    os.environ["QT_FONT_DPI"] = str(int(96 * factor_escala))

    print(f"✅ Escala global aplicada: {factor_escala * 100}%")
    print(f"📐 QT_SCALE_FACTOR = {os.environ.get('QT_SCALE_FACTOR')}")

    # ============================================================
    # 4. IMPORTAR MÓDULOS
    # ============================================================
    from vistas.ventana_principal import VentanaPrincipal, DialogoLogin

    # ============================================================
    # 5. CREAR APP FINAL
    # ============================================================
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Sistema Distribución y Logística")
    app.setOrganizationName("CodigoCritico")

    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # ============================================================
    # 6. SPLASH DE SINCRONIZACIÓN
    # ============================================================
    splash_sync = SplashSincronizacion()
    app.processEvents()
    print("✅ Splash de sincronización mostrado")

    # ============================================================
    # 7. INICIAR SINCRONIZACIÓN CON TURSO (CON PROGRESO REAL)
    # ============================================================
    
    errores_criticos = False
    
    try:
        from utilidades.central_sync import iniciar_sincronizacion_auto, sincronizar_desde_central, verificar_conexion_turso
        from controladores.controlador_ventas import ControladorVentas
        
        # ============================================================
        # ETAPA 1: VERIFICAR CONEXIÓN
        # ============================================================
        splash_sync.set_estado("🔍 Verificando conexión...", "Comprobando conexión con Turso", 5)
        time.sleep(0.3)
        
        conexion_ok = verificar_conexion_turso()
        
        if not conexion_ok:
            splash_sync.set_estado("⚠️ Sin conexión a Turso", "Intentando reconectar...", 10)
            time.sleep(1)
            conexion_ok = verificar_conexion_turso()
        
        if not conexion_ok:
            splash_sync.set_estado("⚠️ Sin conexión a Turso", "Los datos se sincronizarán cuando haya conexión", 15)
            time.sleep(1)
        else:
            splash_sync.set_estado("✅ Conectado a Turso", "Conexión establecida correctamente", 15)
            time.sleep(0.5)
        
        # ============================================================
        # ETAPA 2: INICIAR SINCRONIZACIÓN AUTOMÁTICA
        # ============================================================
        splash_sync.set_estado("🔄 Iniciando sincronización...", "Activando sincronización automática", 20)
        iniciar_sincronizacion_auto()
        time.sleep(0.5)
        splash_sync.set_estado("✅ Sincronización activa", "Los cambios se sincronizarán automáticamente", 25)
        time.sleep(0.3)
        
        # ============================================================
        # ETAPA 3: SINCRONIZAR DATOS DESDE CENTRAL A TURSO
        # ============================================================
        splash_sync.set_estado("📤 Enviando datos a la nube...", "Sincronizando clientes, productos y stock", 30)
        time.sleep(0.3)
        
        try:
            sincronizar_desde_central()
            splash_sync.set_estado("✅ Datos enviados", "Catálogo sincronizado correctamente", 55)
        except Exception as e:
            print(f"⚠️ Error en sincronización de datos: {e}")
            splash_sync.set_estado("⚠️ Error al sincronizar", "Algunos datos no se enviaron", 50)
        time.sleep(0.5)
        
        # ============================================================
        # ETAPA 4: RECIBIR DATOS DESDE TURSO (NOTAS DE VENTA)
        # ============================================================
        splash_sync.set_estado("📥 Recibiendo notas de venta...", "Descargando pedidos desde la nube", 60)
        time.sleep(0.3)
        
        try:
            from utilidades.central_sync import get_sincronizador
            sincronizador = get_sincronizador()
            sincronizador.sincronizar_ahora()
            splash_sync.set_estado("✅ Notas recibidas", "Pedidos descargados correctamente", 70)
        except Exception as e:
            print(f"⚠️ Error al recibir notas: {e}")
            splash_sync.set_estado("⚠️ Error al recibir notas", "Se reintentará automáticamente", 65)
        time.sleep(0.5)
        
        # ============================================================
        # ETAPA 5: PROCESAR NOTAS PENDIENTES (codigo_producto → producto_id)
        # ============================================================
        splash_sync.set_estado("📋 Procesando notas locales...", "Convirtiendo códigos de productos", 75)
        time.sleep(0.3)
        
        try:
            db_conn = obtener_conexion()
            ctrl_ventas = ControladorVentas(db_conn)
            procesadas = ctrl_ventas.procesar_notas_pendientes()
            db_conn.close()
            
            if procesadas > 0:
                splash_sync.set_estado(f"✅ {procesadas} notas procesadas", "Códigos convertidos correctamente", 85)
            else:
                splash_sync.set_estado("✅ Sin notas pendientes", "Todos los datos están actualizados", 85)
        except Exception as e:
            print(f"⚠️ Error procesando notas: {e}")
            splash_sync.set_estado("⚠️ Error procesando notas", "Algunas notas no se pudieron procesar", 80)
        time.sleep(0.5)
        
        # ============================================================
        # ETAPA 6: FINALIZAR
        # ============================================================
        splash_sync.set_estado("✅ ¡Sincronización completada!", "Todos los datos están actualizados", 95)
        time.sleep(0.5)
        
        print("✅ Sincronización completada correctamente")
        
    except Exception as e:
        print(f"❌ Error crítico en sincronización: {e}")
        errores_criticos = True
        splash_sync.set_estado("❌ Error en sincronización", "Reiniciando sistema...", 50)
        time.sleep(2)

    # ============================================================
    # 8. CERRAR SPLASH DE SINCRONIZACIÓN (CON TIEMPO MÍNIMO)
    # ============================================================
    
    if errores_criticos:
        time.sleep(1)
    
    # ✅ FORZAR que el splash se vea al menos 8 segundos
    tiempo_transcurrido = time.time() - splash_sync._tiempo_inicio
    
    if tiempo_transcurrido < 8:
        tiempo_restante = 8 - tiempo_transcurrido
        print(f"⏳ Esperando {tiempo_restante:.1f} segundos...")
        
        splash_sync.set_estado("⏳ Finalizando...", f"Esperando {int(tiempo_restante)} segundos", 98)
        
        pasos = int(tiempo_restante * 10)
        for i in range(pasos):
            time.sleep(0.1)
            if i % 10 == 0:
                splash_sync.update()
                QApplication.processEvents()
    
    # ✅ Cerrar splash de sincronización
    splash_sync.finalizar()
    app.processEvents()
    print("✅ Splash de sincronización cerrado")

    # ============================================================
    # 9. SPLASH DE INICIO (mejorado, 8 segundos)
    # ============================================================
    splash = SplashScreenConAnimacion()
    splash.show()
    app.processEvents()
    print("✅ Splash de inicio mostrado (8 segundos)")

    # ============================================================
    # 10. LOGIN Y VENTANA PRINCIPAL
    # ============================================================
    ventana = None

    def mostrar_login():
        nonlocal ventana
        splash.cerrar()

        db = obtener_conexion()
        login = DialogoLogin(db)

        if login.exec() == QDialog.DialogCode.Accepted:
            ventana = VentanaPrincipal(usuario=login.usuario_actual)
            ventana.show()
            ventana.raise_()
            ventana.activateWindow()
            ventana.setWindowState(ventana.windowState() & ~Qt.WindowState.WindowMinimized)
            ventana.repaint()
            QApplication.processEvents()
            print("✅ Ventana principal mostrada")
            print(f"📐 Escala aplicada: {factor_escala * 100}%")
        else:
            print("❌ Login cancelado. Saliendo...")
            app.quit()

    QTimer.singleShot(8000, mostrar_login)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()