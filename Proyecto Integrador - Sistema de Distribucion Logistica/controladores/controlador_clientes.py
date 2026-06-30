"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.1: Controlador de Clientes con UUID
==================================================
📌 USO: Gestiona clientes con sincronización a Turso
📌 CARACTERÍSTICAS:
    - CRUD completo con UUID
    - Sincronización automática con Turso
    - Geolocalización
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

from modelos.cliente import Cliente
from utilidades.turso_client import get_turso_client
from utilidades.sync_manager import SyncDirection, SyncManager


class ControladorClientes:
    """
    Controlador para gestionar clientes.
    
    Ejemplo:
        ctrl = ControladorClientes(db)
        cliente_id = ctrl.crear_cliente(
            razon_social="Cliente Ejemplo",
            cuit="20-12345678-9"
        )
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el controlador de clientes"""
        self.db = db
        self.modelo = Cliente(db)
        self.sync_manager = SyncManager()
        
        # Registrar tabla para sincronización
        if 'clientes' not in self.sync_manager.tables:
            self.sync_manager.register_table(
                name='clientes',
                direction=SyncDirection.FROM_LOCAL,
                id_field='id',
                timestamp_field='updated_at'
            )
    
    def crear_cliente(self, razon_social: str, cuit: str = None,
                      condicion_iva: str = 'RI', domicilio: str = None,
                      telefono: str = None, email: str = None,
                      aplica_tasa: bool = False, limite_credito: float = 0.0,
                      preventista_id: str = None, calle: str = None,
                      numero: str = None, localidad: str = None,
                      provincia: str = None, latitud: float = None,
                      longitud: float = None, whatsapp: str = None) -> str:
        """
        Crea un nuevo cliente.
        
        Returns:
            str: UUID del cliente creado
        """
        # Validaciones
        if not razon_social or not razon_social.strip():
            raise ValueError("La razón social es obligatoria.")
        
        if cuit:
            cuit = cuit.strip()
            if self.modelo.obtener_por_cuit(cuit):
                raise ValueError("Ya existe un cliente con ese CUIT.")
        
        if condicion_iva not in ('RI', 'M', 'EX', 'CF', 'MT'):
            condicion_iva = 'RI'
        
        # Crear cliente
        cliente_id = self.modelo.crear(
            razon_social=razon_social.strip(),
            cuit=cuit,
            condicion_iva=condicion_iva,
            domicilio=domicilio.strip() if domicilio else None,
            telefono=telefono.strip() if telefono else None,
            email=email.strip() if email else None,
            aplica_tasa_municipal=aplica_tasa,
            limite_credito=limite_credito,
            calle=calle.strip() if calle else None,
            numero=numero.strip() if numero else None,
            localidad=localidad.strip() if localidad else None,
            provincia=provincia.strip() if provincia else None,
            latitud=latitud,
            longitud=longitud,
            preventista_id=preventista_id,
            whatsapp=whatsapp.strip() if whatsapp else None
        )
        
        # Sincronizar a Turso
        self._sincronizar_cliente(cliente_id)
        
        return cliente_id
    
    def _sincronizar_cliente(self, cliente_id: str):
        """
        Sincroniza un cliente específico a Turso.
        """
        try:
            cliente = self.modelo.obtener_por_id(cliente_id)
            if not cliente:
                return
            
            client = get_turso_client()
            if client.is_connected():
                client.insert('clientes', cliente)
                print(f"✅ Cliente {cliente['razon_social']} sincronizado a Turso")
            else:
                # Encolar para sincronización posterior
                self.sync_manager.sync_from_local('clientes', self.db)
                
        except Exception as e:
            print(f"⚠️ Error sincronizando cliente: {e}")
    
    def modificar_cliente(self, cliente_id: str, **campos) -> bool:
        """
        Modifica un cliente existente.
        
        Args:
            cliente_id: UUID del cliente
            **campos: Campos a modificar
        
        Returns:
            bool: True si se modificó correctamente
        """
        if not cliente_id:
            raise ValueError("ID de cliente no proporcionado.")
        
        # Validar CUIT si se está modificando
        if 'cuit' in campos and campos['cuit']:
            nuevo_cuit = campos['cuit'].strip()
            existente = self.modelo.obtener_por_cuit(nuevo_cuit)
            if existente and existente['id'] != cliente_id:
                raise ValueError("El CUIT ya pertenece a otro cliente.")
        
        resultado = self.modelo.actualizar(cliente_id, **campos)
        
        if resultado:
            # Sincronizar a Turso
            self._sincronizar_cliente(cliente_id)
        
        return resultado
    
    def eliminar_cliente(self, cliente_id: str) -> bool:
        """
        Elimina lógicamente un cliente (activo=0).
        
        Args:
            cliente_id: UUID del cliente
        
        Returns:
            bool: True si se eliminó correctamente
        """
        resultado = self.modelo.eliminar(cliente_id)
        
        if resultado:
            # Sincronizar a Turso
            try:
                client = get_turso_client()
                if client.is_connected():
                    client.update('clientes', {'activo': 0}, 'id = ?', [cliente_id])
            except Exception as e:
                print(f"⚠️ Error sincronizando eliminación: {e}")
        
        return resultado
    
    def obtener_cliente(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un cliente por su UUID"""
        return self.modelo.obtener_por_id(cliente_id)
    
    def buscar_por_cuit(self, cuit: str) -> Optional[Dict[str, Any]]:
        """Busca un cliente por CUIT"""
        return self.modelo.obtener_por_cuit(cuit)
    
    def listar_clientes(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los clientes"""
        return self.modelo.listar_todos(solo_activos=solo_activos)
    
    def listar_por_preventista(self, preventista_id: str) -> List[Dict[str, Any]]:
        """Lista clientes de un preventista"""
        return self.modelo.listar_por_preventista(preventista_id)
    
    def sincronizar_todos(self) -> Dict[str, Any]:
        """
        Sincroniza todos los clientes a Turso.
        
        Returns:
            Dict con resultados de la sincronización
        """
        return self.sync_manager.sync_from_local('clientes', self.db)