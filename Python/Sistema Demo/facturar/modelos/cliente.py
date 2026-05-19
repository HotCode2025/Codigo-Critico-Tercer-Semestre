"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Cliente: representa y gestiona la tabla 'clientes'.
"""
import sqlite3
from datetime import date
from typing import List, Optional, Dict, Any

class Cliente:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, razon_social: str, cuit: str, condicion_iva: str = 'RI',
              domicilio: str = None, telefono: str = None, email: str = None,
              aplica_tasa_municipal: bool = False, limite_credito: float = 0.0) -> int:
        """Inserta un nuevo cliente y retorna su ID."""
        query = """INSERT INTO clientes (razon_social, cuit, condicion_iva, domicilio,
                    telefono, email, aplica_tasa_municipal, limite_credito, fecha_alta)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (razon_social, cuit, condicion_iva, domicilio,
                            telefono, email, int(aplica_tasa_municipal),
                            limite_credito, date.today().isoformat()))
        self.db.commit()
        return cur.lastrowid

    def obtener_por_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        if solo_activos:
            cur.execute("SELECT * FROM clientes WHERE activo = 1")
        else:
            cur.execute("SELECT * FROM clientes")
        return [dict(row) for row in cur.fetchall()]

    def actualizar(self, cliente_id: int, **campos) -> bool:
        """Actualiza campos específicos del cliente."""
        if not campos:
            return False
        sets = ", ".join(f"{k} = ?" for k in campos.keys())
        valores = list(campos.values())
        valores.append(cliente_id)
        cur = self.db.cursor()
        cur.execute(f"UPDATE clientes SET {sets} WHERE id = ?", valores)
        self.db.commit()
        return cur.rowcount > 0

    def eliminar(self, cliente_id: int) -> bool:
        """Marca al cliente como inactivo (baja lógica)."""
        return self.actualizar(cliente_id, activo=0)

    def buscar_por_cuit(self, cuit: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM clientes WHERE cuit = ?", (cuit,))
        row = cur.fetchone()
        return dict(row) if row else None