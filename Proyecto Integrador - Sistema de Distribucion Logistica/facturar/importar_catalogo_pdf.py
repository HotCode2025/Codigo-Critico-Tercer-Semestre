"""
Código Crítico - Tercer Semestre - Año 2026
Script para importar el catálogo desde PDF a la base de datos
============================================================
📌 USO: python importar_catalogo_pdf.py [--app] [--central]
📌 FUNCIÓN: Extrae datos del PDF y crea productos en la BD
📌 ARCHIVO: Tregar - Catalogo digital 042026-rev2 (1) (1).pdf
"""

import os
import sys
import re
import sqlite3
import uuid
from typing import List, Dict, Any, Optional

# ============================================================
# CONFIGURACIÓN
# ============================================================

PDF_PATH = "Tregar - Catalogo digital 042026-rev2 (1) (1).pdf"
CENTRAL_DB = "../facturar/distribuidora.db"
APP_DB = "catalogo.db"

# ============================================================
# DATOS DEL CATÁLOGO (extraídos manualmente del PDF)
# ============================================================

# Formato: (codigo, nombre, presentacion, categoria)
PRODUCTOS_CATALOGO = [
    # === Leches Larga Vida ===
    ("1685", "LECHE ENTERA", "Tetra 1 litro (tapa Wing Cap) @ Caja x 12 u.", "Leches Larga Vida"),
    ("682", "LECHE ENTERA", "Tetra 1 litro (tapa Flexicap) @ Caja x 12 u.", "Leches Larga Vida"),
    ("1686", "LECHE PARCIALMENTE DESCREMADA", "Tetra 1 litro (tapa Wing Cap) @ Caja x 12 u.", "Leches Larga Vida"),
    ("1609", "LECHE PARCIALMENTE DESCREMADA", "Tetra 1 litro (tapa Flexicap) @ Caja x 12 u.", "Leches Larga Vida"),
    ("1621", "LECHE DESCREMADA 0% LACTOSA", "Tetra 1 litro (tapa Wing Cap) @ Caja x 12 u.", "Leches Larga Vida"),
    ("1274", "LECHE 0% GRASA", "Tetra 1 litro (tapa Wing Cap) @ Caja x 12 u.", "Leches Larga Vida"),
    
    # === Leches Saborizadas ===
    ("363", "CHOCOLATADA", "Tetra 1 litro (tapa Wing Cap) @ Caja x 12 u.", "Leches Saborizadas"),
    ("1319", "CHOCOLATADA", "Tetra 200 cc. @ Caja x 18 u.", "Leches Saborizadas"),
    
    # === Leches en Polvo ===
    ("378", "LECHE EN POLVO ENTERA INSTANTÁNEA", "Estuche x 800 g @ Caja x 10 u.", "Leches en Polvo"),
    ("312", "LECHE EN POLVO ENTERA (ALIMENTA)", "Bolsa papel Kraft x 25 kg.", "Leches en Polvo"),
    ("346", "SUERO EN POLVO DEMIB", "Bolsa papel Kraft x 25 kg.", "Leches en Polvo"),
    
    # === Yogures Cuchareables ===
    ("2175", "BATIDO ENTERO CON CAFE", "Pote plástico x 120 grs. @ Caja x 12 u.", "Yogures Cuchareables"),
    ("2176", "BATIDO ENTERO CON COCO", "Pote plástico x 120 grs. @ Caja x 12 u.", "Yogures Cuchareables"),
    ("2177", "BATIDO ENTERO CON LIMÓN", "Pote plástico x 120 grs. @ Caja x 12 u.", "Yogures Cuchareables"),
    ("1995", "CREMOSO ENTERO FRUTILLA", "Pote plástico x 125 grs. @ Caja x 24 u.", "Yogures Cuchareables"),
    ("1997", "CREMOSO ENTERO VAINILLA", "Pote plástico x 125 grs. @ Caja x 24 u.", "Yogures Cuchareables"),
    ("1998", "CREMOSO ENTERO DULCE DE LECHE", "Pote plástico x 125 grs. @ Caja x 24 u.", "Yogures Cuchareables"),
    ("2114", "CREMOSO DESCREMADO FRUTILLA", "Pote plástico x 125 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2115", "CREMOSO DESCREMADO VAINILLA", "Pote plástico x 125 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("1636", "ENTERO CON TROZOS DE FRUTILLA", "Pote plástico x 160 grs. @ Caja x 24 u.", "Yogures Cuchareables"),
    ("1637", "ENTERO CON TROZOS DE DURAZNO", "Pote plástico x 160 grs. @ Caja x 24 u.", "Yogures Cuchareables"),
    ("1638", "ENTERO CON TROZOS DE ARÁNDANO", "Pote plástico x 160 grs. @ Caja x 24 u.", "Yogures Cuchareables"),
    ("2154", "ENTERO CON TROZOS DE MANGO + MARACUYÁ", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2153", "ENTERO CON TROZOS DE ANANÁ", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2174", "ENTERO CON TROZOS DE CEREZA", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2155", "DESCREMADO CON TROZOS DE FRUTILLA", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2156", "DESCREMADO CON TROZOS DE DURAZNO", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2157", "DESCREMADO CON TROZOS DE ARANDANO", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    ("2173", "DESCREMADO CON TROZOS DE ANANÁ", "Pote plástico x 160 grs. @ Caja x 18 u.", "Yogures Cuchareables"),
    
    # === Yogures Firmes ===
    ("2231", "FIRME ENTERO FRUTILLA", "Pote plástico x 170 grs. @ Caja x 18 u.", "Yogures Firmes"),
    ("2232", "FIRME ENTERO VAINILLA", "Pote plástico x 170 grs. @ Caja x 18 u.", "Yogures Firmes"),
    ("2240", "FIRME DESCREMADO FRUTILLA", "Pote plástico x 170 grs. @ Caja x 18 u.", "Yogures Firmes"),
    ("2241", "FIRME DESCREMADO VAINILLA", "Pote plástico x 170 grs. @ Caja x 18 u.", "Yogures Firmes"),
    
    # === Yogures Naturales ===
    ("2171", "NATURAL · ENDULZADO", "Pote plástico x 280 grs. @ Caja x 12 u.", "Yogures Naturales"),
    ("1694", "NATURAL · ENDULZADO", "Pote plástico x 140 grs. @ Caja x 18 u.", "Yogures Naturales"),
    ("2172", "NATURAL · SIN AZÚCAR", "Pote plástico x 280 grs. @ Caja x 12 u.", "Yogures Naturales"),
    ("2149", "NATURAL · SIN AZÚCAR", "Pote plástico x 140 grs. @ Caja x 12 u.", "Yogures Naturales"),
    
    # === Yogures con Topping ===
    ("2139", "TOPS ENTERO CON COPOS DE MAIZ", "Pote plástico x 164 grs. @ Caja x 18 u.", "Yogures con Topping"),
    ("2168", "TOPS ENTERO CON GRANOLA", "Pote plástico x 155 grs. @ Caja x 18 u.", "Yogures con Topping"),
    ("2140", "TOPS DESCREMADO CON COPOS DE MAIZ Y MIEL", "Pote plástico x 164 grs. @ Caja x 18 u.", "Yogures con Topping"),
    ("2214", "TOPS DESCREMADO CON GRANOLA", "Pote plástico x 155 grs. @ Caja x 18 u.", "Yogures con Topping"),
    
    # === Yogures Bebibles ===
    ("1993", "ENTERO BEBIBLE FRUTILLA", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    ("1994", "ENTERO BEBIBLE VAINILLA", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    ("1695", "ENTERO BEBIBLE DURAZNO", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    ("1696", "ENTERO BEBIBLE ARANDANO", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    ("2211", "DESCREMADO BEBIBLE FRUTILLA", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    ("2212", "DESCREMADO BEBIBLE VAINILLA", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    ("2213", "DESCREMADO BEBIBLE DURAZNO", "Sachet x 900 g @ Caja x 18 u.", "Yogures Bebibles"),
    
    # === Arroz con Leche ===
    ("2110", "ARROZ CON LECHE CLÁSICO", "Pote plástico x 180 g @ Caja x 20 u.", "Arroz con Leche"),
    ("2111", "ARROZ CON LECHE CON CANELA", "Pote plástico x 180 g @ Caja x 20 u.", "Arroz con Leche"),
    ("2109", "ARROZ CON LECHE CON DULCE DE LECHE", "Pote plástico x 180 g @ Caja x 20 u.", "Arroz con Leche"),
    ("313", "ARROZ CON LECHE CON CHOCOLATE", "Pote plástico x 180 g @ Caja x 20 u.", "Arroz con Leche"),
    ("82", "ARROZ CON LECHE DESCREMADO", "Pote plástico x 180 g @ Caja x 20 u.", "Arroz con Leche"),
    
    # === Quesos Untables Saborizados ===
    ("2078", "CHÂTEL UNTABLE CLÁSICO", "Pote plástico x 180 g @ Caja x 12 u.", "Quesos Untables Saborizados"),
    ("2079", "CHÂTEL UNTABLE CON JAMÓN", "Pote plástico x 180 g @ Caja x 12 u.", "Quesos Untables Saborizados"),
    ("2094", "CHÂTEL UNTABLE CON SALAME", "Pote plástico x 180 g @ Caja x 12 u.", "Quesos Untables Saborizados"),
    ("2169", "CHÂTEL UNTABLE CON SIBOULETTE", "Pote plástico x 180 g @ Caja x 12 u.", "Quesos Untables Saborizados"),
    ("2108", "CHÂTEL UNTABLE CHEDDAR", "Pote plástico x 180 g @ Caja x 12 u.", "Quesos Untables Saborizados"),
    ("2118", "CHÂTEL UNTABLE DESCREMADO", "Pote plástico x 180 g @ Caja x 12 u.", "Quesos Untables Saborizados"),
    
    # === Quesos Untables Blancos & Quesos Crema ===
    ("2144", "QUESO BLANCO CLÁSICO", "Pote plástico x 290 g @ Caja x 12 u.", "Quesos Untables Blancos"),
    ("2145", "QUESO BLANCO LIGHT", "Pote plástico x 290 g @ Caja x 12 u.", "Quesos Untables Blancos"),
    ("1627", "QUESO CREMA CLÁSICO", "Pote plástico x 190 g @ Caja x 12 u.", "Quesos Untables Blancos"),
    ("1760", "QUESO CREMA CLÁSICO", "Pote plástico x 280 g @ Caja x 12 u.", "Quesos Untables Blancos"),
    ("1628", "QUESO CREMA DESCREMADO", "Pote plástico x 190 g @ Caja x 12 u.", "Quesos Untables Blancos"),
    ("1782", "QUESO CREMA DESCREMADO", "Pote plástico x 280 g @ Caja x 12 u.", "Quesos Untables Blancos"),
    
    # === Mascarpone ===
    ("225", "QUESO MASCARPONE", "Pote plástico x 200 g @ Caja x 12 u.", "Mascarpone"),
    
    # === Cremas y Ricottas ===
    ("1999", "CREMA DE LECHE DOBLE", "Pote plástico x 200 cc @ Caja x 12 u.", "Cremas"),
    ("2068", "CREMA DE LECHE DOBLE", "Pote plástico x 350 cc @ Caja x 12 u.", "Cremas"),
    ("269", "CREMA CHANTILLY", "Spray 250 ml @ Bandeja con envoltura plástica x 12 u.", "Cremas"),
    ("2141", "RICOTTA DE LECHE ENTERA", "Pote plástico x 290 g @ Caja x 6 u.", "Ricottas"),
    ("2142", "RICOTTA DE LECHE LIGHT", "Pote plástico x 290 g @ Caja x 6 u.", "Ricottas"),
    
    # === Dulce de Leche ===
    ("1313", "DULCE DE LECHE CLÁSICO", "Pote plástico x 200 g @ Caja x 12 u.", "Dulce de Leche"),
    ("31", "DULCE DE LECHE CLÁSICO", "Pote plástico x 400 g @ Caja x 12 u.", "Dulce de Leche"),
    
    # === Quesos Duros ===
    ("17", "REGGIANITO", "Horma x 7 kg @ Caja x 1 u.", "Quesos Duros"),
    ("208", "REGGIANITO", "Porción 280 g - Envasado al vacío @ Caja x 12 u.", "Quesos Duros"),
    
    # === Quesos Semi Duros ===
    ("1096", "HOLANDA", "Horma x 4,200 kg (aprox) @ Caja x 2 u.", "Quesos Semi Duros"),
    ("142", "HOLANDA", "Porción 440 g - Envasado al vacío @ Caja x 12 u.", "Quesos Semi Duros"),
    ("1099", "PATEGRAS", "Horma x 4,200 kg (aprox) @ Caja x 2 u.", "Quesos Semi Duros"),
    ("1095", "CRIOLLO", "Horma x 4,200 kg (aprox) @ Caja x 2 u.", "Quesos Semi Duros"),
    ("195", "CRIOLLO", "Horma x 4,200 kg (aprox) @ Caja 'Obsequio' x 1 u.", "Quesos Semi Duros"),
    ("257", "CRIOLLO", "Porción 380 g - Envasado al vacío @ Caja x 10 u.", "Quesos Semi Duros"),
    ("104", "FONTINA", "Horma x 9,000 kg (aprox) @ Caja x 1 u.", "Quesos Semi Duros"),
    ("211", "AZUL", "Horma x 1,500 kg (aprox) @ Caja x 2 u.", "Quesos Semi Duros"),
    ("1098", "DANBO", "Horma x 4,200 kg (aprox) - Envasado al vacío @ Caja x 4 u.", "Quesos Semi Duros"),
    ("1097", "MOZZARELLA", "Horma x 4,200 kg (aprox) - Envasado al vacío @ Caja x 4 u.", "Quesos Semi Duros"),
    
    # === Quesos Blandos ===
    ("9", "CREMOSO", "Horma 4,100 kg - Envasado al vacío @ Caja x 4 u.", "Quesos Blandos"),
    ("1245", "CREMOSO", "Porción 520 g - Envasado al vacío @ Caja x 12 u.", "Quesos Blandos"),
    ("170", "CREMOSO", "Porción 520 g - Envasado al vacío @ Caja x 24 u.", "Quesos Blandos"),
    ("1093", "POR SALUT", "Horma 3,900 kg - Envasado al vacío @ Caja x 2 u.", "Quesos Blandos"),
    ("1246", "POR SALUT", "Porción 480 g - Envasado al vacío @ Caja x 12 u.", "Quesos Blandos"),
    ("171", "POR SALUT", "Porción 480 g - Envasado al vacío @ Caja x 24 u.", "Quesos Blandos"),
    ("1094", "POR SALUT LIGHT", "Horma 3,500 kg - Envasado al vacío @ Caja x 2 u.", "Quesos Blandos"),
    ("1100", "POR SALUT LIGHT", "Porción 430 g - Envasado al vacío @ Caja x 12 u.", "Quesos Blandos"),
    ("1101", "POR SALUT LIGHT SIN SAL", "Porción 430 g - Envasado al vacío @ Caja x 12 u.", "Quesos Blandos"),
    
    # === Quesos Rallados ===
    ("180", "RALLADO", "Sobres x 40 g @ Display x 20 u.", "Quesos Rallados"),
    ("2146", "RALLADO", "Sobre x 120 g @ Caja protectora x 24 u.", "Quesos Rallados"),
]

# ============================================================
# FUNCIONES
# ============================================================

def obtener_categoria_id(conn, categoria_nombre):
    """Obtiene o crea una categoría y devuelve su ID"""
    cur = conn.cursor()
    
    # Buscar categoría
    cur.execute("SELECT id FROM categorias WHERE nombre = ?", (categoria_nombre,))
    row = cur.fetchone()
    
    if row:
        return row[0]
    
    # Crear categoría
    categoria_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO categorias (id, nombre, descripcion, activo)
        VALUES (?, ?, ?, ?)
    """, (categoria_id, categoria_nombre, f"Categoría: {categoria_nombre}", 1))
    conn.commit()
    
    return categoria_id


def verificar_imagen(codigo):
    """Verifica si existe una imagen para el código en la carpeta"""
    import os
    carpeta = os.path.join(os.path.dirname(__file__), "..", "facturar", "imagenes_productos")
    if not os.path.exists(carpeta):
        carpeta = "imagenes_productos"
    
    extensiones = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    for ext in extensiones:
        ruta = os.path.join(carpeta, f"{codigo}{ext}")
        if os.path.exists(ruta):
            return f"{codigo}{ext}"
    
    # Buscar en la carpeta actual
    carpeta_local = "imagenes_productos"
    if os.path.exists(carpeta_local):
        for ext in extensiones:
            ruta = os.path.join(carpeta_local, f"{codigo}{ext}")
            if os.path.exists(ruta):
                return f"{codigo}{ext}"
    
    return None


def importar_a_bd(bd_path, es_app=False):
    """Importa los productos a la base de datos especificada"""
    print(f"\n📊 Importando a: {bd_path}")
    
    if not os.path.exists(bd_path):
        print(f"⚠️ La base de datos {bd_path} no existe")
        return 0
    
    conn = sqlite3.connect(bd_path)
    cur = conn.cursor()
    
    # Verificar que la tabla productos existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
    if not cur.fetchone():
        print("❌ La tabla 'productos' no existe en la base de datos")
        conn.close()
        return 0
    
    # Verificar cuántos productos ya existen
    cur.execute("SELECT COUNT(*) FROM productos")
    existentes = cur.fetchone()[0]
    print(f"📊 Productos existentes: {existentes}")
    
    if existentes > 0:
        respuesta = input("¿Deseas eliminar los productos existentes y volver a importar? (s/n): ").lower()
        if respuesta == 's':
            cur.execute("DELETE FROM productos")
            cur.execute("DELETE FROM categorias")
            conn.commit()
            print("✅ Productos y categorías eliminados")
    
    importados = 0
    errores = 0
    
    print(f"\n🔄 Importando {len(PRODUCTOS_CATALOGO)} productos...")
    
    for codigo, nombre, presentacion, categoria in PRODUCTOS_CATALOGO:
        try:
            # Obtener o crear categoría
            categoria_id = obtener_categoria_id(conn, categoria)
            
            # Generar UUID para el producto
            producto_id = str(uuid.uuid4())
            
            # Verificar si la imagen existe
            url_foto = verificar_imagen(codigo)
            
            # Descripción completa
            descripcion = f"{nombre} - {presentacion}"
            
            # Insertar producto
            cur.execute("""
                INSERT INTO productos (
                    id, codigo_producto, descripcion, precio_venta, stock_actual,
                    stock_critico, unidad_medida, categoria_id, url_foto, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                producto_id,
                codigo,
                descripcion,
                0.0,  # precio_venta (se actualizará después)
                0,    # stock_actual
                5,    # stock_critico
                'unidad',
                categoria_id,
                url_foto,
                1
            ))
            
            importados += 1
            status = f"✅ {codigo}: {nombre[:30]}..."
            if url_foto:
                print(f"  {status} (imagen: {url_foto})")
            else:
                print(f"  {status} (⚠️ sin imagen)")
            
        except Exception as e:
            errores += 1
            print(f"  ❌ Error importando {codigo}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 RESUMEN:")
    print(f"  ✅ Importados: {importados}")
    print(f"  ❌ Errores: {errores}")
    
    return importados


def main():
    """Función principal"""
    print("=" * 70)
    print("📦 IMPORTAR CATÁLOGO DESDE PDF")
    print("=" * 70)
    print(f"📄 Archivo: {PDF_PATH}")
    print(f"📋 Productos en catálogo: {len(PRODUCTOS_CATALOGO)}")
    
    # Determinar qué bases de datos actualizar
    importar_central = False
    importar_app = False
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--central":
                importar_central = True
            elif arg == "--app":
                importar_app = True
            elif arg == "--all":
                importar_central = True
                importar_app = True
    else:
        # Por defecto, importar en Central
        importar_central = True
    
    print(f"\n📌 Destinos:")
    print(f"  💻 Central: {'✅' if importar_central else '❌'}")
    print(f"  📱 App: {'✅' if importar_app else '❌'}")
    
    if importar_central:
        importar_a_bd(CENTRAL_DB, es_app=False)
    
    if importar_app:
        importar_a_bd(APP_DB, es_app=True)
    
    print("\n" + "=" * 70)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("=" * 70)
    
    if importar_central:
        print("\n🚀 PARA SINCRONIZAR A TURSO:")
        print("   cd ~/facturar")
        print("   python -c \"from utilidades import sincronizar_ahora; from db.db_manager import obtener_conexion; db=obtener_conexion(); sincronizar_ahora(db); db.close()\"")
    
    if importar_app:
        print("\n🚀 PARA DESCARGAR EN LA APP:")
        print("   cd ~/app")
        print("   python -c \"from turso_client import bajar_tabla_pyturso; bajar_tabla_pyturso('productos')\"")


if __name__ == "__main__":
    main()