"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Categoría de productos.
"""

import sqlite3
from typing import List, Optional, Dict, Any


class Categoria:
    """Clase para gestionar la tabla 'categorias'."""

    def __init__(self, db: sqlite3.Connection):
        """
        Inicializa el modelo con una conexión a la base de datos.
        :param db: Conexión activa a SQLite.
        """
        self.db = db
        self.db.row_factory = sqlite3.Row

    def crear(self, nombre: str) -> int:
        """
        Crea una nueva categoría.
        :param nombre: Nombre de la categoría (debe ser único).
        :return: ID de la categoría creada.
        """
        cur = self.db.cursor()
        cur.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre.strip(),))
        self.db.commit()
        return cur.lastrowid

    def listar_todas(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las categorías ordenadas alfabéticamente.
        :return: Lista de diccionarios con los datos de cada categoría.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM categorias ORDER BY nombre")
        return [dict(row) for row in cur.fetchall()]

    def obtener_por_id(self, categoria_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca una categoría por su ID.
        :param categoria_id: ID de la categoría.
        :return: Diccionario con los datos, o None si no existe.
        """
        cur = self.db.cursor()
        cur.execute("SELECT * FROM categorias WHERE id = ?", (categoria_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def eliminar(self, categoria_id: int) -> bool:
        """
        Elimina una categoría por su ID.
        :param categoria_id: ID de la categoría a eliminar.
        :return: True si se eliminó correctamente.
        """
        cur = self.db.cursor()
        cur.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        self.db.commit()
        return cur.rowcount > 0