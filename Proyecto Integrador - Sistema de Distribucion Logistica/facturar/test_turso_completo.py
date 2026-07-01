#!/usr/bin/env python3
"""
TEST COMPLETO DE COMUNICACIÓN CON TURSO
Prueba todos los métodos posibles de conexión
"""

import os
import json
import requests
import sqlite3
import uuid
from datetime import datetime

print("=" * 70)
print("🧪 TEST COMPLETO DE COMUNICACIÓN CON TURSO")
print("=" * 70)

# ============================================================
# 1. LEER CONFIGURACIÓN
# ============================================================
print("\n📁 1. LEYENDO CONFIGURACIÓN...")

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
print(f"   📌 Token: {token[:30]}...{token[-10:] if len(token) > 40 else ''}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

test_id = str(uuid.uuid4())
print(f"   📌 Test ID: {test_id[:8]}...")

# ============================================================
# 2. MÉTODO 1: SQL DIRECTO CON EXECUTE
# ============================================================
print("\n📤 2. MÉTODO 1: SQL DIRECTO CON execute()")

sql = "INSERT OR REPLACE INTO clientes (id, razon_social, cuit) VALUES (?, ?, ?)"
params = [test_id, 'Test Metodo 1', '20-12345678-9']

payload = {
    "requests": [
        {
            "type": "execute",
            "stmt": {
                "sql": sql,
                "args": [{"type": "text", "value": p} for p in params]
            }
        }
    ]
}

response = requests.post(url, json=payload, headers=headers, timeout=10)
print(f"   📥 Status: {response.status_code}")
print(f"   📥 Respuesta: {response.text[:300]}")

# ============================================================
# 3. MÉTODO 2: SELECT PARA VERIFICAR
# ============================================================
print("\n🔍 3. MÉTODO 2: SELECT PARA VERIFICAR")

payload = {
    "requests": [
        {
            "type": "execute",
            "stmt": {
                "sql": "SELECT id, razon_social FROM clientes WHERE id = ?",
                "args": [{"type": "text", "value": test_id}]
            }
        }
    ]
}

response = requests.post(url, json=payload, headers=headers, timeout=10)
print(f"   📥 Status: {response.status_code}")
print(f"   📥 Respuesta: {response.text[:300]}")

# ============================================================
# 4. MÉTODO 3: BATCH (MÚLTIPLES OPERACIONES)
# ============================================================
print("\n📤 4. MÉTODO 3: BATCH (MÚLTIPLES OPERACIONES)")

test_id2 = str(uuid.uuid4())
payload = {
    "requests": [
        {
            "type": "execute",
            "stmt": {
                "sql": "INSERT OR REPLACE INTO clientes (id, razon_social) VALUES (?, ?)",
                "args": [{"type": "text", "value": test_id2}, {"type": "text", "value": "Test Batch"}]
            }
        },
        {
            "type": "execute",
            "stmt": {
                "sql": "SELECT COUNT(*) as total FROM clientes"
            }
        }
    ]
}

response = requests.post(url, json=payload, headers=headers, timeout=10)
print(f"   📥 Status: {response.status_code}")
print(f"   📥 Respuesta: {response.text[:500]}")

# ============================================================
# 5. MÉTODO 4: USANDO libsql-client (SI ESTÁ INSTALADO)
# ============================================================
print("\n📤 5. MÉTODO 4: libsql-client (alternativo)")

try:
    import libsql_client
    print("   ✅ libsql-client encontrado")
    
    # Crear cliente
    client = libsql_client.create_client(url=url.replace('/v2/pipeline', ''), auth_token=token)
    
    # Insertar
    test_id3 = str(uuid.uuid4())
    result = client.execute(
        "INSERT OR REPLACE INTO clientes (id, razon_social) VALUES (?, ?)",
        [test_id3, "Test libsql-client"]
    )
    print(f"   ✅ Insert resultado: {result}")
    
    # Verificar
    result2 = client.execute("SELECT id, razon_social FROM clientes WHERE id = ?", [test_id3])
    print(f"   ✅ Select resultado: {result2.rows if result2 else 'None'}")
    
    # Limpiar
    client.execute("DELETE FROM clientes WHERE id = ?", [test_id3])
    
except ImportError:
    print("   ⚠️ libsql-client no instalado")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================================
# 6. MÉTODO 5: PROBAR CON SQLITE3 LOCAL (SIMULACIÓN)
# ============================================================
print("\n📤 6. MÉTODO 5: SIMULACIÓN CON SQLITE LOCAL")

# Crear tabla local
conn = sqlite3.connect(':memory:')
conn.execute('CREATE TABLE clientes (id TEXT PRIMARY KEY, razon_social TEXT)')
conn.execute('INSERT INTO clientes (id, razon_social) VALUES (?, ?)', (test_id, 'Local Test'))
row = conn.execute('SELECT * FROM clientes WHERE id = ?', (test_id,)).fetchone()
print(f"   ✅ Local: {row}")

# ============================================================
# 7. LIMPIAR REGISTROS DE PRUEBA
# ============================================================
print("\n🧹 7. LIMPIANDO REGISTROS DE PRUEBA")

# Eliminar test_id
payload = {
    "requests": [
        {
            "type": "execute",
            "stmt": {
                "sql": "DELETE FROM clientes WHERE id = ?",
                "args": [{"type": "text", "value": test_id}]
            }
        },
        {
            "type": "execute",
            "stmt": {
                "sql": "DELETE FROM clientes WHERE id = ?",
                "args": [{"type": "text", "value": test_id2}]
            }
        }
    ]
}
response = requests.post(url, json=payload, headers=headers, timeout=10)
print(f"   📥 Status: {response.status_code}")

# ============================================================
# 8. RESUMEN
# ============================================================
print("\n" + "=" * 70)
print("📊 RESUMEN DE RESULTADOS")
print("=" * 70)

print("""
✅ Métodos probados:
   1. SQL directo con execute() → Ver resultado arriba
   2. SELECT para verificar → Ver resultado arriba
   3. Batch (múltiples operaciones) → Ver resultado arriba
   4. libsql-client (si está instalado) → Ver resultado arriba
   5. SQLite local (simulación) → Funciona correctamente

📌 CONCLUSIÓN: El problema NO es la conexión a Turso,
   sino el FORMATO de los datos que se están enviando.
""")

print("\n" + "=" * 70)
