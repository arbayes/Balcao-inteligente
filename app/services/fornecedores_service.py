"""
SERVIÇO DE FORNECEDORES
Lógica de negócio para gerenciamento de fornecedores
"""

from typing import List, Optional
from app.models.fornecedor import Fornecedor
from app.database.fornecedores_repository import (
    inserir_fornecedor,
    listar_fornecedores,
    obter_fornecedor_por_id,
    atualizar_fornecedor,
    deletar_fornecedor,
    ativar_fornecedor,
    buscar_fornecedores
)


def cadastrar_fornecedor(fornecedor: Fornecedor) -> dict:
    """
    Cadastra um novo fornecedor com validações.
    
    Args:
        fornecedor (Fornecedor): Dados do fornecedor
    
    Returns:
        dict: Resultado da operação
    """
    # Validações
    if not fornecedor.nome or not fornecedor.nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome do fornecedor é obrigatório."
        }
    
    if len(fornecedor.nome.strip()) < 3:
        return {
            "sucesso": False,
            "mensagem": "Nome deve ter pelo menos 3 caracteres."
        }
    
    # CNPJ, email, telefone, endereço, cidade e estado são opcionais
    # Validar CNPJ se fornecido
    if fornecedor.cnpj and fornecedor.cnpj.strip():
        cnpj_limpo = ''.join(filter(str.isdigit, fornecedor.cnpj))
        if cnpj_limpo and len(cnpj_limpo) != 14:
            return {
                "sucesso": False,
                "mensagem": "CNPJ deve ter 14 dígitos."
            }
    
    # Validar email se fornecido
    if fornecedor.email and fornecedor.email.strip():
        if '@' not in fornecedor.email or '.' not in fornecedor.email:
            return {
                "sucesso": False,
                "mensagem": "Email inválido."
            }
    
    try:
        fornecedor_id = inserir_fornecedor(fornecedor)
        return {
            "sucesso": True,
            "mensagem": f"Fornecedor '{fornecedor.nome}' cadastrado com sucesso!",
            "fornecedor_id": fornecedor_id
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cadastrar fornecedor: {str(e)}"
        }


def editar_fornecedor(fornecedor: Fornecedor) -> dict:
    """
    Edita um fornecedor existente.
    
    Args:
        fornecedor (Fornecedor): Dados atualizados do fornecedor
    
    Returns:
        dict: Resultado da operação
    """
    if not fornecedor.id:
        return {
            "sucesso": False,
            "mensagem": "ID do fornecedor não informado."
        }
    
    # Validações
    if not fornecedor.nome or not fornecedor.nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome do fornecedor é obrigatório."
        }
    
    try:
        sucesso = atualizar_fornecedor(fornecedor)
        if sucesso:
            return {
                "sucesso": True,
                "mensagem": f"Fornecedor '{fornecedor.nome}' atualizado com sucesso!"
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Fornecedor não encontrado."
            }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao atualizar fornecedor: {str(e)}"
        }


def remover_fornecedor(fornecedor_id: int) -> dict:
    """
    Remove (desativa) um fornecedor.
    
    Args:
        fornecedor_id (int): ID do fornecedor
    
    Returns:
        dict: Resultado da operação
    """
    try:
        sucesso = deletar_fornecedor(fornecedor_id)
        if sucesso:
            return {
                "sucesso": True,
                "mensagem": "Fornecedor desativado com sucesso!"
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Fornecedor não encontrado."
            }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao remover fornecedor: {str(e)}"
        }


def reativar_fornecedor(fornecedor_id: int) -> dict:
    """
    Reativa um fornecedor desativado.
    
    Args:
        fornecedor_id (int): ID do fornecedor
    
    Returns:
        dict: Resultado da operação
    """
    try:
        sucesso = ativar_fornecedor(fornecedor_id)
        if sucesso:
            return {
                "sucesso": True,
                "mensagem": "Fornecedor reativado com sucesso!"
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Fornecedor não encontrado."
            }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao reativar fornecedor: {str(e)}"
        }


def obter_todos_fornecedores(incluir_inativos: bool = False) -> List[Fornecedor]:
    """
    Obtém lista de todos os fornecedores.
    
    Args:
        incluir_inativos (bool): Se True, inclui fornecedores inativos
    
    Returns:
        List[Fornecedor]: Lista de fornecedores
    """
    if incluir_inativos:
        return listar_fornecedores(ativo=None)
    else:
        return listar_fornecedores(ativo=True)


def pesquisar_fornecedores(termo: str) -> List[Fornecedor]:
    """
    Pesquisa fornecedores por nome, CNPJ ou produtos.
    
    Args:
        termo (str): Termo de busca
    
    Returns:
        List[Fornecedor]: Lista de fornecedores encontrados
    """
    if not termo or not termo.strip():
        return obter_todos_fornecedores()
    
    return buscar_fornecedores(termo.strip())


def obter_fornecedor(fornecedor_id: int) -> Optional[Fornecedor]:
    """
    Obtém um fornecedor específico por ID.
    
    Args:
        fornecedor_id (int): ID do fornecedor
    
    Returns:
        Optional[Fornecedor]: Fornecedor ou None
    """
    return obter_fornecedor_por_id(fornecedor_id)


def gerar_relatorio_fornecedores() -> dict:
    """
    Gera relatório estatístico de fornecedores.
    
    Returns:
        dict: Estatísticas dos fornecedores
    """
    todos_fornecedores = listar_fornecedores(ativo=None)
    ativos = [f for f in todos_fornecedores if f.ativo]
    inativos = [f for f in todos_fornecedores if not f.ativo]
    
    com_ultima_compra = [f for f in ativos if f.ultima_compra]
    sem_ultima_compra = [f for f in ativos if not f.ultima_compra]
    
    return {
        "total_fornecedores": len(todos_fornecedores),
        "ativos": len(ativos),
        "inativos": len(inativos),
        "com_ultima_compra": len(com_ultima_compra),
        "sem_ultima_compra": len(sem_ultima_compra),
        "fornecedores": todos_fornecedores
    }
