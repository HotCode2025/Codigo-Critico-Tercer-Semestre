"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.5: Controlador de Ventas con UUID
==================================================
📌 USO: Gestiona facturación, notas de venta y cuenta corriente
📌 CARACTERÍSTICAS:
    - Facturación con UUID
    - ✅ Transacciones seguras en todas las operaciones críticas
    - ✅ Validaciones de stock y límite de crédito
"""

import sqlite3
import uuid
import json
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

from modelos.nota_venta import NotaVenta
from modelos.factura import Factura
from modelos.producto import Producto
from modelos.cliente import Cliente
from modelos.cobro import Cobro
from modelos.cheque import Cheque
from modelos.cuenta_corriente import CuentaCorriente
from controladores.controlador_stock import ControladorStock
from utilidades.turso_client import get_turso_client
from utilidades.sync_manager import SyncManager
from utilidades.sync_utils import SyncDirection


class ControladorVentas:
    """
    Controlador para gestionar ventas con transacciones seguras.
    """
    
    def __init__(self, db: sqlite3.Connection):
        """Inicializa el controlador de ventas"""
        self.db = db
        self.db.row_factory = sqlite3.Row
        
        # Modelos
        self.nota_modelo = NotaVenta(db)
        self.factura_modelo = Factura(db)
        self.producto_modelo = Producto(db)
        self.cliente_modelo = Cliente(db)
        self.cobro_modelo = Cobro(db)
        self.cheque_modelo = Cheque(db)
        self.cc_modelo = CuentaCorriente(db)
        self.stock_ctrl = ControladorStock(db)
        
        # Sync
        self.sync_manager = SyncManager()
        
        # Crear tablas auxiliares
        self._crear_tablas_auxiliares()
    
    def _crear_tablas_auxiliares(self):
        """Crea tablas auxiliares si no existen"""
        try:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS pedidos_procesados (
                    id TEXT PRIMARY KEY,
                    factura_id TEXT NOT NULL UNIQUE,
                    fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    procesado_por TEXT,
                    observaciones TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pedidos_procesados_factura 
                ON pedidos_procesados(factura_id)
            """)
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Error creando tablas auxiliares: {e}")
    
    # ============================================================
    # ✅ ANULAR FACTURA CON TRANSACCIÓN SEGURA
    # ============================================================
    
    def anular_factura(self, factura_id: str, motivo: str = None, 
                       usuario_id: str = None) -> bool:
        """
        ✅ Anula una factura y revierte el stock con transacción segura.
        
        Args:
            factura_id: UUID de la factura
            motivo: Motivo de la anulación
            usuario_id: UUID del usuario que anula (para auditoría)
        
        Returns:
            bool: True si se anuló correctamente
        
        Raises:
            ValueError: Si la factura no existe, ya está anulada, o tiene cobros asociados
            PermissionError: Si el usuario no tiene permisos
        """
        try:
            with self.db:  # ✅ Transacción automática - rollback en caso de error
                
                # 1. Obtener factura
                factura = self.factura_modelo.obtener_por_id(factura_id)
                if not factura:
                    raise ValueError("Factura no encontrada.")
                
                if factura['estado'] == 'ANULADA':
                    raise ValueError("La factura ya está anulada.")
                
                # 2. Verificar si hay cobros asociados
                if self._factura_tiene_cobros(factura_id):
                    raise ValueError("No se puede anular una factura con cobros asociados.")
                
                # 3. Verificar si hay pagos asociados
                if self._factura_tiene_pagos(factura_id):
                    raise ValueError("No se puede anular una factura con pagos registrados.")
                
                # 4. Verificar permisos (si se proporciona usuario)
                if usuario_id:
                    if not self._verificar_permisos_anulacion(usuario_id):
                        raise PermissionError("No tiene permisos para anular facturas.")
                
                # 5. Obtener saldo anterior del cliente
                cliente = self.cliente_modelo.obtener_por_id(factura['cliente_id'])
                if not cliente:
                    raise ValueError("Cliente no encontrado.")
                
                saldo_anterior = cliente['saldo_cuenta_corriente'] or 0
                saldo_original_antes_factura = factura.get('saldo_anterior_cliente', saldo_anterior)
                
                # 6. Revertir stock (devolver productos)
                detalles = self.factura_modelo.obtener_detalles(factura_id)
                
                for det in detalles:
                    producto = self.producto_modelo.obtener_por_id(det['producto_id'])
                    if not producto:
                        self._registrar_advertencia(
                            f"Producto {det['producto_id']} no encontrado al anular factura {factura_id}"
                        )
                        continue
                    
                    # Crear lote de reversión
                    self.stock_ctrl.crear_lote(
                        producto_id=det['producto_id'],
                        fecha_vencimiento=(date.today() + timedelta(days=365)).isoformat(),
                        cantidad_inicial=det['cantidad'],
                        numero_lote=f"REV-{factura_id[:8]}"
                    )
                
                # 7. Actualizar saldo del cliente
                nuevo_saldo = saldo_original_antes_factura
                self.cliente_modelo.actualizar(
                    factura['cliente_id'], 
                    saldo_cuenta_corriente=nuevo_saldo
                )
                
                # 8. Registrar movimiento de anulación
                self.cc_modelo.registrar_movimiento(
                    cliente_id=factura['cliente_id'],
                    tipo_movimiento='ANULACION',
                    importe=-factura['total'],
                    referencia_id=factura_id,
                    observaciones=motivo or f"Anulación factura {factura['numero_factura']}"
                )
                
                # 9. Marcar factura como anulada
                self.factura_modelo.anular(factura_id)
                
                # 10. Registrar en log de auditoría
                self._registrar_auditoria(
                    accion='ANULAR_FACTURA',
                    factura_id=factura_id,
                    usuario_id=usuario_id,
                    motivo=motivo
                )
                
                # 11. Sincronizar a Turso (opcional, fuera de la transacción)
                try:
                    client = get_turso_client()
                    if client.is_connected():
                        client.update('facturas', {'estado': 'ANULADA'}, 'id = ?', [factura_id])
                except Exception as e:
                    print(f"⚠️ Error sincronizando anulación: {e}")
                
                return True
                
        except Exception as e:
            self._log_error(f"Error al anular factura {factura_id}: {e}")
            raise
    
    def _factura_tiene_cobros(self, factura_id: str) -> bool:
        """Verifica si una factura tiene cobros asociados."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM cuenta_corriente_movimientos
            WHERE referencia_id = ? AND tipo_movimiento = 'COBRO'
        """, (factura_id,))
        return cur.fetchone()[0] > 0
    
    def _factura_tiene_pagos(self, factura_id: str) -> bool:
        """Verifica si una factura tiene pagos registrados."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM cobros
            WHERE factura_ids LIKE ? OR factura_ids = ?
        """, (f"%{factura_id}%", factura_id))
        return cur.fetchone()[0] > 0
    
    def _verificar_permisos_anulacion(self, usuario_id: str) -> bool:
        """Verifica si un usuario tiene permisos para anular facturas."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT rol FROM usuarios 
            WHERE id = ? AND activo = 1
        """, (usuario_id,))
        row = cur.fetchone()
        if not row:
            return False
        return row['rol'] in ('admin', 'supervisor')
    
    def _registrar_auditoria(self, accion: str, **datos):
        """Registra una acción en el log de auditoría."""
        try:
            cur = self.db.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS auditoria (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accion TEXT NOT NULL,
                    datos TEXT,
                    usuario_id TEXT
                )
            """)
            cur.execute("""
                INSERT INTO auditoria (accion, datos, usuario_id)
                VALUES (?, ?, ?)
            """, (accion, json.dumps(datos), datos.get('usuario_id')))
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Error registrando auditoría: {e}")
    
    def _registrar_advertencia(self, mensaje: str):
        """Registra una advertencia en el log."""
        print(f"⚠️ {mensaje}")
        try:
            cur = self.db.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs_advertencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mensaje TEXT NOT NULL
                )
            """)
            cur.execute("INSERT INTO logs_advertencias (mensaje) VALUES (?)", (mensaje,))
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Error registrando advertencia: {e}")
    
    def _log_error(self, mensaje: str):
        """Registra un error en el log."""
        print(f"❌ {mensaje}")
        try:
            cur = self.db.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs_errores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mensaje TEXT NOT NULL
                )
            """)
            cur.execute("INSERT INTO logs_errores (mensaje) VALUES (?)", (mensaje,))
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Error registrando error: {e}")
    
    # ============================================================
    # ✅ FACTURAR CON TRANSACCIÓN SEGURA
    # ============================================================
    
    def _facturar_items(self, cliente_id: str, preventista_id: str,
                        items: List[Dict[str, Any]], 
                        observaciones: str = None,
                        nota_venta_id: str = None) -> str:
        """
        ✅ Factura items directamente con transacción segura.
        
        Returns:
            str: UUID de la factura creada
        """
        if not items:
            raise ValueError("Debe incluir al menos un producto.")
        
        try:
            with self.db:  # ✅ Transacción automática
                
                # 1. Validar cliente
                cliente = self.cliente_modelo.obtener_por_id(cliente_id)
                if not cliente:
                    raise ValueError("Cliente no encontrado.")
                
                # 2. Verificar stock y productos
                for item in items:
                    producto = self.producto_modelo.obtener_por_id(item['producto_id'])
                    if not producto:
                        raise ValueError(f"Producto ID {item['producto_id']} no encontrado.")
                    
                    if item['cantidad'] > producto['stock_actual']:
                        raise ValueError(
                            f"Stock insuficiente para {producto['descripcion']}. "
                            f"Disponible: {producto['stock_actual']:.2f}, "
                            f"Solicitado: {item['cantidad']:.2f}"
                        )
                
                # 3. Verificar límite de crédito (antes de facturar)
                saldo_actual = cliente['saldo_cuenta_corriente'] or 0
                limite = cliente['limite_credito'] or 0
                
                # Calcular total de la factura
                subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in items)
                iva = subtotal * 0.21 if cliente['condicion_iva'] == 'RI' else 0.0
                
                # Obtener tasa municipal
                cur = self.db.cursor()
                cur.execute("SELECT tasa_municipal_porcentaje FROM parametros WHERE id = 1")
                param = cur.fetchone()
                tasa_pct = param['tasa_municipal_porcentaje'] if param else 0.0
                tasa_municipal = subtotal * (tasa_pct / 100.0) if cliente.get('aplica_tasa_municipal') else 0.0
                total = subtotal + iva + tasa_municipal
                
                # ✅ Verificar límite de crédito (incluyendo saldo actual)
                if limite > 0:
                    if saldo_actual > limite:
                        raise ValueError(
                            f"El cliente ya supera su límite de crédito.\n"
                            f"Saldo actual: ${saldo_actual:,.2f}\n"
                            f"Límite: ${limite:,.2f}\n"
                            f"Esta factura: ${total:,.2f}"
                        )
                    
                    if saldo_actual + total > limite:
                        raise ValueError(
                            f"El cliente excedería su límite de crédito.\n"
                            f"Saldo actual: ${saldo_actual:,.2f}\n"
                            f"Esta factura: ${total:,.2f}\n"
                            f"Límite: ${limite:,.2f}"
                        )
                
                # 4. Obtener número de factura
                cur.execute("SELECT punto_venta, ultimo_numero_factura FROM parametros WHERE id = 1")
                params = cur.fetchone()
                punto_venta = params['punto_venta'] if params else '0001'
                ultimo_numero = params['ultimo_numero_factura'] if params else 1
                numero_factura = f"{punto_venta}-{ultimo_numero:08d}"
                
                # 5. Crear factura
                factura_id = self.factura_modelo.crear(
                    cliente_id=cliente_id,
                    numero_factura=numero_factura,
                    tipo_comprobante='B',
                    preventista_id=preventista_id,
                    observaciones=observaciones,
                    nota_venta_id=nota_venta_id
                )
                
                # 6. Agregar detalles y descontar stock
                for item in items:
                    producto = self.producto_modelo.obtener_por_id(item['producto_id'])
                    
                    self.factura_modelo.agregar_detalle(
                        factura_id=factura_id,
                        producto_id=item['producto_id'],
                        codigo_producto=producto['codigo_producto'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio_unitario']
                    )
                    
                    # Descontar stock
                    self.stock_ctrl.descontar_stock(item['producto_id'], item['cantidad'])
                
                # 7. Actualizar saldo del cliente
                nuevo_saldo = saldo_actual + total
                self.cliente_modelo.actualizar(cliente_id, saldo_cuenta_corriente=nuevo_saldo)
                
                # 8. Registrar movimiento en cuenta corriente
                self.cc_modelo.registrar_movimiento(
                    cliente_id=cliente_id,
                    tipo_movimiento='FACTURA',
                    importe=total,
                    referencia_id=factura_id,
                    observaciones=f"Factura {numero_factura}"
                )
                
                # 9. Actualizar número de factura
                cur.execute("UPDATE parametros SET ultimo_numero_factura = ? WHERE id = 1", 
                           (ultimo_numero + 1,))
                
                # 10. Sincronizar factura a Turso
                self._sincronizar_factura(factura_id)
                
                return factura_id
                
        except Exception as e:
            self._log_error(f"Error al facturar items: {e}")
            raise
    
    # ============================================================
    # ✅ REGISTRAR COBRO CON TRANSACCIÓN SEGURA
    # ============================================================
    
    def registrar_cobro(self, cliente_id: str, importe: float,
                        medio_pago: str = 'EFECTIVO',
                        observaciones: str = None,
                        factura_ids: List[str] = None) -> str:
        """
        ✅ Registra un cobro y actualiza la cuenta corriente con transacción segura.
        
        Returns:
            str: UUID del cobro creado
        """
        if importe <= 0:
            raise ValueError("El importe del cobro debe ser positivo.")
        
        if not factura_ids:
            factura_ids = []
        
        try:
            with self.db:  # ✅ Transacción automática
                
                # 1. Verificar cliente
                cliente = self.cliente_modelo.obtener_por_id(cliente_id)
                if not cliente:
                    raise ValueError("Cliente no encontrado.")
                
                # 2. Verificar que el cobro no supere la deuda total
                deuda_total = self._calcular_deuda_cliente(cliente_id)
                if importe > deuda_total:
                    raise ValueError(
                        f"El importe del cobro (${importe:,.2f}) supera la deuda total "
                        f"del cliente (${deuda_total:,.2f})."
                    )
                
                # 3. Registrar cobro
                cobro_id = self.cobro_modelo.registrar(
                    cliente_id=cliente_id,
                    importe=importe,
                    medio_pago=medio_pago,
                    observaciones=observaciones
                )
                
                # 4. Actualizar saldo del cliente
                saldo_actual = cliente['saldo_cuenta_corriente'] or 0
                nuevo_saldo = saldo_actual - importe
                self.cliente_modelo.actualizar(cliente_id, saldo_cuenta_corriente=nuevo_saldo)
                
                # 5. Registrar movimiento en cuenta corriente
                self.cc_modelo.registrar_movimiento(
                    cliente_id=cliente_id,
                    tipo_movimiento='COBRO',
                    importe=-importe,
                    referencia_id=cobro_id,
                    observaciones=observaciones or f"Cobro {medio_pago}"
                )
                
                # 6. Sincronizar cobro
                self._sincronizar_cobro(cobro_id)
                
                return cobro_id
                
        except Exception as e:
            self._log_error(f"Error al registrar cobro: {e}")
            raise
    
    def _calcular_deuda_cliente(self, cliente_id: str) -> float:
        """Calcula la deuda total de un cliente."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(total), 0) as total_facturas
            FROM facturas
            WHERE cliente_id = ? AND estado = 'EMITIDA'
        """, (cliente_id,))
        deuda = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COALESCE(SUM(importe), 0) as total_cobros
            FROM cobros
            WHERE cliente_id = ?
        """, (cliente_id,))
        cobrado = cur.fetchone()[0]
        
        return deuda - cobrado
    
    def _sincronizar_cobro(self, cobro_id: str):
        """Sincroniza un cobro a Turso."""
        try:
            cobro = self.cobro_modelo.obtener_por_id(cobro_id)
            if cobro:
                client = get_turso_client()
                if client.is_connected():
                    client.insert('cobros', cobro)
        except Exception as e:
            print(f"⚠️ Error sincronizando cobro: {e}")
    
    def _sincronizar_factura(self, factura_id: str):
        """Sincroniza una factura a Turso."""
        try:
            factura = self.factura_modelo.obtener_por_id(factura_id)
            if not factura:
                return
            
            client = get_turso_client()
            if client.is_connected():
                client.insert('facturas', factura)
                
                detalles = self.factura_modelo.obtener_detalles(factura_id)
                for det in detalles:
                    client.insert('factura_detalle', det)
        except Exception as e:
            print(f"⚠️ Error sincronizando factura: {e}")
    
    # ============================================================
    # NOTAS DE VENTA
    # ============================================================
    
    def crear_nota_venta(self, preventista_id: str, cliente_id: str,
                         observaciones: str = None) -> str:
        """
        Crea una nueva nota de venta.
        
        Args:
            preventista_id: UUID del preventista
            cliente_id: UUID del cliente
            observaciones: Observaciones de la nota
        
        Returns:
            str: UUID de la nota creada
        """
        # Generar número de nota
        cur = self.db.cursor()
        cur.execute("SELECT MAX(CAST(SUBSTR(numero_nota, 3) AS INTEGER)) as max_num FROM notas_venta")
        row = cur.fetchone()
        max_num = row['max_num'] if row and row['max_num'] else 0
        numero_nota = f"N-{max_num + 1:06d}"
        
        nota_id = self.nota_modelo.crear(
            preventista_id=preventista_id,
            cliente_id=cliente_id,
            numero_nota=numero_nota,
            observaciones=observaciones
        )
        
        return nota_id
    
    def agregar_detalle_nota(self, nota_venta_id: str, codigo_producto: str,
                             cantidad: float, precio_unitario: float) -> str:
        """
        Agrega un detalle a una nota de venta.
        
        Args:
            nota_venta_id: UUID de la nota
            codigo_producto: Código del producto
            cantidad: Cantidad
            precio_unitario: Precio unitario
        
        Returns:
            str: UUID del detalle creado
        """
        # Buscar producto por código
        producto = self.producto_modelo.obtener_por_codigo(codigo_producto)
        producto_id = producto['id'] if producto else None
        
        detalle_id = self.nota_modelo.agregar_detalle(
            nota_venta_id=nota_venta_id,
            codigo_producto=codigo_producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            producto_id=producto_id
        )
        
        return detalle_id
    
    def facturar_desde_nota(self, nota_venta_id: str) -> str:
        """
        Factura una nota de venta completa.
        
        Args:
            nota_venta_id: UUID de la nota
        
        Returns:
            str: UUID de la factura creada
        """
        # Obtener nota
        nota = self.nota_modelo.obtener_por_id(nota_venta_id)
        if not nota:
            raise ValueError("Nota de venta no encontrada.")
        
        if nota['estado'] != 'PENDIENTE':
            raise ValueError("La nota ya fue procesada.")
        
        # Obtener detalles
        detalles = self.nota_modelo.obtener_detalles(nota_venta_id)
        if not detalles:
            raise ValueError("La nota no tiene productos.")
        
        # Preparar items para facturación
        items = []
        for det in detalles:
            # Verificar que tenga producto_id
            if not det.get('producto_id'):
                # Buscar producto por código
                producto = self.producto_modelo.obtener_por_codigo(det['codigo_producto'])
                if producto:
                    det['producto_id'] = producto['id']
                else:
                    raise ValueError(f"Producto '{det['codigo_producto']}' no encontrado.")
            
            items.append({
                'producto_id': det['producto_id'],
                'cantidad': det['cantidad'],
                'precio_unitario': det['precio_unitario']
            })
        
        # Facturar items
        factura_id = self._facturar_items(
            cliente_id=nota['cliente_id'],
            preventista_id=nota['preventista_id'],
            items=items,
            observaciones=f"Factura desde nota {nota['numero_nota']}",
            nota_venta_id=nota_venta_id
        )
        
        # Marcar nota como facturada
        self.nota_modelo.cambiar_estado(nota_venta_id, 'FACTURADA')
        
        return factura_id
    
    def emitir_factura_directa(self, cliente_id: str, preventista_id: str,
                               tipo_comprobante: str, numero_factura: str,
                               items: List[Dict[str, Any]],
                               observaciones: str = None) -> str:
        """
        Emite una factura directa (sin nota de venta).
        
        Args:
            cliente_id: UUID del cliente
            preventista_id: UUID del preventista
            tipo_comprobante: Tipo de comprobante (A, B, C)
            numero_factura: Número de factura
            items: Lista de items con producto_id, cantidad, precio_unitario
            observaciones: Observaciones de la factura
        
        Returns:
            str: UUID de la factura creada
        """
        return self._facturar_items(
            cliente_id=cliente_id,
            preventista_id=preventista_id,
            items=items,
            observaciones=observaciones
        )
    
    # ============================================================
    # ✅ PEDIDOS PENDIENTES
    # ============================================================
    
    def contar_pedidos_pendientes(self) -> int:
        """
        ✅ Cuenta los pedidos pendientes (facturas no procesadas).
        
        Returns:
            int: Cantidad de pedidos pendientes
        """
        cur = self.db.cursor()
        
        # Facturas que NO están en pedidos_procesados
        cur.execute("""
            SELECT COUNT(*) as total
            FROM facturas f
            WHERE f.estado = 'EMITIDA'
            AND NOT EXISTS (
                SELECT 1 FROM pedidos_procesados pp 
                WHERE pp.factura_id = f.id
            )
        """)
        row = cur.fetchone()
        return row['total'] if row else 0
    
    def obtener_pedidos_pendientes(self, limite: int = 100) -> List[Dict[str, Any]]:
        """
        ✅ Obtiene los pedidos pendientes (facturas no procesadas).
        
        Args:
            limite: Límite de resultados
        
        Returns:
            Lista de pedidos pendientes
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT 
                f.id,
                f.numero_factura,
                f.fecha,
                f.total,
                f.tipo_comprobante,
                c.razon_social as cliente_nombre,
                f.observaciones
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.estado = 'EMITIDA'
            AND NOT EXISTS (
                SELECT 1 FROM pedidos_procesados pp 
                WHERE pp.factura_id = f.id
            )
            ORDER BY f.fecha ASC
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cur.fetchall()]
    
    def obtener_historial_pedidos(self, limite: int = 100) -> List[Dict[str, Any]]:
        """
        ✅ Obtiene el historial de pedidos procesados.
        
        Args:
            limite: Límite de resultados
        
        Returns:
            Lista de pedidos procesados
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT 
                f.id as factura_id,
                f.numero_factura,
                f.fecha,
                f.total,
                f.tipo_comprobante,
                c.razon_social as cliente_nombre,
                pp.fecha_procesado,
                pp.procesado_por,
                pp.observaciones
            FROM pedidos_procesados pp
            JOIN facturas f ON pp.factura_id = f.id
            JOIN clientes c ON f.cliente_id = c.id
            ORDER BY pp.fecha_procesado DESC
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cur.fetchall()]
    
    def marcar_pedido_procesado(self, factura_id: str, 
                                procesado_por: str = None, 
                                observaciones: str = None) -> bool:
        """
        ✅ Marca un pedido como procesado.
        
        Args:
            factura_id: UUID de la factura
            procesado_por: Nombre de quien procesa
            observaciones: Observaciones del procesamiento
        
        Returns:
            bool: True si se procesó correctamente
        """
        # Verificar que la factura existe
        factura = self.factura_modelo.obtener_por_id(factura_id)
        if not factura:
            raise ValueError("Factura no encontrada")
        
        # Verificar que no esté ya procesada
        cur = self.db.cursor()
        cur.execute("SELECT id FROM pedidos_procesados WHERE factura_id = ?", (factura_id,))
        if cur.fetchone():
            raise ValueError("El pedido ya está procesado")
        
        # Crear registro de pedido procesado
        pedido_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO pedidos_procesados (
                id, factura_id, fecha_procesado, procesado_por, observaciones
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            pedido_id,
            factura_id,
            datetime.now().isoformat(),
            procesado_por or "Sistema",
            observaciones
        ))
        self.db.commit()
        
        return True
    
    def obtener_detalle_pedido(self, factura_id: str) -> List[Dict[str, Any]]:
        """
        ✅ Obtiene el detalle de un pedido.
        
        Args:
            factura_id: UUID de la factura
        
        Returns:
            Lista de productos del pedido
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT 
                fd.producto_id,
                fd.codigo_producto,
                p.descripcion,
                fd.cantidad,
                fd.precio_unitario,
                (fd.cantidad * fd.precio_unitario) as subtotal
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            WHERE fd.factura_id = ?
            ORDER BY p.descripcion
        """, (factura_id,))
        return [dict(row) for row in cur.fetchall()]
    
    # ============================================================
    # CUENTA CORRIENTE
    # ============================================================
    
    def obtener_movimientos_cliente(self, cliente_id: str, 
                                    desde: str = None, 
                                    hasta: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene los movimientos de cuenta corriente de un cliente.
        
        Args:
            cliente_id: UUID del cliente
            desde: Fecha de inicio (YYYY-MM-DD)
            hasta: Fecha de fin (YYYY-MM-DD)
        
        Returns:
            Lista de movimientos
        """
        return self.cc_modelo.movimientos(cliente_id, desde, hasta)
    
    def obtener_facturas_pendientes_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene facturas pendientes de cobro de un cliente.
        
        Args:
            cliente_id: UUID del cliente
        
        Returns:
            Lista de facturas pendientes
        """
        cur = self.db.cursor()
        cur.execute("""
            SELECT 
                f.id,
                f.numero_factura,
                f.fecha,
                f.total,
                f.saldo_anterior_cliente,
                COALESCE((
                    SELECT SUM(importe) 
                    FROM cuenta_corriente_movimientos 
                    WHERE referencia_id = f.id AND tipo_movimiento = 'COBRO'
                ), 0) as total_cobrado
            FROM facturas f
            WHERE f.cliente_id = ? AND f.estado = 'EMITIDA'
            ORDER BY f.fecha ASC
        """, (cliente_id,))
        
        resultados = []
        for row in cur.fetchall():
            saldo_pendiente = row['total'] - row['total_cobrado']
            if saldo_pendiente > 0:
                resultados.append({
                    'id': row['id'],
                    'numero_factura': row['numero_factura'],
                    'fecha': row['fecha'],
                    'total': row['total'],
                    'saldo_anterior_cliente': row['saldo_anterior_cliente'],
                    'saldo_pendiente': saldo_pendiente
                })
        
        return resultados
    
    # ============================================================
    # PROCESAR NOTAS PENDIENTES (codigo_producto → producto_id)
    # ============================================================
    
    def procesar_notas_pendientes(self) -> Dict[str, Any]:
        """
        ✅ Procesa notas de venta pendientes convirtiendo codigo_producto a producto_id.
        
        Retorna:
            Diccionario con resultados del procesamiento
        """
        from utilidades.central_sync import procesar_notas_pendientes as _procesar_notas
        return _procesar_notas(self.db)
    
    # ============================================================
    # SINCRONIZACIÓN
    # ============================================================
    
    def sincronizar_con_turso(self) -> Dict[str, Any]:
        """
        Sincroniza ventas con Turso.
        """
        from utilidades.central_sync import sincronizar_ahora
        return sincronizar_ahora(self.db)