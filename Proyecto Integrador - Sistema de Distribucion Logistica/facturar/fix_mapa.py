#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Código Crítico - Tercer Semestre Año 2026
==================================================
FIX PARA EL MAPA - Reemplaza el método _generar_html_mapa_local
==================================================
📌 EJECUTAR: python fix_mapa.py
📌 FUNCIÓN: Parchea vista_mapa.py para usar CDN en lugar de archivos locales
"""

import os
import re
import shutil
from datetime import datetime

# ============================================================
# RUTAS
# ============================================================

RUTA_VISTA_MAPA = "vistas/mapa/vista_mapa.py"
RUTA_BACKUP = f"vistas/mapa/vista_mapa.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ============================================================
# NUEVO CÓDIGO PARA _generar_html_mapa_local (CON CDN)
# ============================================================

NUEVO_METODO = """
    def _generar_html_mapa_local(self, clientes_con_mapa, distribuidora_punto):
        \"\"\"Genera HTML usando Leaflet desde CDN (Internet)\"\"\"
        
        if not clientes_con_mapa:
            return None
        
        import json
        clientes_json = json.dumps(clientes_con_mapa, default=str)
        distribuidora_json = json.dumps(distribuidora_punto, default=str) if distribuidora_punto else 'null'
        ruta = "true" if self.chk_ruta_optima.isChecked() else "false"
        
        html = f\"\"\"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Mapa de Clientes</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css" />
            <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>
            <style>
                #map {{ height: 100vh; width: 100%; }}
                body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background: #2C3E50; }}
                .loading {{
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-size: 20px;
                    z-index: 999;
                    background: rgba(0,0,0,0.7);
                    padding: 20px 40px;
                    border-radius: 10px;
                }}
                .leyenda {{
                    position: absolute;
                    bottom: 30px;
                    left: 30px;
                    background: rgba(255,255,255,0.95);
                    padding: 12px 16px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    font-size: 11px;
                    z-index: 1000;
                    border: 2px solid #1565C0;
                    min-width: 160px;
                }}
                .leyenda .titulo {{
                    font-weight: bold;
                    font-size: 12px;
                    color: #1A237E;
                    text-align: center;
                    margin-bottom: 5px;
                }}
                .leyenda .item {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 2px 0;
                }}
                .leyenda .circulo {{
                    width: 14px;
                    height: 14px;
                    border-radius: 50%;
                    display: inline-block;
                    border: 1px solid rgba(0,0,0,0.2);
                }}
                .leyenda .verde {{ background-color: #4CAF50; }}
                .leyenda .rojo {{ background-color: #D32F2F; }}
                .leyenda .amarillo {{ background-color: #FFC107; }}
                .leyenda .azul {{ background-color: #1565C0; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="loading" id="loading">🔄 Cargando mapa...</div>
            <div class="leyenda">
                <div class="titulo">📊 LEYENDA</div>
                <div class="item"><span class="circulo rojo"></span> Deuda (debe)</div>
                <div class="item"><span class="circulo verde"></span> Saldo a favor</div>
                <div class="item"><span class="circulo amarillo"></span> Saldo en cero</div>
                <div class="item"><span class="circulo azul"></span> Distribuidora</div>
            </div>

            <script>
                var clientesData = {clientes_json};
                var distribuidoraData = {distribuidora_json};
                var mostrarRuta = {ruta};

                document.addEventListener('DOMContentLoaded', function() {{
                    var loading = document.getElementById('loading');
                    
                    if (typeof L === 'undefined') {{
                        loading.innerHTML = '❌ Error: Leaflet no se cargó.<br>Verifica tu conexión a Internet';
                        return;
                    }}

                    if (clientesData.length === 0) {{
                        loading.innerHTML = '📍 No hay clientes con coordenadas';
                        return;
                    }}

                    loading.style.display = 'none';

                    var todos = clientesData.slice();
                    if (distribuidoraData) {{
                        todos.push(distribuidoraData);
                    }}

                    var latSum = 0, lonSum = 0;
                    todos.forEach(function(c) {{
                        latSum += c.latitud;
                        lonSum += c.longitud;
                    }});
                    var latCenter = latSum / todos.length;
                    var lonCenter = lonSum / todos.length;

                    var map = L.map('map').setView([latCenter, lonCenter], 12);

                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '&copy; OpenStreetMap'
                    }}).addTo(map);

                    function crearIcono(color, texto) {{
                        return L.divIcon({{
                            className: 'custom-div-icon',
                            html: '<div style="background-color:' + color + '; color:white; border-radius:50%; width:28px; height:28px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px; border:2px solid white; box-shadow:0 2px 5px rgba(0,0,0,0.3);">' + texto + '</div>',
                            iconSize: [28, 28],
                            iconAnchor: [14, 14]
                        }});
                    }}

                    var distribuidoraIcon = L.divIcon({{
                        className: 'custom-div-icon',
                        html: '<div style="background-color:#1565C0; color:white; border-radius:50%; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:14px; border:2px solid white; box-shadow:0 2px 5px rgba(0,0,0,0.3);">🏭</div>',
                        iconSize: [32, 32],
                        iconAnchor: [16, 16]
                    }});

                    if (distribuidoraData) {{
                        L.marker([distribuidoraData.latitud, distribuidoraData.longitud], {{
                            icon: distribuidoraIcon
                        }}).addTo(map).bindPopup('<b>🏭 ' + distribuidoraData.razon_social + '</b><br><i>Punto de partida</i>');
                    }}

                    var markers = [];
                    clientesData.forEach(function(cliente) {{
                        var saldo = cliente.saldo_cuenta_corriente || 0;
                        var color, emoji, estado;

                        if (saldo > 0) {{
                            color = '#D32F2F';
                            emoji = '🔴';
                            estado = 'DEBE';
                        }} else if (saldo < 0) {{
                            color = '#4CAF50';
                            emoji = '🟢';
                            estado = 'A FAVOR';
                        }} else {{
                            color = '#FFC107';
                            emoji = '🟡';
                            estado = 'CERO';
                        }}

                        var icono = crearIcono(color, emoji);
                        var marker = L.marker([cliente.latitud, cliente.longitud], {{
                            icon: icono
                        }}).addTo(map);

                        marker.bindPopup(
                            '<b>' + cliente.razon_social + '</b><br>' +
                            '<b>ID:</b> ' + cliente.id.substring(0, 8) + '...<br>' +
                            '<b>Dir:</b> ' + (cliente.calle || '') + ' ' + (cliente.numero || '') + '<br>' +
                            '<b>Localidad:</b> ' + (cliente.localidad || '') + '<br>' +
                            '<b>Saldo:</b> <span style="color:' + color + '; font-weight:bold;">$' + saldo.toFixed(2) + '</span><br>' +
                            '<b>Estado:</b> ' + estado
                        );

                        markers.push(marker);
                    }});

                    if (mostrarRuta && clientesData.length > 0) {{
                        var latlngs = [];
                        if (distribuidoraData) {{
                            latlngs.push([distribuidoraData.latitud, distribuidoraData.longitud]);
                        }}
                        clientesData.forEach(function(c) {{
                            latlngs.push([c.latitud, c.longitud]);
                        }});

                        L.polyline(latlngs, {{
                            color: '#E74C3C',
                            weight: 4,
                            opacity: 0.8,
                            dashArray: '8, 8'
                        }}).addTo(map);

                        map.fitBounds(L.polyline(latlngs).getBounds(), {{ padding: [50, 50] }});
                    }} else {{
                        var group = L.featureGroup(markers);
                        map.fitBounds(group.getBounds(), {{ padding: [50, 50] }});
                    }}
                }});
            </script>
        </body>
        </html>
        \"\"\"
        
        return html
"""


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def aplicar_fix():
    """Aplica el fix al archivo vista_mapa.py"""
    
    print("=" * 60)
    print("🔧 FIX PARA EL MAPA - USANDO CDN")
    print("=" * 60)
    
    # Verificar que el archivo existe
    if not os.path.exists(RUTA_VISTA_MAPA):
        print(f"\n❌ ERROR: No se encontró {RUTA_VISTA_MAPA}")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto.")
        return False
    
    print(f"\n📁 Archivo encontrado: {RUTA_VISTA_MAPA}")
    
    # Crear backup
    print(f"\n📦 Creando backup: {RUTA_BACKUP}")
    shutil.copy2(RUTA_VISTA_MAPA, RUTA_BACKUP)
    print("✅ Backup creado")
    
    # Leer el archivo
    with open(RUTA_VISTA_MAPA, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar el método antiguo
    patron = r'def _generar_html_mapa_local\(self, clientes_con_mapa, distribuidora_punto\):.*?(?=\n    def |\n\n\n|$)'
    
    # Buscar si ya está usando CDN
    if 'cdn.jsdelivr.net' in contenido:
        print("\n⚠️ El archivo YA ESTÁ usando CDN.")
        print("   No se necesita aplicar el fix.")
        return True
    
    # Reemplazar el método
    if re.search(patron, contenido, re.DOTALL):
        contenido_nuevo = re.sub(patron, NUEVO_METODO.strip(), contenido, flags=re.DOTALL)
        
        # Guardar el archivo modificado
        with open(RUTA_VISTA_MAPA, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print("\n✅ FIX APLICADO CORRECTAMENTE")
        print("   El mapa ahora usará Leaflet desde CDN (Internet)")
        print("   Se creó un backup en:", RUTA_BACKUP)
        return True
    else:
        print("\n⚠️ No se encontró el método _generar_html_mapa_local")
        print("   Verifica que el archivo tenga la estructura correcta.")
        return False


def revertir_fix():
    """Revertir el fix (restaurar backup)"""
    
    backups = [f for f in os.listdir("vistas/mapa/") if f.startswith("vista_mapa.py.backup_")]
    
    if not backups:
        print("❌ No hay backups disponibles")
        return False
    
    print("\n📦 Backups disponibles:")
    for i, b in enumerate(backups):
        print(f"   {i+1}. {b}")
    
    try:
        seleccion = int(input("\nSelecciona el backup a restaurar (número): ")) - 1
        if 0 <= seleccion < len(backups):
            backup_path = os.path.join("vistas/mapa/", backups[seleccion])
            shutil.copy2(backup_path, RUTA_VISTA_MAPA)
            print(f"✅ Restaurado: {backups[seleccion]}")
            return True
    except:
        print("❌ Selección inválida")
    
    return False


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   FIX PARA EL MAPA - Código Crítico 2026")
    print("=" * 60)
    print("\n📌 Este script parchea vista_mapa.py para usar CDN")
    print("   en lugar de archivos locales de Leaflet.")
    print("\n   Selecciona una opción:")
    print("   1. Aplicar fix (usar CDN)")
    print("   2. Revertir fix (restaurar backup)")
    print("   3. Salir")
    
    opcion = input("\nOpción: ").strip()
    
    if opcion == "1":
        aplicar_fix()
    elif opcion == "2":
        revertir_fix()
    else:
        print("Saliendo...")