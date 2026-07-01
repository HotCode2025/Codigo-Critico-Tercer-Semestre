@echo off
echo 🚀 Sistema de Distribución y Logística
echo ========================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    echo    Descargar de: https://python.org
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist venv (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt

REM Ejecutar sistema
echo 🚀 Iniciando sistema...
python main.py

pause