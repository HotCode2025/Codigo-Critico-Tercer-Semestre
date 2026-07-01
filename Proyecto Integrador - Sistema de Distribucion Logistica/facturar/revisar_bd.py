#!/usr/bin/env python3
"""
Código Crítico - Tercer Semestre Año 2026
==================================================
REVISAR BASE DE DATOS LOCAL COMPLETA
==================================================
📌 Muestra:
    - Todas las tablas
    - Estructura de cada tabla
    - Todos los datos de cada tabla
    - Resumen estadístico
"""

import sqlite3
import os
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

DB_PATH = "distribuidora.db"

# Tablas que NO mostrar (internas de SQLite)
TABLAS_IGNORAR = [
    'sqlite_sequence',
    'sqlite_stat1',
    'sqlite_stat4'
]

# ============================================================
# FUNCIONES
# ============================================================

def conectar_bd():
    """Conecta a la base de datos"""
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: No se encontró la base de datos '{DB_PATH}'")
        print(f"📁 Directorio actual: {os.getcwd()}")
        return None
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_tablas(conn):
    """Obtiene todas las tablas de la base de datos"""
    cur = conn.cursor()
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    tablas = [row['name'] for row in cur.fetchall()]
    return [t for t in tablas if t not in TABLAS_IGNORAR]

def obtener_estructura(conn, tabla):
    """Obtiene la estructura de una tabla"""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({tabla})")
    return cur.fetchall()

def obtener_datos(conn, tabla, limite=50):
    """Obtiene los datos de una tabla"""
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM {tabla} LIMIT {limite}")
        return cur.fetchall()
    except Exception as e:
        print(f"   ⚠️ Error al leer datos: {e}")
        return []

def contar_registros(conn, tabla):
    """Cuenta los registros de una tabla"""
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) as total FROM {tabla}")
        return cur.fetchone()['total']
    except:
        return 0

def mostrar_tabla(conn, tabla):
    """Muestra la información completa de una tabla"""
    print("\n" + "=" * 80)
    print(f"📋 TABLA: {tabla.upper()}")
    print("=" * 80)
    
    # Contar registros
    total = contar_registros(conn, tabla)
    print(f"📊 Registros totales: {total}")
    
    # Estructura
    print(f"\n📐 ESTRUCTURA:")
    print("-" * 60)
    columnas = obtener_estructura(conn, tabla)
    for col in columnas:
        pk = "🔑 PK" if col['pk'] else ""
        nullable = "NOT NULL" if col['notnull'] else "NULL"
        print(f"   {col['name']:<25} {col['type']:<15} {nullable:<10} {pk}")
    
    # Datos
    if total > 0:
        print(f"\n📊 DATOS (mostrando hasta 10 registros):")
        print("-" * 60)
        datos = obtener_datos(conn, tabla, limite=10)
        
        if datos:
            # Obtener nombres de columnas
            nombres_cols = [col['name'] for col in columnas]
            
            # Mostrar encabezados
            headers = " | ".join([f"{col[:18]:<18}" for col in nombres_cols])
            print(headers)
            print("-" * 60)
            
            # Mostrar datos
            for row in datos:
                valores = []
                for i, col in enumerate(nombres_cols):
                    val = row[i]
                    if val is None:
                        valores.append("NULL".ljust(18))
                    elif isinstance(val, (int, float)):
                        valores.append(f"{str(val)[:18]:<18}")
                    elif isinstance(val, bytes):
                        valores.append(f"[BLOB {len(val)} bytes]".ljust(18))
                    else:
                        texto = str(val)[:18]
                        if len(str(val)) > 18:
                            texto += "..."
                        valores.append(f"{texto:<18}")
                print(" | ".join(valores))
            
            if total > 10:
                print(f"\n   ... y {total - 10} registros más")
    else:
        print("\n   ℹ️ Tabla vacía")

def mostrar_resumen(conn):
    """Muestra un resumen estadístico de todas las tablas"""
    print("\n" + "=" * 80)
    print("📊 RESUMEN GENERAL")
    print("=" * 80)
    
    tablas = obtener_tablas(conn)
    total_registros = 0
    
    print(f"\n📋 Tablas encontradas: {len(tablas)}")
    print("-" * 60)
    
    for tabla in tablas:
        count = contar_registros(conn, tabla)
        total_registros += count
        print(f"   {tabla:<35} {count:>8} registros")
    
    print("-" * 60)
    print(f"   {'TOTAL':<35} {total_registros:>8} registros")

def buscar_texto(conn, texto):
    """Busca un texto en todas las tablas y columnas"""
    print("\n" + "=" * 80)
    print(f"🔍 BUSCANDO: '{texto}'")
    print("=" * 80)
    
    tablas = obtener_tablas(conn)
    encontrados = 0
    
    for tabla in tablas:
        columnas = obtener_estructura(conn, tabla)
        
        for col in columnas:
            # Solo buscar en columnas de texto
            tipo = col['type'].upper()
            if 'TEXT' not in tipo and 'CHAR' not in tipo and 'VARCHAR' not in tipo:
                continue
            
            try:
                cur = conn.cursor()
                query = f"SELECT * FROM {tabla} WHERE {col['name']} LIKE ? LIMIT 10"
                cur.execute(query, (f"%{texto}%",))
                resultados = cur.fetchall()
                
                if resultados:
                    print(f"\n📌 En {tabla}.{col['name']}: {len(resultados)} coincidencias")
                    for row in resultados:
                        # Mostrar el ID y el texto encontrado
                        try:
                            id_val = row['id'] if 'id' in row.keys() else 'N/A'
                            print(f"   ID: {id_val} - {row[col['name']][:80]}")
                        except:
                            print(f"   {row[col['name']][:80]}")
                    encontrados += len(resultados)
            except:
                pass
    
    if encontrados == 0:
        print("\n   ℹ️ No se encontraron coincidencias")

# ============================================================
# MENÚ INTERACTIVO
# ============================================================

def menu():
    """Menú interactivo"""
    print("\n" + "=" * 80)
    print("🔍 REVISOR DE BASE DE DATOS")
    print("=" * 80)
    print()
    print("   1. Ver todas las tablas")
    print("   2. Ver estructura y datos de una tabla específica")
    print("   3. Ver todas las tablas (completo)")
    print("   4. Ver resumen general")
    print("   5. Buscar texto en toda la base de datos")
    print("   6. Ver tablas de sincronización")
    print("   7. Salir")
    print()
    
    return input("👉 Seleccione una opción: ").strip()

# ============================================================
# MAIN
# ============================================================

def main():
    """Función principal"""
    print("=" * 80)
    print(f"🔍 REVISANDO BASE DE DATOS: {DB_PATH}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    conn = conectar_bd()
    if not conn:
        return
    
    tablas = obtener_tablas(conn)
    print(f"\n✅ Base de datos conectada correctamente")
    print(f"📋 Tablas encontradas: {len(tablas)}")
    
    while True:
        opcion = menu()
        
        if opcion == '1':
            print("\n📋 TABLAS EN LA BASE DE DATOS:")
            print("-" * 40)
            for i, tabla in enumerate(tablas, 1):
                count = contar_registros(conn, tabla)
                print(f"   {i:>2}. {tabla:<35} ({count} registros)")
        
        elif opcion == '2':
            print("\n📋 TABLAS DISPONIBLES:")
            for i, tabla in enumerate(tablas, 1):
                print(f"   {i:>2}. {tabla}")
            
            try:
                idx = int(input("\n👉 Número de tabla: ")) - 1
                if 0 <= idx < len(tablas):
                    mostrar_tabla(conn, tablas[idx])
                else:
                    print("❌ Tabla no válida")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        elif opcion == '3':
            for tabla in tablas:
                mostrar_tabla(conn, tabla)
        
        elif opcion == '4':
            mostrar_resumen(conn)
        
        elif opcion == '5':
            texto = input("🔍 Texto a buscar: ").strip()
            if texto:
                buscar_texto(conn, texto)
            else:
                print("❌ Ingrese un texto válido")
        
        elif opcion == '6':
            print("\n📋 TABLAS DE SINCRONIZACIÓN:")
            print("-" * 60)
            
            sync_tables = ['sync_log', 'sync_log_reverse', 'sync_queue', 'sync_log_history', 'sync_conflictos']
            
            for tabla in sync_tables:
                if tabla in tablas:
                    mostrar_tabla(conn, tabla)
                else:
                    print(f"\n⚠️ Tabla '{tabla}' no existe")
        
        elif opcion == '7':
            print("\n👋 Saliendo...")
            break
        
        else:
            print("❌ Opción no válida")
        
        input("\n📌 Presione Enter para continuar...")

# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    main()