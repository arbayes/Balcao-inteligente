class Produto:
    def __init__(self, nome, sku, preco_compra, preco_venda, quantidade=0, id=None, ativo=True, descricao=None, categoria="Geral", margem_alvo=None):
        self.id = id
        self.nome = nome
        self.sku = sku
        self.descricao = descricao
        self.preco_compra = preco_compra
        self.preco_venda = preco_venda
        self.quantidade = quantidade
        self.ativo = ativo
        self.categoria = categoria
        self.margem_alvo = margem_alvo
    
    @property
    def margem_lucro(self) -> float:
        """
        Calcula automaticamente a porcentagem de lucro baseada nos preços de compra e venda.
        
        Returns:
            float: Porcentagem de lucro (ex: 50.0 para 50%)
        """
        if self.preco_compra <= 0:
            return 0.0
        
        lucro = ((self.preco_venda - self.preco_compra) / self.preco_compra) * 100
        return round(lucro, 2)
