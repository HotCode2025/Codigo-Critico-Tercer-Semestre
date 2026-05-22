"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Preventistas.
Lógica de negocio para gestionar preventistas.
"""
import sqlite3
from typing import List, Optional, Dict, Any
from modelos.preventista import Preventista


class ControladorPreventistas:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.modelo = Preventista(db)

    def crear_preventista(self, nombre: str, apellido: str,
                          legajo: str = None, telefono: str = None,
                          email: str = None, zona: str = None) -> int:
        """Crea un preventista validando nombre y apellido."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            raise ValueError("El apellido es obligatorio.")
        return self.modelo.crear(nombre.strip(), apellido.strip(),
                                 legajo.strip() if legajo else None,
                                 telefono.strip() if telefono else None,
                                 email.strip() if email else None,
                                 zona.strip() if zona else None)

    def modificar_preventista(self, preventista_id: int, **campos) -> bool:
        return self.modelo.actualizar(preventista_id, **campos)

    def eliminar_preventista(self, preventista_id: int) -> bool:
        return self.modelo.eliminar(preventista_id)

    def listar_preventistas(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        return self.modelo.listar_todos(solo_activos=solo_activos)

    def obtener_preventista(self, preventista_id: int) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_id(preventista_id)