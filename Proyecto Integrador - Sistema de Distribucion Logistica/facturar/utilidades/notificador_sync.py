"""
Notificador de cambios en sincronización
"""

from PyQt6.QtWidgets import QApplication
import threading

class NotificadorSync:
    """Notifica a la interfaz cuando hay cambios en la sincronización"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(NotificadorSync, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._callbacks = []
        print("📢 NotificadorSync inicializado")
    
    def registrar_callback(self, callback):
        """Registra una función para ser llamada cuando haya cambios"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            print(f"📢 Callback registrado: {callback.__name__}")
    
    def notificar_cambio(self, tabla="notas_venta"):
        """Notifica que hubo un cambio en la sincronización"""
        print(f"📢 Notificando cambio en {tabla}")
        
        # Ejecutar callbacks en el hilo principal de Qt
        def ejecutar_callback(callback):
            try:
                callback()
            except Exception as e:
                print(f"⚠️ Error en callback: {e}")
        
        for callback in self._callbacks:
            try:
                # Si estamos en Qt, ejecutar en el hilo principal
                app = QApplication.instance()
                if app and threading.current_thread() is not threading.main_thread():
                    app.invokeLater(lambda: ejecutar_callback(callback))
                else:
                    ejecutar_callback(callback)
            except Exception as e:
                print(f"⚠️ Error notificando: {e}")

# Instancia global
notificador = NotificadorSync()

def registrar_actualizador(actualizador):
    """Registra un actualizador de vista"""
    notificador.registrar_callback(actualizador)
