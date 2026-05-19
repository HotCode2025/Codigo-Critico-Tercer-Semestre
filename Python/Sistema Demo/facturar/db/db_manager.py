"""
Código Crítico - Tercer Semestre Año 2026
Gestor de la base de datos SQLite.
Proporciona funciones para inicializar la base de datos (crear tablas)
y obtener conexiones listas para usar.
"""

import sqlite3
import os

# Ruta donde se almacenará la base de datos
_NOMBRE_BD = "distribuidora.db"

def _ruta_base_datos() -> str:
    """Devuelve la ruta absoluta al archivo de base de datos, situado en la raíz del proyecto."""
    # Se asume que db/ está dentro de la raíz del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, _NOMBRE_BD)

def _cargar_script_sql() -> str:
    """Lee el contenido del archivo script_creacion.sql y lo retorna como cadena."""
    sql_path = os.path.join(os.path.dirname(__file__), "script_creacion.sql")
    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"No se encontró el script SQL en {sql_path}")
    with open(sql_path, "r", encoding="utf-8") as f:
        return f.read()

def inicializar_bd():
    """
    Crea el archivo de base de datos y todas las tablas si no existen.
    Se puede llamar al inicio de la aplicación.
    """
    ruta = _ruta_base_datos()
    conexion = sqlite3.connect(ruta)
    try:
        script = _cargar_script_sql()
        conexion.executescript(script)
        conexion.commit()
    finally:
        conexion.close()

def obtener_conexion() -> sqlite3.Connection:
    """
    Devuelve una conexión a la base de datos SQLite.
    Habilita las claves foráneas y configura row_factory para acceso por nombre.
    """
    ruta = _ruta_base_datos()
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row
    return conexion

def aplicar_migraciones():
    """
    Permite modificar la estructura de la base de datos en versiones futuras.
    Por ahora no realiza cambios adicionales, pero está preparada para ejecutar SQL adicional.
    """
    # Ejemplo:
    # conexion = obtener_conexion()
    # conexion.execute("ALTER TABLE clientes ADD COLUMN nuevo_campo TEXT;")
    # conexion.close()
    pass