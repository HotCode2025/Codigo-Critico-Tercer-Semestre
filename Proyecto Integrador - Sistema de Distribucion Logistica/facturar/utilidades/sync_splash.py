"""
Código Crítico - Tercer Semestre Año 2026
==================================================
SPLASH DE SINCRONIZACIÓN REAL - CON ESPERA REAL
==================================================
📌 El splash permanece abierto HASTA QUE TERMINE la sincronización
📌 Muestra el progreso REAL en tiempo real
"""

import os
import threading
import time
from PyQt6.QtWidgets import (QSplashScreen, QProgressBar, QLabel, 
                               QVBoxLayout, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPixmap

from utilidades.sync_monitor import get_sync_monitor


class SyncSplashReal(QSplashScreen):
    """
    Splash de sincronización REAL que espera a que termine.
    """
    
    def __init__(self, db_connection, parent=None):
        super().__init__()
        self.db = db_connection
        self.monitor = get_sync_monitor()
        self._is_finished = False
        self._sync_completed = False
        self._sync_error = None
        self._registros_enviados = 0
        self._registros_recibidos = 0
        self._tabla_actual = ""
        self._total_tablas = 0
        self._tablas_procesadas = 0
        
        # Configurar splash - MISMO ESTILO ORIGINAL
        self.setWindowTitle("Sincronizando...")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(500, 380)
        
        # ESTILO ORIGINAL
        self.setStyleSheet("""
            QSplashScreen {
                background-color: #1A237E;
                border-radius: 15px;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QProgressBar {
                border: none;
                border-radius: 5px;
                height: 20px;
                background-color: rgba(255,255,255,0.2);
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)
        
        # LOGO
        lbl_logo = QLabel("🏢")
        lbl_logo.setStyleSheet("font-size: 48px; background-color: transparent;")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_logo)
        
        # TÍTULO
        lbl_titulo = QLabel("SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA")
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFC107; background-color: transparent;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        # ESTADO
        self.lbl_estado = QLabel("🔄 Conectando a Turso...")
        self.lbl_estado.setStyleSheet("font-size: 12px; color: #B0BEC5; background-color: transparent;")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_estado)
        
        # BARRA DE PROGRESO
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # CONTADOR
        self.lbl_contador = QLabel("📤 0 registros enviados")
        self.lbl_contador.setStyleSheet("font-size: 10px; color: #78909C; background-color: transparent;")
        self.lbl_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_contador)
        
        # TABLA ACTUAL
        self.lbl_tabla = QLabel("⏳ Iniciando...")
        self.lbl_tabla.setStyleSheet("font-size: 10px; color: #546E7A; background-color: transparent;")
        self.lbl_tabla.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_tabla)
        
        # Conectar monitor
        self.monitor.agregar_listener(self._on_sync_event)
        
        # Timer para actualizar UI
        self.timer = QTimer()
        self.timer.timeout.connect(self._actualizar_ui)
        self.timer.start(100)
    
    def _on_sync_event(self, evento, datos):
        """Recibe eventos del monitor de sincronización"""
        if evento == 'inicio':
            self._actualizar_estado("🔄 Iniciando sincronización...", 5)
            self._tablas_procesadas = 0
            self._total_tablas = 0
        
        elif evento == 'inicio_tabla':
            self._tabla_actual = datos.get('tabla', '')
            self._tablas_procesadas += 1
            self._actualizar_estado(f"📋 Procesando: {self._tabla_actual}", 10)
            self.lbl_tabla.setText(f"📋 Tabla: {self._tabla_actual}")
        
        elif evento == 'envio':
            tabla = datos.get('tabla', '')
            cantidad = datos.get('cantidad', 0)
            total = datos.get('total', 0)
            self._registros_enviados = total
            self._tabla_actual = tabla
            self._actualizar_estado(f"📤 Enviando {tabla}: {cantidad} registros", 30)
            self.lbl_tabla.setText(f"📤 Enviando: {tabla}")
            self._actualizar_contador()
        
        elif evento == 'recibido':
            tabla = datos.get('tabla', '')
            cantidad = datos.get('cantidad', 0)
            total = datos.get('total', 0)
            self._registros_recibidos = total
            self._tabla_actual = tabla
            self._actualizar_estado(f"📥 Recibiendo {tabla}: {cantidad} registros", 40)
            self.lbl_tabla.setText(f"📥 Recibiendo: {tabla}")
            self._actualizar_contador()
        
        elif evento == 'error':
            error = datos.get('error', 'Error desconocido')
            self._sync_error = error
            self._actualizar_estado(f"❌ Error: {error[:50]}...", 0)
            self.lbl_tabla.setText(f"❌ Error en: {self._tabla_actual}")
            # No marcar como finished, dejar que el timeout maneje
        
        elif evento == 'fin':
            enviados = datos.get('enviados', 0)
            recibidos = datos.get('recibidos', 0)
            self._registros_enviados = enviados
            self._registros_recibidos = recibidos
            self._sync_completed = True
            self._is_finished = True
            self._actualizar_estado("✅ Sincronización completada", 100)
            self.lbl_tabla.setText("✅ Todos los datos sincronizados")
            self._actualizar_contador()
            # ✅ Esperar 1.5 segundos y cerrar
            QTimer.singleShot(1500, self.close)
    
    def _actualizar_estado(self, mensaje, progreso):
        """Actualiza el estado"""
        if not self._is_finished:
            self.lbl_estado.setText(mensaje)
            self.progress.setValue(progreso)
            QApplication.processEvents()
    
    def _actualizar_contador(self):
        """Actualiza el contador"""
        if self._registros_enviados > 0 or self._registros_recibidos > 0:
            self.lbl_contador.setText(
                f"📤 {self._registros_enviados} enviados | 📥 {self._registros_recibidos} recibidos"
            )
        else:
            self.lbl_contador.setText(f"📤 {self._registros_enviados} registros enviados")
    
    def _actualizar_ui(self):
        """Actualiza la UI desde el timer"""
        if self._is_finished:
            return
        
        # Obtener estado del monitor
        estado = self.monitor.obtener_estado()
        
        # Actualizar contador
        enviados = estado.get('registros_enviados', 0)
        recibidos = estado.get('registros_recibidos', 0)
        if enviados > 0 or recibidos > 0:
            self._registros_enviados = enviados
            self._registros_recibidos = recibidos
            self._actualizar_contador()
        
        # Si está en proceso, actualizar barra
        if estado.get('en_proceso', False):
            progreso = min(90, 10 + (enviados + recibidos) // 10)
            self.progress.setValue(progreso)
            self.lbl_tabla.setText(f"📤 Procesando... ({enviados + recibidos} registros)")
    
    def ejecutar_y_esperar(self, timeout=180):
        """
        ✅ EJECUTA LA SINCRONIZACIÓN Y ESPERA A QUE TERMINE
        Retorna True si fue exitosa, False si hubo error o timeout
        """
        from utilidades.central_sync import sincronizar_ahora
        
        self.show()
        QApplication.processEvents()
        
        # Variable para controlar el hilo
        sync_done = False
        sync_result = None
        
        def sync_task():
            nonlocal sync_done, sync_result
            try:
                self.lbl_estado.setText("📤 Enviando datos a Turso...")
                resultado = sincronizar_ahora(self.db)
                sync_result = resultado
                sync_done = True
                
                # Notificar fin manualmente
                enviados = 0
                recibidos = 0
                central_a_turso = resultado.get('central_a_turso', {})
                for tabla, res in central_a_turso.items():
                    enviados += res.get('sent', 0)
                turso_a_central = resultado.get('turso_a_central', {})
                for tabla, res in turso_a_central.items():
                    recibidos += res.get('received', 0)
                
                self._sync_completed = True
                self._is_finished = True
                self._registros_enviados = enviados
                self._registros_recibidos = recibidos
                self._actualizar_estado("✅ Sincronización completada", 100)
                self.lbl_tabla.setText("✅ Todos los datos sincronizados")
                self._actualizar_contador()
                QTimer.singleShot(1500, self.close)
                
            except Exception as e:
                sync_done = True
                sync_result = {'error': str(e)}
                self._sync_error = str(e)
                self._actualizar_estado(f"❌ Error: {str(e)[:50]}...", 0)
                QTimer.singleShot(2000, self.close)
        
        # Ejecutar en hilo
        thread = threading.Thread(target=sync_task, daemon=True)
        thread.start()
        
        # ✅ ESPERAR ACTIVAMENTE a que termine
        tiempo_espera = 0
        while not sync_done and tiempo_espera < timeout:
            time.sleep(0.1)
            tiempo_espera += 0.1
            # Procesar eventos Qt para mantener la UI viva
            QApplication.processEvents()
            
            # Actualizar barra si está en proceso
            if not self._is_finished:
                estado = self.monitor.obtener_estado()
                enviados = estado.get('registros_enviados', 0)
                recibidos = estado.get('registros_recibidos', 0)
                if estado.get('en_proceso', False):
                    progreso = min(90, 10 + (enviados + recibidos) // 10)
                    self.progress.setValue(progreso)
                    self.lbl_tabla.setText(f"📤 Procesando... ({enviados + recibidos} registros)")
        
        # Si pasó el timeout y no terminó
        if not sync_done:
            self._is_finished = True
            self._actualizar_estado("⏰ Timeout - Sincronización incompleta", 100)
            QTimer.singleShot(1000, self.close)
            return False
        
        # Si hubo error
        if sync_result and 'error' in sync_result:
            return False
        
        return self._sync_completed
    
    def closeEvent(self, event):
        """Cierra el splash y limpia recursos"""
        self._is_finished = True
        self.timer.stop()
        try:
            self.monitor.remover_listener(self._on_sync_event)
        except:
            pass
        super().closeEvent(event)


def mostrar_splash_sincronizacion(db, parent=None, timeout=180):
    """
    ✅ MUESTRA EL SPLASH Y ESPERA A QUE TERMINE LA SINCRONIZACIÓN
    Retorna True si fue exitosa, False si hubo error o timeout
    """
    splash = SyncSplashReal(db, parent)
    
    # ✅ Ejecuta y espera (esto bloquea hasta que termine)
    exito = splash.ejecutar_y_esperar(timeout=timeout)
    
    # Asegurar que se cierre
    try:
        splash.close()
    except:
        pass
    
    return exito