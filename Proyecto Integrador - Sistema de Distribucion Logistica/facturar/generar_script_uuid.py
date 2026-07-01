"""
Genera un script SQL completo con UUIDs reales y 500 notas de venta
"""

import uuid
import random
from datetime import datetime, timedelta, date

# ============================================================
# CONFIGURACIÓN
# ============================================================

FECHA_FIN = date(2026, 6, 28)
FECHA_INICIO = FECHA_FIN - timedelta(days=180)

# ============================================================
# PRODUCTOS (95 productos de Tregar)
# ============================================================

PRODUCTOS = [
    ('1685', 'Leche Entera Tetra 1L Wing Cap', 600, 950, 'Leches'),
    ('682', 'Leche Entera Tetra 1L Flexicap', 600, 950, 'Leches'),
    ('1686', 'Leche Parcialmente Descremada 1L Wing Cap', 580, 920, 'Leches'),
    ('1609', 'Leche Parcialmente Descremada 1L Flexicap', 580, 920, 'Leches'),
    ('1621', 'Leche Descremada 0% Lactosa 1L', 720, 1100, 'Leches'),
    ('1274', 'Leche 0% Grasa 1L', 590, 935, 'Leches'),
    ('363', 'Chocolatada 1L', 650, 1000, 'Leches Saborizadas'),
    ('1319', 'Chocolatada 200cc', 350, 550, 'Leches Saborizadas'),
    ('378', 'Leche en Polvo Entera Instantánea 800g', 850, 1350, 'Leches en Polvo'),
    ('312', 'Leche en Polvo Entera Alimenta 25kg', 18000, 25000, 'Leches en Polvo'),
    ('346', 'Suero en Polvo Demib 25kg', 12000, 18000, 'Leches en Polvo'),
    ('2175', 'Batido Entero con Café 120g', 400, 650, 'Yogures Cuchareables'),
    ('2176', 'Batido Entero con Coco 120g', 400, 650, 'Yogures Cuchareables'),
    ('2177', 'Batido Entero con Limón 120g', 400, 650, 'Yogures Cuchareables'),
    ('1995', 'Cremoso Entero Frutilla 125g', 450, 700, 'Yogures Cuchareables'),
    ('1997', 'Cremoso Entero Vainilla 125g', 450, 700, 'Yogures Cuchareables'),
    ('1998', 'Cremoso Entero Dulce de Leche 125g', 450, 700, 'Yogures Cuchareables'),
    ('2114', 'Cremoso Descremado Frutilla 125g', 430, 680, 'Yogures Cuchareables'),
    ('2115', 'Cremoso Descremado Vainilla 125g', 430, 680, 'Yogures Cuchareables'),
    ('1636', 'Entero con Trozos de Frutilla 160g', 500, 780, 'Yogures Cuchareables'),
    ('1637', 'Entero con Trozos de Durazno 160g', 500, 780, 'Yogures Cuchareables'),
    ('1638', 'Entero con Trozos de Arándano 160g', 520, 800, 'Yogures Cuchareables'),
    ('2154', 'Entero con Trozos de Mango + Maracuyá 160g', 530, 810, 'Yogures Cuchareables'),
    ('2153', 'Entero con Trozos de Ananá 160g', 520, 800, 'Yogures Cuchareables'),
    ('2174', 'Entero con Trozos de Cereza 160g', 540, 820, 'Yogures Cuchareables'),
    ('2155', 'Descremado con Trozos de Frutilla 160g', 480, 750, 'Yogures Cuchareables'),
    ('2156', 'Descremado con Trozos de Durazno 160g', 480, 750, 'Yogures Cuchareables'),
    ('2157', 'Descremado con Trozos de Arándano 160g', 500, 770, 'Yogures Cuchareables'),
    ('2173', 'Descremado con Trozos de Ananá 160g', 480, 750, 'Yogures Cuchareables'),
    ('2231', 'Firme Entero Frutilla 170g', 420, 660, 'Yogures Firmes'),
    ('2232', 'Firme Entero Vainilla 170g', 420, 660, 'Yogures Firmes'),
    ('2240', 'Firme Descremado Frutilla 170g', 400, 640, 'Yogures Firmes'),
    ('2241', 'Firme Descremado Vainilla 170g', 400, 640, 'Yogures Firmes'),
    ('2171', 'Natural Endulzado 280g', 380, 600, 'Yogures Naturales'),
    ('1694', 'Natural Endulzado 140g', 320, 520, 'Yogures Naturales'),
    ('2172', 'Natural Sin Azúcar 280g', 370, 590, 'Yogures Naturales'),
    ('2149', 'Natural Sin Azúcar 140g', 310, 510, 'Yogures Naturales'),
    ('2139', 'Tops Entero con Copos de Maíz 164g', 460, 720, 'Yogures con Topping'),
    ('2168', 'Tops Entero con Granola 155g', 470, 730, 'Yogures con Topping'),
    ('2140', 'Tops Descremado con Copos de Maíz y Miel 164g', 440, 700, 'Yogures con Topping'),
    ('2214', 'Tops Descremado con Granola 155g', 450, 710, 'Yogures con Topping'),
    ('1993', 'Entero Bebible Frutilla 900g', 550, 850, 'Yogures Bebibles'),
    ('1994', 'Entero Bebible Vainilla 900g', 550, 850, 'Yogures Bebibles'),
    ('1695', 'Entero Bebible Durazno 900g', 550, 850, 'Yogures Bebibles'),
    ('1696', 'Entero Bebible Arándano 900g', 560, 860, 'Yogures Bebibles'),
    ('2211', 'Descremado Bebible Frutilla 900g', 530, 820, 'Yogures Bebibles'),
    ('2212', 'Descremado Bebible Vainilla 900g', 530, 820, 'Yogures Bebibles'),
    ('2213', 'Descremado Bebible Durazno 900g', 530, 820, 'Yogures Bebibles'),
    ('2110', 'Arroz con Leche Clásico 180g', 450, 700, 'Arroz con Leche'),
    ('2111', 'Arroz con Leche con Canela 180g', 460, 710, 'Arroz con Leche'),
    ('2109', 'Arroz con Leche con Dulce de Leche 180g', 470, 720, 'Arroz con Leche'),
    ('313', 'Arroz con Leche con Chocolate 180g', 480, 730, 'Arroz con Leche'),
    ('82', 'Arroz con Leche Descremado 180g', 440, 690, 'Arroz con Leche'),
    ('2078', 'Châtel Untable Clásico 180g', 850, 1300, 'Quesos Untables'),
    ('2079', 'Châtel Untable con Jamón 180g', 880, 1350, 'Quesos Untables'),
    ('2094', 'Châtel Untable con Salame 180g', 880, 1350, 'Quesos Untables'),
    ('2169', 'Châtel Untable con Siboulette 180g', 870, 1340, 'Quesos Untables'),
    ('2108', 'Châtel Untable Cheddar 180g', 900, 1380, 'Quesos Untables'),
    ('2118', 'Châtel Untable Descremado 180g', 820, 1280, 'Quesos Untables'),
    ('2144', 'Queso Blanco Clásico 290g', 950, 1450, 'Quesos Untables Blancos'),
    ('2145', 'Queso Blanco Light 290g', 920, 1420, 'Quesos Untables Blancos'),
    ('1627', 'Queso Crema Clásico 190g', 800, 1250, 'Quesos Untables Blancos'),
    ('1760', 'Queso Crema Clásico 280g', 950, 1450, 'Quesos Untables Blancos'),
    ('1628', 'Queso Crema Descremado 190g', 780, 1220, 'Quesos Untables Blancos'),
    ('1782', 'Queso Crema Descremado 280g', 920, 1420, 'Quesos Untables Blancos'),
    ('225', 'Queso Mascarpone 200g', 1100, 1700, 'Mascarpone'),
    ('1999', 'Crema de Leche Doble 200cc', 700, 1100, 'Cremas'),
    ('2068', 'Crema de Leche Doble 350cc', 850, 1300, 'Cremas'),
    ('269', 'Crema Chantilly Spray 250ml', 900, 1400, 'Cremas'),
    ('2141', 'Ricotta de Leche Entera 290g', 800, 1250, 'Ricottas'),
    ('2142', 'Ricotta de Leche Light 290g', 780, 1220, 'Ricottas'),
    ('1313', 'Dulce de Leche Clásico 200g', 550, 850, 'Dulce de Leche'),
    ('31', 'Dulce de Leche Clásico 400g', 750, 1150, 'Dulce de Leche'),
    ('17', 'Reggianito Horma 7kg', 15000, 22000, 'Quesos Duros'),
    ('208', 'Reggianito Porción 280g', 1800, 2800, 'Quesos Duros'),
    ('1096', 'Holanda Horma 4.2kg', 9000, 13500, 'Quesos Semi Duros'),
    ('142', 'Holanda Porción 440g', 1900, 2900, 'Quesos Semi Duros'),
    ('1099', 'Pategrás Horma 4.2kg', 9200, 13800, 'Quesos Semi Duros'),
    ('1095', 'Criollo Horma 4.2kg', 8500, 12800, 'Quesos Semi Duros'),
    ('195', 'Criollo Horma Obsequio 4.2kg', 7500, 11500, 'Quesos Semi Duros'),
    ('257', 'Criollo Porción 380g', 1700, 2600, 'Quesos Semi Duros'),
    ('104', 'Fontina Horma 9kg', 12000, 18000, 'Quesos Semi Duros'),
    ('211', 'Azul Horma 1.5kg', 3000, 4500, 'Quesos Semi Duros'),
    ('1098', 'Danbo Horma 4.2kg', 8800, 13200, 'Quesos Semi Duros'),
    ('1097', 'Mozzarella Horma 4.2kg', 9500, 14200, 'Quesos Semi Duros'),
    ('9', 'Cremoso Horma 4.1kg', 8000, 12000, 'Quesos Blandos'),
    ('1245', 'Cremoso Porción 520g', 2000, 3000, 'Quesos Blandos'),
    ('170', 'Cremoso Porción 520g (24u)', 1900, 2900, 'Quesos Blandos'),
    ('1093', 'Por Salut Horma 3.9kg', 7800, 11700, 'Quesos Blandos'),
    ('1246', 'Por Salut Porción 480g', 1900, 2850, 'Quesos Blandos'),
    ('171', 'Por Salut Porción 480g (24u)', 1800, 2750, 'Quesos Blandos'),
    ('1094', 'Por Salut Light Horma 3.5kg', 7600, 11400, 'Quesos Blandos'),
    ('1100', 'Por Salut Light Porción 430g', 1850, 2800, 'Quesos Blandos'),
    ('1101', 'Por Salut Light Sin Sal Porción 430g', 1850, 2800, 'Quesos Blandos'),
    ('180', 'Queso Rallado 40g', 400, 650, 'Quesos Rallados'),
    ('2146', 'Queso Rallado 120g', 750, 1150, 'Quesos Rallados'),
]

# ============================================================
# PREVENTISTAS
# ============================================================

PREVENTISTAS = [
    ('Ariel', 'Mazara', 'P002', '0261-1234-1002', 'ariel.mazara@tregar.com', 'Valle de Uco'),
    ('Agustina', 'Zúñiga', 'P003', '0261-1234-1003', 'agustina.zuniga@tregar.com', 'Centro Mendoza'),
    ('Maximiliano', 'Morales', 'P004', '0261-1234-1004', 'maximiliano.morales@tregar.com', 'Sur Mendoza'),
    ('Santino', 'Mamani', 'P005', '0261-1234-1005', 'santino.mamani@tregar.com', 'Este Mendoza'),
    ('Joel', 'Gonzalez', 'P006', '0261-1234-1006', 'joel.gonzalez@tregar.com', 'Sur Mendoza'),
    ('Daniel', 'Silva', 'P007', '0264-1234-1007', 'daniel.silva@tregar.com', 'San Juan'),
    ('Damián', 'Ponce de León', 'P008', '0266-1234-1008', 'damian.poncedeleon@tregar.com', 'San Luis'),
]

# ============================================================
# NOMBRES DE NEGOCIOS Y LOCALIDADES
# ============================================================

NOMBRES_NEGOCIOS = [
    'Almacén El Sol', 'Almacén La Esquina', 'Almacén Don José', 
    'Almacén El Buen Gusto', 'Almacén Santa Rosa', 'Almacén La Familia',
    'Almacén El Progreso', 'Kiosco La Plaza', 'Kiosco El Centro',
    'Kiosco La Esquinita', 'Supermercado El Ahorro', 'Supermercado La Economía',
    'Almacén La Amistad', 'Almacén La Esperanza', 'Kiosco El Diario',
    'Supermercado El Precio Justo', 'Almacén El Vecino', 'Kiosco La Golosina'
]

LOCALIDADES = [
    ('Mendoza Capital', 'Mendoza', -32.8902, -68.8440),
    ('Godoy Cruz', 'Mendoza', -32.9167, -68.8333),
    ('Las Heras', 'Mendoza', -32.8500, -68.8000),
    ('Guaymallén', 'Mendoza', -32.8833, -68.7500),
    ('Maipú', 'Mendoza', -33.0000, -68.7667),
    ('San Rafael', 'Mendoza', -34.6000, -68.3333),
    ('General Alvear', 'Mendoza', -34.9833, -67.7000),
    ('Malargüe', 'Mendoza', -35.4667, -69.5833),
    ('San Martín', 'Mendoza', -33.0810, -68.4681),
    ('Junín', 'Mendoza', -33.1333, -68.4667),
    ('Tunuyán', 'Mendoza', -33.5667, -69.0167),
    ('San Juan Capital', 'San Juan', -31.5375, -68.5364),
    ('San Luis Capital', 'San Luis', -33.2950, -66.3370),
    ('Villa Mercedes', 'San Luis', -33.6667, -65.4667),
    ('Rawson', 'San Juan', -31.5667, -68.5667),
    ('Caucete', 'San Juan', -31.6500, -68.2833),
    ('Merlo', 'San Luis', -32.3333, -65.0167),
]

CALLES = ['San Martín', 'Belgrano', 'Mitre', 'Rivadavia', '25 de Mayo', 'Moreno', 'Lavalle', 'España', 'Colón', 'Sarmiento']

# ============================================================
# GENERAR SCRIPT SQL CON UUIDs
# ============================================================

def generar_script():
    print("📝 Generando script SQL con UUIDs...")
    
    output = """-- ============================================================
-- SCRIPT COMPLETO - CON UUIDs REALES
-- ============================================================
-- 
-- NOTAS DE VENTA: 500
-- PRODUCTOS: 95
-- PREVENTISTAS: 7
-- CLIENTES: 700
-- ============================================================

PRAGMA foreign_keys = OFF;

-- ============================================================
-- CATEGORIAS
-- ============================================================

"""
    
    # Categorías
    categorias = sorted(set([p[3] for p in PRODUCTOS]))
    categoria_ids = {}
    for cat in categorias:
        cat_id = str(uuid.uuid4())
        categoria_ids[cat] = cat_id
        output += f"INSERT OR IGNORE INTO categorias (id, nombre) VALUES ('{cat_id}', '{cat}');\n"
    
    # Preventistas
    output += "\n-- ============================================================\n-- PREVENTISTAS\n-- ============================================================\n\n"
    preventista_ids = {}
    for p in PREVENTISTAS:
        pid = str(uuid.uuid4())
        preventista_ids[p[0]] = pid
        output += f"INSERT OR IGNORE INTO preventistas (id, nombre, apellido, legajo, telefono, email, zona, activo) VALUES ('{pid}', '{p[0]}', '{p[1]}', '{p[2]}', '{p[3]}', '{p[4]}', '{p[5]}', 1);\n"
    
    # Usuarios
    output += "\n-- ============================================================\n-- USUARIOS\n-- ============================================================\n\n"
    output += "INSERT OR IGNORE INTO usuarios (id, username, password_hash, rol, preventista_id, activo) VALUES\n"
    output += "('00000000-0000-0000-0000-000000000001', 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', NULL, 1);\n"
    for i, p in enumerate(PREVENTISTAS, 1):
        uid = str(uuid.uuid4())
        output += f"INSERT OR IGNORE INTO usuarios (id, username, password_hash, rol, preventista_id, activo) VALUES ('{uid}', 'prev{i:03d}', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', '{preventista_ids[p[0]]}', 1);\n"
    
    # Productos
    output += "\n-- ============================================================\n-- PRODUCTOS\n-- ============================================================\n\n"
    producto_ids = []
    for i, p in enumerate(PRODUCTOS):
        codigo, nombre, costo, venta, categoria = p
        prod_id = str(uuid.uuid4())
        producto_ids.append(prod_id)
        output += f"INSERT OR IGNORE INTO productos (id, codigo_producto, descripcion, precio_costo, precio_venta, stock_actual, stock_critico, categoria_id, activo) VALUES ('{prod_id}', '{codigo}', '{nombre}', {costo}, {venta}, 100000, {random.randint(100, 500)}, '{categoria_ids[categoria]}', 1);\n"
    
    # Clientes (700)
    output += "\n-- ============================================================\n-- CLIENTES (700)\n-- ============================================================\n\n"
    
    cliente_ids = []
    for i in range(700):
        cid = str(uuid.uuid4())
        cliente_ids.append(cid)
        preventista = PREVENTISTAS[i % len(PREVENTISTAS)]
        localidad, provincia, lat, lon = random.choice(LOCALIDADES)
        calle = random.choice(CALLES)
        numero = random.randint(100, 9999)
        nombre = f"{random.choice(NOMBRES_NEGOCIOS)} {i+1:03d}"
        cuit = f"{random.randint(20, 30)}-{random.randint(10000000, 99999999)}-{random.randint(0, 9)}"
        telefono = f"0261 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        condicion_iva = random.choice(['RI', 'M', 'CF'])
        
        output += f"INSERT OR IGNORE INTO clientes (id, razon_social, cuit, condicion_iva, domicilio, telefono, email, localidad, provincia, calle, numero, latitud, longitud, preventista_id, activo) VALUES ('{cid}', '{nombre}', '{cuit}', '{condicion_iva}', '{calle} {numero}, {localidad}, {provincia}', '{telefono}', 'ventas_{i:03d}@gmail.com', '{localidad}', '{provincia}', '{calle}', '{numero}', {lat + random.uniform(-0.01, 0.01)}, {lon + random.uniform(-0.01, 0.01)}, '{preventista_ids[preventista[0]]}', 1);\n"
    
    # NOTAS DE VENTA (500)
    output += "\n-- ============================================================\n-- NOTAS DE VENTA (500)\n-- ============================================================\n\n"
    
    for i in range(500):
        nota_id = str(uuid.uuid4())
        preventista_id = random.choice(list(preventista_ids.values()))
        cliente_id = random.choice(cliente_ids)
        
        days = (FECHA_FIN - FECHA_INICIO).days
        fecha = FECHA_INICIO + timedelta(days=random.randint(0, days))
        fecha_str = fecha.isoformat()
        numero_nota = f"NOTA-{fecha.strftime('%Y%m')}-{i+1:04d}"
        
        output += f"INSERT OR IGNORE INTO notas_venta (id, preventista_id, cliente_id, fecha, numero_nota, total, estado, procesado_central) VALUES ('{nota_id}', '{preventista_id}', '{cliente_id}', '{fecha_str}', '{numero_nota}', 0, 'PROCESADA', 1);\n"
        
        total_nota = 0
        num_detalles = random.randint(1, 8)
        for j in range(num_detalles):
            detalle_id = str(uuid.uuid4())
            prod_id = random.choice(producto_ids)
            prod_idx = producto_ids.index(prod_id)
            precio = PRODUCTOS[prod_idx][3]
            cantidad = random.randint(1, 10)
            subtotal = cantidad * precio
            total_nota += subtotal
            codigo = PRODUCTOS[prod_idx][0]
            
            output += f"INSERT OR IGNORE INTO nota_venta_detalle (id, nota_venta_id, producto_id, codigo_producto, cantidad, precio_unitario) VALUES ('{detalle_id}', '{nota_id}', '{prod_id}', '{codigo}', {cantidad}, {precio});\n"
        
        output += f"UPDATE notas_venta SET total = {total_nota} WHERE id = '{nota_id}';\n"
    
    output += "\nPRAGMA foreign_keys = ON;\n"
    
    # Guardar
    with open('script_con_uuid.sql', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print("✅ Script generado: script_con_uuid.sql")
    print(f"   Notas: 500")
    print(f"   Productos: {len(PRODUCTOS)}")
    print(f"   Preventistas: {len(PREVENTISTAS)}")
    print(f"   Clientes: 700")
    print(f"   Todas las claves primarias son UUIDs reales")

if __name__ == "__main__":
    generar_script()
