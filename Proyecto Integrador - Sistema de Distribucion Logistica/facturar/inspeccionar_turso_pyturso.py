"""
INSPECCIÓN DE TURSO CON PYTURSO
===============================
📌 Usa pyturso para conectar a Turso
📌 USO: python inspeccionar_turso_pyturso.py
📌 REQUIERE: pip install pyturso
"""

import sys
import os
from datetime import datetime

# ============================================================
# CONFIGURACIÓN - DEL ARCHIVO turso-facturar.txt
# ============================================================

TURSO_URL = "libsql://nube-clarionda.aws-us-east-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODI1MTQyMTEsImlkIjoiMDE5ZjA2MjAtM2YwMS03NzgwLWI0ZDgtNDU3YWY3OWYyNzY1IiwicmlkIjoiOWU1YzkyZDktMmI3MC00MTJjLThkNmYtZjgzMzY5NjM4ODViIn0.H_PKJrBCAvNH5WPaCYUJOgHDVDPQHw7Y4qir1zFlx6MSih-vjUZnojZdp5AmMwAz9151gNCjX-rC3oGuj_ETAw"

def conectar_turso():
    """Conecta a Turso usando pyturso"""
    try:
        from pyturso import Client
        
        print("🔗 Conectando a Turso...")
        print(f"   URL: {TURSO_URL}")
        
        # Crear cliente
        client = Client(TURSO_URL, auth_token=TURSO_TOKEN)
        
        # Probar conexión
        result = client.execute("SELECT 1")
        if result:
            print("✅ Conexión exitosa")
            return client
        else:
            print("❌ No se pudo verificar la conexión")
            return None
            
    except ImportError:
        print("❌ pyturso no está instalado")
        print("   Instala con: pip install pyturso")
        return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def mostrar_resumen(client):
    """Muestra resumen de todas las tablas"""
    print("\n" + "=" * 80)
    print("   📊 RESUMEN GENERAL - TURSO")
    print("=" * 80)
    
    try:
        # Obtener todas las tablas
        result = client.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = result.fetchall()
        
        if not tablas:
            print("   ⚠️ No se encontraron tablas")
            return
        
        print(f"\n   {'TABLA':<30} {'REGISTROS':>12}")
        print("   " + "-" * 80)
        
        total = 0
        for row in tablas:
            tabla = row[0]
            if tabla.startswith('sqlite_'):
                continue
            
            try:
                count_result = client.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = count_result.fetchone()[0]
                total += count
                print(f"   {tabla:<30} {count:>12,}")
            except Exception as e:
                print(f"   {tabla:<30} {'ERROR':>12}")
                print(f"      ⚠️ {e}")
        
        print("   " + "-" * 80)
        print(f"   {'TOTAL':<30} {total:>12,}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_tabla(client, tabla, limite=10):
    """Muestra contenido de una tabla específica"""
    print("\n" + "=" * 80)
    print(f"   📊 TABLA: {tabla.upper()}")
    print("=" * 80)
    
    try:
        # Obtener estructura
        result = client.execute(f"PRAGMA table_info({tabla})")
        columnas = result.fetchall()
        
        if not columnas:
            print("   ⚠️ Tabla no existe o está vacía")
            return
        
        nombres = [col[1] for col in columnas]
        
        # Contar registros
        result = client.execute(f"SELECT COUNT(*) FROM {tabla}")
        total = result.fetchone()[0]
        print(f"\n   📈 Total registros: {total}")
        
        if total == 0:
            print("   ⚠️ Tabla vacía")
            return
        
        # Mostrar estructura
        print("\n   📋 Estructura:")
        for col in columnas:
            print(f"      • {col[1]}: {col[2]} {'PK' if col[5] else ''}")
        
        # Mostrar datos
        print(f"\n   📝 Datos (mostrando hasta {limite} registros):")
        
        columnas_str = ", ".join(nombres)
        result = client.execute(f"SELECT {columnas_str} FROM {tabla} LIMIT {limite}")
        rows = result.fetchall()
        
        if not rows:
            print("      (sin datos)")
            return
        
        # Mostrar encabezados
        print("   " + "-" * 78)
        header = "   "
        for nombre in nombres[:8]:
            header += f"{nombre[:12]:<14}"
        print(header)
        print("   " + "-" * 78)
        
        # Mostrar filas
        for row in rows:
            linea = "   "
            for i, valor in enumerate(row[:8]):
                if valor is None:
                    texto = "NULL"
                elif isinstance(valor, float):
                    texto = f"{valor:,.2f}"
                elif isinstance(valor, int):
                    texto = f"{valor:,}"
                elif isinstance(valor, bytes):
                    texto = f"<BLOB {len(valor)} bytes>"
                else:
                    texto = str(valor)[:12]
                linea += f"{texto:<14}"
            print(linea)
        
        if total > limite:
            print(f"\n   ... y {total - limite} registros más")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def verificar_datos_importantes(client):
    """Verifica datos críticos en Turso"""
    print("\n" + "=" * 80)
    print("   🔍 VERIFICACIÓN DE DATOS IMPORTANTES")
    print("=" * 80)
    
    # 1. Parámetros
    print("\n📌 PARÁMETROS DE LA EMPRESA")
    print("-" * 40)
    try:
        result = client.execute("SELECT * FROM parametros WHERE id = 1")
        row = result.fetchone()
        if row:
            result = client.execute("PRAGMA table_info(parametros)")
            cols = result.fetchall()
            print("   Configuración:")
            for i, col in enumerate(cols):
                print(f"   • {col[1]}: {row[i]}")
        else:
            print("   ⚠️ No se encontraron parámetros")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # 2. Notas de venta (datos que vienen de la App)
    print("\n📋 NOTAS DE VENTA (Datos de App)")
    print("-" * 40)
    try:
        result = client.execute("SELECT COUNT(*) FROM notas_venta")
        total = result.fetchone()[0]
        print(f"   Total: {total}")
        
        if total > 0:
            result = client.execute("""
                SELECT numero_nota, fecha, total, estado, procesado_central
                FROM notas_venta 
                ORDER BY fecha DESC 
                LIMIT 5
            """)
            rows = result.fetchall()
            print("\n   Últimas 5 notas:")
            for row in rows:
                procesado = "✅" if row[4] else "⏳"
                print(f"   {procesado} {row[0]} | {row[1]} | ${row[2]:,.2f} | {row[3]}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # 3. Visitas
    print("\n📍 VISITAS A CLIENTES")
    print("-" * 40)
    try:
        result = client.execute("SELECT COUNT(*) FROM visitas_clientes")
        total = result.fetchone()[0]
        print(f"   Total visitas: {total}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # 4. Posiciones GPS
    print("\n📡 POSICIONES GPS")
    print("-" * 40)
    try:
        result = client.execute("SELECT COUNT(*) FROM posiciones_preventistas")
        total = result.fetchone()[0]
        print(f"   Total posiciones: {total}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # 5. Productos
    print("\n📦 PRODUCTOS")
    print("-" * 40)
    try:
        result = client.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        total = result.fetchone()[0]
        print(f"   Total productos activos: {total}")
        
        # Mostrar algunos productos
        if total > 0:
            result = client.execute("""
                SELECT codigo_producto, descripcion, precio_venta, stock_actual
                FROM productos 
                WHERE activo = 1 
                LIMIT 3
            """)
            rows = result.fetchall()
            print("\n   Ejemplos:")
            for row in rows:
                print(f"   • {row[0]} - {row[1][:30]}... - ${row[2]:,.2f} (stock: {row[3]:,})")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # 6. Clientes
    print("\n👥 CLIENTES")
    print("-" * 40)
    try:
        result = client.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
        total = result.fetchone()[0]
        print(f"   Total clientes activos: {total}")
        
        # Mostrar algunos clientes
        if total > 0:
            result = client.execute("""
                SELECT razon_social, localidad, saldo_cuenta_corriente
                FROM clientes 
                WHERE activo = 1 
                LIMIT 3
            """)
            rows = result.fetchall()
            print("\n   Ejemplos:")
            for row in rows:
                print(f"   • {row[0][:25]}... - {row[1]} - ${row[2]:,.2f}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

def main():
    print("=" * 80)
    print("   🔍 INSPECCIÓN DE BASE DE DATOS TURSO")
    print("   FECHA:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # Verificar pyturso
    try:
        import pyturso
        print(f"✅ pyturso version: {getattr(pyturso, '__version__', 'desconocida')}")
    except ImportError:
        print("\n❌ pyturso no está instalado")
        print("   Instala con: pip install pyturso")
        print("\n   Si hay problemas, prueba con:")
        print("   pip install git+https://github.com/tursodatabase/pyturso.git")
        sys.exit(1)
    
    # Conectar
    client = conectar_turso()
    if not client:
        print("\n❌ No se pudo conectar a Turso")
        return
    
    try:
        # Mostrar resumen
        mostrar_resumen(client)
        
        # Verificar datos importantes
        verificar_datos_importantes(client)
        
        # Menú para ver tablas
        print("\n" + "=" * 80)
        print("   📋 VER TABLAS EN DETALLE")
        print("=" * 80)
        
        print("\nOpciones:")
        print("   1. parametros")
        print("   2. categorias")
        print("   3. productos")
        print("   4. lotes")
        print("   5. preventistas")
        print("   6. usuarios")
        print("   7. clientes")
        print("   8. notas_venta")
        print("   9. nota_venta_detalle")
        print("   10. visitas_clientes")
        print("   11. posiciones_preventistas")
        print("   12. sync_log")
        print("   0. Ver todas")
        print("   q. Salir")
        
        while True:
            opcion = input("\nSeleccione: ").strip()
            
            if opcion.lower() == 'q':
                break
            elif opcion == '0':
                tablas = ['parametros', 'categorias', 'productos', 'lotes', 
                         'preventistas', 'usuarios', 'clientes', 
                         'notas_venta', 'nota_venta_detalle', 
                         'visitas_clientes', 'posiciones_preventistas',
                         'sync_log']
                for tabla in tablas:
                    mostrar_tabla(client, tabla, limite=5)
                break
            else:
                tablas_map = {
                    '1': 'parametros',
                    '2': 'categorias',
                    '3': 'productos',
                    '4': 'lotes',
                    '5': 'preventistas',
                    '6': 'usuarios',
                    '7': 'clientes',
                    '8': 'notas_venta',
                    '9': 'nota_venta_detalle',
                    '10': 'visitas_clientes',
                    '11': 'posiciones_preventistas',
                    '12': 'sync_log',
                }
                
                if opcion in tablas_map:
                    mostrar_tabla(client, tablas_map[opcion], limite=20)
                else:
                    print("   Opción no válida")
        
        print("\n" + "=" * 80)
        print("   ✅ INSPECCIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()