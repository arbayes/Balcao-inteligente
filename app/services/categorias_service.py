"""
SERVIÇO DE CATEGORIAS
Lógica de negócio para categorias de produtos
"""

from app.database.categorias_repository import (
    criar_tabela_categorias,
    inserir_categoria,
    listar_categorias,
    obter_categoria_por_id,
    obter_categoria_por_nome,
    atualizar_categoria,
    ativar_categoria,
    deletar_categoria,
    contar_produtos_por_categoria
)


def criar_categorias_padrao():
    """Cria as categorias padrão se não existirem"""
    categorias_padrao = [
        ("Geral", "Categoria padrão para produtos sem classificação"),
        ("Bebidas Alcoólicas", "Cervejas, vinhos, destilados, etc."),
        ("Bebidas Não Alcoólicas", "Refrigerantes, sucos, água, energéticos"),
        ("Salgados", "Salgados fritos e assados, lanches"),
        ("Frios e Laticínios", "Queijos, presuntos, iogurtes, leite"),
        ("Mercearia", "Arroz, feijão, óleo, açúcar, temperos"),
        ("Pães e Confeitaria", "Pães, bolos, biscoitos"),
        ("Higiene e Limpeza", "Produtos de higiene pessoal e limpeza"),
        ("Congelados", "Carnes, sorvetes, produtos congelados"),
        ("Doces e Guloseimas", "Chocolates, balas, bombons"),
        ("Cigarros e Tabacaria", "Cigarros, isqueiros, etc.")
    ]
    
    for nome, descricao in categorias_padrao:
        if not obter_categoria_por_nome(nome):
            try:
                inserir_categoria(nome, descricao)
            except ValueError:
                pass  # Categoria já existe


def cadastrar_categoria(nome: str, descricao: str = None, margem_alvo: float = None) -> dict:
    """
    Cadastra uma nova categoria.
    
    Args:
        nome (str): Nome da categoria
        descricao (str, optional): Descrição da categoria
    
    Returns:
        dict: Resultado da operação
    
    Exemplo:
        resultado = cadastrar_categoria("Bebidas Quentes", "Café, chá, chocolate...")
        if resultado["sucesso"]:
            print(f"Categoria criada com ID: {resultado['categoria_id']}")
    """
    # Validações
    if not nome or not nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome da categoria não pode estar vazio."
        }
    
    if len(nome.strip()) > 50:
        return {
            "sucesso": False,
            "mensagem": "Nome da categoria não pode ter mais de 50 caracteres."
        }

    if margem_alvo is not None and margem_alvo < 0:
        return {
            "sucesso": False,
            "mensagem": "Margem alvo não pode ser negativa."
        }
    
    # Verificar se já existe
    if obter_categoria_por_nome(nome):
        return {
            "sucesso": False,
            "mensagem": f"Já existe uma categoria chamada '{nome}'."
        }
    
    try:
        categoria_id = inserir_categoria(nome, descricao, margem_alvo)
        return {
            "sucesso": True,
            "mensagem": f"Categoria '{nome}' criada com sucesso.",
            "categoria_id": categoria_id
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao criar categoria: {str(e)}"
        }


def obter_todas_categorias(ativas_apenas=True) -> list:
    """
    Obtém todas as categorias.
    
    Args:
        ativas_apenas (bool): Se True, retorna apenas categorias ativas
    
    Returns:
        list: Lista de categorias
    """
    return listar_categorias(ativas=ativas_apenas)


def obter_nomes_categorias(ativas_apenas=True) -> list:
    """
    Obtém lista de nomes de categorias (útil para combobox).
    
    Args:
        ativas_apenas (bool): Se True, retorna apenas categorias ativas
    
    Returns:
        list: Lista de nomes de categorias
    
    Exemplo:
        nomes = obter_nomes_categorias()
        # ['Geral', 'Carnes', 'Bebidas', ...]
    """
    categorias = listar_categorias(ativas=ativas_apenas)
    return [cat["nome"] for cat in categorias]


def editar_categoria(categoria_id: int, nome: str = None, descricao: str = None, margem_alvo: float = None) -> dict:
    """
    Edita uma categoria existente.
    
    Args:
        categoria_id (int): ID da categoria
        nome (str, optional): Novo nome
        descricao (str, optional): Nova descrição
    
    Returns:
        dict: Resultado da operação
    """
    categoria = obter_categoria_por_id(categoria_id)
    if not categoria:
        return {
            "sucesso": False,
            "mensagem": "Categoria não encontrada."
        }
    
    # Validações
    if nome and not nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome da categoria não pode estar vazio."
        }
    
    if nome and len(nome.strip()) > 50:
        return {
            "sucesso": False,
            "mensagem": "Nome da categoria não pode ter mais de 50 caracteres."
        }

    if margem_alvo is not None and margem_alvo < 0:
        return {
            "sucesso": False,
            "mensagem": "Margem alvo não pode ser negativa."
        }
    
    # Verificar se novo nome já existe (em outra categoria)
    if nome and nome != categoria["nome"]:
        if obter_categoria_por_nome(nome):
            return {
                "sucesso": False,
                "mensagem": f"Já existe uma categoria chamada '{nome}'."
            }
    
    try:
        atualizar_categoria(categoria_id, nome, descricao, margem_alvo)
        return {
            "sucesso": True,
            "mensagem": "Categoria atualizada com sucesso."
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao editar categoria: {str(e)}"
        }


def remover_categoria(categoria_id: int, forcado=False) -> dict:
    """
    Remove uma categoria definitivamente.
    
    Args:
        categoria_id (int): ID da categoria
        forcado (bool): Se True, move os produtos para "Geral" antes de apagar.
    
    Returns:
        dict: Resultado da operação
    """
    categoria = obter_categoria_por_id(categoria_id)
    if not categoria:
        return {
            "sucesso": False,
            "mensagem": "Categoria não encontrada."
        }
    
    # Verificar se é categoria padrão
    if categoria["nome"] == "Geral":
        return {
            "sucesso": False,
            "mensagem": "Não é possível remover a categoria 'Geral'."
        }
    
    # Contar produtos
    num_produtos = contar_produtos_por_categoria(categoria_id)
    
    if num_produtos > 0 and not forcado:
        return {
            "sucesso": False,
            "mensagem": (
                f"Esta categoria tem {num_produtos} produto(s). "
                "Para excluir de vez, os produtos precisam ser movidos para 'Geral'."
            ),
            "num_produtos": num_produtos
        }
    
    try:
        # Mantem os produtos consistentes caso algum item ainda referencie a categoria.
        from app.database.estoque_repository import atualizar_categoria_produtos
        atualizar_categoria_produtos(categoria["nome"], "Geral")
        deletar_categoria(categoria_id)
        
        return {
            "sucesso": True,
            "mensagem": f"Categoria '{categoria['nome']}' excluida de vez."
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao remover categoria: {str(e)}"
        }


def ativar_cat(categoria_id: int) -> dict:
    """Ativa uma categoria."""
    categoria = obter_categoria_por_id(categoria_id)
    if not categoria:
        return {
            "sucesso": False,
            "mensagem": "Categoria não encontrada."
        }
    
    ativar_categoria(categoria_id)
    return {
        "sucesso": True,
        "mensagem": f"Categoria '{categoria['nome']}' ativada."
    }
