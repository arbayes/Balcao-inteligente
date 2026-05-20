"""
MODELO DE COMPRA DE FORNECEDOR
Representa uma compra/pedido realizado a um fornecedor
"""

from datetime import datetime
from typing import Optional, List


class ItemCompra:
    """Representa um item de uma compra"""
    
    def __init__(
        self,
        produto_id: int,
        produto_nome: str,
        quantidade: int,
        preco_unitario: float,
        id: Optional[int] = None
    ):
        self.id = id
        self.produto_id = produto_id
        self.produto_nome = produto_nome
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
    
    @property
    def subtotal(self) -> float:
        return self.quantidade * self.preco_unitario
    
    def __repr__(self):
        return f"ItemCompra(produto={self.produto_nome}, qtd={self.quantidade})"


class CompraFornecedor:
    """Modelo para compras/pedidos de fornecedores"""
    
    def __init__(
        self,
        fornecedor_id: int,
        data_pedido: Optional[datetime] = None,
        data_entrega_esperada: Optional[datetime] = None,
        data_entrega_real: Optional[datetime] = None,
        itens: Optional[List[ItemCompra]] = None,
        valor_total: float = 0.0,
        status: str = "PENDENTE",  # PENDENTE, ENTREGUE, CANCELADA
        forma_pagamento: Optional[str] = None,
        data_pagamento_esperada: Optional[datetime] = None,
        data_pagamento_real: Optional[datetime] = None,
        pago: bool = False,
        observacoes: Optional[str] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.fornecedor_id = fornecedor_id
        self.data_pedido = data_pedido or datetime.now()
        self.data_entrega_esperada = data_entrega_esperada
        self.data_entrega_real = data_entrega_real
        self.itens = itens or []
        self.valor_total = valor_total if valor_total else sum(item.subtotal for item in self.itens)
        self.status = status
        self.forma_pagamento = forma_pagamento
        self.data_pagamento_esperada = data_pagamento_esperada
        self.data_pagamento_real = data_pagamento_real
        self.pago = pago
        self.observacoes = observacoes
    
    def adicionar_item(self, item: ItemCompra):
        """Adiciona um item à compra"""
        self.itens.append(item)
        self._atualizar_valor_total()
    
    def remover_item(self, item_id: int):
        """Remove um item da compra"""
        self.itens = [item for item in self.itens if item.id != item_id]
        self._atualizar_valor_total()
    
    def _atualizar_valor_total(self):
        """Atualiza o valor total da compra"""
        self.valor_total = sum(item.subtotal for item in self.itens)
    
    def __repr__(self):
        return f"CompraFornecedor(fornecedor_id={self.fornecedor_id}, status={self.status}, valor={self.valor_total})"
