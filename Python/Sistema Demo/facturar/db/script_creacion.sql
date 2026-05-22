-- script_creacion.sql
-- Código Crítico - Tercer Semestre Año 2026
-- Script de creación de la base de datos SQLite para el sistema de distribuidora.

-- Tabla de configuración (un solo registro)
CREATE TABLE IF NOT EXISTS parametros (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    moneda TEXT NOT NULL DEFAULT 'ARS',
    nombre_distribuidora TEXT NOT NULL,
    direccion TEXT,
    telefono1 TEXT,
    telefono2 TEXT,
    whatsapp TEXT,
    email TEXT,
    logo BLOB,
    encabezado_factura TEXT,
    encabezado_reporte TEXT,
    tasa_municipal_porcentaje REAL DEFAULT 0.0
);

-- Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    razon_social TEXT NOT NULL,
    cuit TEXT UNIQUE,
    condicion_iva TEXT CHECK(condicion_iva IN ('RI','M','EX','CF','MT')) DEFAULT 'RI',
    domicilio TEXT,
    telefono TEXT,
    email TEXT,
    aplica_tasa_municipal BOOLEAN DEFAULT 0,
    limite_credito REAL DEFAULT 0,
    saldo_cuenta_corriente REAL DEFAULT 0,
    fecha_alta DATE DEFAULT (date('now')),
    activo BOOLEAN DEFAULT 1
);

-- Preventistas
CREATE TABLE IF NOT EXISTS preventistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    legajo TEXT UNIQUE,
    telefono TEXT,
    email TEXT,
    zona TEXT,
    activo BOOLEAN DEFAULT 1
);

-- Productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    precio_costo REAL DEFAULT 0,
    precio_venta REAL DEFAULT 0,
    stock_actual REAL DEFAULT 0,
    stock_critico REAL DEFAULT 0,
    unidad_medida TEXT DEFAULT 'unidad',
    activo BOOLEAN DEFAULT 1
);

-- Lotes (para manejar vencimientos)
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    numero_lote TEXT,
    fecha_vencimiento DATE NOT NULL,
    cantidad_inicial REAL NOT NULL,
    cantidad_actual REAL NOT NULL,
    fecha_ingreso DATE DEFAULT (date('now')),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Nota de Venta (pedido)
CREATE TABLE IF NOT EXISTS notas_venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preventista_id INTEGER NOT NULL REFERENCES preventistas(id),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    numero_nota TEXT,
    total REAL DEFAULT 0,
    observaciones TEXT,
    estado TEXT DEFAULT 'PENDIENTE' -- PENDIENTE, FACTURADA, ANULADA
);

CREATE TABLE IF NOT EXISTS nota_venta_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nota_venta_id INTEGER NOT NULL REFERENCES notas_venta(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL
);

-- Factura Fiscal
CREATE TABLE IF NOT EXISTS facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    preventista_id INTEGER REFERENCES preventistas(id),
    tipo_comprobante TEXT CHECK(tipo_comprobante IN ('A','B','C','X')) DEFAULT 'B',
    numero_factura TEXT NOT NULL,
    fecha DATE DEFAULT (date('now')),
    subtotal REAL DEFAULT 0,
    iva REAL DEFAULT 0,
    tasa_municipal REAL DEFAULT 0,
    total REAL DEFAULT 0,
    observaciones TEXT,
    nota_venta_id INTEGER REFERENCES notas_venta(id),
    estado TEXT DEFAULT 'EMITIDA'
);

CREATE TABLE IF NOT EXISTS factura_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factura_id INTEGER NOT NULL REFERENCES facturas(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad REAL NOT NULL,
    precio_unitario REAL NOT NULL
);

-- Movimientos de Cuenta Corriente
CREATE TABLE IF NOT EXISTS cuenta_corriente_movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('FACTURA','COBRO','NOTA_CREDITO','AJUSTE')),
    referencia_id INTEGER,
    importe REAL NOT NULL,
    saldo_resultante REAL NOT NULL,
    observaciones TEXT
);

-- Cobros (entregas de dinero)
CREATE TABLE IF NOT EXISTS cobros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha DATE DEFAULT (date('now')),
    importe REAL NOT NULL,
    medio_pago TEXT,
    observaciones TEXT
);

-- Historial de importaciones de catálogo PDF
CREATE TABLE IF NOT EXISTS catalogo_importaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_importacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nombre_archivo TEXT,
    procesado_por TEXT,
    total_productos_nuevos INTEGER DEFAULT 0,
    total_actualizaciones INTEGER DEFAULT 0,
    observaciones TEXT
);