PRAGMA foreign_keys = OFF;

CREATE TABLE IF NOT EXISTS parametros (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    moneda TEXT NOT NULL DEFAULT 'ARS',
    nombre_distribuidora TEXT,
    direccion TEXT,
    telefono1 TEXT,
    telefono2 TEXT,
    whatsapp TEXT,
    email TEXT,
    logo BLOB,
    encabezado_factura TEXT,
    encabezado_reporte TEXT,
    tasa_municipal_porcentaje REAL DEFAULT 0.0,
    punto_venta TEXT DEFAULT '0001',
    ultimo_numero_factura INTEGER DEFAULT 1,
    calle TEXT,
    numero TEXT,
    localidad TEXT,
    provincia TEXT,
    pais TEXT DEFAULT 'Argentina',
    latitud REAL,
    longitud REAL,
    escala_visual REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO parametros (id, moneda, nombre_distribuidora, punto_venta, ultimo_numero_factura, escala_visual) 
VALUES (1, 'ARS', 'Tregar Mendoza S.A.', '0001', 1, 1.0);

CREATE TABLE IF NOT EXISTS categorias (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO categorias (id, nombre) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'Arroz con Leche'),
('550e8400-e29b-41d4-a716-446655440002', 'Cremas'),
('550e8400-e29b-41d4-a716-446655440003', 'Dulce de Leche'),
('550e8400-e29b-41d4-a716-446655440004', 'Leches'),
('550e8400-e29b-41d4-a716-446655440005', 'Leches en Polvo'),
('550e8400-e29b-41d4-a716-446655440006', 'Leches Saborizadas'),
('550e8400-e29b-41d4-a716-446655440007', 'Mascarpone'),
('550e8400-e29b-41d4-a716-446655440008', 'Quesos Blandos'),
('550e8400-e29b-41d4-a716-446655440009', 'Quesos Duros'),
('550e8400-e29b-41d4-a716-446655440010', 'Quesos Rallados'),
('550e8400-e29b-41d4-a716-446655440011', 'Quesos Semi Duros'),
('550e8400-e29b-41d4-a716-446655440012', 'Quesos Untables'),
('550e8400-e29b-41d4-a716-446655440013', 'Quesos Untables Blancos'),
('550e8400-e29b-41d4-a716-446655440014', 'Ricottas'),
('550e8400-e29b-41d4-a716-446655440015', 'Yogures Bebibles'),
('550e8400-e29b-41d4-a716-446655440016', 'Yogures con Topping'),
('550e8400-e29b-41d4-a716-446655440017', 'Yogures Cuchareables'),
('550e8400-e29b-41d4-a716-446655440018', 'Yogures Firmes'),
('550e8400-e29b-41d4-a716-446655440019', 'Yogures Naturales');

CREATE TABLE IF NOT EXISTS preventistas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    legajo TEXT UNIQUE,
    telefono TEXT,
    email TEXT,
    zona TEXT,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO preventistas (id, nombre, apellido, legajo, telefono, email, zona, activo) VALUES 
('a57df699-ef89-48ef-b124-455d2054e0dd', 'Ariel', 'Mazara', 'P002', '0261-1234-1002', 'ariel.mazara@tregar.com', 'Valle de Uco', 1),
('0cfb380d-fdf0-48e0-967b-6f752e1431e4', 'Agustina', 'Zuniga', 'P003', '0261-1234-1003', 'agustina.zuniga@tregar.com', 'Centro Mendoza', 1),
('590f73dd-8cbe-4ef0-bfd7-72456ff895fa', 'Maximiliano', 'Morales', 'P004', '0261-1234-1004', 'maximiliano.morales@tregar.com', 'Sur Mendoza', 1),
('a9595c0a-bf4f-4800-8ce0-701728ba49c2', 'Santino', 'Mamani', 'P005', '0261-1234-1005', 'santino.mamani@tregar.com', 'Este Mendoza', 1),
('736ea2f0-4fb4-4337-b840-3e5fc8aa4e85', 'Joel', 'Gonzalez', 'P006', '0261-1234-1006', 'joel.gonzalez@tregar.com', 'Sur Mendoza', 1),
('6949aca7-4a39-469f-acc3-43e1b0165fee', 'Daniel', 'Silva', 'P007', '0264-1234-1007', 'daniel.silva@tregar.com', 'San Juan', 1),
('2f7e38a1-62a5-48ea-9e12-fac0e68110a9', 'Damian', 'Ponce de Leon', 'P008', '0266-1234-1008', 'damian.poncedeleon@tregar.com', 'San Luis', 1);

CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT CHECK(rol IN ('preventista','admin','cliente')) DEFAULT 'preventista',
    preventista_id TEXT REFERENCES preventistas(id),
    cliente_id TEXT REFERENCES clientes(id),
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO usuarios (id, username, password_hash, rol, preventista_id, activo) VALUES
('00000000-0000-0000-0000-000000000001', 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', NULL, 1);

INSERT OR IGNORE INTO usuarios (id, username, password_hash, rol, preventista_id, activo) VALUES 
('d4f5c8e2-7a1b-4c3d-9e8f-6a2b4c8e0d1f', 'prev001', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', 'a57df699-ef89-48ef-b124-455d2054e0dd', 1),
('e5f6d9c3-8b2c-4d4e-a0f9-7b3c5d9e1f2a', 'prev002', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', '0cfb380d-fdf0-48e0-967b-6f752e1431e4', 1),
('f6g7e0d4-9c3d-4e5f-b1g0-8c4d6e0f2g3b', 'prev003', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', '590f73dd-8cbe-4ef0-bfd7-72456ff895fa', 1),
('g7h8f1e5-0d4e-5f6g-c2h1-9d5e7f1g3h4c', 'prev004', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', 'a9595c0a-bf4f-4800-8ce0-701728ba49c2', 1),
('h8i9g2f6-1e5f-6g7h-d3i2-0e6f8g2h4i5d', 'prev005', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', '736ea2f0-4fb4-4337-b840-3e5fc8aa4e85', 1),
('i9j0h3g7-2f6g-7h8i-e4j3-1f7g9h3i5j6e', 'prev006', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', '6949aca7-4a39-469f-acc3-43e1b0165fee', 1),
('j0k1i4h8-3g7h-8i9j-f5k4-2g8h0i4j6k7f', 'prev007', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'preventista', '2f7e38a1-62a5-48ea-9e12-fac0e68110a9', 1);

CREATE TABLE IF NOT EXISTS productos (
    id TEXT PRIMARY KEY,
    codigo_producto TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    precio_costo REAL DEFAULT 0,
    precio_venta REAL DEFAULT 0,
    stock_actual REAL DEFAULT 0,
    stock_critico REAL DEFAULT 0,
    unidad_medida TEXT DEFAULT 'unidad',
    categoria_id TEXT REFERENCES categorias(id),
    foto BLOB,
    url_foto TEXT,
    detalle TEXT,
    precio_oferta REAL,
    destacado INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clientes (
    id TEXT PRIMARY KEY,
    razon_social TEXT NOT NULL,
    cuit TEXT UNIQUE,
    condicion_iva TEXT CHECK(condicion_iva IN ('RI','M','EX','CF','MT')) DEFAULT 'RI',
    domicilio TEXT,
    telefono TEXT,
    whatsapp TEXT,
    email TEXT,
    aplica_tasa_municipal BOOLEAN DEFAULT 0,
    limite_credito REAL DEFAULT 0,
    saldo_cuenta_corriente REAL DEFAULT 0,
    fecha_alta DATE DEFAULT (date('now')),
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    latitud REAL,
    longitud REAL,
    preventista_id TEXT,
    localidad TEXT,
    provincia TEXT,
    calle TEXT,
    numero TEXT
);

CREATE TABLE IF NOT EXISTS lotes (
    id TEXT PRIMARY KEY,
    producto_id TEXT NOT NULL REFERENCES productos(id),
    codigo_producto TEXT,
    numero_lote TEXT,
    fecha_vencimiento DATE NOT NULL,
    cantidad_inicial REAL NOT NULL,
    cantidad_actual REAL NOT NULL,
    fecha_ingreso DATE DEFAULT (date('now')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS notas_venta (
    id TEXT PRIMARY KEY,
    preventista_id TEXT NOT NULL REFERENCES preventistas(id),
    cliente_id TEXT NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    numero_nota TEXT UNIQUE,
    total REAL DEFAULT 0,
    observaciones TEXT,
    estado TEXT DEFAULT 'PENDIENTE',
    procesado_central BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS nota_venta_detalle (
    id TEXT PRIMARY KEY,
    nota_venta_id TEXT NOT NULL REFERENCES notas_venta(id),
    producto_id TEXT,
    codigo_producto TEXT NOT NULL,
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS facturas (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes(id),
    preventista_id TEXT REFERENCES preventistas(id),
    tipo_comprobante TEXT CHECK(tipo_comprobante IN ('A','B','C','X')) DEFAULT 'B',
    numero_factura TEXT NOT NULL UNIQUE,
    fecha DATE DEFAULT (date('now')),
    subtotal REAL DEFAULT 0,
    iva REAL DEFAULT 0,
    tasa_municipal REAL DEFAULT 0,
    total REAL DEFAULT 0,
    observaciones TEXT,
    nota_venta_id TEXT REFERENCES notas_venta(id),
    estado TEXT DEFAULT 'EMITIDA',
    saldo_anterior_cliente REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS factura_detalle (
    id TEXT PRIMARY KEY,
    factura_id TEXT NOT NULL REFERENCES facturas(id),
    producto_id TEXT NOT NULL REFERENCES productos(id),
    codigo_producto TEXT NOT NULL,
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cuenta_corriente_movimientos (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('FACTURA','COBRO','NOTA_CREDITO','AJUSTE','ANULACION','REVERSO_COBRO')),
    referencia_id TEXT,
    importe REAL NOT NULL,
    saldo_resultante REAL NOT NULL,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cobros (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    importe REAL NOT NULL,
    medio_pago TEXT,
    tipo_pago TEXT DEFAULT 'EFECTIVO',
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS cheques (
    id TEXT PRIMARY KEY,
    cobro_id TEXT NOT NULL REFERENCES cobros(id),
    cliente_id TEXT NOT NULL REFERENCES clientes(id),
    banco TEXT NOT NULL,
    numero_cheque TEXT NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    importe REAL NOT NULL,
    estado TEXT DEFAULT 'EN_CARTERA',
    fecha_acreditacion DATE,
    vendido_a TEXT,
    factura_ids TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS posiciones_preventistas (
    id TEXT PRIMARY KEY,
    preventista_id TEXT NOT NULL REFERENCES preventistas(id),
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS visitas_clientes (
    id TEXT PRIMARY KEY,
    preventista_id TEXT NOT NULL REFERENCES preventistas(id),
    cliente_id TEXT NOT NULL REFERENCES clientes(id),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitud REAL,
    longitud REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sync_log (
    tabla TEXT PRIMARY KEY,
    last_timestamp TEXT DEFAULT '1970-01-01T00:00:00'
);

CREATE TABLE IF NOT EXISTS sync_log_reverse (
    tabla TEXT PRIMARY KEY,
    last_timestamp TEXT DEFAULT '1970-01-01T00:00:00'
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    args TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retries INTEGER DEFAULT 0,
    last_error TEXT,
    next_retry TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sync_log_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    args TEXT,
    success BOOLEAN,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sync_conflictos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla TEXT NOT NULL,
    registro_id TEXT NOT NULL,
    version_local INTEGER,
    version_remota INTEGER,
    resolucion TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pedidos_procesados (
    id TEXT PRIMARY KEY,
    factura_id TEXT NOT NULL UNIQUE REFERENCES facturas(id),
    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    procesado_por TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO sync_log (tabla) VALUES 
('clientes'), ('productos'), ('preventistas'), ('categorias'), ('lotes'), ('usuarios');

INSERT OR IGNORE INTO sync_log_reverse (tabla) VALUES 
('notas_venta'), ('nota_venta_detalle');

CREATE TRIGGER IF NOT EXISTS update_parametros_updated_at AFTER UPDATE ON parametros
BEGIN UPDATE parametros SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_categorias_updated_at AFTER UPDATE ON categorias
BEGIN UPDATE categorias SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_productos_updated_at AFTER UPDATE ON productos
BEGIN UPDATE productos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_lotes_updated_at AFTER UPDATE ON lotes
BEGIN UPDATE lotes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_clientes_updated_at AFTER UPDATE ON clientes
BEGIN UPDATE clientes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_preventistas_updated_at AFTER UPDATE ON preventistas
BEGIN UPDATE preventistas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_usuarios_updated_at AFTER UPDATE ON usuarios
BEGIN UPDATE usuarios SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_notas_venta_updated_at AFTER UPDATE ON notas_venta
BEGIN UPDATE notas_venta SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_nota_venta_detalle_updated_at AFTER UPDATE ON nota_venta_detalle
BEGIN UPDATE nota_venta_detalle SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_facturas_updated_at AFTER UPDATE ON facturas
BEGIN UPDATE facturas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_factura_detalle_updated_at AFTER UPDATE ON factura_detalle
BEGIN UPDATE factura_detalle SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_cuenta_corriente_movimientos_updated_at AFTER UPDATE ON cuenta_corriente_movimientos
BEGIN UPDATE cuenta_corriente_movimientos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_cobros_updated_at AFTER UPDATE ON cobros
BEGIN UPDATE cobros SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_cheques_updated_at AFTER UPDATE ON cheques
BEGIN UPDATE cheques SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

PRAGMA foreign_keys = ON;
