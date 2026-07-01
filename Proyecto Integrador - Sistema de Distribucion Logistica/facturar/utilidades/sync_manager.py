"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 4: Gestor de Sincronización con Turso
==================================================
📌 USO: Orquesta la sincronización entre Central y Turso
📌 CARACTERÍSTICAS:
    - Sincronización bidireccional por tabla
    - Control de timestamps (solo datos nuevos)
    - Eventos para notificar progreso
    - Sincronización automática en segundo plano
    - ✅ Conexión SQLite independiente por hilo
"""

import time
import threading
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# ✅ Importar desde sync_utils (evita cíclicos)
from utilidades.sync_utils import (
    log_sync, 
    get_turso_client, 
    SyncDirection, 
    SyncStatus,
    obtener_tablas_sync
)
from utilidades.sync_queue import get_sync_queue


class SyncManager:
    """
    Gestor de sincronización con Turso.
    """
    
    def __init__(self, sync_interval: int = 3):
        self._client = None
        self.sync_interval = sync_interval
        self._running = False
        self._thread = None
        self._listeners: List[Callable] = []
        
        self.tables: Dict[str, Dict] = {}
        self.sync_queue = get_sync_queue()
        
        self.stats = {
            'syncs_completed': 0,
            'syncs_failed': 0,
            'records_sent': 0,
            'records_received': 0,
            'last_sync': None,
            'last_sync_status': None
        }
        
        self._setup_default_tables()
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_turso_client()
        return self._client
    
    def _setup_default_tables(self):
        tablas_config = obtener_tablas_sync()
        
        for table_name, config in tablas_config.items():
            self.register_table(
                name=table_name,
                direction=config['direction'],
                id_field=config.get('id_field', 'id'),
                timestamp_field=config.get('timestamp_field', 'updated_at')
            )
            log_sync(f"📋 Tabla registrada: {table_name} ({config['direction'].value})", "INFO")
    
    def register_table(self, name: str, direction: SyncDirection,
                       id_field: str = "id", timestamp_field: str = "created_at",
                       batch_size: int = 100):
        self.tables[name] = {
            'direction': direction,
            'id_field': id_field,
            'timestamp_field': timestamp_field,
            'batch_size': batch_size,
            'last_sync': None,
            'status': SyncStatus.PENDING
        }
    
    def get_last_sync(self, table: str) -> str:
        if table in self.tables:
            last = self.tables[table].get('last_sync')
            return last or "1970-01-01T00:00:00"
        return "1970-01-01T00:00:00"
    
    def update_last_sync(self, table: str, timestamp: str):
        if table in self.tables:
            self.tables[table]['last_sync'] = timestamp
    
    def _get_db_path(self) -> str:
        from db.db_manager import _ruta_base_datos
        return _ruta_base_datos()
    
    # ============================================================
    # SINCRONIZACIÓN DESDE LOCAL A TURSO (CORREGIDA)
    # ============================================================
    
    def sync_from_local(self, table: str, db_connection) -> Dict[str, Any]:
        """
        Sincroniza datos desde la base de datos local a Turso.
        ✅ Usa conexión SQLite independiente por hilo.
        """
        self.tables[table]['status'] = SyncStatus.RUNNING
        
        thread_db = None
        
        try:
            from db.db_manager import _ruta_base_datos
            import sqlite3
            
            db_path = _ruta_base_datos()
            
            # ✅ Crear conexión independiente para este hilo
            thread_db = sqlite3.connect(db_path)
            thread_db.row_factory = sqlite3.Row
            thread_db.execute("PRAGMA foreign_keys = ON")
            
            last_sync = self.get_last_sync(table)
            timestamp_field = self.tables[table]['timestamp_field']
            batch_size = self.tables[table]['batch_size']
            
            cur = thread_db.cursor()
            
            # ✅ VERIFICAR SI LA TABLA EXISTE Y TIENE DATOS
            try:
                cur.execute(f"SELECT COUNT(*) as total FROM {table}")
                total_registros = cur.fetchone()['total']
                print(f"   📊 {table}: {total_registros} registros en total")
            except sqlite3.OperationalError:
                print(f"   ⚠️ {table}: Tabla no existe o no tiene datos")
                self.tables[table]['status'] = SyncStatus.NO_CHANGES
                return {'table': table, 'sent': 0, 'status': 'no_data', 'message': 'Tabla vacía o no existe'}
            
            if total_registros == 0:
                print(f"   ℹ️ {table}: Tabla vacía, omitiendo")
                self.tables[table]['status'] = SyncStatus.NO_CHANGES
                return {'table': table, 'sent': 0, 'status': 'no_data', 'message': 'Tabla vacía'}
            
            # Obtener registros nuevos o modificados
            query = f"""
                SELECT * FROM {table}
                WHERE {timestamp_field} > ?
                ORDER BY {timestamp_field}
                LIMIT ?
            """
            cur.execute(query, (last_sync, batch_size))
            rows = cur.fetchall()
            
            if not rows:
                print(f"   ℹ️ {table}: Sin cambios desde {last_sync}")
                self.tables[table]['status'] = SyncStatus.NO_CHANGES
                return {'table': table, 'sent': 0, 'status': 'no_changes'}
            
            columns = [desc[0] for desc in cur.description]
            
            sent = 0
            for row in rows:
                data = dict(zip(columns, row))
                try:
                    result = self.client.insert(table, data)
                    if result:
                        sent += 1
                        self.stats['records_sent'] += 1
                        print(f"   ✅ {table}: Enviado registro {sent}/{len(rows)}", end='\r')
                except Exception as e:
                    print(f"\n   ⚠️ Error en {table}: {e}")
                    self.sync_queue.agregar(
                        f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})",
                        list(data.values())
                    )
            
            print()
            
            if sent > 0:
                last_row = rows[-1]
                try:
                    timestamp_idx = None
                    for idx, col in enumerate(columns):
                        if col == timestamp_field:
                            timestamp_idx = idx
                            break
                    
                    if timestamp_idx is not None and len(last_row) > timestamp_idx:
                        last_timestamp = str(last_row[timestamp_idx])
                        if last_timestamp:
                            self.update_last_sync(table, last_timestamp)
                            print(f"   📌 {table}: Último timestamp actualizado: {last_timestamp}")
                except Exception as e:
                    print(f"   ⚠️ {table}: No se pudo actualizar timestamp: {e}")
            
            self.stats['syncs_completed'] += 1
            self.tables[table]['status'] = SyncStatus.SUCCESS
            
            return {
                'table': table,
                'sent': sent,
                'total': len(rows),
                'status': 'success',
                'last_sync': self.get_last_sync(table)
            }
            
        except Exception as e:
            self.stats['syncs_failed'] += 1
            self.tables[table]['status'] = SyncStatus.FAILED
            print(f"   ❌ Error sync local→turso ({table}): {e}")
            return {'table': table, 'error': str(e), 'status': 'failed'}
        
        finally:
            if thread_db:
                try:
                    thread_db.close()
                except:
                    pass
    
    # ============================================================
    # SINCRONIZACIÓN DESDE TURSO A LOCAL
    # ============================================================
    
    def sync_from_turso(self, table: str, db_connection) -> Dict[str, Any]:
        """Sincroniza datos desde Turso a la base de datos local."""
        self.tables[table]['status'] = SyncStatus.RUNNING
        
        try:
            last_sync = self.get_last_sync(table)
            timestamp_field = self.tables[table]['timestamp_field']
            batch_size = self.tables[table]['batch_size']
            
            query = f"""
                SELECT * FROM {table}
                WHERE {timestamp_field} > ?
                ORDER BY {timestamp_field}
                LIMIT ?
            """
            rows = self.client.get_all(query, [last_sync, batch_size])
            
            if not rows:
                self.tables[table]['status'] = SyncStatus.NO_CHANGES
                return {'table': table, 'received': 0, 'status': 'no_changes'}
            
            cur = db_connection.cursor()
            received = 0
            
            for row in rows:
                columns = list(row.keys())
                placeholders = ", ".join(["?" for _ in columns])
                column_str = ", ".join(columns)
                query_local = f"INSERT OR REPLACE INTO {table} ({column_str}) VALUES ({placeholders})"
                
                try:
                    cur.execute(query_local, list(row.values()))
                    received += 1
                    self.stats['records_received'] += 1
                except Exception as e:
                    log_sync(f"⚠️ Error insertando en {table}: {e}", "WARNING")
                    continue
            
            db_connection.commit()
            
            if received > 0:
                last_row = rows[-1]
                last_timestamp = last_row.get(timestamp_field)
                if last_timestamp:
                    self.update_last_sync(table, str(last_timestamp))
            
            self.stats['syncs_completed'] += 1
            self.tables[table]['status'] = SyncStatus.SUCCESS
            
            return {
                'table': table,
                'received': received,
                'status': 'success',
                'last_sync': self.get_last_sync(table)
            }
            
        except Exception as e:
            self.stats['syncs_failed'] += 1
            self.tables[table]['status'] = SyncStatus.FAILED
            log_sync(f"❌ Error sync turso→local ({table}): {e}", "ERROR")
            return {'table': table, 'error': str(e), 'status': 'failed'}
    
    # ============================================================
    # SINCRONIZACIÓN COMPLETA
    # ============================================================
    
    def sync_all(self, db_connection) -> Dict[str, Any]:
        results = {}
        
        self.sync_queue.procesar_pendientes()
        
        for table_name, config in self.tables.items():
            direction = config['direction']
            
            if direction == SyncDirection.FROM_LOCAL:
                result = self.sync_from_local(table_name, db_connection)
            elif direction == SyncDirection.FROM_TURSO:
                result = self.sync_from_turso(table_name, db_connection)
            else:
                result = {'error': f'Dirección no soportada: {direction}'}
            
            results[table_name] = result
            self.stats['last_sync'] = datetime.now().isoformat()
            self.stats['last_sync_status'] = 'success'
            
            self._notify_listeners('table_synced', {
                'table': table_name,
                'result': result
            })
        
        self._notify_listeners('sync_completed', results)
        return results
    
    # ============================================================
    # SINCRONIZACIÓN AUTOMÁTICA
    # ============================================================
    
    def start_auto_sync(self, db_connection):
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._auto_sync_loop,
            args=(db_connection,),
            daemon=True
        )
        self._thread.start()
        self._notify_listeners('auto_sync_started', {
            'interval': self.sync_interval
        })
        log_sync(f"🔄 Sincronización automática iniciada (intervalo: {self.sync_interval}s)", "INFO")
    
    def stop_auto_sync(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._notify_listeners('auto_sync_stopped')
        log_sync("⏹️ Sincronización automática detenida", "INFO")
    
    def _auto_sync_loop(self, db_connection):
        while self._running:
            try:
                results = self.sync_all(db_connection)
                self._notify_listeners('sync_progress', results)
            except Exception as e:
                log_sync(f"❌ Error en auto_sync: {e}", "ERROR")
                self.stats['syncs_failed'] += 1
                self._notify_listeners('sync_error', {'error': str(e)})
            
            for _ in range(self.sync_interval):
                if not self._running:
                    break
                time.sleep(1)
    
    def is_running(self) -> bool:
        return self._running
    
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
                log_sync(f"⚠️ Error en listener: {e}", "WARNING")
    
    # ============================================================
    # ESTADÍSTICAS
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            'tables_registered': len(self.tables),
            'running': self._running,
            'tables_status': {
                name: config['status'].value
                for name, config in self.tables.items()
            },
            'client_stats': self.client.get_stats() if self._client else None,
            'queue_stats': self.sync_queue.obtener_estadisticas()
        }


# ============================================================
# FUNCIONES DE ALTO NIVEL
# ============================================================

def sync_notas_pendientes(db_connection) -> Dict[str, Any]:
    """✅ Sincroniza notas de venta pendientes desde Turso."""
    log_sync("📋 Sincronizando notas pendientes...", "INFO")
    
    try:
        manager = SyncManager()
        
        if 'notas_venta' not in manager.tables:
            manager.register_table(
                'notas_venta',
                SyncDirection.FROM_TURSO,
                id_field='id',
                timestamp_field='created_at'
            )
        
        if 'nota_venta_detalle' not in manager.tables:
            manager.register_table(
                'nota_venta_detalle',
                SyncDirection.FROM_TURSO,
                id_field='id',
                timestamp_field='created_at'
            )
        
        results = {}
        
        result1 = manager.sync_from_turso('notas_venta', db_connection)
        results['notas_venta'] = result1
        
        result2 = manager.sync_from_turso('nota_venta_detalle', db_connection)
        results['nota_venta_detalle'] = result2
        
        log_sync(f"📊 Notas sincronizadas: {result1.get('received', 0)}", "INFO")
        log_sync(f"📊 Detalles sincronizados: {result2.get('received', 0)}", "INFO")
        
        return results
        
    except Exception as e:
        log_sync(f"❌ Error sync_notas_pendientes: {e}", "ERROR")
        return {'error': str(e)}


def sync_clientes_y_saldos(db_connection) -> Dict[str, Any]:
    """Sincroniza clientes y sus saldos desde Central a Turso."""
    manager = SyncManager()
    
    if 'clientes' not in manager.tables:
        manager.register_table(
            'clientes',
            SyncDirection.FROM_LOCAL,
            id_field='id',
            timestamp_field='updated_at'
        )
    
    return manager.sync_from_local('clientes', db_connection)


def sincronizar_todo(db_connection) -> Dict[str, Any]:
    """Sincroniza todas las tablas registradas."""
    manager = SyncManager()
    return manager.sync_all(db_connection)


# ============================================================
# PRUEBA RÁPIDA
# ============================================================

if __name__ == "__main__":
    from db.db_manager import obtener_conexion
    
    print("=" * 60)
    print("🧪 PRUEBA DEL GESTOR DE SINCRONIZACIÓN")
    print("=" * 60)
    
    db = obtener_conexion()
    manager = SyncManager()
    
    print(f"\n📊 Tablas registradas: {list(manager.tables.keys())}")
    print(f"\n📊 Configuración de tablas:")
    for name, config in manager.tables.items():
        print(f"  - {name}: {config['direction'].value}")
    
    client = get_turso_client()
    if client.is_connected():
        print("\n🔄 Ejecutando sincronización de prueba...")
        results = manager.sync_all(db)
        print(f"\n📊 Resultados:")
        for table, result in results.items():
            print(f"  - {table}: {result}")
    else:
        print("\n⚠️ No hay conexión a Turso. Omitiendo sincronización.")
    
    print("\n" + "=" * 60)