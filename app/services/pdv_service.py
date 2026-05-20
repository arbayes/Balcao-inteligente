from app.database.pdv_repository import criar_tabelas_pdv, inserir_venda_pdv, listar_vendas_pdv
from app.database.estoque_repository import obter_produto_por_id
from app.database.clientes_repository import atualizar_valor_gasto
from app.services.estoque_service import entrada_estoque, saida_estoque


FORMAS_PAGAMENTO = ["Dinheiro", "Pix", "Cartao Debito", "Cartao Credito", "Fiado", "Outro"]


def inicializar_pdv():
    criar_tabelas_pdv()


def registrar_venda_produtos(itens, forma_pagamento, cliente_id=None, observacoes=None):
    if not itens:
        return {"sucesso": False, "mensagem": "Adicione pelo menos um produto."}
    if forma_pagamento not in FORMAS_PAGAMENTO:
        return {"sucesso": False, "mensagem": "Forma de pagamento invalida."}
    if forma_pagamento == "Fiado":
        return {
            "sucesso": False,
            "mensagem": "Para venda fiada, use a tela Vendas Fiadas e selecione o cliente."
        }

    itens_processados = []
    total = 0.0
    baixas = {}

    for item in itens:
        produto = obter_produto_por_id(item["produto_id"])
        quantidade = int(item.get("quantidade") or 0)
        if not produto:
            return {"sucesso": False, "mensagem": f"Produto #{item['produto_id']} nao encontrado."}
        if quantidade <= 0:
            return {"sucesso": False, "mensagem": f"Quantidade invalida para {produto.nome}."}
        quantidade_total = baixas.get(produto.id, 0) + quantidade
        if produto.quantidade < quantidade_total:
            return {
                "sucesso": False,
                "mensagem": f"Estoque insuficiente para {produto.nome}. Disponivel: {produto.quantidade}.",
            }
        subtotal = produto.preco_venda * quantidade
        total += subtotal
        itens_processados.append({
            "produto_id": produto.id,
            "nome": produto.nome,
            "sku": produto.sku,
            "quantidade": quantidade,
            "preco_unitario": produto.preco_venda,
            "subtotal": subtotal,
        })
        baixas[produto.id] = quantidade_total

    baixadas = []
    try:
        for produto_id, quantidade in baixas.items():
            resultado = saida_estoque(produto_id, quantidade)
            if not resultado.get("sucesso"):
                _repor_baixas(baixadas)
                return resultado
            baixadas.append((produto_id, quantidade))

        venda_id = inserir_venda_pdv("PRODUTOS", itens_processados, total, forma_pagamento, cliente_id, observacoes)
        if cliente_id:
            atualizar_valor_gasto(cliente_id, total)

        _registrar_no_caixa(venda_id, total, forma_pagamento, "Venda PDV")
        return {"sucesso": True, "mensagem": f"Venda registrada. Total: R$ {total:.2f}", "id": venda_id, "total": total}
    except Exception as e:
        _repor_baixas(baixadas)
        return {"sucesso": False, "mensagem": f"Erro ao registrar venda: {e}"}


def registrar_venda_rapida(valor_total, forma_pagamento, descricao="Venda rapida", observacoes=None):
    if valor_total <= 0:
        return {"sucesso": False, "mensagem": "Valor deve ser maior que zero."}
    if forma_pagamento not in FORMAS_PAGAMENTO:
        return {"sucesso": False, "mensagem": "Forma de pagamento invalida."}
    if forma_pagamento == "Fiado":
        return {
            "sucesso": False,
            "mensagem": "Venda rapida fiada nao baixa estoque nem escolhe cliente. Use Vendas Fiadas."
        }

    itens = [{
        "nome": descricao or "Venda rapida",
        "quantidade": 1,
        "preco_unitario": float(valor_total),
        "subtotal": float(valor_total),
    }]
    try:
        venda_id = inserir_venda_pdv("RAPIDA", itens, float(valor_total), forma_pagamento, None, observacoes)
        _registrar_no_caixa(venda_id, float(valor_total), forma_pagamento, descricao or "Venda rapida")
        return {"sucesso": True, "mensagem": f"Venda rapida registrada. Total: R$ {valor_total:.2f}", "id": venda_id}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao registrar venda rapida: {e}"}


def buscar_vendas_pdv(limite=50):
    return listar_vendas_pdv(limite)


def _repor_baixas(baixas):
    for produto_id, quantidade in baixas:
        entrada_estoque(produto_id, quantidade)


def _registrar_no_caixa(venda_id, total, forma_pagamento, descricao):
    if forma_pagamento == "Fiado":
        return
    try:
        from app.services.caixa_service import registrar_movimento

        registrar_movimento(
            "ENTRADA",
            f"{descricao} #{venda_id}",
            total,
            _normalizar_forma_caixa(forma_pagamento),
        )
    except Exception:
        pass


def _normalizar_forma_caixa(forma):
    mapa = {
        "Cartao Debito": "Cartao Debito",
        "Cartao Credito": "Cartao Credito",
        "Pix": "Pix",
        "Dinheiro": "Dinheiro",
    }
    return mapa.get(forma, "Outro")
