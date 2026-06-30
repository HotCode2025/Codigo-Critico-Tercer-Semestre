"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.3: Controlador de Preventistas con UUID
==================================================
📌 USO: Gestiona preventistas con sincronización a Turso
📌 CARACTERÍSTICAS:
    - CRUD completo con UUID
    - Sincronización automática con Turso
    - Gestión de usuarios asociados
"""

import sqlite3
from typing import List, Optional, Dict, Any

from modelos.preventista import Preventista
from modelos.usuario import Usuario
from utilidades.turso_client import get_turso_client
from utilidades.sync_manager import SyncManager
from utilidades.sync_utils import SyncDirection


class ControladorPreventistas:
    """
    Controlador para gestionar preventistas.
    
    Ejemplo:
        ctrl = ControladorPreventistas(db)
        preventista_id = ctrl.crear_preventista(
            nombre="Juan",
            apellido="Perez",
            legajo="P001"
        )
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el controlador de preventistas"""
        self.db = db
        self.modelo = Preventista(db)
        self.usuario_modelo = Usuario(db)
        self.sync_manager = SyncManager()
        
        # Registrar tabla para sincronización
        if 'preventistas' not in self.sync_manager.tables:
            self.sync_manager.register_table(
                name='preventistas',
                direction=SyncDirection.FROM_LOCAL,
                id_field='id',
                timestamp_field='updated_at'
            )
    
    def crear_preventista(self, nombre: str, apellido: str,
                          legajo: str = None, telefono: str = None,
                          email: str = None, zona: str = None,
                          crear_usuario: bool = True,
                          username: str = None, password: str = None) -> Dict[str, Any]:
        """
        Crea un nuevo preventista y opcionalmente su usuario.
        
        Args:
            nombre: Nombre del preventista
            apellido: Apellido del preventista
            legajo: Legajo (opcional)
            telefono: Teléfono (opcional)
            email: Email (opcional)
            zona: Zona de trabajo (opcional)
            crear_usuario: Si se debe crear usuario asociado
            username: Nombre de usuario (si crear_usuario=True)
            password: Contraseña (si crear_usuario=True)
        
        Returns:
            Dict con preventista_id y opcionalmente usuario_id
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio.")
        if not apellido or not apellido.strip():
            raise ValueError("El apellido es obligatorio.")
        
        # Crear preventista
        preventista_id = self.modelo.crear(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            legajo=legajo.strip() if legajo else None,
            telefono=telefono.strip() if telefono else None,
            email=email.strip() if email else None,
            zona=zona.strip() if zona else None
        )
        
        # ✅ Sincronizar a Turso (IMPORTANTE)
        self._sincronizar_preventista(preventista_id)
        
        resultado = {'preventista_id': preventista_id}
        
        # Crear usuario asociado
        if crear_usuario:
            if not username:
                username = f"prev_{nombre.lower()}_{apellido.lower()}"
            if not password:
                password = legajo or "123456"
            
            usuario_id = self.usuario_modelo.crear(
                username=username,
                password=password,
                rol='preventista',
                preventista_id=preventista_id
            )
            resultado['usuario_id'] = usuario_id
            resultado['username'] = username
        
        return resultado
    
    def _sincronizar_preventista(self, preventista_id: str):
        """
        ✅ Sincroniza un preventista específico a Turso.
        """
        try:
            preventista = self.modelo.obtener_por_id(preventista_id)
            if not preventista:
                print(f"⚠️ Preventista {preventista_id} no encontrado")
                return
            
            client = get_turso_client()
            if client.is_connected():
                # ✅ Insertar en Turso
                result = client.insert('preventistas', preventista)
                if result:
                    print(f"✅ Preventista {preventista['nombre']} {preventista['apellido']} sincronizado a Turso")
                else:
                    print(f"⚠️ Error sincronizando preventista {preventista_id}")
            else:
                # Encolar para sincronización posterior
                from utilidades.sync_queue import get_sync_queue
                queue = get_sync_queue()
                
                columns = list(preventista.keys())
                placeholders = ", ".join(["?" for _ in columns])
                column_str = ", ".join(columns)
                query = f"INSERT OR REPLACE INTO preventistas ({column_str}) VALUES ({placeholders})"
                
                queue.agregar(query, list(preventista.values()))
                print(f"📦 Preventista {preventista_id[:8]} encolado para sincronización")
                
        except Exception as e:
            print(f"⚠️ Error sincronizando preventista: {e}")
    
    def modificar_preventista(self, preventista_id: str, **campos) -> bool:
        """
        Modifica un preventista existente.
        
        Args:
            preventista_id: UUID del preventista
            **campos: Campos a modificar
        
        Returns:
            bool: True si se modificó correctamente
        """
        if not preventista_id:
            raise ValueError("ID de preventista no proporcionado.")
        
        resultado = self.modelo.actualizar(preventista_id, **campos)
        
        if resultado:
            # ✅ Sincronizar a Turso después de modificar
            self._sincronizar_preventista(preventista_id)
        
        return resultado
    
    def eliminar_preventista(self, preventista_id: str) -> bool:
        """
        Elimina lógicamente un preventista (activo=0).
        
        Args:
            preventista_id: UUID del preventista
        
        Returns:
            bool: True si se eliminó correctamente
        """
        if not preventista_id:
            raise ValueError("ID de preventista no proporcionado.")
        
        resultado = self.modelo.eliminar(preventista_id)
        
        if resultado:
            try:
                client = get_turso_client()
                if client.is_connected():
                    client.update('preventistas', {'activo': 0}, 'id = ?', [preventista_id])
                    print(f"✅ Preventista {preventista_id[:8]} desactivado en Turso")
            except Exception as e:
                print(f"⚠️ Error sincronizando eliminación: {e}")
        
        return resultado
    
    def obtener_preventista(self, preventista_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un preventista por su UUID"""
        return self.modelo.obtener_por_id(preventista_id)
    
    def obtener_por_legajo(self, legajo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un preventista por su legajo"""
        return self.modelo.obtener_por_legajo(legajo)
    
    def listar_preventistas(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los preventistas"""
        return self.modelo.listar_todos(solo_activos=solo_activos)
    
    def listar_por_zona(self, zona: str) -> List[Dict[str, Any]]:
        """Lista preventistas por zona"""
        return self.modelo.listar_por_zona(zona)
    
    # ============================================================
    # MÉTODOS PARA USUARIOS ASOCIADOS
    # ============================================================
    
    def obtener_usuario_preventista(self, preventista_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el usuario asociado a un preventista"""
        return self.usuario_modelo.obtener_por_preventista(preventista_id)
    
    def sincronizar_todos(self) -> Dict[str, Any]:
        """
        ✅ Sincroniza TODOS los preventistas a Turso.
        """
        try:
            client = get_turso_client()
            if not client.is_connected():
                return {'error': 'No hay conexión a Turso'}
            
            preventistas = self.listar_preventistas(solo_activos=True)
            enviados = 0
            
            for p in preventistas:
                if client.insert('preventistas', p):
                    enviados += 1
            
            return {
                'total': len(preventistas),
                'enviados': enviados,
                'status': 'success'
            }
        except Exception as e:
            return {'error': str(e)}