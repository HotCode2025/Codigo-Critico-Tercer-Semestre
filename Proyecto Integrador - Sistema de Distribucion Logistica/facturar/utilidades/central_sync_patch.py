"""
Parche para el sincronizador central que respeta el bloqueo de sincronización
"""

import time
from utilidades.sync_lock import SyncLock

def patch_sync_loop(original_sync_function):
    """
    Parchea la función de sincronización para que respete el bloqueo
    """
    def patched_sync_function(*args, **kwargs):
        lock = SyncLock()
        
        # Verificar si la sincronización está habilitada
        if not lock.is_sync_enabled():
            print(f"⏸️ [Sync] Sincronización PAUSADA - Esperando desbloqueo...")
            
            # Esperar hasta que se desbloquee (con timeout)
            start_time = time.time()
            while not lock.is_sync_enabled() and time.time() - start_time < 60:
                time.sleep(1)
            
            if not lock.is_sync_enabled():
                print(f"⚠️ [Sync] Timeout esperando desbloqueo - Omitiendo sincronización")
                return None
        
        # Ejecutar la sincronización original
        return original_sync_function(*args, **kwargs)
    
    return patched_sync_function
