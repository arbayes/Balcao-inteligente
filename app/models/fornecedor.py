"""
MODELO DE FORNECEDOR
Representa um fornecedor da Casa Guarani
"""

from datetime import datetime
from typing import Optional


class Fornecedor:
    """Modelo para fornecedores"""
    
    def __init__(
        self,
        nome: str,
        cnpj: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        produtos_fornecidos: Optional[str] = None,
        prazo_entrega: Optional[int] = None,  # em dias
        dias_entrega: Optional[str] = None,  # dias da semana separados por vírgula (0=Seg, 1=Ter, etc)
        forma_pagamento: Optional[str] = None,
        observacoes: Optional[str] = None,
        ativo: bool = True,
        data_cadastro: Optional[datetime] = None,
        ultima_compra: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        self.id = id
        self.nome = nome
        self.cnpj = cnpj
        self.telefone = telefone
        self.email = email
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.produtos_fornecidos = produtos_fornecidos
        self.prazo_entrega = prazo_entrega
        self.dias_entrega = dias_entrega
        self.forma_pagamento = forma_pagamento
        self.observacoes = observacoes
        self.ativo = ativo
        self.data_cadastro = data_cadastro or datetime.now()
        self.ultima_compra = ultima_compra
    
    def __repr__(self):
        return f"Fornecedor(id={self.id}, nome='{self.nome}', cnpj='{self.cnpj}')"
    
    def __str__(self):
        return f"{self.nome} - {self.cnpj or 'Sem CNPJ'}"
