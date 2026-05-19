"""
Código Crítico - Tercer Semestre Año 2026
Constantes generales del sistema.
"""
# Versión del sistema
VERSION = "1.0.0"

# Nombre por defecto de la base de datos
NOMBRE_BD = "distribuidora.db"

# Directorios relativos
DIRECTORIO_ASSETS = "assets"
DIRECTORIO_REPORTES = "reportes_salida"

# Configuración de moneda por defecto
MONEDA_DEFECTO = "ARS"

# Alícuotas de IVA (usadas en cálculos, también en calculos.py)
IVA_POR_CONDICION = {
    "RI": 0.21,
    "M":  0.0,
    "EX": 0.0,
    "CF": 0.0,
    "MT": 0.0
}

# Días de anticipación para alertas de vencimiento
DIAS_ALERTA_VENCIMIENTO = 14

# Porcentaje límite por defecto para alerta de cuenta corriente
PORCENTAJE_LIMITE_CC = 80.0

# Formatos de fecha aceptados
FORMATO_FECHA_ISO = "%Y-%m-%d"
FORMATO_FECHA_LATINO = "%d/%m/%Y"

# Tipos de comprobante fiscal válidos
TIPOS_COMPROBANTE = ["A", "B", "C", "X"]

# Estados posibles de una nota de venta
ESTADOS_NOTA_VENTA = ["PENDIENTE", "FACTURADA", "ANULADA"]

# Estados de una factura
ESTADOS_FACTURA = ["EMITIDA", "ANULADA"]

# Medios de pago comunes
MEDIOS_PAGO = ["Efectivo", "Transferencia", "Cheque", "Tarjeta"]