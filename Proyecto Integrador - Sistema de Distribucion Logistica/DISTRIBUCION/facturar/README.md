# 📦 Sistema de Distribución y Logística

Sistema completo de gestión para distribuidora de productos lácteos con sincronización en tiempo real entre Central (escritorio) y App Catálogo (móvil/tablet) a través de Turso.

---

## 🚀 **Características Principales**

- ✅ **Gestión de Clientes** - ABM completo con geolocalización
- ✅ **Catálogo de Productos** - Con imágenes, categorías y stock
- ✅ **Facturación Fiscal** - Emisión de facturas tipo A, B, C
- ✅ **Notas de Venta** - Creación y facturación desde App móvil
- ✅ **Cuenta Corriente** - Control de saldos, cobros y cheques
- ✅ **Stock y Lotes** - Control por lote con fechas de vencimiento
- ✅ **Sincronización con Turso** - En tiempo real (cada 3 segundos)
- ✅ **Backups Automáticos** - Programados diariamente
- ✅ **Reportes** - Ventas, stock, rentabilidad, etc.

---

## 📋 **Requisitos del Sistema**

| Requisito | Versión |
|-----------|---------|
| Python | 3.12+ |
| Pip | Última versión |
| Sistema Operativo | Linux (X11), Windows, macOS |

---

## 🔧 **Instalación**



### 1️⃣ **Clonar el repositorio**

```bash


2️⃣ Crear entorno virtual

python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

3️⃣ Instalar dependencias

pip install -r requirements.txt

4️⃣ Configurar Turso
// El sistema ya esta configurado para su uso! La base de Datos la Tenemos en Japón!
[TU_TOKEN_AQUI]

libsql://[NOMBRE_BD].aws-ap-northeast-1.turso.io //  El sistema ya cuenta con Token

5️⃣ Inicializar base de datos
  
  La creacion de la bases de Datos, en la nube se realizo directamente de la página de Turso
  https://turso.tech/

6️⃣ Crear tablas en Turso
   Se las crearon de Forma Manual

7️⃣ Ejecutar el sistema

python main.py

📁 Estructura del Proyecto

facturar/
├── controladores/          # Lógica de negocio
│   ├── controlador_clientes.py
│   ├── controlador_productos.py
│   ├── controlador_ventas.py
│   └── ...
├── modelos/                # Modelos de datos
│   ├── cliente.py
│   ├── producto.py
│   ├── nota_venta.py
│   └── ...
├── vistas/                 # Interfaz gráfica (PyQt6)
│   ├── vista_clientes.py
│   ├── vista_productos_unificada.py
│   ├── vista_facturacion.py
│   └── ...
├── utilidades/             # Utilidades
│   ├── central_sync.py     # Sincronización con Turso
│   ├── backup_profesional.py
│   └── geocodificar.py
├── db/                     # Base de datos
│   ├── db_manager.py
│   └── script_creacion.sql
├── imagenes_productos/     # Imágenes del catálogo
├── logs/                   # Logs de sincronización
├── backups/                # Backups automáticos
├── main.py                 # Punto de entrada
├── config.py               # Configuración
├── requirements.txt        # Dependencias
└── README.md               # Este archivo


🔄 Flujo de Sincronización

┌─────────────────────────────────────────────────────────────────┐
│                         TURSO (Nube)                            │
│                                                                 │
│  📤 Central → Turso:                📥 Turso → Central:         │
│  • Clientes                        • Notas de venta             │
│  • Productos (catálogo)            • Clientes nuevos            │
│  • Stock (lotes)                   • Visitas                    │
│  • Precios                         • Ubicaciones GPS            │
│                                                                 │
│  📤 App → Turso:                    📥 Turso → App:             │
│  • Notas de venta                  • Clientes                   │
│  • Clientes nuevos                 • Productos (catálogo)       │
│  • Visitas                         • Stock                      │
│  • Ubicaciones GPS                 • Precios                    │
└─────────────────────────────────────────────────────────────────┘

Intervalo de sincronización: 3 segundos

🔑 Usuarios por Defecto

Usuario	Contraseña	Rol
admin	admin	Administrador
preventista1	preventista1	Preventista
preventista2	preventista2	Preventista
preventista3	preventista3	Preventista
preventista4	preventista4	Preventista
preventista5	preventista5	Preventista
preventista6	preventista6	Preventista
preventista7	preventista7	Preventista

📊 Módulos Principales
🏢 Clientes

    Alta, baja y modificación

    Geolocalización automática

    Asignación a preventistas

    Historial de cuenta corriente

📦 Productos

    Catálogo con imágenes

    Categorías

    Precios y costos

    Stock por lote

    Fechas de vencimiento

🛒 Notas de Venta

    Creación desde App

    Recepción en Central

    Facturación automática

    Control de stock

💰 Facturación

    Facturas tipo A, B, C

    Cálculo de IVA

    Tasa municipal

    Impresión de PDF

    Anulación

💳 Cuenta Corriente

    Movimientos

    Cobros

    Cheques

    Límite de crédito

    Deudores

📊 Reportes

    Productos más vendidos

    Ventas por preventista

    Stock crítico

    Rentabilidad

    Proyecciones




📄 Licencia

Código Crítico - Tercer Semestre 2026
👨‍💻 Autores

    Desarrollado por el equipo de Código Crítico - Tercer Semestre - Año 2026.-


 Librería Usadas

    PyQt6 por la interfaz gráfica

    Turso por la base de datos en la nube

    OpenStreetMap por la geolocalización

📞 Soporte

Para soporte técnico, contactar al equipo de desarrollo.

Última actualización: 24 Junio 2026

