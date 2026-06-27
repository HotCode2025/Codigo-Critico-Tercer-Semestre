-- ============================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS - UNIFICADO
-- Válido para: App (Tablet) | Central (Turso) | Proveedores
-- ============================================================
-- TODOS LOS SISTEMAS USAN:
--   - codigo_producto como identificador único global
--   - id (INTEGER) como clave primaria interna
--   - UUID (TEXT) para registros distribuidos
--   - foto BLOB para imágenes en la base de datos
-- ============================================================
-- DATOS INICIALES: SOLO usuario admin (sin clientes, sin preventistas)
-- ============================================================

-- ============================================================
-- PARÁMETROS GENERALES (SOLO Central / App)
-- ============================================================

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

-- ============================================================
-- CATEGORÍAS
-- ============================================================

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- ============================================================
-- PRODUCTOS - UNIFICADO (con foto BLOB + url_foto)
-- ============================================================

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_producto TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    precio_costo REAL DEFAULT 0,
    precio_venta REAL DEFAULT 0,
    stock_actual REAL DEFAULT 0,
    stock_critico REAL DEFAULT 0,
    unidad_medida TEXT DEFAULT 'unidad',
    categoria_id INTEGER REFERENCES categorias(id),
    
    -- ============================================================
    -- IMÁGENES: SOPORTE PARA AMBOS MÉTODOS
    -- ============================================================
    foto BLOB,                          -- Imagen directamente en la BD
    url_foto TEXT,                      -- Ruta o URL (para compatibilidad)
    
    detalle TEXT,
    precio_oferta REAL,
    destacado INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Índices para productos
CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo_producto);
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(descripcion);
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);
CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo);

-- ============================================================
-- LOTES - UNIFICADO (con codigo_producto)
-- ============================================================

CREATE TABLE IF NOT EXISTS lotes (
    id TEXT PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    codigo_producto TEXT,                 -- AGREGADO
    numero_lote TEXT,
    fecha_vencimiento DATE NOT NULL,
    cantidad_inicial REAL NOT NULL,
    cantidad_actual REAL NOT NULL,
    fecha_ingreso DATE DEFAULT (date('now')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Índices para lotes
CREATE INDEX IF NOT EXISTS idx_lotes_producto ON lotes(producto_id);
CREATE INDEX IF NOT EXISTS idx_lotes_codigo ON lotes(codigo_producto);
CREATE INDEX IF NOT EXISTS idx_lotes_vencimiento ON lotes(fecha_vencimiento);

-- ============================================================
-- CLIENTES
-- ============================================================

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    preventista_id INTEGER,
    localidad TEXT,
    provincia TEXT,
    calle TEXT,
    numero TEXT
);

-- Índices para clientes
CREATE INDEX IF NOT EXISTS idx_clientes_cuit ON clientes(cuit);
CREATE INDEX IF NOT EXISTS idx_clientes_preventista ON clientes(preventista_id);

-- ============================================================
-- PREVENTISTAS
-- ============================================================

CREATE TABLE IF NOT EXISTS preventistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

-- ============================================================
-- NOTAS DE VENTA
-- ============================================================

CREATE TABLE IF NOT EXISTS notas_venta (
    id TEXT PRIMARY KEY,
    preventista_id INTEGER NOT NULL REFERENCES preventistas(id),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
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

-- Índices para notas de venta
CREATE INDEX IF NOT EXISTS idx_notas_venta_estado ON notas_venta(estado);
CREATE INDEX IF NOT EXISTS idx_notas_venta_fecha ON notas_venta(fecha);
CREATE INDEX IF NOT EXISTS idx_notas_venta_cliente ON notas_venta(cliente_id);

-- ============================================================
-- NOTA VENTA DETALLE - UNIFICADO (codigo_producto)
-- ============================================================

CREATE TABLE IF NOT EXISTS nota_venta_detalle (
    id TEXT PRIMARY KEY,
    nota_venta_id TEXT NOT NULL REFERENCES notas_venta(id),
    producto_id INTEGER,
    codigo_producto TEXT NOT NULL,
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Índices para detalle de notas
CREATE INDEX IF NOT EXISTS idx_nota_detalle_nota ON nota_venta_detalle(nota_venta_id);
CREATE INDEX IF NOT EXISTS idx_nota_detalle_producto ON nota_venta_detalle(producto_id);
CREATE INDEX IF NOT EXISTS idx_nota_detalle_codigo ON nota_venta_detalle(codigo_producto);

-- ============================================================
-- FACTURAS (SOLO Central)
-- ============================================================

CREATE TABLE IF NOT EXISTS facturas (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    preventista_id INTEGER REFERENCES preventistas(id),
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

CREATE INDEX IF NOT EXISTS idx_facturas_cliente ON facturas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_facturas_fecha ON facturas(fecha);
CREATE INDEX IF NOT EXISTS idx_facturas_estado ON facturas(estado);

-- ============================================================
-- FACTURA DETALLE (SOLO Central)
-- ============================================================

CREATE TABLE IF NOT EXISTS factura_detalle (
    id TEXT PRIMARY KEY,
    factura_id TEXT NOT NULL REFERENCES facturas(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    codigo_producto TEXT NOT NULL,        -- UNIFICADO
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_factura_detalle_factura ON factura_detalle(factura_id);
CREATE INDEX IF NOT EXISTS idx_factura_detalle_producto ON factura_detalle(producto_id);
CREATE INDEX IF NOT EXISTS idx_factura_detalle_codigo ON factura_detalle(codigo_producto);

-- ============================================================
-- CUENTA CORRIENTE (SOLO Central)
-- ============================================================

CREATE TABLE IF NOT EXISTS cuenta_corriente_movimientos (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
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

CREATE INDEX IF NOT EXISTS idx_movimientos_cliente ON cuenta_corriente_movimientos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON cuenta_corriente_movimientos(fecha);

-- ============================================================
-- COBROS (SOLO Central)
-- ============================================================

CREATE TABLE IF NOT EXISTS cobros (
    id TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    importe REAL NOT NULL,
    medio_pago TEXT,
    tipo_pago TEXT DEFAULT 'EFECTIVO',
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- ============================================================
-- CHEQUES (SOLO Central)
-- ============================================================

CREATE TABLE IF NOT EXISTS cheques (
    id TEXT PRIMARY KEY,
    cobro_id TEXT NOT NULL REFERENCES cobros(id),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
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

-- ============================================================
-- USUARIOS
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT CHECK(rol IN ('preventista','admin','cliente')) DEFAULT 'preventista',
    preventista_id INTEGER REFERENCES preventistas(id),
    cliente_id INTEGER REFERENCES clientes(id),
    activo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- ============================================================
-- POSICIONES GPS
-- ============================================================

CREATE TABLE IF NOT EXISTS posiciones_preventistas (
    id TEXT PRIMARY KEY,
    preventista_id INTEGER NOT NULL REFERENCES preventistas(id),
    latitud REAL NOT NULL,
    longitud REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_posiciones_preventista ON posiciones_preventistas(preventista_id);
CREATE INDEX IF NOT EXISTS idx_posiciones_timestamp ON posiciones_preventistas(timestamp);

-- ============================================================
-- VISITAS A CLIENTES
-- ============================================================

CREATE TABLE IF NOT EXISTS visitas_clientes (
    id TEXT PRIMARY KEY,
    preventista_id INTEGER NOT NULL REFERENCES preventistas(id),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitud REAL,
    longitud REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_visitas_preventista ON visitas_clientes(preventista_id);
CREATE INDEX IF NOT EXISTS idx_visitas_cliente ON visitas_clientes(cliente_id);

-- ============================================================
-- SINCRONIZACIÓN
-- ============================================================

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

CREATE INDEX IF NOT EXISTS idx_sync_queue_next_retry ON sync_queue(next_retry);

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

CREATE INDEX IF NOT EXISTS idx_sync_conflictos_tabla ON sync_conflictos(tabla);
CREATE INDEX IF NOT EXISTS idx_sync_conflictos_timestamp ON sync_conflictos(timestamp);

-- ============================================================
-- PEDIDOS PARA ARMAR (Central)
-- ============================================================

CREATE TABLE IF NOT EXISTS pedidos_procesados (
    id TEXT PRIMARY KEY,
    factura_id TEXT NOT NULL UNIQUE REFERENCES facturas(id),
    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    procesado_por TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pedidos_procesados_factura ON pedidos_procesados(factura_id);

-- ============================================================
-- TRIGGERS DE ACTUALIZACIÓN (updated_at)
-- ============================================================

CREATE TRIGGER IF NOT EXISTS update_clientes_updated_at AFTER UPDATE ON clientes
BEGIN UPDATE clientes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_preventistas_updated_at AFTER UPDATE ON preventistas
BEGIN UPDATE preventistas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_categorias_updated_at AFTER UPDATE ON categorias
BEGIN UPDATE categorias SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_productos_updated_at AFTER UPDATE ON productos
BEGIN UPDATE productos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

CREATE TRIGGER IF NOT EXISTS update_lotes_updated_at AFTER UPDATE ON lotes
BEGIN UPDATE lotes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

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

CREATE TRIGGER IF NOT EXISTS update_usuarios_updated_at AFTER UPDATE ON usuarios
BEGIN UPDATE usuarios SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; END;

-- ============================================================
-- DATOS INICIALES MÍNIMOS
-- ============================================================
-- SOLO se crea el usuario admin y sus configuraciones mínimas
-- NO se crean clientes, preventistas, productos ni categorías
-- ============================================================

-- ============================================================
-- 1. USUARIO ADMIN (NECESARIO PARA LOGIN)
-- ============================================================
-- Contraseña: admin
-- Hash generado con: hashlib.sha256('admin'.encode()).hexdigest()
-- ============================================================

INSERT OR IGNORE INTO usuarios (username, password_hash, rol) 
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');

-- ============================================================
-- 2. PARÁMETROS GENERALES (NECESARIO PARA FACTURACIÓN)
-- ============================================================

INSERT OR IGNORE INTO parametros (
    id, moneda, nombre_distribuidora, punto_venta, ultimo_numero_factura, escala_visual
) VALUES (
    1, 'ARS', 'Mi Distribuidora', '0001', 1, 1.0
);

-- ============================================================
-- 3. CONTROL DE SINCRONIZACIÓN (NECESARIO PARA SYNC)
-- ============================================================

-- Sync Log (subida)
INSERT OR IGNORE INTO sync_log (tabla) VALUES 
('clientes'),
('productos'),
('preventistas'),
('categorias'),
('lotes'),
('notas_venta'),
('nota_venta_detalle'),
('facturas'),
('factura_detalle'),
('cuenta_corriente_movimientos'),
('cobros'),
('cheques'),
('usuarios'),
('posiciones_preventistas'),
('visitas_clientes');

-- Sync Log Reverse (bajada)
INSERT OR IGNORE INTO sync_log_reverse (tabla) VALUES 
('clientes'),
('productos'),
('preventistas'),
('categorias'),
('usuarios'),
('visitas_clientes');

-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
-- BASE DE DATOS LIMPIA:
--   ✅ Tablas creadas
--   ✅ Usuario admin creado
--   ✅ Parámetros mínimos configurados
--   ✅ Tablas de sincronización inicializadas
--   ❌ SIN clientes de muestra
--   ❌ SIN preventistas de muestra
--   ❌ SIN productos de muestra
--   ❌ SIN categorías de muestra
--   ❌ SIN lotes de muestra
-- ============================================================