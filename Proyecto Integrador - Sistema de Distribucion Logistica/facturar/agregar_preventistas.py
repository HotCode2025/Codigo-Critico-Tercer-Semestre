import os
import re

with open('utilidades/central_sync.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Verificar si ya existe la función
if 'def recibir_preventistas_nuevos' not in contenido:
    # Buscar donde insertar la función
    nueva_funcion = '''
def recibir_preventistas_nuevos(ultimo_timestamp: str = "1970-01-01T00:00:00") -> list:
    """Recibe preventistas nuevos desde Turso"""
    return consultar_turso(
        "SELECT * FROM preventistas WHERE created_at > ? ORDER BY created_at ASC",
        [ultimo_timestamp]
    )
'''
    # Insertar después de recibir_clientes_nuevos
    contenido = contenido.replace(
        'def recibir_clientes_nuevos',
        nueva_funcion + '\n\ndef recibir_clientes_nuevos'
    )
    
    with open('utilidades/central_sync.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    print('✅ Función recibir_preventistas_nuevos() agregada')
else:
    print('✅ Función ya existe')
