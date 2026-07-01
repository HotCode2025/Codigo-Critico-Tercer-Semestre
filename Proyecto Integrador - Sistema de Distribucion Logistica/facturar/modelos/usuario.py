"""
Código Crítico - Tercer Semestre Año 2026
==================================================
Modelo de Usuario con UUID
==================================================
📌 USO: Representa y gestiona la tabla 'usuarios'
📌 CARACTERÍSTICAS:
    - Clave primaria: UUID (TEXT)
    - Autenticación con hash SHA256
    - Sincronización: Central → Turso → App
"""

import hashlib
import sqlite3
from typing import List, Optional, Dict, Any
from modelos.base import ModeloBase


class Usuario(ModeloBase):
    """
    Modelo para gestionar usuarios del sistema.
    
    Ejemplo:
        usuario = Usuario(db)
        usuario_id = usuario.crear(
            username="juan",
            password="123456",
            rol="preventista",
            preventista_id=preventista_id
        )
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el modelo de usuario"""
        super().__init__(db)
        self._tabla = "usuarios"
    
    def _hash_password(self, password: str) -> str:
        """
        Genera hash SHA256 de la contraseña.
        
        Args:
            password: Contraseña en texto plano
        
        Returns:
            str: Hash SHA256 hex
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def crear(self, username: str, password: str, rol: str = 'preventista',
              preventista_id: str = None, cliente_id: str = None) -> str:
        """
        Crea un nuevo usuario con UUID.
        
        Args:
            username: Nombre de usuario (único)
            password: Contraseña en texto plano
            rol: admin, preventista, cliente
            preventista_id: UUID del preventista (si aplica)
            cliente_id: UUID del cliente (si aplica)
        
        Returns:
            str: UUID del usuario creado
        """
        usuario_id = self.generar_uuid()
        password_hash = self._hash_password(password)
        
        query = """
            INSERT INTO usuarios (
                id, username, password_hash, rol, 
                preventista_id, cliente_id, activo
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        
        cur = self.db.cursor()
        cur.execute(query, (
            usuario_id,
            username,
            password_hash,
            rol,
            preventista_id,
            cliente_id
        ))
        self.db.commit()
        return usuario_id
    
    def autenticar(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
        
        Returns:
            Dict con datos del usuario, o None si falla
        """
        password_hash = self._hash_password(password)
        
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, username, rol, preventista_id, cliente_id, activo
            FROM usuarios
            WHERE username = ? AND password_hash = ? AND activo = 1
        """, (username, password_hash))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_id(self, usuario_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su UUID"""
        return super().obtener_por_id(self._tabla, usuario_id)
    
    def obtener_por_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su nombre de usuario"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_preventista(self, preventista_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por el UUID del preventista asociado"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE preventista_id = ?", (preventista_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_cliente(self, cliente_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por el UUID del cliente asociado"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE cliente_id = ?", (cliente_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los usuarios"""
        return super().listar_todos(self._tabla, solo_activos)
    
    def cambiar_contrasena(self, usuario_id: str, password_actual: str, 
                           password_nueva: str) -> bool:
        """
        Cambia la contraseña verificando la actual.
        
        Args:
            usuario_id: UUID del usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña
        
        Returns:
            bool: True si se cambió correctamente
        """
        usuario = self.obtener_por_id(usuario_id)
        if not usuario:
            return False
        
        hash_actual = self._hash_password(password_actual)
        if usuario['password_hash'] != hash_actual:
            return False
        
        nuevo_hash = self._hash_password(password_nueva)
        return self.actualizar(usuario_id, password_hash=nuevo_hash)
    
    def resetear_contrasena(self, usuario_id: str, nueva_password: str) -> bool:
        """Resetea la contraseña sin verificar la actual (solo admin)"""
        nuevo_hash = self._hash_password(nueva_password)
        return self.actualizar(usuario_id, password_hash=nuevo_hash)
    
    def actualizar(self, usuario_id: str, **campos) -> bool:
        """Actualiza un usuario"""
        return super().actualizar(self._tabla, usuario_id, **campos)
    
    def eliminar(self, usuario_id: str) -> bool:
        """Elimina lógicamente un usuario (activo=0)"""
        return super().eliminar(self._tabla, usuario_id)
    
    def activar(self, usuario_id: str) -> bool:
        """Activa un usuario"""
        return self.actualizar(usuario_id, activo=1)
    
    def desactivar(self, usuario_id: str) -> bool:
        """Desactiva un usuario"""
        return self.actualizar(usuario_id, activo=0)
    
    def eliminar_fisico(self, usuario_id: str) -> bool:
        """Elimina físicamente un usuario (DELETE) - SOLO ADMIN"""
        return super().eliminar_fisico(self._tabla, usuario_id)


# ============================================================
# FUNCIONES DE UTILIDAD
# ============================================================

def crear_usuario_admin(db: sqlite3.Connection):
    """
    Crea el usuario admin por defecto si no existe.
    
    Args:
        db: Conexión a la base de datos
    """
    usuario_modelo = Usuario(db)
    
    # Verificar si ya existe el usuario admin
    admin = usuario_modelo.obtener_por_username('admin')
    if not admin:
        # Crear usuario admin con UUID fijo
        admin_id = '00000000-0000-0000-0000-000000000001'
        
        # Verificar si ya existe un usuario con ese ID
        cur = db.cursor()
        cur.execute("SELECT id FROM usuarios WHERE id = ?", (admin_id,))
        if not cur.fetchone():
            # Crear usuario admin
            cur.execute("""
                INSERT INTO usuarios (id, username, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (
                admin_id,
                'admin',
                '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',  # hash de 'admin'
                'admin'
            ))
            db.commit()
            print("✅ Usuario admin creado (usuario: admin, contraseña: admin)")
        else:
            print("ℹ️ Usuario admin ya existe")
    else:
        print("ℹ️ Usuario admin ya existe")


def crear_preventista_con_usuario(db: sqlite3.Connection, 
                                   nombre: str, 
                                   apellido: str,
                                   legajo: str = None,
                                   username: str = None,
                                   password: str = None,
                                   telefono: str = None,
                                   email: str = None,
                                   zona: str = None) -> Dict[str, Any]:
    """
    Crea un preventista y su usuario asociado automáticamente.
    
    Args:
        db: Conexión a la base de datos
        nombre: Nombre del preventista
        apellido: Apellido del preventista
        legajo: Legajo (opcional)
        username: Nombre de usuario (si no se proporciona, se genera)
        password: Contraseña (si no se proporciona, usa el legajo)
        telefono: Teléfono (opcional)
        email: Email (opcional)
        zona: Zona (opcional)
    
    Returns:
        Dict con preventista_id, usuario_id y username
    """
    from modelos.preventista import Preventista
    
    preventista_modelo = Preventista(db)
    usuario_modelo = Usuario(db)
    
    # Generar username si no se proporciona
    if not username:
        username = f"prev_{nombre.lower()}_{apellido.lower()}"
    
    # Generar password si no se proporciona
    if not password:
        password = legajo or "123456"
    
    # Crear preventista
    preventista_id = preventista_modelo.crear(
        nombre=nombre,
        apellido=apellido,
        legajo=legajo,
        telefono=telefono,
        email=email,
        zona=zona
    )
    
    # Crear usuario asociado
    usuario_id = usuario_modelo.crear(
        username=username,
        password=password,
        rol='preventista',
        preventista_id=preventista_id
    )
    
    return {
        'preventista_id': preventista_id,
        'usuario_id': usuario_id,
        'username': username
    }


if __name__ == "__main__":
    # Prueba rápida del modelo
    from db.db_manager import obtener_conexion
    
    db = obtener_conexion()
    
    # Crear usuario admin
    crear_usuario_admin(db)
    
    # Probar autenticación
    usuario_modelo = Usuario(db)
    admin = usuario_modelo.autenticar('admin', 'admin')
    if admin:
        print(f"✅ Autenticación exitosa: {admin['username']} ({admin['rol']})")
    else:
        print("❌ Autenticación fallida")
    
    # Listar usuarios
    usuarios = usuario_modelo.listar_todos()
    print(f"📋 Usuarios en el sistema: {len(usuarios)}")
    for u in usuarios:
        print(f"  - {u['username']} ({u['rol']}) - {'Activo' if u['activo'] else 'Inactivo'}")
    
    db.close()