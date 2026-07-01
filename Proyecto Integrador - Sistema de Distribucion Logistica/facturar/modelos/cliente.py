"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 6.2: Modelo de Cliente con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'clientes'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Sincronización: Central → Turso → App
    - La App SOLO LEE clientes (no los crea)
"""

from datetime import date
from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Cliente(ModeloBase):
    """
    Modelo para gestionar clientes.
    
    Ejemplo:
        cliente = Cliente(db)
        cliente_id = cliente.crear(
            razon_social="Cliente Ejemplo",
            cuit="20-12345678-9",
            condicion_iva="RI"
        )
    """
    
    def __init__(self, db):
        """Inicializa el modelo de cliente"""
        super().__init__(db)
        self._tabla = "clientes"
    
    def crear(self, razon_social: str, cuit: str, condicion_iva: str = 'RI',
              domicilio: str = None, telefono: str = None, email: str = None,
              aplica_tasa_municipal: bool = False, limite_credito: float = 0.0,
              calle: str = None, numero: str = None, localidad: str = None,
              provincia: str = None, latitud: float = None, longitud: float = None,
              preventista_id: str = None, whatsapp: str = None) -> str:
        """
        Crea un nuevo cliente con UUID.
        
        Returns:
            str: UUID del cliente creado
        """
        cliente_id = self.generar_uuid()
        
        # Construir domicilio a partir de calle, numero, localidad, provincia
        if calle and numero and localidad:
            domicilio = f"{calle} {numero}, {localidad}, {provincia or ''}"
        elif calle and numero:
            domicilio = f"{calle} {numero}"
        elif domicilio is None:
            domicilio = ""
        
        query = """
            INSERT INTO clientes (
                id, razon_social, cuit, condicion_iva, domicilio,
                telefono, email, aplica_tasa_municipal, limite_credito, 
                fecha_alta, calle, numero, localidad, provincia, 
                latitud, longitud, preventista_id, whatsapp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            cliente_id,
            razon_social,
            cuit,
            condicion_iva,
            domicilio,
            telefono,
            email,
            1 if aplica_tasa_municipal else 0,
            limite_credito,
            date.today().isoformat(),
            calle,
            numero,
            localidad,
            provincia,
            latitud,
            longitud,
            preventista_id,
            whatsapp
        ))
        self.db.commit()
        return cliente_id
    
    def obtener_por_id(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por su UUID"""
        return super().obtener_por_id(self._tabla, cliente_id)
    
    def obtener_por_cuit(self, cuit: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por su CUIT"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM clientes WHERE cuit = ?", (cuit,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los clientes"""
        return super().listar_todos(self._tabla, solo_activos)
    
    def listar_por_preventista(self, preventista_id: str) -> List[Dict[str, Any]]:
        """Lista clientes asignados a un preventista"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM clientes 
            WHERE preventista_id = ? AND activo = 1
            ORDER BY razon_social
        """, (preventista_id,))
        return [dict(row) for row in cur.fetchall()]
    
    def actualizar(self, cliente_id: str, **campos) -> bool:
        """Actualiza un cliente"""
        return super().actualizar(self._tabla, cliente_id, **campos)
    
    def eliminar(self, cliente_id: str) -> bool:
        """Elimina lógicamente un cliente (activo=0)"""
        return super().eliminar(self._tabla, cliente_id)
    
    def obtener_saldo(self, cliente_id: str) -> float:
        """Obtiene el saldo de cuenta corriente de un cliente"""
        cur = self.db.cursor()
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        return row['saldo_cuenta_corriente'] if row else 0.0
    
    def actualizar_saldo(self, cliente_id: str, nuevo_saldo: float) -> bool:
        """Actualiza el saldo de cuenta corriente"""
        return self.actualizar(cliente_id, saldo_cuenta_corriente=nuevo_saldo)