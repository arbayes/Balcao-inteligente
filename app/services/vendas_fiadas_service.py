import json
from datetime import datetime
from app.database.vendas_fiadas_repository import (
    inserir_venda_fiada,
    listar_vendas_fiadas_por_cliente,
    listar_vendas_fiadas_pendentes,
    calcular_divida_cliente,
    atualizar_status_venda,
    obter_venda_fiada,
    atualizar_venda_fiada
)
from app.database.connection import get_connection
from app.database.estoque_repository import obter_produto_por_id
from app.services.estoque_service import entrada_estoque, saida_estoque
from app.models.venda_fiada import VendaFiada

def criar_venda_fiada(cliente_id: int, produtos: list, notas: str = None) -> dict:
    """
    Cria uma nova venda fiada.
    
    Args:
        cliente_id: ID do cliente
        produtos: Lista de dicts com {produto_id, quantidade}
        notas: Anotações sobre a venda
    
    Returns:
        dict com sucesso e mensagem
    """
    if not produtos or len(produtos) == 0:
        return {
            "sucesso": False,
            "mensagem": "Adicione pelo menos um produto!"
        }
    
    valor_total = 0
    produtos_detalhados = []
    baixas = {}
    
    # Processar produtos e calcular valor
    for item in produtos:
        produto = obter_produto_por_id(item['produto_id'])
        
        if not produto:
            return {
                "sucesso": False,
                "mensagem": f"Produto ID {item['produto_id']} não encontrado!"
            }
        
        quantidade = int(item['quantidade'])
        if quantidade <= 0:
            return {
                "sucesso": False,
                "mensagem": f"Quantidade inválida para {produto.nome}!"
            }
        
        quantidade_total = baixas.get(produto.id, {"quantidade": 0})["quantidade"] + quantidade
        if produto.quantidade < quantidade_total:
            return {
                "sucesso": False,
                "mensagem": (
                    f"Estoque insuficiente para {produto.nome}. "
                    f"Disponivel: {produto.quantidade}."
                )
            }
        
        # Usar preço de venda
        preco_unitario = produto.preco_venda
        subtotal = quantidade * preco_unitario
        valor_total += subtotal
        
        produtos_detalhados.append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "subtotal": subtotal,
            "estoque_baixado": True
        })
        baixas[produto.id] = {"quantidade": quantidade_total, "nome": produto.nome}
    
    baixadas = []
    try:
        for produto_id, baixa in baixas.items():
            quantidade = baixa["quantidade"]
            nome = baixa["nome"]
            resultado = saida_estoque(produto_id, quantidade)
            if not resultado.get("sucesso"):
                _repor_baixas(baixadas)
                return {
                    "sucesso": False,
                    "mensagem": f"Nao foi possivel baixar estoque de {nome}: {resultado.get('mensagem')}"
                }
            baixadas.append((produto_id, quantidade))

        venda = VendaFiada(
            cliente_id=cliente_id,
            produtos=produtos_detalhados,
            valor_total=valor_total,
            status="PENDENTE",
            notas=notas
        )
        
        inserir_venda_fiada(venda)
        
        return {
            "sucesso": True,
            "mensagem": f"Venda fiada criada! Total: R$ {valor_total:.2f}",
            "valor_total": valor_total
        }
    
    except Exception as e:
        _repor_baixas(baixadas)
        return {
            "sucesso": False,
            "mensagem": f"Erro ao criar venda fiada: {str(e)}"
        }

def obter_divida_cliente(cliente_id: int) -> dict:
    """Retorna informações sobre a dívida de um cliente."""
    divida = calcular_divida_cliente(cliente_id)
    vendas = listar_vendas_fiadas_por_cliente(cliente_id)
    
    vendas_pendentes = [v for v in vendas if v.status != "PAGO"]
    
    return {
        "cliente_id": cliente_id,
        "divida_total": divida['divida_total'],
        "quantidade_vendas": divida['quantidade_vendas'],
        "inadimplente": divida['inadimplente'],
        "vendas_pendentes": vendas_pendentes
    }

def pagar_venda(venda_id: int) -> dict:
    """Marca uma venda fiada como paga."""
    try:
        atualizar_status_venda(venda_id, "PAGO", datetime.now())
        return {
            "sucesso": True,
            "mensagem": "Venda marcada como paga!"
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao atualizar venda: {str(e)}"
        }

def marcar_inadimplente(cliente_id: int) -> dict:
    """Marca todas as vendas pendentes de um cliente como inadimplentes."""
    try:
        vendas = listar_vendas_fiadas_por_cliente(cliente_id)
        
        for venda in vendas:
            if venda.status in ['PENDENTE', 'PARCIAL']:
                atualizar_venda_fiada(venda.id, status='INADIMPLENTE')
        
        return {
            "sucesso": True,
            "mensagem": f"Cliente marcado como inadimplente com {len([v for v in vendas if v.status != 'PAGO'])} venda(s) pendente(s)"
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro: {str(e)}"
        }

def obter_resumo_inadimplentes() -> dict:
    """Retorna resumo de todos os clientes inadimplentes."""
    vendas_pendentes = listar_vendas_fiadas_pendentes()
    
    clientes_divida = {}
    
    for venda in vendas_pendentes:
        cliente_id = venda.cliente_id
        if cliente_id not in clientes_divida:
            clientes_divida[cliente_id] = {
                "divida_total": 0,
                "quantidade_vendas": 0,
                "status": []
            }
        
        clientes_divida[cliente_id]["divida_total"] += venda.valor_total
        clientes_divida[cliente_id]["quantidade_vendas"] += 1
        clientes_divida[cliente_id]["status"].append(venda.status)
    
    return clientes_divida

def deletar_venda(venda_id: int) -> dict:
    """Deleta uma venda fiada e desfaz a baixa de estoque quando aplicavel."""
    try:
        venda = obter_venda_fiada(venda_id)
        if not venda:
            return {
                "sucesso": False,
                "mensagem": "Venda nao encontrada."
            }

        _deletar_venda_e_repor_estoque(venda)
        return {
            "sucesso": True,
            "mensagem": "Venda deletada com sucesso! Estoque ajustado quando necessario."
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao deletar: {str(e)}"
        }


def reconciliar_estoque_vendas_antigas() -> dict:
    """
    Baixa do estoque vendas fiadas antigas que ainda nao possuem a marcacao
    estoque_baixado nos itens salvos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    vendas_corrigidas = 0
    unidades_baixadas = 0
    puladas = []

    try:
        cursor.execute("SELECT id, produtos FROM vendas_fiadas ORDER BY id")
        vendas = cursor.fetchall()

        for venda in vendas:
            venda_id = venda["id"]
            try:
                produtos = json.loads(venda["produtos"])
            except Exception:
                puladas.append(f"Venda #{venda_id}: produtos salvos em formato invalido.")
                continue

            if not isinstance(produtos, list):
                puladas.append(f"Venda #{venda_id}: lista de produtos invalida.")
                continue

            itens_sem_baixa = [
                item for item in produtos
                if isinstance(item, dict) and item.get("produto_id") and not item.get("estoque_baixado")
            ]
            if not itens_sem_baixa:
                continue

            baixas = {}
            nomes = {}
            for item in itens_sem_baixa:
                try:
                    produto_id = int(item["produto_id"])
                    quantidade = int(item.get("quantidade") or 0)
                except (TypeError, ValueError):
                    quantidade = 0

                if quantidade <= 0:
                    continue

                baixas[produto_id] = baixas.get(produto_id, 0) + quantidade
                nomes[produto_id] = item.get("nome") or f"Produto #{produto_id}"

            if not baixas:
                continue

            motivo_pular = None
            for produto_id, quantidade in baixas.items():
                cursor.execute(
                    "SELECT quantidade, ativo FROM produtos WHERE id = ?",
                    (produto_id,)
                )
                produto = cursor.fetchone()
                if not produto:
                    motivo_pular = f"produto '{nomes[produto_id]}' nao encontrado."
                    break
                if not produto["ativo"]:
                    motivo_pular = f"produto '{nomes[produto_id]}' esta inativo."
                    break
                if int(produto["quantidade"] or 0) < quantidade:
                    motivo_pular = (
                        f"estoque insuficiente para '{nomes[produto_id]}'. "
                        f"Disponivel: {produto['quantidade']}, necessario: {quantidade}."
                    )
                    break

            if motivo_pular:
                puladas.append(f"Venda #{venda_id}: {motivo_pular}")
                continue

            for produto_id, quantidade in baixas.items():
                cursor.execute(
                    "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ? AND ativo = 1",
                    (quantidade, produto_id)
                )

            for item in itens_sem_baixa:
                item["estoque_baixado"] = True

            cursor.execute(
                "UPDATE vendas_fiadas SET produtos = ? WHERE id = ?",
                (json.dumps(produtos, ensure_ascii=False), venda_id)
            )
            vendas_corrigidas += 1
            unidades_baixadas += sum(baixas.values())

        conn.commit()

        mensagem = (
            f"Reconciliação concluida. Vendas corrigidas: {vendas_corrigidas}. "
            f"Unidades baixadas: {unidades_baixadas}."
        )
        if puladas:
            mensagem += "\n\nVendas nao alteradas:\n- " + "\n- ".join(puladas[:8])
            if len(puladas) > 8:
                mensagem += f"\n- ... e mais {len(puladas) - 8}."

        return {
            "sucesso": True,
            "mensagem": mensagem,
            "vendas_corrigidas": vendas_corrigidas,
            "unidades_baixadas": unidades_baixadas,
            "puladas": puladas
        }
    except Exception as e:
        conn.rollback()
        return {
            "sucesso": False,
            "mensagem": f"Erro ao reconciliar estoque: {str(e)}"
        }
    finally:
        conn.close()


def _repor_baixas(baixas):
    for produto_id, quantidade in baixas:
        entrada_estoque(produto_id, quantidade)


def _deletar_venda_e_repor_estoque(venda: VendaFiada):
    itens_com_baixa = [item for item in venda.produtos if item.get("estoque_baixado")]

    conn = get_connection()
    cursor = conn.cursor()
    try:
        for item in itens_com_baixa:
            quantidade = int(item.get("quantidade") or 0)
            if quantidade <= 0:
                continue
            cursor.execute(
                "UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?",
                (quantidade, int(item["produto_id"]))
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Produto #{item.get('produto_id')} nao encontrado para repor estoque.")

        cursor.execute("DELETE FROM vendas_fiadas WHERE id = ?", (venda.id,))
        if cursor.rowcount == 0:
            raise ValueError("Venda nao encontrada para deletar.")

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
