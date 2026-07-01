#!/usr/bin/env python3
import os
import re

archivo = 'vistas/notas_venta/vista_notas_venta.py'

# Leer el archivo
with open(archivo, 'r', encoding='utf-8') as f:
    contenido = f.read()

# 1. Agregar import si no existe
if 'from utilidades.sync_lock import' not in contenido:
    # Buscar imports existentes
    lines = contenido.split('\n')
    pos_import = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            pos_import = i + 1
    
    lines.insert(pos_import, 'from utilidades.sync_lock import with_sync_lock, SyncLockContext')
    contenido = '\n'.join(lines)
    print("✅ Import agregado")

# 2. Buscar la función facturar_nota
patron = r'def facturar_nota\(self, tab\):'
match = re.search(patron, contenido)

if match:
    pos = match.start()
    # Verificar si ya tiene el decorador
    texto_anterior = contenido[pos-30:pos] if pos >= 30 else ''
    
    if '@with_sync_lock' not in texto_anterior:
        # Agregar el decorador con indentación correcta
        contenido = contenido[:pos] + '    @with_sync_lock\n' + contenido[pos:]
        print("✅ Decorador agregado a facturar_nota")
    else:
        print("ℹ️ facturar_nota ya tiene el decorador")
else:
    print("⚠️ No se encontró la función facturar_nota")

# Guardar
with open(archivo, 'w', encoding='utf-8') as f:
    f.write(contenido)

print(f"✅ {archivo} reparado")
