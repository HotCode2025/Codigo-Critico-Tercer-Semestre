"""
Módulo para controlar el bloqueo de sincronización durante operaciones críticas
"""

import threading
import time
from datetime import datetime

class SyncLock:
    """Controla el bloqueo de la sincronización automática"""
    
    _instance = None
    _lock = threading.Lock()
    _sync_enabled = True
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SyncLock, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._sync_enabled = True
        print(f"🔓 [SyncLock] Sincronización habilitada inicialmente")
    
    def lock_sync(self, motivo="Operación crítica"):
        with self._lock:
            if self._sync_enabled:
                self._sync_enabled = False
                print(f"🔒 [SyncLock] Sincronización BLOQUEADA - Motivo: {motivo} - {datetime.now().strftime('%H:%M:%S')}")
                return True
            return False
    
    def unlock_sync(self):
        with self._lock:
            if not self._sync_enabled:
                self._sync_enabled = True
                print(f"🔓 [SyncLock] Sincronización REACTIVADA - {datetime.now().strftime('%H:%M:%S')}")
                return True
            return False
    
    def is_sync_enabled(self):
        with self._lock:
            return self._sync_enabled
    
    def is_sync_locked(self):
        with self._lock:
            return not self._sync_enabled

def with_sync_lock(func):
    """Decorador que bloquea la sincronización durante la ejecución"""
    def wrapper(*args, **kwargs):
        lock = SyncLock()
        try:
            lock.lock_sync(f"Ejecutando {func.__name__}")
            result = func(*args, **kwargs)
            return result
        finally:
            lock.unlock_sync()
    return wrapper

class SyncLockContext:
    """Context manager para bloquear sincronización"""
    def __init__(self, motivo="Operación crítica"):
        self.motivo = motivo
        self.lock = SyncLock()
        self.bloqueado = False
    
    def __enter__(self):
        self.bloqueado = self.lock.lock_sync(self.motivo)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.bloqueado:
            self.lock.unlock_sync()
        return False

# Instancia global
sync_lock = SyncLock()
