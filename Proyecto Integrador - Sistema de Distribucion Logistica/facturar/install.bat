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
echo Para ejecutar:
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Credenciales: admin / admin
echo ==================================================
pause