"""
SERVIÇO DE IMPORTAÇÃO XML POR FORNECEDOR
Registra histórico de XML importados para cada fornecedor
"""

import os
from datetime import datetime
from typing import List, Dict

from app.database.fornecedor_xml_repository import (
    criar_tabela_fornecedor_xml_imports,
    registrar_importacao_fornecedor as registrar_importacao_repo,
    listar_importacoes_fornecedor as listar_importacoes_repo,
)


def garantir_tabela_importacoes():
    """Garante que a tabela de importações por fornecedor existe"""
    criar_tabela_fornecedor_xml_imports()


def registrar_importacao_fornecedor(
    fornecedor_id: int,
    caminho_arquivo: str,
    resultado: dict
) -> int:
    """Registra o resultado de uma importação XML para um fornecedor"""
    nome_arquivo = os.path.basename(caminho_arquivo)
    data_importacao = datetime.now().isoformat()

    avisos = resultado.get("avisos", []) or []
    comparacoes = resultado.get("comparacoes_preco", []) or []

    return registrar_importacao_repo(
        fornecedor_id=fornecedor_id,
        caminho_arquivo=caminho_arquivo,
        nome_arquivo=nome_arquivo,
        data_importacao=data_importacao,
        total_itens=resultado.get("itens_processados", 0),
        produtos_criados=resultado.get("produtos_criados", 0),
        produtos_atualizados=resultado.get("produtos_atualizados", 0),
        avisos="\n".join(avisos),
        comparacoes_preco="\n".join(comparacoes),
    )


def listar_importacoes_fornecedor(fornecedor_id: int) -> List[Dict]:
    """Lista importações XML de um fornecedor"""
    return listar_importacoes_repo(fornecedor_id)
