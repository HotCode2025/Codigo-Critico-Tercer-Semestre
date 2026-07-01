"""
Utilidades del sistema - Código Crítico 2026
"""

import sqlite3
import time
import threading
from datetime import datetime

# ============================================================
# FUNCIONES DE SINCRONIZACIÓN CON TURSO
# ============================================================

def verificar_conexion_turso():
    """Verifica la conexión con Turso"""
    try:
        from utilidades.turso_client import get_turso_client
        client = get_turso_client()
        if client.is_connected():
            print("✅ Conexión a Turso: OK")
            return True
        else:
            print("❌ Sin conexión a Turso")
            return False
    except Exception as e:
        print(f"❌ Error verificando conexión Turso: {e}")
        return False

def iniciar_sincronizacion_auto(db_conn=None, intervalo=60):
    """Inicia la sincronización automática con Turso usando sync_auto"""
    try:
        from utilidades.sync_auto import iniciar
        iniciar()
        print(f"🔄 Sincronización automática iniciada (intervalo: {intervalo}s)")
        return True
    except ImportError:
        try:
            # Fallback a sync_simple si sync_auto no existe
            from utilidades.sync_simple import iniciar_sincronizador
            iniciar_sincronizador()
            print(f"✅ Sincronización automática iniciada (intervalo: {intervalo}s) [usando sync_simple]")
            return True
        except Exception as e:
            print(f"⚠️ Error al iniciar sincronización: {e}")
            print("   La sincronización automática no está disponible")
            return False
    except Exception as e:
        print(f"⚠️ Error al iniciar sincronización: {e}")
        print("   La sincronización automática no está disponible")
        return False

def detener_sincronizacion_auto():
    """Detiene la sincronización automática con Turso"""
    try:
        from utilidades.sync_auto import detener
        detener()
        print("⏹️ Sincronización automática detenida")
        return True
    except ImportError:
        try:
            from utilidades.sync_simple import detener_sincronizador
            detener_sincronizador()
            print("⏹️ Sincronización automática detenida [usando sync_simple]")
            return True
        except Exception as e:
            print(f"⚠️ Error al detener sincronización: {e}")
            return False
    except Exception as e:
        print(f"⚠️ Error al detener sincronización: {e}")
        return False

def sincronizar_ahora():
    """Ejecuta sincronización manual inmediata"""
    try:
        from utilidades.sync_auto import sincronizar_ahora as sync_ahora
        sync_ahora()
        print("✅ Sincronización manual completada")
        return True
    except ImportError:
        try:
            from utilidades.sync_simple import sincronizar_ahora as sync_ahora
            sync_ahora()
            print("✅ Sincronización manual completada [usando sync_simple]")
            return True
        except Exception as e:
            print(f"⚠️ Error en sincronización manual: {e}")
            return False
    except Exception as e:
        print(f"⚠️ Error en sincronización manual: {e}")
        return False

# ============================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    from db.db_manager import obtener_conexion
    return obtener_conexion()

def ejecutar_consulta(consulta, parametros=None):
    """Ejecuta una consulta en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if parametros:
            cursor.execute(consulta, parametros)
        else:
            cursor.execute(consulta)
        return cursor.fetchall()
    finally:
        conn.close()

# ============================================================
# EXPORTAR FUNCIONES PRINCIPALES
# ============================================================

__all__ = [
    'verificar_conexion_turso',
    'iniciar_sincronizacion_auto',
    'detener_sincronizacion_auto',
    'sincronizar_ahora',
    'get_db_connection',
    'ejecutar_consulta'
]
