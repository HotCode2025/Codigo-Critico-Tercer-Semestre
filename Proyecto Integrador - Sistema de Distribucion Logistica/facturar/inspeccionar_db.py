"""
INSPECCIÓN COMPLETA DE LA BASE DE DATOS LOCAL
=============================================
📌 Muestra TODOS los datos generados por generar_datos_masivos.py
📌 USO: python inspeccionar_db.py
"""

import sqlite3
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def obtener_conexion_local():
    """Obtiene conexión a la base de datos local"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'distribuidora.db')
    if not os.path.exists(db_path):
        # Intentar con otro nombre común
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'distribuidora.db')
    
    print(f"📁 Conectando a: {db_path}")
    return sqlite3.connect(db_path)

def mostrar_tabla(cur, tabla, limite=10):
    """Muestra el contenido completo de una tabla"""
    print("\n" + "=" * 80)
    print(f"   📊 TABLA: {tabla.upper()}")
    print("=" * 80)
    
    try:
        # Obtener estructura
        cur.execute(f"PRAGMA table_info({tabla})")
        columnas = cur.fetchall()
        
        if not columnas:
            print("   ⚠️ Tabla vacía o no existe")
            return
        
        nombres = [col[1] for col in columnas]
        
        # Contar registros
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        total = cur.fetchone()[0]
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
        
        # Construir consulta
        columnas_str = ", ".join(nombres)
        cur.execute(f"SELECT {columnas_str} FROM {tabla} LIMIT {limite}")
        rows = cur.fetchall()
        
        if not rows:
            print("      (sin datos)")
            return
        
        # Mostrar encabezados
        print("   " + "-" * 78)
        header = "   "
        for i, nombre in enumerate(nombres):
            header += f"{nombre[:12]:<14}"
        print(header)
        print("   " + "-" * 78)
        
        # Mostrar filas
        for row in rows:
            linea = "   "
            for i, valor in enumerate(row):
                if valor is None:
                    texto = "NULL"
                elif isinstance(valor, (int, float)):
                    if isinstance(valor, float):
                        texto = f"{valor:,.2f}"
                    else:
                        texto = f"{valor:,}"
                elif isinstance(valor, bytes):
                    texto = f"<BLOB {len(valor)} bytes>"
                else:
                    texto = str(valor)[:12]
                linea += f"{texto:<14}"
            print(linea)
        
        if total > limite:
            print(f"\n   ... y {total - limite} registros más")
        
    except sqlite3.OperationalError as e:
        print(f"   ❌ Error: {e}")

def mostrar_resumen_general(cur):
    """Muestra un resumen general de todas las tablas"""
    print("\n" + "=" * 80)
    print("   📊 RESUMEN GENERAL DE TODAS LAS TABLAS")
    print("=" * 80)
    
    # Obtener todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tablas = cur.fetchall()
    
    print(f"\n   {'TABLA':<30} {'REGISTROS':>12} {'COLUMNAS':>10}")
    print("   " + "-" * 80)
    
    total_registros = 0
    tabla_detalles = []
    
    for (tabla,) in tablas:
        if tabla.startswith('sqlite_'):
            continue
            
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cur.fetchone()[0]
        total_registros += count
        
        cur.execute(f"PRAGMA table_info({tabla})")
        cols = cur.fetchall()
        
        print(f"   {tabla:<30} {count:>12,} {len(cols):>10}")
        tabla_detalles.append({'nombre': tabla, 'registros': count, 'columnas': len(cols)})
    
    print("   " + "-" * 80)
    print(f"   {'TOTAL GENERAL':<30} {total_registros:>12,}")
    print()

def mostrar_datos_criticos(cur):
    """Muestra datos críticos específicos"""
    print("\n" + "=" * 80)
    print("   🔍 DATOS CRÍTICOS - VERIFICACIÓN DETALLADA")
    print("=" * 80)
    
    # 1. Parámetros
    print("\n📌 PARÁMETROS DE LA EMPRESA")
    print("-" * 40)
    try:
        cur.execute("SELECT * FROM parametros WHERE id = 1")
        row = cur.fetchone()
        if row:
            cur.execute("PRAGMA table_info(parametros)")
            cols = cur.fetchall()
            for i, col in enumerate(cols):
                print(f"   {col[1]}: {row[i]}")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 2. Productos destacados
    print("\n📌 PRODUCTOS DESTACADOS")
    print("-" * 40)
    try:
        cur.execute("""
            SELECT codigo_producto, descripcion, precio_venta, stock_actual 
            FROM productos 
            WHERE destacado = 1 
            LIMIT 5
        """)
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"   • {row[0]} - {row[1][:30]}... ${row[2]:,.2f} (stock: {row[3]:,})")
        else:
            print("   (sin productos destacados)")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 3. Clientes con mayor saldo
    print("\n📌 TOP 5 CLIENTES CON MAYOR SALDO")
    print("-" * 40)
    try:
        cur.execute("""
            SELECT razon_social, localidad, saldo_cuenta_corriente 
            FROM clientes 
            WHERE activo = 1 
            ORDER BY saldo_cuenta_corriente DESC 
            LIMIT 5
        """)
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"   • {row[0][:20]} - {row[1]}: ${row[2]:,.2f}")
        else:
            print("   (sin clientes con saldo)")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 4. Facturas recientes
    print("\n📌 ÚLTIMAS 5 FACTURAS")
    print("-" * 40)
    try:
        cur.execute("""
            SELECT numero_factura, fecha, total, estado 
            FROM facturas 
            ORDER BY fecha DESC 
            LIMIT 5
        """)
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"   • {row[0]} - {row[1]} - ${row[2]:,.2f} ({row[3]})")
        else:
            print("   (sin facturas)")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 5. Cobros
    print("\n📌 TOTAL DE COBROS")
    print("-" * 40)
    try:
        cur.execute("SELECT COUNT(*), SUM(importe) FROM cobros")
        count, total = cur.fetchone()
        print(f"   • Total cobros: {count}")
        print(f"   • Monto total: ${total:,.2f}" if total else "   • Monto total: $0.00")
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    # 6. Notas de venta por estado
    print("\n📌 NOTAS DE VENTA POR ESTADO")
    print("-" * 40)
    try:
        cur.execute("""
            SELECT estado, COUNT(*) as total 
            FROM notas_venta 
            GROUP BY estado
        """)
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"   • {row[0]}: {row[1]}")
        else:
            print("   (sin notas de venta)")
    except Exception as e:
        print(f"   ⚠️ {e}")

def buscar_datos_especificos(cur):
    """Busca datos específicos por solicitud del usuario"""
    print("\n" + "=" * 80)
    print("   🔎 BÚSQUEDA DE DATOS ESPECÍFICOS")
    print("=" * 80)
    
    while True:
        print("\nOpciones:")
        print("   1. Buscar cliente por nombre")
        print("   2. Buscar producto por código")
        print("   3. Buscar preventista por legajo")
        print("   4. Ver todas las categorías")
        print("   5. Ver todos los lotes")
        print("   6. Ver movimientos de cuenta corriente")
        print("   0. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '0':
            break
        elif opcion == '1':
            termino = input("Ingrese nombre a buscar: ").strip()
            if termino:
                cur.execute("""
                    SELECT razon_social, localidad, telefono, saldo_cuenta_corriente 
                    FROM clientes 
                    WHERE razon_social LIKE ? 
                    LIMIT 10
                """, (f'%{termino}%',))
                rows = cur.fetchall()
                if rows:
                    print(f"\n   Encontrados {len(rows)} clientes:")
                    for row in rows:
                        print(f"   • {row[0]} - {row[1]} - Tel: {row[2]} - Saldo: ${row[3]:,.2f}")
                else:
                    print("   No se encontraron clientes")
        
        elif opcion == '2':
            codigo = input("Ingrese código de producto: ").strip()
            if codigo:
                cur.execute("""
                    SELECT codigo_producto, descripcion, precio_venta, stock_actual 
                    FROM productos 
                    WHERE codigo_producto LIKE ? 
                    LIMIT 10
                """, (f'%{codigo}%',))
                rows = cur.fetchall()
                if rows:
                    print(f"\n   Encontrados {len(rows)} productos:")
                    for row in rows:
                        print(f"   • {row[0]} - {row[1][:30]} - ${row[2]:,.2f} (stock: {row[3]:,})")
                else:
                    print("   No se encontraron productos")
        
        elif opcion == '3':
            legajo = input("Ingrese legajo: ").strip()
            if legajo:
                cur.execute("""
                    SELECT nombre, apellido, legajo, telefono, zona 
                    FROM preventistas 
                    WHERE legajo LIKE ? 
                """, (f'%{legajo}%',))
                rows = cur.fetchall()
                if rows:
                    print(f"\n   Encontrados {len(rows)} preventistas:")
                    for row in rows:
                        print(f"   • {row[0]} {row[1]} ({row[2]}) - Tel: {row[3]}")
                        print(f"     Zona: {row[4][:60]}...")
                else:
                    print("   No se encontraron preventistas")
        
        elif opcion == '4':
            print("\n   CATEGORÍAS:")
            cur.execute("SELECT nombre FROM categorias ORDER BY nombre")
            rows = cur.fetchall()
            if rows:
                for i, (cat,) in enumerate(rows, 1):
                    print(f"   {i}. {cat}")
            else:
                print("   (sin categorías)")
        
        elif opcion == '5':
            print("\n   LOTES (últimos 10):")
            cur.execute("""
                SELECT numero_lote, codigo_producto, cantidad_actual, fecha_vencimiento 
                FROM lotes 
                ORDER BY fecha_vencimiento 
                LIMIT 10
            """)
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    print(f"   • {row[0]} - Prod: {row[1]} - Cant: {row[2]:,.0f} - Vence: {row[3]}")
            else:
                print("   (sin lotes)")
        
        elif opcion == '6':
            print("\n   MOVIMIENTOS DE CUENTA CORRIENTE (últimos 10):")
            cur.execute("""
                SELECT cliente_id, fecha, tipo_movimiento, importe, saldo_resultante 
                FROM cuenta_corriente_movimientos 
                ORDER BY fecha DESC 
                LIMIT 10
            """)
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    print(f"   • Cliente: {row[0][:8]}... - {row[1]} - {row[2]} - ${row[3]:,.2f} (saldo: ${row[4]:,.2f})")
            else:
                print("   (sin movimientos)")

def main():
    print("=" * 80)
    print("   🔍 INSPECCIÓN COMPLETA DE BASE DE DATOS LOCAL")
    print("   FECHA:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    try:
        db = obtener_conexion_local()
        cur = db.cursor()
        
        # Verificar que la base de datos existe y tiene tablas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cur.fetchall()
        
        if not tablas:
            print("\n❌ No se encontraron tablas en la base de datos.")
            print("   Asegúrate de que la base de datos esté inicializada.")
            db.close()
            return
        
        print(f"\n✅ Base de datos encontrada con {len(tablas)} tablas")
        
        # Mostrar resumen general
        mostrar_resumen_general(cur)
        
        # Mostrar datos críticos
        mostrar_datos_criticos(cur)
        
        # Preguntar si quiere ver tablas específicas
        print("\n" + "=" * 80)
        print("   📋 VER TABLAS ESPECÍFICAS")
        print("=" * 80)
        
        print("\n¿Qué tabla desea ver en detalle?")
        print("   1. parametros")
        print("   2. categorias")
        print("   3. productos")
        print("   4. lotes")
        print("   5. preventistas")
        print("   6. usuarios")
        print("   7. clientes")
        print("   8. notas_venta")
        print("   9. nota_venta_detalle")
        print("   10. facturas")
        print("   11. factura_detalle")
        print("   12. cuenta_corriente_movimientos")
        print("   13. cobros")
        print("   14. cheques")
        print("   0. Ver todas (puede ser extenso)")
        print("   q. Salir")
        
        while True:
            opcion = input("\nSeleccione una opción: ").strip()
            
            if opcion.lower() == 'q':
                break
            elif opcion == '0':
                for tabla in ['parametros', 'categorias', 'productos', 'lotes', 
                              'preventistas', 'usuarios', 'clientes', 
                              'notas_venta', 'nota_venta_detalle', 'facturas',
                              'factura_detalle', 'cuenta_corriente_movimientos',
                              'cobros', 'cheques']:
                    mostrar_tabla(cur, tabla, limite=5)
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
                    '10': 'facturas',
                    '11': 'factura_detalle',
                    '12': 'cuenta_corriente_movimientos',
                    '13': 'cobros',
                    '14': 'cheques',
                }
                
                if opcion in tablas_map:
                    mostrar_tabla(cur, tablas_map[opcion], limite=20)
                else:
                    print("   Opción no válida")
        
        # Buscar datos específicos
        buscar_datos_especificos(cur)
        
        db.close()
        
        print("\n" + "=" * 80)
        print("   ✅ INSPECCIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()