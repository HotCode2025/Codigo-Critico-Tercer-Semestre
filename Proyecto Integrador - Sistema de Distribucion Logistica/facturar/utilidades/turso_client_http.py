"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Cliente Turso vía HTTP DIRECTA (CORREGIDO)
==================================================
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable


class TursoClientHTTP:
    """
    Cliente Turso usando requests HTTP directamente.
    ✅ Maneja el formato de respuesta de Turso (con type/value)
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.url = None
        self.token = None
        self._connected = False
        self._listeners = []
        self._initialized = True
        
        # Estadísticas
        self.stats = {
            'queries_executed': 0,
            'queries_failed': 0,
            'last_error': None,
            'last_sync': None,
            'total_records_sent': 0,
            'total_records_received': 0
        }
        
        self._load_config()
        self._test_connection()
    
    def _load_config(self):
        """Carga configuración desde turso-facturar.txt"""
        posibles_rutas = [
            "turso-facturar.txt",
            os.path.join(os.getcwd(), "turso-facturar.txt"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "turso-facturar.txt"),
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        lines = f.read().strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            if line.startswith('libsql://'):
                                self.url = line.replace('libsql://', 'https://')
                            elif line.startswith('https://'):
                                self.url = line
                            elif line and not line.startswith('#') and line.startswith('eyJ'):
                                self.token = line
                    
                    if self.url and self.token:
                        print(f"✅ Configuración encontrada en: {ruta}")
                        break
                except Exception as e:
                    print(f"⚠️ Error leyendo {ruta}: {e}")
        
        # Variables de entorno como fallback
        if not self.token:
            self.token = os.environ.get("TURSO_TOKEN")
        if not self.url:
            self.url = os.environ.get("TURSO_URL")
        
        # Valores por defecto
        if not self.url:
            self.url = "https://nube-clarionda.aws-us-east-1.turso.io"
        
        # Asegurar que la URL termine correctamente
        if not self.url.endswith('/v2/pipeline'):
            if self.url.endswith('/'):
                self.url += 'v2/pipeline'
            else:
                self.url += '/v2/pipeline'
        
        print(f"📌 URL: {self.url}")
        if self.token:
            print(f"📌 Token: {self.token[:30]}...{self.token[-10:] if len(self.token) > 40 else ''}")
        else:
            print("⚠️ No se encontró token de Turso")
    
    def _test_connection(self) -> bool:
        """Prueba la conexión con Turso."""
        try:
            print("🔄 Probando conexión a Turso...")
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "requests": [
                    {"type": "execute", "stmt": {"sql": "SELECT 1 as test"}}
                ]
            }
            
            response = requests.post(self.url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    self._connected = True
                    print("✅ Conexión a Turso establecida correctamente")
                    self._notify_listeners('connected', {'status': 'success'})
                    return True
            
            print(f"❌ Error en conexión: {response.status_code}")
            self._connected = False
            return False
            
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        return self._connected
    
    def _parse_value(self, value):
        """Parsea un valor de Turso (puede ser dict con type/value o valor directo)"""
        if isinstance(value, dict):
            # Formato de Turso: {"type": "text", "value": "algo"}
            return value.get('value')
        return value
    
    def _execute_raw(self, query: str, params: List = None) -> Optional[Dict]:
        """Ejecuta una consulta SQL via HTTP."""
        if not self._connected:
            print("⚠️ Sin conexión a Turso")
            return None
        
        try:
            self.stats['queries_executed'] += 1
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {
                            "sql": query,
                            "args": params or []
                        }
                    }
                ]
            }
            
            response = requests.post(self.url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return data['results'][0]
                return None
            
            self.stats['queries_failed'] += 1
            self.stats['last_error'] = f"HTTP {response.status_code}"
            print(f"❌ HTTP Error {response.status_code}")
            return None
            
        except Exception as e:
            self.stats['queries_failed'] += 1
            self.stats['last_error'] = str(e)
            print(f"❌ Error en query: {e}")
            return None
    
    def get_one(self, query: str, params: List = None) -> Optional[Dict[str, Any]]:
        """Obtiene una sola fila como diccionario."""
        result = self._execute_raw(query, params)
        if result:
            response = result.get('response', {})
            result_data = response.get('result', {})
            rows = result_data.get('rows', [])
            cols = result_data.get('cols', [])
            
            if rows and cols:
                row = rows[0]
                parsed = {}
                for i, col in enumerate(cols):
                    col_name = col.get('name', f'col_{i}')
                    raw_value = row[i] if i < len(row) else None
                    parsed[col_name] = self._parse_value(raw_value)
                return parsed
        return None
    
    def get_all(self, query: str, params: List = None) -> List[Dict[str, Any]]:
        """Obtiene todas las filas como lista de diccionarios."""
        result = self._execute_raw(query, params)
        if result:
            response = result.get('response', {})
            result_data = response.get('result', {})
            rows = result_data.get('rows', [])
            cols = result_data.get('cols', [])
            
            if rows and cols:
                parsed_rows = []
                for row in rows:
                    parsed = {}
                    for i, col in enumerate(cols):
                        col_name = col.get('name', f'col_{i}')
                        raw_value = row[i] if i < len(row) else None
                        parsed[col_name] = self._parse_value(raw_value)
                    parsed_rows.append(parsed)
                return parsed_rows
        return []
    
    def execute(self, query: str, params: List = None) -> bool:
        """Ejecuta una consulta (INSERT, UPDATE, DELETE)."""
        result = self._execute_raw(query, params)
        return result is not None
    
    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Inserta o reemplaza un registro."""
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_str = ", ".join(columns)
        query = f"INSERT OR REPLACE INTO {table} ({column_str}) VALUES ({placeholders})"
        
        # Convertir valores a tipos simples
        values = []
        for v in data.values():
            if isinstance(v, (dict, list)):
                values.append(json.dumps(v))
            else:
                values.append(v)
        
        success = self.execute(query, values)
        if success:
            self.stats['total_records_sent'] += 1
        return success
    
    def update(self, table: str, data: Dict[str, Any], 
               where: str, where_params: List) -> bool:
        """Actualiza registros."""
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(data.values()) + where_params
        return self.execute(query, params)
    
    def delete(self, table: str, where: str, where_params: List) -> bool:
        """Elimina registros."""
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute(query, where_params)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cliente."""
        return {**self.stats, 'connected': self._connected, 'url': self.url}
    
    def close(self):
        """Cierra la conexión."""
        self._connected = False
        print("👋 Conexión a Turso cerrada")
    
    def add_listener(self, callback: Callable):
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remove_listener(self, callback: Callable):
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, event: str, data: Any = None):
        for listener in self._listeners:
            try:
                listener(event, data)
            except Exception as e:
                print(f"⚠️ Error en listener: {e}")


# ============================================================
# SINGLETON
# ============================================================

_turso_client = None

def get_turso_client() -> TursoClientHTTP:
    """Obtiene la instancia única del cliente Turso."""
    global _turso_client
    if _turso_client is None:
        _turso_client = TursoClientHTTP()
    return _turso_client


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DEL CLIENTE TURSO (HTTP CORREGIDO)")
    print("=" * 60)
    
    client = get_turso_client()
    
    print(f"\n📊 Estado:")
    print(f"  - Conectado: {client.is_connected()}")
    print(f"  - URL: {client.url}")
    
    if client.is_connected():
        # Probar consulta
        result = client.get_one("SELECT 1 as test, datetime('now') as ahora")
        print(f"\n✅ Test de consulta: {result}")
        
        # Listar tablas
        tables = client.get_all("SELECT name FROM sqlite_master WHERE type='table'")
        print(f"\n📋 Tablas en Turso: {len(tables)}")
        for t in tables:
            print(f"  - {t.get('name', t)}")
            
        # Probar inserción
        import uuid
        test_id = str(uuid.uuid4())
        print(f"\n✏️ Probando inserción...")
        
        # Crear tabla de prueba
        client.execute("""
            CREATE TABLE IF NOT EXISTS test_conexion (
                id TEXT PRIMARY KEY,
                test_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar
        if client.insert('test_conexion', {'id': test_id, 'test_value': 'OK'}):
            print(f"   ✅ Inserción exitosa: {test_id[:8]}...")
            
            # Verificar
            record = client.get_one("SELECT * FROM test_conexion WHERE id = ?", [test_id])
            print(f"   📊 Registro verificado: {record}")
            
            # Limpiar
            client.delete('test_conexion', 'id = ?', [test_id])
            print("   🧹 Registro eliminado")
    else:
        print("\n⚠️ No hay conexión a Turso.")
    
    print("\n" + "=" * 60)