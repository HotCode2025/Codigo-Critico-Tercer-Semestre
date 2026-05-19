"""
Código Crítico - Tercer Semestre Año 2026
Extractor de datos estructurados a partir de las filas crudas obtenidas del PDF.
Transforma las filas de texto en diccionarios con los campos esperados:
código, descripción, precio_costo, stock, fecha_vencimiento.
Permite configurar la posición de cada columna y aplicar mapeos.
"""

from typing import List, Dict, Any, Optional

class ExtractorDatos:
    """
    Toma una lista de filas (listas de celdas) y las convierte en una lista de
    diccionarios usando un mapeo de columnas.
    """

    def __init__(self,
                 codigo_col: int = 0,
                 descripcion_col: int = 1,
                 precio_costo_col: int = 2,
                 stock_col: int = 3,
                 fecha_venc_col: int = 4,
                 tiene_encabezado: bool = True,
                 fila_inicio_datos: int = 1):
        """
        Inicializa el extractor con la configuración de columnas.
        :param codigo_col: índice de la columna del código del producto (0‑based).
        :param descripcion_col: índice de la columna de la descripción.
        :param precio_costo_col: índice de la columna del precio de costo.
        :param stock_col: índice de la columna del stock inicial. Opcional.
        :param fecha_venc_col: índice de la columna de fecha de vencimiento (AAAA-MM-DD). Opcional.
        :param tiene_encabezado: Si la primera fila contiene los títulos de columna.
        :param fila_inicio_datos: Número de fila (0‑based) desde la que empiezan los datos
                                 (útil si hay filas de título adicionales).
        """
        self.codigo_col = codigo_col
        self.descripcion_col = descripcion_col
        self.precio_costo_col = precio_costo_col
        self.stock_col = stock_col
        self.fecha_venc_col = fecha_venc_col
        self.tiene_encabezado = tiene_encabezado
        self.fila_inicio = fila_inicio_datos

    def extraer(self, filas_brutas: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Procesa las filas extraídas del PDF y devuelve una lista de diccionarios
        con los campos: 'codigo', 'descripcion', 'precio_costo', 'stock' (opcional),
        'fecha_vencimiento' (opcional).
        Las filas que no tengan código se ignoran automáticamente.
        """
        # Determinar el índice de inicio
        inicio = self.fila_inicio
        # Si hay encabezado y la primera fila coincide, la saltamos
        if self.tiene_encabezado and len(filas_brutas) > 0:
            # Podemos detectar si la primera fila es un título común
            primera_celda = filas_brutas[0][self.codigo_col] if len(filas_brutas[0]) > self.codigo_col else ''
            if primera_celda.lower() in ('codigo', 'código', 'cod', 'producto', 'cód.'):
                inicio += 1

        if inicio >= len(filas_brutas):
            return []

        datos_extraidos = []
        for i in range(inicio, len(filas_brutas)):
            fila = filas_brutas[i]
            if not fila or len(fila) == 0:
                continue
            # Obtener código: debe ser obligatorio
            codigo = self._obtener_celda(fila, self.codigo_col).strip()
            if not codigo:
                continue   # sin código no es un producto válido

            descripcion = self._obtener_celda(fila, self.descripcion_col).strip()
            precio_costo_str = self._obtener_celda(fila, self.precio_costo_col).replace('$','').replace(',','').strip()
            stock_str = self._obtener_celda(fila, self.stock_col).replace('$','').replace(',','').strip() if self.stock_col is not None else None
            fecha_venc = self._obtener_celda(fila, self.fecha_venc_col).strip() if self.fecha_venc_col is not None else None

            # Convertir precio
            try:
                precio_costo = float(precio_costo_str) if precio_costo_str else 0.0
            except ValueError:
                precio_costo = 0.0

            # Convertir stock (opcional)
            stock = None
            if stock_str:
                try:
                    stock = float(stock_str)
                except ValueError:
                    stock = None

            # Validar fecha (formato esperado AAAA-MM-DD o DD/MM/AAAA)
            fecha_venc_normalizada = None
            if fecha_venc:
                fecha_venc_normalizada = self._normalizar_fecha(fecha_venc)

            item = {
                'codigo': codigo,
                'descripcion': descripcion,
                'precio_costo': precio_costo,
                'stock': stock,
                'fecha_vencimiento': fecha_venc_normalizada
            }
            datos_extraidos.append(item)

        return datos_extraidos

    def _obtener_celda(self, fila: List[str], indice: int) -> str:
        """Devuelve el texto de una celda dada su índice, o cadena vacía si no existe."""
        if 0 <= indice < len(fila):
            return str(fila[indice] or '')
        return ''

    def _normalizar_fecha(self, fecha_str: str) -> Optional[str]:
        """
        Convierte fechas en formatos comunes a ISO (AAAA-MM-DD).
        Ejemplos soportados: 'DD/MM/AAAA', 'DD-MM-AAAA', 'AAAA/MM/DD', 'AAAA-MM-DD'.
        Retorna None si no se puede parsear.
        """
        import re
        from datetime import datetime

        # Eliminar puntos, guiones y barras estandarizando
        partes = re.split(r'[/.-]', fecha_str.strip())
        if len(partes) != 3:
            return None
        try:
            # Intentar día/mes/año (formato español/latino)
            if len(partes[0]) <= 2 and len(partes[2]) >= 4:
                dia, mes, anio = int(partes[0]), int(partes[1]), int(partes[2])
            # Intentar año/mes/día
            elif len(partes[0]) >= 4:
                anio, mes, dia = int(partes[0]), int(partes[1]), int(partes[2])
            else:
                return None
            fecha = datetime(anio, mes, dia)
            return fecha.strftime('%Y-%m-%d')
        except (ValueError, IndexError):
            return None

    def configurar_desde_mapa(self, mapa_columnas: Dict[str, int]):
        """
        Permite reconfigurar las columnas usando un diccionario.
        Ejemplo: {'codigo': 0, 'descripcion': 1, 'precio_costo': 2, 'stock': 3, 'fecha_vencimiento': 4}
        """
        if 'codigo' in mapa_columnas:
            self.codigo_col = mapa_columnas['codigo']
        if 'descripcion' in mapa_columnas:
            self.descripcion_col = mapa_columnas['descripcion']
        if 'precio_costo' in mapa_columnas:
            self.precio_costo_col = mapa_columnas['precio_costo']
        if 'stock' in mapa_columnas:
            self.stock_col = mapa_columnas['stock']
        if 'fecha_vencimiento' in mapa_columnas:
            self.fecha_venc_col = mapa_columnas['fecha_vencimiento']