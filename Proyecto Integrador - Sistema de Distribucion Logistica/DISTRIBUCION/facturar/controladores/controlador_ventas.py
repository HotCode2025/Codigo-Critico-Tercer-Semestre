"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Ventas – Manejo completo de facturación, pagos y cuenta corriente.
Soporta:
- Emisión de facturas con descuento de stock
- Pagos parciales y totales
- Registro de cheques
- Cancelación/anulación de facturas
- Reversión de stock al anular
- Resumen de cuenta corriente por cliente
- Guarda saldo anterior del cliente para anulación correcta
- Pedidos para armar (facturas pendientes de procesar)
- RECEPCIÓN DE NOTAS DESDE TURSO CON CÓDIGO DE PRODUCTO
- PROCESAMIENTO DE NOTAS PENDIENTES (codigo_producto → producto_id)
"""

import sqlite3
import uuid
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from modelos.nota_venta import NotaVenta
from modelos.factura import Factura
from modelos.producto import Producto
from modelos.cliente import Cliente
from modelos.cobro import Cobro
from modelos.cheque import Cheque
from controladores.controlador_stock import ControladorStock
from utilidades.central_sync import enviar_a_turso


class ControladorVentas:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.nota_venta_modelo = NotaVenta(db)
        self.factura_modelo = Factura(db)
        self.producto_modelo = Producto(db)
        self.cliente_modelo = Cliente(db)
        self.cobro_modelo = Cobro(db)
        self.cheque_modelo = Cheque(db)
        self.stock_ctrl = ControladorStock(db)
        self.db.row_factory = sqlite3.Row
        
        self._crear_tabla_pedidos()

    def _crear_tabla_pedidos(self):
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
            self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_pedidos_procesados_fecha 
                ON pedidos_procesados(fecha_procesado)
            """)
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Error creando tabla pedidos_procesados: {e}")

    # ============================================================
    # PROCESAR NOTAS PENDIENTES (codigo_producto → producto_id)
    # ============================================================
    
    def procesar_notas_pendientes(self) -> int:
        """
        Procesa todas las notas de venta que están en estado PENDIENTE
        pero que tienen codigo_producto en lugar de producto_id.
        Convierte codigo_producto a producto_id y actualiza la nota.
        Retorna la cantidad de notas procesadas.
        """
        cur = self.db.cursor()
        
        # Buscar notas pendientes que tienen detalle con codigo_producto
        cur.execute("""
            SELECT DISTINCT n.id, n.numero_nota, n.cliente_id, n.preventista_id
            FROM notas_venta n
            JOIN nota_venta_detalle nd ON n.id = nd.nota_venta_id
            WHERE n.estado = 'PENDIENTE' 
            AND nd.codigo_producto IS NOT NULL
            AND nd.producto_id IS NULL
        """)
        
        notas = cur.fetchall()
        procesadas = 0
        
        if not notas:
            print("✅ No hay notas pendientes con codigo_producto por procesar.")
            return 0
        
        print(f"📋 Encontradas {len(notas)} notas con codigo_producto por procesar.")
        
        for nota in notas:
            nota_id = nota['id']
            numero_nota = nota['numero_nota']
            
            # Obtener detalles con codigo_producto
            cur.execute("""
                SELECT id, codigo_producto, cantidad, precio_unitario
                FROM nota_venta_detalle
                WHERE nota_venta_id = ? AND codigo_producto IS NOT NULL AND producto_id IS NULL
            """, (nota_id,))
            
            detalles = cur.fetchall()
            
            if not detalles:
                continue
            
            todos_ok = True
            productos_asignados = 0
            
            for det in detalles:
                codigo = det['codigo_producto']
                
                # Buscar producto por código
                cur.execute("SELECT id FROM productos WHERE codigo_producto = ? AND activo = 1", (codigo,))
                prod = cur.fetchone()
                
                if prod:
                    # Actualizar detalle con producto_id
                    cur.execute("""
                        UPDATE nota_venta_detalle 
                        SET producto_id = ? 
                        WHERE id = ?
                    """, (prod['id'], det['id']))
                    productos_asignados += 1
                    print(f"   ✅ Producto '{codigo}' → ID {prod['id']}")
                else:
                    print(f"   ⚠️ Producto con código '{codigo}' NO encontrado en nota {numero_nota}")
                    todos_ok = False
            
            if todos_ok:
                self.db.commit()
                procesadas += 1
                print(f"✅ Nota {numero_nota} procesada: {productos_asignados} productos asignados")
            else:
                self.db.rollback()
                print(f"❌ Nota {numero_nota} tiene productos no encontrados. No se procesó.")
        
        print(f"📊 Total notas procesadas: {procesadas}")
        return procesadas

    # ============================================================
    # RECEPCIÓN DE NOTAS DESDE TURSO
    # ============================================================
    
    def obtener_producto_por_codigo(self, codigo_producto: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código"""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM productos WHERE codigo_producto = ? AND activo = 1", (codigo_producto,))
        row = cur.fetchone()
        return dict(row) if row else None

    def procesar_nota_desde_turso(self, nota_data: dict) -> bool:
        """
        Procesa una nota de venta recibida desde Turso.
        Busca los productos por código en lugar de ID.
        """
        try:
            detalles = nota_data.get('detalle', [])
            if not detalles:
                return False
            
            items = []
            for detalle in detalles:
                codigo = detalle.get('codigo_producto')
                if not codigo:
                    continue
                
                producto = self.obtener_producto_por_codigo(codigo)
                if not producto:
                    print(f"⚠️ Producto con código {codigo} no encontrado en Central")
                    continue
                
                items.append({
                    'producto_id': producto['id'],
                    'codigo_producto': codigo,
                    'cantidad': detalle.get('cantidad', 0),
                    'precio_unitario': detalle.get('precio_unitario', 0)
                })
            
            if not items:
                return False
            
            # Crear nota de venta local con los items encontrados
            nota_id = str(uuid.uuid4())
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO notas_venta 
                (id, preventista_id, cliente_id, fecha, numero_nota, total, observaciones, estado, procesado_central)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDIENTE', 1)
            """, (
                nota_id,
                nota_data.get('preventista_id'),
                nota_data.get('cliente_id'),
                nota_data.get('fecha', date.today().isoformat()),
                nota_data.get('numero_nota'),
                nota_data.get('total', 0),
                nota_data.get('observaciones')
            ))
            
            for item in items:
                detalle_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO nota_venta_detalle 
                    (id, nota_venta_id, producto_id, codigo_producto, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    detalle_id,
                    nota_id,
                    item['producto_id'],
                    item['codigo_producto'],
                    item['cantidad'],
                    item['precio_unitario']
                ))
            
            self.db.commit()
            print(f"✅ Nota {nota_data.get('numero_nota')} procesada desde Turso")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error procesando nota desde Turso: {e}")
            return False

    # =================== NOTAS DE VENTA ===================
    
    def crear_nota_venta(self, preventista_id: int, cliente_id: int,
                         numero_nota: str, observaciones: str = None) -> str:
        if not preventista_id or not cliente_id:
            raise ValueError("Preventista y cliente son obligatorios.")
        return self.nota_venta_modelo.crear(preventista_id, cliente_id,
                                            numero_nota, observaciones)

    def agregar_detalle_nota(self, nota_venta_id: str, producto_id: int,
                             cantidad: float, precio_unitario: float = None) -> str:
        producto = self.producto_modelo.obtener_por_id(producto_id)
        if not producto:
            raise ValueError("Producto no encontrado.")
        if precio_unitario is None:
            precio_unitario = producto['precio_venta']
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        return self.nota_venta_modelo.agregar_detalle(nota_venta_id, producto_id,
                                                      cantidad, precio_unitario)

    def listar_notas_pendientes(self) -> List[Dict[str, Any]]:
        return self.nota_venta_modelo.listar_por_estado('PENDIENTE')

    def facturar_desde_nota(self, nota_venta_id: str) -> str:
        """
        Factura una nota de venta.
        Convierte automáticamente codigo_producto a producto_id si es necesario.
        """
        try:
            nota = self.nota_venta_modelo.obtener_por_id(nota_venta_id)
            if not nota or nota['estado'] != 'PENDIENTE':
                raise ValueError("La nota de venta no existe o ya fue procesada.")

            cur = self.db.cursor()
            
            # ✅ PRIMERO: Convertir codigo_producto a producto_id si es necesario
            cur.execute("""
                SELECT id, codigo_producto, producto_id
                FROM nota_venta_detalle
                WHERE nota_venta_id = ? AND codigo_producto IS NOT NULL AND producto_id IS NULL
            """, (nota_venta_id,))
            
            pendientes = cur.fetchall()
            if pendientes:
                print(f"📋 Convirtiendo {len(pendientes)} productos en nota {nota['numero_nota']}")
                for det in pendientes:
                    codigo = det['codigo_producto']
                    cur.execute("SELECT id FROM productos WHERE codigo_producto = ? AND activo = 1", (codigo,))
                    prod = cur.fetchone()
                    if prod:
                        cur.execute("UPDATE nota_venta_detalle SET producto_id = ? WHERE id = ?", 
                                   (prod['id'], det['id']))
                        print(f"  ✅ {codigo} → producto_id {prod['id']}")
                    else:
                        raise ValueError(f"Producto con código '{codigo}' no encontrado en Central")
                self.db.commit()
                print(f"✅ Conversión completada para nota {nota['numero_nota']}")
            
            # ✅ SEGUNDO: Obtener detalles con producto_id
            cur.execute("""
                SELECT nd.producto_id, nd.cantidad, nd.precio_unitario, p.stock_actual
                FROM nota_venta_detalle nd
                JOIN productos p ON nd.producto_id = p.id
                WHERE nd.nota_venta_id = ?
            """, (nota_venta_id,))
            
            detalles = [dict(row) for row in cur.fetchall()]
            
            if not detalles:
                raise ValueError("La nota no tiene productos con producto_id válido.")
            
            # Verificar stock
            for det in detalles:
                if det['cantidad'] > det['stock_actual']:
                    raise ValueError(f"Stock insuficiente para producto ID {det['producto_id']}")
            
            items = [{
                'producto_id': d['producto_id'],
                'cantidad': d['cantidad'],
                'precio_unitario': d['precio_unitario']
            } for d in detalles]
            
            return self._facturar_items(nota, items)
            
        except Exception as e:
            raise e

    def _facturar_items(self, nota: dict, items: List[Dict[str, Any]]) -> str:
        """
        Factura una nota con los items ya convertidos a producto_id.
        Método interno usado por facturar_desde_nota.
        """
        cur = self.db.cursor()
        
        cur.execute("SELECT punto_venta, ultimo_numero_factura FROM parametros WHERE id = 1")
        params = cur.fetchone()
        punto_venta = params['punto_venta'] if params else '0001'
        ultimo_numero = params['ultimo_numero_factura'] if params else 1
        numero_factura = f"{punto_venta}-{ultimo_numero:08d}"
        
        factura_id = self.emitir_factura_directa(
            cliente_id=nota['cliente_id'],
            preventista_id=nota['preventista_id'],
            tipo_comprobante='B',
            numero_factura=numero_factura,
            items=items,
            observaciones=f"Facturada desde nota {nota['numero_nota']}"
        )
        
        cur.execute("UPDATE parametros SET ultimo_numero_factura = ? WHERE id = 1", 
                   (ultimo_numero + 1,))
        
        self.nota_venta_modelo.cambiar_estado(nota['id'], 'FACTURADA', commit=True)
        
        return factura_id

    # =================== FACTURACIÓN ===================
    
    def emitir_factura_directa(self, cliente_id: int, preventista_id: int,
                               tipo_comprobante: str, numero_factura: str,
                               items: List[Dict[str, Any]],
                               observaciones: str = None) -> str:
        self.db.execute("BEGIN TRANSACTION")
        try:
            if not items:
                raise ValueError("Debe incluir al menos un producto.")
            
            cliente = self.cliente_modelo.obtener_por_id(cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado.")
            
            saldo_antes_de_factura = cliente['saldo_cuenta_corriente'] or 0.0
            
            cur = self.db.cursor()
            cur.execute("SELECT tasa_municipal_porcentaje FROM parametros WHERE id = 1")
            param = cur.fetchone()
            tasa_porcentaje = param['tasa_municipal_porcentaje'] if param else 0.0
            
            subtotal = 0.0
            for item in items:
                subtotal += item['cantidad'] * item.get('precio_unitario', 0)
            
            iva = subtotal * 0.21 if cliente['condicion_iva'] == 'RI' else 0.0
            tasa_municipal = subtotal * (tasa_porcentaje / 100.0) if cliente.get('aplica_tasa_municipal') else 0.0
            total = subtotal + iva + tasa_municipal
            
            nuevo_saldo = saldo_antes_de_factura + total
            
            if cliente['limite_credito'] > 0 and nuevo_saldo > cliente['limite_credito']:
                raise ValueError(f"El cliente excede su límite de crédito. "
                               f"Límite: ${cliente['limite_credito']:,.2f}, "
                               f"Saldo actual: ${saldo_antes_de_factura:,.2f}, "
                               f"Nuevo saldo: ${nuevo_saldo:,.2f}")
            
            for item in items:
                producto = self.producto_modelo.obtener_por_id(item['producto_id'])
                if not producto:
                    raise ValueError(f"Producto ID {item['producto_id']} no encontrado")
                if item['cantidad'] > producto['stock_actual']:
                    raise ValueError(f"Stock insuficiente para {producto['descripcion']}. "
                                   f"Stock disponible: {producto['stock_actual']:.0f}")
            
            factura_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO facturas (id, cliente_id, preventista_id, tipo_comprobante,
                   numero_factura, fecha, subtotal, iva, tasa_municipal, total, 
                   observaciones, estado, saldo_anterior_cliente)
                   VALUES (?, ?, ?, ?, ?, date('now'), ?, ?, ?, ?, ?, 'EMITIDA', ?)
            """, (factura_id, cliente_id, preventista_id, tipo_comprobante,
                  numero_factura, subtotal, iva, tasa_municipal, total, observaciones, 
                  saldo_antes_de_factura))
            
            for item in items:
                detalle_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO factura_detalle (id, factura_id, producto_id, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?, ?)
                """, (detalle_id, factura_id, item['producto_id'], item['cantidad'], 
                      item.get('precio_unitario', 0)))
                
                self.stock_ctrl.descontar_stock(item['producto_id'], item['cantidad'])
            
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?", 
                       (nuevo_saldo, cliente_id))
            
            mov_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO cuenta_corriente_movimientos
                (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe, saldo_resultante, observaciones)
                VALUES (?, ?, date('now'), 'FACTURA', ?, ?, ?, ?)
            """, (mov_id, cliente_id, factura_id, total, nuevo_saldo, 
                  f"Factura {numero_factura}"))
            
            self.db.commit()
            
            try:
                enviar_a_turso("""
                    INSERT INTO facturas (id, cliente_id, preventista_id, tipo_comprobante,
                       numero_factura, fecha, subtotal, iva, tasa_municipal, total, 
                       observaciones, estado)
                    VALUES (?, ?, ?, ?, ?, date('now'), ?, ?, ?, ?, ?, 'EMITIDA')
                """, [factura_id, cliente_id, preventista_id, tipo_comprobante,
                      numero_factura, subtotal, iva, tasa_municipal, total, observaciones])
            except Exception as e:
                print(f"⚠️ Error sincronizando factura con Turso: {e}")
            
            return factura_id
            
        except Exception as e:
            self.db.rollback()
            raise e

    # =================== PEDIDOS PARA ARMAR ===================
    
    def obtener_pedidos_pendientes(self) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("""
            SELECT f.id, f.numero_factura, f.fecha, f.total, 
                   c.razon_social as cliente_nombre, c.id as cliente_id,
                   f.tipo_comprobante,
                   (SELECT COUNT(*) FROM pedidos_procesados WHERE factura_id = f.id) as ya_procesado
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id
            WHERE f.estado = 'EMITIDA'
            ORDER BY f.fecha ASC
        """)
        resultados = []
        for row in cur.fetchall():
            if row['ya_procesado'] == 0:
                resultados.append(dict(row))
        return resultados

    def marcar_pedido_procesado(self, factura_id: str, procesado_por: str = None, 
                                observaciones: str = None) -> bool:
        cur = self.db.cursor()
        cur.execute("SELECT id FROM facturas WHERE id = ? AND estado = 'EMITIDA'", (factura_id,))
        if not cur.fetchone():
            raise ValueError("Factura no encontrada o no está emitida.")
        
        cur.execute("SELECT id FROM pedidos_procesados WHERE factura_id = ?", (factura_id,))
        if cur.fetchone():
            raise ValueError("Este pedido ya fue procesado anteriormente.")
        
        pedido_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO pedidos_procesados (id, factura_id, procesado_por, observaciones)
            VALUES (?, ?, ?, ?)
        """, (pedido_id, factura_id, procesado_por, observaciones))
        self.db.commit()
        return True

    def obtener_detalle_pedido(self, factura_id: str) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("""
            SELECT p.descripcion, p.codigo_producto, fd.cantidad, fd.precio_unitario,
                   (fd.cantidad * fd.precio_unitario) as subtotal
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            WHERE fd.factura_id = ?
        """, (factura_id,))
        return [dict(row) for row in cur.fetchall()]

    def contar_pedidos_pendientes(self) -> int:
        pedidos = self.obtener_pedidos_pendientes()
        return len(pedidos)

    def obtener_historial_pedidos(self, limite: int = 50) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("""
            SELECT pp.id, pp.factura_id, pp.fecha_procesado, pp.procesado_por, pp.observaciones,
                   f.numero_factura, f.fecha, f.total, f.tipo_comprobante,
                   c.razon_social as cliente_nombre
            FROM pedidos_procesados pp
            JOIN facturas f ON pp.factura_id = f.id
            JOIN clientes c ON f.cliente_id = c.id
            ORDER BY pp.fecha_procesado DESC
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cur.fetchall()]

    def obtener_pedido_procesado_por_factura(self, factura_id: str) -> Optional[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("""
            SELECT pp.*, f.numero_factura, f.fecha, f.total,
                   c.razon_social as cliente_nombre
            FROM pedidos_procesados pp
            JOIN facturas f ON pp.factura_id = f.id
            JOIN clientes c ON f.cliente_id = c.id
            WHERE pp.factura_id = ?
        """, (factura_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    # =================== COBROS Y PAGOS ===================
    
    def registrar_cobro(self, cliente_id: int, importe: float, 
                        medio_pago: str = 'EFECTIVO', 
                        observaciones: str = None,
                        factura_ids: List[str] = None) -> str:
        if importe <= 0:
            raise ValueError("El importe del cobro debe ser positivo.")
        
        self.db.execute("BEGIN TRANSACTION")
        try:
            cliente = self.cliente_modelo.obtener_por_id(cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado.")
            
            saldo_actual = cliente['saldo_cuenta_corriente']
            nuevo_saldo = saldo_actual - importe
            
            cobro_id = str(uuid.uuid4())
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO cobros (id, cliente_id, fecha, importe, medio_pago, observaciones)
                VALUES (?, ?, date('now'), ?, ?, ?)
            """, (cobro_id, cliente_id, importe, medio_pago, observaciones))
            
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?", 
                       (nuevo_saldo, cliente_id))
            
            mov_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO cuenta_corriente_movimientos
                (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe, saldo_resultante, observaciones)
                VALUES (?, ?, date('now'), 'COBRO', ?, ?, ?, ?)
            """, (mov_id, cliente_id, cobro_id, -importe, nuevo_saldo, 
                  f"Cobro {medio_pago} por ${importe:,.2f}"))
            
            if factura_ids:
                for factura_id in factura_ids:
                    cur.execute("UPDATE facturas SET estado = 'PAGADA' WHERE id = ? AND estado = 'EMITIDA'", (factura_id,))
            
            self.db.commit()
            
            try:
                enviar_a_turso("""
                    INSERT INTO cobros (id, cliente_id, fecha, importe, medio_pago, observaciones)
                    VALUES (?, ?, date('now'), ?, ?, ?)
                """, [cobro_id, cliente_id, importe, medio_pago, observaciones])
            except Exception as e:
                print(f"⚠️ Error replicando cobro a Turso: {e}")
            
            return cobro_id
            
        except Exception as e:
            self.db.rollback()
            raise e

    def registrar_cobro_con_cheque(self, cliente_id: int, importe: float,
                                    banco: str, numero_cheque: str,
                                    fecha_emision: str, fecha_vencimiento: str,
                                    factura_ids: str = None) -> str:
        self.db.execute("BEGIN TRANSACTION")
        try:
            cobro_id = self.registrar_cobro(
                cliente_id, importe, 'CHEQUE', 
                f"Cheque {banco} N°{numero_cheque}", 
                factura_ids.split(',') if factura_ids else None
            )
            
            cheque_id = str(uuid.uuid4())
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO cheques (id, cobro_id, cliente_id, banco, numero_cheque,
                       fecha_emision, fecha_vencimiento, importe, estado, factura_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EN_CARTERA', ?)
            """, (cheque_id, cobro_id, cliente_id, banco, numero_cheque,
                  fecha_emision, fecha_vencimiento, importe, factura_ids))
            
            self.db.commit()
            return cheque_id
            
        except Exception as e:
            self.db.rollback()
            raise e

    # =================== ANULACIÓN ===================
    
    def anular_factura(self, factura_id: str, motivo: str = None) -> bool:
        self.db.execute("BEGIN TRANSACTION")
        try:
            cur = self.db.cursor()
            
            cur.execute("SELECT * FROM facturas WHERE id = ? AND estado != 'ANULADA'", (factura_id,))
            factura = cur.fetchone()
            if not factura:
                raise ValueError("Factura no encontrada o ya anulada.")
            
            saldo_antes_de_factura = factura['saldo_anterior_cliente']
            
            cur.execute("SELECT producto_id, cantidad FROM factura_detalle WHERE factura_id = ?", (factura_id,))
            detalles = cur.fetchall()
            
            for det in detalles:
                lote_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO lotes (id, producto_id, numero_lote, fecha_vencimiento, 
                                       cantidad_inicial, cantidad_actual, fecha_ingreso)
                    VALUES (?, ?, ?, ?, ?, ?, date('now'))
                """, (lote_id, det['producto_id'], f"REV-{factura_id[:8]}", 
                      date.today().isoformat(), det['cantidad'], det['cantidad']))
                
                cur.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?",
                           (det['cantidad'], det['producto_id']))
            
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = ? WHERE id = ?",
                       (saldo_antes_de_factura, factura['cliente_id']))
            
            mov_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO cuenta_corriente_movimientos
                (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe, saldo_resultante, observaciones)
                VALUES (?, ?, date('now'), 'ANULACION', ?, ?, ?, ?)
            """, (mov_id, factura['cliente_id'], factura_id, -factura['total'],
                  saldo_antes_de_factura, motivo or f"Anulación factura {factura['numero_factura']}"))
            
            cur.execute("UPDATE facturas SET estado = 'ANULADA' WHERE id = ?", (factura_id,))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    def reversar_cobro(self, cobro_id: str, motivo: str = None) -> bool:
        self.db.execute("BEGIN TRANSACTION")
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM cobros WHERE id = ?", (cobro_id,))
            cobro = cur.fetchone()
            if not cobro:
                raise ValueError("Cobro no encontrado.")
            
            cur.execute("UPDATE clientes SET saldo_cuenta_corriente = saldo_cuenta_corriente + ? WHERE id = ?",
                       (cobro['importe'], cobro['cliente_id']))
            
            mov_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO cuenta_corriente_movimientos
                (id, cliente_id, fecha, tipo_movimiento, referencia_id, importe, saldo_resultante, observaciones)
                VALUES (?, ?, date('now'), 'REVERSO_COBRO', ?, ?, ?, ?)
            """, (mov_id, cobro['cliente_id'], cobro_id, cobro['importe'],
                  cobro['importe'], motivo or f"Reverso de cobro {cobro_id[:8]}"))
            
            cur.execute("UPDATE cheques SET estado = 'RECHAZADO', observaciones = ? WHERE cobro_id = ?",
                       (motivo, cobro_id))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    # =================== CONSULTAS DE CUENTA CORRIENTE ===================
    
    def obtener_saldo_cliente(self, cliente_id: int) -> float:
        cur = self.db.cursor()
        cur.execute("SELECT saldo_cuenta_corriente FROM clientes WHERE id = ?", (cliente_id,))
        row = cur.fetchone()
        return row['saldo_cuenta_corriente'] if row else 0.0

    def obtener_movimientos_cliente(self, cliente_id: int, 
                                    fecha_desde: str = None, 
                                    fecha_hasta: str = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM cuenta_corriente_movimientos WHERE cliente_id = ?"
        params = [cliente_id]
        
        if fecha_desde:
            query += " AND fecha >= ?"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND fecha <= ?"
            params.append(fecha_hasta)
        
        query += " ORDER BY fecha DESC, created_at DESC"
        
        cur = self.db.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def obtener_resumen_cuenta_corriente(self, cliente_id: int = None) -> List[Dict[str, Any]]:
        if cliente_id:
            query = """
                SELECT c.id, c.razon_social, c.cuit, c.saldo_cuenta_corriente,
                       c.limite_credito,
                       (c.saldo_cuenta_corriente * 100.0 / NULLIF(c.limite_credito, 0)) as porcentaje_uso
                FROM clientes c
                WHERE c.id = ? AND c.activo = 1
            """
            params = [cliente_id]
        else:
            query = """
                SELECT c.id, c.razon_social, c.cuit, c.saldo_cuenta_corriente,
                       c.limite_credito,
                       (c.saldo_cuenta_corriente * 100.0 / NULLIF(c.limite_credito, 0)) as porcentaje_uso
                FROM clientes c
                WHERE c.activo = 1 AND c.saldo_cuenta_corriente != 0
                ORDER BY c.saldo_cuenta_corriente DESC
            """
            params = []
        
        cur = self.db.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def obtener_facturas_pendientes_cliente(self, cliente_id: int) -> List[Dict[str, Any]]:
        cur = self.db.cursor()
        cur.execute("""
            SELECT f.id, f.numero_factura, f.fecha, f.total,
                   COALESCE(SUM(ccm.importe), 0) as pagado,
                   (f.total - COALESCE(SUM(ccm.importe), 0)) as saldo_pendiente
            FROM facturas f
            LEFT JOIN cuenta_corriente_movimientos ccm 
                ON ccm.referencia_id = f.id AND ccm.tipo_movimiento = 'COBRO'
            WHERE f.cliente_id = ? AND f.estado = 'EMITIDA'
            GROUP BY f.id
            HAVING saldo_pendiente > 0
            ORDER BY f.fecha
        """, (cliente_id,))
        return [dict(row) for row in cur.fetchall()]

    def generar_resumen_cuenta_corriente(self, cliente_id: int) -> Dict[str, Any]:
        cliente = self.cliente_modelo.obtener_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado.")
        
        movimientos = self.obtener_movimientos_cliente(cliente_id)
        facturas_pendientes = self.obtener_facturas_pendientes_cliente(cliente_id)
        
        return {
            'cliente': cliente,
            'saldo_actual': cliente['saldo_cuenta_corriente'],
            'limite_credito': cliente['limite_credito'],
            'movimientos': movimientos,
            'facturas_pendientes': facturas_pendientes,
            'total_pendiente': sum(f['saldo_pendiente'] for f in facturas_pendientes)
        }

    def obtener_estadisticas_ventas(self, fecha_desde: str = None, fecha_hasta: str = None) -> Dict[str, Any]:
        query = "SELECT COUNT(*) as total_facturas, SUM(total) as total_ventas FROM facturas WHERE estado = 'EMITIDA'"
        params = []
        
        if fecha_desde and fecha_hasta:
            query += " AND fecha BETWEEN ? AND ?"
            params = [fecha_desde, fecha_hasta]
        
        cur = self.db.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        
        return {
            'total_facturas': row['total_facturas'] if row else 0,
            'total_ventas': row['total_ventas'] if row else 0.0
        }

    def imprimir_resumen_cuenta(self, cliente_id: int) -> str:
        resumen = self.generar_resumen_cuenta_corriente(cliente_id)
        
        html = f"""
        <html>
        <head><meta charset="UTF-8"><title>Resumen de Cuenta Corriente</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            h1 {{ color: #1A237E; text-align: center; }}
            h2 {{ color: #1565C0; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            th {{ background-color: #1A237E; color: white; padding: 8px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 6px; }}
            .total {{ font-weight: bold; font-size: 14px; text-align: right; }}
            .saldo {{ color: #D32F2F; font-size: 18px; font-weight: bold; }}
        </style>
        </head>
        <body>
            <h1>Resumen de Cuenta Corriente</h1>
            <h2>{resumen['cliente']['razon_social']}</h2>
            <p>CUIT: {resumen['cliente']['cuit'] or 'N/A'}</p>
            <p>Límite de Crédito: ${resumen['limite_credito']:,.2f}</p>
            <p>Saldo Actual: <span class="saldo">${resumen['saldo_actual']:,.2f}</span></p>
            <h3>Facturas Pendientes</h3>
            <table>
                <tr><th>Factura</th><th>Fecha</th><th>Total</th><th>Saldo Pendiente</th></tr>
        """
        for fact in resumen['facturas_pendientes']:
            html += f"""
                <tr>
                    <td>{fact['numero_factura']}</td>
                    <td>{fact['fecha']}</td>
                    <td>${fact['total']:,.2f}</td>
                    <td>${fact['saldo_pendiente']:,.2f}</td>
                </tr>
            """
        html += f"""
            </table><p class="total">Total Pendiente: ${resumen['total_pendiente']:,.2f}</p>
            <h3>Últimos Movimientos</h3>
            <table>
                <tr><th>Fecha</th><th>Tipo</th><th>Importe</th><th>Saldo Resultante</th><th>Observaciones</th></tr>
        """
        for mov in resumen['movimientos'][:20]:
            html += f"""
                <tr>
                    <td>{mov['fecha']}</td>
                    <td>{mov['tipo_movimiento']}</td>
                    <td>${mov['importe']:,.2f}</td>
                    <td>${mov['saldo_resultante']:,.2f}</td>
                    <td>{mov.get('observaciones', '')}</td>
                </tr>
            """
        html += "</table></body></html>"
        return html


if __name__ == "__main__":
    from db.db_manager import obtener_conexion
    db = obtener_conexion()
    ctrl = ControladorVentas(db)
    print("✅ Controlador de Ventas cargado correctamente")