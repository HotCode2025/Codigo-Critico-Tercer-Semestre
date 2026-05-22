"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Clientes.
Contiene la lógica de negocio para gestionar clientes:
validaciones, verificación de CUIT, límite de crédito, etc.
"""
import sqlite3
from typing import List, Optional, Dict, Any
from modelos.cliente import Cliente


class ControladorClientes:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.modelo = Cliente(db)

    def crear_cliente(self, razon_social: str, cuit: str = None,
                      condicion_iva: str = 'RI', domicilio: str = None,
                      telefono: str = None, email: str = None,
                      aplica_tasa: bool = False, limite_credito: float = 0.0) -> int:
        """Crea un nuevo cliente tras validar datos obligatorios y unicidad de CUIT."""
        # Validaciones básicas
        if not razon_social or not razon_social.strip():
            raise ValueError("La razón social es obligatoria.")
        if cuit:
            cuit = cuit.strip()
            if self.modelo.buscar_por_cuit(cuit):
                raise ValueError("Ya existe un cliente con ese CUIT.")
        # Asegurar valores por defecto
        if condicion_iva not in ('RI', 'M', 'EX', 'CF', 'MT'):
            condicion_iva = 'RI'
        return self.modelo.crear(razon_social=razon_social.strip(),
                                 cuit=cuit,
                                 condicion_iva=condicion_iva,
                                 domicilio=domicilio.strip() if domicilio else None,
                                 telefono=telefono.strip() if telefono else None,
                                 email=email.strip() if email else None,
                                 aplica_tasa_municipal=aplica_tasa,
                                 limite_credito=limite_credito)

    def modificar_cliente(self, cliente_id: int, **campos) -> bool:
        """Actualiza los campos permitidos de un cliente."""
        if not cliente_id:
            raise ValueError("ID de cliente no proporcionado.")
        # Si se cambia el CUIT, verificar que no esté duplicado
        if 'cuit' in campos and campos['cuit']:
            nuevo_cuit = campos['cuit'].strip()
            existente = self.modelo.buscar_por_cuit(nuevo_cuit)
            if existente and existente['id'] != cliente_id:
                raise ValueError("El CUIT ya pertenece a otro cliente.")
        return self.modelo.actualizar(cliente_id, **campos)

    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Da de baja lógica al cliente."""
        return self.modelo.eliminar(cliente_id)

    def obtener_cliente(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_id(cliente_id)

    def listar_clientes(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        return self.modelo.listar_todos(solo_activos=solo_activos)

    def buscar_por_cuit(self, cuit: str) -> Optional[Dict[str, Any]]:
        return self.modelo.buscar_por_cuit(cuit)