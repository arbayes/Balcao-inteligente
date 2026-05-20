from datetime import datetime
from typing import Optional, List, Dict

class VendaFiada:
    """Modelo para vendas fiadas/crédito ao cliente"""
    
    def __init__(
        self,
        cliente_id: int,
        produtos: List[Dict],  # Lista de dicts: {"produto_id": int, "nome": str, "quantidade": int, "preco_unitario": float, "subtotal": float}
        valor_total: float,
        status: str = "PENDENTE",  # PENDENTE, PARCIAL, PAGO, INADIMPLENTE
        data_venda: Optional[datetime] = None,
        data_pagamento: Optional[datetime] = None,
        id: Optional[int] = None,
        notas: Optional[str] = None
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.produtos = produtos  # JSON string quando salvo no BD
        self.valor_total = valor_total
        self.status = status
        self.data_venda = data_venda or datetime.now()
        self.data_pagamento = data_pagamento
        self.notas = notas
