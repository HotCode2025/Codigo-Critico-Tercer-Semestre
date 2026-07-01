#!/usr/bin/env python3
"""
SINCRONIZACIÓN DIRECTA - SIN COLUMNA version
"""

import sqlite3
import json
import os
import requests
from datetime import datetime

print("=" * 60)
print("🔄 SINCRONIZACIÓN DIRECTA A TURSO")
print("=" * 60)

# ============================================================
# 1. LEER CONFIGURACIÓN
# ============================================================
print("\n📁 1. CONFIGURACIÓN...")

url = None
token = None

with open('turso-facturar.txt', 'r') as f:
    lines = f.read().strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('libsql://') or line.startswith('https://'):
            url = line.replace('libsql://', 'https://')
        elif line and not line.startswith('#') and line.startswith('eyJ'):
            token = line

if not url.endswith('/v2/pipeline'):
    url = url.rstrip('/') + '/v2/pipeline'

print(f"   📌 URL: {url}")
print(f"   📌 Token: {token[:30]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# ============================================================
# 2. COLUMNAS PERMITIDAS PARA CADA TABLA
# ============================================================
# ⚠️ SOLO columnas que existen en Turso (sin 'version')

COLUMNAS_POR_TABLA = {
    'clientes': [
        'id', 'razon_social', 'cuit', 'condicion_iva', 'domicilio',
        'telefono', 'whatsapp', 'email', 'aplica_tasa_municipal',
        'limite_credito', 'saldo_cuenta_corriente', 'fecha_alta',
        'activo', 'latitud', 'longitud', 'preventista_id',
        'localidad', 'provincia', 'calle', 'numero',
        'created_at', 'updated_at'
    ],
    'productos': [
        'id', 'codigo_producto', 'descripcion', 'precio_costo',
        'precio_venta', 'stock_actual', 'stock_critico',
        'unidad_medida', 'categoria_id', 'foto', 'url_foto',
        'detalle', 'precio_oferta', 'destacado', 'activo',
        'created_at', 'updated_at'
    ],
    'preventistas': [
        'id', 'nombre', 'apellido', 'legajo', 'telefono',
        'email', 'zona', 'activo', 'created_at', 'updated_at'
    ],
    'categorias': [
        'id', 'nombre', 'descripcion', 'activo',
        'created_at', 'updated_at'
    ],
    'lotes': [
        'id', 'producto_id', 'codigo_producto', 'numero_lote',
        'fecha_vencimiento', 'cantidad_inicial', 'cantidad_actual',
        'fecha_ingreso', 'created_at', 'updated_at'
    ],
    'usuarios': [
        'id', 'username', 'password_hash', 'rol',
        'preventista_id', 'cliente_id', 'activo',
        'created_at', 'updated_at'
    ]
}

# ============================================================
# 3. CONEXIÓN LOCAL
# ============================================================
print("\n📁 2. LEYENDO DATOS LOCALES...")

db_path = "distribuidora.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# ============================================================
# 4. FUNCIÓN PARA ENVIAR DATOS
# ============================================================

def enviar_tabla(nombre_tabla):
    """Envía una tabla completa a Turso"""
    print(f"\n📤 ENVIANDO: {nombre_tabla}")
    
    # Obtener columnas permitidas
    columnas = COLUMNAS_POR_TABLA.get(nombre_tabla, [])
    if not columnas:
        print(f"   ⚠️ No hay columnas definidas para {nombre_tabla}")
        return 0
    
    # Obtener datos
    cur = conn.cursor()
    col_str = ", ".join(columnas)
    try:
        cur.execute(f"SELECT {col_str} FROM {nombre_tabla}")
    except Exception as e:
        print(f"   ❌ Error leyendo {nombre_tabla}: {e}")
        return 0
    
    rows = cur.fetchall()
    if not rows:
        print(f"   ℹ️ {nombre_tabla}: sin datos")
        return 0
    
    print(f"   📊 {len(rows)} registros")
    
    enviados = 0
    errores = 0
    
    for row in rows:
        # Construir datos SOLO con columnas permitidas
        data = {}
        for col in columnas:
            val = row[col]
            if val is None:
                continue
            
            # Convertir tipos
            if col in ['activo', 'aplica_tasa_municipal', 'destacado']:
                data[col] = 1 if val else 0
            elif col in ['precio_costo', 'precio_venta', 'stock_actual', 'stock_critico',
                         'limite_credito', 'saldo_cuenta_corriente', 'latitud', 'longitud',
                         'cantidad_inicial', 'cantidad_actual', 'importe', 'total', 'iva', 'subtotal']:
                data[col] = float(val) if val else 0.0
            else:
                data[col] = str(val) if val is not None else None
        
        if not data:
            continue
        
        # Construir SQL
        cols = list(data.keys())
        placeholders = ", ".join(["?" for _ in cols])
        col_str_sql = ", ".join(cols)
        sql = f"INSERT OR REPLACE INTO {nombre_tabla} ({col_str_sql}) VALUES ({placeholders})"
        
        # Formatear argumentos para Turso (TODOS como TEXT)
        args = []
        for v in data.values():
            if v is None:
                args.append({"type": "null", "value": None})
            else:
                args.append({"type": "text", "value": str(v)})
        
        # Enviar
        payload = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": sql,
                        "args": args
                    }
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data_resp = response.json()
                if data_resp.get('results'):
                    result = data_resp['results'][0]
                    if result.get('type') == 'error':
                        errores += 1
                        if errores <= 3:
                            print(f"   ❌ Error: {result.get('error', {}).get('message', 'desconocido')}")
                    else:
                        enviados += 1
                        if enviados % 50 == 0:
                            print(f"   📍 {enviados}/{len(rows)} enviados")
                else:
                    errores += 1
            else:
                errores += 1
                if errores <= 3:
                    print(f"   ❌ HTTP {response.status_code}")
        except Exception as e:
            errores += 1
            if errores <= 3:
                print(f"   ❌ Excepción: {e}")
    
    print(f"   ✅ {nombre_tabla}: {enviados} enviados, {errores} errores")
    return enviados

# ============================================================
# 5. EJECUTAR SINCRONIZACIÓN
# ============================================================
print("\n📁 3. SINCRONIZANDO...")

tablas = ['clientes', 'productos', 'preventistas', 'categorias', 'lotes', 'usuarios']

total = 0
for tabla in tablas:
    total += enviar_tabla(tabla)

# ============================================================
# 6. VERIFICAR
# ============================================================
print("\n📁 4. VERIFICANDO EN TURSO...")

for tabla in tablas:
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": f"SELECT COUNT(*) as total FROM {tabla}"
                }
            }
        ]
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                if result.get('type') == 'ok':
                    rows = result.get('response', {}).get('result', {}).get('rows', [])
                    if rows:
                        total_reg = rows[0][0] if rows[0] else 0
                        print(f"   📄 {tabla}: {total_reg} registros")
                    else:
                        print(f"   📄 {tabla}: 0 registros")
                else:
                    print(f"   ❌ {tabla}: {result}")
            else:
                print(f"   ❌ {tabla}: sin respuesta")
        else:
            print(f"   ❌ {tabla}: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ {tabla}: {e}")

print("\n" + "=" * 60)
print("✅ SINCRONIZACIÓN COMPLETADA")
print("=" * 60)

conn.close()
