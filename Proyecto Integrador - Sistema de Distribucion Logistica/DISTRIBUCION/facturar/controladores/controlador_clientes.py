"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Clientes – Sincroniza con Turso incluyendo preventista_id
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from modelos.cliente import Cliente
from utilidades.central_sync import enviar_a_turso


class ControladorClientes:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.modelo = Cliente(db)

    def crear_cliente(self, razon_social: str, cuit: str = None,
                      condicion_iva: str = 'RI', domicilio: str = None,
                      telefono: str = None, email: str = None,
                      aplica_tasa: bool = False, limite_credito: float = 0.0,
                      preventista_id: int = None) -> int:
        if not razon_social or not razon_social.strip():
            raise ValueError("La razón social es obligatoria.")
        if cuit:
            cuit = cuit.strip()
            if self.modelo.buscar_por_cuit(cuit):
                raise ValueError("Ya existe un cliente con ese CUIT.")
        if condicion_iva not in ('RI', 'M', 'EX', 'CF', 'MT'):
            condicion_iva = 'RI'

        cliente_id = self.modelo.crear(
            razon_social=razon_social.strip(),
            cuit=cuit,
            condicion_iva=condicion_iva,
            domicilio=domicilio.strip() if domicilio else None,
            telefono=telefono.strip() if telefono else None,
            email=email.strip() if email else None,
            aplica_tasa_municipal=aplica_tasa,
            limite_credito=limite_credito
        )

        try:
            enviar_a_turso(
                """INSERT INTO clientes (id, razon_social, cuit, condicion_iva, domicilio,
                   telefono, email, aplica_tasa_municipal, limite_credito, 
                   saldo_cuenta_corriente, preventista_id, activo, 
                   created_at, updated_at, version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 1, ?, ?, 1)""",
                [cliente_id, razon_social.strip(), cuit, condicion_iva,
                 domicilio.strip() if domicilio else None,
                 telefono.strip() if telefono else None,
                 email.strip() if email else None,
                 int(aplica_tasa), limite_credito,
                 preventista_id,
                 datetime.now().isoformat(), datetime.now().isoformat()]
            )
        except Exception as e:
            print(f"⚠️ Error replicando cliente a Turso: {e}")

        return cliente_id

    def modificar_cliente(self, cliente_id: int, **campos) -> bool:
        if not cliente_id:
            raise ValueError("ID de cliente no proporcionado.")
        if 'cuit' in campos and campos['cuit']:
            nuevo_cuit = campos['cuit'].strip()
            existente = self.modelo.buscar_por_cuit(nuevo_cuit)
            if existente and existente['id'] != cliente_id:
                raise ValueError("El CUIT ya pertenece a otro cliente.")

        resultado = self.modelo.actualizar(cliente_id, **campos)

        if campos:
            set_clause = ", ".join(f"{col} = ?" for col in campos.keys())
            valores = list(campos.values())
            valores.append(cliente_id)
            try:
                enviar_a_turso(
                    f"UPDATE clientes SET {set_clause} WHERE id = ?",
                    valores
                )
            except Exception as e:
                print(f"⚠️ Error replicando modificación de cliente a Turso: {e}")

        return resultado

    def eliminar_cliente(self, cliente_id: int) -> bool:
        resultado = self.modelo.eliminar(cliente_id)
        try:
            enviar_a_turso(
                "UPDATE clientes SET activo = 0 WHERE id = ?",
                [cliente_id]
            )
        except Exception as e:
            print(f"⚠️ Error replicando eliminación de cliente a Turso: {e}")
        return resultado

    def obtener_cliente(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        return self.modelo.obtener_por_id(cliente_id)

    def listar_clientes(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        return self.modelo.listar_todos(solo_activos=solo_activos)

    def buscar_por_cuit(self, cuit: str) -> Optional[Dict[str, Any]]:
        return self.modelo.buscar_por_cuit(cuit)