"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.4: Modelo de Preventista con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'preventistas'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Sincronización: Central → Turso → App
"""

from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Preventista(ModeloBase):
    """
    Modelo para gestionar preventistas.
    
    Ejemplo:
        preventista = Preventista(db)
        preventista_id = preventista.crear(
            nombre="Juan",
            apellido="Perez",
            legajo="P001"
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de preventista"""
        super().__init__(db)
        self._tabla = "preventistas"
    
    def crear(self, nombre: str, apellido: str, legajo: str = None,
              telefono: str = None, email: str = None, zona: str = None) -> str:
        """
        Crea un nuevo preventista con UUID.
        
        Returns:
            str: UUID del preventista creado
        """
        preventista_id = self.generar_uuid()
        
        query = """
            INSERT INTO preventistas (
                id, nombre, apellido, legajo, telefono, email, zona
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            preventista_id,
            nombre,
            apellido,
            legajo,
            telefono,
            email,
            zona
        ))
        self.db.commit()
        return preventista_id
    
    def obtener_por_id(self, preventista_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un preventista por su UUID"""
        return super().obtener_por_id(self._tabla, preventista_id)
    
    def obtener_por_legajo(self, legajo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un preventista por su legajo"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM preventistas WHERE legajo = ?", (legajo,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los preventistas"""
        return super().listar_todos(self._tabla, solo_activos)
    
    def listar_por_zona(self, zona: str) -> List[Dict[str, Any]]:
        """Lista preventistas por zona"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM preventistas 
            WHERE zona = ? AND activo = 1
            ORDER BY apellido, nombre
        """, (zona,))
        return [dict(row) for row in cur.fetchall()]
    
    # ✅ CORREGIDO: acepta kwargs para ser compatible con el método base
    def actualizar(self, preventista_id: str, **campos) -> bool:
        """
        Actualiza un preventista.
        ✅ Ahora acepta **kwargs para ser compatible con ModeloBase.actualizar()
        """
        if not preventista_id:
            raise ValueError("El ID del preventista es obligatorio.")
        
        # Si no hay campos, retornar False
        if not campos:
            return False
        
        # Construir la consulta dinámicamente
        sets = ", ".join([f"{k} = ?" for k in campos.keys()])
        valores = list(campos.values())
        valores.append(preventista_id)
        
        cur = self.db.cursor()
        query = f"UPDATE {self._tabla} SET {sets} WHERE id = ?"
        cur.execute(query, valores)
        self.db.commit()
        return cur.rowcount > 0
    
    def eliminar(self, preventista_id: str) -> bool:
        """
        ✅ CORREGIDO: Elimina lógicamente un preventista (activo=0)
        """
        if not preventista_id:
            raise ValueError("El ID del preventista es obligatorio.")
        
        # ✅ Llamar directamente al método de la clase base con los parámetros correctos
        return super().actualizar(self._tabla, preventista_id, activo=0)