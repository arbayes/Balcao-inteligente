from app.database.caixa_repository import (
    criar_tabelas_caixa,
    obter_caixa_aberto,
    abrir_caixa as repo_abrir_caixa,
    fechar_caixa as repo_fechar_caixa,
    inserir_movimento,
    listar_movimentos,
    listar_caixas,
    obter_caixa,
)


TIPOS_MOVIMENTO = {
    "ENTRADA": "Entrada",
    "SAIDA": "Saida",
    "SANGRIA": "Sangria",
    "REFORCO": "Reforco",
    "FIADO_RECEBIDO": "Fiado recebido",
}

FORMAS_PAGAMENTO = ["Dinheiro", "Pix", "Cartao Debito", "Cartao Credito", "Outro"]


def inicializar_caixa():
    criar_tabelas_caixa()


def caixa_aberto():
    return obter_caixa_aberto()


def abrir_caixa(saldo_inicial, observacoes=None):
    try:
        if obter_caixa_aberto():
            return {"sucesso": False, "mensagem": "Ja existe um caixa aberto."}
        if saldo_inicial < 0:
            return {"sucesso": False, "mensagem": "Saldo inicial nao pode ser negativo."}

        caixa_id = repo_abrir_caixa(float(saldo_inicial), observacoes)
        inserir_movimento(
            caixa_id,
            "ENTRADA",
            "Saldo inicial",
            float(saldo_inicial),
            "Dinheiro",
            "abertura",
        )
        return {"sucesso": True, "mensagem": "Caixa aberto com sucesso.", "id": caixa_id}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao abrir caixa: {e}"}


def registrar_movimento(tipo, descricao, valor, forma_pagamento="Dinheiro"):
    try:
        caixa = obter_caixa_aberto()
        if not caixa:
            return {"sucesso": False, "mensagem": "Abra o caixa antes de registrar movimentos."}
        if tipo not in TIPOS_MOVIMENTO:
            return {"sucesso": False, "mensagem": "Tipo de movimento invalido."}
        if valor <= 0:
            return {"sucesso": False, "mensagem": "Valor deve ser maior que zero."}
        if not descricao or not descricao.strip():
            return {"sucesso": False, "mensagem": "Informe uma descricao."}

        movimento_id = inserir_movimento(
            caixa["id"],
            tipo,
            descricao.strip(),
            float(valor),
            forma_pagamento or "Dinheiro",
            "manual",
        )
        return {"sucesso": True, "mensagem": "Movimento registrado.", "id": movimento_id}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao registrar movimento: {e}"}


def obter_resumo_caixa(caixa_id=None):
    caixa = obter_caixa(caixa_id) if caixa_id else obter_caixa_aberto()
    if not caixa:
        return None

    movimentos = listar_movimentos(caixa["id"])
    totais = {
        "ENTRADA": 0.0,
        "SAIDA": 0.0,
        "SANGRIA": 0.0,
        "REFORCO": 0.0,
        "FIADO_RECEBIDO": 0.0,
    }
    por_forma = {}

    for movimento in movimentos:
        tipo = movimento["tipo"]
        valor = float(movimento["valor"] or 0)
        totais[tipo] = totais.get(tipo, 0) + valor
        forma = movimento["forma_pagamento"] or "Outro"
        por_forma[forma] = por_forma.get(forma, 0) + valor

    saldo_esperado = (
        totais.get("ENTRADA", 0)
        + totais.get("REFORCO", 0)
        + totais.get("FIADO_RECEBIDO", 0)
        - totais.get("SAIDA", 0)
        - totais.get("SANGRIA", 0)
    )

    return {
        "caixa": caixa,
        "movimentos": movimentos,
        "totais": totais,
        "por_forma": por_forma,
        "saldo_esperado": saldo_esperado,
        "total_entradas": totais.get("ENTRADA", 0) + totais.get("REFORCO", 0) + totais.get("FIADO_RECEBIDO", 0),
        "total_saidas": totais.get("SAIDA", 0) + totais.get("SANGRIA", 0),
    }


def fechar_caixa(saldo_contado, observacoes=None):
    try:
        caixa = obter_caixa_aberto()
        if not caixa:
            return {"sucesso": False, "mensagem": "Nao existe caixa aberto."}
        if saldo_contado < 0:
            return {"sucesso": False, "mensagem": "Saldo contado nao pode ser negativo."}

        resumo = obter_resumo_caixa(caixa["id"])
        saldo_esperado = resumo["saldo_esperado"]
        diferenca = float(saldo_contado) - saldo_esperado
        sucesso = repo_fechar_caixa(
            caixa["id"],
            float(saldo_contado),
            saldo_esperado,
            diferenca,
            observacoes,
        )
        if not sucesso:
            return {"sucesso": False, "mensagem": "Nao foi possivel fechar o caixa."}

        return {
            "sucesso": True,
            "mensagem": "Caixa fechado com sucesso.",
            "saldo_esperado": saldo_esperado,
            "saldo_contado": float(saldo_contado),
            "diferenca": diferenca,
        }
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao fechar caixa: {e}"}


def historico_caixas(limite=30):
    return listar_caixas(limite)
