"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.1: Modelo Base con UUID
==================================================
📌 USO: Clase base para todos los modelos del sistema
📌 CARACTERÍSTICAS:
    - Generación automática de UUID
    - Conexión compartida a la base de datos
    - Row factory para obtener diccionarios
    - ✅ Sanitización de nombres de tabla (seguridad)
"""

import uuid
import sqlite3
from typing import Optional, Dict, Any, List, Set, FrozenSet


class ModeloBase:
    """
    Clase base para todos los modelos del sistema.
    
    Proporciona:
        - Conexión a la base de datos
        - Generación de UUID
        - Métodos comunes (obtener_por_id, listar_todos, etc.)
    """
    
    # ✅ Tablas permitidas en el sistema (seguridad)
    _TABLAS_PERMITIDAS: FrozenSet[str] = frozenset([
        'clientes', 'productos', 'preventistas', 'categorias',
        'lotes', 'usuarios', 'facturas', 'factura_detalle',
        'notas_venta', 'nota_venta_detalle', 'cobros', 'cheques',
        'cuenta_corriente_movimientos', 'pedidos_procesados',
        'parametros', 'visitas_clientes', 'posiciones_preventistas',
        'gastos', 'otros_ingresos', 'proyecciones_config',
        'catalogo_importaciones'
    ])
    
    def __init__(self, db: sqlite3.Connection):
        """
        Inicializa el modelo con una conexión a la base de datos.
        
        Args:
            db: Conexión activa a SQLite
        """
        self.db = db
        self.db.row_factory = sqlite3.Row
    
    def _validar_tabla(self, tabla: str) -> str:
        """
        ✅ Valida que el nombre de tabla sea seguro (previene SQL Injection).
        
        Args:
            tabla: Nombre de la tabla a validar
        
        Returns:
            str: Nombre de tabla validado
        
        Raises:
            TypeError: Si el nombre no es string
            ValueError: Si la tabla no está permitida
        """
        if not isinstance(tabla, str):
            raise TypeError(f"El nombre de tabla debe ser string, recibido: {type(tabla)}")
        
        tabla_limpia = tabla.strip()
        if not tabla_limpia:
            raise ValueError("El nombre de tabla no puede estar vacío")
        
        if tabla_limpia not in self._TABLAS_PERMITIDAS:
            raise ValueError(f"Tabla no permitida: '{tabla_limpia}'. "
                           f"Tablas permitidas: {sorted(self._TABLAS_PERMITIDAS)}")
        
        return tabla_limpia
    
    def _validar_campos(self, **campos) -> Dict[str, Any]:
        """
        ✅ Valida que los nombres de campos sean seguros.
        
        Args:
            **campos: Diccionario de campos a validar
        
        Returns:
            Dict con campos validados
        """
        # Solo permitir caracteres alfanuméricos y guión bajo
        import re
        patron = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        
        for key in list(campos.keys()):
            if not patron.match(key):
                raise ValueError(f"Nombre de campo no permitido: '{key}'")
        
        return campos
    
    def generar_uuid(self) -> str:
        """
        Genera un UUID versión 4 (aleatorio).
        
        Returns:
            str: UUID como string (ej: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')
        """
        return str(uuid.uuid4())
    
    def obtener_por_id(self, tabla: str, id_registro: str) -> Optional[Dict[str, Any]]:
        """
        ✅ Obtiene un registro por su ID (con validación de tabla).
        
        Args:
            tabla: Nombre de la tabla
            id_registro: UUID del registro
        
        Returns:
            Dict con los datos del registro, o None si no existe
        """
        tabla = self._validar_tabla(tabla)
        cur = self.db.cursor()
        cur.execute(f"SELECT * FROM {tabla} WHERE id = ?", (id_registro,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todos(self, tabla: str, activo: bool = True, 
                     limit: Optional[int] = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        ✅ Lista registros de una tabla (con validación y paginación).
        
        Args:
            tabla: Nombre de la tabla
            activo: Si es True, solo devuelve registros con activo=1
            limit: Límite de registros (None para todos)
            offset: Desplazamiento para paginación
        
        Returns:
            Lista de diccionarios con los datos
        """
        tabla = self._validar_tabla(tabla)
        cur = self.db.cursor()
        
        if activo:
            query = f"SELECT * FROM {tabla} WHERE activo = 1"
        else:
            query = f"SELECT * FROM {tabla}"
        
        if limit is not None:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        cur.execute(query)
        return [dict(row) for row in cur.fetchall()]
    
    def contar_todos(self, tabla: str, activo: bool = True) -> int:
        """
        ✅ Cuenta registros en una tabla (con validación).
        
        Args:
            tabla: Nombre de la tabla
            activo: Si es True, solo cuenta registros activos
        
        Returns:
            int: Cantidad de registros
        """
        tabla = self._validar_tabla(tabla)
        cur = self.db.cursor()
        
        if activo:
            cur.execute(f"SELECT COUNT(*) FROM {tabla} WHERE activo = 1")
        else:
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        
        return cur.fetchone()[0]
    
    def actualizar(self, tabla: str, id_registro: str, **campos) -> bool:
        """
        ✅ Actualiza campos específicos de un registro (con validación).
        
        Args:
            tabla: Nombre de la tabla
            id_registro: UUID del registro
            **campos: Campos a actualizar (ej: nombre='Juan', activo=0)
        
        Returns:
            bool: True si se actualizó al menos un registro
        """
        if not campos:
            return False
        
        tabla = self._validar_tabla(tabla)
        campos = self._validar_campos(**campos)
        
        sets = ", ".join(f"{k} = ?" for k in campos.keys())
        valores = list(campos.values())
        valores.append(id_registro)
        
        cur = self.db.cursor()
        cur.execute(f"UPDATE {tabla} SET {sets} WHERE id = ?", valores)
        self.db.commit()
        return cur.rowcount > 0
    
    def eliminar(self, tabla: str, id_registro: str) -> bool:
        """
        ✅ Elimina lógicamente un registro (activo=0) (con validación).
        
        Args:
            tabla: Nombre de la tabla
            id_registro: UUID del registro
        
        Returns:
            bool: True si se desactivó correctamente
        """
        tabla = self._validar_tabla(tabla)
        return self.actualizar(tabla, id_registro, activo=0)
    
    def eliminar_fisico(self, tabla: str, id_registro: str) -> bool:
        """
        ✅ Elimina físicamente un registro (DELETE) (con validación).
        USAR CON CUIDADO - solo para administradores.
        
        Args:
            tabla: Nombre de la tabla
            id_registro: UUID del registro
        
        Returns:
            bool: True si se eliminó correctamente
        """
        tabla = self._validar_tabla(tabla)
        cur = self.db.cursor()
        cur.execute(f"DELETE FROM {tabla} WHERE id = ?", (id_registro,))
        self.db.commit()
        return cur.rowcount > 0
    
    def buscar(self, tabla: str, campo: str, valor: Any, 
               limit: Optional[int] = 50) -> List[Dict[str, Any]]:
        """
        ✅ Busca registros por un campo específico (con validación).
        
        Args:
            tabla: Nombre de la tabla
            campo: Nombre del campo
            valor: Valor a buscar
            limit: Límite de resultados
        
        Returns:
            Lista de diccionarios con los datos
        """
        tabla = self._validar_tabla(tabla)
        campo = self._validar_campos(**{campo: None})  # Validar nombre de campo
        
        cur = self.db.cursor()
        query = f"SELECT * FROM {tabla} WHERE {campo} LIKE ? AND activo = 1"
        if limit:
            query += f" LIMIT {limit}"
        
        cur.execute(query, (f"%{valor}%",))
        return [dict(row) for row in cur.fetchall()]
    
    def ejecutar_consulta_segura(self, query: str, params: List = None) -> List[Dict[str, Any]]:
        """
        ✅ Ejecuta una consulta SQL con validación básica.
        Solo permite SELECT, INSERT, UPDATE, DELETE con parámetros.
        
        Args:
            query: Consulta SQL (con ? como placeholders)
            params: Lista de parámetros
        
        Returns:
            Lista de diccionarios con los resultados (para SELECT)
        """
        # Validar que solo sea una consulta permitida
        query_upper = query.strip().upper()
        permitidas = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        
        if not any(query_upper.startswith(p) for p in permitidas):
            raise ValueError(f"Tipo de consulta no permitida: {query_upper.split()[0] if query_upper else 'vacía'}")
        
        # Validar que no haya comandos peligrosos
        peligrosos = ['DROP', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for p in peligrosos:
            if p in query_upper:
                raise ValueError(f"Comando no permitido en consulta: {p}")
        
        cur = self.db.cursor()
        cur.execute(query, params or [])
        self.db.commit()
        
        # Si es SELECT, devolver resultados
        if query_upper.startswith('SELECT'):
            return [dict(row) for row in cur.fetchall()]
        
        return []