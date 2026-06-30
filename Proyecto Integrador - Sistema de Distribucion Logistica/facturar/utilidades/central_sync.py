"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 5: central_sync.py - Punto de entrada para sincronización
==================================================
📌 USO: Punto de entrada para sincronización desde Central
📌 FUNCIONES PRINCIPALES:
    - sincronizar_desde_central(): Envía datos a Turso
    - sincronizar_desde_turso(): Recibe datos de Turso
    - iniciar_sincronizacion_auto(): Sincronización automática
    - sincronizar_ahora_directo(): Sincronización HTTP directa
"""

import os
import sys
import json
import threading
import time
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

# ✅ Importar desde sync_utils (evita cíclicos)
from utilidades.sync_utils import log_sync, get_turso_client, SyncDirection
from utilidades.sync_queue import get_sync_queue
from utilidades.sync_directo import sincronizar_ahora_directo, verificar_conexion_turso_directo


# ============================================================
# FUNCIÓN: VERIFICAR SI TABLA TIENE DATOS (CON CONEXIÓN PROPIA)
# ============================================================

def verificar_tabla_con_datos(db_connection, tabla: str) -> bool:
    """
    Verifica si una tabla tiene datos.
    ✅ Crea su propia conexión SQLite para evitar problemas de hilos
    """
    from db.db_manager import _ruta_base_datos
    import sqlite3
    
    thread_db = None
    try:
        db_path = _ruta_base_datos()
        
        # ✅ Crear conexión INDEPENDIENTE para este hilo
        thread_db = sqlite3.connect(db_path)
        thread_db.row_factory = sqlite3.Row
        thread_db.execute("PRAGMA foreign_keys = ON")
        
        cur = thread_db.cursor()
        cur.execute(f"SELECT COUNT(*) as total FROM {tabla}")
        total = cur.fetchone()[0]
        return total > 0
        
    except Exception as e:
        log_sync(f"  ⚠️ Error verificando tabla {tabla}: {e}", "WARNING")
        return False
    
    finally:
        # ✅ Cerrar conexión independiente
        if thread_db:
            try:
                thread_db.close()
            except:
                pass


# ============================================================
# FUNCIÓN: PROCESAR NOTAS PENDIENTES
# ============================================================

def procesar_notas_pendientes(db_connection) -> Dict[str, Any]:
    """
    Procesa notas de venta pendientes convirtiendo codigo_producto a producto_id.
    ✅ Crea su propia conexión SQLite para evitar problemas de hilos.
    """
    from db.db_manager import _ruta_base_datos
    
    log_sync("📋 PROCESANDO notas pendientes (codigo_producto → producto_id)", "INFO")
    
    thread_db = None
    resultados = {
        'notas_procesadas': 0,
        'errores': 0,
        'detalles': []
    }
    
    try:
        db_path = _ruta_base_datos()
        
        thread_db = sqlite3.connect(db_path)
        thread_db.row_factory = sqlite3.Row
        thread_db.execute("PRAGMA foreign_keys = ON")
        
        cur = thread_db.cursor()
        
        cur.execute("""
            SELECT DISTINCT n.id, n.numero_nota
            FROM notas_venta n
            JOIN nota_venta_detalle nd ON n.id = nd.nota_venta_id
            WHERE n.estado = 'PENDIENTE' 
            AND nd.producto_id IS NULL
            AND nd.codigo_producto IS NOT NULL
        """)
        
        notas = cur.fetchall()
        
        if not notas:
            log_sync("✅ Sin notas pendientes por procesar", "SUCCESS")
            return resultados
        
        log_sync(f"📋 Encontradas {len(notas)} notas con codigo_producto", "INFO")
        
        for nota in notas:
            nota_id = nota['id']
            numero_nota = nota['numero_nota']
            
            cur.execute("""
                SELECT id, codigo_producto, cantidad, precio_unitario
                FROM nota_venta_detalle
                WHERE nota_venta_id = ? AND producto_id IS NULL
            """, (nota_id,))
            
            detalles = cur.fetchall()
            productos_ok = 0
            productos_error = []
            
            for det in detalles:
                codigo = det['codigo_producto']
                
                cur.execute(
                    "SELECT id FROM productos WHERE codigo_producto = ? AND activo = 1",
                    (codigo,)
                )
                prod = cur.fetchone()
                
                if prod:
                    cur.execute("""
                        UPDATE nota_venta_detalle 
                        SET producto_id = ? 
                        WHERE id = ?
                    """, (prod['id'], det['id']))
                    productos_ok += 1
                else:
                    productos_error.append(codigo)
                    log_sync(f"⚠️ Producto '{codigo}' NO encontrado", "WARNING")
            
            if productos_error:
                resultados['errores'] += 1
                resultados['detalles'].append({
                    'nota': numero_nota,
                    'errores': productos_error
                })
                log_sync(f"⚠️ Nota {numero_nota}: {len(productos_error)} productos no encontrados", "WARNING")
            else:
                cur.execute("""
                    UPDATE notas_venta 
                    SET estado = 'PROCESADA' 
                    WHERE id = ?
                """, (nota_id,))
                resultados['notas_procesadas'] += 1
                log_sync(f"✅ Nota {numero_nota} procesada: {productos_ok} productos", "SUCCESS")
            
            thread_db.commit()
        
        log_sync(f"📊 NOTAS PROCESADAS: {resultados['notas_procesadas']}, ERRORES: {resultados['errores']}", "INFO")
        return resultados
        
    except Exception as e:
        if thread_db:
            thread_db.rollback()
        log_sync(f"❌ Error procesando notas: {e}", "ERROR")
        return {'error': str(e)}
    
    finally:
        if thread_db:
            try:
                thread_db.close()
            except:
                pass


# ============================================================
# FUNCIÓN: SYNC_NOTAS_PENDIENTES
# ============================================================

def sync_notas_pendientes(db_connection) -> Dict[str, Any]:
    """✅ Sincroniza notas de venta pendientes desde Turso."""
    log_sync("📋 Sincronizando notas pendientes desde Turso...", "INFO")
    
    try:
        from utilidades.sync_manager import SyncManager
        
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


# ============================================================
# FUNCIÓN: SINCRONIZAR AHORA (VÍA HTTP DIRECTA) - PRINCIPAL
# ============================================================

def sincronizar_ahora(db_connection) -> Dict[str, Any]:
    """
    ✅ Ejecuta sincronización inmediata usando HTTP DIRECTA.
    Esta es la función principal que usa el sistema.
    """
    log_sync("🔄 SINCRONIZACIÓN MANUAL INICIADA (HTTP DIRECTA)", "INFO")
    
    # ✅ Usar el método directo que FUNCIONA
    try:
        resultado = sincronizar_ahora_directo(db_connection)
        
        # Convertir al formato esperado por el sistema
        formateado = {
            'central_a_turso': resultado,
            'turso_a_central': {},
            'notas_procesadas': {'notas_procesadas': 0, 'errores': 0}
        }
        
        log_sync("🔄 SINCRONIZACIÓN MANUAL COMPLETADA (HTTP DIRECTA)", "SUCCESS")
        return formateado
        
    except Exception as e:
        log_sync(f"❌ Error en sincronización HTTP directa: {e}", "ERROR")
        return {'error': str(e)}


# ============================================================
# FUNCIÓN: VERIFICAR CONEXIÓN A TURSO
# ============================================================

def verificar_conexion_turso() -> bool:
    """Verifica si hay conexión activa con Turso usando HTTP directo"""
    return verificar_conexion_turso_directo()


# ============================================================
# FUNCIÓN: SINCRONIZAR DESDE CENTRAL A TURSO (LEGADO - MANTENIDO POR COMPATIBILIDAD)
# ============================================================

def sincronizar_desde_central(db_connection) -> Dict[str, Any]:
    """
    Sincroniza datos desde Central a Turso.
    ✅ Mantenido por compatibilidad - usa HTTP directo
    """
    log_sync("📤 INICIANDO sincronización Central → Turso (HTTP directo)", "INFO")
    return sincronizar_ahora(db_connection)


# ============================================================
# FUNCIÓN: SINCRONIZAR DESDE TURSO A CENTRAL
# ============================================================

def sincronizar_desde_turso(db_connection) -> Dict[str, Any]:
    """Sincroniza datos desde Turso a Central."""
    log_sync("📥 INICIANDO sincronización Turso → Central", "INFO")
    
    client = get_turso_client()
    if not client.is_connected():
        log_sync("❌ No hay conexión con Turso", "ERROR")
        return {'error': 'No hay conexión con Turso'}
    
    results = {}
    
    # 1. Sincronizar notas de venta
    notas_result = sync_notas_pendientes(db_connection)
    results['notas_venta'] = notas_result
    
    if notas_result.get('received', 0) > 0:
        log_sync(f"  ✅ notas_venta: {notas_result['received']} notas recibidas", "SUCCESS")
    
    from utilidades.sync_manager import SyncManager
    
    manager = SyncManager()
    
    # 2. Sincronizar visitas
    if 'visitas_clientes' not in manager.tables:
        manager.register_table(
            'visitas_clientes',
            SyncDirection.FROM_TURSO,
            id_field='id',
            timestamp_field='created_at'
        )
    
    visitas_result = manager.sync_from_turso('visitas_clientes', db_connection)
    results['visitas_clientes'] = visitas_result
    
    if visitas_result.get('received', 0) > 0:
        log_sync(f"  ✅ visitas_clientes: {visitas_result['received']} visitas recibidas", "SUCCESS")
    
    # 3. Sincronizar posiciones
    if 'posiciones_preventistas' not in manager.tables:
        manager.register_table(
            'posiciones_preventistas',
            SyncDirection.FROM_TURSO,
            id_field='id',
            timestamp_field='timestamp'
        )
    
    posiciones_result = manager.sync_from_turso('posiciones_preventistas', db_connection)
    results['posiciones_preventistas'] = posiciones_result
    
    if posiciones_result.get('received', 0) > 0:
        log_sync(f"  ✅ posiciones_preventistas: {posiciones_result['received']} posiciones recibidas", "SUCCESS")
    
    log_sync(f"📥 FINALIZADA sincronización Turso → Central", "SUCCESS")
    return results


# ============================================================
# FUNCIÓN: SINCRONIZACIÓN COMPLETA
# ============================================================

def sincronizacion_completa(db_connection) -> Dict[str, Any]:
    """Ejecuta sincronización completa (ambas direcciones)."""
    log_sync("🔄 INICIANDO sincronización COMPLETA", "INFO")
    
    resultados = {
        'central_a_turso': {},
        'turso_a_central': {},
        'notas_procesadas': {}
    }
    
    # Paso 1: Central → Turso (HTTP directo)
    resultados['central_a_turso'] = sincronizar_ahora(db_connection)
    
    # Paso 2: Turso → Central
    resultados['turso_a_central'] = sincronizar_desde_turso(db_connection)
    
    # Paso 3: Procesar notas
    resultados['notas_procesadas'] = procesar_notas_pendientes(db_connection)
    
    log_sync("🔄 FINALIZADA sincronización COMPLETA", "SUCCESS")
    return resultados


# ============================================================
# SINCRONIZACIÓN AUTOMÁTICA
# ============================================================

_sincronizador = None
_sync_lock = threading.Lock()

class SincronizadorAutomatico:
    """Sincronizador automático que corre en segundo plano."""
    
    def __init__(self, db_connection, intervalo: int = 5):
        self.db = db_connection
        self.intervalo = intervalo
        self._ejecutando = False
        self._thread = None
        self._listeners = []
    
    def iniciar(self):
        if self._ejecutando:
            return
        
        self._ejecutando = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        log_sync(f"🔄 Sincronizador automático iniciado (intervalo: {self.intervalo}s)", "INFO")
        self._notificar('iniciado', {'intervalo': self.intervalo})
    
    def detener(self):
        self._ejecutando = False
        if self._thread:
            self._thread.join(timeout=5)
        log_sync("⏹️ Sincronizador automático detenido", "INFO")
        self._notificar('detenido')
    
    def _loop(self):
        while self._ejecutando:
            try:
                resultado = sincronizacion_completa(self.db)
                self._notificar('sincronizado', resultado)
            except Exception as e:
                log_sync(f"❌ Error en sincronización automática: {e}", "ERROR")
                self._notificar('error', {'error': str(e)})
            
            for _ in range(self.intervalo):
                if not self._ejecutando:
                    break
                time.sleep(1)
    
    def esta_ejecutando(self) -> bool:
        return self._ejecutando
    
    def agregar_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def remover_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notificar(self, evento: str, datos: Any = None):
        for listener in self._listeners:
            try:
                listener(evento, datos)
            except Exception as e:
                log_sync(f"⚠️ Error en listener: {e}", "WARNING")


def iniciar_sincronizacion_auto(db_connection, intervalo: int = 5) -> SincronizadorAutomatico:
    """Inicia la sincronización automática."""
    global _sincronizador
    with _sync_lock:
        if _sincronizador is None:
            _sincronizador = SincronizadorAutomatico(db_connection, intervalo)
        if not _sincronizador.esta_ejecutando():
            _sincronizador.iniciar()
    return _sincronizador


def detener_sincronizacion_auto():
    """Detiene la sincronización automática global."""
    global _sincronizador
    with _sync_lock:
        if _sincronizador:
            _sincronizador.detener()
            _sincronizador = None


# ============================================================
# PRUEBA RÁPIDA
# ============================================================

if __name__ == "__main__":
    from db.db_manager import obtener_conexion
    
    print("=" * 60)
    print("🧪 PRUEBA DE central_sync.py (HTTP DIRECTA)")
    print("=" * 60)
    
    db = obtener_conexion()
    
    if verificar_conexion_turso():
        print("✅ Conexión a Turso verificada")
        
        print("\n🔄 Ejecutando sincronización manual...")
        resultado = sincronizar_ahora(db)
        
        print("\n📊 RESULTADOS:")
        central_a_turso = resultado.get('central_a_turso', {})
        for tabla, res in central_a_turso.items():
            if res.get('enviados', 0) > 0:
                print(f"   ✅ {tabla}: {res['enviados']} registros enviados")
            elif res.get('total', 0) == 0:
                print(f"   ℹ️ {tabla}: sin datos")
            else:
                print(f"   ⚠️ {tabla}: {res}")
    else:
        print("⚠️ No hay conexión a Turso")
    
    print("\n" + "=" * 60)