"""
Código Crítico - Tercer Semestre Año 2026
==================================================
PARTE 7.7: Controlador de Cheques con UUID
==================================================
📌 USO: Gestiona cheques con consulta al BCRA
📌 CARACTERÍSTICAS:
    - CRUD completo con UUID
    - Estados: EN_CARTERA, DEPOSITADO, VENDIDO, ACREDITADO, RECHAZADO
    - Consulta al BCRA (pendiente implementación completa)
"""

import requests
from typing import List, Dict, Any, Optional

from modelos.cheque import Cheque
from modelos.cliente import Cliente


class ControladorCheques:
    """
    Controlador para gestionar cheques.
    
    Ejemplo:
        ctrl = ControladorCheques(db)
        cheque_id = ctrl.crear_cheque(...)
    """
    
    BCRA_API_CHEQUES = "https://api.bcra.gob.ar/cheques/v1.0"
    
    def __init__(self, db):
        """Inicializa el controlador de cheques"""
        self.db = db
        self.modelo = Cheque(db)
        self.cliente_modelo = Cliente(db)
    
    def crear_cheque(self, cobro_id: str, cliente_id: str, banco: str,
                     numero_cheque: str, fecha_emision: str, fecha_vencimiento: str,
                     importe: float, factura_ids: str = None, observaciones: str = None) -> str:
        """
        Registra un nuevo cheque en cartera.
        
        Returns:
            str: UUID del cheque creado
        """
        if importe <= 0:
            raise ValueError("El importe del cheque debe ser positivo.")
        
        # Verificar si ya existe un cheque con el mismo número
        existente = self.modelo.obtener_por_numero(numero_cheque)
        if existente:
            raise ValueError(f"Ya existe un cheque con el número {numero_cheque}.")
        
        return self.modelo.crear(
            cobro_id=cobro_id,
            cliente_id=cliente_id,
            banco=banco,
            numero_cheque=numero_cheque,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            importe=importe,
            factura_ids=factura_ids,
            observaciones=observaciones
        )
    
    def listar_en_cartera(self) -> List[Dict[str, Any]]:
        """Lista cheques en cartera"""
        return self.modelo.listar_en_cartera()
    
    def listar_vendidos(self) -> List[Dict[str, Any]]:
        """Lista cheques vendidos"""
        return self.modelo.listar_vendidos()
    
    def listar_por_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Lista cheques de un cliente"""
        return self.modelo.listar_por_cliente(cliente_id)
    
    def acreditar(self, cheque_id: str, fecha_acreditacion: str) -> bool:
        """Marca un cheque como acreditado"""
        return self.modelo.acreditar(cheque_id, fecha_acreditacion)
    
    def vender(self, cheque_id: str, vendido_a: str) -> bool:
        """Marca un cheque como vendido"""
        return self.modelo.vender(cheque_id, vendido_a)
    
    def rechazar(self, cheque_id: str, observaciones: str = None) -> bool:
        """Marca un cheque como rechazado"""
        return self.modelo.rechazar(cheque_id, observaciones)
    
    # ============================================================
    # CONSULTA BCRA
    # ============================================================
    
    def consultar_cheque_bcra(self, codigo_entidad: int, numero_cheque: str) -> Optional[Dict[str, Any]]:
        """
        Consulta si un cheque fue denunciado en el BCRA.
        
        Args:
            codigo_entidad: Código de la entidad bancaria (ej: 14 para Banco Provincia)
            numero_cheque: Número completo del cheque
        
        Returns:
            Dict con datos de la denuncia, o None si no fue denunciado
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
    
    def verificar_cheques_en_cartera(self) -> List[Dict[str, Any]]:
        """
        Verifica todos los cheques en cartera contra el BCRA.
        
        Returns:
            Lista de cheques con alertas
        """
        cheques = self.listar_en_cartera()
        alertas = []
        
        for cheque in cheques:
            # Aquí se debería obtener el código de entidad desde el banco
            # Por ahora, solo se muestra un mensaje informativo
            alertas.append({
                'cheque': cheque,
                'mensaje': 'Consulta BCRA no implementada completamente',
                'estado': 'PENDIENTE'
            })
        
        return alertas