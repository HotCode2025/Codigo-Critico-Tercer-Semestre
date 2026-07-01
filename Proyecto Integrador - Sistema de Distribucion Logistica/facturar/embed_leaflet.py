#!/usr/bin/env python3
"""
Embeber Leaflet en el HTML como base64 - CORREGIDO
"""

import os

def embed_leaflet():
    """Convierte archivos Leaflet a texto para embeber en HTML"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("📦 EMBEBER LEAFLET EN HTML")
    print("=" * 60)
    
    # CSS
    css_path = os.path.join(base_dir, "assets", "leaflet", "css", "leaflet.min.css")
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        print(f"✅ CSS cargado: {len(css_content)} caracteres")
    else:
        print(f"❌ CSS no encontrado: {css_path}")
        return
    
    # JS
    js_path = os.path.join(base_dir, "assets", "leaflet", "js", "leaflet.min.js")
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        print(f"✅ JS cargado: {len(js_content)} caracteres")
    else:
        print(f"❌ JS no encontrado: {js_path}")
        return
    
    # ✅ Generar HTML con contenido embebido (corregido)
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mapa de Clientes</title>
    <style>
        {css_content}
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
        // Leaflet JS embebido
        {js_content}
    </script>
    <script>
        // Datos desde Python se insertarán aquí dinámicamente
        var clientesData = [];
        var distribuidoraData = null;
        var mostrarRuta = false;

        function renderizarMapa() {{
            var loading = document.getElementById('loading');
            
            if (typeof L === 'undefined') {{
                loading.innerHTML = '❌ Error: Leaflet no se cargó correctamente';
                return;
            }}

            if (clientesData.length === 0) {{
                loading.innerHTML = '📍 No hay clientes con coordenadas';
                return;
            }}

            loading.style.display = 'none';

            // Calcular centro
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
        }}

        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {{
            if (clientesData.length > 0) {{
                renderizarMapa();
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Guardar HTML embebido
    output_path = os.path.join(base_dir, "assets", "mapa_embebido.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ HTML embebido guardado en: {output_path}")
    print(f"📊 Tamaño: {len(html)} caracteres")
    print("\n📌 Ahora ejecuta: python main.py y ve al mapa")

if __name__ == "__main__":
    embed_leaflet()