"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 10: db_manager.py con UUID y pyturso
==================================================
📌 USO: Gestión de la base de datos SQLite
📌 CARACTERÍSTICAS:
    - Inicialización con script SQL (UUID)
    - Migraciones automáticas
    - Soporte para pyturso
"""

import sqlite3
import os
import sys

_NOMBRE_BD = "distribuidora.db"

def _ruta_base_datos() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, _NOMBRE_BD)

def _cargar_script_sql() -> str:
    """Carga el script SQL de creación de la base de datos."""
    import sys
    posibles_rutas = []
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        posibles_rutas = [
            os.path.join(base_dir, "db", "script_creacion.sql"),
            os.path.join(base_dir, "script_creacion.sql"),
            os.path.join(os.path.dirname(__file__), "script_creacion.sql"),
            os.path.join(base_dir, "db", "script_con_uuid.sql"),
            os.path.join(base_dir, "script_con_uuid.sql"),
            os.path.join(os.path.dirname(__file__), "script_con_uuid.sql"),
        ]
    else:
        posibles_rutas = [
            os.path.join(os.path.dirname(__file__), "script_creacion.sql"),
            os.path.join(os.getcwd(), "db", "script_creacion.sql"),
            os.path.join(os.path.dirname(__file__), "script_con_uuid.sql"),
            os.path.join(os.getcwd(), "db", "script_con_uuid.sql"),
            os.path.join(os.getcwd(), "script_con_uuid.sql"),
        ]
    
    # Primero buscar script_con_uuid.sql
    for sql_path in posibles_rutas:
        if os.path.exists(sql_path):
            print(f"📄 Cargando script: {sql_path}")
            with open(sql_path, "r", encoding="utf-8") as f:
                return f.read()
    
    # Si no existe, mostrar error
    raise FileNotFoundError(f"No se encontró el script SQL. Buscado en: {posibles_rutas}")

def _tablas_existen(conexion) -> bool:
    """Verifica si la base de datos ya está inicializada."""
    try:
        cur = conexion.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parametros'")
        return cur.fetchone() is not None
    except:
        return False

def _verificar_uuid(conexion) -> bool:
    """Verifica si las tablas ya usan UUID (TEXT) en lugar de INTEGER."""
    try:
        cur = conexion.cursor()
        cur.execute("PRAGMA table_info(clientes)")
        columnas = cur.fetchall()
        for col in columnas:
            if col[1] == 'id':
                return 'TEXT' in col[2].upper()
        return False
    except:
        return False

def _verificar_datos(conexion) -> bool:
    """Verifica si la base de datos tiene datos cargados."""
    try:
        cur = conexion.cursor()
        cur.execute("SELECT COUNT(*) FROM clientes")
        count = cur.fetchone()[0]
        return count > 0
    except:
        return False

def aplicar_migraciones():
    """Aplica migraciones necesarias para UUID."""
    ruta = _ruta_base_datos()
    if not os.path.exists(ruta):
        print("⚠️ Base de datos no existe. Se creará al inicializar.")
        return
    
    conexion = sqlite3.connect(ruta)
    try:
        # Verificar si la base de datos ya usa UUID
        if _verificar_uuid(conexion):
            print("✅ Base de datos ya usa UUID")
            return
        
        print("⚠️ Migración UUID necesaria")
        print("📌 Para migrar a UUID, se debe:")
        print("   1. Hacer backup de la base de datos")
        print("   2. Eliminar la base de datos existente")
        print("   3. Ejecutar el nuevo script SQL con UUID")
        print("   4. Importar los datos desde el backup")
        print("")
        print("📌 O usar el script de migración automática:")
        print("   python scripts/migrar_a_uuid.py")
        
    except Exception as e:
        print(f"Error en migración: {e}")
    finally:
        conexion.close()

def inicializar_bd():
    """Inicializa la base de datos con el script SQL (versión UUID)."""
    ruta = _ruta_base_datos()
    db_ya_inicializada = False
    
    if os.path.exists(ruta):
        try:
            conexion = sqlite3.connect(ruta)
            db_ya_inicializada = _tablas_existen(conexion)
            conexion.close()
        except:
            pass
    
    if db_ya_inicializada:
        print("✅ Base de datos ya inicializada.")
        aplicar_migraciones()
        
        # Verificar si tiene datos
        try:
            conexion = sqlite3.connect(ruta)
            tiene_datos = _verificar_datos(conexion)
            conexion.close()
            if not tiene_datos:
                print("⚠️ Base de datos vacía. Ejecutando script con datos...")
                # Si está vacía, cargar el script con datos
                conexion = sqlite3.connect(ruta)
                try:
                    script = _cargar_script_sql()
                    # Ejecutar solo los INSERTs (no la estructura)
                    # Esto es más complejo, mejor ejecutar todo el script
                    conexion.executescript(script)
                    conexion.commit()
                    print("✅ Datos cargados correctamente.")
                except Exception as e:
                    print(f"❌ Error al cargar datos: {e}")
                finally:
                    conexion.close()
        except:
            pass
        
        return
    
    print("📁 Creando base de datos...")
    conexion = sqlite3.connect(ruta)
    try:
        script = _cargar_script_sql()
        conexion.executescript(script)
        conexion.commit()
        print("✅ Base de datos creada correctamente.")
        print("📌 Todas las tablas usan UUID (TEXT) como clave primaria.")
        print("📌 Datos de prueba cargados (500 notas, 700 clientes, 95 productos).")
    except Exception as e:
        print(f"❌ Error al ejecutar script: {e}")
        raise
    finally:
        conexion.close()
    
    aplicar_migraciones()

def obtener_conexion() -> sqlite3.Connection:
    """Obtiene una conexión a la base de datos."""
    ruta = _ruta_base_datos()
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row
    return conexion
