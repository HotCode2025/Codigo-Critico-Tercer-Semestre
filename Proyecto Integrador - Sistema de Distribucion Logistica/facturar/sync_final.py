#!/usr/bin/env python3
"""
SINCRONIZACIÓN FINAL - CONVERSIÓN DE TIPOS CORRECTA
"""

from db.db_manager import obtener_conexion
from utilidades.turso_client import get_turso_client
import json

def convertir_valor(key, value):
    """Convierte el valor al tipo correcto según la columna"""
    # Columnas que deben ser INTEGER
    if key in ['activo', 'aplica_tasa_municipal', 'destacado']:
        if isinstance(value, str):
            return int(value) if value else 0
        return 1 if value else 0
    
    # Columnas que deben ser REAL
    if key in ['precio_costo', 'precio_venta', 'stock_actual', 'stock_critico', 
               'limite_credito', 'saldo_cuenta_corriente', 'latitud', 'longitud',
               'cantidad_inicial', 'cantidad_actual']:
        if value is None or value == '':
            return 0.0
        return float(value)
    
    # Columnas de fecha
    if key in ['fecha', 'fecha_alta', 'fecha_emision', 'fecha_vencimiento',
               'created_at', 'updated_at']:
        if value is None:
            return None
        return str(value)
    
    # TODO lo demás como string
    return str(value) if value is not None else None

def sync_table(table):
    db = obtener_conexion()
    client = get_turso_client()
    
    if not client.is_connected():
        print(f'❌ No hay conexión a Turso')
        return
    
    cur = db.cursor()
    cur.execute(f'SELECT * FROM {table} WHERE activo = 1')
    rows = cur.fetchall()
    
    print(f'📤 {table}: {len(rows)} registros')
    
    enviados = 0
    errores = 0
    
    for row in rows:
        data = dict(row)
        # Limpiar None y convertir tipos
        clean_data = {}
        for key, value in data.items():
            if value is None:
                continue
            clean_data[key] = convertir_valor(key, value)
        
        try:
            if client.insert(table, clean_data):
                enviados += 1
                if enviados % 50 == 0:
                    print(f'   📍 {enviados}/{len(rows)} enviados')
            else:
                errores += 1
                print(f'   ❌ Error en: {clean_data.get("id", "sin id")[:8]}')
        except Exception as e:
            errores += 1
            print(f'   ❌ Excepción: {e}')
    
    print(f'   ✅ {table}: {enviados} enviados, {errores} errores')
    db.close()

# Tablas a sincronizar
tablas = ['clientes', 'productos', 'preventistas', 'categorias', 'lotes', 'usuarios']

print('=' * 60)
print('🔄 SINCRONIZACIÓN FINAL')
print('=' * 60)

for tabla in tablas:
    sync_table(tabla)

# Verificar
client = get_turso_client()
print('\n📊 VERIFICANDO EN TURSO:')
for tabla in tablas:
    try:
        count = client.get_one(f'SELECT COUNT(*) as total FROM {tabla}')
        print(f'   📄 {tabla}: {count["total"] if count else 0} registros')
    except:
        print(f'   ❌ {tabla}: Error')
