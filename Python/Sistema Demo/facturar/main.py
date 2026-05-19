"""
Código Crítico - Tercer Semestre Año 2026
Punto de entrada principal del Sistema de Gestión para Distribuidora.
Inicializa la base de datos SQLite, crea las tablas si es necesario,
y lanza la interfaz gráfica con la ventana principal.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar el gestor de base de datos y la ventana principal
from db.db_manager import inicializar_bd, obtener_conexion
from vistas.ventana_principal import VentanaPrincipal

def main():
    """
    Función principal:
    1. Inicializa la base de datos (crea tablas si no existen).
    2. Crea la aplicación Qt y la ventana principal.
    3. Ejecuta el bucle de eventos.
    """
    # 1. Preparar la base de datos
    print("Inicializando base de datos...")
    inicializar_bd()   # Ejecuta el script SQL y crea el archivo si no existe
    print("Base de datos lista.")

    # 2. Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema Distribuidora")
    app.setOrganizationName("CodigoCritico")

    # Configurar una fuente base para toda la aplicación (opcional)
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)

    # 3. Mostrar la ventana principal
    ventana = VentanaPrincipal()
    ventana.show()

    # 4. Ejecutar el bucle de eventos de Qt
    sys.exit(app.exec())

if __name__ == "__main__":
    main()