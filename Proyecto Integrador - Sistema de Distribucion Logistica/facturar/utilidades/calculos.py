"""
Código Crítico - Tercer Semestre Año 2026
Funciones para cálculos financieros: IVA, tasas municipales, márgenes, ganancias.
"""

from typing import Dict, Optional

# Alícuotas de IVA según condición fiscal (estándar Argentina)
IVA_POR_CONDICION = {
    'RI': 0.21,          # Responsable Inscripto
    'M': 0.0,            # Monotributista (no discrimina IVA en factura)
    'EX': 0.0,           # Exento
    'CF': 0.0,           # Consumidor Final
    'MT': 0.0            # Monotributista (idem)
}

def calcular_iva(monto_neto: float, condicion_iva: str) -> float:
    """
    Calcula el IVA a partir del monto neto y la condición fiscal del cliente.
    Retorna el importe del IVA.
    """
    tasa = IVA_POR_CONDICION.get(condicion_iva, 0.0)
    return round(monto_neto * tasa, 2)

def calcular_tasa_municipal(monto_neto: float, porcentaje_tasa: float) -> float:
    """
    Calcula el importe de la tasa municipal.
    :param porcentaje_tasa: porcentaje a aplicar (ej: 2.5 significa 2.5%).
    """
    return round(monto_neto * (porcentaje_tasa / 100.0), 2)

def calcular_total_factura(subtotal: float, iva: float, tasa_municipal: float = 0.0) -> float:
    """Suma subtotal + IVA + tasa municipal."""
    return round(subtotal + iva + tasa_municipal, 2)

def calcular_ganancia_unitaria(precio_venta: float, precio_costo: float) -> float:
    """Ganancia bruta por unidad."""
    return round(precio_venta - precio_costo, 2)

def calcular_ganancia_total(precio_venta: float, precio_costo: float, cantidad: float) -> float:
    """Ganancia total (precio_venta - precio_costo) * cantidad."""
    return round((precio_venta - precio_costo) * cantidad, 2)

def calcular_margen_porcentaje(precio_costo: float, precio_venta: float) -> float:
    """
    Calcula el margen porcentual sobre el costo.
    Ejemplo: costo 100, venta 150 => 50.0 (50%).
    """
    if precio_costo == 0:
        return 0.0
    return round(((precio_venta - precio_costo) / precio_costo) * 100, 2)

def aplicar_porcentaje_incremento(precio_costo: float, porcentaje: float) -> float:
    """
    Calcula nuevo precio de venta a partir del costo y un porcentaje de incremento.
    Ejemplo: costo 100, porcentaje 50 => 150.
    """
    return round(precio_costo * (1 + porcentaje / 100.0), 2)

def obtener_porcentaje_iva(condicion_iva: str) -> float:
    """Devuelve la tasa de IVA (en decimal) para la condición dada."""
    return IVA_POR_CONDICION.get(condicion_iva, 0.0)