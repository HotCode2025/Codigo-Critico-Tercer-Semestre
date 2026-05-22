"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Preventista: representa y gestiona la tabla 'preventistas'.
"""
import sqlite3
from typing import List, Optional, Dict, Any

class Preventista:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, nombre: str, apellido: str, legajo: str = None,
              telefono: str = None, email: str = None, zona: str = None) -> int:
        query = """INSERT INTO preventistas (nombre, apellido, legajo, telefono, email, zona)
                   VALUES (?, ?, ?, ?, ?, ?)"""
        cur = self.db.cursor()
        cur.execute(query, (nombre, apellido, legajo, telefono, email, zona))
        self.db.commit()
        return cur.lastrowid

    def obtener_por_id(self, preventista_id: int) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("SELECT * FROM preventistas WHERE id = ?", (preventista_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        if solo_activos:
            cur.execute("SELECT * FROM preventistas WHERE activo = 1")
        else:
            cur.execute("SELECT * FROM preventistas")
        return [dict(row) for row in cur.fetchall()]

    def actualizar(self, preventista_id: int, **campos) -> bool:
        if not campos:
            return False
        sets = ", ".join(f"{k} = ?" for k in campos.keys())
        valores = list(campos.values())
        valores.append(preventista_id)
        cur = self.db.cursor()
        cur.execute(f"UPDATE preventistas SET {sets} WHERE id = ?", valores)
        self.db.commit()
        return cur.rowcount > 0

    def eliminar(self, preventista_id: int) -> bool:
        return self.actualizar(preventista_id, activo=0)