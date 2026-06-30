"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Utilidades compartidas para sincronización
==================================================
"""

import os
import json
from datetime import datetime
from typing import Any, List, Dict, Optional
from enum import Enum


LOG_DIR = "logs"

def asegurar_directorio_log():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def log_sync(mensaje: str, nivel: str = "INFO"):
    asegurar_directorio_log()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{nivel}] {mensaje}\n"
    try:
        log_file = os.path.join(LOG_DIR, f"sync_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    except:
        pass
    print(f"{log_line.strip()}")


def escape_sql(valor: Any) -> str:
    if valor is None:
        return "NULL"
    if isinstance(valor, str):
        return f"'{valor.replace("'", "''")}'"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, datetime):
        return f"'{valor.isoformat()}'"
    if isinstance(valor, (dict, list)):
        return f"'{json.dumps(valor)}'"
    return f"'{str(valor)}'"


class SyncDirection(Enum):
    FROM_LOCAL = "from_local"
    FROM_TURSO = "from_turso"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    NO_CHANGES = "no_changes"


def obtener_tablas_sync() -> Dict[str, Dict]:
    """
    ✅ OPTIMIZADO: batch_size = 500 para sincronización más rápida
    """
    return {
        'clientes': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'updated_at', 'batch_size': 500},
        'productos': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'updated_at', 'batch_size': 500},
        'preventistas': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'updated_at', 'batch_size': 500},
        'categorias': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'updated_at', 'batch_size': 500},
        'lotes': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'updated_at', 'batch_size': 500},
        'usuarios': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'updated_at', 'batch_size': 500},
        'facturas': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'factura_detalle': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'cobros': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'cheques': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'cuenta_corriente_movimientos': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'pedidos_procesados': {'direction': SyncDirection.FROM_LOCAL, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        
        'notas_venta': {'direction': SyncDirection.FROM_TURSO, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'nota_venta_detalle': {'direction': SyncDirection.FROM_TURSO, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'visitas_clientes': {'direction': SyncDirection.FROM_TURSO, 'id_field': 'id', 'timestamp_field': 'created_at', 'batch_size': 500},
        'posiciones_preventistas': {'direction': SyncDirection.FROM_TURSO, 'id_field': 'id', 'timestamp_field': 'timestamp', 'batch_size': 500},
    }


_turso_client_instance = None

def get_turso_client():
    global _turso_client_instance
    if _turso_client_instance is None:
        from utilidades.turso_client import get_turso_client as _get_turso
        _turso_client_instance = _get_turso()
    return _turso_client_instance


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 sync_utils.py")
    print("=" * 60)
    print(f"📊 Tablas configuradas: {list(obtener_tablas_sync().keys())}")