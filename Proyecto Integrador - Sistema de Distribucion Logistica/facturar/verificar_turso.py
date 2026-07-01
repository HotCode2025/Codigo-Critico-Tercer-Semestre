#!/usr/bin/env python3
"""
Código Crítico - Tercer Semestre Año 2026
==================================================
VERIFICAR SINCRONIZACIÓN CON TURSO (CORREGIDO)
==================================================
"""

import sqlite3
from datetime import datetime
from utilidades.turso_client import get_turso_client
from db.db_manager import obtener_conexion, _ruta_base_datos


class Colores:
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'
    RESET = '\033[0m'
    NEGRITA = '\033[1m'


def print_color(texto, color=Colores.BLANCO):
    print(f"{color}{texto}{Colores.RESET}")


def conectar_local():
    try:
        conn = sqlite3.connect(_ruta_base_datos())
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print_color(f"❌ Error conectando a local: {e}", Colores.ROJO)
        return None


def verificar_conexion_turso():
    print_color("\n🔌 VERIFICANDO CONEXIÓN A TURSO", Colores.NEGRITA + Colores.AZUL)
    print("-" * 60)
    
    client = get_turso_client()
    
    if client.is_connected():
        print_color("✅ Conexión a Turso: OK", Colores.VERDE)
        if hasattr(client, 'config') and client.config:
            print_color(f"   📌 URL: {client.config.url}", Colores.CYAN)
        stats = client.get_stats() if hasattr(client, 'get_stats') else {}
        print_color(f"   📊 Consultas ejecutadas: {stats.get('queries_executed', 0)}", Colores.CYAN)
        return client
    else:
        print_color("❌ Sin conexión a Turso", Colores.ROJO)
        return None


def listar_tablas_turso(client):
    print_color("\n📋 TABLAS EN TURSO", Colores.NEGRITA + Colores.AZUL)
    print("-" * 60)
    
    try:
        tablas = client.get_all("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        
        if not tablas:
            print_color("   ℹ️ No hay tablas en Turso", Colores.AMARILLO)
            return []
        
        print_color(f"   Encontradas {len(tablas)} tablas:", Colores.VERDE)
        for t in tablas:
            try:
                count_result = client.get_one(f"SELECT COUNT(*) as total FROM {t['name']}")
                total = int(count_result['total']) if count_result and count_result.get('total') is not None else 0
            except:
                total = 0
            print_color(f"   📄 {t['name']:<30} ({total} registros)", Colores.CYAN)
        
        return [t['name'] for t in tablas]
    except Exception as e:
        print_color(f"❌ Error listando tablas: {e}", Colores.ROJO)
        return []


def verificar_tabla_turso(client, tabla, limite=5):
    print_color(f"\n📊 TABLA: {tabla.upper()}", Colores.NEGRITA + Colores.MAGENTA)
    print("-" * 60)
    
    try:
        try:
            count_result = client.get_one(f"SELECT COUNT(*) as total FROM {tabla}")
            total = int(count_result['total']) if count_result and count_result.get('total') is not None else 0
        except:
            total = 0
        print_color(f"   Registros totales en Turso: {total}", Colores.CYAN)
        
        if total == 0:
            print_color("   ℹ️ Tabla vacía", Colores.AMARILLO)
            return
        
        try:
            datos = client.get_all(f"SELECT * FROM {tabla} LIMIT {limite}")
        except:
            datos = []
        
        if datos:
            print_color(f"\n   Datos (mostrando {min(len(datos), limite)} de {total}):", Colores.CYAN)
            print("   " + "-" * 50)
            columnas = list(datos[0].keys())
            headers = " | ".join([f"{col[:15]:<15}" for col in columnas])
            print(f"   {headers}")
            print("   " + "-" * 50)
            
            for row in datos:
                valores = []
                for col in columnas:
                    val = row.get(col)
                    if val is None:
                        valores.append("NULL".ljust(15))
                    else:
                        texto = str(val)[:15]
                        if len(str(val)) > 15:
                            texto += "..."
                        valores.append(f"{texto:<15}")
                print(f"   {' | '.join(valores)}")
            
            if total > limite:
                print_color(f"\n   ... y {total - limite} registros más", Colores.AMARILLO)
    except Exception as e:
        print_color(f"❌ Error verificando tabla {tabla}: {e}", Colores.ROJO)


def verificar_preventistas(client):
    print_color("\n👥 VERIFICANDO PREVENTISTAS", Colores.NEGRITA + Colores.MAGENTA)
    print("-" * 60)
    
    try:
        try:
            count_result = client.get_one("SELECT COUNT(*) as total FROM preventistas")
            total_turso = int(count_result['total']) if count_result and count_result.get('total') is not None else 0
        except Exception as e:
            print(f"   ⚠️ Error contando: {e}")
            total_turso = 0
            
        print_color(f"   📊 Preventistas en Turso: {total_turso}", Colores.CYAN)
        
        if total_turso > 0:
            try:
                preventistas = client.get_all("SELECT id, nombre, apellido, legajo, telefono FROM preventistas")
                print_color(f"\n   📋 LISTA DE PREVENTISTAS EN TURSO:", Colores.CYAN)
                for p in preventistas:
                    print_color(f"      - {p.get('nombre', '')} {p.get('apellido', '')} | Legajo: {p.get('legajo', '-')} | Tel: {p.get('telefono', '-')}", Colores.CYAN)
            except Exception as e:
                print_color(f"   ⚠️ No se pudieron obtener los detalles: {e}", Colores.AMARILLO)
        else:
            print_color("   ⚠️ No hay preventistas en Turso", Colores.AMARILLO)
            print_color("   💡 Crea un preventista en la Central y sincroniza", Colores.AMARILLO)
    except Exception as e:
        print_color(f"❌ Error verificando preventistas: {e}", Colores.ROJO)


def verificar_clientes(client):
    print_color("\n👥 VERIFICANDO CLIENTES", Colores.NEGRITA + Colores.MAGENTA)
    print("-" * 60)
    
    try:
        try:
            count_result = client.get_one("SELECT COUNT(*) as total FROM clientes")
            total_turso = int(count_result['total']) if count_result and count_result.get('total') is not None else 0
        except Exception as e:
            print(f"   ⚠️ Error contando: {e}")
            total_turso = 0
            
        print_color(f"   📊 Clientes en Turso: {total_turso}", Colores.CYAN)
        
        if total_turso > 0:
            try:
                clientes = client.get_all("SELECT id, razon_social, cuit, telefono FROM clientes LIMIT 5")
                print_color(f"\n   📋 PRIMEROS 5 CLIENTES:", Colores.CYAN)
                for c in clientes:
                    print_color(f"      - {c.get('razon_social', '')} | CUIT: {c.get('cuit', '-')}", Colores.CYAN)
            except Exception as e:
                print_color(f"   ⚠️ No se pudieron obtener los detalles: {e}", Colores.AMARILLO)
    except Exception as e:
        print_color(f"❌ Error verificando clientes: {e}", Colores.ROJO)


def comparar_con_local(tabla):
    print_color(f"\n🔄 COMPARANDO '{tabla}' LOCAL vs TURSO", Colores.NEGRITA + Colores.AZUL)
    print("-" * 60)
    
    conn_local = conectar_local()
    if not conn_local:
        return
    
    client = get_turso_client()
    if not client.is_connected():
        conn_local.close()
        return
    
    try:
        cur = conn_local.cursor()
        try:
            cur.execute(f"SELECT COUNT(*) as total FROM {tabla}")
            row = cur.fetchone()
            total_local = int(row['total']) if row and row['total'] is not None else 0
        except Exception as e:
            print(f"   ⚠️ Error contando local: {e}")
            total_local = 0
        
        try:
            count_result = client.get_one(f"SELECT COUNT(*) as total FROM {tabla}")
            total_turso = int(count_result['total']) if count_result and count_result.get('total') is not None else 0
        except Exception as e:
            print(f"   ⚠️ Error contando Turso: {e}")
            total_turso = 0
        
        print_color(f"   📊 LOCAL: {total_local} registros", Colores.CYAN)
        print_color(f"   📊 TURSO: {total_turso} registros", Colores.CYAN)
        
        if total_local == total_turso:
            print_color(f"   ✅ {tabla}: Sincronizado correctamente", Colores.VERDE)
        else:
            diff = int(total_local) - int(total_turso)
            print_color(f"   ⚠️ {tabla}: Diferencia de {abs(diff)} registros", Colores.AMARILLO)
            if diff > 0:
                print_color(f"   💡 {diff} registros faltan en Turso", Colores.AMARILLO)
            elif diff < 0:
                print_color(f"   💡 {abs(diff)} registros extra en Turso", Colores.AMARILLO)
    except Exception as e:
        print_color(f"❌ Error comparando {tabla}: {e}", Colores.ROJO)
    finally:
        conn_local.close()


def verificar_sincronizacion_manual():
    print_color("\n🔄 EJECUTANDO SINCRONIZACIÓN MANUAL", Colores.NEGRITA + Colores.AZUL)
    print("-" * 60)
    
    try:
        from utilidades.central_sync import sincronizar_ahora
        db = obtener_conexion()
        resultado = sincronizar_ahora(db)
        
        if resultado:
            print_color("✅ Sincronización completada", Colores.VERDE)
            central_a_turso = resultado.get('central_a_turso', {})
            for tabla, res in central_a_turso.items():
                if res.get('sent', 0) > 0:
                    print_color(f"   📤 {tabla}: {res['sent']} registros enviados", Colores.VERDE)
        else:
            print_color("❌ Error en sincronización", Colores.ROJO)
    except Exception as e:
        print_color(f"❌ Error: {e}", Colores.ROJO)


def main():
    print("=" * 80)
    print_color(f"🔍 VERIFICANDO SINCRONIZACIÓN CON TURSO", Colores.NEGRITA + Colores.AZUL)
    print_color(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colores.CYAN)
    print("=" * 80)
    
    client = verificar_conexion_turso()
    if not client:
        return
    
    tablas = listar_tablas_turso(client)
    
    for tabla in tablas:
        if tabla not in ['sqlite_sequence', 'sync_log', 'sync_queue', 'sync_log_history', 'sync_conflictos']:
            verificar_tabla_turso(client, tabla, limite=3)
    
    verificar_preventistas(client)
    verificar_clientes(client)
    
    print_color("\n" + "=" * 80, Colores.NEGRITA)
    print_color("📊 COMPARACIÓN LOCAL VS TURSO", Colores.NEGRITA + Colores.AZUL)
    print("=" * 80)
    
    for tabla in ['clientes', 'productos', 'preventistas', 'categorias', 'lotes', 'usuarios']:
        if tabla in tablas:
            comparar_con_local(tabla)
    
    print_color("\n" + "=" * 80, Colores.NEGRITA)
    print_color("📌 OPCIONES", Colores.NEGRITA + Colores.AZUL)
    print("=" * 80)
    print("   1. Salir")
    print("   2. Ejecutar sincronización manual")
    
    opcion = input("\n👉 Seleccione una opción: ").strip()
    
    if opcion == '2':
        verificar_sincronizacion_manual()
        verificar_preventistas(client)
    
    print_color("\n✅ Verificación completada", Colores.VERDE)


if __name__ == "__main__":
    main()