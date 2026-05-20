"""
Tela de Relatorios - painel visual com indicadores, caixa e exportacoes.
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
    QDialog, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from app.services.relatorio_service import (
    gerar_relatorio_geral,
    gerar_ranking_estoque,
    gerar_ranking_margem,
    exportar_relatorio_pdf,
    exportar_relatorio_excel,
)
from app.services.analise_inteligente import (
    analisar_cenario_estoque,
    gerar_analise_inteligente,
    gerar_dicas_acao,
)
from app.services.vendas_fiadas_service import obter_resumo_inadimplentes
from app.ui.graficos_view import criar_figura_graficos
from app.ui.styles import apply_table_style, dialog_style, style_button, style_card, tab_style, table_style, title_style


def _moeda(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _data_curta(valor):
    if not valor:
        return "-"
    return str(valor)[:16].replace("T", " ")


class JanelaGraficos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = None
        self.setWindowTitle("Painel de Decisao - Graficos")
        self.setGeometry(100, 100, 1100, 780)
        self.setMinimumSize(920, 680)
        self.setStyleSheet(dialog_style())
        layout = QVBoxLayout(self)
        title = QLabel("PAINEL DE DECISAO")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #0D47A1;")
        layout.addWidget(title)
        subtitle = QLabel(
            "Use esta tela para decidir o que comprar, o que esta prendendo dinheiro, "
            "quais precos revisar e como caixa/fiado estao afetando o dia."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555; padding-bottom: 6px;")
        layout.addWidget(subtitle)

        self.grafico_layout = QVBoxLayout()
        try:
            self.canvas = FigureCanvasQTAgg(criar_figura_graficos())
            self.grafico_layout.addWidget(self.canvas)
        except Exception as e:
            self.grafico_layout.addWidget(QLabel(f"Erro ao gerar graficos: {e}"))
        layout.addLayout(self.grafico_layout)

        buttons = QHBoxLayout()
        btn_atualizar = QPushButton("Atualizar Graficos")
        style_button(btn_atualizar)
        btn_atualizar.clicked.connect(self.atualizar_graficos)
        buttons.addWidget(btn_atualizar)
        buttons.addStretch()
        btn_fechar = QPushButton("Fechar")
        style_button(btn_fechar, "neutral")
        btn_fechar.clicked.connect(self.accept)
        buttons.addWidget(btn_fechar)
        layout.addLayout(buttons)

    def atualizar_graficos(self):
        if self.canvas:
            self.grafico_layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
        self.canvas = FigureCanvasQTAgg(criar_figura_graficos())
        self.grafico_layout.addWidget(self.canvas)


class RelatorioView(QWidget):
    def __init__(self):
        super().__init__()
        self.relatorio = {}
        self.analises = []
        self.dicas = []
        self.ranking_estoque = []
        self.ranking_margem = []
        self.inadimplentes = {}
        self._setup_ui()
        self.carregar_relatorio()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        title = QLabel("RELATORIOS E ANALISES")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet(title_style())
        main_layout.addWidget(title)

        actions = QHBoxLayout()
        self.btn_atualizar = QPushButton("Atualizar")
        style_button(self.btn_atualizar)
        self.btn_atualizar.clicked.connect(self.carregar_relatorio)
        actions.addWidget(self.btn_atualizar)

        self.btn_graficos = QPushButton("Graficos")
        style_button(self.btn_graficos, "purple")
        self.btn_graficos.clicked.connect(self.abrir_graficos)
        actions.addWidget(self.btn_graficos)

        self.btn_pdf = QPushButton("Exportar PDF")
        style_button(self.btn_pdf, "danger")
        self.btn_pdf.clicked.connect(self.exportar_pdf)
        actions.addWidget(self.btn_pdf)

        self.btn_excel = QPushButton("Exportar Excel")
        style_button(self.btn_excel, "success")
        self.btn_excel.clicked.connect(self.exportar_excel)
        actions.addWidget(self.btn_excel)
        actions.addStretch()
        main_layout.addLayout(actions)

        self.cards_layout = QGridLayout()
        self.card_clientes = self._criar_card("Clientes", "0", "#1976D2")
        self.card_estoque = self._criar_card("Valor em estoque", "R$ 0,00", "#0D47A1")
        self.card_lucro = self._criar_card("Lucro potencial", "R$ 0,00", "#2e7d32")
        self.card_fiado = self._criar_card("Fiado pendente", "R$ 0,00", "#bf4f00")
        self.card_caixa = self._criar_card("Caixa", "Fechado", "#6A1B9A")
        self.card_alertas = self._criar_card("Alertas", "0", "#b71c1c")
        for i, card in enumerate([
            self.card_clientes, self.card_estoque, self.card_lucro,
            self.card_fiado, self.card_caixa, self.card_alertas
        ]):
            self.cards_layout.addWidget(card, i // 3, i % 3)
        main_layout.addLayout(self.cards_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(tab_style(compact=True))
        self.tab_resumo = self._criar_tab_resumo()
        self.tab_caixa = self._criar_tab_caixa()
        self.tab_alertas = self._criar_tab_alertas()
        self.tab_rankings = self._criar_tab_rankings()
        self.tab_acoes = self._criar_tab_acoes()
        self.tabs.addTab(self.tab_resumo, "Resumo")
        self.tabs.addTab(self.tab_caixa, "Caixa")
        self.tabs.addTab(self.tab_alertas, "Alertas")
        self.tabs.addTab(self.tab_rankings, "Rankings")
        self.tabs.addTab(self.tab_acoes, "Ações")
        main_layout.addWidget(self.tabs)

    def _criar_card(self, titulo, valor, cor):
        frame = QFrame()
        style_card(frame, cor)
        layout = QVBoxLayout(frame)
        label = QLabel(titulo)
        label.setStyleSheet("color: #555; font-weight: bold;")
        value = QLabel(valor)
        value.setStyleSheet(f"color: {cor}; font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        layout.addWidget(value)
        frame.valor = value
        return frame

    def _table_style(self):
        return table_style()

    def _criar_tabela(self, headers):
        tabela = QTableWidget()
        tabela.setColumnCount(len(headers))
        tabela.setHorizontalHeaderLabels(headers)
        apply_table_style(tabela)
        return tabela

    def _criar_tab_resumo(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.tabela_resumo = self._criar_tabela(["Indicador", "Valor"])
        layout.addWidget(self.tabela_resumo)
        return widget

    def _criar_tab_caixa(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.caixa_status = QLabel("Caixa fechado")
        self.caixa_status.setStyleSheet("font-weight: bold; color: #0D47A1; padding: 6px;")
        layout.addWidget(self.caixa_status)
        self.tabela_caixa = self._criar_tabela(["ID", "Abertura", "Fechamento", "Esperado", "Contado", "Diferenca", "Status"])
        layout.addWidget(self.tabela_caixa)
        return widget

    def _criar_tab_alertas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.tabela_alertas = self._criar_tabela(["Tipo", "Item", "Detalhe", "Acao sugerida"])
        layout.addWidget(self.tabela_alertas)
        return widget

    def _criar_tab_rankings(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        self.tabela_ranking_estoque = self._criar_tabela(["#", "Produto", "Qtd", "Codigo"])
        self.tabela_ranking_margem = self._criar_tabela(["#", "Produto", "Margem", "Codigo"])
        layout.addWidget(self.tabela_ranking_estoque)
        layout.addWidget(self.tabela_ranking_margem)
        return widget

    def _criar_tab_acoes(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        self.texto_acoes = QTextEdit()
        self.texto_acoes.setReadOnly(True)
        self.texto_acoes.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #111111;
                border: 1px solid #1976D2;
                border-radius: 5px;
                font-size: 11pt;
                padding: 8px;
            }
        """)
        layout.addWidget(self.texto_acoes)
        scroll.setWidget(content)
        return scroll

    def carregar_relatorio(self):
        self.relatorio = gerar_relatorio_geral()
        cenario = analisar_cenario_estoque()
        self.analises = gerar_analise_inteligente(cenario)
        self.dicas = gerar_dicas_acao(cenario)
        self.ranking_estoque = gerar_ranking_estoque(self.relatorio)
        self.ranking_margem = gerar_ranking_margem(self.relatorio)
        self.inadimplentes = obter_resumo_inadimplentes()

        self._atualizar_cards()
        self._preencher_resumo()
        self._preencher_caixa()
        self._preencher_alertas()
        self._preencher_rankings()
        self._preencher_acoes()

    def _set_table_rows(self, tabela, linhas):
        tabela.setRowCount(0)
        for linha in linhas:
            row = tabela.rowCount()
            tabela.insertRow(row)
            for col, valor in enumerate(linha):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if isinstance(valor, str) and valor.startswith("R$ -"):
                    item.setForeground(QColor("#b71c1c"))
                tabela.setItem(row, col, item)

    def _atualizar_cards(self):
        total_fiado = sum(info["divida_total"] for info in self.inadimplentes.values())
        caixa = self.relatorio.get("caixa", {})
        caixa_texto = "Aberto" if caixa.get("aberto") else "Fechado"
        if caixa.get("aberto"):
            caixa_texto = _moeda((caixa.get("atual") or {}).get("saldo_esperado", 0))
        alertas = len(self.relatorio.get("baixo_estoque", [])) + len(self.relatorio.get("produtos_abaixo_margem_alvo", []))

        self.card_clientes.valor.setText(str(self.relatorio["total_clientes"]))
        self.card_estoque.valor.setText(_moeda(self.relatorio["valor_total_venda"]))
        self.card_lucro.valor.setText(_moeda(self.relatorio["lucro_potencial"]))
        self.card_fiado.valor.setText(_moeda(total_fiado))
        self.card_caixa.valor.setText(caixa_texto)
        self.card_alertas.valor.setText(str(alertas))

    def _preencher_resumo(self):
        total_fiado = sum(info["divida_total"] for info in self.inadimplentes.values())
        linhas = [
            ["Clientes cadastrados", self.relatorio["total_clientes"]],
            ["Produtos ativos", self.relatorio["total_produtos"]],
            ["Itens em estoque", self.relatorio["total_itens_estoque"]],
            ["Valor de custo do estoque", _moeda(self.relatorio["valor_total_custo"])],
            ["Valor potencial de venda", _moeda(self.relatorio["valor_total_venda"])],
            ["Lucro potencial", _moeda(self.relatorio["lucro_potencial"])],
            ["Margem media", f"{self.relatorio['margem_media']:.1f}%"],
            ["Fiado pendente", _moeda(total_fiado)],
            ["Clientes com debito", len(self.inadimplentes)],
        ]
        self._set_table_rows(self.tabela_resumo, linhas)

    def _preencher_caixa(self):
        caixa = self.relatorio.get("caixa", {})
        if caixa.get("aberto"):
            atual = caixa.get("atual") or {}
            self.caixa_status.setText(
                f"Caixa aberto | Esperado: {_moeda(atual.get('saldo_esperado', 0))} | "
                f"Entradas: {_moeda(atual.get('total_entradas', 0))} | "
                f"Saidas: {_moeda(atual.get('total_saidas', 0))}"
            )
        elif caixa.get("ultimo_fechado"):
            ultimo = caixa["ultimo_fechado"]
            self.caixa_status.setText(
                f"Caixa fechado | Ultima diferenca: {_moeda(ultimo.get('diferenca', 0))}"
            )
        else:
            self.caixa_status.setText("Nenhum caixa registrado ainda.")

        linhas = []
        for item in caixa.get("historico", []):
            linhas.append([
                item.get("id", ""),
                _data_curta(item.get("data_abertura")),
                _data_curta(item.get("data_fechamento")),
                _moeda(item.get("saldo_esperado") if item.get("saldo_esperado") is not None else item.get("saldo_inicial")),
                _moeda(item.get("saldo_contado")) if item.get("saldo_contado") is not None else "-",
                _moeda(item.get("diferenca")) if item.get("diferenca") is not None else "-",
                item.get("status", ""),
            ])
        self._set_table_rows(self.tabela_caixa, linhas)

    def _preencher_alertas(self):
        linhas = []
        for produto in self.relatorio.get("baixo_estoque", []):
            linhas.append(["Estoque baixo", produto.nome, f"{produto.quantidade} unidade(s)", "Comprar ou repor estoque"])
        for item in self.relatorio.get("produtos_abaixo_margem_alvo", []):
            linhas.append([
                "Margem abaixo do alvo",
                item["nome"],
                f"Atual {item['margem_atual']:.1f}% / Alvo {item['margem_alvo']:.1f}%",
                "Revisar preco de venda ou custo",
            ])
        for cliente_id, info in self.inadimplentes.items():
            linhas.append([
                "Fiado pendente",
                f"Cliente #{cliente_id}",
                f"{info['quantidade_vendas']} venda(s) | {_moeda(info['divida_total'])}",
                "Cobrar ou negociar pagamento",
            ])
        if not linhas:
            linhas.append(["Tudo certo", "-", "Nenhum alerta importante agora", "-"])
        self._set_table_rows(self.tabela_alertas, linhas)

    def _preencher_rankings(self):
        linhas_estoque = []
        for i, produto in enumerate(self.ranking_estoque[:10], 1):
            linhas_estoque.append([i, produto.nome, produto.quantidade, produto.sku])
        self._set_table_rows(self.tabela_ranking_estoque, linhas_estoque)

        linhas_margem = []
        for i, produto in enumerate(self.ranking_margem[:10], 1):
            linhas_margem.append([i, produto.nome, f"{produto.margem_lucro:.1f}%", produto.sku])
        self._set_table_rows(self.tabela_ranking_margem, linhas_margem)

    def _preencher_acoes(self):
        partes = []
        if self.analises:
            partes.append("ANALISES INTELIGENTES")
            for analise in self.analises:
                partes.append(f"\n{analise['titulo']}")
                partes.append(analise.get("mensagem", ""))
                if analise.get("acao"):
                    partes.append(f"Acao: {analise['acao']}")
        if self.dicas:
            partes.append("\nACOES RAPIDAS")
            partes.extend([f"- {dica}" for dica in self.dicas])
        if not partes:
            partes.append("Sem recomendacoes urgentes no momento.")
        self.texto_acoes.setText("\n".join(partes))

    def abrir_graficos(self):
        JanelaGraficos(self).exec()

    def exportar_pdf(self):
        try:
            caminho = exportar_relatorio_pdf(gerar_relatorio_geral())
            self._perguntar_abrir("PDF Gerado", caminho)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar PDF:\n{e}")

    def exportar_excel(self):
        try:
            caminho = exportar_relatorio_excel(gerar_relatorio_geral())
            self._perguntar_abrir("Excel Gerado", caminho)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar Excel:\n{e}")

    def _perguntar_abrir(self, titulo, caminho):
        resposta = QMessageBox.question(
            self,
            titulo,
            f"Relatorio salvo em:\n{caminho}\n\nDeseja abrir o arquivo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            os.startfile(caminho)
