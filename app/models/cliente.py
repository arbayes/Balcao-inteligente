from datetime import datetime
from typing import Optional

class Cliente:
    def __init__(
        self,
        nome: str,
        cpf: str,
        telefone: Optional[str] = None,
        email: Optional[str] = None,
        endereco: Optional[str] = None,
        id: Optional[int] = None,
        ativo: bool = True,
        vip: bool = False,
        data_cadastro: Optional[datetime] = None,
        data_ultima_compra: Optional[datetime] = None,
        valor_total_gasto: float = 0.0
    ):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email
        self.endereco = endereco
        self.ativo = ativo
        self.vip = vip
        self.data_cadastro = data_cadastro or datetime.now()
        self.data_ultima_compra = data_ultima_compra
        self.valor_total_gasto = valor_total_gasto
        