"""
INSPECCIÓN COMPLETA DE TURSO - VERSIÓN REQUESTS
===============================================
📌 Versión estable usando solo requests
📌 USO: python inspeccionar_turso_completo.py
"""

import requests
import json
from datetime import datetime

# Configuración
TURSO_URL = "https://nube-clarionda.aws-us-east-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODI1MTQyMTEsImlkIjoiMDE5ZjA2MjAtM2YwMS03NzgwLWI0ZDgtNDU3YWY3OWYyNzY1IiwicmlkIjoiOWU1YzkyZDktMmI3MC00MTJjLThkNmYtZjgzMzY5NjM4ODViIn0.H_PKJrBCAvNH5WPaCYUJOgHDVDPQHw7Y4qir1zFlx6MSih-vjUZnojZdp5AmMwAz9151gNCjX-rC3oGuj_ETAw"

def query(sql):
    """Ejecuta una query en Turso"""
    headers = {"Authorization": f"Bearer {TURSO_TOKEN}", "Content-Type": "application/json"}
    payload = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
    
    try:
        r = requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data.get('results') and data['results'][0].get('response'):
                result = data['results'][0]['response']['result']
                if result and result.get('rows'):
                    return result['rows']
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def obtener_valor(row, index=0):
    """Obtiene un valor de una fila"""
    if isinstance(row, dict):
        valores = list(row.values())
        return valores[index] if index < len(valores) else None
    return row[index] if index < len(row) else None

def mostrar_tabla(nombre, limite=10):
    """Muestra el contenido de una tabla"""
    print("\n" + "=" * 80)
    print(f"   📊 TABLA: {nombre.upper()}")
    print("=" * 80)
    
    # Obtener estructura
    cols = query(f"PRAGMA table_info({nombre})")
    if not cols:
        print("   ❌ Tabla no encontrada")
        return
    
    # Nombres de columnas
    nombres = []
    for col in cols:
        if isinstance(col, dict):
            valores = list(col.values())
            nombres.append(valores[1] if len(valores) > 1 else '')
        else:
            nombres.append(col[1])
    
    # Contar registros
    count_result = query(f"SELECT COUNT(*) FROM {nombre}")
    total = 0
    if count_result:
        total = obtener_valor(count_result[0])
    
    print(f"\n   📈 Total registros: {total}")
    
    if total == 0:
        print("   ⚠️ Tabla vacía")
        return
    
    # Estructura
    print("\n   📋 Estructura:")
    for col in cols:
        if isinstance(col, dict):
            valores = list(col.values())
            nombre_col = valores[1] if len(valores) > 1 else ''
            tipo = valores[2] if len(valores) > 2 else ''
            pk = valores[5] if len(valores) > 5 else 0
        else:
            nombre_col = col[1]
            tipo = col[2]
            pk = col[5]
        print(f"      • {nombre_col}: {tipo} {'PK' if pk else ''}")
    
    # Datos
    print(f"\n   📝 Datos (mostrando hasta {limite} registros):")
    
    columnas_str = ", ".join(nombres[:8])
    rows = query(f"SELECT {columnas_str} FROM {nombre} LIMIT {limite}")
    
    if not rows:
        print("      (sin datos)")
        return
    
    # Encabezados
    print("   " + "-" * 78)
    header = "   "
    for nombre_col in nombres[:8]:
        header += f"{nombre_col[:12]:<14}"
    print(header)
    print("   " + "-" * 78)
    
    # Filas
    for row in rows:
        linea = "   "
        if isinstance(row, dict):
            valores = list(row.values())
        else:
            valores = row
        
        for valor in valores[:8]:
            if valor is None:
                texto = "NULL"
            elif isinstance(valor, float):
                texto = f"{valor:,.2f}"
            elif isinstance(valor, int):
                texto = f"{valor:,}"
            elif isinstance(valor, bytes):
                texto = f"<BLOB>"
            else:
                texto = str(valor)[:12]
            linea += f"{texto:<14}"
        print(linea)
    
    if total > limite:
        print(f"\n   ... y {total - limite} registros más")

def main():
    print("=" * 80)
    print("   🔍 INSPECCIÓN DE TURSO")
    print(f"   FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Probar conexión
    print("\n🔗 Probando conexión...")
    test = query("SELECT 1")
    if test is None:
        print("❌ No se pudo conectar a Turso")
        return
    print("✅ Conectado!")
    
    # Listar tablas
    print("\n📊 TABLAS EN TURSO:")
    print("-" * 40)
    
    tablas = query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    if tablas:
        for row in tablas:
            # CORRECCIÓN REALIZADA AQUÍ:
            nombre = obtener_valor(row)
            if nombre and not nombre.startswith('sqlite_'):
                count_result = query(f"SELECT COUNT(*) FROM {nombre}")
                count = obtener_valor(count_result[0]) if count_result else 0
                print(f"   • {nombre}: {count:,} registros")
    
    # Menú
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
    print("   0. Ver todas")
    print("   q. Salir")
    
    while True:
        opcion = input("\nSeleccione: ").strip()
        
        if opcion.lower() == 'q':
            break
        
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
        }
        
        if opcion == '0':
            for tabla in tablas_map.values():
                mostrar_tabla(tabla, limite=5)
            break
        elif opcion in tablas_map:
            mostrar_tabla(tablas_map[opcion], limite=20)
        else:
            print("   Opción no válida")
    
    print("\n" + "=" * 80)
    print("   ✅ INSPECCIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ requests no está instalado")
        print("   Instala con: pip install requests")
        exit(1)
    
    main()