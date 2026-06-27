"""
Código Crítico - Tercer Semestre Año 2026
Gestor de la base de datos SQLite.
"""

import sqlite3
import os
import sys

_NOMBRE_BD = "distribuidora.db"

def _ruta_base_datos() -> str:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, _NOMBRE_BD)

def _cargar_script_sql() -> str:
    import sys
    posibles_rutas = []
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        posibles_rutas = [
            os.path.join(base_dir, "db", "script_creacion.sql"),
            os.path.join(base_dir, "script_creacion.sql"),
            os.path.join(os.path.dirname(__file__), "script_creacion.sql"),
        ]
    else:
        posibles_rutas = [
            os.path.join(os.path.dirname(__file__), "script_creacion.sql"),
            os.path.join(os.getcwd(), "db", "script_creacion.sql"),
        ]
    for sql_path in posibles_rutas:
        if os.path.exists(sql_path):
            with open(sql_path, "r", encoding="utf-8") as f:
                return f.read()
    raise FileNotFoundError(f"No se encontró el script SQL. Buscado en: {posibles_rutas}")

def _tablas_existen(conexion) -> bool:
    try:
        cur = conexion.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parametros'")
        return cur.fetchone() is not None
    except:
        return False

def aplicar_migraciones():
    ruta = _ruta_base_datos()
    if not os.path.exists(ruta):
        print("⚠️ Base de datos no existe. Se creará al inicializar.")
        return
    conexion = sqlite3.connect(ruta)
    try:
        # Migración 1
        try:
            conexion.execute("ALTER TABLE cobros ADD COLUMN tipo_pago TEXT DEFAULT 'EFECTIVO';")
            conexion.commit()
            print("Migración 1: columna tipo_pago agregada a cobros.")
        except sqlite3.OperationalError:
            pass

        # Migración 2
        try:
            conexion.execute("ALTER TABLE parametros ADD COLUMN punto_venta TEXT DEFAULT '0001';")
            conexion.execute("ALTER TABLE parametros ADD COLUMN ultimo_numero_factura INTEGER DEFAULT 1;")
            conexion.commit()
            print("Migración 2: columnas punto_venta y ultimo_numero_factura agregadas.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise e

        # Migración 3
        conexion.execute("CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(descripcion);")
        conexion.execute("CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria_id);")
        conexion.commit()

        # Migración 4
        try:
            for col, tipo in [("whatsapp", "TEXT"), ("latitud", "REAL"), ("longitud", "REAL"),
                              ("preventista_id", "INTEGER"), ("localidad", "TEXT"), ("provincia", "TEXT"),
                              ("calle", "TEXT"), ("numero", "TEXT")]:
                try:
                    conexion.execute(f"ALTER TABLE clientes ADD COLUMN {col} {tipo};")
                except sqlite3.OperationalError:
                    pass
            conexion.executescript("""
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
                CREATE TABLE IF NOT EXISTS posiciones_preventistas (
                    id TEXT PRIMARY KEY,
                    preventista_id INTEGER NOT NULL,
                    latitud REAL NOT NULL,
                    longitud REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS visitas_clientes (
                    id TEXT PRIMARY KEY,
                    preventista_id INTEGER NOT NULL,
                    cliente_id INTEGER NOT NULL,
                    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    latitud REAL,
                    longitud REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conexion.executescript("""
                INSERT OR IGNORE INTO usuarios (username, password_hash, rol) 
                VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin');
                INSERT OR IGNORE INTO preventistas (id, nombre, apellido, legajo) VALUES (1, 'Juan', 'Perez', 'P001');
                INSERT OR IGNORE INTO usuarios (username, password_hash, rol, preventista_id) 
                VALUES ('preventista1', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'preventista', 1);
                INSERT OR IGNORE INTO clientes (id, razon_social, cuit, latitud, longitud, localidad, provincia) 
                VALUES (1, 'Cliente Ejemplo', '20-12345678-9', -34.6037, -58.3816, 'CABA', 'Buenos Aires');
            """)
            conexion.commit()
            print("Migración 4: geolocalización, usuarios y datos iniciales agregados.")
        except Exception as e:
            print(f"Error en migración 4: {e}")

        # Migración 5
        try:
            conexion.execute("ALTER TABLE clientes ADD COLUMN calle TEXT;")
            conexion.execute("ALTER TABLE clientes ADD COLUMN numero TEXT;")
            conexion.commit()
            print("Migración 5: columnas calle y numero agregadas a clientes.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise e

        # Migración 6
        try:
            cur = conexion.cursor()
            cur.execute("PRAGMA table_info(parametros)")
            columnas_existentes = [row[1] for row in cur.fetchall()]
            columnas_nuevas = [
                ("calle", "TEXT"), ("numero", "TEXT"), ("localidad", "TEXT"),
                ("provincia", "TEXT"), ("pais", "TEXT DEFAULT 'Argentina'"),
                ("latitud", "REAL"), ("longitud", "REAL")
            ]
            for col, tipo in columnas_nuevas:
                if col not in columnas_existentes:
                    conexion.execute(f"ALTER TABLE parametros ADD COLUMN {col} {tipo}")
            conexion.commit()
        except Exception as e:
            print(f"Error en migración 6: {e}")

        # Migración 7
        try:
            cur = conexion.cursor()
            cur.execute("PRAGMA table_info(parametros)")
            columnas_existentes = [row[1] for row in cur.fetchall()]
            columnas_contacto = [("telefono1", "TEXT"), ("telefono2", "TEXT"), ("whatsapp", "TEXT"), ("email", "TEXT")]
            for col, tipo in columnas_contacto:
                if col not in columnas_existentes:
                    conexion.execute(f"ALTER TABLE parametros ADD COLUMN {col} {tipo}")
            conexion.commit()
        except Exception as e:
            print(f"Error en migración 7: {e}")

        # Migración 8
        try:
            conexion.execute("ALTER TABLE facturas ADD COLUMN saldo_anterior_cliente REAL DEFAULT 0;")
            conexion.commit()
            print("Migración 8: columna saldo_anterior_cliente agregada a facturas.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise e

        # Migración 9
        try:
            conexion.executescript("""
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
                CREATE INDEX IF NOT EXISTS idx_sync_queue_next_retry ON sync_queue(next_retry);
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
                CREATE TABLE IF NOT EXISTS sync_log (tabla TEXT PRIMARY KEY, last_timestamp TEXT DEFAULT '1970-01-01T00:00:00');
                CREATE TABLE IF NOT EXISTS sync_log_reverse (tabla TEXT PRIMARY KEY, last_timestamp TEXT DEFAULT '1970-01-01T00:00:00');
            """)
            conexion.commit()
            print("Migración 9: tablas de sincronización creadas.")
        except Exception as e:
            print(f"Error en migración 9: {e}")

        # Migración 10
        try:
            conexion.executescript("""
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
            """)
            conexion.commit()
            print("Migración 10: triggers de updated_at creados.")
        except Exception as e:
            print(f"Error en migración 10: {e}")

        # Migración 11
        try:
            conexion.executescript("""
                INSERT OR IGNORE INTO sync_log (tabla) VALUES 
                ('clientes'),('productos'),('preventistas'),('categorias'),
                ('lotes'),('notas_venta'),('nota_venta_detalle'),('facturas'),
                ('factura_detalle'),('cuenta_corriente_movimientos'),('cobros'),('cheques'),
                ('usuarios'),('posiciones_preventistas'),('visitas_clientes');
                INSERT OR IGNORE INTO sync_log_reverse (tabla) VALUES 
                ('clientes'),('productos'),('preventistas'),('categorias'),('usuarios'),
                ('visitas_clientes');
            """)
            conexion.commit()
            print("Migración 11: datos iniciales sync_log insertados.")
        except Exception as e:
            print(f"Error en migración 11: {e}")

        # Migración 12
        try:
            conexion.execute("CREATE INDEX IF NOT EXISTS idx_notas_venta_procesado ON notas_venta(procesado_central);")
            conexion.execute("CREATE INDEX IF NOT EXISTS idx_notas_venta_created_at ON notas_venta(created_at);")
            conexion.commit()
            print("Migración 12: índices de notas_venta creados.")
        except Exception as e:
            print(f"Error en migración 12: {e}")

        # Migración 13
        try:
            conexion.executescript("""
                CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATE NOT NULL,
                    categoria TEXT NOT NULL,
                    descripcion TEXT,
                    importe REAL NOT NULL,
                    tipo TEXT DEFAULT 'OPERATIVO',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS otros_ingresos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATE NOT NULL,
                    concepto TEXT NOT NULL,
                    importe REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS proyecciones_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    porcentaje_crecimiento_mensual REAL DEFAULT 5.0,
                    meses_proyeccion INTEGER DEFAULT 6
                );
                INSERT OR IGNORE INTO proyecciones_config (id, porcentaje_crecimiento_mensual, meses_proyeccion)
                VALUES (1, 5.0, 6);
            """)
            conexion.commit()
            print("Migración 13: tablas de rentabilidad creadas.")
        except Exception as e:
            print(f"Error en migración 13: {e}")

        # Migración 14: escala_visual
        try:
            conexion.execute("ALTER TABLE parametros ADD COLUMN escala_visual REAL DEFAULT 1.0;")
            conexion.commit()
            print("Migración 14: columna escala_visual agregada a parametros.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                pass
            else:
                raise e

        # Migración 15: Tabla de pedidos para armar
        try:
            conexion.executescript("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id TEXT PRIMARY KEY,
                    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
                    fecha_pedido DATE DEFAULT (date('now')),
                    estado TEXT DEFAULT 'PENDIENTE',
                    total REAL DEFAULT 0,
                    observaciones TEXT,
                    nota_venta_id TEXT,
                    factura_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS pedido_detalle (
                    id TEXT PRIMARY KEY,
                    pedido_id TEXT NOT NULL REFERENCES pedidos(id),
                    producto_id INTEGER NOT NULL REFERENCES productos(id),
                    cantidad REAL NOT NULL,
                    precio_unitario REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
                CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos(cliente_id);
                CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_pedido);
            """)
            conexion.commit()
            print("Migración 15: tabla pedidos creada.")
        except Exception as e:
            print(f"Error en migración 15: {e}")

        # Migración 16: Tabla de pedidos_procesados (historial de pedidos armados)
        try:
            conexion.executescript("""
                CREATE TABLE IF NOT EXISTS pedidos_procesados (
                    id TEXT PRIMARY KEY,
                    factura_id TEXT NOT NULL UNIQUE,
                    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    procesado_por TEXT,
                    observaciones TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_pedidos_procesados_factura ON pedidos_procesados(factura_id);
                CREATE INDEX IF NOT EXISTS idx_pedidos_procesados_fecha ON pedidos_procesados(fecha_procesado);
            """)
            conexion.commit()
            print("Migración 16: tabla pedidos_procesados creada.")
        except Exception as e:
            print(f"Error en migración 16: {e}")

        # ============================================================
        # MIGRACIÓN 17: agregar codigo_producto a nota_venta_detalle
        # ============================================================
        try:
            conexion.execute("ALTER TABLE nota_venta_detalle ADD COLUMN codigo_producto TEXT;")
            conexion.commit()
            print("Migración 17: columna codigo_producto agregada a nota_venta_detalle.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise e

    finally:
        conexion.close()

def inicializar_bd():
    ruta = _ruta_base_datos()
    db_ya_inicializada = False
    if os.path.exists(ruta):
        try:
            conexion = sqlite3.connect(ruta)
            db_ya_inicializada = _tablas_existen(conexion)
            conexion.close()
        except:
            pass
    if db_ya_inicializada:
        print("✅ Base de datos ya inicializada.")
        aplicar_migraciones()
        return
    print("📁 Creando base de datos...")
    conexion = sqlite3.connect(ruta)
    try:
        script = _cargar_script_sql()
        conexion.executescript(script)
        conexion.commit()
        print("✅ Base de datos creada correctamente.")
    except Exception as e:
        print(f"❌ Error al ejecutar script: {e}")
        raise
    finally:
        conexion.close()
    aplicar_migraciones()

def obtener_conexion() -> sqlite3.Connection:
    ruta = _ruta_base_datos()
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    conexion.row_factory = sqlite3.Row
    return conexion