"""
Prueba del sistema de bloqueo de sincronización
"""

import time
import threading
from utilidades.sync_lock import SyncLock, with_sync_lock, SyncLockContext

def operacion_larga():
    """Simula una operación larga que bloquea la sincronización"""
    lock = SyncLock()
    
    print("🔄 Iniciando operación larga...")
    lock.lock_sync("Operación larga")
    
    # Simular trabajo
    for i in range(5):
        print(f"   Trabajando... {i+1}/5")
        time.sleep(1)
    
    lock.unlock_sync()
    print("✅ Operación completada")

@with_sync_lock
def operacion_con_decorador():
    """Operación que usa el decorador"""
    print("🔄 Ejecutando operación con decorador...")
    time.sleep(3)
    print("✅ Operación completada")

def sincronizacion_simulada():
    """Simula la sincronización automática"""
    lock = SyncLock()
    
    while True:
        if lock.is_sync_enabled():
            print("🔄 Sincronizando...")
            time.sleep(2)
        else:
            print("⏸️ Sincronización PAUSADA")
            time.sleep(1)

def test_sync_lock():
    """Prueba el sistema de bloqueo"""
    print("=" * 60)
    print("🧪 TEST DEL SISTEMA DE BLOQUEO DE SINCRONIZACIÓN")
    print("=" * 60)
    
    # Iniciar sincronización simulada en segundo plano
    sync_thread = threading.Thread(target=sincronizacion_simulada, daemon=True)
    sync_thread.start()
    
    print("\n✅ Sincronización automática iniciada")
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("🔒 Probando bloqueo manual...")
    print("=" * 60)
    operacion_larga()
    
    print("\n" + "=" * 60)
    print("🔒 Probando bloqueo con decorador...")
    print("=" * 60)
    operacion_con_decorador()
    
    print("\n" + "=" * 60)
    print("🔒 Probando bloqueo con context manager...")
    print("=" * 60)
    with SyncLockContext("Operación con context manager"):
        for i in range(3):
            print(f"   Trabajando... {i+1}/3")
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    
    # Mostrar estado final
    lock = SyncLock()
    print(f"\n📊 Estado final: {lock.get_status()}")

if __name__ == '__main__':
    test_sync_lock()
