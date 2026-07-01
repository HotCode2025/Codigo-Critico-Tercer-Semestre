#!/usr/bin/env python3
"""
Código Crítico - Tercer Semestre Año 2026
==================================================
MONITOR DE SINCRONIZACIÓN EN TIEMPO REAL
==================================================
📌 Muestra:
    - Estado de conexión
    - Datos enviando/recibiendo
    - Progreso en tiempo real
    - Estadísticas de sincronización
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, List

from utilidades.sync_utils import log_sync
from utilidades.turso_client import get_turso_client


class SyncMonitor:
    """
    Monitor de sincronización en tiempo real.
    Muestra el progreso de la sincronización con Turso.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._registros_enviados = 0
        self._registros_recibidos = 0
        self._tablas_procesadas: List[str] = []
        self._errores: List[str] = []
        self._ultima_sincronizacion = None
        self._en_proceso = False
        self._listeners = []
        
        # Estadísticas detalladas
        self.estadisticas = {
            'total_enviados': 0,
            'total_recibidos': 0,
            'tablas_sincronizadas': {},
            'errores': [],
            'ultimo_evento': None
        }
    
    def iniciar_sincronizacion(self, tabla: str = None):
        """Marca el inicio de una sincronización"""
        self._en_proceso = True
        self._tablas_procesadas = []
        self._errores = []
        self._registros_enviados = 0
        self._registros_recibidos = 0
        self._ultima_sincronizacion = datetime.now()
        
        if tabla:
            self._notificar('inicio_tabla', {'tabla': tabla})
        else:
            self._notificar('inicio', {'timestamp': self._ultima_sincronizacion})
    
    def registrar_envio(self, tabla: str, cantidad: int):
        """Registra envío de datos a Turso"""
        self._registros_enviados += cantidad
        if tabla not in self.estadisticas['tablas_sincronizadas']:
            self.estadisticas['tablas_sincronizadas'][tabla] = {'enviados': 0, 'recibidos': 0}
        self.estadisticas['tablas_sincronizadas'][tabla]['enviados'] += cantidad
        self.estadisticas['total_enviados'] += cantidad
        
        # Mostrar en consola con colores
        print(f"   📤 Enviando {tabla}: {cantidad} registros (Total: {self._registros_enviados})")
        
        self._notificar('envio', {
            'tabla': tabla,
            'cantidad': cantidad,
            'total': self._registros_enviados
        })
    
    def registrar_recibido(self, tabla: str, cantidad: int):
        """Registra recepción de datos desde Turso"""
        self._registros_recibidos += cantidad
        if tabla not in self.estadisticas['tablas_sincronizadas']:
            self.estadisticas['tablas_sincronizadas'][tabla] = {'enviados': 0, 'recibidos': 0}
        self.estadisticas['tablas_sincronizadas'][tabla]['recibidos'] += cantidad
        self.estadisticas['total_recibidos'] += cantidad
        
        # Mostrar en consola con colores
        print(f"   📥 Recibiendo {tabla}: {cantidad} registros (Total: {self._registros_recibidos})")
        
        self._notificar('recibido', {
            'tabla': tabla,
            'cantidad': cantidad,
            'total': self._registros_recibidos
        })
    
    def registrar_error(self, tabla: str, error: str):
        """Registra un error de sincronización"""
        self._errores.append(f"{tabla}: {error}")
        self.estadisticas['errores'].append({
            'tabla': tabla,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
        
        # Mostrar en consola con color rojo
        print(f"   ❌ Error en {tabla}: {error}")
        
        self._notificar('error', {
            'tabla': tabla,
            'error': error
        })
    
    def finalizar_sincronizacion(self):
        """Marca el fin de la sincronización"""
        self._en_proceso = False
        self.estadisticas['ultimo_evento'] = {
            'timestamp': datetime.now().isoformat(),
            'enviados': self._registros_enviados,
            'recibidos': self._registros_recibidos,
            'errores': len(self._errores)
        }
        
        # Mostrar resumen en consola
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE SINCRONIZACIÓN")
        print("=" * 60)
        print(f"   📤 Enviados: {self._registros_enviados} registros")
        print(f"   📥 Recibidos: {self._registros_recibidos} registros")
        print(f"   ❌ Errores: {len(self._errores)}")
        if self._errores:
            print(f"   ⚠️ Errores: {', '.join(self._errores[:3])}")
        
        self._notificar('fin', {
            'enviados': self._registros_enviados,
            'recibidos': self._registros_recibidos,
            'errores': len(self._errores)
        })
    
    def obtener_estado(self) -> Dict[str, Any]:
        """Obtiene el estado actual del monitor"""
        client = get_turso_client()
        
        return {
            'conectado': client.is_connected() if client else False,
            'en_proceso': self._en_proceso,
            'ultima_sincronizacion': self._ultima_sincronizacion,
            'registros_enviados': self._registros_enviados,
            'registros_recibidos': self._registros_recibidos,
            'tablas_procesadas': self._tablas_procesadas,
            'errores': self._errores,
            'estadisticas': self.estadisticas,
            'url': client.config.url if client and hasattr(client, 'config') else None
        }
    
    def agregar_listener(self, callback):
        """Agrega un listener para eventos"""
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def _notificar(self, evento: str, datos: Any = None):
        """Notifica a todos los listeners"""
        for listener in self._listeners:
            try:
                listener(evento, datos)
            except Exception as e:
                print(f"⚠️ Error en listener: {e}")
    
    def mostrar_progreso(self, mensaje: str = "", nivel: str = "INFO"):
        """Muestra progreso en consola con formato"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colores = {
            'INFO': '\033[94m',     # Azul
            'SUCCESS': '\033[92m',  # Verde
            'WARNING': '\033[93m',  # Amarillo
            'ERROR': '\033[91m',    # Rojo
            'SEND': '\033[96m',     # Cian
            'RECEIVE': '\033[95m'   # Magenta
        }
        
        color = colores.get(nivel, '\033[0m')
        print(f"{color}[{timestamp}] {mensaje}\033[0m")


# ============================================================
# SINGLETON
# ============================================================

_monitor = None

def get_sync_monitor() -> SyncMonitor:
    """Obtiene la instancia única del monitor"""
    global _monitor
    if _monitor is None:
        _monitor = SyncMonitor()
    return _monitor


# ============================================================
# FUNCIÓN PARA MOSTRAR ESTADO EN CONSOLA
# ============================================================

def mostrar_estado_sincronizacion():
    """Muestra el estado actual de la sincronización"""
    monitor = get_sync_monitor()
    estado = monitor.obtener_estado()
    
    print("\n" + "=" * 60)
    print("📊 ESTADO DE SINCRONIZACIÓN")
    print("=" * 60)
    
    # Estado de conexión
    if estado['conectado']:
        print("   ✅ Turso: Conectado")
    else:
        print("   ❌ Turso: Desconectado")
    
    # Estado de proceso
    if estado['en_proceso']:
        print(f"   🔄 Sincronización en curso...")
        print(f"   📤 Enviados: {estado['registros_enviados']}")
        print(f"   📥 Recibidos: {estado['registros_recibidos']}")
    else:
        print(f"   ⏸️  Sincronización inactiva")
        if estado['ultima_sincronizacion']:
            print(f"   🕐 Última: {estado['ultima_sincronizacion'].strftime('%H:%M:%S')}")
    
    # Tablas procesadas
    if estado['tablas_procesadas']:
        print(f"   📋 Tablas procesadas: {len(estado['tablas_procesadas'])}")
        for tabla in estado['tablas_procesadas'][:5]:
            print(f"      - {tabla}")
        if len(estado['tablas_procesadas']) > 5:
            print(f"      ... y {len(estado['tablas_procesadas']) - 5} más")
    
    # Errores
    if estado['errores']:
        print(f"   ❌ Errores: {len(estado['errores'])}")
        for error in estado['errores'][:3]:
            print(f"      - {error}")
    
    print("=" * 60)