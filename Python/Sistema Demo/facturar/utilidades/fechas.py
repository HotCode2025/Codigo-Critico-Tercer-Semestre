"""
Código Crítico - Tercer Semestre Año 2026
Funciones auxiliares para manejo de fechas.
"""

from datetime import date, datetime, timedelta
from typing import Optional

def fecha_hoy() -> date:
    """Devuelve la fecha actual."""
    return date.today()

def fecha_actual_iso() -> str:
    """Devuelve la fecha actual en formato ISO (AAAA-MM-DD)."""
    return date.today().isoformat()

def parsear_fecha(fecha_str: str) -> Optional[date]:
    """
    Convierte una cadena de fecha en objeto date.
    Soporta formatos: AAAA-MM-DD, DD/MM/AAAA, DD-MM-AAAA.
    Retorna None si no se puede parsear.
    """
    if not fecha_str:
        return None
    # Intentar ISO
    try:
        return date.fromisoformat(fecha_str)
    except ValueError:
        pass
    # Intentar formatos con barra o guión (DD/MM/AAAA)
    separadores = ['/', '-']
    for sep in separadores:
        partes = fecha_str.split(sep)
        if len(partes) == 3:
            try:
                dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])
                return date(anio, mes, dia)
            except (ValueError, IndexError):
                continue
    return None

def sumar_dias(fecha: date, dias: int) -> date:
    """Suma (o resta si es negativo) días a una fecha."""
    return fecha + timedelta(days=dias)

def diferencia_dias(fecha1: date, fecha2: date) -> int:
    """Devuelve la diferencia en días entre fecha1 y fecha2 (fecha1 - fecha2)."""
    return (fecha1 - fecha2).days

def fecha_en_rango(fecha: date, inicio: date, fin: date) -> bool:
    """Retorna True si la fecha está dentro del intervalo [inicio, fin]."""
    return inicio <= fecha <= fin

def es_vencimiento_proximo(fecha_venc: date, dias_aviso: int = 14) -> bool:
    """Indica si la fecha de vencimiento está dentro de los próximos 'dias_aviso' días."""
    hoy = date.today()
    limite = hoy + timedelta(days=dias_aviso)
    return hoy <= fecha_venc <= limite