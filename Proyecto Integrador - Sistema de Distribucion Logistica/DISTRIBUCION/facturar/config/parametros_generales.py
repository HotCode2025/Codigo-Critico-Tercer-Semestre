"""
Código Crítico - Tercer Semestre Año 2026
Gestor de parámetros generales del sistema.
Lee y escribe la configuración única almacenada en la tabla 'parametros'.
"""

import sqlite3
from typing import Optional, Dict, Any

class ParametrosGenerales:
    """
    Clase que encapsula el acceso a los parámetros de la empresa.
    Siempre existe una única fila con id=1.
    """

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.asegurar_fila()   # Garantiza que exista el registro id=1

    def asegurar_fila(self):
        """Crea la fila por defecto si no existe."""
        cur = self.db.cursor()
        cur.execute("SELECT id FROM parametros WHERE id=1")
        if cur.fetchone() is None:
            cur.execute("""
                INSERT INTO parametros (id, moneda, nombre_distribuidora,
                    direccion, telefono1, telefono2, whatsapp, email,
                    encabezado_factura, encabezado_reporte, tasa_municipal_porcentaje)
                VALUES (1, 'ARS', 'Distribuidora Ejemplo', '', '', '', '', '',
                        '', '', 0.0)
            """)
            self.db.commit()

    def cargar(self) -> Dict[str, Any]:
        """Devuelve un diccionario con todos los parámetros."""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM parametros WHERE id=1")
        row = cur.fetchone()
        if row:
            return dict(row)
        return {}

    def guardar(self, datos: Dict[str, Any]):
        """
        Actualiza los parámetros. Solo modifica los campos presentes en el diccionario.
        """
        permitidos = [
            'moneda', 'nombre_distribuidora', 'direccion',
            'telefono1', 'telefono2', 'whatsapp', 'email',
            'encabezado_factura', 'encabezado_reporte',
            'tasa_municipal_porcentaje'
        ]
        sets = []
        valores = []
        for campo in permitidos:
            if campo in datos:
                sets.append(f"{campo} = ?")
                valores.append(datos[campo])
        if sets:
            valores.append(1)  # id
            query = f"UPDATE parametros SET {', '.join(sets)} WHERE id = ?"
            cur = self.db.cursor()
            cur.execute(query, valores)
            self.db.commit()

    def guardar_logo(self, datos_binarios: bytes):
        """Almacena el logo en la base de datos."""
        cur = self.db.cursor()
        cur.execute("UPDATE parametros SET logo = ? WHERE id = 1", (datos_binarios,))
        self.db.commit()

    def obtener_logo(self) -> Optional[bytes]:
        """Obtiene los datos binarios del logo (puede ser None)."""
        cur = self.db.cursor()
        cur.execute("SELECT logo FROM parametros WHERE id=1")
        row = cur.fetchone()
        if row:
            return row['logo']
        return None