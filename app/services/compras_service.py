"""
SERVIÇO DE COMPRAS DE FORNECEDORES
Lógica de negócio para gerenciamento de compras
"""

from typing import List, Optional
from datetime import datetime
from app.models.compra_fornecedor import CompraFornecedor, ItemCompra
from app.database.compras_repository import (
    criar_tabela_compras,
    inserir_compra,
    obter_compra_por_id,
    listar_compras_fornecedor,
    atualizar_compra,
    deletar_compra,
    obter_compras_pendentes_pagamento
)
from app.database.connection import get_connection


def registrar_compra(fornecedor_id: int, itens: List[ItemCompra], forma_pagamento: str = None, observacoes: str = None) -> dict:
    """Registra uma nova compra de fornecedor"""
    try:
        compra = CompraFornecedor(
            fornecedor_id=fornecedor_id,
            itens=itens,
            forma_pagamento=forma_pagamento,
            observacoes=observacoes
        )
        
        compra_id = inserir_compra(compra)
        
        return {
            "sucesso": True,
            "mensagem": "Compra registrada com sucesso!",
            "compra_id": compra_id
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao registrar compra: {str(e)}"
        }


def marcar_entregue(compra_id: int, data_entrega: Optional[datetime] = None) -> dict:
    """Marca uma compra como entregue e adiciona os itens ao estoque."""
    try:
        compra = obter_compra_por_id(compra_id)
        if not compra:
            return {"sucesso": False, "mensagem": "Compra não encontrada"}
        
        if compra.status == "ENTREGUE":
            return {"sucesso": True, "mensagem": "Compra ja estava entregue. Estoque nao foi somado novamente."}

        data_real = data_entrega or datetime.now()
        conn = get_connection()
        cursor = conn.cursor()
        try:
            for item in compra.itens:
                if item.quantidade <= 0:
                    raise ValueError(f"Quantidade invalida para {item.produto_nome}.")
                cursor.execute(
                    "SELECT id FROM produtos WHERE id = ? AND ativo = 1",
                    (item.produto_id,)
                )
                if not cursor.fetchone():
                    raise ValueError(f"Produto '{item.produto_nome}' nao encontrado ou inativo.")

            for item in compra.itens:
                cursor.execute(
                    "UPDATE produtos SET quantidade = quantidade + ? WHERE id = ? AND ativo = 1",
                    (item.quantidade, item.produto_id)
                )

            cursor.execute(
                """
                UPDATE compras_fornecedores
                SET status = ?, data_entrega_real = ?
                WHERE id = ?
                """,
                ("ENTREGUE", data_real.isoformat(), compra_id)
            )

            conn.commit()
            return {"sucesso": True, "mensagem": "Compra marcada como entregue e estoque atualizado."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro: {str(e)}"}


def registrar_pagamento(compra_id: int, data_pagamento: Optional[datetime] = None) -> dict:
    """Registra o pagamento de uma compra"""
    try:
        compra = obter_compra_por_id(compra_id)
        if not compra:
            return {"sucesso": False, "mensagem": "Compra não encontrada"}
        
        compra.pago = True
        compra.data_pagamento_real = data_pagamento or datetime.now()
        
        if atualizar_compra(compra):
            return {"sucesso": True, "mensagem": "Pagamento registrado"}
        
        return {"sucesso": False, "mensagem": "Erro ao registrar pagamento"}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro: {str(e)}"}


def deletar_compra_com_estoque(compra_id: int) -> dict:
    """Deleta uma compra e desfaz a entrada no estoque se ela ja foi entregue."""
    try:
        compra = obter_compra_por_id(compra_id)
        if not compra:
            return {"sucesso": False, "mensagem": "Compra nao encontrada"}

        if compra.status != "ENTREGUE":
            if deletar_compra(compra_id):
                return {"sucesso": True, "mensagem": "Compra deletada"}
            return {"sucesso": False, "mensagem": "Erro ao deletar compra"}

        conn = get_connection()
        cursor = conn.cursor()
        try:
            for item in compra.itens:
                cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (item.produto_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Produto '{item.produto_nome}' nao encontrado.")
                if int(row[0] or 0) < item.quantidade:
                    raise ValueError(
                        f"Estoque insuficiente para desfazer a compra de {item.produto_nome}. "
                        "Ajuste o estoque manualmente antes de deletar."
                    )

            for item in compra.itens:
                cursor.execute(
                    "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
                    (item.quantidade, item.produto_id)
                )

            cursor.execute("DELETE FROM itens_compra_fornecedor WHERE compra_id = ?", (compra_id,))
            cursor.execute("DELETE FROM compras_fornecedores WHERE id = ?", (compra_id,))
            conn.commit()
            return {"sucesso": True, "mensagem": "Compra deletada e estoque ajustado."}
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao deletar compra: {e}"}


def obter_resumo_compras(fornecedor_id: int) -> dict:
    """Obtém resumo das compras de um fornecedor"""
    try:
        compras = listar_compras_fornecedor(fornecedor_id)
        
        total_pendente = sum(c.valor_total for c in compras if not c.pago and c.status == "ENTREGUE")
        total_compras = sum(c.valor_total for c in compras if c.status == "ENTREGUE")
        
        return {
            "total_compras": len([c for c in compras if c.status == "ENTREGUE"]),
            "total_valor": total_compras,
            "total_pendente_pagamento": total_pendente,
            "compras_pendentes": len([c for c in compras if not c.pago])
        }
    except Exception as e:
        print(f"Erro ao obter resumo: {e}")
        return {}


def obter_compras_em_atraso() -> List[CompraFornecedor]:
    """Obtém compras com pagamento em atraso"""
    try:
        compras = obter_compras_pendentes_pagamento()
        agora = datetime.now()
        
        em_atraso = []
        for compra in compras:
            if compra.data_pagamento_esperada and compra.data_pagamento_esperada < agora:
                em_atraso.append(compra)
        
        return em_atraso
    except Exception as e:
        print(f"Erro ao obter compras em atraso: {e}")
        return []
