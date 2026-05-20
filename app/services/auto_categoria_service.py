"""
SERVIÇO DE AUTO-CATEGORIZAÇÃO
Detecta padrões em nomes de produtos e cria subcategorias automaticamente
"""

import re
from typing import Tuple, Optional

from app.database.categorias_repository import (
    obter_categoria_por_nome,
    inserir_categoria,
    listar_categorias
)


PADROES_VOLUME = [
    (r"(\d+)\s*ml", "{}ml"),
    (r"(\d+)\s*l\b", "{}L"),
    (r"(\d+)\s*lt\b", "{}L"),
    (r"(\d+)\s*litro", "{}L"),
    (r"(\d+)\s*x\s*(\d+)\s*ml", "{1}x{2}ml"),
    (r"pack\s+com\s+(\d+)", "Pack {1}"),
]

PADROES_TIPO = [
    (r"(premium|superior|extra|especial)", "{0}"),
    (r"(light|zero|diet)", "{0}"),
    (r"(nacional|importad)", "{0}"),
]


def extrair_padrao(nome_produto: str) -> Optional[Tuple[str, str]]:
    """
    Extrai padrão do nome do produto (ex: volume, tipo).

    Args:
        nome_produto (str): Nome do produto

    Returns:
        tuple: (subcategoria, padrão_encontrado) ou None
    """
    nome_lower = nome_produto.lower()

    # Verificar volumes
    for padrao, formato in PADROES_VOLUME:
        match = re.search(padrao, nome_lower)
        if match:
            grupos = match.groups()
            if len(grupos) == 1:
                subcategoria = formato.format(grupos[0])
            elif len(grupos) == 2:
                subcategoria = formato.format(grupos[0], grupos[1])
            else:
                subcategoria = formato.format(*grupos)
            return (subcategoria, "volume")

    # Verificar tipos
    for padrao, formato in PADROES_TIPO:
        match = re.search(padrao, nome_lower)
        if match:
            grupos = match.groups()
            subcategoria = formato.format(*grupos)
            return (subcategoria, "tipo")

    return None


def extrair_categoria_base(nome_produto: str) -> str:
    """
    Extrai a categoria base do nome (ex: 'Cerveja' de 'Cerveja Brahma 600ml').

    Args:
        nome_produto (str): Nome do produto

    Returns:
        str: Categoria base
    """
    nome = nome_produto.strip()
    
    # Tentar remover padrões de volume/tipo
    nome_sem_padrao = nome
    for padrao, _ in PADROES_VOLUME + PADROES_TIPO:
        nome_sem_padrao = re.sub(padrao, "", nome_sem_padrao, flags=re.IGNORECASE)
    
    # Pegar primeira palavra ou a parte antes de números
    parts = nome_sem_padrao.split()
    if parts:
        categoria_base = parts[0].strip()
        return categoria_base if categoria_base else "Geral"
    
    return "Geral"


def criar_subcategoria(categoria_pai: str, subcategoria_nome: str) -> bool:
    """
    Cria uma subcategoria se não existir.

    Args:
        categoria_pai (str): Nome da categoria pai
        subcategoria_nome (str): Nome da subcategoria

    Returns:
        bool: True se criado ou já existe
    """
    categoria_completa = f"{categoria_pai}/{subcategoria_nome}"
    
    # Verificar se já existe
    if obter_categoria_por_nome(categoria_completa):
        return True
    
    try:
        inserir_categoria(
            categoria_completa,
            f"Subcategoria de {categoria_pai}"
        )
        return True
    except Exception:
        return False


def obter_categoria_com_subcategoria(
    nome_produto: str,
    categoria_base_override: Optional[str] = None
) -> str:
    """
    Obtém categoria completa com subcategoria para um produto.

    Args:
        nome_produto (str): Nome do produto
        categoria_base_override (str, optional): Categoria base forçada

    Returns:
        str: Categoria completa (ex: "Cerveja/600ml" ou "Geral")
    """
    categoria_base = categoria_base_override or extrair_categoria_base(nome_produto)
    
    # Verificar se categoria base existe
    if not obter_categoria_por_nome(categoria_base):
        # Se não existe, retornar "Geral"
        if categoria_base != "Geral":
            categoria_base = "Geral"
    
    # Extrair padrão (subcategoria)
    resultado = extrair_padrao(nome_produto)
    if not resultado:
        return categoria_base
    
    subcategoria, _ = resultado
    
    # Tentar criar subcategoria
    if criar_subcategoria(categoria_base, subcategoria):
        return f"{categoria_base}/{subcategoria}"
    
    return categoria_base


def auto_categorizar_produto(nome_produto: str, categoria_sugerida: Optional[str] = None) -> str:
    """
    Retorna categoria automática para um produto.

    Args:
        nome_produto (str): Nome do produto
        categoria_sugerida (str, optional): Categoria sugerida (tem prioridade)

    Returns:
        str: Categoria recomendada
    """
    if categoria_sugerida and categoria_sugerida != "Geral":
        # Se uma categoria foi sugerida e não é Geral, usar ela como base
        return obter_categoria_com_subcategoria(nome_produto, categoria_sugerida)
    
    # Caso contrário, tentar detectar automaticamente
    return obter_categoria_com_subcategoria(nome_produto)
