"""
Código Crítico - Tercer Semestre Año 2026
Plantilla para generar facturas individuales en PDF.
Se utiliza en conjunto con el generador de reportes para imprimir facturas sueltas.
"""

import sqlite3
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle,
                                Image, Spacer, HRFlowable)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from modelos.factura import Factura
from modelos.cliente import Cliente
from modelos.producto import Producto

class PlantillaFactura:
    def __init__(self, db: sqlite3.Connection, factura_id: int):
        self.db = db
        self.factura_id = factura_id
        self.factura_modelo = Factura(db)
        self.cliente_modelo = Cliente(db)
        self.producto_modelo = Producto(db)
        # Obtener datos de factura y cliente
        self.factura = self.factura_modelo.obtener_por_id(factura_id)
        if not self.factura:
            raise ValueError("Factura no encontrada.")
        self.cliente = self.cliente_modelo.obtener_por_id(self.factura['cliente_id'])
        self.detalles = self._obtener_detalles()

        # Parámetros de empresa
        cur = self.db.cursor()
        cur.execute("SELECT * FROM parametros WHERE id = 1")
        row = cur.fetchone()
        self.params = dict(row) if row else {}

    def _obtener_detalles(self):
        cur = self.db.cursor()
        cur.execute("""
            SELECT fd.*, p.descripcion, p.codigo
            FROM factura_detalle fd
            JOIN productos p ON fd.producto_id = p.id
            WHERE fd.factura_id = ?
        """, (self.factura_id,))
        return [dict(row) for row in cur.fetchall()]

    def generar_pdf(self, ruta_salida: str):
        doc = SimpleDocTemplate(ruta_salida, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=20*mm, bottomMargin=20*mm)
        elementos = []
        estilos = getSampleStyleSheet()

        # Logo y encabezado
        logo_path = self._obtener_logo()
        if logo_path:
            img = Image(logo_path, width=50*mm, height=18*mm)
            img.hAlign = 'LEFT'
            elementos.append(img)

        empresa_nombre = self.params.get('nombre_distribuidora', 'Distribuidora')
        elementos.append(Paragraph(empresa_nombre, estilos['Heading1']))
        if self.params.get('encabezado_factura'):
            elementos.append(Paragraph(self.params['encabezado_factura'], estilos['Normal']))
        elementos.append(Spacer(1, 5*mm))

        # Datos de la factura (a la derecha)
        datos_factura = f"""
        <b>FACTURA {self.factura['tipo_comprobante']}</b> Nº {self.factura['numero_factura']}<br/>
        Fecha: {self.factura['fecha']}<br/>
        Cliente: {self.cliente['razon_social']}<br/>
        CUIT: {self.cliente['cuit'] or 'N/A'}<br/>
        Cond. IVA: {self.cliente['condicion_iva']}
        """
        elementos.append(Paragraph(datos_factura, estilos['Normal']))
        elementos.append(Spacer(1, 5*mm))

        # Línea separadora
        elementos.append(HRFlowable(width="100%", thickness=1, color=colors.grey))

        # Tabla de productos
        encabezados = ["Código", "Descripción", "Cant.", "Precio Unit.", "Subtotal"]
        tabla_datos = [encabezados]
        for det in self.detalles:
            tabla_datos.append([
                det['codigo'],
                det['descripcion'],
                f"{det['cantidad']:.2f}",
                f"$ {det['precio_unitario']:,.2f}",
                f"$ {det['cantidad'] * det['precio_unitario']:,.2f}"
            ])
        tabla = Table(tabla_datos, colWidths=[30*mm, 70*mm, 20*mm, 30*mm, 30*mm])
        estilo_tabla = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ])
        tabla.setStyle(estilo_tabla)
        elementos.append(tabla)

        # Totales
        elementos.append(Spacer(1, 5*mm))
        totales = f"""
        <b>Subtotal:</b> $ {self.factura['subtotal']:,.2f}<br/>
        <b>IVA ({'21' if self.cliente['condicion_iva']=='RI' else '0'}%):</b> $ {self.factura['iva']:,.2f}<br/>
        <b>Tasa Municipal:</b> $ {self.factura['tasa_municipal']:,.2f}<br/>
        <b>TOTAL:</b> $ {self.factura['total']:,.2f}
        """
        elementos.append(Paragraph(totales, estilos['Normal']))

        doc.build(elementos)
        return ruta_salida

    def _obtener_logo(self):
        logo_blob = self.params.get('logo')
        if logo_blob:
            temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"logo_factura_{self.factura_id}.png")
            with open(temp_path, 'wb') as f:
                f.write(logo_blob)
            return temp_path
        return None