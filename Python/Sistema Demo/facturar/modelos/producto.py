"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Producto: representa y gestiona la tabla 'productos'.
"""
import sqlite3
from typing import List, Optional, Dict, Any

class Producto:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, codigo: str, descripcion: str, precio_costo: float = 0.0,
              precio_venta: float = 0.0, stock_critico: float = 0.0,
              unidad_medida: str = 'unidad') -> int:
        query = """INSERT INTO productos (codigo, descripcion, precio_costo, precio_venta,
                    stock_actual, stock_critico, unidad_medida)
                    VALUES (?, ?, ?, ?, 0, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (codigo, descripcion, precio_costo, precio_venta,
                            stock_critico, unidad_medida))
        self.db.commit()
        return cur.lastrowid

    def obtener_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        if solo_activos:
            cur.execute("SELECT * FROM productos WHERE activo = 1")
        else:
            cur.execute("SELECT * FROM productos")
        return [dict(row) for row in cur.fetchall()]

    def actualizar(self, producto_id: int, **campos) -> bool:
        if not campos:
            return False
        sets = ", ".join(f"{k} = ?" for k in campos.keys())
        valores = list(campos.values())
        valores.append(producto_id)
        cur = self.db.cursor()
        cur.execute(f"UPDATE productos SET {sets} WHERE id = ?", valores)
        self.db.commit()
        return cur.rowcount > 0

    def eliminar(self, producto_id: int) -> bool:
        return self.actualizar(producto_id, activo=0)

    def stock_bajo_minimo(self) -> List[Dict[str, Any]]:
        """Productos cuyo stock actual está por debajo del crítico."""
        cur = self.db.cursor()
        cur.execute("""SELECT * FROM productos WHERE activo = 1
                        AND stock_actual <= stock_critico""")
        return [dict(row) for row in cur.fetchall()]