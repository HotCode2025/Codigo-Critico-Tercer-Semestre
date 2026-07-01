"""
Controlador de Notas de Venta - Código Crítico 2026
"""

import sqlite3
from datetime import datetime
import uuid

class ControladorNotasVenta:
    """Controlador para gestionar notas de venta"""
    
    def __init__(self):
        self.db_path = 'distribuidora.db'
    
    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def obtener_todas(self):
        """Obtiene todas las notas de venta"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, numero_nota, fecha, cliente_id, total, estado 
                FROM notas_venta 
                ORDER BY fecha DESC
            ''')
            
            resultados = []
            for row in cursor.fetchall():
                # Obtener nombre del cliente
                cursor.execute('SELECT razon_social FROM clientes WHERE id = ?', (row[3],))
                cliente = cursor.fetchone()
                cliente_nombre = cliente[0] if cliente else 'N/A'
                
                resultados.append({
                    'id': row[0],
                    'numero_nota': row[1],
                    'fecha': row[2],
                    'cliente_id': row[3],
                    'cliente_nombre': cliente_nombre,
                    'total': row[4],
                    'estado': row[5]
                })
            
            return resultados
            
        except sqlite3.Error as e:
            print(f"Error al obtener notas: {e}")
            return []
        finally:
            conn.close()
    
    def obtener_por_id(self, nota_id):
        """Obtiene una nota por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, preventista_id, cliente_id, fecha, numero_nota, 
                       total, observaciones, estado, procesado_central,
                       created_at, updated_at, version
                FROM notas_venta 
                WHERE id = ?
            ''', (nota_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'preventista_id': row[1],
                    'cliente_id': row[2],
                    'fecha': row[3],
                    'numero_nota': row[4],
                    'total': row[5],
                    'observaciones': row[6],
                    'estado': row[7],
                    'procesado_central': row[8],
                    'created_at': row[9],
                    'updated_at': row[10],
                    'version': row[11]
                }
            return None
            
        except sqlite3.Error as e:
            print(f"Error al obtener nota: {e}")
            return None
        finally:
            conn.close()
    
    def obtener_detalles(self, nota_id):
        """Obtiene los detalles de una nota"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, nota_venta_id, producto_id, codigo_producto,
                       cantidad, precio_unitario, created_at, updated_at, version
                FROM nota_venta_detalle 
                WHERE nota_venta_id = ?
            ''', (nota_id,))
            
            resultados = []
            for row in cursor.fetchall():
                resultados.append({
                    'id': row[0],
                    'nota_venta_id': row[1],
                    'producto_id': row[2],
                    'codigo_producto': row[3],
                    'cantidad': row[4],
                    'precio_unitario': row[5],
                    'created_at': row[6],
                    'updated_at': row[7],
                    'version': row[8]
                })
            
            return resultados
            
        except sqlite3.Error as e:
            print(f"Error al obtener detalles: {e}")
            return []
        finally:
            conn.close()
    
    def cambiar_estado(self, nota_id, nuevo_estado):
        """Cambia el estado de una nota"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE notas_venta 
                SET estado = ?, updated_at = ?
                WHERE id = ?
            ''', (nuevo_estado, datetime.now().isoformat(), nota_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error al cambiar estado: {e}")
            return False
        finally:
            conn.close()
    
    def eliminar(self, nota_id):
        """Elimina una nota de venta"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Primero eliminar detalles
            cursor.execute('DELETE FROM nota_venta_detalle WHERE nota_venta_id = ?', (nota_id,))
            # Luego eliminar la nota
            cursor.execute('DELETE FROM notas_venta WHERE id = ?', (nota_id,))
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error al eliminar nota: {e}")
            return False
        finally:
            conn.close()

    def obtener_por_preventista(self, preventista_id):
        """Obtiene notas de venta de un preventista específico"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, numero_nota, fecha, cliente_id, total, estado 
                FROM notas_venta 
                WHERE preventista_id = ?
                ORDER BY fecha DESC
            ''', (preventista_id,))
            
            resultados = []
            for row in cursor.fetchall():
                # Obtener nombre del cliente
                cursor.execute('SELECT razon_social FROM clientes WHERE id = ?', (row[3],))
                cliente = cursor.fetchone()
                cliente_nombre = cliente[0] if cliente else 'N/A'
                
                resultados.append({
                    'id': row[0],
                    'numero_nota': row[1],
                    'fecha': row[2],
                    'cliente_id': row[3],
                    'cliente_nombre': cliente_nombre,
                    'total': row[4],
                    'estado': row[5]
                })
            
            return resultados
            
        except sqlite3.Error as e:
            print(f"Error al obtener notas por preventista: {e}")
            return []
        finally:
            conn.close()
