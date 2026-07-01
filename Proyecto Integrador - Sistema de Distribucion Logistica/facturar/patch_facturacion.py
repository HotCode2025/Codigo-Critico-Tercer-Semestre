"""
Parche para agregar bloqueo de sincronización a la facturación
"""

import sys
import inspect
import importlib.util
from utilidades.sync_lock import SyncLockContext

def parchear_funcion_facturar():
    """Busca y parchea la función de facturación en la interfaz"""
    
    # Buscar archivos que contengan funciones de facturación
    archivos_encontrados = []
    patrones = ['facturar', 'procesar_nota', 'generar_factura', 'emitir_factura']
    
    import os
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    for patron in patrones:
                        if f'def {patron}' in contenido or f'def {patron}_' in contenido:
                            archivos_encontrados.append(os.path.join(root, file))
                            break
    
    print("📋 Archivos con funciones de facturación encontrados:")
    for archivo in archivos_encontrados:
        print(f"   {archivo}")
    
    return archivos_encontrados

def aplicar_parche_manual():
    """Instrucciones para aplicar el parche manualmente"""
    
    print("\n" + "=" * 60)
    print("🔧 INSTRUCCIONES PARA APLICAR EL PARCHE")
    print("=" * 60)
    print()
    print("1. Abre el archivo donde está la función de facturación")
    print()
    print("2. Agrega esta importación al inicio:")
    print("   from utilidades.sync_lock import with_sync_lock, SyncLockContext")
    print()
    print("3. Opción A: Usar el decorador (recomendado)")
    print("   @with_sync_lock")
    print("   def facturar_nota(self, nota_id):")
    print("       # Tu código de facturación aquí")
    print("       pass")
    print()
    print("4. Opción B: Usar context manager")
    print("   def facturar_nota(self, nota_id):")
    print("       with SyncLockContext('Facturando nota'):")
    print("           # Tu código de facturación aquí")
    print("           pass")
    print()
    print("5. Reiniciar el sistema")
    print()

def crear_parche_automatico():
    """Intenta crear un parche automático"""
    
    archivos = parchear_funcion_facturar()
    
    if not archivos:
        print("\n❌ No se encontraron archivos de facturación")
        print("ℹ️ Busca manualmente dónde está la función de facturación")
        aplicar_parche_manual()
        return
    
    print("\n📝 Archivos encontrados. Revisa cada uno para aplicar el parche.")
    print("🔍 Busca funciones como: facturar, procesar_nota, generar_factura, etc.")
    aplicar_parche_manual()

if __name__ == '__main__':
    crear_parche_automatico()
