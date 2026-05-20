"""
DASHBOARD VIEW - Tela Inicial com Visão Geral do Sistema
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from app.services.relatorio_service import gerar_relatorio_geral, gerar_recomendacoes
from app.database.vendas_fiadas_repository import listar_vendas_fiadas_pendentes
from app.database.fornecedores_repository import obter_fornecedores_do_dia
from app.ui.styles import section_title_style, style_button, style_card, title_style
from datetime import datetime


class DashboardView(QWidget):
    """Dashboard com visão geral do sistema"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.carregar_dados()
        
        # Auto-refresh a cada 30 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.carregar_dados)
        self.timer.start(30000)  # 30 segundos
    
    def setup_ui(self):
        """Configura a interface do dashboard"""
        # Layout principal com scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget de conteúdo
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        
        # ==================== TÍTULO ====================
        title_label = QLabel("🏪 CASA GUARANI - DASHBOARD")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(title_style())
        content_layout.addWidget(title_label)
        
        # ==================== CARDS DE RESUMO (GRID RESPONSIVO) ====================
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(8)
        
        # Card 1: Clientes
        self.card_clientes = self.criar_card("👥", "CLIENTES", "0", "#1976D2")
        self.cards_layout.addWidget(self.card_clientes, 0, 0)
        
        # Card 2: Produtos
        self.card_produtos = self.criar_card("📦", "PRODUTOS", "0", "#1565C0")
        self.cards_layout.addWidget(self.card_produtos, 0, 1)
        
        # Card 3: Valor em Estoque
        self.card_valor_estoque = self.criar_card("💰", "ESTOQUE", "R$ 0,00", "#FFC107")
        self.cards_layout.addWidget(self.card_valor_estoque, 0, 2)
        
        # Card 4: Lucro Potencial
        self.card_lucro = self.criar_card("📈", "LUCRO", "R$ 0,00", "#FFB300")
        self.cards_layout.addWidget(self.card_lucro, 0, 3)
        
        # Card 5: Margem Média
        self.card_margem = self.criar_card("📉", "MARGEM", "0%", "#0D47A1")
        self.cards_layout.addWidget(self.card_margem, 1, 0)
        
        # Card 6: Baixo Estoque
        self.card_baixo_estoque = self.criar_card("⚠️", "ALERTA", "0", "#F57F17")
        self.cards_layout.addWidget(self.card_baixo_estoque, 1, 1)
        
        # Card 7: Total Itens
        self.card_total_itens = self.criar_card("📊", "ITENS", "0", "#1976D2")
        self.cards_layout.addWidget(self.card_total_itens, 1, 2)
        
        # Card 8: Vendas Fiadas
        self.card_vendas_fiadas = self.criar_card("💳", "FIADO", "R$ 0,00", "#FFA000")
        self.cards_layout.addWidget(self.card_vendas_fiadas, 1, 3)
        
        content_layout.addLayout(self.cards_layout)
        
        # ==================== GRÁFICOS ====================
        graficos_layout = QGridLayout()
        graficos_layout.setSpacing(10)
        
        # Gráfico 1: Pizza - Distribuição de Valor por Categoria
        grafico1_container = self.criar_container_grafico("📊 CATEGORIAS")
        self.figura_pizza = Figure(figsize=(4, 3), facecolor='#f5f5f5')
        self.canvas_pizza = FigureCanvas(self.figura_pizza)
        grafico1_container.layout().addWidget(self.canvas_pizza)
        graficos_layout.addWidget(grafico1_container, 0, 0)
        
        # Gráfico 2: Barras - Top 10 Produtos
        grafico2_container = self.criar_container_grafico("🏆 TOP PRODUTOS")
        self.figura_barras = Figure(figsize=(4, 3), facecolor='#f5f5f5')
        self.canvas_barras = FigureCanvas(self.figura_barras)
        grafico2_container.layout().addWidget(self.canvas_barras)
        graficos_layout.addWidget(grafico2_container, 0, 1)
        
        content_layout.addLayout(graficos_layout)
        
        # ==================== FORNECEDORES DO DIA ====================
        fornecedores_dia_label = QLabel("📦 FORNECEDORES DE HOJE")
        fornecedores_dia_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        fornecedores_dia_label.setStyleSheet(section_title_style())
        content_layout.addWidget(fornecedores_dia_label)
        
        self.fornecedores_dia_layout = QVBoxLayout()
        self.fornecedores_dia_layout.setSpacing(6)
        content_layout.addLayout(self.fornecedores_dia_layout)
        
        # ==================== RECOMENDAÇÕES ====================
        recomendacoes_label = QLabel("💡 RECOMENDAÇÕES")
        recomendacoes_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        recomendacoes_label.setStyleSheet(section_title_style())
        content_layout.addWidget(recomendacoes_label)
        
        self.recomendacoes_layout = QVBoxLayout()
        self.recomendacoes_layout.setSpacing(6)
        content_layout.addLayout(self.recomendacoes_layout)
        
        # ==================== BOTÃO DE ATUALIZAR ====================
        btn_layout = QHBoxLayout()
        btn_atualizar = QPushButton("🔄 Atualizar")
        style_button(btn_atualizar)
        btn_atualizar.clicked.connect(self.carregar_dados)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_atualizar)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)
        
        content_layout.addStretch()
        
        # Configurar scroll
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def criar_card(self, icone: str, titulo: str, valor: str, cor: str) -> QFrame:
        """Cria um card de informação"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        style_card(card, cor)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(3)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Ícone e Título
        header_layout = QHBoxLayout()
        icone_label = QLabel(icone)
        icone_label.setFont(QFont("Arial", 14))
        header_layout.addWidget(icone_label)
        
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        titulo_label.setStyleSheet("color: #666;")
        header_layout.addWidget(titulo_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Valor
        valor_label = QLabel(valor)
        valor_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        valor_label.setStyleSheet(f"color: {cor};")
        valor_label.setObjectName("valor_label")
        layout.addWidget(valor_label)
        
        return card
    
    def criar_container_grafico(self, titulo: str) -> QFrame:
        """Cria um container para gráfico"""
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        style_card(container, "#1976D2")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Título do gráfico
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        titulo_label.setStyleSheet("color: #1976D2; padding-bottom: 5px;")
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo_label)
        
        return container
    
    def atualizar_valor_card(self, card: QFrame, novo_valor: str):
        """Atualiza o valor de um card"""
        valor_label = card.findChild(QLabel, "valor_label")
        if valor_label:
            valor_label.setText(novo_valor)
    
    def carregar_dados(self):
        """Carrega e atualiza todos os dados do dashboard"""
        try:
            # Gerar relatório
            relatorio = gerar_relatorio_geral()
            
            # Atualizar cards
            self.atualizar_valor_card(self.card_clientes, str(relatorio["total_clientes"]))
            self.atualizar_valor_card(self.card_produtos, str(relatorio["total_produtos"]))
            self.atualizar_valor_card(self.card_valor_estoque, 
                                     f"R$ {relatorio['valor_total_venda']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.atualizar_valor_card(self.card_lucro, 
                                     f"R$ {relatorio['lucro_potencial']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.atualizar_valor_card(self.card_margem, f"{relatorio['margem_media']:.1f}%")
            self.atualizar_valor_card(self.card_baixo_estoque, str(len(relatorio["baixo_estoque"])))
            self.atualizar_valor_card(self.card_total_itens, str(relatorio["total_itens_estoque"]))
            
            # Vendas Fiadas
            vendas_fiadas = listar_vendas_fiadas_pendentes()
            total_fiado = sum(v.valor_total for v in vendas_fiadas)
            self.atualizar_valor_card(self.card_vendas_fiadas, 
                                     f"R$ {total_fiado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            # Atualizar gráficos
            self.atualizar_grafico_pizza(relatorio)
            self.atualizar_grafico_barras(relatorio)
            
            # Atualizar fornecedores do dia
            self.atualizar_fornecedores_dia()
            
            # Atualizar recomendações
            self.atualizar_recomendacoes(relatorio)
            
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard: {e}")
    
    def atualizar_grafico_pizza(self, relatorio: dict):
        """Atualiza o gráfico de pizza"""
        self.figura_pizza.clear()
        ax = self.figura_pizza.add_subplot(111)
        
        if not relatorio["produtos"]:
            ax.text(0.5, 0.5, "Nenhum produto cadastrado", 
                   ha='center', va='center', fontsize=10, color='#999')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # Agrupar por categoria
            categorias = {}
            for p in relatorio["produtos"]:
                cat = p.categoria if hasattr(p, 'categoria') and p.categoria else "Sem Categoria"
                valor = p.preco_venda * p.quantidade
                categorias[cat] = categorias.get(cat, 0) + valor
            
            if categorias:
                labels = list(categorias.keys())
                valores = list(categorias.values())
                cores = plt.cm.Set3(range(len(labels)))
                
                # Reduzir tamanho da fonte
                ax.pie(valores, labels=labels, autopct='%1.1f%%', 
                      colors=cores, startangle=90, textprops={'fontsize': 8})
                ax.axis('equal')
            else:
                ax.text(0.5, 0.5, "Sem dados de categoria", 
                       ha='center', va='center', fontsize=10, color='#999')
                ax.axis('off')
        
        self.figura_pizza.tight_layout()
        self.canvas_pizza.draw()
    
    def atualizar_grafico_barras(self, relatorio: dict):
        """Atualiza o gráfico de barras"""
        self.figura_barras.clear()
        ax = self.figura_barras.add_subplot(111)
        
        if not relatorio["produtos"]:
            ax.text(0.5, 0.5, "Nenhum produto cadastrado", 
                   ha='center', va='center', fontsize=10, color='#999')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            # Top 5 produtos por valor total (reduzido de 10 para 5)
            produtos_valor = [(p.nome, p.preco_venda * p.quantidade) 
                             for p in relatorio["produtos"]]
            produtos_valor.sort(key=lambda x: x[1], reverse=True)
            top_5 = produtos_valor[:5]
            
            if top_5:
                nomes = [p[0][:12] + "..." if len(p[0]) > 12 else p[0] for p in top_5]
                valores = [p[1] for p in top_5]
                
                cores = plt.cm.viridis(range(len(nomes)))
                bars = ax.barh(nomes, valores, color=cores)
                
                ax.set_xlabel('Valor (R$)', fontsize=8)
                ax.set_title('Top 5 Produtos', fontsize=9, pad=5)
                ax.tick_params(axis='both', labelsize=7)
                
                # Inverter para mostrar o maior no topo
                ax.invert_yaxis()
                
                # Adicionar valores nas barras (formatação mais compacta)
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2, 
                           f'{width:.0f}', 
                           ha='left', va='center', fontsize=7, color='#333')
            else:
                ax.text(0.5, 0.5, "Sem dados suficientes", 
                       ha='center', va='center', fontsize=10, color='#999')
                ax.axis('off')
        
        self.figura_barras.tight_layout()
        self.canvas_barras.draw()
    
    def atualizar_fornecedores_dia(self):
        """Atualiza a seção de fornecedores do dia"""
        # Limpar widgets anteriores
        while self.fornecedores_dia_layout.count():
            item = self.fornecedores_dia_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Obter dia da semana atual (0=Segunda, 6=Domingo)
        dia_hoje = datetime.now().weekday()
        
        # Buscar fornecedores do dia
        fornecedores_hoje = obter_fornecedores_do_dia(dia_hoje)
        
        if not fornecedores_hoje:
            msg = self.criar_fornecedor_dia_widget(
                "ℹ️", "Nenhum fornecedor agendado para hoje", "", "#607D8B"
            )
            self.fornecedores_dia_layout.addWidget(msg)
        else:
            dias_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            for fornecedor in fornecedores_hoje:
                produtos = fornecedor.produtos_fornecidos or "Produtos diversos"
                widget = self.criar_fornecedor_dia_widget(
                    "📦",
                    f"{fornecedor.nome}",
                    f"{produtos} | Tel: {fornecedor.telefone or 'N/A'}",
                    "#1976D2"
                )
                self.fornecedores_dia_layout.addWidget(widget)
    
    def criar_fornecedor_dia_widget(self, icone: str, titulo: str, mensagem: str, cor: str) -> QFrame:
        """Cria um widget de fornecedor do dia"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        style_card(frame, cor, "#FFF9C4")
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Ícone
        icone_label = QLabel(icone)
        icone_label.setFont(QFont("Arial", 14))
        layout.addWidget(icone_label)
        
        # Conteúdo
        content_layout = QVBoxLayout()
        
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        titulo_label.setStyleSheet(f"color: {cor};")
        content_layout.addWidget(titulo_label)
        
        if mensagem:
            mensagem_label = QLabel(mensagem)
            mensagem_label.setFont(QFont("Arial", 8))
            mensagem_label.setStyleSheet("color: #0D47A1;")
            mensagem_label.setWordWrap(True)
            content_layout.addWidget(mensagem_label)
        
        layout.addLayout(content_layout, 1)
        
        return frame
    
    def atualizar_recomendacoes(self, relatorio: dict):
        """Atualiza a seção de recomendações"""
        # Limpar recomendações antigas
        while self.recomendacoes_layout.count():
            item = self.recomendacoes_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Gerar novas recomendações
        recomendacoes = gerar_recomendacoes(relatorio)
        
        if not recomendacoes:
            msg = self.criar_recomendacao(
                "✅", "TUDO CERTO!", 
                "Nenhuma recomendação no momento. Continue assim!", 
                "#4CAF50"
            )
            self.recomendacoes_layout.addWidget(msg)
        else:
            for rec in recomendacoes[:5]:  # Mostrar até 5 recomendações
                cor_map = {
                    "alerta": "#FF9800",
                    "aviso": "#F44336",
                    "sucesso": "#4CAF50",
                    "info": "#2196F3"
                }
                cor = cor_map.get(rec["tipo"], "#607D8B")
                
                widget = self.criar_recomendacao(
                    rec.get("titulo", "").split()[0],  # Pegar apenas o emoji
                    rec.get("titulo", ""),
                    rec.get("mensagem", "") + " " + rec.get("acao", ""),
                    cor
                )
                self.recomendacoes_layout.addWidget(widget)
    
    def criar_recomendacao(self, icone: str, titulo: str, mensagem: str, cor: str) -> QFrame:
        """Cria um widget de recomendação"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        style_card(frame, cor)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Ícone
        icone_label = QLabel(icone)
        icone_label.setFont(QFont("Arial", 12))
        layout.addWidget(icone_label)
        
        # Conteúdo
        content_layout = QVBoxLayout()
        
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        titulo_label.setStyleSheet(f"color: {cor};")
        content_layout.addWidget(titulo_label)
        
        mensagem_label = QLabel(mensagem)
        mensagem_label.setFont(QFont("Arial", 8))
        mensagem_label.setStyleSheet("color: #666;")
        mensagem_label.setWordWrap(True)
        content_layout.addWidget(mensagem_label)
        
        layout.addLayout(content_layout, 1)
        
        return frame
