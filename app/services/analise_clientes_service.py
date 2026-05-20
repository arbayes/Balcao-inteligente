from datetime import datetime, timedelta
from app.database.clientes_repository import (
    obter_clientes_vip,
    obter_clientes_inativos_desde_dias,
    listar_clientes
)

def analise_clientes_vip():
    """Analisa clientes VIP com recomendações personalizadas."""
    clientes_vip = obter_clientes_vip()
    
    if not clientes_vip:
        return {
            "status": "⚠️ SEM VIP",
            "total": 0,
            "valor_total": 0,
            "valor_medio": 0,
            "top_cliente": None,
            "mensagem": "Você ainda não possui clientes VIP cadastrados.",
            "recomendacoes": [
                "🎯 Identifique seus maiores gastadores",
                "💎 Marque-os como VIP para acompanhamento especial",
                "🎁 Ofereça benefícios exclusivos aos VIPs"
            ]
        }
    
    valor_total = sum(c.valor_total_gasto for c in clientes_vip)
    valor_medio = valor_total / len(clientes_vip) if clientes_vip else 0
    cliente_maior = max(clientes_vip, key=lambda c: c.valor_total_gasto)
    
    return {
        "status": "👑 VIP IDENTIFICADOS",
        "total": len(clientes_vip),
        "valor_total": valor_total,
        "valor_medio": valor_medio,
        "top_cliente": {
            "nome": cliente_maior.nome,
            "gasto": cliente_maior.valor_total_gasto
        },
        "recomendacoes": [
            f"👑 {len(clientes_vip)} clientes VIP gerando R$ {valor_total:.2f}",
            "🎁 Mantenha contato regular com seus VIPs",
            "💰 Ofereça descontos exclusivos ou brinde",
            f"⭐ Top cliente: {cliente_maior.nome} (R$ {cliente_maior.valor_total_gasto:.2f})"
        ]
    }


def analise_clientes_inativos(dias: int = 30):
    """Analisa clientes inativos e sugere reativação."""
    clientes_inativos = obter_clientes_inativos_desde_dias(dias)
    
    if not clientes_inativos:
        return {
            "status": "✅ TODOS ATIVOS",
            "total": 0,
            "nunca_compraram": 0,
            "deixaram_comprar": 0,
            "mensagem": f"Nenhum cliente inativo há {dias} dias.",
            "recomendacoes": []
        }
    
    # Separar que nunca compraram vs que deixaram de comprar
    nunca_compraram = [c for c in clientes_inativos if c.data_ultima_compra is None]
    deixaram_comprar = [c for c in clientes_inativos if c.data_ultima_compra is not None]
    
    recomendacoes = [
        f"⚠️ {len(clientes_inativos)} clientes inativos há {dias}+ dias"
    ]
    
    if nunca_compraram:
        recomendacoes.append(f"🆕 {len(nunca_compraram)} novos clientes que nunca compraram - envie uma proposta!")
    
    if deixaram_comprar:
        recomendacoes.append(f"🔄 {len(deixaram_comprar)} clientes que pararam - entre em contato!")
    
    recomendacoes.extend([
        "📞 Faça uma ligação ou envie uma mensagem",
        "🎁 Oferça um desconto especial para reativar"
    ])
    
    return {
        "status": "⚠️ CLIENTES INATIVOS",
        "total": len(clientes_inativos),
        "nunca_compraram": len(nunca_compraram),
        "deixaram_comprar": len(deixaram_comprar),
        "recomendacoes": recomendacoes
    }


def analise_clientes_mais_frequentes():
    """Identifica clientes mais frequentes (mais compras)."""
    clientes = listar_clientes()
    
    # Ordenar por valor gasto
    clientes_ranking = sorted(clientes, key=lambda c: c.valor_total_gasto, reverse=True)[:5]
    
    if not clientes_ranking or clientes_ranking[0].valor_total_gasto == 0:
        return {
            "status": "📊 DADOS INSUFICIENTES",
            "total": 0,
            "ranking": [],
            "mensagem": "Nenhuma compra registrada ainda.",
            "recomendacoes": [
                "🛍️ Comece a registrar vendas para análise",
                "📈 Isto ajudará a identificar padrões de compra"
            ]
        }
    
    return {
        "status": "⭐ TOP CLIENTES",
        "total": len(clientes_ranking),
        "ranking": [
            {
                "posicao": i + 1,
                "nome": c.nome,
                "gasto": c.valor_total_gasto,
                "data_ultima": c.data_ultima_compra
            }
            for i, c in enumerate(clientes_ranking)
        ],
        "recomendacoes": [
            "🏆 Seus 5 maiores gastadores acima",
            "🎯 Mantenha estes clientes satisfeitos",
            "💎 Considere marcar os maiores como VIP"
        ]
    }


def segmentacao_clientes():
    """Segmenta clientes por padrão de compra."""
    clientes = listar_clientes()
    
    segmentos = {
        "alto_valor": [],
        "medio_valor": [],
        "baixo_valor": [],
        "novos": []
    }
    
    if not clientes:
        return {
            "status": "📭 SEM CLIENTES",
            "total_clientes": 0,
            "alto_valor": 0,
            "medio_valor": 0,
            "baixo_valor": 0,
            "novos": 0,
            "mensagem": "Você ainda não possui clientes cadastrados.",
            "recomendacoes": []
        }
    
    # Calcular quartis
    valores = [c.valor_total_gasto for c in clientes if c.valor_total_gasto > 0]
    
    if valores:
        q3 = sorted(valores)[len(valores) // 4 * 3]  # 75º percentil
        q1 = sorted(valores)[len(valores) // 4]      # 25º percentil
    else:
        q1 = q3 = 0
    
    for cliente in clientes:
        if cliente.valor_total_gasto == 0:
            segmentos["novos"].append(cliente)
        elif cliente.valor_total_gasto >= q3:
            segmentos["alto_valor"].append(cliente)
        elif cliente.valor_total_gasto >= q1:
            segmentos["medio_valor"].append(cliente)
        else:
            segmentos["baixo_valor"].append(cliente)
    
    return {
        "status": "📊 SEGMENTAÇÃO",
        "total_clientes": len(clientes),
        "alto_valor": len(segmentos["alto_valor"]),
        "medio_valor": len(segmentos["medio_valor"]),
        "baixo_valor": len(segmentos["baixo_valor"]),
        "novos": len(segmentos["novos"]),
        "recomendacoes": [
            f"💎 {len(segmentos['alto_valor'])} clientes Alto Valor - VIP priority",
            f"📈 {len(segmentos['medio_valor'])} clientes Médio Valor - Crescimento",
            f"🌱 {len(segmentos['baixo_valor'])} clientes Baixo Valor - Retenção",
            f"🆕 {len(segmentos['novos'])} clientes Novos - Primeira venda"
        ]
    }


def gerar_relatorio_completo_clientes():
    """Gera um relatório completo com todas as análises."""
    return {
        "vip": analise_clientes_vip(),
        "inativos": analise_clientes_inativos(),
        "ranking": analise_clientes_mais_frequentes(),
        "segmentacao": segmentacao_clientes()
    }
