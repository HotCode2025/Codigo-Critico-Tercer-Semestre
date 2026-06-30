"""
Código Crítico - Tercer Semestre Año 2026
Utilidad para geocodificar direcciones usando Nominatim (OpenStreetMap).
"""

import requests
import time
import os
import json
from typing import Tuple, Optional

# Archivo de caché para evitar muchas consultas repetidas
CACHE_FILE = "geocache.json"

def cargar_cache():
    """Carga el caché de geolocalización"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_cache(cache):
    """Guarda el caché de geolocalización"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except:
        pass

def obtener_coordenadas(calle: str, numero: str, localidad: str, provincia: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Convierte una dirección en coordenadas (latitud, longitud).
    Retorna (lat, lon) o (None, None) si no se pudo geocodificar.
    """
    if not calle or not localidad:
        print(f"⚠️ Dirección incompleta: calle='{calle}', localidad='{localidad}'")
        return None, None

    # Construir la dirección completa
    direccion = f"{calle} {numero or ''}, {localidad}, {provincia or 'Argentina'}, Argentina"
    direccion = direccion.replace("  ", " ").strip()
    
    # Verificar caché
    cache = cargar_cache()
    if direccion in cache:
        print(f"📦 Usando caché para: {direccion[:50]}...")
        lat, lon = cache[direccion]
        return lat, lon
    
    # URL de Nominatim
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": direccion,
        "format": "json",
        "limit": 1,
        "addressdetails": 0
    }
    headers = {
        "User-Agent": "SistemaDistribucionLogistica/1.0"
    }

    try:
        time.sleep(1.2)  # Respetar límite de Nominatim (1 request por segundo)
        print(f"🌐 Geocodificando: {direccion[:80]}...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            # Guardar en caché
            cache[direccion] = (lat, lon)
            guardar_cache(cache)
            print(f"✅ Geocodificado: ({lat:.4f}, {lon:.4f})")
            return lat, lon
        else:
            print(f"❌ No se encontró: {direccion[:80]}")
            return None, None
    except Exception as e:
        print(f"⚠️ Error al geocodificar: {e}")
        return None, None


def geocodificar_direccion_simple(direccion: str) -> Tuple[Optional[float], Optional[float]]:
    """Geocodifica una dirección completa en una sola cadena."""
    if not direccion:
        return None, None
    
    # Verificar caché
    cache = cargar_cache()
    if direccion in cache:
        lat, lon = cache[direccion]
        return lat, lon
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": direccion, "format": "json", "limit": 1}
    headers = {"User-Agent": "SistemaDistribucionLogistica/1.0"}
    
    try:
        time.sleep(1.2)
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            cache[direccion] = (lat, lon)
            guardar_cache(cache)
            return lat, lon
        return None, None
    except:
        return None, None