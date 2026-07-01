"""
Código Crítico - Tercer Semestre Año 2026
==================================================
main.py - Punto de entrada del sistema
==================================================
"""

import sys
import os
import time
import math
import threading
from datetime import datetime

# ============================================================
# CONFIGURACIÓN ANTES DE IMPORTAR PyQt6
# ============================================================

# Forzar X11 (Wayland no escala bien)
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_SCALE_FACTOR"] = "1.0"

# ============================================================
# IMPORTAR PyQt6 - CONFIGURACIÓN PARA WEBENGINE
# ============================================================

from PyQt6.QtCore import Qt, QTimer, QRect, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QDialog
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QBrush, QPen, QRegion

# ✅ CONFIGURAR WEBENGINE ANTES DE CREAR LA APP
Qt.AA_ShareOpenGLContexts = Qt.ApplicationAttribute.AA_ShareOpenGLContexts

# Asegurar el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_manager import inicializar_bd, obtener_conexion
from modelos.usuario import crear_usuario_admin
from utilidades import (
    verificar_conexion_turso,
    iniciar_sincronizacion_auto, 
    sincronizar_ahora
)
from utilidades.sync_directo import iniciar, detener

# ✅ IMPORTAR VENTANA PRINCIPAL Y LOGIN
from vistas.ventana_principal import VentanaPrincipal, DialogoLogin


# ============================================================
# SELECTOR CIRCULAR DE ESCALA - 800x800 CON EFECTOS MEJORADOS
# ============================================================

class SelectorCircularEscala(QSplashScreen):
    """Splash circular para seleccionar escala - 800x800 con efectos mejorados"""
    
    def __init__(self):
        pixmap = QPixmap(800, 800)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setMask(QRegion(0, 0, 800, 800, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)

        self.angulo1 = 0      # Anillo exterior
        self.angulo2 = 0      # Anillo medio
        self.angulo3 = 0      # Anillo interior
        self.progreso = 0
        self.escala_seleccionada = 1.0
        self.seleccionado = False
        self.texto = "🖥️ SELECCIONE\nRESOLUCIÓN"
        
        # Opciones con más espacio entre botones
        self.opciones = [
            {"texto": "MEDIANO\n100%", "escala": 1.0, "color": "#2196F3", "angulo": -90},
            {"texto": "GRANDE\n130%", "escala": 1.3, "color": "#4CAF50", "angulo": 30},
            {"texto": "MUY GRANDE\n160%", "escala": 1.6, "color": "#FF9800", "angulo": 150}
        ]
        self.opcion_seleccionada = None
        
        # Timer para animación
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulos)
        self.timer_animacion.start(30)

        self.timer_progreso = QTimer()
        self.timer_progreso.timeout.connect(self._actualizar_progreso)

        self.show()
        QApplication.processEvents()

    def _actualizar_angulos(self):
        self.angulo1 = (self.angulo1 + 3) % 360
        self.angulo2 = (self.angulo2 + 5) % 360
        self.angulo3 = (self.angulo3 + 7) % 360
        self.update()

    def _actualizar_progreso(self):
        if self.progreso < 100:
            self.progreso += 2
            self.update()
        else:
            self.timer_progreso.stop()
            self.timer_animacion.stop()
            QTimer.singleShot(300, self.close)

    def iniciar_progreso(self):
        self.progreso = 0
        self.timer_progreso.start(30)

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        
        radio_interno = 150
        radio_externo = 310

        dist = ((x - centro_x) ** 2 + (y - centro_y) ** 2) ** 0.5
        if radio_interno < dist < radio_externo:
            ang = (math.atan2(y - centro_y, x - centro_x) * 180 / math.pi + 90) % 360
            
            if -60 <= ang < 60:
                idx = 0
            elif 60 <= ang < 180:
                idx = 1
            else:
                idx = 2
            
            self.opcion_seleccionada = idx
            self.escala_seleccionada = self.opciones[idx]["escala"]
            self.seleccionado = True
            self.texto = f"✅ {self.opciones[idx]['texto']}"
            self.iniciar_progreso()

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 380

        # Fondo con gradiente
        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(13, 71, 161))
        gradiente.setColorAt(0.5, QColor(21, 101, 192))
        gradiente.setColorAt(1, QColor(26, 35, 126))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        # ============================================================
        # ANILLOS GIRATORIOS CON EFECTO LIGHT
        # ============================================================
        
        # Anillo 1 (exterior) - Naranja/Dorado con glow
        pen = QPen()
        pen.setWidth(5)
        pen.setColor(QColor(255, 193, 7, 200))
        painter.setPen(pen)
        painter.drawArc(centro_x - 320, centro_y - 320, 640, 640,
                       self.angulo1 * 16, 100 * 16)
        
        pen.setColor(QColor(255, 193, 7, 80))
        pen.setWidth(12)
        painter.setPen(pen)
        painter.drawArc(centro_x - 320, centro_y - 320, 640, 640,
                       (self.angulo1 + 30) * 16, 40 * 16)

        # Anillo 2 (medio) - Azul con glow
        pen.setColor(QColor(33, 150, 243, 200))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawArc(centro_x - 290, centro_y - 290, 580, 580,
                       (360 - self.angulo2) * 16, 80 * 16)
        
        pen.setColor(QColor(33, 150, 243, 80))
        pen.setWidth(12)
        painter.setPen(pen)
        painter.drawArc(centro_x - 290, centro_y - 290, 580, 580,
                       (360 - self.angulo2 + 30) * 16, 30 * 16)

        # Anillo 3 (interior) - Verde con glow
        pen.setColor(QColor(76, 175, 80, 200))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawArc(centro_x - 260, centro_y - 260, 520, 520,
                       (self.angulo3 + 180) * 16, 70 * 16)
        
        pen.setColor(QColor(76, 175, 80, 80))
        pen.setWidth(12)
        painter.setPen(pen)
        painter.drawArc(centro_x - 260, centro_y - 260, 520, 520,
                       (self.angulo3 + 210) * 16, 30 * 16)

        # Puntos luminosos
        for i in range(12):
            ang = i * 30 + self.angulo1
            rad = math.radians(ang)
            px = centro_x + 320 * math.cos(rad)
            py = centro_y + 320 * math.sin(rad)
            
            brillo = 150 + 105 * math.sin(math.radians(i * 30 + self.angulo1))
            painter.setBrush(QBrush(QColor(255, 193, 7, int(brillo))))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(px - 4), int(py - 4), 8, 8)

        # ============================================================
        # BOTONES CIRCULARES
        # ============================================================
        op_radio = 230
        boton_radio = 75
        
        for i, op in enumerate(self.opciones):
            angulo_rad = math.radians(op["angulo"])
            x = centro_x + op_radio * math.cos(angulo_rad)
            y = centro_y + op_radio * math.sin(angulo_rad)
            
            is_selected = self.opcion_seleccionada == i
            
            # Sombra del botón
            painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x - boton_radio + 6), int(y - boton_radio + 6), 
                               int(boton_radio * 2), int(boton_radio * 2))
            
            # Fondo del botón con gradiente
            if is_selected:
                grad_boton = QLinearGradient(x - boton_radio, y - boton_radio, 
                                              x + boton_radio, y + boton_radio)
                grad_boton.setColorAt(0, QColor(255, 215, 0))
                grad_boton.setColorAt(1, QColor(255, 193, 7))
                painter.setBrush(QBrush(grad_boton))
                painter.setPen(QPen(QColor(255, 255, 255), 4))
            else:
                grad_boton = QLinearGradient(x - boton_radio, y - boton_radio, 
                                              x + boton_radio, y + boton_radio)
                grad_boton.setColorAt(0, QColor(op["color"]))
                grad_boton.setColorAt(1, QColor(op["color"]).darker(150))
                painter.setBrush(QBrush(grad_boton))
                painter.setPen(QPen(QColor(255, 255, 255, 150), 3))
            
            painter.drawEllipse(int(x - boton_radio), int(y - boton_radio), 
                               int(boton_radio * 2), int(boton_radio * 2))
            
            # Efecto light en el botón
            if not is_selected:
                painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(x - boton_radio + 10), int(y - boton_radio + 10), 
                                   int(boton_radio * 0.8), int(boton_radio * 0.8))
            
            # Texto del botón
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(QFont("Segoe UI", 14 if is_selected else 12, 
                                  QFont.Weight.Bold if is_selected else QFont.Weight.DemiBold))
            
            lineas = op["texto"].split("\n")
            for j, linea in enumerate(lineas):
                rect = QRect(int(x - 70), int(y - 30 + j * 32), 140, 35)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, linea)
            
            # Check en botón seleccionado
            if is_selected:
                painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
                painter.setPen(Qt.PenStyle.NoPen)
                cx = int(x + boton_radio - 25)
                cy = int(y - boton_radio + 15)
                painter.drawEllipse(cx, cy, 18, 18)
                painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
                painter.setPen(QPen(QColor(26, 35, 126)))
                painter.drawText(QRect(cx - 18, cy - 18, 36, 36),
                                Qt.AlignmentFlag.AlignCenter, "✓")

        # ============================================================
        # CENTRO - LOGO Y TEXTO
        # ============================================================
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
        painter.drawEllipse(centro_x - 100, centro_y - 100, 200, 200)

        painter.setFont(QFont("Segoe UI", 42))
        painter.setPen(QPen(QColor(26, 35, 126)))
        painter.drawText(QRect(centro_x - 60, centro_y - 45, 120, 60),
                        Qt.AlignmentFlag.AlignCenter, "🖥️")
        
        if self.seleccionado:
            texto_mostrar = self.texto.replace("✅ ", "")
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(76, 175, 80)))
        else:
            texto_mostrar = "Toca un\nbotón"
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(26, 35, 126)))
        
        rect_centro = QRect(centro_x - 80, centro_y + 15, 160, 50)
        painter.drawText(rect_centro, Qt.AlignmentFlag.AlignCenter, texto_mostrar)

        # Barra de progreso circular
        if self.progreso > 0:
            pen.setWidth(14)
            pen.setColor(QColor(76, 175, 80))
            painter.setPen(pen)
            
            angulo_fin = int(360 * self.progreso / 100)
            painter.drawArc(centro_x - 140, centro_y - 140, 280, 280,
                          90 * 16, angulo_fin * 16)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(76, 175, 80, 220)))
            painter.drawEllipse(centro_x - 45, centro_y + 110, 90, 45)
            
            painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(255, 255, 255)))
            rect_pct = QRect(centro_x - 45, centro_y + 110, 90, 45)
            painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, f"{self.progreso}%")
        
        # Pie de página
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.drawText(QRect(centro_x - 300, centro_y + 280, 600, 30),
                        Qt.AlignmentFlag.AlignCenter, "v3.0.0 - Código Crítico - UUID")
        
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QPen(QColor(130, 130, 130, 180)))
        painter.drawText(QRect(centro_x - 300, centro_y + 310, 600, 25),
                        Qt.AlignmentFlag.AlignCenter, "Seleccione una resolución y toque el botón")


# ============================================================
# HILO DE SINCRONIZACIÓN
# ============================================================

class SyncThread(QThread):
    progreso = pyqtSignal(str, str, int)
    finalizado = pyqtSignal(bool, str)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._is_running = True
    
    def stop(self):
        self._is_running = False
    
    def run(self):
        try:
            self.progreso.emit("🔍 Verificando conexión...", "Comprobando conexión con Turso", 5)
            self._esperar(2)
            
            conexion_ok = verificar_conexion_turso()
            
            if not conexion_ok:
                self.progreso.emit("⚠️ Sin conexión a Turso", "Intentando reconectar...", 10)
                self._esperar(1)
                conexion_ok = verificar_conexion_turso()
            
            if not conexion_ok:
                self.progreso.emit("⚠️ Sin conexión a Turso", "Datos locales - sincronización pendiente", 15)
                self._esperar(1)
                self.finalizado.emit(False, "Sin conexión a Turso")
                return
            
            self.progreso.emit("✅ Conectado a Turso", "Conexión establecida", 15)
            self._esperar(0.5)
            
            self.progreso.emit("📤 Enviando datos a la nube...", "Sincronizando...", 30)
            
            try:
                resultado = sincronizar_ahora(self.db)
                enviados = 0
                central_a_turso = resultado.get('central_a_turso', {})
                for tabla, res in central_a_turso.items():
                    enviados += res.get('sent', 0)
                
                self.progreso.emit(
                    f"✅ {enviados} registros enviados",
                    "Datos sincronizados correctamente",
                    95
                )
                self._esperar(1)
            except Exception as e:
                self.progreso.emit("⚠️ Error parcial", f"{str(e)[:30]}", 80)
                self._esperar(1)
            
            self.progreso.emit("✅ ¡Sincronización completada!", "Todos los datos están actualizados", 100)
            self._esperar(0.5)
            self.finalizado.emit(True, "Sincronización exitosa")
            
        except Exception as e:
            self.progreso.emit("❌ Error", f"Error en sincronización: {str(e)[:50]}", 50)
            self._esperar(1)
            self.finalizado.emit(False, str(e))
    
    def _esperar(self, segundos):
        for _ in range(int(segundos * 10)):
            if not self._is_running:
                break
            time.sleep(0.1)
            QApplication.processEvents()


# ============================================================
# SPLASH DE SINCRONIZACIÓN - 800x800 CON EFECTO DE LUJO
# ============================================================

class SplashSincronizacion(QSplashScreen):
    """Splash circular de sincronización - 800x800 con efectos de lujo"""
    
    def __init__(self):
        pixmap = QPixmap(800, 800)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        self.setMask(QRegion(0, 0, 800, 800, QRegion.RegionType.Ellipse))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.SplashScreen)
        self.setStyleSheet("background: transparent;")
        
        # Ángulos para los tres anillos
        self.angulo1 = 0
        self.angulo2 = 0
        self.angulo3 = 0
        
        self.progreso = 0
        self.texto_estado = "🔄 Conectando con Turso..."
        self.detalle_estado = "Iniciando sincronización..."
        self._sync_thread = None
        
        # Timer para animación de anillos
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self._actualizar_angulos)
        self.timer_animacion.start(30)
        
        self.show()
        QApplication.processEvents()
    
    def _actualizar_angulos(self):
        self.angulo1 = (self.angulo1 + 3) % 360
        self.angulo2 = (self.angulo2 + 5) % 360
        self.angulo3 = (self.angulo3 + 7) % 360
        self.update()
    
    def set_estado(self, texto, detalle="", progreso=None):
        self.texto_estado = texto
        if detalle:
            self.detalle_estado = detalle
        if progreso is not None:
            self.progreso = min(progreso, 100)
        self.update()
        QApplication.processEvents()
    
    def ejecutar_sincronizacion(self, db):
        self._sync_thread = SyncThread(db)
        self._sync_thread.progreso.connect(self._on_progreso)
        self._sync_thread.finalizado.connect(self._on_finalizado)
        self._sync_thread.start()
    
    def _on_progreso(self, texto, detalle, progreso):
        self.set_estado(texto, detalle, progreso)
    
    def _on_finalizado(self, exito, mensaje):
        if exito:
            self.set_estado("✅ ¡Sincronización completada!", mensaje, 100)
        else:
            self.set_estado("⚠️ Sincronización incompleta", mensaje, 80)
        QTimer.singleShot(1500, self.close)
    
    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        centro_x = self.width() // 2
        centro_y = self.height() // 2
        radio = 370

        # ============================================================
        # FONDO CON GRADIENTE RADIAL DE LUJO
        # ============================================================
        gradiente = QLinearGradient(centro_x - radio, centro_y - radio, 
                                     centro_x + radio, centro_y + radio)
        gradiente.setColorAt(0, QColor(13, 71, 161))
        gradiente.setColorAt(0.4, QColor(21, 101, 192))
        gradiente.setColorAt(0.7, QColor(26, 35, 126))
        gradiente.setColorAt(1, QColor(10, 20, 60))

        painter.setBrush(QBrush(gradiente))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(centro_x - radio, centro_y - radio, radio * 2, radio * 2)

        # ============================================================
        # ANILLOS GIRATORIOS CON EFECTO DE LUJO Y GLOW
        # ============================================================
        
        # Anillo 1 (exterior) - Dorado con glow
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(QColor(255, 215, 0, 200))
        painter.setPen(pen)
        painter.drawArc(centro_x - 320, centro_y - 320, 640, 640,
                       self.angulo1 * 16, 120 * 16)
        
        pen.setColor(QColor(255, 215, 0, 60))
        pen.setWidth(14)
        painter.setPen(pen)
        painter.drawArc(centro_x - 320, centro_y - 320, 640, 640,
                       (self.angulo1 + 30) * 16, 60 * 16)
        
        # Puntos luminosos en anillo 1
        for i in range(8):
            ang = i * 45 + self.angulo1
            rad = math.radians(ang)
            px = centro_x + 320 * math.cos(rad)
            py = centro_y + 320 * math.sin(rad)
            brillo = 150 + 105 * math.sin(math.radians(i * 45 + self.angulo1 * 2))
            painter.setBrush(QBrush(QColor(255, 215, 0, int(brillo))))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(px - 5), int(py - 5), 10, 10)

        # Anillo 2 (medio) - Azul eléctrico con glow
        pen.setWidth(4)
        pen.setColor(QColor(33, 150, 243, 200))
        painter.setPen(pen)
        painter.drawArc(centro_x - 280, centro_y - 280, 560, 560,
                       (360 - self.angulo2) * 16, 100 * 16)
        
        pen.setColor(QColor(33, 150, 243, 60))
        pen.setWidth(14)
        painter.setPen(pen)
        painter.drawArc(centro_x - 280, centro_y - 280, 560, 560,
                       (360 - self.angulo2 + 30) * 16, 50 * 16)
        
        # Puntos luminosos en anillo 2
        for i in range(6):
            ang = i * 60 + self.angulo2
            rad = math.radians(ang)
            px = centro_x + 280 * math.cos(rad)
            py = centro_y + 280 * math.sin(rad)
            brillo = 150 + 105 * math.sin(math.radians(i * 60 + self.angulo2 * 2))
            painter.setBrush(QBrush(QColor(33, 150, 243, int(brillo))))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(px - 4), int(py - 4), 8, 8)

        # Anillo 3 (interior) - Verde esmeralda con glow
        pen.setWidth(4)
        pen.setColor(QColor(76, 175, 80, 200))
        painter.setPen(pen)
        painter.drawArc(centro_x - 240, centro_y - 240, 480, 480,
                       (self.angulo3 + 180) * 16, 80 * 16)
        
        pen.setColor(QColor(76, 175, 80, 60))
        pen.setWidth(14)
        painter.setPen(pen)
        painter.drawArc(centro_x - 240, centro_y - 240, 480, 480,
                       (self.angulo3 + 210) * 16, 40 * 16)
        
        # Puntos luminosos en anillo 3
        for i in range(4):
            ang = i * 90 + self.angulo3
            rad = math.radians(ang)
            px = centro_x + 240 * math.cos(rad)
            py = centro_y + 240 * math.sin(rad)
            brillo = 150 + 105 * math.sin(math.radians(i * 90 + self.angulo3 * 2))
            painter.setBrush(QBrush(QColor(76, 175, 80, int(brillo))))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(px - 4), int(py - 4), 8, 8)

        # ============================================================
        # ICONO CENTRAL CON EFECTO DE LUJO
        # ============================================================
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Círculo interior con gradiente
        grad_center = QLinearGradient(centro_x - 100, centro_y - 100, 
                                       centro_x + 100, centro_y + 100)
        grad_center.setColorAt(0, QColor(255, 255, 255, 250))
        grad_center.setColorAt(1, QColor(220, 230, 255, 250))
        painter.setBrush(QBrush(grad_center))
        painter.drawEllipse(centro_x - 100, centro_y - 100, 200, 200)
        
        # Borde brillante del círculo interior
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen.setWidth(3)
        pen.setColor(QColor(255, 215, 0, 150))
        painter.setPen(pen)
        painter.drawEllipse(centro_x - 100, centro_y - 100, 200, 200)
        
        # Icono de base de datos estilizado
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(26, 35, 126, 230)))
        
        painter.drawEllipse(centro_x - 45, centro_y - 45, 90, 30)
        painter.drawRect(centro_x - 45, centro_y - 45, 90, 60)
        painter.drawEllipse(centro_x - 45, centro_y + 15, 90, 30)
        
        pen.setColor(QColor(255, 255, 255, 100))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawArc(centro_x - 35, centro_y - 40, 70, 20, 0, 180 * 16)
        painter.drawArc(centro_x - 35, centro_y + 10, 70, 20, 0, 180 * 16)

        # ============================================================
        # TEXTO DE ESTADO CENTRAL
        # ============================================================
        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(26, 35, 126)))
        
        rect_texto = QRect(centro_x - 160, centro_y + 50, 320, 35)
        painter.drawText(rect_texto, Qt.AlignmentFlag.AlignCenter, self.texto_estado)
        
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QPen(QColor(80, 80, 80)))
        rect_detalle = QRect(centro_x - 180, centro_y + 85, 360, 25)
        painter.drawText(rect_detalle, Qt.AlignmentFlag.AlignCenter, self.detalle_estado)

        # ============================================================
        # BARRA DE PROGRESO CIRCULAR DE LUJO
        # ============================================================
        if self.progreso > 0:
            pen.setWidth(8)
            pen.setColor(QColor(76, 175, 80, 200))
            painter.setPen(pen)
            
            angulo_fin = int(360 * self.progreso / 100)
            painter.drawArc(centro_x - 130, centro_y - 130, 260, 260,
                          90 * 16, angulo_fin * 16)
            
            pen.setColor(QColor(76, 175, 80, 50))
            pen.setWidth(18)
            painter.setPen(pen)
            painter.drawArc(centro_x - 130, centro_y - 130, 260, 260,
                          90 * 16, angulo_fin * 16)
            
            painter.setPen(Qt.PenStyle.NoPen)
            grad_pct = QLinearGradient(centro_x - 40, centro_y + 125, 
                                        centro_x + 40, centro_y + 165)
            grad_pct.setColorAt(0, QColor(76, 175, 80, 230))
            grad_pct.setColorAt(1, QColor(46, 125, 50, 230))
            painter.setBrush(QBrush(grad_pct))
            painter.drawRoundedRect(centro_x - 40, centro_y + 125, 80, 40, 10, 10)
            
            painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            painter.setPen(QPen(QColor(255, 255, 255)))
            rect_pct = QRect(centro_x - 40, centro_y + 125, 80, 40)
            painter.drawText(rect_pct, Qt.AlignmentFlag.AlignCenter, f"{self.progreso}%")

        # ============================================================
        # PIE DE PÁGINA
        # ============================================================
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QPen(QColor(180, 180, 180, 200)))
        painter.drawText(QRect(centro_x - 300, centro_y + 280, 600, 25),
                        Qt.AlignmentFlag.AlignCenter, "v3.0.0 - Código Crítico - UUID")
        
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor(130, 130, 130, 150)))
        painter.drawText(QRect(centro_x - 300, centro_y + 305, 600, 20),
                        Qt.AlignmentFlag.AlignCenter, "Sincronizando con la nube...")
    
    def closeEvent(self, event):
        if self._sync_thread and self._sync_thread.isRunning():
            self._sync_thread.stop()
            self._sync_thread.wait(2000)
        self.timer_animacion.stop()
        super().closeEvent(event)


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("=" * 60)
    print("   SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA - UUID")
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
    # 2. CREAR APP TEMPORAL PARA EL SELECTOR
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
    
    os.environ["QT_SCALE_FACTOR"] = str(factor_escala)
    os.environ["QT_FONT_DPI"] = str(int(96 * factor_escala))
    print(f"✅ Escala global aplicada: {factor_escala * 100}%")

    # ============================================================
    # 3. CREAR APP PRINCIPAL
    # ============================================================
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Sistema Distribución y Logística")
    app.setOrganizationName("CodigoCritico")
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # ============================================================
    # 4. SPLASH DE SINCRONIZACIÓN
    # ============================================================
    splash_sync = SplashSincronizacion()
    app.processEvents()
    print("✅ Splash de sincronización mostrado (800x800)")

    # ============================================================
    # 5. EJECUTAR SINCRONIZACIÓN EN HILO SEPARADO
    # ============================================================
    db_conn = obtener_conexion()
    
    if verificar_conexion_turso():
        splash_sync.ejecutar_sincronizacion(db_conn)
    else:
        splash_sync.set_estado("⚠️ Sin conexión a Turso", "Datos locales - sincronización pendiente", 50)
        QTimer.singleShot(2000, splash_sync.close)
    
    tiempo_espera = 0
    while splash_sync.isVisible() and tiempo_espera < 300:
        app.processEvents()
        time.sleep(0.5)
        tiempo_espera += 0.5
    
    if splash_sync.isVisible():
        splash_sync.close()
        print("⚠️ Timeout: Forzando cierre del splash")
    
    print("✅ Splash de sincronización cerrado")

    # ============================================================
    # 6. INICIAR SINCRONIZACIÓN AUTOMÁTICA
    # ============================================================
    try:
        iniciar_sincronizacion_auto(db_conn, intervalo=5)
        print("🔄 Sincronización automática iniciada (en segundo plano)")
    except Exception as e:
        print(f"⚠️ Error iniciando sincronización automática: {e}")
    
    db_conn.close()

    # ============================================================
    # 7. LOGIN Y VENTANA PRINCIPAL
    # ============================================================
    db = obtener_conexion()
    login = DialogoLogin(db)

    if login.exec() == QDialog.DialogCode.Accepted:
        iniciar()
        print("🔄 Sincronizador automático iniciado")
        ventana = VentanaPrincipal(usuario=login.usuario_actual)
        iniciar_sincronizacion_auto()
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

    sys.exit(app.exec())


if __name__ == "__main__":
    main()