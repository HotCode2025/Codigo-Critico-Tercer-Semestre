"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Rentabilidad - Cálculos de ganancias, gastos y proyecciones.
"""

import sqlite3
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from dateutil.relativedelta import relativedelta


class ControladorRentabilidad:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row
        self._crear_tablas()
    
    def _crear_tablas(self):
        """Crea las tablas de rentabilidad si no existen."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                categoria TEXT NOT NULL,
                descripcion TEXT,
                importe REAL NOT NULL,
                tipo TEXT DEFAULT 'OPERATIVO',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS otros_ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                concepto TEXT NOT NULL,
                importe REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS proyecciones_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                porcentaje_crecimiento_mensual REAL DEFAULT 5.0,
                meses_proyeccion INTEGER DEFAULT 6
            )
        """)
        self.db.execute("""
            INSERT OR IGNORE INTO proyecciones_config (id, porcentaje_crecimiento_mensual, meses_proyeccion)
            VALUES (1, 5.0, 6)
        """)
        self.db.commit()
    
    # =================== GANANCIAS ===================
    
    def obtener_ganancia_por_periodo(self, fecha_desde: str, fecha_hasta: str) -> Dict[str, Any]:
        """
        Calcula la ganancia bruta y neta del período.
        Ganancia bruta = Suma de (precio_venta - precio_costo) * cantidad
        """
        cur = self.db.cursor()
        
        # Ganancia bruta de facturas
        cur.execute("""
            SELECT SUM((fd.precio_unitario - p.precio_costo) * fd.cantidad) as ganancia_bruta,
                   SUM(fd.cantidad * fd.precio_unitario) as ventas_totales
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            JOIN facturas f ON fd.factura_id = f.id
            WHERE f.fecha BETWEEN ? AND ? AND f.estado = 'EMITIDA'
        """, (fecha_desde, fecha_hasta))
        resultado = cur.fetchone()
        
        ganancia_bruta = resultado['ganancia_bruta'] or 0.0
        ventas_totales = resultado['ventas_totales'] or 0.0
        
        # Gastos del período
        gastos = self.obtener_gastos_por_periodo(fecha_desde, fecha_hasta)
        total_gastos = sum(g['importe'] for g in gastos)
        
        # Otros ingresos
        otros_ingresos = self.obtener_otros_ingresos_por_periodo(fecha_desde, fecha_hasta)
        total_otros_ingresos = sum(i['importe'] for i in otros_ingresos)
        
        ganancia_neta = ganancia_bruta - total_gastos + total_otros_ingresos
        
        return {
            'ventas_totales': ventas_totales,
            'ganancia_bruta': ganancia_bruta,
            'total_gastos': total_gastos,
            'otros_ingresos': total_otros_ingresos,
            'ganancia_neta': ganancia_neta,
            'margen_neto': (ganancia_neta / ventas_totales * 100) if ventas_totales > 0 else 0
        }
    
    def obtener_ganancia_mensual(self, anio: int = None) -> List[Dict[str, Any]]:
        """Obtiene ganancia mensual del año."""
        if anio is None:
            anio = date.today().year
        
        resultados = []
        for mes in range(1, 13):
            fecha_desde = f"{anio}-{mes:02d}-01"
            if mes == 12:
                fecha_hasta = f"{anio}-12-31"
            else:
                fecha_hasta = f"{anio}-{mes+1:02d}-01"
            
            data = self.obtener_ganancia_por_periodo(fecha_desde, fecha_hasta)
            resultados.append({
                'mes': mes,
                'nombre_mes': self._nombre_mes(mes),
                'ventas': data['ventas_totales'],
                'ganancia_bruta': data['ganancia_bruta'],
                'gastos': data['total_gastos'],
                'ganancia_neta': data['ganancia_neta']
            })
        
        return resultados
    
    def _nombre_mes(self, mes: int) -> str:
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return meses[mes - 1]
    
    # =================== GASTOS ===================
    
    def agregar_gasto(self, fecha: str, categoria: str, importe: float, 
                      descripcion: str = None, tipo: str = 'OPERATIVO') -> int:
        """Agrega un nuevo gasto."""
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO gastos (fecha, categoria, descripcion, importe, tipo)
            VALUES (?, ?, ?, ?, ?)
        """, (fecha, categoria, descripcion, importe, tipo))
        self.db.commit()
        return cur.lastrowid
    
    def obtener_gastos_por_periodo(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        """Obtiene todos los gastos de un período."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM gastos 
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """, (fecha_desde, fecha_hasta))
        return [dict(row) for row in cur.fetchall()]
    
    def obtener_gastos_por_categoria(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        """Obtiene gastos agrupados por categoría."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT categoria, SUM(importe) as total, COUNT(*) as cantidad
            FROM gastos 
            WHERE fecha BETWEEN ? AND ?
            GROUP BY categoria
            ORDER BY total DESC
        """, (fecha_desde, fecha_hasta))
        return [dict(row) for row in cur.fetchall()]
    
    def eliminar_gasto(self, gasto_id: int) -> bool:
        """Elimina un gasto."""
        cur = self.db.cursor()
        cur.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
        self.db.commit()
        return cur.rowcount > 0
    
    # =================== OTROS INGRESOS ===================
    
    def agregar_ingreso(self, fecha: str, concepto: str, importe: float) -> int:
        """Agrega otro ingreso (no proveniente de facturas)."""
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO otros_ingresos (fecha, concepto, importe)
            VALUES (?, ?, ?)
        """, (fecha, concepto, importe))
        self.db.commit()
        return cur.lastrowid
    
    def obtener_otros_ingresos_por_periodo(self, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        """Obtiene otros ingresos del período."""
        cur = self.db.cursor()
        cur.execute("""
            SELECT * FROM otros_ingresos 
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """, (fecha_desde, fecha_hasta))
        return [dict(row) for row in cur.fetchall()]
    
    def eliminar_ingreso(self, ingreso_id: int) -> bool:
        """Elimina otro ingreso."""
        cur = self.db.cursor()
        cur.execute("DELETE FROM otros_ingresos WHERE id = ?", (ingreso_id,))
        self.db.commit()
        return cur.rowcount > 0
    
    # =================== PROYECCIONES ===================
    
    def obtener_config_proyecciones(self) -> Dict[str, Any]:
        """Obtiene la configuración de proyecciones."""
        cur = self.db.cursor()
        cur.execute("SELECT * FROM proyecciones_config WHERE id = 1")
        row = cur.fetchone()
        return dict(row) if row else {'porcentaje_crecimiento_mensual': 5.0, 'meses_proyeccion': 6}
    
    def actualizar_config_proyecciones(self, porcentaje: float, meses: int) -> bool:
        """Actualiza la configuración de proyecciones."""
        cur = self.db.cursor()
        cur.execute("""
            UPDATE proyecciones_config 
            SET porcentaje_crecimiento_mensual = ?, meses_proyeccion = ?
            WHERE id = 1
        """, (porcentaje, meses))
        self.db.commit()
        return cur.rowcount > 0
    
    def obtener_proyeccion(self) -> Dict[str, Any]:
        """
        Calcula proyección de ganancias para los próximos meses.
        Basado en el promedio de los últimos 3 meses + crecimiento configurado.
        """
        config = self.obtener_config_proyecciones()
        meses_proyeccion = config['meses_proyeccion']
        crecimiento = config['porcentaje_crecimiento_mensual'] / 100.0
        
        # Obtener ganancias de los últimos 3 meses
        hoy = date.today()
        datos_historicos = []
        
        for i in range(1, 4):
            fecha_inicio = (hoy - relativedelta(months=i)).replace(day=1)
            fecha_fin = fecha_inicio + relativedelta(months=1) - timedelta(days=1)
            resultado = self.obtener_ganancia_por_periodo(
                fecha_inicio.isoformat(), 
                fecha_fin.isoformat()
            )
            datos_historicos.append(resultado['ganancia_neta'])
        
        # Promedio de los últimos 3 meses
        promedio = sum(datos_historicos) / len(datos_historicos) if datos_historicos else 0
        
        # Proyección con crecimiento
        proyecciones = []
        fecha_actual = hoy
        valor_actual = promedio
        
        for i in range(1, meses_proyeccion + 1):
            fecha_actual = fecha_actual + relativedelta(months=1)
            valor_actual = valor_actual * (1 + crecimiento)
            proyecciones.append({
                'mes': fecha_actual.strftime('%B %Y'),
                'proyeccion': valor_actual,
                'crecimiento_aplicado': crecimiento * 100
            })
        
        return {
            'promedio_historico': promedio,
            'proyecciones': proyecciones,
            'config': config
        }