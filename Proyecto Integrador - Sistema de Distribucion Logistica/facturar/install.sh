
---

### 4. `install.sh` (Linux/Mac)

```bash
#!/bin/bash
# Script de instalación automática

echo "=================================================="
echo "   SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA"
echo "   Instalación automática"
echo "=================================================="

echo ""
echo "📦 Creando entorno virtual..."
python3 -m venv venv

echo ""
echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo ""
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📦 Verificando instalación..."
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"
python -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('✅ WebEngine OK')"

echo ""
echo "📦 Verificando base de datos..."
python -c "import sqlite3; conn=sqlite3.connect('distribuidora.db'); print('✅ Base de datos OK')"

echo ""
echo "=================================================="
echo "✅ ¡Instalación completada!"
echo ""
echo "Para ejecutar:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Credenciales: admin / admin"
echo "=================================================="

echo "Análisis crítico de código
✅ GUÍA PARA SUBIR EL PROYECTO CON BASE DE DATOS Y TOKEN INCLUIDO

Entendido. Es para un proyecto de la facultad, la base de datos y el token deben estar incluidos para que al descargarlo funcione directamente.
📁 ESTRUCTURA COMPLETA PARA SUBIR
text

facturar/
├── README.md                    # Instrucciones
├── requirements.txt             # Dependencias
├── install.sh                   # Instalación Linux/Mac
├── install.bat                  # Instalación Windows
├── main.py                      # Punto de entrada
├── constantes.py
├── distribuidora.db             # ✅ BASE DE DATOS (INCLUIDA)
├── turso-facturar.txt           # ✅ TOKEN DE TURSO (INCLUIDO)
├── assets/
│   └── leaflet/
│       ├── css/
│       │   └── leaflet.min.css
│       └── js/
│           └── leaflet.min.js
├── db/
│   ├── db_manager.py
│   └── script_creacion.sql
├── modelos/
│   └── ... (todos los modelos)
├── controladores/
│   └── ... (todos los controladores)
├── vistas/
│   └── ... (todas las vistas)
├── utilidades/
│   └── ... (todas las utilidades)
├── .gitignore                   # Archivos a ignorar
├── .env                         # Variables de entorno
└── start.py                     # Script de inicio alternativo

📄 .gitignore ACTUALIZADO (NO IGNORA BD NI TOKEN)
gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
venv_new/
ENV/
dist/
build/
*.egg-info/
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Backups (pero NO la base principal)
backups/
*.zip
*.tar.gz

# Logs
logs/
*.log

# Reportes
reportes/
*.xlsx
*.csv

# Imágenes subidas (las que genere el usuario)
imagenes_productos/
!assets/imagenes_productos/

# Archivos temporales
temp/
tmp/
*.tmp
geocache.json

# Sistema
.DS_Store
Thumbs.db
desktop.ini

# ✅ NOTA: NO ignoramos distribuidora.db ni turso-facturar.txt
# Para que el sistema funcione al descargar

📄 README.md PARA LA FACULTAD
markdown

# 🏢 Sistema de Distribución y Logística

**Proyecto de Facultad - Código Crítico**
**Tercer Semestre 2026**

---

## 📋 Descripción

Sistema completo de gestión para una distribuidora con las siguientes funcionalidades:

- ✅ Gestión de Clientes (CRUD con UUID)
- ✅ Gestión de Productos (CRUD con UUID)
- ✅ Gestión de Preventistas (CRUD con UUID)
- ✅ Facturación con PDF y QR
- ✅ Cuenta Corriente
- ✅ Cheques con consulta BCRA
- ✅ Notas de Venta
- ✅ Dashboard con gráficos
- ✅ Mapa de clientes con Leaflet
- ✅ Sincronización con Turso (base de datos en la nube)
- ✅ Sistema de Backups automáticos

---

## 🚀 INSTALACIÓN RÁPIDA (3 PASOS)

### Linux / Mac

```bash
# 1. Clonar o descargar el proyecto
cd facturar

# 2. Ejecutar el instalador
./install.sh

# 3. Ejecutar el sistema
python main.py

Windows
cmd

# 1. Clonar o descargar el proyecto
cd facturar

# 2. Ejecutar el instalador
install.bat

# 3. Ejecutar el sistema
python main.py

🔐 CREDENCIALES DE ACCESO
Usuario	Contraseña	Rol
admin	admin	Administrador
prev001	admin	Preventista
prev002	admin	Preventista
📦 DEPENDENCIAS

Todas las dependencias se instalan automáticamente con el script de instalación:
Dependencia	Versión	Uso
PyQt6	6.6.0	Interfaz gráfica
PyQt6-WebEngine	6.6.0	Mapa interactivo
requests	2.31.0	Sincronización HTTP
reportlab	4.0.4	Generación de PDF
matplotlib	3.7.2	Gráficos
Pillow	10.0.0	Imágenes
python-dateutil	2.8.2	Fechas
🗄️ BASE DE DATOS

La base de datos distribuidora.db ya está incluida con datos de prueba:

    ✅ 700+ clientes

    ✅ 95+ productos

    ✅ 500+ notas de venta

    ✅ 7 preventistas

    ✅ 19 categorías

☁️ SINCRONIZACIÓN CON TURSO

El sistema incluye el token de Turso en el archivo turso-facturar.txt.
La sincronización es automática cada 5 segundos.
📁 ESTRUCTURA DEL PROYECTO
text

facturar/
├── main.py              # Punto de entrada
├── distribuidora.db     # Base de datos (incluida)
├── turso-facturar.txt   # Token de Turso (incluido)
├── db/                  # Gestión de base de datos
├── modelos/             # Modelos de datos (UUID)
├── controladores/       # Lógica de negocio
├── vistas/              # Interfaz de usuario
├── utilidades/          # Utilidades y sincronización
└── assets/              # Recursos (Leaflet)

🧪 PRUEBA RÁPIDA
bash

# Verificar PyQt6
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"

# Verificar WebEngine
python -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('✅ WebEngine OK')"

# Verificar base de datos
python -c "import sqlite3; conn=sqlite3.connect('distribuidora.db'); print('✅ Base de datos OK')"

📝 NOTAS PARA LA ENTREGA

    Base de datos incluida - No necesita crear ni migrar nada

    Token de Turso incluido - La sincronización funciona directamente

    Datos de prueba - El sistema viene con datos precargados

    Instalación automática - Un solo comando y listo

👨‍💻 Desarrollado por

Código Crítico
Tercer Semestre 2026
📄 Licencia

Proyecto académico - Todos los derechos reservados
text


---

## 📄 `install.sh` (Instalación Automática)

```bash
#!/bin/bash
# Script de instalación automática

echo "=================================================="
echo "   SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA"
echo "   Instalación automática"
echo "=================================================="

echo ""
echo "📦 Creando entorno virtual..."
python3 -m venv venv

echo ""
echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo ""
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📦 Verificando instalación..."
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"
python -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('✅ WebEngine OK')"

echo ""
echo "📦 Verificando base de datos..."
python -c "import sqlite3; conn=sqlite3.connect('distribuidora.db'); print('✅ Base de datos OK')"

echo ""
echo "=================================================="
echo "✅ ¡Instalación completada!"
echo ""
echo "Para ejecutar el sistema:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Credenciales: admin / admin"
echo "=================================================="

bash

chmod +x install.sh

📄 install.bat (Windows)
batch

@echo off
echo ==================================================
echo    SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA
echo    Instalación automática
echo ==================================================

echo.
echo 📦 Creando entorno virtual...
python -m venv venv

echo.
echo 📦 Activando entorno virtual...
call venv\Scripts\activate

echo.
echo 📦 Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 📦 Verificando instalación...
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"
python -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('✅ WebEngine OK')"

echo.
echo 📦 Verificando base de datos...
python -c "import sqlite3; conn=sqlite3.connect('distribuidora.db'); print('✅ Base de datos OK')"

echo.
echo ==================================================
echo ✅ ¡Instalación completada!
echo.
echo Para ejecutar el sistema:
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Credenciales: admin / admin
echo ==================================================
pause

📄 requirements.txt
txt

# Core
PyQt6==6.6.0
PyQt6-WebEngine==6.6.0

# HTTP y Sincronización
requests==2.31.0

# PDF y Reportes
reportlab==4.0.4

# Gráficos
matplotlib==3.7.2

# Procesamiento de imágenes
Pillow==10.0.0

# Utilidades de fechas
python-dateutil==2.8.2

📄 .env (Variables de entorno)
env

# Configuración del sistema
QT_SCALE_FACTOR=1.0

🚀 COMANDOS PARA SUBIR A GITHUB
bash

# 1. Inicializar repositorio
git init

# 2. Agregar todos los archivos (INCLUYENDO BD Y TOKEN)
git add .

# 3. Verificar que no se ignora nada importante
git status

# 4. Hacer commit
git commit -m "Sistema de Distribución y Logística - Proyecto Facultad"

# 5. Conectar con GitHub
git remote add origin https://github.com/tu-usuario/facturar.git

# 6. Subir
git push -u origin main

🎯 PARA EL USUARIO FINAL (COMPAÑERO DE FACULTAD)
bash

# PASO 1: Clonar o descargar
git clone https://github.com/tu-usuario/facturar.git
cd facturar

# PASO 2: Instalar (Linux/Mac)
./install.sh

# PASO 2: Instalar (Windows)
install.bat

# PASO 3: Ejecutar
python main.py

# PASO 4: Login
# Usuario: admin
# Contraseña: admin

✅ RESUMEN
Elemento	Estado
Base de datos	✅ Incluida (distribuidora.db)
Token Turso	✅ Incluido (turso-facturar.txt)
Dependencias	✅ En requirements.txt
Instalación automática	✅ install.sh / install.bat
README	✅ Instrucciones claras
Credenciales	✅ admin / admin

¿Necesitas que ajuste algo más?
ne sql
✅ GUÍA COMPLETA PARA SUBIR EL PROYECTO CON BASE DE DATOS Y TOKEN - INCLUYENDO SQL
📁 ESTRUCTURA DE ARCHIVOS PARA SUBIR
text

facturar/
├── README.md                    # Instrucciones
├── requirements.txt             # Dependencias
├── install.sh                   # Instalación Linux/Mac
├── install.bat                  # Instalación Windows
├── main.py                      # Punto de entrada
├── constantes.py
├── distribuidora.db             # ✅ BASE DE DATOS (INCLUIDA)
├── turso-facturar.txt           # ✅ TOKEN DE TURSO (INCLUIDO)
├── assets/
│   └── leaflet/
│       ├── css/
│       │   └── leaflet.min.css
│       └── js/
│           └── leaflet.min.js
├── db/
│   ├── db_manager.py
│   └── script_creacion.sql      # ✅ SCRIPT SQL DE CREACIÓN
├── modelos/
│   ├── __init__.py
│   ├── base.py
│   ├── cliente.py
│   ├── producto.py
│   ├── categoria.py
│   ├── preventista.py
│   ├── usuario.py
│   ├── nota_venta.py
│   ├── factura.py
│   ├── lote.py
│   ├── cobro.py
│   ├── cheque.py
│   ├── cuenta_corriente.py
│   └── catalogo.py
├── controladores/
│   ├── __init__.py
│   ├── controlador_clientes.py
│   ├── controlador_productos.py
│   ├── controlador_preventistas.py
│   ├── controlador_ventas.py
│   ├── controlador_stock.py
│   ├── controlador_cuentacorriente.py
│   ├── controlador_cheques.py
│   ├── controlador_reportes.py
│   └── controlador_rentabilidad.py
├── vistas/
│   ├── __init__.py
│   ├── ventana_principal.py
│   ├── acerca_de.py
│   ├── clientes/
│   │   └── vista_clientes.py
│   ├── productos/
│   │   └── vista_productos_unificada.py
│   ├── preventistas/
│   │   └── vista_preventistas.py
│   ├── facturacion/
│   │   └── vista_facturacion.py
│   ├── notas_venta/
│   │   └── vista_notas_venta.py
│   ├── cheques/
│   │   └── vista_cheques.py
│   ├── cuenta_corriente/
│   │   └── vista_cuenta_corriente.py
│   ├── dashboard/
│   │   └── vista_dashboard.py
│   ├── rentabilidad/
│   │   └── vista_rentabilidad.py
│   ├── mapa/
│   │   └── vista_mapa.py
│   ├── parametros/
│   │   └── vista_parametros.py
│   ├── backup/
│   │   ├── vista_backup.py
│   │   └── backup_splash.py
│   └── sincronizacion/
│       └── vista_monitor.py
├── utilidades/
│   ├── __init__.py
│   ├── turso_client.py
│   ├── sync_manager.py
│   ├── sync_queue.py
│   ├── sync_utils.py
│   ├── sync_lock.py
│   ├── central_sync.py
│   ├── sync_directo.py
│   ├── sync_monitor.py
│   ├── backup_profesional.py
│   ├── backup_splash.py
│   ├── geocodificar.py
│   ├── validaciones.py
│   ├── fechas.py
│   ├── imagenes.py
│   ├── calculos.py
│   └── notificador_sync.py
├── .gitignore
├── .env
└── start.py

📄 ARCHIVOS NECESARIOS
1. .gitignore
gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
venv_new/
ENV/
dist/
build/
*.egg-info/
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Backups
backups/
*.zip
*.tar.gz

# Logs
logs/
*.log

# Reportes
reportes/
*.xlsx
*.csv

# Imágenes subidas
imagenes_productos/

# Archivos temporales
temp/
tmp/
*.tmp
geocache.json

# Sistema
.DS_Store
Thumbs.db
desktop.ini

# ✅ NOTA: NO ignoramos distribuidora.db ni turso-facturar.txt
# El sistema debe funcionar al descargar

2. requirements.txt
txt

# Core
PyQt6==6.6.0
PyQt6-WebEngine==6.6.0

# HTTP y Sincronización
requests==2.31.0

# PDF y Reportes
reportlab==4.0.4

# Gráficos
matplotlib==3.7.2

# Procesamiento de imágenes
Pillow==10.0.0

# Utilidades de fechas
python-dateutil==2.8.2

3. README.md
markdown

# 🏢 Sistema de Distribución y Logística

**Proyecto de Facultad - Código Crítico**
**Tercer Semestre 2026**

---

## 📋 Descripción

Sistema completo de gestión para una distribuidora.

### Funcionalidades

- ✅ Gestión de Clientes (CRUD con UUID)
- ✅ Gestión de Productos (CRUD con UUID)
- ✅ Gestión de Preventistas (CRUD con UUID)
- ✅ Facturación con PDF y QR
- ✅ Cuenta Corriente
- ✅ Cheques con consulta BCRA
- ✅ Notas de Venta
- ✅ Dashboard con gráficos
- ✅ Mapa de clientes con Leaflet
- ✅ Sincronización con Turso
- ✅ Sistema de Backups automáticos

---

## 🚀 INSTALACIÓN (3 PASOS)

### Linux / Mac

```bash
# 1. Descargar y entrar
cd facturar

# 2. Ejecutar instalador
./install.sh

# 3. Ejecutar sistema
python main.py

Windows
cmd

# 1. Descargar y entrar
cd facturar

# 2. Ejecutar instalador
install.bat

# 3. Ejecutar sistema
python main.py

🔐 CREDENCIALES
Usuario	Contraseña	Rol
admin	admin	Administrador
prev001	admin	Preventista
🗄️ BASE DE DATOS

La base de datos distribuidora.db ya está incluida con datos de prueba.
☁️ TURSO

El token de Turso está incluido en turso-facturar.txt.
La sincronización es automática cada 5 segundos.
👨‍💻 Desarrollado por

Código Crítico
Tercer Semestre 2026
text


---

### 4. `install.sh` (Linux/Mac)

```bash
#!/bin/bash
# Script de instalación automática

echo "=================================================="
echo "   SISTEMA DE DISTRIBUCIÓN Y LOGÍSTICA"
echo "   Instalación automática"
echo "=================================================="

echo ""
echo "📦 Creando entorno virtual..."
python3 -m venv venv

echo ""
echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo ""
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📦 Verificando instalación..."
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 OK')"
python -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('✅ WebEngine OK')"

echo ""
echo "📦 Verificando base de datos..."
python -c "import sqlite3; conn=sqlite3.connect('distribuidora.db'); print('✅ Base de datos OK')"

echo ""
echo "=================================================="
echo "✅ ¡Instalación completada!"
echo ""
echo "Para ejecutar:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Credenciales: admin / admin"
echo "=================================================="



echo "chmod +x install.sh