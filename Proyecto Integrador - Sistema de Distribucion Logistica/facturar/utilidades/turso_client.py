"""
Código Crítico - Tercer Semestre Año 2026
Cliente Turso vía HTTP - VERSIÓN CORREGIDA CON VERIFICACIÓN REAL
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable


class TursoClient:
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
        posibles_rutas = [
            "turso-facturar.txt",
            os.path.join(os.getcwd(), "turso-facturar.txt"),
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
        
        if not self.token:
            self.token = os.environ.get("TURSO_TOKEN")
        if not self.url:
            self.url = os.environ.get("TURSO_URL")
        
        if not self.url:
            self.url = "https://nube-clarionda.aws-us-east-1.turso.io"
        
        if not self.url.endswith('/v2/pipeline'):
            if self.url.endswith('/'):
                self.url += 'v2/pipeline'
            else:
                self.url += '/v2/pipeline'
        
        print(f"📌 URL: {self.url}")
        if self.token:
            print(f"📌 Token: {self.token[:30]}...")
        else:
            print("⚠️ No se encontró token de Turso")
    
    def _test_connection(self) -> bool:
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
        if isinstance(value, dict):
            return value.get('value')
        return value
    
    def _format_arg(self, value):
        """✅ TODOS los valores se convierten a strings"""
        if value is None:
            return {"type": "null", "value": None}
        elif isinstance(value, bool):
            return {"type": "text", "value": "1" if value else "0"}
        elif isinstance(value, (int, float)):
            return {"type": "text", "value": str(value)}
        elif isinstance(value, (list, dict)):
            return {"type": "text", "value": json.dumps(value)}
        else:
            return {"type": "text", "value": str(value)}
    
    def _execute_raw(self, query: str, params: List = None) -> Optional[Dict]:
        """
        ✅ CORREGIDO: Retorna el resultado completo para verificar errores
        """
        if not self._connected:
            print("⚠️ Sin conexión a Turso")
            return None
        
        try:
            self.stats['queries_executed'] += 1
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            formatted_params = None
            if params:
                formatted_params = [self._format_arg(p) for p in params]
            
            payload = {
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {
                            "sql": query,
                            "args": formatted_params or []
                        }
                    }
                ]
            }
            
            response = requests.post(self.url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return data['results'][0]
                print(f"⚠️ Respuesta sin 'results': {data}")
                return None
            
            self.stats['queries_failed'] += 1
            self.stats['last_error'] = f"HTTP {response.status_code}: {response.text[:200]}"
            print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
            return None
            
        except Exception as e:
            self.stats['queries_failed'] += 1
            self.stats['last_error'] = str(e)
            print(f"❌ Error en query: {e}")
            return None
    
    def execute(self, query: str, params: List = None) -> bool:
        """
        ✅ CORREGIDO: Verifica REALMENTE si la consulta fue exitosa
        """
        result = self._execute_raw(query, params)
        if result is None:
            return False
        
        # ✅ VERIFICAR SI HUBO ERROR EN LA RESPUESTA
        response = result.get('response', {})
        result_data = response.get('result', {})
        
        # Si hay error en la respuesta
        error = result_data.get('error')
        if error:
            print(f"❌ Error en Turso: {error}")
            return False
        
        # Si hay affected_row_count, verificar que sea > 0
        affected = result_data.get('affected_row_count')
        if affected is not None:
            if affected > 0:
                return True
            else:
                print(f"⚠️ No se afectaron filas (affected_row_count=0)")
                return False
        
        # Si hay rows, verificar que haya al menos una
        rows = result_data.get('rows')
        if rows is not None:
            return len(rows) > 0
        
        # Si no hay error y no hay affected_row_count, asumir éxito
        return True
    
    def get_one(self, query: str, params: List = None) -> Optional[Dict[str, Any]]:
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
    
    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_str = ", ".join(columns)
        query = f"INSERT OR REPLACE INTO {table} ({column_str}) VALUES ({placeholders})"
        
        values = []
        for v in data.values():
            if v is None:
                values.append(None)
            elif isinstance(v, (dict, list)):
                values.append(json.dumps(v))
            else:
                values.append(v)
        
        success = self.execute(query, values)
        if success:
            self.stats['total_records_sent'] += 1
            return True
        
        print(f"❌ Falló inserción en {table}: {data.get('id', 'sin id')[:8]}")
        return False
    
    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        if not data_list:
            return 0
        
        success = 0
        for data in data_list:
            if self.insert(table, data):
                success += 1
        return success
    
    def update(self, table: str, data: Dict[str, Any], 
               where: str, where_params: List) -> bool:
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(data.values()) + where_params
        return self.execute(query, params)
    
    def delete(self, table: str, where: str, where_params: List) -> bool:
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute(query, where_params)
    
    def get_stats(self) -> Dict[str, Any]:
        return {**self.stats, 'connected': self._connected, 'url': self.url}
    
    def close(self):
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


_turso_client = None

def get_turso_client() -> TursoClient:
    global _turso_client
    if _turso_client is None:
        _turso_client = TursoClient()
    return _turso_client


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DEL CLIENTE TURSO")
    print("=" * 60)
    
    client = get_turso_client()
    print(f"\n📊 Conectado: {client.is_connected()}")
    
    if client.is_connected():
        import uuid
        test_id = str(uuid.uuid4())
        print(f"\n✏️ Probando inserción...")
        
        result = client.insert('clientes', {'id': test_id, 'razon_social': 'Test', 'cuit': '20-12345678-9'})
        print(f"   ✅ Insert resultado: {result}")
        
        record = client.get_one('SELECT * FROM clientes WHERE id = ?', [test_id])
        print(f"   📊 Registro: {record}")
        
        if record:
            client.delete('clientes', 'id = ?', [test_id])
            print("   🧹 Registro eliminado")
    else:
        print("\n⚠️ No hay conexión a Turso.")
    
    print("\n" + "=" * 60)
