 🚚 SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA

**Código Crítico - Tercer Semestre Año 2026**

Sistema completo de gestión para distribuidoras.

## 📋 CARACTERÍSTICAS

- ✅ Gestión de Clientes, Productos y Preventistas
- ✅ Facturación con PDF y QR
- ✅ Cuenta Corriente y Cheques
- ✅ Notas de Venta
- ✅ Dashboard con gráficos
- ✅ Mapa de clientes
- ✅ Sincronización con Turso (OPCIONAL)
- ✅ Backups automáticos
- ✅ Todos los datos con UUID

---

## 🚀 INSTALACIÓN (3 PASOS)  Para LINUX -- EL SISTEMA ESTA OPTIMIZADO PARA LINUX

### Paso 1: Clonar y entrar

```bash
git clone https://github.com/tu-usuario/sistema-distribucion.git
cd sistema-distribucion
Paso 2: Instalar dependencias
bash
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
Paso 3: Ejecutar
bash
python main.py
Usuario: admin
Contraseña: admin

🔧 CONFIGURACIÓN DE TURSO (OPCIONAL)
El sistema usa SQLite local por defecto. Para usar Turso:

Crea una cuenta en Turso

Crea una base de datos

Copia el token y la URL

Crea el archivo turso-facturar.txt:

txt
eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODI1MTQyMTEsImlkIjoiMDE5ZjA2MjAtM2YwMS03NzgwLWI0ZDgtNDU3YWY3OWYyNzY1IiwicmlkIjoiOWU1YzkyZDktMmI3MC00MTJjLThkNmYtZjgzMzY5NjM4ODViIn0.H_PKJrBCAvNH5WPaCYUJOgHDVDPQHw7Y4qir1zFlx6MSih-vjUZnojZdp5AmMwAz9151gNCjX-rC3oGuj_ETAw

libsql://nube-clarionda.aws-us-east-1.turso.io
El sistema detectará automáticamente la conexión

📁 ESTRUCTURA DEL PROYECTO
text
sistema-distribucion/
├── assets/                 # Imágenes y recursos
├── controladores/          # Lógica de negocio
├── db/                     # Base de datos
├── modelos/                # Modelos de datos
├── utilidades/             # Utilidades
├── vistas/                 # Interfaces de usuario
├── backups/                # Backups (se crea automáticamente)
├── logs/                   # Logs (se crea automáticamente)
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
└── README.md              # Esta documentación
📊 MÓDULOS DEL SISTEMA
Módulo	Descripción
Dashboard	Métricas, gráficos y pedidos pendientes
Clientes	CRUD completo con geolocalización
Productos	Gestión con imágenes y stock
Preventistas	Gestión de vendedores
Facturación	Emisión con PDF y QR
Notas de Venta	Pedidos desde preventistas
Cheques	Gestión y consulta BCRA
Cuenta Corriente	Saldos y cobros
Rentabilidad	Ganancias y proyecciones
Mapa	Ubicación de clientes
🧪 DATOS DE PRUEBA
El sistema incluye:

1000 clientes de prueba

96 productos de ejemplo

7 preventistas configurados

19 categorías de productos

📝 LICENCIA
Código Crítico - Tercer Semestre 2026
Proyecto educativo para fines académicos.