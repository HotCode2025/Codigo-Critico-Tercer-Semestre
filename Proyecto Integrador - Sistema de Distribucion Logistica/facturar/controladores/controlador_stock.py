"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.4: Controlador de Stock con UUID
==================================================
📌 USO: Gestiona stock y lotes con sincronización a Turso
📌 CARACTERÍSTICAS:
    - Gestión de lotes con UUID
    - FIFO (First In, First Out)
    - Sincronización automática
    - ✅ Singleton SyncManager (corregido)
"""

import sqlite3
from datetime import date, timedelta
from typing import List, Optional, Dict, Any

from modelos.lote import Lote
from modelos.producto import Producto
from utilidades.turso_client import get_turso_client
from utilidades.sync_utils import SyncDirection, SyncStatus
from utilidades.sync_manager import SyncManager


class ControladorStock:
    """
    Controlador para gestionar stock y lotes.
    
    Ejemplo:
        ctrl = ControladorStock(db)
        lote_id = ctrl.crear_lote(
            producto_id=producto_id,
            fecha_vencimiento="2026-12-31",
            cantidad_inicial=100.0
        )
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el controlador de stock"""
        self.db = db
        self.lote_modelo = Lote(db)
        self.producto_modelo = Producto(db)
        
        # ✅ Usar singleton de SyncManager (no crear uno nuevo)
        self.sync_manager = SyncManager()
        
        # ✅ Registrar tabla para sincronización (solo si no está registrada)
        if 'lotes' not in self.sync_manager.tables:
            self.sync_manager.register_table(
                name='lotes',
                direction=SyncDirection.FROM_LOCAL,
                id_field='id',
                timestamp_field='updated_at'
            )
            print("📋 Tabla 'lotes' registrada para sincronización")
    
    def _sincronizar_lote(self, lote_id: str):
        """
        Sincroniza un lote específico a Turso.
        """
        try:
            lote = self.lote_modelo.obtener_por_id(lote_id)
            if not lote:
                return
            
            # ✅ Usar sync_manager en lugar de crear cliente directamente
            if self.sync_manager.client.is_connected():
                self.sync_manager.client.insert('lotes', lote)
                print(f"✅ Lote {lote['numero_lote'] or lote_id[:8]} sincronizado a Turso")
            else:
                # Encolar para sincronización posterior
                self.sync_manager.sync_queue.agregar(
                    f"INSERT OR REPLACE INTO lotes (id, producto_id, codigo_producto, numero_lote, fecha_vencimiento, cantidad_inicial, cantidad_actual, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [lote['id'], lote['producto_id'], lote.get('codigo_producto'), lote.get('numero_lote'), 
                     lote['fecha_vencimiento'], lote['cantidad_inicial'], lote['cantidad_actual'], lote.get('fecha_ingreso')]
                )
                print(f"📦 Lote {lote_id[:8]} encolado para sincronización")
                
        except Exception as e:
            print(f"⚠️ Error sincronizando lote: {e}")
    
    def crear_lote(self, producto_id: str, fecha_vencimiento: str,
                   cantidad_inicial: float, numero_lote: str = None) -> str:
        """
        Crea un nuevo lote.
        
        Args:
            producto_id: UUID del producto
            fecha_vencimiento: Fecha de vencimiento (YYYY-MM-DD)
            cantidad_inicial: Cantidad inicial
            numero_lote: Número de lote (opcional)
        
        Returns:
            str: UUID del lote creado
        """
        # Validaciones
        if not producto_id:
            raise ValueError("Producto no válido.")
        
        producto = self.producto_modelo.obtener_por_id(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado.")
        
        if cantidad_inicial <= 0:
            raise ValueError("La cantidad inicial debe ser mayor que cero.")
        
        try:
            date.fromisoformat(fecha_vencimiento)
        except ValueError:
            raise ValueError("Formato de fecha inválido (use AAAA-MM-DD).")
        
        # Crear lote
        lote_id = self.lote_modelo.crear(
            producto_id=producto_id,
            fecha_vencimiento=fecha_vencimiento,
            cantidad_inicial=cantidad_inicial,
            numero_lote=numero_lote
        )
        
        # Sincronizar a Turso
        self._sincronizar_lote(lote_id)
        
        return lote_id
    
    def descontar_stock(self, producto_id: str, cantidad: float) -> bool:
        """
        Reduce el stock del producto usando FIFO.
        
        Args:
            producto_id: UUID del producto
            cantidad: Cantidad a descontar
        
        Returns:
            bool: True si se descontó correctamente
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        
        # Obtener lotes con stock
        lotes = self.lote_modelo.listar_por_producto(producto_id)
        lotes_con_stock = [l for l in lotes if l['cantidad_actual'] > 0]
        lotes_con_stock.sort(key=lambda l: l['fecha_vencimiento'])
        
        restante = cantidad
        for lote in lotes_con_stock:
            if restante <= 0:
                break
            
            disponible = lote['cantidad_actual']
            a_restar = min(disponible, restante)
            
            # Reducir cantidad
            self.lote_modelo.reducir_cantidad(lote['id'], a_restar)
            self._sincronizar_lote(lote['id'])
            
            restante -= a_restar
        
        if restante > 0:
            raise ValueError(f"Stock insuficiente. Faltan {restante:.2f} unidades.")
        
        return True
    
    def ajustar_stock(self, producto_id: str, cantidad: float, 
                      operacion: str = 'sumar') -> bool:
        """
        Ajusta el stock de un producto manualmente.
        
        Args:
            producto_id: UUID del producto
            cantidad: Cantidad a sumar o restar
            operacion: 'sumar' o 'restar'
        
        Returns:
            bool: True si se ajustó correctamente
        """
        if operacion not in ['sumar', 'restar']:
            raise ValueError("Operación debe ser 'sumar' o 'restar'")
        
        producto = self.producto_modelo.obtener_por_id(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado")
        
        nueva_cantidad = cantidad if operacion == 'sumar' else -cantidad
        nuevo_stock = producto['stock_actual'] + nueva_cantidad
        
        if nuevo_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        
        # Si es una suma, crear un lote de ingreso
        if operacion == 'sumar' and cantidad > 0:
            fecha_vencimiento = (date.today() + timedelta(days=365)).isoformat()
            self.crear_lote(
                producto_id=producto_id,
                fecha_vencimiento=fecha_vencimiento,
                cantidad_inicial=cantidad,
                numero_lote=f"AJUSTE-{producto['codigo_producto']}"
            )
        
        # Si es resta, descontar stock
        elif operacion == 'restar' and cantidad > 0:
            self.descontar_stock(producto_id, cantidad)
        
        return True
    
    def obtener_lotes_por_vencer(self, dias: int = 14) -> List[Dict[str, Any]]:
        """Lista lotes que vencen en los próximos X días"""
        return self.lote_modelo.lotes_por_vencer(dias_anticipacion=dias)
    
    def stock_actual_producto(self, producto_id: str) -> float:
        """Obtiene el stock actual de un producto"""
        prod = self.producto_modelo.obtener_por_id(producto_id)
        return prod['stock_actual'] if prod else 0.0
    
    def listar_lotes_producto(self, producto_id: str) -> List[Dict[str, Any]]:
        """Lista lotes de un producto"""
        return self.lote_modelo.listar_por_producto(producto_id)
    
    def obtener_producto_por_codigo(self, codigo_producto: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código"""
        return self.producto_modelo.obtener_por_codigo(codigo_producto)