"""
Código Crítico - Tercer Semestre Año 2026
Generador de logo placeholder para la distribuidora.
Ejecute este script una vez para crear el archivo 'logo.png' dentro de la carpeta assets/.
Requiere la biblioteca Pillow: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

def crear_logo(nombre_empresa: str = "Distribuidora", ruta_salida: str = "logo.png"):
    """
    Crea una imagen PNG simple a modo de logo corporativo.
    :param nombre_empresa: Texto que se mostrará en el logo.
    :param ruta_salida: Ruta donde se guardará el PNG generado.
    """
    # Dimensiones del logo
    ancho, alto = 400, 120

    # Crear imagen con fondo blanco
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Dibujar un rectángulo decorativo
    draw.rectangle([10, 10, ancho-10, alto-10], outline=(30, 60, 120), width=3)

    # Intentar usar una fuente TrueType, si no está disponible usar la por defecto
    try:
        fuente = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        try:
            fuente = ImageFont.truetype("LiberationSans-Regular.ttf", 40)
        except IOError:
            fuente = ImageFont.load_default()

    # Texto principal centrado
    try:
        # Pillow >= 8.0.0 admite anchor
        draw.text((ancho//2, alto//2), nombre_empresa, fill=(30, 60, 120),
                  font=fuente, anchor="mm")
    except TypeError:
        # Fallback para versiones anteriores
        texto_ancho, texto_alto = draw.textsize(nombre_empresa, font=fuente)
        draw.text(((ancho - texto_ancho)/2, (alto - texto_alto)/2),
                  nombre_empresa, fill=(30, 60, 120), font=fuente)

    # Guardar la imagen
    img.save(ruta_salida, "PNG")
    print(f"Logo generado exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    # Ubicación de salida dentro de la misma carpeta assets
    ruta_destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    crear_logo(nombre_empresa="Distribuidora", ruta_salida=ruta_destino)