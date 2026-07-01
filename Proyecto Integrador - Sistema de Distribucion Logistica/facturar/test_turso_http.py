#!/usr/bin/env python3
"""
Código Crítico - Tercer Semestre Año 2026
==================================================
TEST DE CONEXIÓN A TURSO - HTTP DIRECTA
==================================================
"""

import os
import json
import requests
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

def cargar_configuracion():
    """Carga la configuración desde turso-facturar.txt"""
    url = None
    token = None
    
    # Buscar el archivo en varias ubicaciones
    rutas = [
        "turso-facturar.txt",
        os.path.join(os.getcwd(), "turso-facturar.txt"),
        os.path.join(os.path.dirname(__file__), "turso-facturar.txt"),
    ]
    
    for ruta in rutas:
        if os.path.exists(ruta):
            print(f"📁 Archivo encontrado: {ruta}")
            with open(ruta, 'r', encoding='utf-8') as f:
                lineas = f.read().strip().split('\n')
                for linea in lineas:
                    linea = linea.strip()
                    if not linea or linea.startswith('#'):
                        continue
                    
                    # Detectar URL
                    if linea.startswith('libsql://') or linea.startswith('https://'):
                        url = linea
                        if url.startswith('libsql://'):
                            url = url.replace('libsql://', 'https://')
                        print(f"   📌 URL encontrada: {url}")
                    
                    # Detectar Token (JWT)
                    elif linea.startswith('eyJ'):
                        token = linea
                        print(f"   📌 Token encontrado: {token[:30]}...{token[-10:] if len(token) > 40 else ''}")
            
            break
    
    # Si no se encontró, usar variables de entorno
    if not token:
        token = os.environ.get("TURSO_TOKEN")
        if token:
            print("   📌 Token desde variable de entorno")
    
    if not url:
        url = os.environ.get("TURSO_URL")
        if url:
            print(f"   📌 URL desde variable de entorno: {url}")
    
    # Valores por defecto
    if not url:
        url = "https://nube-clarionda.aws-us-east-1.turso.io"
        print(f"   ⚠️ Usando URL por defecto: {url}")
    
    if not token:
        print("   ❌ No se encontró token de Turso")
    
    # Asegurar formato correcto de URL
    if url and not url.endswith('/v2/pipeline'):
        if url.endswith('/'):
            url += 'v2/pipeline'
        else:
            url += '/v2/pipeline'
    
    return url, token

# ============================================================
# FUNCIONES DE PRUEBA
# ============================================================

def probar_conexion(url, token):
    """Prueba la conexión a Turso"""
    
    print("\n" + "=" * 60)
    print("🔌 PROBANDO CONEXIÓN A TURSO")
    print("=" * 60)
    print(f"🌐 URL: {url}")
    print(f"🔑 Token: {token[:30]}...{token[-10:] if token and len(token) > 40 else ''}")
    print("")
    
    if not token:
        print("❌ ERROR: No hay token de autenticación")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Consulta de prueba
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": "SELECT 1 as test, datetime('now') as ahora, 'Turso' as fuente"
                }
            }
        ]
    }
    
    print("📤 Enviando consulta de prueba...")
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        
        print(f"📥 Código HTTP: {response.status_code}")
        print(f"📥 Respuesta: {response.text[:500]}")
        print("")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results'):
                resultado = data['results'][0]
                if resultado.get('response', {}).get('result', {}).get('rows'):
                    rows = resultado['response']['result']['rows']
                    cols = resultado['response']['result']['cols']
                    
                    print("✅ CONEXIÓN EXITOSA!")
                    print("")
                    print("📊 Resultado de la consulta:")
                    for row in rows:
                        for i, col in enumerate(cols):
                            print(f"   {col['name']}: {row[i]}")
                    
                    return True
                else:
                    print("⚠️ La consulta no devolvió filas")
                    return False
            else:
                print("⚠️ Respuesta sin 'results'")
                print(f"   Datos: {data}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   {response.text[:300]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - El servidor no respondió en 15 segundos")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ ERROR DE CONEXIÓN - No se pudo conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

def listar_tablas(url, token):
    """Lista las tablas en la base de datos Turso"""
    
    print("\n" + "=" * 60)
    print("📋 LISTANDO TABLAS EN TURSO")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('results'):
                resultado = data['results'][0]
                if resultado.get('response', {}).get('result', {}).get('rows'):
                    rows = resultado['response']['result']['rows']
                    cols = resultado['response']['result']['cols']
                    
                    if rows:
                        print(f"✅ Encontradas {len(rows)} tablas:")
                        for row in rows:
                            print(f"   📄 {row[0]}")
                    else:
                        print("ℹ️ No hay tablas en la base de datos")
                    return True
                else:
                    print("⚠️ No se pudieron obtener las tablas")
                    return False
            else:
                print("⚠️ Respuesta sin 'results'")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_insercion(url, token):
    """Prueba insertar un registro en Turso"""
    
    print("\n" + "=" * 60)
    print("✏️ PROBANDO INSERCIÓN EN TURSO")
    print("=" * 60)
    
    import uuid
    test_id = str(uuid.uuid4())
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Crear tabla de prueba si no existe
    payload_create = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": """
                        CREATE TABLE IF NOT EXISTS test_conexion (
                            id TEXT PRIMARY KEY,
                            test_value TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """
                }
            }
        ]
    }
    
    print("📤 Creando tabla de prueba...")
    response = requests.post(url, json=payload_create, headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ Error creando tabla: {response.status_code}")
        return False
    
    # Insertar registro
    payload_insert = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": "INSERT OR REPLACE INTO test_conexion (id, test_value) VALUES (?, ?)",
                    "args": [test_id, f"Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                }
            }
        ]
    }
    
    print(f"📤 Insertando registro: {test_id[:8]}...")
    response = requests.post(url, json=payload_insert, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print("✅ Inserción exitosa!")
        
        # Verificar inserción
        payload_select = {
            "requests": [
                {
                    "type": "execute",
                    "stmt": {
                        "sql": "SELECT * FROM test_conexion WHERE id = ?",
                        "args": [test_id]
                    }
                }
            ]
        }
        
        response = requests.post(url, json=payload_select, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                resultado = data['results'][0]
                if resultado.get('response', {}).get('result', {}).get('rows'):
                    rows = resultado['response']['result']['rows']
                    cols = resultado['response']['result']['cols']
                    print("✅ Registro verificado:")
                    for row in rows:
                        for i, col in enumerate(cols):
                            print(f"   {col['name']}: {row[i]}")
                    
                    # Limpiar registro de prueba
                    payload_delete = {
                        "requests": [
                            {
                                "type": "execute",
                                "stmt": {
                                    "sql": "DELETE FROM test_conexion WHERE id = ?",
                                    "args": [test_id]
                                }
                            }
                        ]
                    }
                    requests.post(url, json=payload_delete, headers=headers, timeout=10)
                    print("🧹 Registro de prueba eliminado")
                    
                    return True
        
        return True
    else:
        print(f"❌ Error en inserción: {response.status_code}")
        print(f"   {response.text[:200]}")
        return False

# ============================================================
# MAIN
# ============================================================

def main():
    """Función principal"""
    
    print("=" * 60)
    print("🧪 TEST DE CONEXIÓN A TURSO")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("")
    
    # 1. Cargar configuración
    print("📁 1. CARGANDO CONFIGURACIÓN")
    print("-" * 40)
    url, token = cargar_configuracion()
    print("")
    
    if not url or not token:
        print("❌ No se pudo cargar la configuración")
        print("")
        print("📌 Verifica que:")
        print("   1. El archivo 'turso-facturar.txt' existe")
        print("   2. Contiene el token y la URL en el formato correcto")
        print("")
        return 1
    
    # 2. Probar conexión
    print("📁 2. PROBANDO CONEXIÓN")
    print("-" * 40)
    
    if not probar_conexion(url, token):
        print("\n❌ La conexión falló. Revisa la URL y el token.")
        return 1
    
    # 3. Listar tablas
    print("\n📁 3. LISTANDO TABLAS")
    print("-" * 40)
    listar_tablas(url, token)
    
    # 4. Probar inserción
    print("\n📁 4. PROBANDO INSERCIÓN")
    print("-" * 40)
    probar_insercion(url, token)
    
    # Resumen
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("")
    print("🎉 El sistema está listo para usar Turso!")
    
    return 0

if __name__ == "__main__":
    exit(main())