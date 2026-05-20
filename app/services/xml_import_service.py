"""
SERVIÇO DE IMPORTAÇÃO XML (NF-e)
Parseia XML de nota fiscal e cadastra/atualiza produtos no estoque
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional, Tuple

from app.models.produto import Produto
from app.database.estoque_repository import (
    obter_produto_por_sku,
    obter_produto_por_sku_inativo,
    inserir_produto,
    aumentar_quantidade,
    atualizar_produto,
    reativar_produto
)
from app.database.categorias_repository import obter_margem_categoria_por_nome
from app.services.auto_categoria_service import auto_categorizar_produto

DEFAULT_MARGEM_ALVO = 0.30


def _parse_float(valor: Optional[str]) -> Optional[float]:
    if valor is None:
        return None
    try:
        return float(str(valor).replace(",", "."))
    except Exception:
        return None


def _find_text(node: ET.Element, tag: str) -> Optional[str]:
    if node is None:
        return None
    for child in node.iter():
        if child.tag.endswith(tag):
            return child.text
    return None


def _extrair_itens_nfe(root: ET.Element) -> List[ET.Element]:
    return root.findall(".//{*}det")


def importar_nfe_xml(
    caminho_xml: str,
    auto_atualizar_preco_venda: bool = False,
    margem_alvo: Optional[float] = None,
    auto_categorizar: bool = False,
    unidades_por_embalagem: Optional[int] = None
) -> dict:
    """
    Importa XML de NF-e e adiciona/atualiza produtos no estoque.
    
    Args:
        unidades_por_embalagem: Se informado, divide o preço e multiplica a quantidade
                                (ex: 24 unidades por caixa)
    
    Returns:
        dict: Resultado da importação
    """
    if not caminho_xml or not os.path.exists(caminho_xml):
        return {
            "sucesso": False,
            "mensagem": "Arquivo XML não encontrado."
        }
    
    try:
        tree = ET.parse(caminho_xml)
        root = tree.getroot()
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao ler XML: {str(e)}"
        }
    
    itens = _extrair_itens_nfe(root)
    if not itens:
        return {
            "sucesso": False,
            "mensagem": "Nenhum item encontrado no XML."
        }
    
    itens_processados = 0
    produtos_criados = 0
    produtos_atualizados = 0
    avisos = []
    comparacoes_preco = []
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    for idx, det in enumerate(itens, start=1):
        prod = det.find(".//{*}prod")
        if prod is None:
            avisos.append(f"Item {idx}: bloco <prod> não encontrado.")
            continue
        
        sku = _find_text(prod, "cProd") or _find_text(prod, "cEAN")
        nome = _find_text(prod, "xProd")
        q_com = _find_text(prod, "qCom") or _find_text(prod, "qTrib")
        v_un = _find_text(prod, "vUnCom") or _find_text(prod, "vUnTrib")
        v_total = _find_text(prod, "vProd")
        
        if not sku:
            sku = f"XML-{timestamp}-{idx:03d}"
            avisos.append(f"Item {idx}: SKU ausente, gerado {sku}.")
        
        if not nome:
            nome = f"Produto {sku}"
            avisos.append(f"Item {idx}: nome ausente, usado '{nome}'.")
        
        quantidade = _parse_float(q_com) or 0.0
        if quantidade <= 0:
            avisos.append(f"Item {idx}: quantidade inválida ({q_com}).")
            continue
        
        quantidade_int = int(round(quantidade))
        if abs(quantidade - quantidade_int) > 0.0001:
            avisos.append(
                f"Item {idx}: quantidade {quantidade} arredondada para {quantidade_int}."
            )
        
        preco_unitario = _parse_float(v_un)
        if preco_unitario is None:
            v_total_float = _parse_float(v_total) or 0.0
            if quantidade_int > 0:
                preco_unitario = v_total_float / quantidade_int
        preco_unitario = max(preco_unitario or 0.0, 0.0)
        
        # Calcular preço unitário se especificado unidades por embalagem
        if unidades_por_embalagem and unidades_por_embalagem > 0:
            preco_unitario = preco_unitario / unidades_por_embalagem
            quantidade_int = quantidade_int * unidades_por_embalagem
            avisos.append(
                f"Item {idx}: Calculado preço unitário (R$ {preco_unitario:.2f}) "
                f"com {unidades_por_embalagem} un/embalagem. Total: {quantidade_int} unidades."
            )
        
        # Verificar se produto existe (ativo ou inativo)
        produto_existente = obter_produto_por_sku(sku.strip())
        produto_inativo = None
        if not produto_existente:
            produto_inativo = obter_produto_por_sku_inativo(sku.strip())
        
        if produto_existente:
            # Atualiza estoque
            aumentar_quantidade(produto_existente.id, quantidade_int)

            # Comparação de preço de compra
            preco_compra_atual = produto_existente.preco_compra
            if abs(preco_compra_atual - preco_unitario) > 0.0001:
                if preco_compra_atual > 0:
                    variacao = ((preco_unitario - preco_compra_atual) / preco_compra_atual) * 100
                else:
                    variacao = None

                margem_atual = None
                if produto_existente.preco_compra and produto_existente.preco_compra > 0:
                    margem_atual = (produto_existente.preco_venda - produto_existente.preco_compra) / produto_existente.preco_compra

                margem_produto = produto_existente.margem_alvo
                margem_categoria = None
                if produto_existente.categoria:
                    margem_categoria = obter_margem_categoria_por_nome(produto_existente.categoria)

                margem_base = (
                    margem_produto
                    if margem_produto is not None
                    else (margem_categoria if margem_categoria is not None else (margem_alvo if margem_alvo is not None else DEFAULT_MARGEM_ALVO))
                )
                preco_venda_sugerido = round(preco_unitario * (1 + margem_base), 2)

                if auto_atualizar_preco_venda:
                    atualizar_produto(
                        produto_existente.id,
                        preco_compra=preco_unitario,
                        preco_venda=preco_venda_sugerido
                    )
                else:
                    atualizar_produto(produto_existente.id, preco_compra=preco_unitario)

                if variacao is None:
                    comparacoes_preco.append(
                        f"{produto_existente.nome}: preço compra atualizado para R$ {preco_unitario:.2f}. "
                        f"Sugestão venda: R$ {preco_venda_sugerido:.2f}."
                    )
                else:
                    tendencia = "aumentou" if variacao > 0 else "diminuiu"
                    comparacoes_preco.append(
                        f"{produto_existente.nome}: preço compra {tendencia} {variacao:.1f}% "
                        f"(R$ {preco_compra_atual:.2f} → R$ {preco_unitario:.2f}). "
                        f"Sugestão venda: R$ {preco_venda_sugerido:.2f}."
                    )

            produtos_atualizados += 1
        elif produto_inativo:
            # Reativar produto inativo
            reativar_produto(produto_inativo.id)
            aumentar_quantidade(produto_inativo.id, quantidade_int)
            atualizar_produto(produto_inativo.id, preco_compra=preco_unitario)
            
            if auto_atualizar_preco_venda:
                margem_produto = produto_inativo.margem_alvo
                margem_categoria = None
                if produto_inativo.categoria:
                    margem_categoria = obter_margem_categoria_por_nome(produto_inativo.categoria)
                
                margem_base = (
                    margem_produto
                    if margem_produto is not None
                    else (margem_categoria if margem_categoria is not None else (margem_alvo if margem_alvo is not None else DEFAULT_MARGEM_ALVO))
                )
                preco_venda_sugerido = round(preco_unitario * (1 + margem_base), 2)
                atualizar_produto(produto_inativo.id, preco_venda=preco_venda_sugerido)
            
            produtos_atualizados += 1
            avisos.append(f"Item {idx}: Produto inativo reativado e quantidade atualizada.")
        else:
            categoria_produto = "Geral"
            if auto_categorizar:
                categoria_produto = auto_categorizar_produto(nome.strip())

            margem_categoria = obter_margem_categoria_por_nome(categoria_produto)
            margem_base_novo = margem_categoria if margem_categoria is not None else (margem_alvo if margem_alvo is not None else None)
            preco_venda_novo = preco_unitario
            if auto_atualizar_preco_venda and margem_base_novo is not None:
                preco_venda_novo = round(preco_unitario * (1 + margem_base_novo), 2)
            produto = Produto(
                nome=nome.strip(),
                sku=sku.strip(),
                preco_compra=preco_unitario,
                preco_venda=preco_venda_novo,
                quantidade=quantidade_int,
                descricao=None,
                categoria=categoria_produto,
                margem_alvo=margem_base_novo
            )
            try:
                inserir_produto(produto)
                produtos_criados += 1
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    avisos.append(
                        f"Item {idx}: SKU {sku.strip()} já existe no banco, pulado."
                    )
                else:
                    avisos.append(
                        f"Item {idx}: Erro ao inserir produto - {str(e)}"
                    )
        
        itens_processados += 1
    
    mensagem = (
        f"Importação concluída. Itens processados: {itens_processados}. "
        f"Novos produtos: {produtos_criados}. Atualizados: {produtos_atualizados}."
    )
    
    if comparacoes_preco:
        mensagem += "\n\nComparação de preços:\n- " + "\n- ".join(comparacoes_preco[:10])
        if len(comparacoes_preco) > 10:
            mensagem += f"\n- ... e mais {len(comparacoes_preco) - 10} item(s)."

    if avisos:
        mensagem += "\n\nAvisos:\n- " + "\n- ".join(avisos[:10])
        if len(avisos) > 10:
            mensagem += f"\n- ... e mais {len(avisos) - 10} aviso(s)."
    
    return {
        "sucesso": True,
        "mensagem": mensagem,
        "itens_processados": itens_processados,
        "produtos_criados": produtos_criados,
        "produtos_atualizados": produtos_atualizados,
        "avisos": avisos,
        "comparacoes_preco": comparacoes_preco
    }
