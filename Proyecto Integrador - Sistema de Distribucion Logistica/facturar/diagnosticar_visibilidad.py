import sqlite3

def diagnosticar():
    conn = sqlite3.connect('distribuidora.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE VISIBILIDAD DE NOTAS DE VENTA")
    print("=" * 80)
    print()
    
    # 1. Usuarios y sus preventistas
    print("👥 USUARIOS Y PREVENTISTAS:")
    cursor.execute("""
        SELECT u.username, u.rol, p.legajo, p.nombre || ' ' || p.apellido as nombre
        FROM usuarios u
        LEFT JOIN preventistas p ON u.preventista_id = p.id
        WHERE u.activo = 1
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} ({row[1]}) -> {row[2]} {row[3]}")
    print()
    
    # 2. Ver notas por preventista
    print("📊 NOTAS POR PREVENTISTA:")
    cursor.execute("""
        SELECT 
            p.legajo,
            p.nombre || ' ' || p.apellido as nombre,
            COUNT(n.id) as cantidad,
            SUM(n.total) as total
        FROM preventistas p
        LEFT JOIN notas_venta n ON p.id = n.preventista_id
        GROUP BY p.id
        ORDER BY cantidad DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} - {row[1]}: {row[2]} notas (${row[3] or 0:,.2f})")
    print()
    
    # 3. Notas sin preventista
    cursor.execute("SELECT COUNT(*) FROM notas_venta WHERE preventista_id IS NULL OR preventista_id = ''")
    sin_preventista = cursor.fetchone()[0]
    print(f"⚠️ Notas sin preventista asignado: {sin_preventista}")
    
    if sin_preventista > 0:
        cursor.execute("SELECT numero_nota, fecha FROM notas_venta WHERE preventista_id IS NULL OR preventista_id = '' LIMIT 5")
        print("   Ejemplos:")
        for row in cursor.fetchall():
            print(f"      {row[0]} - {row[1]}")
    print()
    
    # 4. Notas por estado
    print("📋 NOTAS POR ESTADO:")
    cursor.execute("SELECT estado, COUNT(*) FROM notas_venta GROUP BY estado")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")
    print()
    
    # 5. Últimas 10 notas
    print("📋 ÚLTIMAS 10 NOTAS:")
    cursor.execute("""
        SELECT 
            n.numero_nota,
            n.fecha,
            n.total,
            n.estado,
            n.procesado_central,
            p.legajo
        FROM notas_venta n
        LEFT JOIN preventistas p ON n.preventista_id = p.id
        ORDER BY n.created_at DESC
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} | {row[1]} | ${row[2]:,.2f} | {row[3]} | Central: {row[4]} | Preventista: {row[5]}")
    print()
    
    # 6. Ver si hay filtros que ocultan las notas
    print("🔍 POSIBLES FILTROS QUE OCULTAN NOTAS:")
    print("   - Estado 'PROCESADO_CENTRAL' o 'FINALIZADO' puede ocultarlas")
    print("   - Filtro por fecha (solo muestra últimas X días)")
    print("   - Filtro por preventista (solo muestra del logueado)")
    print("   - Notas con procesado_central = 1 (ya subidas)")
    print()
    
    # 7. Verificar notas recientes
    cursor.execute("SELECT COUNT(*) FROM notas_venta WHERE fecha >= date('now', '-7 days')")
    recientes = cursor.fetchone()[0]
    print(f"📅 Notas de los últimos 7 días: {recientes}")
    
    conn.close()
    print("=" * 80)

if __name__ == '__main__':
    diagnosticar()
