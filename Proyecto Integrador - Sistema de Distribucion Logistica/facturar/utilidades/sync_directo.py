"""
Sincronizador directo - Descarga notas Y DETALLES desde Turso a local
SIEMPRE descarga los detalles, incluso si las notas ya existen
"""

import sqlite3
import time
import threading
from datetime import datetime
from utilidades.turso_client import get_turso_client

class SyncDirecto:
    def __init__(self, intervalo=30):
        self.intervalo = intervalo
        self.running = False
        self.thread = None
        self.db_path = 'distribuidora.db'
        self.client = get_turso_client()
        self.ultima_sync = None
        self.notas_sincronizadas = 0
        self.detalles_sincronizados = 0
        print("🔄 SyncDirecto inicializado - Sincroniza NOTAS y DETALLES siempre")
    
    def sincronizar(self):
        """Sincroniza notas Y DETALLES desde Turso a local (SIEMPRE)"""
        if not self.client.is_connected():
            print("⚠️ [SyncDirecto] Sin conexión a Turso")
            return
        
        try:
            print(f"🔄 [SyncDirecto] Verificando... {datetime.now().strftime('%H:%M:%S')}")
            
            # ============================================================
            # 1. SINCRONIZAR NOTAS (PADRE)
            # ============================================================
            notas_turso = self.client.get_all(
                "SELECT * FROM notas_venta ORDER BY created_at DESC"
            )
            
            if notas_turso:
                print(f"📊 [SyncDirecto] {len(notas_turso)} notas en Turso")
                
                conn = sqlite3.connect(self.db_path, timeout=10)
                cursor = conn.cursor()
                
                # Obtener IDs de notas locales
                cursor.execute('SELECT id FROM notas_venta')
                ids_local = [row[0] for row in cursor.fetchall()]
                
                # Notas nuevas
                notas_nuevas = [n for n in notas_turso if n['id'] not in ids_local]
                
                if notas_nuevas:
                    print(f"📥 [SyncDirecto] {len(notas_nuevas)} notas nuevas")
                    
                    for nota in notas_nuevas:
                        print(f"   📄 {nota['numero_nota']} - ${nota['total']} - {nota['estado']}")
                        
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
                        self.notas_sincronizadas += 1
                    
                    conn.commit()
                    print(f"✅ [SyncDirecto] {len(notas_nuevas)} notas sincronizadas")
                else:
                    print("ℹ️ [SyncDirecto] No hay notas nuevas")
                
                # ============================================================
                # 2. SINCRONIZAR DETALLES (HIJO) - SIEMPRE, PARA TODAS LAS NOTAS
                # ============================================================
                print(f"🔄 [SyncDirecto] Sincronizando detalles de TODAS las notas...")
                
                detalles_turso = self.client.get_all(
                    "SELECT * FROM nota_venta_detalle ORDER BY created_at DESC"
                )
                
                if detalles_turso:
                    print(f"📊 [SyncDirecto] {len(detalles_turso)} detalles en Turso")
                    
                    # Obtener IDs de detalles locales
                    cursor.execute('SELECT id FROM nota_venta_detalle')
                    ids_local_detalles = [row[0] for row in cursor.fetchall()]
                    
                    # Detalles nuevos
                    detalles_nuevos = [d for d in detalles_turso if d['id'] not in ids_local_detalles]
                    
                    if detalles_nuevos:
                        print(f"📥 [SyncDirecto] {len(detalles_nuevos)} detalles nuevos")
                        
                        for detalle in detalles_nuevos:
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
                                self.detalles_sincronizados += 1
                            except Exception as e:
                                print(f"      ❌ Error detalle: {e}")
                        
                        conn.commit()
                        print(f"✅ [SyncDirecto] {len(detalles_nuevos)} detalles sincronizados")
                    else:
                        print("ℹ️ [SyncDirecto] No hay detalles nuevos")
                    
                    # MOSTRAR RESUMEN POR NOTA
                    print("\n📋 RESUMEN DE DETALLES POR NOTA:")
                    for nota in notas_turso:
                        cursor.execute('SELECT COUNT(*) FROM nota_venta_detalle WHERE nota_venta_id = ?', (nota['id'],))
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"   ✅ {nota['numero_nota']}: {count} detalles")
                        else:
                            print(f"   ❌ {nota['numero_nota']}: 0 detalles")
                else:
                    print("ℹ️ [SyncDirecto] No hay detalles en Turso")
                
                conn.close()
            else:
                print("ℹ️ [SyncDirecto] No hay notas en Turso")
                return
            
            self.ultima_sync = datetime.now()
            print(f"📊 [SyncDirecto] Totales: {self.notas_sincronizadas} notas, {self.detalles_sincronizados} detalles")
            
        except Exception as e:
            print(f"❌ [SyncDirecto] Error: {e}")
            import traceback
            traceback.print_exc()
    
    def iniciar(self):
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"🔄 SyncDirecto iniciado (cada {self.intervalo}s)")
    
    def detener(self):
        self.running = False
        print("⏹️ SyncDirecto detenido")
    
    def _loop(self):
        while self.running:
            self.sincronizar()
            for _ in range(self.intervalo):
                if not self.running:
                    break
                time.sleep(1)
    
    def sincronizar_ahora(self):
        self.sincronizar()

# ============================================================
# FUNCIONES DE COMPATIBILIDAD
# ============================================================

def get_turso_config():
    import os
    url = None
    token = None
    
    posibles_rutas = [
        "turso-facturar.txt",
        os.path.join(os.getcwd(), "turso-facturar.txt"),
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('libsql://') or line.startswith('https://'):
                            url = line.replace('libsql://', 'https://')
                        elif line and not line.startswith('#') and line.startswith('eyJ'):
                            token = line
                
                if url and token:
                    break
            except:
                pass
    
    if not url:
        url = "https://nube-clarionda.aws-us-east-1.turso.io"
    
    if not url.endswith('/v2/pipeline'):
        url = url.rstrip('/') + '/v2/pipeline'
    
    return url, token

def verificar_conexion_turso_directo():
    import requests
    url, token = get_turso_config()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url + '/query', json={'query': 'SELECT 1'}, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def sincronizar_tabla_directo(db_path, tabla, limite=None):
    return {'tabla': tabla, 'total': 0, 'enviados': 0, 'errores': 0}

def sincronizar_todas_tablas(db_path):
    return {}

def sincronizar_ahora_directo(db_connection=None):
    sync = SyncDirecto()
    sync.sincronizar()
    return {'status': 'ok'}

# Instancia global
sync = SyncDirecto(intervalo=30)

def iniciar():
    sync.iniciar()

def detener():
    sync.detener()

def sincronizar_ahora():
    sync.sincronizar_ahora()
