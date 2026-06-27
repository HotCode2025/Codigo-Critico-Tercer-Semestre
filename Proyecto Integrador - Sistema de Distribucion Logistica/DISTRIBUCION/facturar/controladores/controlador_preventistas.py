"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Preventistas – ahora sincroniza directamente con Turso.
"""

import sqlite3
from typing import List, Optional, Dict, Any
from modelos.preventista import Preventista
from utilidades.central_sync import enviar_a_turso


class ControladorPreventistas:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.modelo = Preventista(db)

    def crear_preventista(self, nombre: str, apellido: str,
                          legajo: str = None, telefono: str = None,
                          email: str = None, zona: str = None) -> int:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            raise ValueError("El apellido es obligatorio.")

        preventista_id = self.modelo.crear(
            nombre.strip(), apellido.strip(),
            legajo.strip() if legajo else None,
            telefono.strip() if telefono else None,
            email.strip() if email else None,
            zona.strip() if zona else None
        )

        enviar_a_turso(
            """INSERT INTO preventistas (nombre, apellido, legajo, telefono, email, zona)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [nombre.strip(), apellido.strip(),
             legajo.strip() if legajo else None,
             telefono.strip() if telefono else None,
             email.strip() if email else None,
             zona.strip() if zona else None]
        )

        return preventista_id

    def modificar_preventista(self, preventista_id: int, **campos) -> bool:
        resultado = self.modelo.actualizar(preventista_id, **campos)
        if campos:
            set_clause = ", ".join(f"{col} = ?" for col in campos.keys())
            valores = list(campos.values())
            valores.append(preventista_id)
            enviar_a_turso(
                f"UPDATE preventistas SET {set_clause} WHERE id = ?",
                valores
            )
        return resultado

    def eliminar_preventista(self, preventista_id: int) -> bool:
        resultado = self.modelo.eliminar(preventista_id)
        enviar_a_turso(
            "UPDATE preventistas SET activo = 0 WHERE id = ?",
            [preventista_id]
        )
        return resultado

    def listar_preventistas(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        return self.modelo.listar_todos(solo_activos=solo_activos)

    def obtener_preventista(self, preventista_id: int) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_id(preventista_id)