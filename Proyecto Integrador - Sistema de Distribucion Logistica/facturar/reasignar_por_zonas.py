#!/usr/bin/env python3
"""
Reasignar clientes a preventistas según su zona
"""

import sqlite3
from db.db_manager import obtener_conexion
from collections import Counter
import re

def normalizar_zona(localidad):
    """Normaliza el nombre de la localidad para mejor matching"""
    localidad = localidad.strip().upper()
    # Remover acentos simples
    localidad = localidad.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    localidad = localidad.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return localidad

def reasignar_clientes_por_zona():
    conn = obtener_conexion()
    cur = conn.cursor()
    
    print("=" * 70)
    print("📋 REASIGNAR CLIENTES POR ZONA")
    print("=" * 70)
    
    # ============================================================
    # 1. OBTENER PREVENTISTAS Y SUS ZONAS
    # ============================================================
    cur.execute("""
        SELECT id, nombre, apellido, zona
        FROM preventistas
        WHERE activo = 1
    """)
    preventistas = cur.fetchall()
    
    if not preventistas:
        print("❌ No hay preventistas activos")
        return
    
    print(f"\n📊 Preventistas activos: {len(preventistas)}")
    
    # Verificar si tienen zona definida
    tienen_zona = [p for p in preventistas if p['zona'] and p['zona'].strip()]
    sin_zona = [p for p in preventistas if not p['zona'] or not p['zona'].strip()]
    
    if sin_zona:
        print(f"\n⚠️ {len(sin_zona)} preventistas sin zona definida:")
        for p in sin_zona:
            print(f"   - {p['nombre']} {p['apellido']}")
        
        # Asignar zonas basadas en sus clientes actuales
        print("\n📌 Asignando zonas automáticamente...")
        for p in sin_zona:
            # Ver qué localidades tienen sus clientes
            cur.execute("""
                SELECT DISTINCT localidad
                FROM clientes
                WHERE preventista_id = ? AND activo = 1 AND localidad IS NOT NULL
                LIMIT 10
            """, (p['id'],))
            localidades = [row['localidad'] for row in cur.fetchall()]
            
            if localidades:
                # Usar la localidad más común
                zona = localidades[0]
                cur.execute("UPDATE preventistas SET zona = ? WHERE id = ?", (zona, p['id']))
                print(f"   ✅ {p['nombre']} {p['apellido']} → Zona: {zona}")
            else:
                # Si no tiene clientes, asignar zona por defecto
                zonas_disponibles = ['NORTE', 'SUR', 'ESTE', 'OESTE', 'CENTRO']
                idx = len([p for p in preventistas if p['zona'] and p['zona'].strip()]) % len(zonas_disponibles)
                zona = zonas_disponibles[idx]
                cur.execute("UPDATE preventistas SET zona = ? WHERE id = ?", (zona, p['id']))
                print(f"   ✅ {p['nombre']} {p['apellido']} → Zona: {zona} (asignada por defecto)")
        
        conn.commit()
        
        # Actualizar lista de preventistas
        cur.execute("""
            SELECT id, nombre, apellido, zona
            FROM preventistas
            WHERE activo = 1
        """)
        preventistas = cur.fetchall()
    
    # ============================================================
    # 2. MOSTRAR ZONAS ACTUALES
    # ============================================================
    print("\n📊 ZONAS DE PREVENTISTAS:")
    print("-" * 50)
    for p in preventistas:
        zona = p['zona'] or 'SIN ZONA'
        # Contar clientes actuales
        cur.execute("SELECT COUNT(*) as total FROM clientes WHERE preventista_id = ? AND activo = 1", (p['id'],))
        total = cur.fetchone()['total']
        print(f"   🏷️ {p['nombre']} {p['apellido']}: {zona} ({total} clientes)")
    
    # ============================================================
    # 3. REASIGNAR CLIENTES
    # ============================================================
    print("\n" + "=" * 70)
    print("🔄 REASIGNANDO CLIENTES POR ZONA")
    print("=" * 70)
    
    # Primero, limpiar todos los preventistas de los clientes
    print("\n📌 Limpiando asignaciones anteriores...")
    cur.execute("UPDATE clientes SET preventista_id = NULL WHERE activo = 1")
    conn.commit()
    print("   ✅ Todas las asignaciones limpiadas")
    
    # Crear diccionario de zona → preventista
    zona_preventista = {}
    for p in preventistas:
        zona = p['zona'].strip().upper() if p['zona'] else 'SIN ZONA'
        # Normalizar zona
        zona = normalizar_zona(zona)
        zona_preventista[zona] = p['id']
    
    print(f"\n📊 Mapeo de zonas a preventistas:")
    for zona, id_preventista in zona_preventista.items():
        # Obtener nombre del preventista
        cur.execute("SELECT nombre, apellido FROM preventistas WHERE id = ?", (id_preventista,))
        p = cur.fetchone()
        print(f"   🏷️ {zona} → {p['nombre']} {p['apellido']}")
    
    # Obtener todos los clientes activos
    cur.execute("""
        SELECT id, razon_social, localidad, provincia
        FROM clientes
        WHERE activo = 1
    """)
    clientes = cur.fetchall()
    
    print(f"\n📊 Total clientes a reasignar: {len(clientes)}")
    
    # Asignar cada cliente según su localidad
    asignados = 0
    no_asignados = 0
    asignacion_por_preventista = {}
    
    for cliente in clientes:
        localidad = cliente['localidad'] or ''
        provincia = cliente['provincia'] or ''
        
        # Buscar zona que coincida con la localidad
        localidad_normalizada = normalizar_zona(localidad)
        provincia_normalizada = normalizar_zona(provincia)
        
        preventista_id = None
        zona_encontrada = None
        
        # Intentar matching exacto de localidad
        for zona, id_preventista in zona_preventista.items():
            if zona in localidad_normalizada or localidad_normalizada in zona:
                preventista_id = id_preventista
                zona_encontrada = zona
                break
        
        # Si no hay match, intentar con provincia
        if not preventista_id:
            for zona, id_preventista in zona_preventista.items():
                if zona in provincia_normalizada or provincia_normalizada in zona:
                    preventista_id = id_preventista
                    zona_encontrada = zona
                    break
        
        # Si aún no hay match, asignar al primer preventista (o al que tenga menos clientes)
        if not preventista_id:
            # Buscar el preventista con menos clientes
            cur.execute("""
                SELECT preventista_id, COUNT(*) as total
                FROM clientes
                WHERE preventista_id IS NOT NULL
                GROUP BY preventista_id
                ORDER BY total ASC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                preventista_id = row['preventista_id']
                zona_encontrada = "SIN ZONA"
            else:
                # Si no hay asignaciones, usar el primer preventista
                preventista_id = list(zona_preventista.values())[0]
                zona_encontrada = "SIN ZONA"
        
        # Asignar cliente
        if preventista_id:
            cur.execute("UPDATE clientes SET preventista_id = ? WHERE id = ?", (preventista_id, cliente['id']))
            asignados += 1
            
            # Contar asignaciones por preventista
            if preventista_id not in asignacion_por_preventista:
                asignacion_por_preventista[preventista_id] = 0
            asignacion_por_preventista[preventista_id] += 1
        else:
            no_asignados += 1
            print(f"   ⚠️ {cliente['razon_social']} - No se pudo asignar")
    
    conn.commit()
    
    # ============================================================
    # 4. MOSTRAR RESULTADOS
    # ============================================================
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DE LA REASIGNACIÓN")
    print("=" * 70)
    
    print(f"\n✅ Clientes asignados: {asignados}")
    print(f"⚠️ Clientes sin asignar: {no_asignados}")
    
    print("\n📊 DISTRIBUCIÓN FINAL POR PREVENTISTA:")
    print("-" * 50)
    
    for p in preventistas:
        total = asignacion_por_preventista.get(p['id'], 0)
        zona = p['zona'] or 'SIN ZONA'
        barra = '█' * min(int(total / 5), 40)
        print(f"   {p['nombre']} {p['apellido']:20} | {zona:15} | {total:4} clientes {barra}")
    
    # ============================================================
    # 5. VERIFICAR ASIGNACIÓN POR ZONA
    # ============================================================
    print("\n📊 VERIFICACIÓN POR ZONA:")
    print("-" * 50)
    
    for zona, id_preventista in zona_preventista.items():
        cur.execute("""
            SELECT COUNT(*) as total
            FROM clientes
            WHERE preventista_id = ? AND activo = 1
        """, (id_preventista,))
        total = cur.fetchone()['total']
        cur.execute("SELECT nombre, apellido FROM preventistas WHERE id = ?", (id_preventista,))
        p = cur.fetchone()
        print(f"   🏷️ {zona}: {total} clientes → {p['nombre']} {p['apellido']}")
    
    print("\n" + "=" * 70)
    print("✅ REASIGNACIÓN COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    reasignar_clientes_por_zona()
