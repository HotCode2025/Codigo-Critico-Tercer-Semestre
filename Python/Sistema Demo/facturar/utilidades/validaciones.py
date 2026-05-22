"""
Código Crítico - Tercer Semestre Año 2026
Módulo de validaciones comunes para datos del sistema.
"""

import re
from datetime import datetime

def validar_cuit(cuit: str) -> bool:
    """
    Valida un CUIT argentino (11 dígitos, con dígito verificador).
    Acepta formatos: XX-XXXXXXXX-X o XXXXXXXXXXX.
    Retorna True si es válido, False en caso contrario.
    """
    cuit = re.sub(r'[^\d]', '', cuit)  # eliminar guiones y espacios
    if len(cuit) != 11:
        return False
    if not cuit.isdigit():
        return False
    multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(cuit[i]) * multiplicadores[i] for i in range(10))
    resto = suma % 11
    digito_verif = 11 - resto
    if digito_verif == 11:
        digito_verif = 0
    if digito_verif == 10:
        return False  # no debería ocurrir, pero se rechaza
    return digito_verif == int(cuit[10])

def validar_email(email: str) -> bool:
    """
    Verifica que el string tenga un formato básico de email.
    Retorna True si es válido.
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_requerido(texto: str) -> bool:
    """Retorna True si el texto no está vacío (ni solo espacios)."""
    return bool(texto and texto.strip())

def validar_numero_positivo(valor) -> bool:
    """Retorna True si el valor puede convertirse a float y es > 0."""
    try:
        num = float(valor)
        return num > 0
    except (ValueError, TypeError):
        return False

def validar_numero_no_negativo(valor) -> bool:
    """Retorna True si el valor puede convertirse a float y es >= 0."""
    try:
        num = float(valor)
        return num >= 0
    except (ValueError, TypeError):
        return False

def validar_fecha_iso(fecha_str: str) -> bool:
    """
    Verifica que una cadena tenga formato ISO AAAA-MM-DD y sea una fecha real.
    """
    try:
        datetime.fromisoformat(fecha_str)
        return True
    except (ValueError, TypeError):
        return False