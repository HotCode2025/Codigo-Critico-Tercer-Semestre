"""
Sincronizador simple con Turso - Usando el cliente oficial
Basado en verificar_turso.py
"""

import sqlite3
import time
import threading
from datetime import datetime
from utilidades.turso_client import get_turso_client

class SincronizadorSimple:
    def __init__(self, intervalo=60):
        self.intervalo = intervalo
        self.running = False
        self.thread = None
        self.db_path = 'distribuidora.db'
        self.client = get_turso_client()
        
        print(f"✅ Sincronizador simple inicializado (intervalo: {intervalo}s)")
        if self.client.is_connected():
            print(f"📌 Conexión a Turso: OK")
        else:
            print(f"⚠️ Sin conexión a Turso")
    
    def sincronizar_notas(self):
        """Sincroniza notas de venta desde Turso usando el cliente oficial"""
        if not self.client.is_connected():
            print(f"⚠️ [Sync] Sin conexión a Turso")
            return
        
        try:
            print(f"🔄 [Sync] Verificando notas en Turso... {datetime.now().strftime('%H:%M:%S')}")
            
            # 1. Obtener IDs de Turso usando el cliente
            notas_turso = self.client.get_all(
                "SELECT id, numero_nota, fecha, total, estado FROM notas_venta ORDER BY created_at DESC"
            )
            
            if notas_turso is None:
                print(f"⚠️ [Sync] Error obteniendo notas de Turso")
                return
            
            print(f"📥 [Sync] Notas en Turso: {len(notas_turso)}")
            
            if not notas_turso:
                return
            
            # 2. Conectar a base local (conexión separada)
            conn = sqlite3.connect(self.db_path, timeout=5)
            cursor = conn.cursor()
            
            # 3. Verificar cuáles notas ya existen
            ids_turso = [row['id'] for row in notas_turso]
            placeholders = ','.join(['?'] * len(ids_turso))
            cursor.execute(f'SELECT id FROM notas_venta WHERE id IN ({placeholders})', ids_turso)
            ids_local = [row[0] for row in cursor.fetchall()]
            
            # 4. Identificar notas nuevas
            ids_nuevos = set(ids_turso) - set(ids_local)
            
            if not ids_nuevos:
                print(f"✅ [Sync] No hay notas nuevas")
                conn.close()
                return
            
            print(f"📥 [Sync] {len(ids_nuevos)} notas nuevas encontradas")
            
            # 5. Descargar notas completas
            for id_nota in ids_nuevos:
                print(f"   📄 Descargando nota {id_nota[:8]}...")
                
                # Obtener nota completa usando el cliente
                nota = self.client.get_one(f'SELECT * FROM notas_venta WHERE id = "{id_nota}"')
                
                if nota:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO notas_venta 
                            (id, preventista_id, cliente_id, fecha, numero_nota, 
                             total, observaciones, estado, procesado_central, 
                             created_at, updated_at, version)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            nota.get('id'), nota.get('preventista_id'), nota.get('cliente_id'),
                            nota.get('fecha'), nota.get('numero_nota'),
                            float(nota.get('total', 0)),
                            nota.get('observaciones'), nota.get('estado'),
                            int(nota.get('procesado_central', 0)),
                            nota.get('created_at'), nota.get('updated_at'),
                            int(nota.get('version', 1))
                        ))
                        print(f"   ✅ {nota.get('numero_nota')} - Total: ${float(nota.get('total', 0)):,.2f}")
                        conn.commit()
                    except Exception as e:
                        print(f"   ❌ Error insertando nota: {e}")
                
                # Obtener detalles
                detalles = self.client.get_all(f'SELECT * FROM nota_venta_detalle WHERE nota_venta_id = "{id_nota}"')
                
                if detalles:
                    for detalle in detalles:
                        try:
                            cursor.execute('''
                                INSERT OR REPLACE INTO nota_venta_detalle 
                                (id, nota_venta_id, producto_id, codigo_producto,
                                 cantidad, precio_unitario, created_at, updated_at, version)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                detalle.get('id'), detalle.get('nota_venta_id'),
                                detalle.get('producto_id'), detalle.get('codigo_producto'),
                                float(detalle.get('cantidad', 0)),
                                float(detalle.get('precio_unitario', 0)),
                                detalle.get('created_at'), detalle.get('updated_at'),
                                int(detalle.get('version', 1))
                            ))
                        except Exception as e:
                            print(f"   ❌ Error detalle: {e}")
                    conn.commit()
                    print(f"   ✅ {len(detalles)} detalles guardados")
            
            conn.close()
            print(f"✅ [Sync] {len(ids_nuevos)} notas sincronizadas")
            # Notificar a la interfaz
            if len(ids_nuevos) > 0:
                pass  # No hay acción necesaria
            
        except Exception as e:
            print(f"❌ [Sync] Error: {e}")
            import traceback
            traceback.print_exc()
    
    def iniciar(self):
        """Inicia el sincronizador en segundo plano"""
        if self.running:
            print("⚠️ Sincronizador ya está corriendo")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("🔄 Sincronizador simple iniciado (cada 60s)")
    
    def detener(self):
        """Detiene el sincronizador"""
        self.running = False
        print("⏹️ Sincronizador detenido")
    
    def _loop(self):
        """Bucle principal del sincronizador"""
        while self.running:
            try:
                self.sincronizar_notas()
            except Exception as e:
                print(f"❌ [Sync] Error en bucle: {e}")
            
            # Esperar el intervalo
            for _ in range(self.intervalo):
                if not self.running:
                    break
                time.sleep(1)
    
    def sincronizar_ahora(self):
        """Ejecuta una sincronización inmediata"""
        self.sincronizar_notas()

# Instancia global
sincronizador = SincronizadorSimple(intervalo=60)

def iniciar_sincronizador():
    """Función para iniciar desde main.py"""
    sincronizador.iniciar()

def detener_sincronizador():
    """Función para detener desde main.py"""
    sincronizador.detener()

def sincronizar_ahora():
    """Función para sincronización manual"""
    sincronizador.sincronizar_ahora()
