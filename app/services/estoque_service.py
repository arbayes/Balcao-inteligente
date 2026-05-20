from app.database.estoque_repository import (
    criar_tabela_estoque,
    inserir_produto,
    listar_produtos,
    obter_produto_por_id,
    atualizar_produto,
    aumentar_quantidade,
    diminuir_quantidade,
    desativar_produto,
    reativar_produto
)
from app.models.produto import Produto


def cadastrar_produto(nome: str, sku: str, preco_compra: float, preco_venda: float, quantidade: int = 0, descricao: str = None, categoria: str = "Geral", margem_alvo: float = None) -> dict:
    """
    Cadastra um novo produto no estoque.
    
    Args:
        nome (str): Nome do produto
        sku (str): SKU único do produto
        preco_compra (float): Preço de compra do produto
        preco_venda (float): Preço de venda do produto
        quantidade (int, optional): Quantidade inicial (padrão: 0)
        descricao (str, optional): Descrição do produto
        categoria (str, optional): Categoria do produto (padrão: "Geral")
    
    Returns:
        dict: Resultado da operação com sucesso, mensagem e margem de lucro
    
    Exemplos:
        cadastrar_produto("Carne Vermelha", "CARNE01", 15.00, 35.90, 50, categoria="Carnes")
        cadastrar_produto("Refrigerante", "REFR01", 2.50, 5.90, categoria="Bebidas")
    """
    # Validações
    if not nome or not nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome do produto não pode estar vazio."
        }
    
    if not sku or not sku.strip():
        return {
            "sucesso": False,
            "mensagem": "Código do Produto não pode estar vazio."
        }
    
    if preco_compra < 0:
        return {
            "sucesso": False,
            "mensagem": "Preço de compra não pode ser negativo."
        }
    
    if preco_venda < 0:
        return {
            "sucesso": False,
            "mensagem": "Preço de venda não pode ser negativo."
        }
    
    if quantidade < 0:
        return {
            "sucesso": False,
            "mensagem": "Quantidade não pode ser negativa."
        }

    if margem_alvo is not None and margem_alvo < 0:
        return {
            "sucesso": False,
            "mensagem": "Margem alvo não pode ser negativa."
        }
    
    try:
        produto = Produto(
            nome=nome.strip(),
            sku=sku.strip(),
            preco_compra=preco_compra,
            preco_venda=preco_venda,
            quantidade=quantidade,
            descricao=descricao.strip() if descricao else None,
            categoria=categoria.strip() if categoria else "Geral",
            margem_alvo=margem_alvo
        )
        inserir_produto(produto)
        
        return {
            "sucesso": True,
            "mensagem": f"Produto '{nome}' cadastrado com sucesso.",
            "margem_lucro": produto.margem_lucro
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cadastrar produto: {str(e)}"
        }


def buscar_produtos(termo: str = None, campo: str = None) -> list:
    """
    Busca produtos ativos de forma moderna e flexível.
    
    Args:
        termo (str, optional): Termo para buscar (busca em todos os campos por padrão)
        campo (str, optional): Campo específico (nome, sku, descricao)
    
    Returns:
        list: Lista de produtos com id, nome, sku, descricao, preco_compra, preco_venda, quantidade, margem_lucro, ativo
    
    Exemplos:
        buscar_produtos()  # Retorna todos os produtos ativos
        buscar_produtos("Notebook")  # Busca por nome, sku ou descrição
        buscar_produtos("NB001", "sku")  # Busca específica por SKU
    """
    produtos = listar_produtos(busca=termo, filtro_por=campo)
    
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "sku": p.sku,
            "descricao": p.descricao,
            "preco_compra": p.preco_compra,
            "preco_venda": p.preco_venda,
            "quantidade": p.quantidade,
            "categoria": p.categoria,
            "margem_alvo": p.margem_alvo,
            "margem_lucro": p.margem_lucro,
            "ativo": p.ativo
        }
        for p in produtos
    ]


def obter_produto(produto_id: int) -> dict:
    """
    Obtém um produto específico pelo ID.
    
    Args:
        produto_id (int): ID do produto
    
    Returns:
        dict: Dados do produto ou None se não encontrado
    
    Exemplo:
        produto = obter_produto(1)
    """
    produto = obter_produto_por_id(produto_id)
    
    if produto:
        return {
            "id": produto.id,
            "nome": produto.nome,
            "sku": produto.sku,
            "descricao": produto.descricao,
            "preco_compra": produto.preco_compra,
            "preco_venda": produto.preco_venda,
            "quantidade": produto.quantidade,
            "categoria": produto.categoria,
            "margem_alvo": produto.margem_alvo,
            "margem_lucro": produto.margem_lucro,
            "ativo": produto.ativo
        }
    return None


def editar_produto(produto_id: int, nome: str = None, sku: str = None, descricao: str = None, preco_compra: float = None, preco_venda: float = None, quantidade: int = None, categoria: str = None, margem_alvo: float = None) -> dict:
    """
    Edita dados de um produto existente.
    
    Args:
        produto_id (int): ID do produto
        nome (str, optional): Novo nome
        sku (str, optional): Novo SKU
        descricao (str, optional): Nova descrição
        preco_compra (float, optional): Novo preço de compra
        preco_venda (float, optional): Novo preço de venda
        quantidade (int, optional): Nova quantidade
        categoria (str, optional): Nova categoria
    
    Returns:
        dict: Resultado da operação com sucesso, mensagem e nova margem de lucro (se preços foram alterados)
    
    Exemplos:
        editar_produto(1, nome="Notebook Gamer")
        editar_produto(1, preco_venda=3499.99, quantidade=10, categoria="Eletrônicos")
    """
    if not any([nome, sku, descricao, preco_compra is not None, preco_venda is not None, quantidade is not None, categoria, margem_alvo is not None]):
        return {
            "sucesso": False,
            "mensagem": "Nenhum campo para atualizar foi fornecido."
        }
    
    # Validações básicas
    if nome and not nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome não pode estar vazio."
        }
    
    if sku and not sku.strip():
        return {
            "sucesso": False,
            "mensagem": "Código do Produto não pode estar vazio."
        }
    
    if preco_compra is not None and preco_compra < 0:
        return {
            "sucesso": False,
            "mensagem": "Preço de compra não pode ser negativo."
        }
    
    if preco_venda is not None and preco_venda < 0:
        return {
            "sucesso": False,
            "mensagem": "Preço de venda não pode ser negativo."
        }
    
    if quantidade is not None and quantidade < 0:
        return {
            "sucesso": False,
            "mensagem": "Quantidade não pode ser negativa."
        }

    if margem_alvo is not None and margem_alvo < 0:
        return {
            "sucesso": False,
            "mensagem": "Margem alvo não pode ser negativa."
        }
    
    sucesso = atualizar_produto(
        produto_id,
        nome.strip() if nome else None,
        sku.strip() if sku else None,
        descricao.strip() if descricao else None,
        preco_compra,
        preco_venda,
        quantidade,
        categoria.strip() if categoria else None,
        margem_alvo
    )
    
    if sucesso:
        # Obter produto atualizado para retornar a margem de lucro
        produto_atualizado = obter_produto(produto_id)
        margem_lucro = produto_atualizado.get("margem_lucro") if produto_atualizado else None
        
        resultado = {
            "sucesso": True,
            "mensagem": "Produto atualizado com sucesso."
        }
        
        if margem_lucro is not None:
            resultado["margem_lucro"] = margem_lucro
        
        return resultado
    else:
        return {
            "sucesso": False,
            "mensagem": "Produto não encontrado ou não foi possível atualizar."
        }


def entrada_estoque(produto_id: int, quantidade: int) -> dict:
    """
    Registra uma entrada de produtos no estoque.
    
    Args:
        produto_id (int): ID do produto
        quantidade (int): Quantidade a adicionar
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplo:
        entrada_estoque(1, 50)  # Adiciona 50 unidades ao produto 1
    """
    if quantidade <= 0:
        return {
            "sucesso": False,
            "mensagem": "Quantidade deve ser maior que zero."
        }
    
    sucesso = aumentar_quantidade(produto_id, quantidade)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": f"Entrada de {quantidade} unidade(s) registrada com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Produto não encontrado."
        }


def saida_estoque(produto_id: int, quantidade: int) -> dict:
    """
    Registra uma saída de produtos do estoque.
    
    Args:
        produto_id (int): ID do produto
        quantidade (int): Quantidade a remover
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplo:
        saida_estoque(1, 5)  # Remove 5 unidades do produto 1
    """
    if quantidade <= 0:
        return {
            "sucesso": False,
            "mensagem": "Quantidade deve ser maior que zero."
        }
    
    sucesso = diminuir_quantidade(produto_id, quantidade)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": f"Saída de {quantidade} unidade(s) registrada com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Produto não encontrado ou quantidade insuficiente em estoque."
        }


def deletar_produto(produto_id: int) -> dict:
    """
    Deleta um produto (soft delete - apenas desativa).
    
    Args:
        produto_id (int): ID do produto
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplo:
        deletar_produto(1)
    """
    sucesso = desativar_produto(produto_id)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": "Produto deletado com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Produto não encontrado ou já foi deletado."
        }


def reativar_produto_service(produto_id: int) -> dict:
    """
    Reativa um produto que foi deletado.
    
    Args:
        produto_id (int): ID do produto
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplo:
        reativar_produto_service(1)
    """
    sucesso = reativar_produto(produto_id)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": "Produto reativado com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Produto não encontrado ou já está ativo."
        }
