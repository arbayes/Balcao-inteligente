"""
Análise Inteligente de Dados - Recomendações Adaptativas
Gera análises baseadas em padrões reais dos dados
"""

from app.database.clientes_repository import listar_clientes
from app.database.estoque_repository import listar_produtos


def analisar_cenario_estoque():
    """
    Analisa o cenário real de estoque.
    
    Returns:
        dict: Análise do cenário
    """
    produtos = listar_produtos()
    
    if not produtos:
        return {
            "situacao": "vazio",
            "total_produtos": 0,
            "total_itens": 0,
            "total_valor_estoque": 0,
            "media_quantidade": 0,
            "media_margem": 0,
            "baixo_estoque": [],
            "superestocado": [],
            "baixa_margem": [],
            "alta_margem": []
        }
    
    # Calcular métricas
    total_itens = sum(p.quantidade for p in produtos)
    total_valor_estoque = sum(p.preco_venda * p.quantidade for p in produtos)
    media_quantidade = total_itens / len(produtos) if produtos else 0
    media_margem = sum(p.margem_lucro for p in produtos) / len(produtos) if produtos else 0
    
    # Contar produtos por situação
    baixo_estoque = [p for p in produtos if p.quantidade <= 5]
    superestocado = [p for p in produtos if p.quantidade > media_quantidade * 3]
    baixa_margem = [p for p in produtos if p.margem_lucro < 20]
    alta_margem = [p for p in produtos if p.margem_lucro >= 50]
    
    # Análise de cenário
    cenario = {
        "situacao": "com_dados",
        "total_produtos": len(produtos),
        "total_itens": total_itens,
        "total_valor_estoque": total_valor_estoque,
        "media_quantidade": media_quantidade,
        "media_margem": media_margem,
        "baixo_estoque": baixo_estoque,
        "superestocado": superestocado,
        "baixa_margem": baixa_margem,
        "alta_margem": alta_margem
    }
    
    return cenario
    
    return cenario


def gerar_analise_inteligente(cenario):
    """
    Gera análise inteligente e adaptativa baseada no cenário real.
    
    Args:
        cenario (dict): Cenário do estoque
    
    Returns:
        list: Análises inteligentes e dinâmicas
    """
    analises = []
    
    # ===== SITUAÇÃO GERAL =====
    if cenario["total_produtos"] == 0:
        analises.append({
            "tipo": "info",
            "titulo": "📋 COMECE AQUI",
            "prioridade": "Média",
            "mensagem": "Seu sistema está vazio. Cadastre seus primeiro produto para começar a usar o gerenciador.",
            "dados": None
        })
        return analises
    
    # ===== ANÁLISE DE VOLUME =====
    if cenario["total_itens"] > cenario["media_quantidade"] * cenario["total_produtos"] * 2:
        analises.append({
            "tipo": "alerta",
            "titulo": "📦 ESTOQUE EXCESSIVO",
            "prioridade": "Alta",
            "mensagem": f"Você tem {cenario['total_itens']} unidades em estoque. Considerando a média ({cenario['media_quantidade']:.0f} por produto), você está com EXCESSO. Isso congela capital.",
            "acao": "Reduza preços para movimentar estoque ou aumente as vendas.",
            "produtos": [p.nome for p in cenario["superestocado"][:3]]
        })
    elif cenario["total_itens"] < cenario["media_quantidade"] / 2:
        analises.append({
            "tipo": "aviso",
            "titulo": "📉 ESTOQUE BAIXO",
            "prioridade": "Média",
            "mensagem": f"Total de {cenario['total_itens']} unidades. Você está abaixo da média. Cuidado com falta de produtos.",
            "acao": "Aumente os reabastecimentos, especialmente dos produtos que mais vende.",
            "produtos": None
        })
    else:
        analises.append({
            "tipo": "sucesso",
            "titulo": "✅ ESTOQUE EQUILIBRADO",
            "prioridade": "Baixa",
            "mensagem": f"Total de {cenario['total_itens']} unidades com média de {cenario['media_quantidade']:.0f} por produto. Sua gestão está boa!",
            "acao": "Mantenha a rotina de reabastecimento atual.",
            "produtos": None
        })
    
    # ===== ANÁLISE DE MARGENS ESPECÍFICA =====
    if cenario["alta_margem"] and not cenario["baixa_margem"]:
        analises.append({
            "tipo": "sucesso",
            "titulo": "💎 MARGENS EXCELENTES",
            "prioridade": "Baixa",
            "mensagem": f"Todos os {len(cenario['alta_margem'])} produtos têm margem ≥50%! Sua estratégia de preço está perfeita.",
            "acao": "Continue com essa política de preços.",
            "produtos": None
        })
    elif cenario["baixa_margem"] and len(cenario["baixa_margem"]) > cenario["total_produtos"] / 2:
        analises.append({
            "tipo": "alerta",
            "titulo": "📉 MARGENS CRÍTICAS",
            "prioridade": "Alta",
            "mensagem": f"{len(cenario['baixa_margem'])} de {cenario['total_produtos']} produtos com margem <20%. Você está perdendo dinheiro.",
            "acao": "Revise urgentemente os preços de venda ou negocie custos melhores.",
            "produtos": [p.nome for p in cenario["baixa_margem"][:5]]
        })
    elif cenario["baixa_margem"]:
        analises.append({
            "tipo": "aviso",
            "titulo": "⚠️ ALGUNS PRODUTOS PREJUDICIAIS",
            "prioridade": "Média",
            "mensagem": f"{len(cenario['baixa_margem'])} produtos com margem <20%. Estão impactando seus lucros.",
            "acao": "Aumente o preço de venda ou reduza o custo de aquisição destes produtos.",
            "produtos": [p.nome for p in cenario["baixa_margem"]]
        })
    
    # ===== ANÁLISE DE DIVERSIFICAÇÃO =====
    if cenario["total_produtos"] < 5:
        analises.append({
            "tipo": "info",
            "titulo": "🎯 POUCOS PRODUTOS",
            "prioridade": "Baixa",
            "mensagem": f"Você tem apenas {cenario['total_produtos']} produto(s). Considere diversificar para reduzir risco.",
            "acao": "Procure novos produtos para oferecer aos clientes.",
            "produtos": None
        })
    
    # ===== ANÁLISE DE VALOR TOTAL =====
    if cenario["total_valor_estoque"] > 50000:
        analises.append({
            "tipo": "aviso",
            "titulo": "💰 CAPITAL GRANDE EM ESTOQUE",
            "prioridade": "Média",
            "mensagem": f"R$ {cenario['total_valor_estoque']:,.2f} investido em estoque. Verifique se está tudo vendendo bem.",
            "acao": "Acelere as vendas ou reduza reabastecimentos."
        })
    elif cenario["total_valor_estoque"] < 5000:
        analises.append({
            "tipo": "info",
            "titulo": "📦 ESTOQUE PEQUENO",
            "prioridade": "Baixa",
            "mensagem": f"R$ {cenario['total_valor_estoque']:,.2f} investido. Seu estoque é pequeno.",
            "acao": "Verifique se está faltando produtos para vender."
        })
    
    # ===== PADRÕES ESPECÍFICOS =====
    if cenario["baixo_estoque"]:
        analises.append({
            "tipo": "alerta",
            "titulo": "⚠️ REABASTEÇA AGORA",
            "prioridade": "Alta",
            "mensagem": f"{len(cenario['baixo_estoque'])} produto(s) com ≤5 unidades. Risco de falta.",
            "acao": "Faça entrada de estoque para estes produtos imediatamente.",
            "produtos": [p.nome for p in cenario["baixo_estoque"]]
        })
    
    # Se tudo está bem
    if not analises or (len(analises) == 1 and analises[0]["tipo"] == "sucesso"):
        analises.append({
            "tipo": "sucesso",
            "titulo": "🎉 TUDO FUNCIONANDO BEM",
            "prioridade": "Baixa",
            "mensagem": "Seu sistema está em boa forma! Estoque equilibrado e margens saudáveis.",
            "acao": "Continue monitorando regularmente."
        })
    
    # Ordenar por prioridade
    ordem_prioridade = {"Alta": 0, "Média": 1, "Baixa": 2}
    analises.sort(key=lambda x: ordem_prioridade.get(x.get("prioridade", "Baixa"), 3))
    
    return analises


def gerar_dicas_acao(cenario):
    """
    Gera dicas de ação rápida baseado no cenário.
    
    Returns:
        list: Lista de ações recomendadas
    """
    acoes = []
    
    # Top 3 produtos que precisam atenção
    if cenario["baixo_estoque"]:
        for p in cenario["baixo_estoque"][:3]:
            acoes.append(f"🔴 URGENTE: Reabasteça '{p.nome}' - apenas {p.quantidade} unidades")
    
    if cenario["baixa_margem"]:
        for p in cenario["baixa_margem"][:3]:
            acoes.append(f"⚠️ REVISÃO: '{p.nome}' tem margem de {p.margem_lucro:.1f}% (muito baixa)")
    
    if cenario["superestocado"]:
        for p in cenario["superestocado"][:3]:
            acoes.append(f"📦 PROMOÇÃO: '{p.nome}' está com {p.quantidade} unidades (muito alto)")
    
    return acoes if acoes else ["✅ Nenhuma ação urgente necessária"]
