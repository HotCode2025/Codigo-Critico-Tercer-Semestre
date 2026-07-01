"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.5: Modelo de Categoría con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'categorias'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Sincronización: Central → Turso → App
"""

from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Categoria(ModeloBase):
    """
    Modelo para gestionar categorías de productos.
    
    Ejemplo:
        categoria = Categoria(db)
        categoria_id = categoria.crear(nombre="Bebidas")
    """
    
    def __init__(self, db):
        """Inicializa el modelo de categoría"""
        super().__init__(db)
        self._tabla = "categorias"
    
    def crear(self, nombre: str, descripcion: str = None) -> str:
        """
        Crea una nueva categoría con UUID.
        
        Returns:
            str: UUID de la categoría creada
        """
        categoria_id = self.generar_uuid()
        
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO categorias (id, nombre, descripcion) VALUES (?, ?, ?)",
            (categoria_id, nombre.strip(), descripcion)
        )
        self.db.commit()
        return categoria_id
    
    def obtener_por_id(self, categoria_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una categoría por su UUID"""
        return super().obtener_por_id(self._tabla, categoria_id)
    
    def obtener_por_nombre(self, nombre: str) -> Optional[Dict[str, Any]]:
        """Obtiene una categoría por su nombre"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM categorias WHERE nombre = ?", (nombre,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todas(self) -> List[Dict[str, Any]]:
        """Lista todas las categorías activas"""
        return super().listar_todos(self._tabla, activo=True)
    
    def actualizar(self, categoria_id: str, **campos) -> bool:
        """Actualiza una categoría"""
        return super().actualizar(self._tabla, categoria_id, **campos)
    
    def eliminar(self, categoria_id: str) -> bool:
        """Elimina lógicamente una categoría (activo=0)"""
        return super().eliminar(self._tabla, categoria_id)