"""
Código Crítico - Tercer Semestre Año 2026
central_sync.py – Sincronización Central ↔ Turso.

FLUJO DEFINITIVO:
- Central → Turso: clientes, productos (SIN FOTOS), preventistas, categorias, lotes
- Turso → Central: notas_venta (con detalle por código de producto), clientes nuevos, visitas
"""

import os
import sys
import json
import threading
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

# ============================================================
# CONFIGURACIÓN DE TURSO - LEER DESDE ARCHIVO
# ============================================================

def _leer_token_desde_archivo() -> Optional[str]:
    rutas_posibles = [
        os.path.join(os.path.dirname(__file__), "turso-facturar.txt"),
        os.path.join(os.getcwd(), "turso-facturar.txt"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "turso-facturar.txt"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "turso-facturar.txt"),
    ]
    
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    lineas = contenido.split('\n')
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not linea.startswith('libsql://') and not linea.startswith('http'):
                            if linea.startswith('eyJ'):
                                print(f"Token encontrado en: {ruta}")
                                return linea
            except Exception as e:
                print(f"Error leyendo {ruta}: {e}")
    return None

def _leer_url_desde_archivo() -> Optional[str]:
    rutas_posibles = [
        os.path.join(os.path.dirname(__file__), "turso-facturar.txt"),
        os.path.join(os.getcwd(), "turso-facturar.txt"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "turso-facturar.txt"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "turso-facturar.txt"),
    ]
    
    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read().strip()
                    lineas = contenido.split('\n')
                    for linea in lineas:
                        linea = linea.strip()
                        if linea.startswith('libsql://'):
                            url = linea.replace('libsql://', 'https://')
                            if not url.endswith('/v2/pipeline'):
                                if url.endswith('/'):
                                    url += 'v2/pipeline'
                                else:
                                    url += '/v2/pipeline'
                            print(f"URL encontrada en: {ruta} -> {url}")
                            return url
                        elif linea.startswith('https://'):
                            if not linea.endswith('/v2/pipeline'):
                                if linea.endswith('/'):
                                    linea += 'v2/pipeline'
                                else:
                                    linea += '/v2/pipeline'
                            print(f"URL encontrada en: {ruta} -> {linea}")
                            return linea
            except Exception as e:
                print(f"Error leyendo {ruta}: {e}")
    return None

def _get_turso_config() -> Tuple[Optional[str], Optional[str]]:
    token = os.environ.get("TURSO_TOKEN")
    url = os.environ.get("TURSO_URL")
    if token and url:
        print("Usando configuración desde variables de entorno")
        return token, url
    
    config_paths = [
        os.path.expanduser("~/.distribuidora/turso.conf"),
        "/etc/distribuidora/turso.conf",
        os.path.join(os.getcwd(), ".turso.conf")
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                token = data.get('token')
                url = data.get('url')
                if token and url:
                    print(f"Usando configuración desde {path}")
                    return token, url
            except:
                pass
    
    token = _leer_token_desde_archivo()
    url = _leer_url_desde_archivo()
    
    if token and url:
        print("Usando configuración desde turso-facturar.txt")
        return token, url
    
    print("Usando valores por defecto")
    return DEFAULT_TOKEN, DEFAULT_URL

# ✅ CORREGIDO: Nueva URL (us-east-1)
DEFAULT_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODIzNTEzNzEsImlkIjoiMDE5ZWZjNmEtZWIwMS03NzljLWI0Y2YtNTBiMDg5YmJkNDUzIiwicmlkIjoiYTAxZjc1YWMtNTFmYy00ODZhLTlmN2ItNGJjYjk1NzA4Nzc1In0.0zPGT_YfMvZDQmfsO9rtm3aQC6vuoAY-8eiJGOgssm1fFGi-UlWK31BFJfOWOF119LEncP6s7RKhGGBoMnrLAw"
DEFAULT_URL = "https://distribuidora-clarionda.aws-us-east-1.turso.io/v2/pipeline"  # ✅ CORREGIDO

TURSO_TOKEN, TURSO_PIPELINE_URL = _get_turso_config()

print("\n" + "=" * 60)
print("CONFIGURACION DE TURSO")
print("=" * 60)
if TURSO_TOKEN:
    token_preview = TURSO_TOKEN[:25] + "..." + TURSO_TOKEN[-10:] if len(TURSO_TOKEN) > 35 else TURSO_TOKEN
    print(f"Token: {token_preview}")
else:
    print("No se encontró token de Turso")

if TURSO_PIPELINE_URL:
    print(f"URL: {TURSO_PIPELINE_URL}")
else:
    print("No se encontró URL de Turso")
print("=" * 60 + "\n")

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def _log_sync(mensaje: str, nivel: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{nivel}] {mensaje}\n"
    try:
        log_file = os.path.join(LOG_DIR, f"sync_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error al escribir log: {e}")
    
    if nivel == "ERROR":
        print(f"\033[91m{log_line.strip()}\033[0m")
    elif nivel == "WARNING":
        print(f"\033[93m{log_line.strip()}\033[0m")
    else:
        print(log_line.strip())

def _escape(val):
    if val is None:
        return "NULL"
    if isinstance(val, bytes):
        hex_string = val.hex()
        return "X'" + hex_string + "'"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, dict):
        if 'value' in val:
            return _escape(val['value'])
        return "'" + json.dumps(val).replace("'", "''") + "'"
    return "'" + str(val).replace("'", "''") + "'"

def _pipeline_turso(requests_payload: list, timeout: int = 15) -> dict:
    if not TURSO_TOKEN or not TURSO_PIPELINE_URL:
        return {"error": "No hay configuración de Turso"}
    try:
        body = {"requests": requests_payload}
        response = requests.post(
            TURSO_PIPELINE_URL,
            headers={"Authorization": f"Bearer {TURSO_TOKEN}", "Content-Type": "application/json"},
            json=body,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        _log_sync(f"Error de red al contactar Turso: {e}", "ERROR")
        return {"error": str(e)}

def _ejecutar_en_hilo(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper

def verificar_conexion_turso() -> bool:
    if not TURSO_TOKEN or not TURSO_PIPELINE_URL:
        _log_sync("No hay configuración de Turso", "ERROR")
        return False
    try:
        resultado = consultar_turso("SELECT 1 as test")
        if resultado and len(resultado) > 0:
            _log_sync("Conexión a Turso establecida correctamente", "INFO")
            return True
        else:
            _log_sync("La conexión a Turso devolvió un resultado vacío", "ERROR")
            return False
    except Exception as e:
        _log_sync(f"Error al conectar a Turso: {e}", "ERROR")
        return False

# ============================================================
# COLA DE SINCRONIZACIÓN
# ============================================================

class SyncQueue:
    def __init__(self):
        self._lock = threading.Lock()
        self._crear_tablas()
        self._procesador_activo = False
        self._thread = None
    
    def _get_conn(self):
        from db.db_manager import obtener_conexion
        return obtener_conexion()
    
    def _crear_tablas(self):
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    args TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    retries INTEGER DEFAULT 0,
                    last_error TEXT,
                    next_retry TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_log_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    args TEXT,
                    success BOOLEAN,
                    error TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_next_retry ON sync_queue(next_retry)")
            conn.commit()
        finally:
            conn.close()
    
    def agregar(self, query: str, args: List = None):
        with self._lock:
            conn = self._get_conn()
            try:
                next_retry = datetime.now().isoformat()
                conn.execute("INSERT INTO sync_queue (query, args, next_retry) VALUES (?, ?, ?)",
                             (query, json.dumps(args) if args else None, next_retry))
                conn.commit()
                _log_sync(f"Operación encolada: {query[:80]}...", "WARNING")
            finally:
                conn.close()
    
    def _build_query(self, query: str, args: List) -> str:
        if not args:
            return query
        parts = query.split("?")
        if len(parts) - 1 != len(args):
            return query
        full_query = parts[0]
        for i, val in enumerate(args):
            full_query += _escape(val) + parts[i + 1]
        return full_query
    
    def procesar_pendientes(self, max_retries: int = 3, backoff_seconds: int = 10):
        with self._lock:
            conn = self._get_conn()
            try:
                ahora = datetime.now().isoformat()
                cur = conn.cursor()
                cur.execute("SELECT * FROM sync_queue WHERE next_retry <= ? ORDER BY created_at ASC", (ahora,))
                pendientes = cur.fetchall()
                exitosos = 0
                fallidos = 0
                
                for pend in pendientes:
                    query = pend["query"]
                    args = json.loads(pend["args"]) if pend["args"] else None
                    retries = pend["retries"]
                    full_query = self._build_query(query, args)
                    resultado = _pipeline_turso([
                        {"type": "execute", "stmt": {"sql": full_query}},
                        {"type": "close"}
                    ])
                    ok = resultado and not resultado.get("results", [{}])[0].get("error")
                    
                    if ok:
                        conn.execute("DELETE FROM sync_queue WHERE id = ?", (pend["id"],))
                        conn.execute("INSERT INTO sync_log_history (query, args, success) VALUES (?, ?, 1)",
                                     (query, json.dumps(args) if args else None))
                        exitosos += 1
                        _log_sync(f"Pendiente sincronizado: {query[:80]}...")
                    else:
                        error_msg = resultado.get("results", [{}])[0].get("error", "Error desconocido")
                        nuevo_retries = retries + 1
                        if nuevo_retries >= max_retries:
                            conn.execute("DELETE FROM sync_queue WHERE id = ?", (pend["id"],))
                            conn.execute("INSERT INTO sync_log_history (query, args, success, error) VALUES (?, ?, 0, ?)",
                                         (query, json.dumps(args) if args else None, f"Max retries: {error_msg}"))
                            fallidos += 1
                            _log_sync(f"Falló permanentemente: {query[:80]}...", "ERROR")
                        else:
                            delay = backoff_seconds * (2 ** retries)
                            next_retry = (datetime.now() + timedelta(seconds=delay)).isoformat()
                            conn.execute("UPDATE sync_queue SET retries = ?, last_error = ?, next_retry = ? WHERE id = ?",
                                         (nuevo_retries, str(error_msg), next_retry, pend["id"]))
                            fallidos += 1
                            _log_sync(f"Reintento {nuevo_retries}/{max_retries} en {delay}s", "WARNING")
                
                conn.commit()
                return exitosos, fallidos
            finally:
                conn.close()
    
    def procesar_en_background(self, intervalo: int = 3):
        if self._procesador_activo:
            return
        self._procesador_activo = True
        def _loop():
            while self._procesador_activo:
                try:
                    self.procesar_pendientes()
                except Exception as e:
                    _log_sync(f"Error en procesador de cola: {e}", "ERROR")
                time.sleep(intervalo)
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()
        _log_sync("Procesador de cola iniciado")
    
    def detener(self):
        self._procesador_activo = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def get_estadisticas(self) -> dict:
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as pendientes FROM sync_queue")
            pendientes = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) as total FROM sync_log_history")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) as exitosos FROM sync_log_history WHERE success = 1")
            exitosos = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) as fallidos FROM sync_log_history WHERE success = 0")
            fallidos = cur.fetchone()[0]
            return {'pendientes': pendientes, 'total_historial': total, 'exitosos': exitosos, 'fallidos': fallidos}
        finally:
            conn.close()

_queue = None

def get_queue() -> SyncQueue:
    global _queue
    if _queue is None:
        _queue = SyncQueue()
        _queue.procesar_en_background()
    return _queue

@_ejecutar_en_hilo
def enviar_a_turso(query: str, args: list = None):
    if not TURSO_TOKEN or not TURSO_PIPELINE_URL:
        get_queue().agregar(query, args)
        _log_sync("Sin conexión a Turso. Encolando.", "WARNING")
        return
    try:
        if args:
            parts = query.split("?")
            if len(parts) - 1 != len(args):
                _log_sync(f"Error: número de argumentos no coincide", "ERROR")
                return
            full_query = parts[0]
            for i, val in enumerate(args):
                full_query += _escape(val) + parts[i + 1]
        else:
            full_query = query
        _log_sync(f"Enviando a Turso: {full_query[:100]}...", "DEBUG")
        resultado = _pipeline_turso([
            {"type": "execute", "stmt": {"sql": full_query}},
            {"type": "close"}
        ])
        if resultado and not resultado.get("results", [{}])[0].get("error"):
            _log_sync(f"Replicado a Turso correctamente")
        else:
            error_msg = resultado.get("results", [{}])[0].get("error", "Error desconocido")
            _log_sync(f"Error replicando: {error_msg}. Encolando...", "WARNING")
            get_queue().agregar(query, args)
    except Exception as e:
        _log_sync(f"Excepción al enviar: {e}. Encolando...", "ERROR")
        get_queue().agregar(query, args)

def consultar_turso(query: str, args: list = None) -> list:
    if not TURSO_TOKEN or not TURSO_PIPELINE_URL:
        _log_sync("Sin conexión a Turso para consulta", "WARNING")
        return []
    try:
        if args:
            parts = query.split("?")
            if len(parts) - 1 != len(args):
                _log_sync(f"Error: número de argumentos no coincide", "ERROR")
                return []
            full_query = parts[0]
            for i, val in enumerate(args):
                full_query += _escape(val) + parts[i + 1]
        else:
            full_query = query
        
        _log_sync(f"Ejecutando consulta: {full_query[:100]}...", "DEBUG")
        
        resultado = _pipeline_turso([
            {"type": "execute", "stmt": {"sql": full_query}},
            {"type": "close"}
        ])
        
        if not resultado:
            _log_sync("Error: resultado vacío de _pipeline_turso", "ERROR")
            return []
        
        if "error" in resultado:
            _log_sync(f"Error en pipeline: {resultado['error']}", "ERROR")
            return []
        
        if "results" not in resultado:
            _log_sync("Error: no hay 'results' en la respuesta", "ERROR")
            return []
        
        first = resultado["results"][0]
        if first.get("type") != "ok":
            _log_sync(f"Error en respuesta: tipo {first.get('type')}", "ERROR")
            return []
        
        response = first.get("response", {})
        if response.get("type") != "execute":
            _log_sync(f"Error: tipo de respuesta inesperado: {response.get('type')}", "ERROR")
            return []
        
        result = response.get("result", {})
        if result.get("error"):
            _log_sync(f"Error en consulta: {result.get('error')}", "ERROR")
            return []
        
        cols = [c["name"] for c in result.get("cols", [])]
        rows = result.get("rows", [])
        
        if not cols:
            return []
        
        parsed_rows = []
        for row in rows:
            parsed_row = {}
            for i, col_name in enumerate(cols):
                if i < len(row):
                    val = row[i]
                    if isinstance(val, dict) and "value" in val:
                        parsed_row[col_name] = val["value"]
                    else:
                        parsed_row[col_name] = val
            parsed_rows.append(parsed_row)
        
        _log_sync(f"Consulta exitosa: {len(parsed_rows)} filas", "DEBUG")
        return parsed_rows
        
    except Exception as e:
        _log_sync(f"Error en consultar_turso: {e}", "ERROR")
        import traceback
        _log_sync(traceback.format_exc(), "ERROR")
        return []

# ============================================================
# RECEPCIÓN DE DATOS DESDE TURSO
# ============================================================

def recibir_notas_venta(ultimo_timestamp: str = "1970-01-01T00:00:00") -> list:
    return consultar_turso('''
        SELECT 
            n.id,
            n.numero_nota,
            n.fecha,
            n.total,
            n.observaciones,
            n.preventista_id,
            n.cliente_id,
            n.estado,
            n.procesado_central,
            n.created_at,
            (
                SELECT json_group_array(
                    json_object(
                        'id', nd.id,
                        'codigo_producto', nd.codigo_producto,
                        'cantidad', nd.cantidad,
                        'precio_unitario', nd.precio_unitario
                    )
                )
                FROM nota_venta_detalle nd
                WHERE nd.nota_venta_id = n.id
            ) as detalle
        FROM notas_venta n
        WHERE n.created_at > ? AND n.procesado_central = 0 
        ORDER BY n.created_at ASC
    ''', [ultimo_timestamp])

def recibir_clientes_nuevos(ultimo_timestamp: str = "1970-01-01T00:00:00") -> list:
    return consultar_turso(
        "SELECT * FROM clientes WHERE created_at > ? ORDER BY created_at ASC",
        [ultimo_timestamp]
    )

def recibir_preventistas_nuevos(ultimo_timestamp: str = "1970-01-01T00:00:00") -> list:
    return consultar_turso(
        "SELECT * FROM preventistas WHERE created_at > ? ORDER BY created_at ASC",
        [ultimo_timestamp]
    )

def recibir_visitas(ultimo_timestamp: str = "1970-01-01T00:00:00") -> list:
    return consultar_turso(
        "SELECT * FROM visitas_clientes WHERE created_at > ? ORDER BY created_at ASC",
        [ultimo_timestamp]
    )

# ============================================================
# APLICAR CAMBIOS LOCALES (RECIBIR DESDE TURSO)
# ============================================================

def aplicar_cambios_locales(tabla: str, filas: list):
    if not filas:
        return
    from db.db_manager import obtener_conexion
    import json
    
    conn = obtener_conexion()
    try:
        conn.execute("BEGIN TRANSACTION")
        cur = conn.cursor()
        
        for fila in filas:
            fila_limpia = {}
            detalle_data = None
            nota_id = None
            
            for key, value in fila.items():
                if isinstance(value, dict):
                    if 'value' in value:
                        fila_limpia[key] = value['value']
                    else:
                        fila_limpia[key] = str(value)
                elif key == 'detalle' and value:
                    detalle_data = value
                    continue
                else:
                    fila_limpia[key] = value
            
            if tabla == 'notas_venta':
                nota_id = fila_limpia.get('id')
            
            if tabla == 'nota_venta_detalle' and 'codigo_producto' in fila_limpia:
                codigo = fila_limpia.get('codigo_producto')
                if codigo:
                    cur.execute(
                        "SELECT id FROM productos WHERE codigo_producto = ? AND activo = 1",
                        (codigo,)
                    )
                    prod = cur.fetchone()
                    if prod:
                        fila_limpia['producto_id'] = prod['id']
                    else:
                        fila_limpia['producto_id'] = None
            
            columnas = ", ".join(fila_limpia.keys())
            placeholders = ", ".join(["?" for _ in fila_limpia])
            cur.execute(
                f"INSERT OR REPLACE INTO {tabla} ({columnas}) VALUES ({placeholders})",
                list(fila_limpia.values())
            )
            
            if tabla == 'notas_venta' and detalle_data and nota_id:
                detalle_items = json.loads(detalle_data) if isinstance(detalle_data, str) else detalle_data
                
                for item in detalle_items:
                    codigo = item.get('codigo_producto')
                    if codigo:
                        cur.execute(
                            "SELECT id FROM productos WHERE codigo_producto = ? AND activo = 1",
                            (codigo,)
                        )
                        prod = cur.fetchone()
                        if prod:
                            producto_id = prod['id']
                        else:
                            producto_id = None
                        
                        cur.execute("""
                            INSERT OR REPLACE INTO nota_venta_detalle 
                            (id, nota_venta_id, producto_id, codigo_producto, cantidad, precio_unitario, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item.get('id'),
                            nota_id,
                            producto_id,
                            codigo,
                            item.get('cantidad', 0),
                            item.get('precio_unitario', 0),
                            item.get('created_at', datetime.now().isoformat())
                        ))
        
        conn.commit()
        _log_sync(f"Aplicados {len(filas)} cambios en tabla '{tabla}'")
    except Exception as e:
        conn.rollback()
        _log_sync(f"Error al aplicar cambios en {tabla}: {e}", "ERROR")
        import traceback
        _log_sync(traceback.format_exc(), "ERROR")
        raise
    finally:
        conn.close()

# ============================================================
# SINCRONIZADOR AUTOMÁTICO
# ============================================================

class SincronizadorTurso:
    def __init__(self, intervalo_segundos: int = 3):
        self.intervalo = intervalo_segundos
        self.ejecutando = False
        self.thread = None
        self.ultima_sync = {}
        
        self.tablas_pull = [
            'clientes',
            'preventistas',
            'notas_venta',
            'visitas_clientes'
        ]
    
    def iniciar(self):
        if self.ejecutando:
            return
        self.ejecutando = True
        self.thread = threading.Thread(target=self._bucle_sincronizacion, daemon=True)
        self.thread.start()
        _log_sync(f"Sincronización automática iniciada (intervalo: {self.intervalo}s)")
    
    def detener(self):
        self.ejecutando = False
        _log_sync("Sincronización automática detenida")
    
    def _bucle_sincronizacion(self):
        while self.ejecutando:
            try:
                self._sincronizar_todo()
            except Exception as e:
                _log_sync(f"Error en sincronización: {e}", "ERROR")
            time.sleep(self.intervalo)
    
    def _sincronizar_todo(self):
        for tabla in self.tablas_pull:
            self._sincronizar_tabla(tabla)
    
    def _sincronizar_tabla(self, tabla: str):
        try:
            ultimo = self.ultima_sync.get(tabla, "1970-01-01T00:00:00")
            
            if tabla == 'notas_venta':
                datos = recibir_notas_venta(ultimo)
            elif tabla == 'clientes':
                datos = recibir_clientes_nuevos(ultimo)
            elif tabla == 'preventistas':
                datos = recibir_preventistas_nuevos(ultimo)
            elif tabla == 'visitas_clientes':
                datos = recibir_visitas(ultimo)
            else:
                return
            
            if datos:
                aplicar_cambios_locales(tabla, datos)
                self.ultima_sync[tabla] = datos[-1].get('created_at', datetime.now().isoformat())
                _log_sync(f"Sincronizado {tabla}: {len(datos)} registros nuevos")
                
                if tabla == 'notas_venta':
                    for fila in datos:
                        nota_id = fila.get('id')
                        if nota_id:
                            enviar_a_turso(
                                "UPDATE notas_venta SET procesado_central = 1 WHERE id = ?",
                                [str(nota_id)]
                            )
                    _log_sync(f"{len(datos)} notas marcadas como procesadas", "INFO")
        except Exception as e:
            _log_sync(f"Error sincronizando tabla {tabla}: {e}", "ERROR")
    
    def sincronizar_ahora(self):
        _log_sync("Sincronización manual iniciada")
        self._sincronizar_todo()
        _log_sync("Sincronización manual completada")
    
    def get_estado(self) -> dict:
        return {
            'ejecutando': self.ejecutando,
            'intervalo': self.intervalo,
            'ultima_sync': self.ultima_sync,
            'tablas': self.tablas_pull,
            'cola_estadisticas': get_queue().get_estadisticas() if _queue else {}
        }

_sincronizador_global = None

def get_sincronizador() -> SincronizadorTurso:
    global _sincronizador_global
    if _sincronizador_global is None:
        _sincronizador_global = SincronizadorTurso(intervalo_segundos=3)
    return _sincronizador_global

def iniciar_sincronizacion_auto():
    get_sincronizador().iniciar()

def detener_sincronizacion_auto():
    if _sincronizador_global:
        _sincronizador_global.detener()

def sincronizar_ahora():
    get_sincronizador().sincronizar_ahora()

# ============================================================
# FUNCIONES DE SINCRONIZACIÓN DESDE CENTRAL A TURSO
# ============================================================

def sincronizar_desde_central():
    print("=" * 60)
    print("📤 CENTRAL → TURSO (clientes, productos, preventistas, categorias, lotes)")
    print("=" * 60)
    
    if not verificar_conexion_turso():
        print("❌ No hay conexión con Turso")
        return
    
    from db.db_manager import obtener_conexion
    conn = obtener_conexion()
    cur = conn.cursor()
    
    tablas = [
        ('clientes', 'id'),
        ('preventistas', 'id'),
        ('categorias', 'id'),
        ('lotes', 'id'),
    ]
    
    total_sincronizados = 0
    
    for tabla, id_field in tablas:
        print(f"\n📤 Sincronizando {tabla}...")
        cur.execute(f"SELECT * FROM {tabla}")
        registros = cur.fetchall()
        
        if not registros:
            print(f"   ⚠️ {tabla}: sin registros")
            continue
        
        columnas = [desc[0] for desc in cur.description]
        
        for registro in registros:
            valores = list(registro)
            placeholders = ", ".join(["?" for _ in columnas])
            columnas_str = ", ".join(columnas)
            query = f"INSERT OR REPLACE INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
            enviar_a_turso(query, valores)
            total_sincronizados += 1
        
        print(f"   ✅ {tabla}: {len(registros)} registros enviados")
    
    print(f"\n📤 Sincronizando productos (SIN FOTOS)...")
    cur.execute("""
        SELECT 
            id, codigo_producto, descripcion, precio_costo, precio_venta,
            stock_actual, stock_critico, unidad_medida, categoria_id,
            detalle, precio_oferta, destacado, activo,
            created_at, updated_at, version
        FROM productos 
        WHERE activo = 1
    """)
    productos = cur.fetchall()
    
    if productos:
        columnas = ['id', 'codigo_producto', 'descripcion', 'precio_costo', 'precio_venta',
                    'stock_actual', 'stock_critico', 'unidad_medida', 'categoria_id',
                    'detalle', 'precio_oferta', 'destacado', 'activo',
                    'created_at', 'updated_at', 'version']
        
        for prod in productos:
            valores = list(prod)
            placeholders = ", ".join(["?" for _ in columnas])
            columnas_str = ", ".join(columnas)
            query = f"INSERT OR REPLACE INTO productos ({columnas_str}) VALUES ({placeholders})"
            enviar_a_turso(query, valores)
            total_sincronizados += 1
        
        print(f"   ✅ productos: {len(productos)} registros enviados (SIN FOTOS)")
    else:
        print(f"   ⚠️ productos: sin registros")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL: {total_sincronizados} registros sincronizados")
    print("=" * 60)