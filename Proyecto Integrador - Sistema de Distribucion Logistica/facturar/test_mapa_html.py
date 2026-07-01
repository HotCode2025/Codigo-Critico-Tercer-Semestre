#!/usr/bin/env python3
"""
Test para diagnosticar el problema del mapa
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from db.db_manager import obtener_conexion
from vistas.mapa.vista_mapa import VistaMapa

def test_mapa():
    """Prueba el mapa"""
    print("=" * 60)
    print("🧪 TEST DEL MAPA")
    print("=" * 60)
    
    # Verificar PyQt6-WebEngine
    try:
        import PyQt6.QtWebEngineWidgets
        print("✅ PyQt6-WebEngine instalado")
    except ImportError:
        print("❌ PyQt6-WebEngine NO instalado")
        print("   Ejecutar: pip install PyQt6-WebEngine")
        return
    
    app = QApplication(sys.argv)
    db = obtener_conexion()
    
    print("📊 Conectado a base de datos")
    
    # Crear ventana del mapa
    ventana = VistaMapa(db)
    
    # Verificar clientes con coordenadas
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) as total FROM clientes WHERE latitud IS NOT NULL AND longitud IS NOT NULL")
    total = cur.fetchone()['total']
    print(f"📊 Clientes con coordenadas: {total}")
    
    # Mostrar ventana
    ventana.show()
    print("🗺️ Ventana del mapa abierta")
    print("   Presiona Ctrl+C para salir")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_mapa()
