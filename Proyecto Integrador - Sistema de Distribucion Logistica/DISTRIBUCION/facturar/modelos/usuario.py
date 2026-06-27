"""
Código Crítico - Tercer Semestre Año 2026
Modelo de Usuario - Autenticación y gestión de usuarios.
Soporta roles: admin, preventista, cliente
"""

import sqlite3
import hashlib
import uuid
from typing import List, Optional, Dict, Any


class Usuario:
    """Modelo para gestión de usuarios del sistema."""
    
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row
    
    def _hash_password(self, password: str) -> str:
        """Genera hash SHA256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def crear(self, username: str, password: str, rol: str = 'preventista',
              preventista_id: int = None, cliente_id: int = None) -> int:
        """
        Crea un nuevo usuario.
        
        Args:
            username: Nombre de usuario único
            password: Contraseña en texto plano (se hashea)
            rol: admin, preventista, cliente
            preventista_id: ID del preventista asociado (si rol=preventista)
            cliente_id: ID del cliente asociado (si rol=cliente)
        """
        if not username or not password:
            raise ValueError("Usuario y contraseña son obligatorios.")
        
        if rol not in ('admin', 'preventista', 'cliente'):
            raise ValueError("Rol inválido. Debe ser admin, preventista o cliente.")
        
        # Verificar username único
        cur = self.db.cursor()
        cur.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
        if cur.fetchone():
            raise ValueError(f"El usuario '{username}' ya existe.")
        
        password_hash = self._hash_password(password)
        
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, rol, preventista_id, cliente_id, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (username, password_hash, rol, preventista_id, cliente_id))
        
        self.db.commit()
        return cur.lastrowid
    
    def autenticar(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un usuario y devuelve sus datos si es correcto."""
        password_hash = self._hash_password(password)
        
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, username, rol, preventista_id, cliente_id, activo
            FROM usuarios
            WHERE username = ? AND password_hash = ? AND activo = 1
        """, (username, password_hash))
        
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        cur = self.db.cursor()
        cur.execute("SELECT id, username, rol, preventista_id, cliente_id, activo, password_hash FROM usuarios WHERE id = ?", (usuario_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su nombre de usuario."""
        cur = self.db.cursor()
        cur.execute("SELECT id, username, rol, preventista_id, cliente_id, activo FROM usuarios WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_preventista_id(self, preventista_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por el ID del preventista asociado."""
        cur = self.db.cursor()
        cur.execute("SELECT id, username, rol, preventista_id, cliente_id, activo FROM usuarios WHERE preventista_id = ?", (preventista_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def obtener_por_cliente_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por el ID del cliente asociado."""
        cur = self.db.cursor()
        cur.execute("SELECT id, username, rol, preventista_id, cliente_id, activo FROM usuarios WHERE cliente_id = ?", (cliente_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def listar_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Lista todos los usuarios."""
        cur = self.db.cursor()
        if solo_activos:
            cur.execute("SELECT id, username, rol, preventista_id, cliente_id, activo FROM usuarios WHERE activo = 1")
        else:
            cur.execute("SELECT id, username, rol, preventista_id, cliente_id, activo FROM usuarios")
        return [dict(row) for row in cur.fetchall()]
    
    def cambiar_contrasena(self, usuario_id: int, password_actual: str, password_nueva: str) -> bool:
        """Cambia la contraseña de un usuario verificando la actual."""
        usuario = self.obtener_por_id(usuario_id)
        if not usuario:
            return False
        
        password_hash_actual = self._hash_password(password_actual)
        if usuario['password_hash'] != password_hash_actual:
            return False
        
        nuevo_hash = self._hash_password(password_nueva)
        cur = self.db.cursor()
        cur.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (nuevo_hash, usuario_id))
        self.db.commit()
        return True
    
    def resetear_contrasena(self, usuario_id: int, nueva_password: str) -> bool:
        """Resetea la contraseña de un usuario (sin verificar la actual). Solo admin."""
        nuevo_hash = self._hash_password(nueva_password)
        cur = self.db.cursor()
        cur.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (nuevo_hash, usuario_id))
        self.db.commit()
        return True
    
    def cambiar_rol(self, usuario_id: int, nuevo_rol: str) -> bool:
        """Cambia el rol de un usuario."""
        if nuevo_rol not in ('admin', 'preventista', 'cliente'):
            return False
        
        cur = self.db.cursor()
        cur.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (nuevo_rol, usuario_id))
        self.db.commit()
        return True
    
    def desactivar(self, usuario_id: int) -> bool:
        """Desactiva un usuario (baja lógica)."""
        cur = self.db.cursor()
        cur.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))
        self.db.commit()
        return True
    
    def activar(self, usuario_id: int) -> bool:
        """Activa un usuario."""
        cur = self.db.cursor()
        cur.execute("UPDATE usuarios SET activo = 1 WHERE id = ?", (usuario_id,))
        self.db.commit()
        return True
    
    def eliminar(self, usuario_id: int) -> bool:
        """Elimina físicamente un usuario (solo para admin)."""
        cur = self.db.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        self.db.commit()
        return True


def crear_usuario_admin(db):
    """Crea el usuario admin por defecto si no existe."""
    usuario_modelo = Usuario(db)
    
    admin = usuario_modelo.obtener_por_username('admin')
    if not admin:
        usuario_modelo.crear('admin', 'admin', 'admin')
        print("✅ Usuario admin creado (admin/admin)")


def crear_preventista_con_usuario(db, nombre, apellido, legajo, username, password, telefono=None, email=None, zona=None):
    """
    Crea un preventista y su usuario asociado automáticamente.
    """
    from modelos.preventista import Preventista
    
    preventista_modelo = Preventista(db)
    usuario_modelo = Usuario(db)
    
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