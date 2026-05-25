"""
Código Crítico - Tercer Semestre Año 2026
Lector de archivos PDF de catálogos de proveedores.
Abre un documento PDF, extrae las tablas de todas las páginas y devuelve
los datos en bruto (lista de listas) para ser procesados por el extractor.
"""

import os
from typing import List, Optional

# Instale pdfplumber: pip install pdfplumber
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    raise ImportError(
        "Se requiere pdfplumber para leer PDF. Instálelo con 'pip install pdfplumber'"
    )

class LectorPDF:
    """
    Clase responsable de leer un archivo PDF y extraer tablas.
    Soporta configuraciones básicas como página inicial/final y ajustes de área.
    """

    def __init__(self, ruta_archivo: str):
        """
        Inicializa el lector con la ruta del PDF.
        :param ruta_archivo: Ruta absoluta o relativa al archivo PDF.
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")
        self.ruta = ruta_archivo
        self.paginas = []  # lista de páginas parseadas (pdfplumber page objects)

    def abrir_pdf(self):
        """Abre el documento PDF y guarda las referencias a las páginas."""
        self.pdf = pdfplumber.open(self.ruta)
        self.paginas = self.pdf.pages

    def cerrar_pdf(self):
        """Cierra el documento para liberar recursos."""
        if hasattr(self, 'pdf') and self.pdf:
            self.pdf.close()

    def extraer_tablas(self,
                       pagina_inicio: int = 0,
                       pagina_fin: Optional[int] = None,
                       configuracion: dict = None) -> List[List[str]]:
        """
        Extrae todas las tablas encontradas en el rango de páginas.
        :param pagina_inicio: índice de la primera página (0-based). Por defecto 0.
        :param pagina_fin: índice de la última página (exclusivo). None = hasta el final.
        :param configuracion: diccionario con ajustes para pdfplumber (ej: {
                                "vertical_strategy": "lines",
                                "horizontal_strategy": "lines"})
        :return: Lista de filas, cada fila es una lista de celdas (texto).
        """
        if not self.paginas:
            self.abrir_pdf()

        if pagina_fin is None:
            pagina_fin = len(self.paginas)

        tablas_totales = []
        config = configuracion if configuracion else {}

        for i in range(pagina_inicio, min(pagina_fin, len(self.paginas))):
            pagina = self.paginas[i]
            # Extraer todas las tablas de la página
            tablas = pagina.extract_tables(config)
            for tabla in tablas:
                if tabla:
                    # Limpiar celdas con None y espacios extra
                    tabla_limpia = []
                    for fila in tabla:
                        fila_limpia = [celda.strip() if celda else '' for celda in fila]
                        # Ignorar filas completamente vacías
                        if any(fila_limpia):
                            tabla_limpia.append(fila_limpia)
                    if tabla_limpia:
                        tablas_totales.extend(tabla_limpia)
        return tablas_totales

    def extraer_texto_completo(self) -> str:
        """Extrae todo el texto del PDF (útil para catálogos no tabulares)."""
        if not self.paginas:
            self.abrir_pdf()
        texto = ""
        for pagina in self.paginas:
            texto += pagina.extract_text() or ""
        return texto