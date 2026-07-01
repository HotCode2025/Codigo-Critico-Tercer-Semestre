#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Código Crítico - Tercer Semestre Año 2026
==================================================
FIX PARA controlador_ventas.py - Error HAVING
==================================================
📌 EJECUTAR: python fix_controlador_ventas.py
📌 FUNCIÓN: Corrige el error "HAVING clause on a non-aggregate query"
"""

import os
import re
import shutil
from datetime import datetime

RUTA_CONTROLADOR = "controladores/controlador_ventas.py"
RUTA_BACKUP = f"controladores/controlador_ventas.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

NUEVA_FUNCION = """    def obtener_facturas_pendientes_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        \"\"\"
        Obtiene facturas pendientes de cobro de un cliente.
        
        Args:
            cliente_id: UUID del cliente
        
        Returns:
            Lista de facturas pendientes
        \"\"\"
        cur = self.db.cursor()
        cur.execute(\"\"\"
            SELECT 
                f.id,
                f.numero_factura,
                f.fecha,
                f.total,
                f.saldo_anterior_cliente,
                COALESCE((
                    SELECT SUM(importe) 
                    FROM cuenta_corriente_movimientos 
                    WHERE referencia_id = f.id AND tipo_movimiento = 'COBRO'
                ), 0) as total_cobrado
            FROM facturas f
            WHERE f.cliente_id = ? AND f.estado = 'EMITIDA'
            ORDER BY f.fecha ASC
        \"\"\", (cliente_id,))
        
        resultados = []
        for row in cur.fetchall():
            saldo_pendiente = row['total'] - row['total_cobrado']
            if saldo_pendiente > 0:
                resultados.append({
                    'id': row['id'],
                    'numero_factura': row['numero_factura'],
                    'fecha': row['fecha'],
                    'total': row['total'],
                    'saldo_anterior_cliente': row['saldo_anterior_cliente'],
                    'saldo_pendiente': saldo_pendiente
                })
        
        return resultados"""

def aplicar_fix():
    """Aplica el fix al archivo controlador_ventas.py"""
    
    print("=" * 60)
    print("🔧 FIX PARA controlador_ventas.py - Error HAVING")
    print("=" * 60)
    
    if not os.path.exists(RUTA_CONTROLADOR):
        print(f"\n❌ ERROR: No se encontró {RUTA_CONTROLADOR}")
        return False
    
    print(f"\n📁 Archivo encontrado: {RUTA_CONTROLADOR}")
    
    # Crear backup
    print(f"\n📦 Creando backup: {RUTA_BACKUP}")
    shutil.copy2(RUTA_CONTROLADOR, RUTA_BACKUP)
    print("✅ Backup creado")
    
    with open(RUTA_CONTROLADOR, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar la función problemática
    patron = r'def obtener_facturas_pendientes_cliente\(self, cliente_id: str\) -> List\[Dict\[str, Any\]\]:.*?(?=\n    def |\n\n\n|$)'
    
    if re.search(patron, contenido, re.DOTALL):
        contenido_nuevo = re.sub(patron, NUEVA_FUNCION, contenido, flags=re.DOTALL)
        
        with open(RUTA_CONTROLADOR, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print("\n✅ FIX APLICADO CORRECTAMENTE")
        print("   La función obtener_facturas_pendientes_cliente fue corregida")
        print("   Se creó un backup en:", RUTA_BACKUP)
        return True
    else:
        print("\n⚠️ No se encontró la función obtener_facturas_pendientes_cliente")
        return False

def revertir_fix():
    """Revertir el fix (restaurar backup)"""
    backups = [f for f in os.listdir("controladores/") if f.startswith("controlador_ventas.py.backup_")]
    
    if not backups:
        print("❌ No hay backups disponibles")
        return False
    
    print("\n📦 Backups disponibles:")
    for i, b in enumerate(backups):
        print(f"   {i+1}. {b}")
    
    try:
        seleccion = int(input("\nSelecciona el backup a restaurar (número): ")) - 1
        if 0 <= seleccion < len(backups):
            backup_path = os.path.join("controladores/", backups[seleccion])
            shutil.copy2(backup_path, RUTA_CONTROLADOR)
            print(f"✅ Restaurado: {backups[seleccion]}")
            return True
    except:
        print("❌ Selección inválida")
    
    return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   FIX PARA controlador_ventas.py - Código Crítico 2026")
    print("=" * 60)
    print("\n📌 Este script corrige el error:")
    print("   'HAVING clause on a non-aggregate query'")
    print("\n   Selecciona una opción:")
    print("   1. Aplicar fix")
    print("   2. Revertir fix (restaurar backup)")
    print("   3. Salir")
    
    opcion = input("\nOpción: ").strip()
    
    if opcion == "1":
        aplicar_fix()
    elif opcion == "2":
        revertir_fix()
    else:
        print("Saliendo...")