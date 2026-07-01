"""
Código Crítico - Tercer Semestre Año 2026
Script para generar datos masivos de prueba - CON VENTAS
============================================================
📌 COMPATIBLE CON: script_creacion.sql (UUID)
📌 PERÍODO: 26-06-2026 hacia atrás 6 meses
📌 CLIENTES: 700 (100 por preventista)
📌 VENTAS: Facturas y notas de venta procesadas
📌 USO: python generar_datos_masivos.py
"""

import sqlite3
import random
import sys
import os
import uuid
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_manager import obtener_conexion, inicializar_bd

# ============================================================
# CONFIGURACIÓN - PERÍODO DE 6 MESES
# ============================================================

FECHA_FIN = date(2026, 6, 26)
FECHA_INICIO = FECHA_FIN - timedelta(days=180)  # 6 meses
CANTIDAD_CLIENTES_POR_PREVENTISTA = 100
TOTAL_CLIENTES = 700

# ============================================================
# PARÁMETROS DE LA EMPRESA
# ============================================================

PARAMETROS = {
    'moneda': 'ARS',
    'nombre_distribuidora': 'Tregar Mendoza S.A.',
    'direccion': 'Av. San Martín 1234, San Martín, Mendoza',
    'telefono1': '0261-1234-5678',
    'telefono2': '0261-1234-5679',
    'whatsapp': '0261-1234-5678',
    'email': 'ventas@tregar-mendoza.com.ar',
    'encabezado_factura': 'Tregar - Productos Lácteos',
    'encabezado_reporte': 'Tregar - Sistema de Distribución Mendoza',
    'tasa_municipal_porcentaje': 2.5,
    'punto_venta': '0001',
    'ultimo_numero_factura': 1,
    'calle': 'Av. San Martín',
    'numero': '1234',
    'localidad': 'San Martín',
    'provincia': 'Mendoza',
    'pais': 'Argentina',
    'latitud': -33.0810,
    'longitud': -68.4681
}

# ============================================================
# PREVENTISTAS CON ASIGNACIÓN SOLICITADA
# ============================================================

PREVENTISTAS = [
    {
        'nombre': 'Ariel',
        'apellido': 'Mazara',
        'legajo': 'P002',
        'telefono': '0261-1234-1002',
        'email': 'ariel.mazara@tregar.com',
        'zona': 'Valle de Uco',
        'localidad': 'Tunuyán',
        'provincia': 'Mendoza'
    },
    {
        'nombre': 'Agustina',
        'apellido': 'Zúñiga',
        'legajo': 'P003',
        'telefono': '0261-1234-1003',
        'email': 'agustina.zuniga@tregar.com',
        'zona': 'Centro Mendoza',
        'localidad': 'Mendoza Capital',
        'provincia': 'Mendoza'
    },
    {
        'nombre': 'Maximiliano',
        'apellido': 'Morales',
        'legajo': 'P004',
        'telefono': '0261-1234-1004',
        'email': 'maximiliano.morales@tregar.com',
        'zona': 'Sur Mendoza',
        'localidad': 'San Rafael',
        'provincia': 'Mendoza'
    },
    {
        'nombre': 'Santino',
        'apellido': 'Mamani',
        'legajo': 'P005',
        'telefono': '0261-1234-1005',
        'email': 'santino.mamani@tregar.com',
        'zona': 'Este Mendoza',
        'localidad': 'Junín',
        'provincia': 'Mendoza'
    },
    {
        'nombre': 'Joel',
        'apellido': 'Gonzalez',
        'legajo': 'P006',
        'telefono': '0261-1234-1006',
        'email': 'joel.gonzalez@tregar.com',
        'zona': 'Sur Mendoza',
        'localidad': 'General Alvear',
        'provincia': 'Mendoza'
    },
    {
        'nombre': 'Daniel',
        'apellido': 'Silva',
        'legajo': 'P007',
        'telefono': '0264-1234-1007',
        'email': 'daniel.silva@tregar.com',
        'zona': 'San Juan',
        'localidad': 'San Juan Capital',
        'provincia': 'San Juan'
    },
    {
        'nombre': 'Damián',
        'apellido': 'Ponce de León',
        'legajo': 'P008',
        'telefono': '0266-1234-1008',
        'email': 'damian.poncedeleon@tregar.com',
        'zona': 'San Luis',
        'localidad': 'San Luis Capital',
        'provincia': 'San Luis'
    },
]

# ============================================================
# LOCALIDADES POR ZONA
# ============================================================

LOCALIDADES = {
    # Valle de Uco (P002 - Ariel Mazara)
    'Tunuyán': {'provincia': 'Mendoza', 'lat': -33.5667, 'lon': -69.0167},
    'San Carlos': {'provincia': 'Mendoza', 'lat': -33.7667, 'lon': -69.0333},
    'Tupungato': {'provincia': 'Mendoza', 'lat': -33.3667, 'lon': -69.1500},
    'La Consulta': {'provincia': 'Mendoza', 'lat': -33.7333, 'lon': -69.0667},
    'Villa Seca': {'provincia': 'Mendoza', 'lat': -33.5667, 'lon': -69.0667},
    'Los Árboles': {'provincia': 'Mendoza', 'lat': -33.3833, 'lon': -69.2000},
    
    # Centro Mendoza (P003 - Agustina Zúñiga)
    'Mendoza Capital': {'provincia': 'Mendoza', 'lat': -32.8902, 'lon': -68.8440},
    'Godoy Cruz': {'provincia': 'Mendoza', 'lat': -32.9167, 'lon': -68.8333},
    'Las Heras': {'provincia': 'Mendoza', 'lat': -32.8500, 'lon': -68.8000},
    'Guaymallén': {'provincia': 'Mendoza', 'lat': -32.8833, 'lon': -68.7500},
    'Maipú': {'provincia': 'Mendoza', 'lat': -33.0000, 'lon': -68.7667},
    
    # Sur Mendoza (P004 - Maximiliano Morales y P006 - Joel Gonzalez)
    'San Rafael': {'provincia': 'Mendoza', 'lat': -34.6000, 'lon': -68.3333},
    'General Alvear': {'provincia': 'Mendoza', 'lat': -34.9833, 'lon': -67.7000},
    'Malargüe': {'provincia': 'Mendoza', 'lat': -35.4667, 'lon': -69.5833},
    'El Nihuil': {'provincia': 'Mendoza', 'lat': -35.0167, 'lon': -68.7000},
    'La Paz': {'provincia': 'Mendoza', 'lat': -33.4500, 'lon': -67.5500},
    'Villa Atuel': {'provincia': 'Mendoza', 'lat': -34.8167, 'lon': -68.2000},
    
    # Este Mendoza (P005 - Santino Mamani)
    'Junín': {'provincia': 'Mendoza', 'lat': -33.1333, 'lon': -68.4667},
    'Rivadavia': {'provincia': 'Mendoza', 'lat': -33.1833, 'lon': -68.4667},
    'San Martín': {'provincia': 'Mendoza', 'lat': -33.0810, 'lon': -68.4681},
    'Santa Rosa': {'provincia': 'Mendoza', 'lat': -33.2500, 'lon': -68.1500},
    'La Dormida': {'provincia': 'Mendoza', 'lat': -33.0000, 'lon': -68.5000},
    'Monte Comán': {'provincia': 'Mendoza', 'lat': -34.1000, 'lon': -67.2667},
    
    # San Juan (P007 - Daniel Silva)
    'San Juan Capital': {'provincia': 'San Juan', 'lat': -31.5375, 'lon': -68.5364},
    'Rivadavia SJ': {'provincia': 'San Juan', 'lat': -31.5500, 'lon': -68.5833},
    'Rawson': {'provincia': 'San Juan', 'lat': -31.5667, 'lon': -68.5667},
    'Chimbas': {'provincia': 'San Juan', 'lat': -31.5000, 'lon': -68.5333},
    'Santa Lucía SJ': {'provincia': 'San Juan', 'lat': -31.5333, 'lon': -68.5000},
    'Caucete': {'provincia': 'San Juan', 'lat': -31.6500, 'lon': -68.2833},
    'Pocito': {'provincia': 'San Juan', 'lat': -31.6833, 'lon': -68.6000},
    
    # San Luis (P008 - Damián Ponce de León)
    'San Luis Capital': {'provincia': 'San Luis', 'lat': -33.2950, 'lon': -66.3370},
    'Villa Mercedes': {'provincia': 'San Luis', 'lat': -33.6667, 'lon': -65.4667},
    'La Punta': {'provincia': 'San Luis', 'lat': -33.1833, 'lon': -66.3000},
    'Juana Koslay': {'provincia': 'San Luis', 'lat': -33.2167, 'lon': -66.2667},
    'Merlo': {'provincia': 'San Luis', 'lat': -32.3333, 'lon': -65.0167},
    'Concarán': {'provincia': 'San Luis', 'lat': -32.5667, 'lon': -65.2500},
}

# ============================================================
# CALLES POR LOCALIDAD
# ============================================================

CALLES = {
    'Mendoza Capital': ['Av. San Martín', 'Av. España', 'Av. Las Heras', 'Peatonal Sarmiento', 'Colón', 'Belgrano', 'Lavalle', 'Chile'],
    'Godoy Cruz': ['Av. San Martín', 'Av. España', 'Av. Las Heras', 'Belgrano', 'Mitre', 'Rivadavia', 'San Luis', 'Mendoza'],
    'Guaymallén': ['Av. San Martín', 'Av. España', 'Av. Bandera de los Andes', 'Belgrano', 'Mitre', 'Rivadavia', 'Pedro Molina'],
    'Maipú': ['Av. San Martín', 'Av. España', 'Av. Las Heras', 'Belgrano', 'Mitre', 'Rivadavia', 'San Luis', 'Mendoza'],
    'Las Heras': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno'],
    'Tunuyán': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno', 'Lavalle'],
    'San Carlos': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno'],
    'Tupungato': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'La Consulta': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Villa Seca': ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'],
    'Los Árboles': ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'],
    'San Rafael': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno'],
    'General Alvear': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno', 'Lavalle'],
    'Malargüe': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'El Nihuil': ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'],
    'La Paz': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Villa Atuel': ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'],
    'Junín': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Rivadavia': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno'],
    'San Martín': ['Av. San Martín', 'Av. Libertador', 'Mitre', 'Belgrano', 'Sarmiento', 'Rivadavia', '25 de Mayo', 'Moreno'],
    'Santa Rosa': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'La Dormida': ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'],
    'Monte Comán': ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'],
    'San Juan Capital': ['Av. Libertador', 'Av. España', 'Av. Rawson', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Rivadavia SJ': ['Av. Libertador', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Rawson': ['Av. Libertador', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Chimbas': ['Av. Libertador', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Santa Lucía SJ': ['Av. Libertador', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Caucete': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Pocito': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'San Luis Capital': ['Av. Illia', 'Av. España', 'Av. Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Colón'],
    'Villa Mercedes': ['Av. San Martín', 'Av. España', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'La Punta': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Juana Koslay': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Merlo': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
    'Concarán': ['Av. San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo'],
}

# ============================================================
# NOMBRES DE NEGOCIOS
# ============================================================

NOMBRES_NEGOCIOS = [
    'Almacén Don José', 'Almacén La Esquina', 'Almacén El Progreso', 'Almacén Santa Rosa',
    'Almacén La Familia', 'Almacén El Buen Gusto', 'Almacén La Amistad', 'Almacén El Sol',
    'Almacén La Esperanza', 'Almacén El Porvenir', 'Almacén Doña María', 'Almacén El Vecino',
    'Almacén La Confianza', 'Almacén El Éxito', 'Almacén La Economía', 'Almacén Don Pedro',
    'Kiosco La Esquina', 'Kiosco El Diario', 'Kiosco La Plaza', 'Kiosco El Centro',
    'Kiosco Don Luis', 'Kiosco La Esquinita', 'Kiosco El Chango', 'Kiosco La Golosina',
    'Supermercado El Ahorro', 'Supermercado La Economía', 'Supermercado El Precio Justo',
    'Supermercado La Oferta', 'Supermercado El Mayorista', 'Supermercado La Distribuidora',
]

# ============================================================
# PRODUCTOS - CATÁLOGO TREGAR (95 productos)
# ============================================================

PRODUCTOS_TREGAR = [
    # LECHES LARGA VIDA (6)
    {'codigo_producto': '1685', 'nombre': 'Leche Entera Tetra 1L (Wing Cap)', 'costo': 600, 'venta': 950, 'categoria': 'Leches'},
    {'codigo_producto': '682', 'nombre': 'Leche Entera Tetra 1L (Flexicap)', 'costo': 600, 'venta': 950, 'categoria': 'Leches'},
    {'codigo_producto': '1686', 'nombre': 'Leche Parcialmente Descremada 1L (Wing Cap)', 'costo': 580, 'venta': 920, 'categoria': 'Leches'},
    {'codigo_producto': '1609', 'nombre': 'Leche Parcialmente Descremada 1L (Flexicap)', 'costo': 580, 'venta': 920, 'categoria': 'Leches'},
    {'codigo_producto': '1621', 'nombre': 'Leche Descremada 0% Lactosa 1L', 'costo': 720, 'venta': 1100, 'categoria': 'Leches'},
    {'codigo_producto': '1274', 'nombre': 'Leche 0% Grasa 1L', 'costo': 590, 'venta': 935, 'categoria': 'Leches'},
    
    # LECHES SABORIZADAS (2)
    {'codigo_producto': '363', 'nombre': 'Chocolatada 1L', 'costo': 650, 'venta': 1000, 'categoria': 'Leches Saborizadas'},
    {'codigo_producto': '1319', 'nombre': 'Chocolatada 200cc', 'costo': 350, 'venta': 550, 'categoria': 'Leches Saborizadas'},
    
    # LECHES EN POLVO (3)
    {'codigo_producto': '378', 'nombre': 'Leche en Polvo Entera Instantánea 800g', 'costo': 850, 'venta': 1350, 'categoria': 'Leches en Polvo'},
    {'codigo_producto': '312', 'nombre': 'Leche en Polvo Entera (Alimenta) 25kg', 'costo': 18000, 'venta': 25000, 'categoria': 'Leches en Polvo'},
    {'codigo_producto': '346', 'nombre': 'Suero en Polvo Demib 25kg', 'costo': 12000, 'venta': 18000, 'categoria': 'Leches en Polvo'},
    
    # YOGURES CUCHAREABLES (18)
    {'codigo_producto': '2175', 'nombre': 'Batido Entero con Café 120g', 'costo': 400, 'venta': 650, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2176', 'nombre': 'Batido Entero con Coco 120g', 'costo': 400, 'venta': 650, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2177', 'nombre': 'Batido Entero con Limón 120g', 'costo': 400, 'venta': 650, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '1995', 'nombre': 'Cremoso Entero Frutilla 125g', 'costo': 450, 'venta': 700, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '1997', 'nombre': 'Cremoso Entero Vainilla 125g', 'costo': 450, 'venta': 700, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '1998', 'nombre': 'Cremoso Entero Dulce de Leche 125g', 'costo': 450, 'venta': 700, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2114', 'nombre': 'Cremoso Descremado Frutilla 125g', 'costo': 430, 'venta': 680, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2115', 'nombre': 'Cremoso Descremado Vainilla 125g', 'costo': 430, 'venta': 680, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '1636', 'nombre': 'Entero con Trozos de Frutilla 160g', 'costo': 500, 'venta': 780, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '1637', 'nombre': 'Entero con Trozos de Durazno 160g', 'costo': 500, 'venta': 780, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '1638', 'nombre': 'Entero con Trozos de Arándano 160g', 'costo': 520, 'venta': 800, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2154', 'nombre': 'Entero con Trozos de Mango + Maracuyá 160g', 'costo': 530, 'venta': 810, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2153', 'nombre': 'Entero con Trozos de Ananá 160g', 'costo': 520, 'venta': 800, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2174', 'nombre': 'Entero con Trozos de Cereza 160g', 'costo': 540, 'venta': 820, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2155', 'nombre': 'Descremado con Trozos de Frutilla 160g', 'costo': 480, 'venta': 750, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2156', 'nombre': 'Descremado con Trozos de Durazno 160g', 'costo': 480, 'venta': 750, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2157', 'nombre': 'Descremado con Trozos de Arándano 160g', 'costo': 500, 'venta': 770, 'categoria': 'Yogures Cuchareables'},
    {'codigo_producto': '2173', 'nombre': 'Descremado con Trozos de Ananá 160g', 'costo': 480, 'venta': 750, 'categoria': 'Yogures Cuchareables'},
    
    # YOGURES FIRMES (4)
    {'codigo_producto': '2231', 'nombre': 'Firme Entero Frutilla 170g', 'costo': 420, 'venta': 660, 'categoria': 'Yogures Firmes'},
    {'codigo_producto': '2232', 'nombre': 'Firme Entero Vainilla 170g', 'costo': 420, 'venta': 660, 'categoria': 'Yogures Firmes'},
    {'codigo_producto': '2240', 'nombre': 'Firme Descremado Frutilla 170g', 'costo': 400, 'venta': 640, 'categoria': 'Yogures Firmes'},
    {'codigo_producto': '2241', 'nombre': 'Firme Descremado Vainilla 170g', 'costo': 400, 'venta': 640, 'categoria': 'Yogures Firmes'},
    
    # YOGURES NATURALES (4)
    {'codigo_producto': '2171', 'nombre': 'Natural Endulzado 280g', 'costo': 380, 'venta': 600, 'categoria': 'Yogures Naturales'},
    {'codigo_producto': '1694', 'nombre': 'Natural Endulzado 140g', 'costo': 320, 'venta': 520, 'categoria': 'Yogures Naturales'},
    {'codigo_producto': '2172', 'nombre': 'Natural Sin Azúcar 280g', 'costo': 370, 'venta': 590, 'categoria': 'Yogures Naturales'},
    {'codigo_producto': '2149', 'nombre': 'Natural Sin Azúcar 140g', 'costo': 310, 'venta': 510, 'categoria': 'Yogures Naturales'},
    
    # YOGURES CON TOPPING (4)
    {'codigo_producto': '2139', 'nombre': 'Tops Entero con Copos de Maíz 164g', 'costo': 460, 'venta': 720, 'categoria': 'Yogures con Topping'},
    {'codigo_producto': '2168', 'nombre': 'Tops Entero con Granola 155g', 'costo': 470, 'venta': 730, 'categoria': 'Yogures con Topping'},
    {'codigo_producto': '2140', 'nombre': 'Tops Descremado con Copos de Maíz y Miel 164g', 'costo': 440, 'venta': 700, 'categoria': 'Yogures con Topping'},
    {'codigo_producto': '2214', 'nombre': 'Tops Descremado con Granola 155g', 'costo': 450, 'venta': 710, 'categoria': 'Yogures con Topping'},
    
    # YOGURES BEBIBLES (7)
    {'codigo_producto': '1993', 'nombre': 'Entero Bebible Frutilla 900g', 'costo': 550, 'venta': 850, 'categoria': 'Yogures Bebibles'},
    {'codigo_producto': '1994', 'nombre': 'Entero Bebible Vainilla 900g', 'costo': 550, 'venta': 850, 'categoria': 'Yogures Bebibles'},
    {'codigo_producto': '1695', 'nombre': 'Entero Bebible Durazno 900g', 'costo': 550, 'venta': 850, 'categoria': 'Yogures Bebibles'},
    {'codigo_producto': '1696', 'nombre': 'Entero Bebible Arándano 900g', 'costo': 560, 'venta': 860, 'categoria': 'Yogures Bebibles'},
    {'codigo_producto': '2211', 'nombre': 'Descremado Bebible Frutilla 900g', 'costo': 530, 'venta': 820, 'categoria': 'Yogures Bebibles'},
    {'codigo_producto': '2212', 'nombre': 'Descremado Bebible Vainilla 900g', 'costo': 530, 'venta': 820, 'categoria': 'Yogures Bebibles'},
    {'codigo_producto': '2213', 'nombre': 'Descremado Bebible Durazno 900g', 'costo': 530, 'venta': 820, 'categoria': 'Yogures Bebibles'},
    
    # ARROZ CON LECHE (5)
    {'codigo_producto': '2110', 'nombre': 'Arroz con Leche Clásico 180g', 'costo': 450, 'venta': 700, 'categoria': 'Arroz con Leche'},
    {'codigo_producto': '2111', 'nombre': 'Arroz con Leche con Canela 180g', 'costo': 460, 'venta': 710, 'categoria': 'Arroz con Leche'},
    {'codigo_producto': '2109', 'nombre': 'Arroz con Leche con Dulce de Leche 180g', 'costo': 470, 'venta': 720, 'categoria': 'Arroz con Leche'},
    {'codigo_producto': '313', 'nombre': 'Arroz con Leche con Chocolate 180g', 'costo': 480, 'venta': 730, 'categoria': 'Arroz con Leche'},
    {'codigo_producto': '82', 'nombre': 'Arroz con Leche Descremado 180g', 'costo': 440, 'venta': 690, 'categoria': 'Arroz con Leche'},
    
    # QUESOS UNTABLES SABORIZADOS (6)
    {'codigo_producto': '2078', 'nombre': 'Châtel Untable Clásico 180g', 'costo': 850, 'venta': 1300, 'categoria': 'Quesos Untables'},
    {'codigo_producto': '2079', 'nombre': 'Châtel Untable con Jamón 180g', 'costo': 880, 'venta': 1350, 'categoria': 'Quesos Untables'},
    {'codigo_producto': '2094', 'nombre': 'Châtel Untable con Salame 180g', 'costo': 880, 'venta': 1350, 'categoria': 'Quesos Untables'},
    {'codigo_producto': '2169', 'nombre': 'Châtel Untable con Siboulette 180g', 'costo': 870, 'venta': 1340, 'categoria': 'Quesos Untables'},
    {'codigo_producto': '2108', 'nombre': 'Châtel Untable Cheddar 180g', 'costo': 900, 'venta': 1380, 'categoria': 'Quesos Untables'},
    {'codigo_producto': '2118', 'nombre': 'Châtel Untable Descremado 180g', 'costo': 820, 'venta': 1280, 'categoria': 'Quesos Untables'},
    
    # QUESOS UNTABLES BLANCOS & QUESOS CREMA (6)
    {'codigo_producto': '2144', 'nombre': 'Queso Blanco Clásico 290g', 'costo': 950, 'venta': 1450, 'categoria': 'Quesos Untables Blancos'},
    {'codigo_producto': '2145', 'nombre': 'Queso Blanco Light 290g', 'costo': 920, 'venta': 1420, 'categoria': 'Quesos Untables Blancos'},
    {'codigo_producto': '1627', 'nombre': 'Queso Crema Clásico 190g', 'costo': 800, 'venta': 1250, 'categoria': 'Quesos Untables Blancos'},
    {'codigo_producto': '1760', 'nombre': 'Queso Crema Clásico 280g', 'costo': 950, 'venta': 1450, 'categoria': 'Quesos Untables Blancos'},
    {'codigo_producto': '1628', 'nombre': 'Queso Crema Descremado 190g', 'costo': 780, 'venta': 1220, 'categoria': 'Quesos Untables Blancos'},
    {'codigo_producto': '1782', 'nombre': 'Queso Crema Descremado 280g', 'costo': 920, 'venta': 1420, 'categoria': 'Quesos Untables Blancos'},
    
    # MASCARPONE (1)
    {'codigo_producto': '225', 'nombre': 'Queso Mascarpone 200g', 'costo': 1100, 'venta': 1700, 'categoria': 'Mascarpone'},
    
    # CREMAS Y RICOTTAS (5)
    {'codigo_producto': '1999', 'nombre': 'Crema de Leche Doble 200cc', 'costo': 700, 'venta': 1100, 'categoria': 'Cremas'},
    {'codigo_producto': '2068', 'nombre': 'Crema de Leche Doble 350cc', 'costo': 850, 'venta': 1300, 'categoria': 'Cremas'},
    {'codigo_producto': '269', 'nombre': 'Crema Chantilly Spray 250ml', 'costo': 900, 'venta': 1400, 'categoria': 'Cremas'},
    {'codigo_producto': '2141', 'nombre': 'Ricotta de Leche Entera 290g', 'costo': 800, 'venta': 1250, 'categoria': 'Ricottas'},
    {'codigo_producto': '2142', 'nombre': 'Ricotta de Leche Light 290g', 'costo': 780, 'venta': 1220, 'categoria': 'Ricottas'},
    
    # DULCE DE LECHE (2)
    {'codigo_producto': '1313', 'nombre': 'Dulce de Leche Clásico 200g', 'costo': 550, 'venta': 850, 'categoria': 'Dulce de Leche'},
    {'codigo_producto': '31', 'nombre': 'Dulce de Leche Clásico 400g', 'costo': 750, 'venta': 1150, 'categoria': 'Dulce de Leche'},
    
    # QUESOS DUROS (2)
    {'codigo_producto': '17', 'nombre': 'Reggianito Horma 7kg', 'costo': 15000, 'venta': 22000, 'categoria': 'Quesos Duros'},
    {'codigo_producto': '208', 'nombre': 'Reggianito Porción 280g', 'costo': 1800, 'venta': 2800, 'categoria': 'Quesos Duros'},
    
    # QUESOS SEMI DUROS (10)
    {'codigo_producto': '1096', 'nombre': 'Holanda Horma 4.2kg', 'costo': 9000, 'venta': 13500, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '142', 'nombre': 'Holanda Porción 440g', 'costo': 1900, 'venta': 2900, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '1099', 'nombre': 'Pategrás Horma 4.2kg', 'costo': 9200, 'venta': 13800, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '1095', 'nombre': 'Criollo Horma 4.2kg', 'costo': 8500, 'venta': 12800, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '195', 'nombre': 'Criollo Horma Obsequio 4.2kg', 'costo': 7500, 'venta': 11500, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '257', 'nombre': 'Criollo Porción 380g', 'costo': 1700, 'venta': 2600, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '104', 'nombre': 'Fontina Horma 9kg', 'costo': 12000, 'venta': 18000, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '211', 'nombre': 'Azul Horma 1.5kg', 'costo': 3000, 'venta': 4500, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '1098', 'nombre': 'Danbo Horma 4.2kg', 'costo': 8800, 'venta': 13200, 'categoria': 'Quesos Semi Duros'},
    {'codigo_producto': '1097', 'nombre': 'Mozzarella Horma 4.2kg', 'costo': 9500, 'venta': 14200, 'categoria': 'Quesos Semi Duros'},
    
    # QUESOS BLANDOS (9)
    {'codigo_producto': '9', 'nombre': 'Cremoso Horma 4.1kg', 'costo': 8000, 'venta': 12000, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '1245', 'nombre': 'Cremoso Porción 520g', 'costo': 2000, 'venta': 3000, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '170', 'nombre': 'Cremoso Porción 520g (24u)', 'costo': 1900, 'venta': 2900, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '1093', 'nombre': 'Por Salut Horma 3.9kg', 'costo': 7800, 'venta': 11700, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '1246', 'nombre': 'Por Salut Porción 480g', 'costo': 1900, 'venta': 2850, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '171', 'nombre': 'Por Salut Porción 480g (24u)', 'costo': 1800, 'venta': 2750, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '1094', 'nombre': 'Por Salut Light Horma 3.5kg', 'costo': 7600, 'venta': 11400, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '1100', 'nombre': 'Por Salut Light Porción 430g', 'costo': 1850, 'venta': 2800, 'categoria': 'Quesos Blandos'},
    {'codigo_producto': '1101', 'nombre': 'Por Salut Light Sin Sal Porción 430g', 'costo': 1850, 'venta': 2800, 'categoria': 'Quesos Blandos'},
    
    # QUESOS RALLADOS (2)
    {'codigo_producto': '180', 'nombre': 'Queso Rallado 40g', 'costo': 400, 'venta': 650, 'categoria': 'Quesos Rallados'},
    {'codigo_producto': '2146', 'nombre': 'Queso Rallado 120g', 'costo': 750, 'venta': 1150, 'categoria': 'Quesos Rallados'},
]

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def fecha_aleatoria():
    """Genera una fecha aleatoria dentro del período"""
    days = (FECHA_FIN - FECHA_INICIO).days
    return FECHA_INICIO + timedelta(days=random.randint(0, days))

def generar_cuit():
    base = str(random.randint(20000000000, 30999999999))
    return f"{base[:2]}-{base[2:10]}-{base[10]}"

def generar_telefono(provincia):
    prefijos = {
        'Mendoza': '0261',
        'San Juan': '0264',
        'San Luis': '0266'
    }
    prefijo = prefijos.get(provincia, '0261')
    return f"{prefijo} {random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generar_nombre_negocio(localidad, index):
    base = random.choice(NOMBRES_NEGOCIOS)
    return f"{base} {localidad[:3]}{index:02d}" if random.choice([True, False]) else base

# ============================================================
# FUNCIONES DE CARGA
# ============================================================

def inicializar_si_es_necesario():
    print("📁 Verificando base de datos...")
    try:
        db = obtener_conexion()
        cur = db.cursor()
        cur.execute("SELECT 1 FROM parametros LIMIT 1")
        db.close()
        print("   ✅ Base de datos ya existe")
    except sqlite3.OperationalError:
        print("   ⚠️ Base de datos no encontrada. Creando...")
        inicializar_bd()
        print("   ✅ Base de datos creada")

def limpiar_base():
    print("🧹 Limpiando base de datos...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("PRAGMA foreign_keys = OFF")
    
    tablas = ['factura_detalle', 'nota_venta_detalle', 'cheques', 'cobros', 
              'cuenta_corriente_movimientos', 'facturas', 'pedidos_procesados',
              'notas_venta', 'lotes', 'productos', 'categorias', 'clientes', 
              'preventistas', 'usuarios', 'parametros']
    
    for tabla in tablas:
        try:
            cur.execute(f"DELETE FROM {tabla}")
            print(f"   ✅ Limpiada tabla {tabla}")
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ No se pudo limpiar {tabla}: {e}")
        except Exception as e:
            print(f"   ⚠️ Error en {tabla}: {e}")
    
    cur.execute("PRAGMA foreign_keys = ON")
    db.commit()
    db.close()
    print("   ✅ Base de datos limpiada")

def cargar_parametros():
    print("\n📝 Cargando parámetros de la empresa...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("DELETE FROM parametros WHERE id = 1")
    cur.execute("""
        INSERT INTO parametros (
            id, moneda, nombre_distribuidora, direccion, telefono1, telefono2,
            whatsapp, email, encabezado_factura, encabezado_reporte,
            tasa_municipal_porcentaje, punto_venta, ultimo_numero_factura,
            calle, numero, localidad, provincia, pais, latitud, longitud, escala_visual
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1.0)
    """, (
        PARAMETROS['moneda'], PARAMETROS['nombre_distribuidora'], PARAMETROS['direccion'],
        PARAMETROS['telefono1'], PARAMETROS['telefono2'], PARAMETROS['whatsapp'],
        PARAMETROS['email'], PARAMETROS['encabezado_factura'], PARAMETROS['encabezado_reporte'],
        PARAMETROS['tasa_municipal_porcentaje'], PARAMETROS['punto_venta'], PARAMETROS['ultimo_numero_factura'],
        PARAMETROS['calle'], PARAMETROS['numero'], PARAMETROS['localidad'], PARAMETROS['provincia'],
        PARAMETROS['pais'], PARAMETROS['latitud'], PARAMETROS['longitud']
    ))
    db.commit()
    db.close()
    print("   ✅ Parámetros cargados")

def cargar_categorias():
    print("\n📂 Cargando categorías...")
    db = obtener_conexion()
    cur = db.cursor()
    
    categorias = sorted(set([p['categoria'] for p in PRODUCTOS_TREGAR]))
    
    categoria_map = {}
    for categoria in categorias:
        categoria_id = str(uuid.uuid4())
        cur.execute("INSERT OR IGNORE INTO categorias (id, nombre) VALUES (?, ?)", (categoria_id, categoria))
        cur.execute("SELECT id FROM categorias WHERE nombre = ?", (categoria,))
        row = cur.fetchone()
        if row:
            categoria_map[categoria] = row[0]
    
    db.commit()
    print(f"   ✅ {len(categoria_map)} categorías cargadas")
    db.close()
    return categoria_map

def cargar_preventistas():
    print("\n👥 Cargando preventistas...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("DELETE FROM preventistas")
    
    for p in PREVENTISTAS:
        preventista_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO preventistas (
                id, nombre, apellido, legajo, telefono, email, zona, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            preventista_id,
            p['nombre'],
            p['apellido'],
            p['legajo'],
            p['telefono'],
            p['email'],
            p['zona']
        ))
    
    db.commit()
    print(f"   ✅ {len(PREVENTISTAS)} preventistas cargados")
    db.close()

def cargar_usuarios():
    print("\n🔐 Cargando usuarios...")
    db = obtener_conexion()
    cur = db.cursor()
    
    import hashlib
    def hash_password(pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()
    
    cur.execute("DELETE FROM usuarios WHERE username != 'admin'")
    
    cur.execute("SELECT id FROM usuarios WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO usuarios (id, username, password_hash, rol, activo) 
            VALUES ('00000000-0000-0000-0000-000000000001', 'admin', ?, 'admin', 1)
        """, (hash_password('admin'),))
    
    cur.execute("SELECT id FROM preventistas")
    preventistas = cur.fetchall()
    
    for i, p in enumerate(preventistas, 1):
        usuario_id = str(uuid.uuid4())
        try:
            cur.execute("""
                INSERT OR REPLACE INTO usuarios (id, username, password_hash, rol, preventista_id, activo)
                VALUES (?, ?, ?, 'preventista', ?, 1)
            """, (usuario_id, f"prev{i:03d}", hash_password(f"prev{i:03d}"), p['id']))
        except Exception as e:
            print(f"   ⚠️ Error al crear usuario prev{i:03d}: {e}")
    
    db.commit()
    print(f"   ✅ Usuarios cargados (1 admin + {len(preventistas)} preventistas)")
    db.close()

def cargar_clientes():
    print("\n🏢 Cargando 700 clientes (100 por preventista)...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("SELECT id, nombre, apellido, zona FROM preventistas WHERE activo = 1")
    preventistas = cur.fetchall()
    
    total = 0
    
    for preventista in preventistas:
        preventista_id = preventista['id']
        zona = preventista['zona']
        
        # Obtener localidades de esta zona
        localidades_zona = []
        for loc, info in LOCALIDADES.items():
            if zona == 'Valle de Uco' and info['provincia'] == 'Mendoza' and loc in ['Tunuyán', 'San Carlos', 'Tupungato', 'La Consulta', 'Villa Seca', 'Los Árboles']:
                localidades_zona.append(loc)
            elif zona == 'Centro Mendoza' and info['provincia'] == 'Mendoza' and loc in ['Mendoza Capital', 'Godoy Cruz', 'Las Heras', 'Guaymallén', 'Maipú']:
                localidades_zona.append(loc)
            elif zona == 'Sur Mendoza' and info['provincia'] == 'Mendoza' and loc in ['San Rafael', 'General Alvear', 'Malargüe', 'El Nihuil', 'La Paz', 'Villa Atuel']:
                localidades_zona.append(loc)
            elif zona == 'Este Mendoza' and info['provincia'] == 'Mendoza' and loc in ['Junín', 'Rivadavia', 'San Martín', 'Santa Rosa', 'La Dormida', 'Monte Comán']:
                localidades_zona.append(loc)
            elif zona == 'San Juan' and info['provincia'] == 'San Juan':
                localidades_zona.append(loc)
            elif zona == 'San Luis' and info['provincia'] == 'San Luis':
                localidades_zona.append(loc)
        
        if not localidades_zona:
            print(f"   ⚠️ No hay localidades para {preventista['nombre']} {preventista['apellido']} (Zona: {zona})")
            continue
        
        print(f"   📍 {preventista['nombre']} {preventista['apellido']} - {zona} ({len(localidades_zona)} localidades)")
        
        # Distribuir 100 clientes entre las localidades
        clientes_por_localidad = {}
        for loc in localidades_zona:
            clientes_por_localidad[loc] = random.randint(10, 20)
        
        total_asignado = sum(clientes_por_localidad.values())
        if total_asignado != CANTIDAD_CLIENTES_POR_PREVENTISTA:
            diff = CANTIDAD_CLIENTES_POR_PREVENTISTA - total_asignado
            first_loc = list(clientes_por_localidad.keys())[0]
            clientes_por_localidad[first_loc] += diff
        
        for localidad, cantidad in clientes_por_localidad.items():
            info = LOCALIDADES[localidad]
            lat_base, lon_base = info['lat'], info['lon']
            calles = CALLES.get(localidad, ['Principal', 'Belgrano', 'Mitre', 'Rivadavia'])
            provincia = info['provincia']
            
            for i in range(cantidad):
                nombre = generar_nombre_negocio(localidad, i)
                
                calle = random.choice(calles)
                numero = random.randint(100, 9999)
                
                lat = lat_base + random.uniform(-0.015, 0.015)
                lon = lon_base + random.uniform(-0.015, 0.015)
                
                cliente_id = str(uuid.uuid4())
                
                try:
                    cur.execute("""
                        INSERT INTO clientes (
                            id, razon_social, cuit, condicion_iva, domicilio, telefono, whatsapp, email,
                            aplica_tasa_municipal, limite_credito, calle, numero, localidad, provincia,
                            latitud, longitud, preventista_id, activo, saldo_cuenta_corriente
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
                    """, (
                        cliente_id, nombre, generar_cuit(), random.choice(['RI', 'M', 'CF']),
                        f"{calle} {numero}, {localidad}, {provincia}",
                        generar_telefono(provincia),
                        generar_telefono(provincia) if random.choice([True, False]) else None,
                        f"ventas_{localidad[:3]}_{i:03d}@gmail.com",
                        1 if random.choice([True, False]) else 0,
                        random.choice([0, 50000, 100000, 200000, 500000, 1000000]),
                        calle, str(numero), localidad, provincia,
                        lat, lon, preventista_id
                    ))
                    total += 1
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️ Error al insertar cliente: {e}")
                    continue
        
        db.commit()
        print(f"      ✅ {total} clientes cargados hasta ahora")
    
    db.close()
    print(f"\n   ✅ TOTAL: {total} clientes cargados")
    return total

def cargar_productos(categoria_map):
    print("\n📦 Cargando productos (stock: 100,000 unidades)...")
    db = obtener_conexion()
    cur = db.cursor()
    
    total = 0
    fecha_vencimiento = (date.today() + timedelta(days=365)).isoformat()
    
    for producto in PRODUCTOS_TREGAR:
        codigo = producto['codigo_producto']
        nombre = producto['nombre']
        precio_costo = producto['costo']
        precio_venta = producto['venta']
        categoria_nombre = producto['categoria']
        
        categoria_id = categoria_map.get(categoria_nombre)
        if categoria_id is None:
            print(f"   ⚠️ Categoría no encontrada: {categoria_nombre}")
            continue
        
        stock_actual = 100000
        stock_critico = random.randint(100, 500)
        
        producto_id = str(uuid.uuid4())
        try:
            cur.execute("""
                INSERT INTO productos (
                    id, codigo_producto, descripcion, precio_costo, precio_venta,
                    stock_actual, stock_critico, unidad_medida, categoria_id, destacado, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                producto_id, codigo, nombre, precio_costo, precio_venta,
                stock_actual, stock_critico,
                random.choice(['unidad', 'kg', 'l', 'paquete', 'caja']),
                categoria_id, random.choice([0, 0, 0, 1])
            ))
            
            lote_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO lotes (id, producto_id, codigo_producto, numero_lote, fecha_vencimiento,
                                   cantidad_inicial, cantidad_actual, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (lote_id, producto_id, codigo, f"LOTE-{codigo}-001", fecha_vencimiento, stock_actual, stock_actual))
            
            total += 1
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al insertar producto {codigo}: {e}")
            continue
        
        if total % 50 == 0:
            db.commit()
            print(f"   ... {total} productos procesados")
    
    db.commit()
    print(f"   ✅ {total} productos cargados (stock: 100,000 unidades)")
    db.close()

# ============================================================
# FUNCIONES DE VENTAS - NOTAS Y FACTURAS
# ============================================================

def cargar_notas_venta():
    print("\n📋 Cargando notas de venta (500 notas)...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("SELECT id FROM clientes")
    clientes = [row['id'] for row in cur.fetchall()]
    cur.execute("SELECT id FROM preventistas")
    preventistas = [row['id'] for row in cur.fetchall()]
    cur.execute("SELECT id, codigo_producto, precio_venta FROM productos WHERE activo = 1")
    productos = [dict(row) for row in cur.fetchall()]
    
    if not productos:
        print("   ⚠️ No hay productos para cargar notas de venta")
        db.close()
        return
    
    total = 0
    for i in range(500):
        fecha = fecha_aleatoria()
        cliente_id = random.choice(clientes) if clientes else None
        preventista_id = random.choice(preventistas) if preventistas else None
        numero_nota = f"NOTA-{fecha.strftime('%Y%m')}-{i:04d}"
        
        nota_id = str(uuid.uuid4())
        try:
            cur.execute("""
                INSERT INTO notas_venta (id, preventista_id, cliente_id, fecha, numero_nota, total, estado, procesado_central)
                VALUES (?, ?, ?, ?, ?, 0, 'PROCESADA', 1)
            """, (nota_id, preventista_id, cliente_id, fecha.isoformat(), numero_nota))
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al insertar nota de venta: {e}")
            continue
        
        total_nota = 0
        
        for _ in range(random.randint(1, 8)):
            producto = random.choice(productos)
            cantidad = random.randint(1, 10)
            subtotal = cantidad * producto['precio_venta']
            total_nota += subtotal
            
            detalle_id = str(uuid.uuid4())
            try:
                cur.execute("""
                    INSERT INTO nota_venta_detalle (id, nota_venta_id, producto_id, codigo_producto, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (detalle_id, nota_id, producto['id'], producto['codigo_producto'], cantidad, producto['precio_venta']))
            except sqlite3.OperationalError as e:
                print(f"   ⚠️ Error al insertar detalle de nota: {e}")
                continue
        
        try:
            cur.execute("UPDATE notas_venta SET total = ? WHERE id = ?", (total_nota, nota_id))
            total += 1
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al actualizar total de nota: {e}")
            continue
        
        if total % 100 == 0:
            db.commit()
            print(f"   ... {total} notas cargadas")
    
    db.commit()
    print(f"   ✅ {total} notas de venta cargadas (TODAS procesadas = 1)")
    db.close()

def cargar_facturas():
    print("\n💰 Cargando facturas (300 facturas)...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("SELECT id, razon_social, condicion_iva, saldo_cuenta_corriente FROM clientes WHERE activo = 1")
    clientes = [dict(row) for row in cur.fetchall()]
    cur.execute("SELECT id, codigo_producto, precio_venta FROM productos WHERE activo = 1")
    productos = [dict(row) for row in cur.fetchall()]
    cur.execute("SELECT id FROM preventistas")
    preventistas = [row['id'] for row in cur.fetchall()]
    
    if not productos:
        print("   ⚠️ No hay productos para cargar facturas")
        db.close()
        return
    
    cur.execute("SELECT ultimo_numero_factura FROM parametros WHERE id = 1")
    row = cur.fetchone()
    ultimo_numero = row['ultimo_numero_factura'] if row else 1
    
    total = 0
    
    for _ in range(300):
        fecha = fecha_aleatoria()
        cliente = random.choice(clientes)
        preventista_id = random.choice(preventistas) if preventistas else None
        
        subtotal = 0
        items = []
        for _ in range(random.randint(1, 10)):
            producto = random.choice(productos)
            cantidad = random.randint(1, 10)
            items.append((producto['id'], cantidad, producto['precio_venta']))
            subtotal += cantidad * producto['precio_venta']
        
        iva = subtotal * 0.21 if cliente['condicion_iva'] == 'RI' else 0
        total_factura = subtotal + iva
        
        numero_factura = f"0001-{ultimo_numero:08d}"
        ultimo_numero += 1
        
        saldo_anterior = cliente['saldo_cuenta_corriente']
        
        factura_id = str(uuid.uuid4())
        try:
            cur.execute("""
                INSERT INTO facturas (id, cliente_id, preventista_id, tipo_comprobante, numero_factura,
                    fecha, subtotal, iva, total, estado, saldo_anterior_cliente)
                VALUES (?, ?, ?, 'B', ?, ?, ?, ?, ?, 'EMITIDA', ?)
            """, (factura_id, cliente['id'], preventista_id, numero_factura,
                  fecha.isoformat(), subtotal, iva, total_factura, saldo_anterior))
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al insertar factura: {e}")
            continue
        
        for prod_id, cant, precio in items:
            detalle_id = str(uuid.uuid4())
            try:
                cur.execute("""
                    INSERT INTO factura_detalle (id, factura_id, producto_id, codigo_producto, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (detalle_id, factura_id, prod_id, producto['codigo_producto'], cant, precio))
            except sqlite3.OperationalError as e:
                print(f"   ⚠️ Error al insertar detalle de factura: {e}")
                continue
        
        nuevo_saldo = cliente['saldo_cuenta_corriente'] + total_factura
        try:
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?", (nuevo_saldo, cliente['id']))
            cliente['saldo_cuenta_corriente'] = nuevo_saldo
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al actualizar saldo: {e}")
            continue
        
        mov_id = str(uuid.uuid4())
        try:
            cur.execute("""
                INSERT INTO cuenta_corriente_movimientos (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe, saldo_resultante)
                VALUES (?, ?, ?, 'FACTURA', ?, ?, ?)
            """, (mov_id, cliente['id'], fecha.isoformat(), factura_id, total_factura, nuevo_saldo))
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al insertar movimiento: {e}")
            continue
        
        total += 1
        if total % 50 == 0:
            db.commit()
            print(f"   ... {total} facturas cargadas")
    
    try:
        cur.execute("UPDATE parametros SET ultimo_numero_factura = ? WHERE id = 1", (ultimo_numero,))
        db.commit()
    except sqlite3.OperationalError as e:
        print(f"   ⚠️ Error al actualizar número de factura: {e}")
    
    print(f"   ✅ {total} facturas cargadas")
    db.close()

def cargar_cobros():
    print("\n💵 Cargando cobros...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("SELECT id, saldo_cuenta_corriente FROM clientes WHERE saldo_cuenta_corriente > 0")
    clientes = [dict(row) for row in cur.fetchall()]
    
    if not clientes:
        print("   ⚠️ No hay clientes con deuda para cargar cobros")
        db.close()
        return
    
    medios = ['EFECTIVO', 'TRANSFERENCIA', 'CHEQUE', 'DEBITO', 'CREDITO']
    total = 0
    
    for cliente in clientes:
        saldo = cliente['saldo_cuenta_corriente']
        
        if saldo > 0 and random.random() < 0.6:
            porcentaje_pago = random.uniform(0.3, 1.0)
            importe = round(saldo * porcentaje_pago, 2)
            
            if importe > 0:
                nuevo_saldo = saldo - importe
                
                cobro_id = str(uuid.uuid4())
                try:
                    cur.execute("""
                        INSERT INTO cobros (id, cliente_id, fecha, importe, medio_pago, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (cobro_id, cliente['id'], fecha_aleatoria().isoformat(), importe, random.choice(medios), "Cobro registrado"))
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️ Error al insertar cobro: {e}")
                    continue
                
                try:
                    cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?", (nuevo_saldo, cliente['id']))
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️ Error al actualizar saldo: {e}")
                    continue
                
                mov_id = str(uuid.uuid4())
                try:
                    cur.execute("""
                        INSERT INTO cuenta_corriente_movimientos (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe, saldo_resultante)
                        VALUES (?, ?, ?, 'COBRO', ?, ?, ?)
                    """, (mov_id, cliente['id'], fecha_aleatoria().isoformat(), cobro_id, -importe, nuevo_saldo))
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️ Error al insertar movimiento: {e}")
                    continue
                
                total += 1
                if total % 50 == 0:
                    db.commit()
    
    db.commit()
    print(f"   ✅ {total} cobros cargados")
    db.close()

def cargar_cheques():
    print("\n🏦 Cargando cheques...")
    db = obtener_conexion()
    cur = db.cursor()
    
    cur.execute("SELECT id FROM clientes")
    clientes = [row['id'] for row in cur.fetchall()]
    cur.execute("SELECT id FROM cobros")
    cobros = [row['id'] for row in cur.fetchall()]
    
    if not clientes or not cobros:
        print("   ⚠️ No hay clientes o cobros para cargar cheques")
        db.close()
        return
    
    bancos = ['Banco Nación', 'Banco Provincia', 'Banco Galicia', 'Banco Santander', 'BBVA']
    estados = ['EN_CARTERA', 'VENDIDO', 'ACREDITADO', 'DEPOSITADO']
    total = 0
    
    for _ in range(50):
        if not cobros:
            break
        
        fecha_emision = fecha_aleatoria()
        fecha_vencimiento = fecha_emision + timedelta(days=random.randint(30, 90))
        estado = random.choice(estados)
        
        cheque_id = str(uuid.uuid4())
        try:
            cur.execute("""
                INSERT INTO cheques (id, cobro_id, cliente_id, banco, numero_cheque,
                    fecha_emision, fecha_vencimiento, importe, estado, vendido_a, fecha_acreditacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cheque_id, random.choice(cobros), random.choice(clientes),
                random.choice(bancos), str(random.randint(10000000, 99999999)),
                fecha_emision.isoformat(), fecha_vencimiento.isoformat(),
                round(random.uniform(5000, 50000), 2),
                estado,
                f"Comprador {random.randint(1, 100)}" if estado == 'VENDIDO' else None,
                fecha_vencimiento.isoformat() if estado == 'ACREDITADO' else None
            ))
            total += 1
        except sqlite3.OperationalError as e:
            print(f"   ⚠️ Error al insertar cheque: {e}")
            continue
    
    db.commit()
    print(f"   ✅ {total} cheques cargados")
    db.close()

def actualizar_saldos():
    print("\n🔄 Actualizando saldos de cuenta corriente...")
    db = obtener_conexion()
    cur = db.cursor()
    
    try:
        cur.execute("""
            UPDATE clientes SET saldo_cuenta_corriente = (
                SELECT COALESCE(SUM(CASE WHEN tipo_movimiento = 'FACTURA' THEN importe ELSE -importe END), 0)
                FROM cuenta_corriente_movimientos
                WHERE cliente_id = clientes.id
            )
        """)
        db.commit()
        print("   ✅ Saldos actualizados correctamente")
    except sqlite3.OperationalError as e:
        print(f"   ⚠️ Error al actualizar saldos: {e}")
    
    db.close()

def main():
    print("=" * 70)
    print("   GENERANDO DATOS MASIVOS - CON VENTAS")
    print("   COMPATIBLE CON script_creacion.sql (UUID)")
    print(f"   PERÍODO: {FECHA_INICIO.strftime('%d-%m-%Y')} a {FECHA_FIN.strftime('%d-%m-%Y')}")
    print("   TOTAL: 700 CLIENTES (100 por preventista)")
    print("   VENTAS: Notas (500) + Facturas (300) + Cobros + Cheques")
    print("=" * 70)
    
    inicializar_si_es_necesario()
    
    print(f"\n📅 Período: {FECHA_INICIO} a {FECHA_FIN} (6 meses)")
    print(f"👥 Preventistas: {len(PREVENTISTAS)}")
    print(f"📦 Productos totales: {len(PRODUCTOS_TREGAR)}")
    print(f"🏢 Clientes: {TOTAL_CLIENTES}")
    print("=" * 70)
    
    try:
        limpiar_base()
        cargar_parametros()
        cargar_preventistas()
        cargar_usuarios()
        cargar_clientes()
        
        categoria_map = cargar_categorias()
        cargar_productos(categoria_map)
        
        # VENTAS
        cargar_notas_venta()
        cargar_facturas()
        cargar_cobros()
        cargar_cheques()
        
        actualizar_saldos()
        
        print("\n" + "=" * 70)
        print("   ✅ DATOS GENERADOS EXITOSAMENTE")
        print("=" * 70)
        
        db = obtener_conexion()
        cur = db.cursor()
        
        try:
            cur.execute("SELECT COUNT(*) FROM clientes")
            print(f"\n📊 ESTADÍSTICAS FINALES:")
            print(f"   👥 Clientes: {cur.fetchone()[0]}")
        except:
            print("   👥 Clientes: Error al contar")
        
        try:
            cur.execute("SELECT COUNT(*) FROM productos")
            print(f"   📦 Productos: {cur.fetchone()[0]}")
        except:
            print("   📦 Productos: Error al contar")
        
        try:
            cur.execute("SELECT COUNT(*) FROM notas_venta")
            print(f"   📋 Notas de venta: {cur.fetchone()[0]}")
        except:
            print("   📋 Notas de venta: Error al contar")
        
        try:
            cur.execute("SELECT COUNT(*) FROM facturas")
            print(f"   💰 Facturas: {cur.fetchone()[0]}")
        except:
            print("   💰 Facturas: Error al contar")
        
        try:
            cur.execute("SELECT COUNT(*) FROM cobros")
            print(f"   💵 Cobros: {cur.fetchone()[0]}")
        except:
            print("   💵 Cobros: Error al contar")
        
        try:
            cur.execute("SELECT COUNT(*) FROM cheques")
            print(f"   🏦 Cheques: {cur.fetchone()[0]}")
        except:
            print("   🏦 Cheques: Error al contar")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()