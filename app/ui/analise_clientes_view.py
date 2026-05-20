"""
ANÁLISE DE CLIENTES - Segmentação, VIP e Recomendações Inteligentes
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from app.services.analise_clientes_service import (
    analise_clientes_vip,
    analise_clientes_inativos,
    analise_clientes_mais_frequentes,
    segmentacao_clientes,
    gerar_relatorio_completo_clientes
)
from app.database.clientes_repository import (
    obter_clientes_vip,
    obter_clientes_inativos_desde_dias,
    listar_clientes
)
from app.ui.styles import apply_table_style, style_button, tab_style


class AnaliseClientesView(QWidget):
    """Aba de análise detalhada de clientes"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_analises()
    
    def _setup_ui(self):
        """Configura a interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Abas de análise
        self.abas = QTabWidget()
        self.abas.setStyleSheet(tab_style(compact=True))
        
        # Aba 1: VIP
        self.aba_vip = QWidget()
        self._setup_aba_vip()
        self.abas.addTab(self.aba_vip, "👑 Clientes VIP")
        
        # Aba 2: Inativos
        self.aba_inativos = QWidget()
        self._setup_aba_inativos()
        self.abas.addTab(self.aba_inativos, "⚠️ Clientes Inativos")
        
        # Aba 3: Ranking
        self.aba_ranking = QWidget()
        self._setup_aba_ranking()
        self.abas.addTab(self.aba_ranking, "⭐ Top Clientes")
        
        # Aba 4: Segmentação
        self.aba_segmentacao = QWidget()
        self._setup_aba_segmentacao()
        self.abas.addTab(self.aba_segmentacao, "📊 Segmentação")
        
        main_layout.addWidget(self.abas)
        
        # Botão de atualizar
        btn_atualizar = QPushButton("🔄 Atualizar Análises")
        style_button(btn_atualizar)
        btn_atualizar.clicked.connect(self.carregar_analises)
        main_layout.addWidget(btn_atualizar)
    
    def _setup_aba_vip(self):
        """Configura aba de clientes VIP"""
        layout = QVBoxLayout(self.aba_vip)
        
        # Texto de análise
        self.text_vip = QTextEdit()
        self.text_vip.setReadOnly(True)
        layout.addWidget(self.text_vip)
        
        # Tabela de VIPs
        self.tabela_vip = QTableWidget()
        self.tabela_vip.setColumnCount(4)
        self.tabela_vip.setHorizontalHeaderLabels(["Nome", "CPF", "Email", "Total Gasto"])
        apply_table_style(self.tabela_vip)
        layout.addWidget(self.tabela_vip)
    
    def _setup_aba_inativos(self):
        """Configura aba de clientes inativos"""
        layout = QVBoxLayout(self.aba_inativos)
        
        # Texto de análise
        self.text_inativos = QTextEdit()
        self.text_inativos.setReadOnly(True)
        layout.addWidget(self.text_inativos)
        
        # Tabela de inativos
        self.tabela_inativos = QTableWidget()
        self.tabela_inativos.setColumnCount(4)
        self.tabela_inativos.setHorizontalHeaderLabels(["Nome", "Email", "Última Compra", "Dias Inativo"])
        apply_table_style(self.tabela_inativos)
        layout.addWidget(self.tabela_inativos)
    
    def _setup_aba_ranking(self):
        """Configura aba de ranking"""
        layout = QVBoxLayout(self.aba_ranking)
        
        # Texto de análise
        self.text_ranking = QTextEdit()
        self.text_ranking.setReadOnly(True)
        layout.addWidget(self.text_ranking)
        
        # Tabela de ranking
        self.tabela_ranking = QTableWidget()
        self.tabela_ranking.setColumnCount(4)
        self.tabela_ranking.setHorizontalHeaderLabels(["Posição", "Nome", "Email", "Total Gasto"])
        apply_table_style(self.tabela_ranking)
        layout.addWidget(self.tabela_ranking)
    
    def _setup_aba_segmentacao(self):
        """Configura aba de segmentação"""
        layout = QVBoxLayout(self.aba_segmentacao)
        
        # Texto de análise
        self.text_segmentacao = QTextEdit()
        self.text_segmentacao.setReadOnly(True)
        layout.addWidget(self.text_segmentacao)
        
        # Tabela de segmentação
        self.tabela_segmentacao = QTableWidget()
        self.tabela_segmentacao.setColumnCount(2)
        self.tabela_segmentacao.setHorizontalHeaderLabels(["Segmento", "Total"])
        apply_table_style(self.tabela_segmentacao)
        layout.addWidget(self.tabela_segmentacao)
    
    def carregar_analises(self):
        """Carrega todas as análises"""
        self._carregar_vip()
        self._carregar_inativos()
        self._carregar_ranking()
        self._carregar_segmentacao()
    
    def _carregar_vip(self):
        """Carrega análise de VIPs"""
        analise = analise_clientes_vip()
        
        # Atualizar texto
        texto = f"Status: {analise['status']}\n"
        texto += f"Total: {analise['total']} clientes VIP\n\n"
        
        if analise['total'] > 0:
            texto += f"Valor Total: R$ {analise['valor_total']:.2f}\n"
            texto += f"Valor Médio: R$ {analise['valor_medio']:.2f}\n"
            texto += f"Top Cliente: {analise['top_cliente']['nome']} (R$ {analise['top_cliente']['gasto']:.2f})\n\n"
        
        texto += "Recomendações:\n"
        for rec in analise['recomendacoes']:
            texto += f"• {rec}\n"
        
        self.text_vip.setText(texto)
        
        # Atualizar tabela
        self.tabela_vip.setRowCount(0)
        if analise['total'] > 0:
            clientes_vip = obter_clientes_vip()
            for cliente in clientes_vip:
                row = self.tabela_vip.rowCount()
                self.tabela_vip.insertRow(row)
                
                self.tabela_vip.setItem(row, 0, QTableWidgetItem(cliente.nome))
                self.tabela_vip.setItem(row, 1, QTableWidgetItem(cliente.cpf))
                self.tabela_vip.setItem(row, 2, QTableWidgetItem(cliente.email or "—"))
                
                item_gasto = QTableWidgetItem(f"R$ {cliente.valor_total_gasto:.2f}")
                self.tabela_vip.setItem(row, 3, item_gasto)
    
    def _carregar_inativos(self):
        """Carrega análise de inativos"""
        analise = analise_clientes_inativos()
        
        # Atualizar texto
        texto = f"Status: {analise['status']}\n"
        texto += f"Total: {analise['total']} clientes inativos\n"
        
        if analise['total'] > 0:
            if analise.get('nunca_compraram', 0) > 0:
                texto += f"Nunca compraram: {analise['nunca_compraram']}\n"
            if analise.get('deixaram_comprar', 0) > 0:
                texto += f"Deixaram de comprar: {analise['deixaram_comprar']}\n"
        
        texto += "\nRecomendações:\n"
        for rec in analise['recomendacoes']:
            texto += f"• {rec}\n"
        
        self.text_inativos.setText(texto)
        
        # Atualizar tabela
        self.tabela_inativos.setRowCount(0)
        if analise['total'] > 0:
            from datetime import datetime, timedelta
            clientes_inativos = obter_clientes_inativos_desde_dias(30)
            for cliente in clientes_inativos:
                row = self.tabela_inativos.rowCount()
                self.tabela_inativos.insertRow(row)
                
                self.tabela_inativos.setItem(row, 0, QTableWidgetItem(cliente.nome))
                self.tabela_inativos.setItem(row, 1, QTableWidgetItem(cliente.email or "—"))
                
                if cliente.data_ultima_compra:
                    data_str = cliente.data_ultima_compra.strftime("%d/%m/%Y")
                    dias_inativo = (datetime.now() - cliente.data_ultima_compra).days
                else:
                    data_str = "Nunca comprou"
                    dias_inativo = "—"
                
                self.tabela_inativos.setItem(row, 2, QTableWidgetItem(data_str))
                self.tabela_inativos.setItem(row, 3, QTableWidgetItem(str(dias_inativo)))
    
    def _carregar_ranking(self):
        """Carrega análise de ranking"""
        analise = analise_clientes_mais_frequentes()
        
        # Atualizar texto
        texto = f"Status: {analise['status']}\n"
        texto += f"Total de clientes: {analise.get('total', 0)}\n\n"
        
        if 'ranking' in analise:
            texto += "Top 5 Clientes:\n"
            for item in analise['ranking']:
                texto += f"{item['posicao']}. {item['nome']} - R$ {item['gasto']:.2f}\n"
        
        texto += "\nRecomendações:\n"
        for rec in analise['recomendacoes']:
            texto += f"• {rec}\n"
        
        self.text_ranking.setText(texto)
        
        # Atualizar tabela
        self.tabela_ranking.setRowCount(0)
        if 'ranking' in analise:
            for item in analise['ranking']:
                row = self.tabela_ranking.rowCount()
                self.tabela_ranking.insertRow(row)
                
                self.tabela_ranking.setItem(row, 0, QTableWidgetItem(str(item['posicao'])))
                self.tabela_ranking.setItem(row, 1, QTableWidgetItem(item['nome']))
                
                cliente = next((c for c in listar_clientes() if c.nome == item['nome']), None)
                self.tabela_ranking.setItem(row, 2, QTableWidgetItem(cliente.email if cliente else "—"))
                
                self.tabela_ranking.setItem(row, 3, QTableWidgetItem(f"R$ {item['gasto']:.2f}"))
    
    def _carregar_segmentacao(self):
        """Carrega análise de segmentação"""
        analise = segmentacao_clientes()
        
        # Atualizar texto
        texto = f"Status: {analise['status']}\n"
        texto += f"Total de clientes: {analise['total_clientes']}\n\n"
        texto += f"Alto Valor: {analise['alto_valor']} clientes\n"
        texto += f"Médio Valor: {analise['medio_valor']} clientes\n"
        texto += f"Baixo Valor: {analise['baixo_valor']} clientes\n"
        texto += f"Novos: {analise['novos']} clientes\n\n"
        
        texto += "Recomendações:\n"
        for rec in analise['recomendacoes']:
            texto += f"• {rec}\n"
        
        self.text_segmentacao.setText(texto)
        
        # Atualizar tabela
        self.tabela_segmentacao.setRowCount(0)
        
        segmentos_data = [
            ("💎 Alto Valor", analise['alto_valor']),
            ("📈 Médio Valor", analise['medio_valor']),
            ("🌱 Baixo Valor", analise['baixo_valor']),
            ("🆕 Novos Clientes", analise['novos'])
        ]
        
        for label, count in segmentos_data:
            row = self.tabela_segmentacao.rowCount()
            self.tabela_segmentacao.insertRow(row)
            
            self.tabela_segmentacao.setItem(row, 0, QTableWidgetItem(label))
            
            item_count = QTableWidgetItem(str(count))
            item_count.setForeground(QColor("#2196F3"))
            font = item_count.font()
            font.setBold(True)
            item_count.setFont(font)
            self.tabela_segmentacao.setItem(row, 1, item_count)
