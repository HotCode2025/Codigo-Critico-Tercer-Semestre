"""
Código Crítico - Tercer Semestre Año 2026
Utilidades para manejo de fechas.
Funciones comunes de formato, conversión y validación de fechas.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Union


def fecha_hoy_iso() -> str:
    """Devuelve la fecha actual en formato ISO (AAAA-MM-DD)."""
    return date.today().isoformat()


def datetime_ahora_iso() -> str:
    """Devuelve la fecha y hora actual en formato ISO."""
    return datetime.now().isoformat()


def str_a_fecha(fecha_str: str) -> Optional[date]:
    """
    Convierte un string a objeto date.
    Soporta formatos: AAAA-MM-DD, DD/MM/AAAA, DD-MM-AAAA.
    """
    if not fecha_str:
        return None
    
    # Probar diferentes formatos
    formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def fecha_a_str(fecha_obj: Union[date, datetime, str]) -> str:
    """Convierte una fecha a string en formato ISO."""
    if isinstance(fecha_obj, str):
        return fecha_obj
    if isinstance(fecha_obj, datetime):
        return fecha_obj.date().isoformat()
    if isinstance(fecha_obj, date):
        return fecha_obj.isoformat()
    return ""


def validar_fecha_iso(fecha_str: str) -> bool:
    """Valida si un string tiene formato ISO válido."""
    try:
        datetime.fromisoformat(fecha_str)
        return True
    except (ValueError, TypeError):
        return False


def dias_entre(fecha1: str, fecha2: str) -> int:
    """Calcula la diferencia en días entre dos fechas."""
    f1 = str_a_fecha(fecha1)
    f2 = str_a_fecha(fecha2)
    if f1 and f2:
        return (f2 - f1).days
    return 0


def sumar_dias(fecha_str: str, dias: int) -> str:
    """Suma una cantidad de días a una fecha."""
    fecha_obj = str_a_fecha(fecha_str)
    if fecha_obj:
        return (fecha_obj + timedelta(days=dias)).isoformat()
    return ""


def formatear_fecha_argentina(fecha_str: str) -> str:
    """Convierte una fecha ISO a formato argentino (DD/MM/AAAA)."""
    fecha_obj = str_a_fecha(fecha_str)
    if fecha_obj:
        return fecha_obj.strftime('%d/%m/%Y')
    return ""


def obtener_mes_anio(fecha_str: str) -> str:
    """Devuelve el mes y año en formato 'MM-AAAA'."""
    fecha_obj = str_a_fecha(fecha_str)
    if fecha_obj:
        return fecha_obj.strftime('%m-%Y')
    return ""


def primer_dia_mes(fecha_str: str = None) -> str:
    """Devuelve el primer día del mes de la fecha dada."""
    if not fecha_str:
        fecha_obj = date.today()
    else:
        fecha_obj = str_a_fecha(fecha_str)
    if fecha_obj:
        return fecha_obj.replace(day=1).isoformat()
    return ""


def ultimo_dia_mes(fecha_str: str = None) -> str:
    """Devuelve el último día del mes de la fecha dada."""
    if not fecha_str:
        fecha_obj = date.today()
    else:
        fecha_obj = str_a_fecha(fecha_str)
    if fecha_obj:
        siguiente_mes = fecha_obj.replace(day=28) + timedelta(days=4)
        return (siguiente_mes - timedelta(days=siguiente_mes.day)).isoformat()
    return ""