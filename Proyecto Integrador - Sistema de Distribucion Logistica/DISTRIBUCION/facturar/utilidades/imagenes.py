"""
Código Crítico - Tercer Semestre Año 2026
Utilidad para redimensionar imágenes del catálogo.
"""
from PIL import Image
import os

def redimensionar_para_catalogo(ruta_original: str, ruta_destino: str,
                                ancho_max: int = 400, alto_max: int = 400) -> tuple:
    """
    Reduce una imagen manteniendo la proporción y la guarda en la ruta destino.
    Retorna (True, None) si fue exitoso, o (False, mensaje_error) si falló.
    """
    try:
        if not os.path.exists(ruta_original):
            return False, f"No se encuentra el archivo origen:\n{ruta_original}"

        with Image.open(ruta_original) as img:
            # Si la imagen tiene transparencia (RGBA) o paleta (P), la convertimos a RGB
            # para poder guardarla como JPEG sin errores.
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail((ancho_max, alto_max), Image.LANCZOS)
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            img.save(ruta_destino, optimize=True, quality=85)

        return True, None
    except Exception as e:
        return False, f"Error al procesar la imagen:\n{str(e)}"