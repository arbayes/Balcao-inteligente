"""
Graficos de gestao: foco em decisoes praticas, nao visualizacoes soltas.
"""

from matplotlib.figure import Figure

from app.services.relatorio_service import gerar_relatorio_geral
from app.services.vendas_fiadas_service import obter_resumo_inadimplentes


def _moeda_curta(valor):
    valor = float(valor or 0)
    if abs(valor) >= 1000:
        return f"R$ {valor / 1000:.1f}k"
    return f"R$ {valor:.0f}"


def _sem_dados(ax, titulo, mensagem):
    ax.set_title(titulo, fontsize=11, fontweight="bold", loc="left")
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        mensagem,
        ha="center",
        va="center",
        fontsize=10,
        color="#666666",
        transform=ax.transAxes,
    )


def criar_figura_graficos():
    relatorio = gerar_relatorio_geral()
    produtos = relatorio.get("produtos", [])
    inadimplentes = obter_resumo_inadimplentes()
    caixa = relatorio.get("caixa", {})

    fig = Figure(figsize=(12, 8), dpi=90)
    fig.patch.set_facecolor("#f5f7fa")
    fig.suptitle(
        "Painel de Decisao - Casa Guarani",
        fontsize=16,
        fontweight="bold",
        color="#0D47A1",
    )

    ax_compra = fig.add_subplot(2, 2, 1)
    ax_dinheiro = fig.add_subplot(2, 2, 2)
    ax_margem = fig.add_subplot(2, 2, 3)
    ax_caixa = fig.add_subplot(2, 2, 4)

    _grafico_reposicao(ax_compra, produtos)
    _grafico_dinheiro_parado(ax_dinheiro, produtos)
    _grafico_margem(ax_margem, relatorio)
    _grafico_caixa_fiado(ax_caixa, caixa, inadimplentes)

    fig.tight_layout(rect=[0, 0.02, 1, 0.94], h_pad=3.0, w_pad=2.5)
    return fig


def _grafico_reposicao(ax, produtos):
    baixos = sorted([p for p in produtos if p.quantidade <= 5], key=lambda p: p.quantidade)[:8]
    if not baixos:
        _sem_dados(ax, "Comprar Primeiro", "Nenhum produto em estoque critico.")
        return

    nomes = [p.nome[:24] for p in baixos]
    qtds = [p.quantidade for p in baixos]
    cores = ["#b71c1c" if p.quantidade == 0 else "#ef6c00" for p in baixos]

    ax.barh(nomes, qtds, color=cores)
    ax.set_title("Comprar Primeiro", fontsize=11, fontweight="bold", loc="left")
    ax.set_xlabel("Unidades no estoque")
    ax.invert_yaxis()
    ax.grid(True, axis="x", alpha=0.25)
    ax.set_xlim(left=0, right=max(6, max(qtds) + 1))
    for i, qtd in enumerate(qtds):
        ax.text(qtd + 0.1, i, str(qtd), va="center", fontsize=9, fontweight="bold")


def _grafico_dinheiro_parado(ax, produtos):
    itens = sorted(
        [p for p in produtos if p.quantidade > 0],
        key=lambda p: p.preco_compra * p.quantidade,
        reverse=True,
    )[:8]
    if not itens:
        _sem_dados(ax, "Dinheiro Parado no Estoque", "Nenhum estoque com valor para analisar.")
        return

    nomes = [p.nome[:24] for p in itens]
    valores = [p.preco_compra * p.quantidade for p in itens]
    ax.barh(nomes, valores, color="#1976D2")
    ax.set_title("Dinheiro Parado no Estoque", fontsize=11, fontweight="bold", loc="left")
    ax.set_xlabel("Custo em estoque")
    ax.invert_yaxis()
    ax.grid(True, axis="x", alpha=0.25)
    for i, valor in enumerate(valores):
        ax.text(valor, i, f" {_moeda_curta(valor)}", va="center", fontsize=9, fontweight="bold")


def _grafico_margem(ax, relatorio):
    abaixo = relatorio.get("produtos_abaixo_margem_alvo", [])[:8]
    if not abaixo:
        baixa = sorted(relatorio.get("baixa_margem", []), key=lambda p: p.margem_lucro)[:8]
        abaixo = [
            {
                "nome": p.nome,
                "margem_atual": p.margem_lucro,
                "margem_alvo": 30,
            }
            for p in baixa
        ]

    if not abaixo:
        _sem_dados(ax, "Preco para Revisar", "Nenhum produto com margem preocupante.")
        return

    nomes = [item["nome"][:22] for item in abaixo]
    atuais = [item["margem_atual"] for item in abaixo]
    alvos = [item.get("margem_alvo", 30) for item in abaixo]
    gaps = [max(alvo - atual, 0) for atual, alvo in zip(atuais, alvos)]

    ax.barh(nomes, atuais, color="#FFC107", label="Atual")
    ax.barh(nomes, gaps, left=atuais, color="#b71c1c", alpha=0.75, label="Falta")
    ax.set_title("Preco para Revisar", fontsize=11, fontweight="bold", loc="left")
    ax.set_xlabel("Margem %")
    ax.invert_yaxis()
    ax.grid(True, axis="x", alpha=0.25)
    ax.legend(fontsize=8)
    for i, (atual, alvo) in enumerate(zip(atuais, alvos)):
        ax.text(max(atual, alvo) + 1, i, f"{atual:.1f}% / {alvo:.1f}%", va="center", fontsize=8)


def _grafico_caixa_fiado(ax, caixa, inadimplentes):
    total_fiado = sum(info["divida_total"] for info in inadimplentes.values())
    atual = caixa.get("atual") or {}
    ultimo = caixa.get("ultimo_fechado") or {}

    if caixa.get("aberto"):
        labels = ["Entradas", "Saidas", "Saldo esperado", "Fiado pendente"]
        valores = [
            atual.get("total_entradas", 0),
            atual.get("total_saidas", 0),
            atual.get("saldo_esperado", 0),
            total_fiado,
        ]
    else:
        labels = ["Ultimo esperado", "Ultimo contado", "Diferenca", "Fiado pendente"]
        valores = [
            ultimo.get("saldo_esperado", 0),
            ultimo.get("saldo_contado", 0),
            abs(ultimo.get("diferenca", 0) or 0),
            total_fiado,
        ]

    if not any(valores):
        _sem_dados(ax, "Caixa e Fiado", "Abra/feche caixas e registre fiado para acompanhar.")
        return

    cores = ["#2e7d32", "#b71c1c", "#1976D2", "#bf4f00"]
    bars = ax.bar(labels, valores, color=cores)
    ax.set_title("Caixa e Fiado", fontsize=11, fontweight="bold", loc="left")
    ax.set_ylabel("Valor")
    ax.grid(True, axis="y", alpha=0.25)
    ax.tick_params(axis="x", labelrotation=12)
    for bar, valor in zip(bars, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            _moeda_curta(valor),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )
