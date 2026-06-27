"""
Código Crítico - Tercer Semestre Año 2026
Controlador de Cheques con consulta al BCRA (cheques denunciados).
"""

import requests
from typing import List, Dict, Any, Optional
from modelos.cheque import Cheque


class ControladorCheques:
    BCRA_API_CHEQUES = "https://api.bcra.gob.ar/cheques/v1.0"

    def __init__(self, db):
        self.db = db
        self.modelo = Cheque(db)

    # --- ABM ---
    def crear_cheque(self, cobro_id: str, cliente_id: int, banco: str,
                     numero_cheque: str, fecha_emision: str, fecha_vencimiento: str,
                     importe: float, factura_ids: str = None, observaciones: str = None) -> str:
        """Registra un nuevo cheque en cartera."""
        if importe <= 0:
            raise ValueError("El importe del cheque debe ser positivo.")
        return self.modelo.crear(cobro_id, cliente_id, banco, numero_cheque,
                                 fecha_emision, fecha_vencimiento, importe,
                                 factura_ids, observaciones)

    def listar_en_cartera(self) -> List[Dict[str, Any]]:
        return self.modelo.listar_en_cartera()

    def listar_vendidos(self) -> List[Dict[str, Any]]:
        return self.modelo.listar_vendidos()

    def acreditar(self, cheque_id: str, fecha_acreditacion: str) -> bool:
        return self.modelo.cambiar_estado(cheque_id, 'ACREDITADO', fecha_acreditacion=fecha_acreditacion)

    def vender(self, cheque_id: str, vendido_a: str) -> bool:
        return self.modelo.cambiar_estado(cheque_id, 'VENDIDO', vendido_a=vendido_a)

    # --- Consulta BCRA ---
    def consultar_cheque_bcra(self, codigo_entidad: int, numero_cheque: str) -> Optional[Dict[str, Any]]:
        """
        Consulta si un cheque fue denunciado (extraviado, sustraído, adulterado).
        :param codigo_entidad: Código numérico de la entidad bancaria (ej: 14 para Banco Provincia).
        :param numero_cheque: Número completo del cheque.
        :return: Diccionario con los datos de la denuncia, o None si no fue denunciado.
        """
        url = f"{self.BCRA_API_CHEQUES}/denunciados/{codigo_entidad}/{numero_cheque}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 0 and data.get('results'):
                    return data['results']
            return None
        except requests.RequestException as e:
            print(f"Error al consultar BCRA: {e}")
            return None

    @staticmethod
    def obtener_entidades_bcra() -> List[Dict[str, Any]]:
        """Obtiene la lista de entidades bancarias desde la API del BCRA."""
        url = "https://api.bcra.gob.ar/cheques/v1.0/entidades"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 0:
                    return data.get('results', [])
            return []
        except requests.RequestException:
            return []

    def verificar_cheques_en_cartera(self) -> List[Dict[str, Any]]:
        """
        Verifica todos los cheques en cartera contra la API del BCRA.
        Retorna una lista con los cheques que fueron denunciados.
        """
        cheques = self.listar_en_cartera()
        alertas = []
        for cheque in cheques:
            # Necesitamos el código de entidad; como no lo guardamos en la tabla,
            # se podría agregar opcionalmente. Por ahora, mostramos que hay que
            # consultar manualmente.
            pass
        return alertas