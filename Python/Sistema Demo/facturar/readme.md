# 📦 Sistema de Gestión Integral para Distribuidora
> **Código Crítico** • Tercer Semestre (Año 2026)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6%20(Qt)-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/Licencia-Libre%20/%20Acad%C3%A9mica-blue?style=for-the-badge)

Solución de escritorio centralizada y modular desarrollada en Python para la administración logística, comercial y fiscal de distribuidoras con flotas de preventistas (soporte nativo para 25 usuarios). Incluye control estricto de stock por lotes, alertas tempranas de vencimiento, cuenta corriente automatizada y un potente lector de catálogos PDF para actualización de precios.

---

## 🚀 Características Principales

* **👥 Clientes y Fuerza de Venta:** ABM completo de clientes, asignación a los 25 preventistas, configuración de condiciones frente al IVA y asignación de límites de crédito personalizados.
* **📦 Stock Inteligente y Crítico:** Gestión de inventario mediante trazabilidad por lotes. Alertas automatizadas de stock mínimo y de productos próximos a vencer con **14 días de anticipación** para facilitar la gestión de ofertas.
* **📑 Circuito Comercial Completo:** Emisión de Notas de Venta (pedidos de preventistas), conversión a Facturación Fiscal (A, B y C) con cálculo automático de IVA y tasas municipales.
* **💳 Finanzas y Cuenta Corriente:** Monitoreo de saldos en tiempo real, historial completo de movimientos (débitos/créditos), registro analítico de cobros/entregas y bloqueos por límite superado.
* **📊 Analítica y Reportes Avanzados:** Módulo estadístico de ganancias (costo vs. venta), productos más vendidos por mes/cliente, listado de mercadería entregada sin cobrar y rendimiento comercial por preventista. Exportación profesional a **PDF (ReportLab)** y **Excel (openpyxl)**.
* **📄 Lector Inteligente de Catálogos (PDF):** Extracción automatizada de datos desde archivos de proveedores mediante `pdfplumber`. Permite la actualización masiva de precios aplicando márgenes de ganancia porcentuales automáticos o edición manual.
* **⚙️ Panel de Parámetros Generales:** Configuración global del sistema: nombre de la empresa, datos de contacto (Teléfono, WhatsApp, Email), divisas y personalización de encabezados/pie de página para comprobantes y reportes.

---

## 📂 Arquitectura del Proyecto (Estructura Modular)

El software implementa una arquitectura desacoplada basada en el patrón de diseño Mediador/Controlador para asegurar la escalabilidad hacia futuras plataformas móviles (Tablets):

```text
distribuidora_app/
├── ⚙️ config/                 # Constantes y parámetros globales del sistema
├── 🗄️ db/                     # Gestor de base de datos y script SQL de inicialización
├── 📦 modelos/                # Clases de negocio (Cliente, Producto, Factura, etc.)
├── 🎨 vistas/                 # Interfaces gráficas profesionales agrupadas por módulo
├── 🎮 controladores/          # Lógica de interacción entre modelos y vistas
├── 📊 reportes/               # Motor de renderizado de reportes y plantillas PDF
├── 📄 pdf/                    # Motores de parsing y extracción de texto de catálogos
├── 🛠️ utilidades/             # Funciones transversales (fechas, cálculos, alertas)
├── 🖼️ assets/                 # Recursos estáticos (Logotipos, iconos de la app)
├── 🚀 main.py                 # Punto de entrada principal de la aplicación
├── 📄 requirements.txt        # Manifiesto de dependencias del proyecto
└── 📝 README.md               # Documentación del sistema

🛠️ Requisitos del Entorno

Asegúrese de contar con los siguientes elementos instalados en su entorno local:

    Python 3.8 o superior

    pip (Gestor de paquetes de Python)
    Dependencias Core del EcosistemaLibreríaPropósito / Función


PySide6	Framework para la interfaz gráfica profesional de alta fidelidad (Qt).
ReportLab	Generación dinámica y diseño de documentos y facturas en PDF.
pdfplumber	Procesamiento y extracción precisa de tablas en catálogos del proveedor.
openpyxl	Generación nativa de reportes y auditorías en formato de hojas de cálculo Excel.
Pillow	Procesamiento y escalado optimizado del logotipo de la distribuidora.

⚙️ Instalación y Configuración

Siga estos pasos para desplegar el sistema en su entorno de desarrollo local:

    Clonar o descargar el repositorio en su máquina local.

    Instalar las dependencias requeridas ejecutando en la terminal:

    pip install -r requirements.txt

    Preparar la Base de Datos:
El sistema está diseñado para inicializar y migrar la base de datos SQLite automáticamente en su primer inicio. Si prefiere realizar el aprovisionamiento de manera manual, dispone de dos opciones:

    Ejecutar el gestor desde la terminal:

    python db/db_manager.py

O bien, abrir y ejecutar el archivo db/script_creacion.sql desde su entorno gráfico de preferencia (DBeaver, Beekeeper Studio o DB Browser for SQLite).

Identidad de la Distribuidora (Logo):
El sistema requiere un logotipo corporativo en formato PNG ubicado exactamente en assets/logo.png. Si aún no cuenta con uno, puede generar una plantilla de prueba ejecutando:

python assets/generar_logo.py

    💡 Nota: Una vez dentro del sistema, podrá actualizar o reemplazar el logo de manera interactiva desde el módulo Parámetros.

    💻 Ejecución del Sistema

Para lanzar el entorno centralizado de la distribuidora, ejecute el siguiente comando en la raíz del proyecto:

python main.py

Al iniciar, se desplegará la ventana principal optimizada con una barra de navegación superior desde la cual tendrá acceso inmediato y fluido a todos los módulos operativos y analíticos del sistema.

📝 Licencia y Autoría

    Desarrollado por: Código Crítico (Tercer Semestre - Año 2026).

    Licencia: Software de uso libre y académico. Prohibida su comercialización sin autorización expresa del autor.