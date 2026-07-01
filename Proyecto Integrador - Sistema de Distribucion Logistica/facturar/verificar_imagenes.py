# verificar_imagenes.py
"""
Código Crítico - Tercer Semestre - Año 2026
Script para verificar imágenes sueltas y productos sin imagen
============================================================
📌 USO: python verificar_imagenes.py
"""

import os
import sqlite3

BD_PATH = "distribuidora.db"
CARPETA_IMAGENES = "imagenes_productos"
EXTENSIONES = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']

def obtener_productos_bd():
    """Obtiene todos los códigos de productos de la BD"""
    conn = sqlite3.connect(BD_PATH)
    cur = conn.cursor()
    cur.execute("SELECT codigo_producto, descripcion FROM productos")
    productos = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()
    return productos

def obtener_imagenes_carpeta():
    """Obtiene todos los códigos de imágenes en la carpeta"""
    imagenes = set()
    if not os.path.exists(CARPETA_IMAGENES):
        return imagenes
    
    for archivo in os.listdir(CARPETA_IMAGENES):
        nombre, ext = os.path.splitext(archivo)
        if ext.lower() in EXTENSIONES:
            imagenes.add(nombre)
    return imagenes

def verificar():
    """Verifica y muestra el estado de las imágenes"""
    print("=" * 60)
    print("📸 VERIFICACIÓN DE IMÁGENES")
    print("=" * 60)
    
    productos = obtener_productos_bd()
    imagenes = obtener_imagenes_carpeta()
    
    print(f"\n📊 Productos en BD: {len(productos)}")
    print(f"📁 Imágenes en carpeta: {len(imagenes)}")
    
    # Imágenes sueltas
    imagenes_sueltas = imagenes - set(productos.keys())
    
    # Productos sin imagen
    productos_sin_imagen = set(productos.keys()) - imagenes
    
    print("\n" + "-" * 60)
    print("📸 IMÁGENES SUELTAS (sin producto en BD)")
    print("-" * 60)
    
    if imagenes_sueltas:
        print(f"⚠️ {len(imagenes_sueltas)} imágenes sueltas:")
        for img in sorted(imagenes_sueltas):
            # Buscar el archivo con extensión
            archivo = None
            for ext in EXTENSIONES:
                ruta = os.path.join(CARPETA_IMAGENES, f"{img}{ext}")
                if os.path.exists(ruta):
                    archivo = f"{img}{ext}"
                    break
            print(f"  📄 {archivo or img}")
    else:
        print("✅ No hay imágenes sueltas")
    
    print("\n" + "-" * 60)
    print("📦 PRODUCTOS SIN IMAGEN")
    print("-" * 60)
    
    if productos_sin_imagen:
        print(f"⚠️ {len(productos_sin_imagen)} productos sin imagen:")
        for codigo in sorted(productos_sin_imagen):
            desc = productos[codigo]
            print(f"  📦 {codigo}: {desc[:50]}...")
    else:
        print("✅ Todos los productos tienen imagen")
    
    print("\n" + "-" * 60)
    print("📊 RESUMEN FINAL")
    print("-" * 60)
    print(f"  📁 Imágenes en carpeta: {len(imagenes)}")
    print(f"  📊 Productos en BD: {len(productos)}")
    print(f"  📸 Imágenes sueltas: {len(imagenes_sueltas)}")
    print(f"  📦 Productos sin imagen: {len(productos_sin_imagen)}")
    print("=" * 60)
    
    # Sugerencias
    if imagenes_sueltas:
        print("\n💡 SUGERENCIAS PARA IMÁGENES SUELTAS:")
        print("   Estas imágenes no corresponden a ningún producto en la BD.")
        print("   Puedes:")
        print("   1. Eliminarlas si no son necesarias")
        print("   2. Crear los productos en la BD con esos códigos")
        print("   3. Renombrarlas para que coincidan con códigos existentes")
    
    if productos_sin_imagen:
        print("\n💡 SUGERENCIAS PARA PRODUCTOS SIN IMAGEN:")
        print("   Estos productos no tienen imagen en la carpeta.")
        print("   Puedes:")
        print("   1. Agregar las imágenes con el nombre {codigo}.jpg")
        print("   2. O actualizar los códigos de los productos")
    
    return imagenes_sueltas, productos_sin_imagen

if __name__ == "__main__":
    imagenes_sueltas, productos_sin_imagen = verificar()