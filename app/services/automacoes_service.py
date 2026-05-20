from datetime import datetime

from app.database.automacoes_repository import (
    listar_automacoes,
    obter_automacao,
    inserir_automacao,
    atualizar_automacao,
    alternar_automacao,
    registrar_execucao,
    deletar_automacao,
)


GATILHOS = {
    "estoque_baixo": "Estoque baixo",
    "fiado_pendente": "Fiado pendente",
    "sempre": "Sempre no intervalo",
}

ACOES = {
    "mostrar_alerta": "Mostrar aviso",
    "fazer_backup": "Fazer backup",
}


def obter_opcoes_automacao():
    return GATILHOS, ACOES


def buscar_automacoes(ativas_apenas=False):
    return listar_automacoes(ativas_apenas=ativas_apenas)


def salvar_automacao(nome, gatilho, valor_limite, acao, intervalo_minutos, ativo=True, automacao_id=None):
    if not nome or not nome.strip():
        return {"sucesso": False, "mensagem": "Informe um nome para a automacao."}
    if gatilho not in GATILHOS:
        return {"sucesso": False, "mensagem": "Gatilho invalido."}
    if acao not in ACOES:
        return {"sucesso": False, "mensagem": "Acao invalida."}
    if intervalo_minutos < 1:
        return {"sucesso": False, "mensagem": "O intervalo deve ser de pelo menos 1 minuto."}

    try:
        valor_limite = float(valor_limite or 0)
        if automacao_id:
            sucesso = atualizar_automacao(
                automacao_id,
                nome.strip(),
                gatilho,
                valor_limite,
                acao,
                intervalo_minutos,
                ativo,
            )
            if not sucesso:
                return {"sucesso": False, "mensagem": "Automacao nao encontrada."}
        else:
            automacao_id = inserir_automacao(
                nome.strip(),
                gatilho,
                valor_limite,
                acao,
                intervalo_minutos,
                ativo,
            )

        return {"sucesso": True, "mensagem": "Automacao salva com sucesso.", "id": automacao_id}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao salvar automacao: {e}"}


def mudar_status_automacao(automacao_id, ativo):
    try:
        sucesso = alternar_automacao(automacao_id, ativo)
        if sucesso:
            status = "ativada" if ativo else "desativada"
            return {"sucesso": True, "mensagem": f"Automacao {status} com sucesso."}
        return {"sucesso": False, "mensagem": "Automacao nao encontrada."}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao mudar status: {e}"}


def remover_automacao(automacao_id):
    try:
        sucesso = deletar_automacao(automacao_id)
        if sucesso:
            return {"sucesso": True, "mensagem": "Automacao removida com sucesso."}
        return {"sucesso": False, "mensagem": "Automacao nao encontrada."}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao remover automacao: {e}"}


def executar_automacoes(forcar=False):
    resultados = []
    for automacao in listar_automacoes(ativas_apenas=True):
        if not forcar and not _pode_executar(automacao):
            continue

        resultado = _executar_automacao(automacao)
        if resultado["executou"]:
            registrar_execucao(automacao["id"], resultado["mensagem"])
            resultados.append(resultado)

    return resultados


def testar_automacao(automacao_id):
    automacao = obter_automacao(automacao_id)
    if not automacao:
        return {"sucesso": False, "mensagem": "Automacao nao encontrada."}

    resultado = _executar_automacao(automacao, teste=True)
    registrar_execucao(automacao["id"], resultado["mensagem"])
    return {"sucesso": True, "mensagem": resultado["mensagem"], "executou": resultado["executou"]}


def _pode_executar(automacao):
    ultima_execucao = automacao.get("ultima_execucao")
    if not ultima_execucao:
        return True

    try:
        if isinstance(ultima_execucao, str):
            ultima = datetime.fromisoformat(ultima_execucao)
        else:
            ultima = ultima_execucao
        minutos = int(automacao.get("intervalo_minutos") or 30)
        return (datetime.now() - ultima).total_seconds() >= minutos * 60
    except Exception:
        return True


def _executar_automacao(automacao, teste=False):
    gatilho = automacao["gatilho"]
    acao = automacao["acao"]
    limite = float(automacao.get("valor_limite") or 0)

    condicao = _avaliar_gatilho(gatilho, limite)
    if not condicao["ativa"]:
        prefixo = "Teste: " if teste else ""
        return {
            "id": automacao["id"],
            "nome": automacao["nome"],
            "executou": True,
            "mensagem": prefixo + condicao["mensagem"],
        }

    if acao == "fazer_backup":
        return _executar_backup(automacao, condicao, teste)

    prefixo = "Teste: " if teste else ""
    return {
        "id": automacao["id"],
        "nome": automacao["nome"],
        "executou": True,
        "mensagem": prefixo + condicao["mensagem"],
    }


def _avaliar_gatilho(gatilho, limite):
    if gatilho == "estoque_baixo":
        from app.database.estoque_repository import listar_produtos

        produtos = listar_produtos()
        produtos_baixos = [p for p in produtos if p.quantidade <= limite]
        if produtos_baixos:
            nomes = ", ".join([p.nome for p in produtos_baixos[:5]])
            if len(produtos_baixos) > 5:
                nomes += f" e mais {len(produtos_baixos) - 5}"
            return {
                "ativa": True,
                "mensagem": f"Estoque baixo: {len(produtos_baixos)} produto(s) em ou abaixo de {limite:g}. {nomes}",
            }
        return {"ativa": False, "mensagem": "Nenhum produto abaixo do limite de estoque."}

    if gatilho == "fiado_pendente":
        from app.database.vendas_fiadas_repository import listar_vendas_fiadas_pendentes

        vendas = listar_vendas_fiadas_pendentes()
        total = sum(v.valor_total for v in vendas)
        if vendas and total >= limite:
            return {
                "ativa": True,
                "mensagem": f"Fiado pendente: {len(vendas)} venda(s), total R$ {total:.2f}.",
            }
        return {"ativa": False, "mensagem": "Nenhuma venda fiada pendente dentro da regra."}

    if gatilho == "sempre":
        return {"ativa": True, "mensagem": "Intervalo atingido para automacao periodica."}

    return {"ativa": False, "mensagem": "Gatilho nao reconhecido."}


def _executar_backup(automacao, condicao, teste=False):
    if teste:
        return {
            "id": automacao["id"],
            "nome": automacao["nome"],
            "executou": True,
            "mensagem": "Teste: backup seria executado agora.",
        }

    try:
        from app.services.backup_service import fazer_backup

        resultado = fazer_backup()
        if resultado.get("sucesso"):
            mensagem = f"Backup automatico concluido: {resultado.get('caminho', '')}"
        else:
            mensagem = resultado.get("mensagem", "Backup automatico nao concluido.")
    except Exception as e:
        mensagem = f"Erro no backup automatico: {e}"

    return {
        "id": automacao["id"],
        "nome": automacao["nome"],
        "executou": True,
        "mensagem": mensagem,
    }
