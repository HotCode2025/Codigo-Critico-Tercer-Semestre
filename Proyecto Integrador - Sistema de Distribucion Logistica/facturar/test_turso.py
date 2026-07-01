"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Cliente Oficial de Turso - VERSIÓN SÍNCRONA (SIN ASYNCIO)
==================================================
"""

import os
import json
import time
import threading
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

# ✅ Intentar importar libsql_client
try:
    from libsql_client import create_client, Client
except ImportError:
    try:
        # Versión alternativa
        from libsql_client import Client
        def create_client(url, auth_token=None):
            return Client(url, auth_token=auth_token)
    except ImportError:
        print("❌ No se pudo importar libsql_client. Instalar con: pip install libsql-client")
        raise


# ============================================================
# CONFIGURACIÓN
# ============================================================

@dataclass
class TursoConfig:
    """Configuración de conexión a Turso"""
    url: str
    token: str
    max_retries: int = 5
    timeout: int = 30
    
    @classmethod
    def from_file(cls, filepath: str = "turso-facturar.txt") -> "TursoConfig":
        """Lee la configuración desde el archivo."""
        url = None
        token = None
        
        # Buscar en varias ubicaciones
        posibles_rutas = [
            filepath,
            os.path.join(os.path.dirname(os.path.dirname(__file__)), filepath),
            os.path.join(os.getcwd(), filepath),
            os.path.join(os.path.dirname(__file__), "..", filepath),
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        lines = f.read().strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            
                            if line.startswith('libsql://') or line.startswith('https://'):
                                if line.startswith('libsql://'):
                                    # Convertir libsql:// a https://
                                    url = line.replace('libsql://', 'https://')
                                else:
                                    url = line
                                
                                # Asegurar que termina con /v2/pipeline
                                if not url.endswith('/v2/pipeline'):
                                    if url.endswith('/'):
                                        url += 'v2/pipeline'
                                    else:
                                        url += '/v2/pipeline'
                            
                            elif line and not line.startswith('#') and line.startswith('eyJ'):
                                token = line
                    
                    if url and token:
                        print(f"✅ Configuración encontrada en: {ruta}")
                        break
                except Exception as e:
                    print(f"⚠️ Error leyendo {ruta}: {e}")
        
        # Variables de entorno
        if not token:
            token = os.environ.get("TURSO_TOKEN")
        if not url:
            url = os.environ.get("TURSO_URL")
        
        # Valores por defecto
        if not url:
            url = "https://nube-clarionda.aws-us-east-1.turso.io/v2/pipeline"
        if not token:
            token = ""
        
        print(f"📌 URL configurada: {url}")
        if token:
            print(f"📌 Token: {token[:30]}...{token[-10:] if len(token) > 40 else ''}")
        else:
            print("⚠️ No se encontró token de Turso")
        
        return cls(url=url, token=token)


# ============================================================
# CLIENTE TURSO SÍNCRONO (SINGLETON)
# ============================================================

class TursoClient:
    """
    ✅ Cliente oficial de Turso con conexiones síncronas.
    ✅ Implementa el patrón Singleton.
    ✅ Maneja reconexiones automáticas.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[TursoConfig] = None):
        """Inicializa el cliente de Turso (síncrono)"""
        if hasattr(self, '_initialized'):
            return
        
        self.config = config or TursoConfig.from_file()
        self._client: Optional[Client] = None
        self._connected = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 3
        self._listeners: List[Callable] = []
        self._initialized = True
        
        # Estadísticas
        self.stats = {
            'queries_executed': 0,
            'queries_failed': 0,
            'last_error': None,
            'last_sync': None,
            'total_reconnects': 0,
            'total_records_sent': 0,
            'total_records_received': 0
        }
        
        # Conectar de forma síncrona
        self._connect()
    
    # ============================================================
    # CONEXIÓN (SIN ASYNCIO)
    # ============================================================
    
    def _connect(self) -> bool:
        """
        ✅ Establece conexión con Turso (síncrono).
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            print("🔄 Conectando a Turso...")
            
            # ✅ Crear cliente síncrono directamente
            self._client = create_client(
                url=self.config.url,
                auth_token=self.config.token
            )
            
            # ✅ Verificar conexión con una consulta simple (síncrona)
            result = self._client.execute("SELECT 1 as test")
            
            if result and len(result.rows) > 0:
                self._connected = True
                self._reconnect_attempts = 0
                print("✅ Conexión a Turso establecida correctamente")
                self._notify_listeners('connected', {'status': 'success'})
                return True
            else:
                self._connected = False
                print("⚠️ Conexión a Turso: respuesta vacía")
                return False
                
        except Exception as e:
            self._connected = False
            self.stats['last_error'] = str(e)
            print(f"❌ Error conectando a Turso: {e}")
            self._notify_listeners('error', {'error': str(e)})
            return False
    
    def reconnect(self) -> bool:
        """✅ Reconecta a Turso con backoff exponencial."""
        self.stats['total_reconnects'] += 1
        
        for attempt in range(self._max_reconnect_attempts):
            print(f"⏳ Reintentando conexión (intento {attempt + 1}/{self._max_reconnect_attempts})...")
            
            if self._connect():
                self._reconnect_attempts = 0
                return True
            
            wait_time = 2 ** attempt
            self._reconnect_attempts = attempt + 1
            print(f"⏳ Esperando {wait_time}s antes de reintentar...")
            time.sleep(wait_time)
        
        return False
    
    def is_connected(self) -> bool:
        """✅ Indica si hay conexión activa con Turso"""
        return self._connected
    
    # ============================================================
    # CONSULTAS (SÍNCRONAS)
    # ============================================================
    
    def execute(self, query: str, params: List = None) -> Optional[Any]:
        """
        ✅ Ejecuta una consulta SQL en Turso (síncrono).
        
        Args:
            query: Consulta SQL (con ? como placeholders)
            params: Lista de parámetros
        
        Returns:
            ResultSet o None si falla
        """
        if not self._connected:
            print("⚠️ Sin conexión a Turso, intentando reconectar...")
            if not self.reconnect():
                return None
        
        try:
            self.stats['queries_executed'] += 1
            result = self._client.execute(query, params or [])
            return result
            
        except Exception as e:
            self.stats['queries_failed'] += 1
            self.stats['last_error'] = str(e)
            print(f"❌ Error ejecutando query: {e}")
            
            # Si es error de conexión, reintentar
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                if self.reconnect():
                    try:
                        return self._client.execute(query, params or [])
                    except Exception as e2:
                        print(f"❌ Error en reintento: {e2}")
                        return None
            return None
    
    def get_one(self, query: str, params: List = None) -> Optional[Dict[str, Any]]:
        """✅ Obtiene una sola fila como diccionario."""
        result = self.execute(query, params)
        if result and len(result.rows) > 0:
            try:
                columns = [col.name for col in result.columns]
            except:
                # Fallback si no se pueden obtener los nombres de columna
                row = result.rows[0]
                return {f"col_{i}": row[i] for i in range(len(row))}
            
            row = result.rows[0]
            return {col: row[idx] for idx, col in enumerate(columns)}
        return None
    
    def get_all(self, query: str, params: List = None) -> List[Dict[str, Any]]:
        """✅ Obtiene todas las filas como lista de diccionarios."""
        result = self.execute(query, params)
        if result and len(result.rows) > 0:
            try:
                columns = [col.name for col in result.columns]
                return [{col: row[idx] for idx, col in enumerate(columns)} for row in result.rows]
            except:
                return [{f"col_{i}": row[i] for i in range(len(row))} for row in result.rows]
        return []
    
    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """✅ Inserta o reemplaza un registro en una tabla."""
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_str = ", ".join(columns)
        query = f"INSERT OR REPLACE INTO {table} ({column_str}) VALUES ({placeholders})"
        
        result = self.execute(query, list(data.values()))
        if result is not None:
            self.stats['total_records_sent'] += 1
            return True
        return False
    
    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """✅ Inserta múltiples registros en una tabla."""
        if not data_list:
            return 0
        
        columns = list(data_list[0].keys())
        column_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        query = f"INSERT OR REPLACE INTO {table} ({column_str}) VALUES ({placeholders})"
        
        success = 0
        for data in data_list:
            if self.execute(query, list(data.values())) is not None:
                success += 1
                self.stats['total_records_sent'] += 1
        
        return success
    
    def update(self, table: str, data: Dict[str, Any], 
               where: str, where_params: List) -> bool:
        """✅ Actualiza registros en una tabla."""
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(data.values()) + where_params
        
        result = self.execute(query, params)
        return result is not None
    
    def delete(self, table: str, where: str, where_params: List) -> bool:
        """✅ Elimina registros de una tabla."""
        query = f"DELETE FROM {table} WHERE {where}"
        result = self.execute(query, where_params)
        return result is not None
    
    # ============================================================
    # EVENTOS Y LISTENERS
    # ============================================================
    
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
    # ESTADÍSTICAS
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """✅ Obtiene estadísticas del cliente."""
        return {
            'connected': self._connected,
            'reconnect_attempts': self._reconnect_attempts,
            **self.stats
        }
    
    # ============================================================
    # CIERRE
    # ============================================================
    
    def close(self):
        """✅ Cierra la conexión con Turso."""
        if self._client:
            try:
                self._client.close()
            except:
                pass
        self._connected = False
        print("👋 Conexión a Turso cerrada")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================
# SINGLETON GLOBAL
# ============================================================

_turso_client = None

def get_turso_client() -> TursoClient:
    """✅ Obtiene la instancia única del cliente Turso."""
    global _turso_client
    if _turso_client is None:
        _turso_client = TursoClient()
    return _turso_client


# ============================================================
# PRUEBA RÁPIDA
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DEL CLIENTE TURSO (SÍNCRONO)")
    print("=" * 60)
    
    client = get_turso_client()
    
    print(f"\n📊 Estado:")
    print(f"  - Conectado: {client.is_connected()}")
    print(f"  - Estadísticas: {client.get_stats()}")
    
    if client.is_connected():
        # Probar consulta
        result = client.get_one("SELECT 1 as test, datetime('now') as now")
        print(f"\n✅ Test de consulta: {result}")
        
        # Listar tablas
        tables = client.get_all("SELECT name FROM sqlite_master WHERE type='table'")
        print(f"\n📋 Tablas en Turso: {len(tables)}")
        for t in tables[:10]:
            print(f"  - {t.get('name', t)}")
    else:
        print("\n⚠️ No hay conexión a Turso. Verifica el token y la URL.")
    
    print("\n" + "=" * 60)