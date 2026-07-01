"""
INSPECCIÓN DE TURSO VÍA API REST - VERSIÓN FINAL
================================================
📌 Usa la API REST de Turso directamente
📌 USO: python inspeccionar_turso_rest.py
📌 REQUIERE: pip install requests
"""

import requests
import json
import sys
from datetime import datetime

# ============================================================
# CONFIGURACIÓN - DEL ARCHIVO turso-facturar.txt
# ============================================================

TURSO_URL = "https://nube-clarionda.aws-us-east-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODI1MTQyMTEsImlkIjoiMDE5ZjA2MjAtM2YwMS03NzgwLWI0ZDgtNDU3YWY3OWYyNzY1IiwicmlkIjoiOWU1YzkyZDktMmI3MC00MTJjLThkNmYtZjgzMzY5NjM4ODViIn0.H_PKJrBCAvNH5WPaCYUJOgHDVDPQHw7Y4qir1zFlx6MSih-vjUZnojZdp5AmMwAz9151gNCjX-rC3oGuj_ETAw"

def ejecutar_query(sql):
    """Ejecuta una query vía REST API de Turso"""
    headers = {
        "Authorization": f"Bearer {TURSO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {"sql": sql}
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{TURSO_URL}/v2/pipeline",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and data['results'][0].get('response'):
                result = data['results'][0]['response']['result']
                if result and result.get('rows'):
                    return result['rows']
                elif result and result.get('cols'):
                    return []
            return None
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Timeout - La conexión tardó demasiado")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - No se pudo conectar a Turso")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def obtener_valor(row, index=0):
    """Obtiene un valor de una fila, sea diccionario o lista"""
    if isinstance(row, dict):
        # Si es diccionario, obtener el primer valor o el valor por índice
        valores = list(row.values())
        if index < len(valores):
            return valores[index]
        return None
    elif isinstance(row, (list, tuple)):
        if index < len(row):
            return row[index]
        return None
    return row

def obtener_nombre_columna(col, index=1):
    """Obtiene el nombre de una columna de PRAGMA table_info"""
    if isinstance(col, dict):
        # Intentar obtener 'name' o el segundo valor
        if 'name' in col:
            return col['name']
        valores = list(col.values())
        if len(valores) > 1:
            return valores[1]
        return valores[0] if valores else None
    elif isinstance(col, (list, tuple)):
        if len(col) > index:
            return col[index]
        return col[0] if col else None
    return col

def mostrar_resumen():
    """Muestra resumen de todas las tablas"""
    print("\n" + "=" * 80)
    print("   📊 RESUMEN GENERAL - TURSO")
    print("=" * 80)
    
    # Obtener todas las tablas
    tablas = ejecutar_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    
    if tablas is None:
        print("   ❌ No se pudieron obtener las tablas")
        return
    
    if not tablas:
        print("   ⚠️ No se encontraron tablas")
        return
    
    print(f"\n   {'TABLA':<30} {'REGISTROS':>12}")
    print("   " + "-" * 80)
    
    total = 0
    for row in tablas:
        # Obtener el nombre de la tabla
        if isinstance(row, dict):
            tabla = row.get('name')
            if tabla is None:
                # Si no tiene 'name', tomar el primer valor
                valores = list(row.values())
                tabla = valores[0] if valores else None
        else:
            tabla = row[0]
        
        if not tabla or tabla.startswith('sqlite_'):
            continue
        
        resultado = ejecutar_query(f"SELECT COUNT(*) FROM {tabla}")
        if resultado is not None and resultado:
            # Obtener el count
            if isinstance(resultado[0], dict):
                count = list(resultado[0].values())[0]
            else:
                count = resultado[0][0]
            total += count
            print(f"   {tabla:<30} {count:>12,}")
        else:
            print(f"   {tabla:<30} {'ERROR':>12}")
    
    print("   " + "-" * 80)
    print(f"   {'TOTAL':<30} {total:>12,}")
    print()

def mostrar_tabla(tabla, limite=10):
    """Muestra contenido de una tabla específica"""
    print("\n" + "=" * 80)
    print(f"   📊 TABLA: {tabla.upper()}")
    print("=" * 80)
    
    # Obtener estructura
    columnas = ejecutar_query(f"PRAGMA table_info({tabla})")
    
    if columnas is None:
        print("   ❌ Error al obtener estructura de la tabla")
        return
    
    if not columnas:
        print("   ⚠️ Tabla no existe o está vacía")
        return
    
    # Obtener nombres de columnas
    nombres = []
    for col in columnas:
        if isinstance(col, dict):
            nombre = col.get('name')
            if nombre is None:
                valores = list(col.values())
                nombre = valores[1] if len(valores) > 1 else valores[0]
        else:
            nombre = col[1]
        nombres.append(nombre)
    
    # Contar registros
    resultado = ejecutar_query(f"SELECT COUNT(*) FROM {tabla}")
    if resultado is None:
        print("   ❌ Error al contar registros")
        return
    
    total = 0
    if resultado:
        if isinstance(resultado[0], dict):
            total = list(resultado[0].values())[0]
        else:
            total = resultado[0][0]
    
    print(f"\n   📈 Total registros: {total}")
    
    if total == 0:
        print("   ⚠️ Tabla vacía")
        return
    
    # Mostrar estructura
    print("\n   📋 Estructura:")
    for col in columnas:
        if isinstance(col, dict):
            valores = list(col.values())
            nombre = col.get('name') or (valores[1] if len(valores) > 1 else valores[0])
            tipo = col.get('type') or (valores[2] if len(valores) > 2 else '')
            pk = col.get('pk') or (valores[5] if len(valores) > 5 else 0)
        else:
            nombre = col[1]
            tipo = col[2]
            pk = col[5]
        print(f"      • {nombre}: {tipo} {'PK' if pk else ''}")
    
    # Mostrar datos
    print(f"\n   📝 Datos (mostrando hasta {limite} registros):")
    
    columnas_str = ", ".join(nombres)
    resultado = ejecutar_query(f"SELECT {columnas_str} FROM {tabla} LIMIT {limite}")
    
    if resultado is None:
        print("      ❌ Error al obtener datos")
        return
    
    rows = resultado
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
        # Si es diccionario, obtener valores
        if isinstance(row, dict):
            valores = list(row.values())
        else:
            valores = row
            
        for i, valor in enumerate(valores[:8]):
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

def verificar_datos_importantes():
    """Verifica datos críticos en Turso"""
    print("\n" + "=" * 80)
    print("   🔍 VERIFICACIÓN DE DATOS IMPORTANTES")
    print("=" * 80)
    
    # 1. Parámetros
    print("\n📌 PARÁMETROS DE LA EMPRESA")
    print("-" * 40)
    resultado = ejecutar_query("SELECT * FROM parametros WHERE id = 1")
    if resultado:
        columnas = ejecutar_query("PRAGMA table_info(parametros)")
        if columnas:
            for i, col in enumerate(columnas):
                nombre = obtener_nombre_columna(col)
                valor = obtener_valor(resultado[0], i)
                print(f"   • {nombre}: {valor}")
    else:
        print("   ⚠️ No se encontraron parámetros")
    
    # 2. Notas de venta (datos que vienen de la App)
    print("\n📋 NOTAS DE VENTA (Datos de App)")
    print("-" * 40)
    resultado = ejecutar_query("SELECT COUNT(*) FROM notas_venta")
    if resultado:
        total = obtener_valor(resultado[0])
        print(f"   Total: {total}")
        
        if total and total > 0:
            resultado = ejecutar_query("""
                SELECT numero_nota, fecha, total, estado, procesado_central
                FROM notas_venta 
                ORDER BY fecha DESC 
                LIMIT 5
            """)
            if resultado:
                print("\n   Últimas 5 notas:")
                for row in resultado:
                    vals = list(row.values()) if isinstance(row, dict) else row
                    procesado = "✅" if vals[4] else "⏳"
                    print(f"   {procesado} {vals[0]} | {vals[1]} | ${vals[2]:,.2f} | {vals[3]}")
    else:
        print("   ⚠️ Error al consultar notas de venta")
    
    # 3. Visitas
    print("\n📍 VISITAS A CLIENTES")
    print("-" * 40)
    resultado = ejecutar_query("SELECT COUNT(*) FROM visitas_clientes")
    if resultado:
        total = obtener_valor(resultado[0])
        print(f"   Total visitas: {total}")
    else:
        print("   ⚠️ Error al consultar visitas")
    
    # 4. Posiciones GPS
    print("\n📡 POSICIONES GPS")
    print("-" * 40)
    resultado = ejecutar_query("SELECT COUNT(*) FROM posiciones_preventistas")
    if resultado:
        total = obtener_valor(resultado[0])
        print(f"   Total posiciones: {total}")
    else:
        print("   ⚠️ Error al consultar posiciones")
    
    # 5. Productos
    print("\n📦 PRODUCTOS")
    print("-" * 40)
    resultado = ejecutar_query("SELECT COUNT(*) FROM productos WHERE activo = 1")
    if resultado:
        total = obtener_valor(resultado[0])
        print(f"   Total productos activos: {total}")
    else:
        print("   ⚠️ Error al consultar productos")
    
    # 6. Clientes
    print("\n👥 CLIENTES")
    print("-" * 40)
    resultado = ejecutar_query("SELECT COUNT(*) FROM clientes WHERE activo = 1")
    if resultado:
        total = obtener_valor(resultado[0])
        print(f"   Total clientes activos: {total}")
    else:
        print("   ⚠️ Error al consultar clientes")

def main():
    print("=" * 80)
    print("   🔍 INSPECCIÓN DE BASE DE DATOS TURSO")
    print("   FECHA:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # Verificar requests
    try:
        import requests
    except ImportError:
        print("\n❌ requests no está instalado")
        print("   Instala con: pip install requests")
        sys.exit(1)
    
    # Probar conexión
    print("\n🔍 Probando conexión a Turso...")
    resultado = ejecutar_query("SELECT 1")
    
    if resultado is None:
        print("\n❌ No se pudo conectar a Turso")
        print("\n   Posibles causas:")
        print("   • Token inválido o expirado")
        print("   • URL incorrecta")
        print("   • Sin conexión a internet")
        return
    
    print("✅ Conexión exitosa")
    
    # Mostrar resumen general
    mostrar_resumen()
    
    # Verificar datos importantes
    verificar_datos_importantes()
    
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
                mostrar_tabla(tabla, limite=5)
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
                mostrar_tabla(tablas_map[opcion], limite=20)
            else:
                print("   Opción no válida")
    
    print("\n" + "=" * 80)
    print("   ✅ INSPECCIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    main()