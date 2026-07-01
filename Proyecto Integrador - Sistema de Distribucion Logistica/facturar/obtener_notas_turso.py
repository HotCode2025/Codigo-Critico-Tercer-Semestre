import requests
import json

# Leer configuración
with open('turso-facturar.txt', 'r') as f:
    lines = f.readlines()
    token = lines[0].strip()
    url_base = lines[1].strip()

# Construir URL correcta para Turso HTTP
# Si la URL es libsql://nube-clarionda.aws-us-east-1.turso.io
# La URL HTTP es https://nube-clarionda.aws-us-east-1.turso.io/v2/pipeline
if url_base.startswith('libsql://'):
    # Extraer el nombre del dominio
    domain = url_base.replace('libsql://', '')
    url = f'https://{domain}/v2/pipeline'
else:
    url = url_base

print(f'📡 Conectando a: {url}')
print(f'🔑 Token: {token[:20]}...')

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Obtener todas las notas
query = 'SELECT id, numero_nota, fecha, total, estado FROM notas_venta'
print(f'\n📝 Consulta: {query}')

response = requests.post(
    f'{url}/query',
    headers=headers,
    json={'query': query}
)

print(f'📊 Código de respuesta: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    rows = data.get('rows', [])
    print(f'\n📋 NOTAS EN TURSO: {len(rows)}')
    print('=' * 60)
    
    for row in rows:
        print(f'ID: {row[0]}')
        print(f'Nota: {row[1]}')
        print(f'Fecha: {row[2]}')
        print(f'Total: ${row[3]}')
        print(f'Estado: {row[4]}')
        print('-' * 40)
else:
    print(f'❌ Error: {response.status_code}')
    print(f'   {response.text}')
