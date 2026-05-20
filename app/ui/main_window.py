"""
SISTEMA DE GERENCIAMENTO - Janela Principal
Versão 0.6 - Interface com PyQt6 + Novos Serviços Profissionais
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction

from app.database.clientes_repository import criar_tabela_clientes
from app.database.estoque_repository import criar_tabela_estoque
from app.database.vendas_fiadas_repository import criar_tabela_vendas_fiadas
from app.database.categorias_repository import criar_tabela_categorias
from app.database.fornecedores_repository import criar_tabela_fornecedores
from app.database.fornecedor_xml_repository import criar_tabela_fornecedor_xml_imports
from app.database.automacoes_repository import criar_tabela_automacoes, criar_automacoes_padrao
from app.database.caixa_repository import criar_tabelas_caixa
from app.database.pdv_repository import criar_tabelas_pdv
from app.services.categorias_service import criar_categorias_padrao
from app.services.backup_service import fazer_backup
from app.services.theme_service import get_theme_service
from app.services.alert_service import get_alert_service
from app.services.backup_scheduler import get_backup_scheduler
from app.services.db_optimizer import get_db_optimizer
from app.services.metas_service import get_metas_service
from app.services.automacoes_service import executar_automacoes
from app.utils.keyboard_shortcuts import KeyboardShortcuts
from app.ui.dashboard_view import DashboardView
from app.ui.clientes_view import ClientesView
from app.ui.estoque_view import EstoqueView
from app.ui.relatorio_view import RelatorioView
from app.ui.vendas_fiadas_view import VendasFiadasView
from app.ui.fornecedores_view import FornecedoresView
from app.ui.automacoes_view import AutomacoesView
from app.ui.caixa_view import CaixaView
from app.ui.pdv_view import PDVView
from app.ui.styles import style_button, tab_style, title_style


class MainWindow(QMainWindow):
    """Janela principal da aplicação com todos os serviços profissionais"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GERENCIADOR CASA GUARANI v0.6")
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(800, 500)
        
        # Inicializar serviços profissionais PRIMEIRO
        try:
            self.theme_service = get_theme_service()
            self.alert_service = get_alert_service()
            self.backup_scheduler = get_backup_scheduler()
            self.db_optimizer = get_db_optimizer()
            self.metas_service = get_metas_service()
            
            # Aplicar tema
            self.setStyleSheet(self.theme_service.get_stylesheet())
            
            # Atalhos de teclado
            self.keyboard_shortcuts = KeyboardShortcuts(self)
        except Exception as e:
            print(f"Erro ao inicializar serviços: {e}")
        
        # Inicializar banco de dados
        self._init_database()
        
        # Otimizar banco
        try:
            self._optimizar_banco()
        except Exception as e:
            print(f"Aviso ao otimizar: {e}")
        
        # Setup da UI
        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        
        # Configurar backup automático
        self._setup_backup_automatico()
        
        # Configurar monitoramento de alertas
        try:
            self._setup_alertas()
        except Exception as e:
            print(f"Aviso ao setup alertas: {e}")

        # Configurar automacoes do sistema
        try:
            self._setup_automacoes()
        except Exception as e:
            print(f"Aviso ao setup automacoes: {e}")
        
        # Fazer backup inicial ao abrir
        self._fazer_backup_silencioso()
    
    def _setup_backup_automatico(self):
        """Configura timer para backup automático a cada hora"""
        self.backup_timer = QTimer()
        self.backup_timer.timeout.connect(self._fazer_backup_silencioso)
        self.backup_timer.start(3600000)  # 3600000 ms = 1 hora
    
    def _fazer_backup_silencioso(self):
        """Faz backup sem notificar o usuário"""
        try:
            resultado = fazer_backup()
            if resultado['sucesso']:
                msg = f"✅ Backup automático - {resultado['mensagem'].split('!')[-1].strip()}"
                self.statusBar().showMessage(msg, 5000)
        except Exception as e:
            print(f"Erro no backup automático: {e}")
    
    def _optimizar_banco(self):
        """Otimiza o banco de dados com índices e views"""
        try:
            self.db_optimizer.criar_indices()
            self.db_optimizer.criar_view_relatorios()
            stats = self.db_optimizer.analisar_performance()
            print(f"✅ Banco otimizado: {stats}")
        except Exception as e:
            print(f"⚠️ Aviso ao otimizar banco: {e}")
    
    def _setup_alertas(self):
        """Configura monitoramento de alertas a cada 5 minutos"""
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self._verificar_alertas)
        self.alert_timer.start(300000)  # 5 minutos

    def _setup_automacoes(self):
        """Configura verificacao de automacoes a cada minuto"""
        self.automacoes_timer = QTimer()
        self.automacoes_timer.timeout.connect(self._executar_automacoes)
        self.automacoes_timer.start(60000)
        self._executar_automacoes()

    def _executar_automacoes(self):
        """Executa automacoes ativas e mostra o resultado na barra de status"""
        try:
            resultados = executar_automacoes()
            mensagens = [r["mensagem"] for r in resultados if r.get("mensagem")]
            if mensagens:
                self.statusBar().showMessage(f"Automacao: {mensagens[0]}", 15000)
                if hasattr(self, "automacoes_view"):
                    self.automacoes_view.carregar_automacoes()
        except Exception as e:
            print(f"Erro ao executar automacoes: {e}")
    
    def _verificar_alertas(self):
        """Verifica e exibe alertas do sistema"""
        try:
            alertas = self.alert_service.gerar_alertas()
            contagem = self.alert_service.obter_contador_alertas()
            
            if contagem['total'] > 0:
                msg = f"⚠️ Sistema: {contagem['error']} crítico(s), {contagem['warning']} aviso(s)"
                self.statusBar().showMessage(msg, 15000)
        except Exception as e:
            print(f"Erro ao verificar alertas: {e}")
    
    def _init_database(self):
        """Inicializa o banco de dados"""
        try:
            from app.database.compras_repository import criar_tabela_compras
            
            criar_tabela_clientes()
            criar_tabela_estoque()
            criar_tabela_vendas_fiadas()
            criar_tabela_categorias()
            criar_tabela_fornecedores()
            criar_tabela_fornecedor_xml_imports()
            criar_tabela_compras()
            criar_tabela_automacoes()
            criar_tabelas_caixa()
            criar_tabelas_pdv()
            criar_categorias_padrao()
            criar_automacoes_padrao()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar banco de dados:\n{str(e)}")
    
    def _setup_ui(self):
        """Configura a interface principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Título
        title_label = QLabel("CASA GUARANI - MERCEARIA & BAR")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(title_style())
        main_layout.addWidget(title_label)
        
        # Abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(tab_style())
        
        # Tab Dashboard
        self.dashboard_view = DashboardView()
        self.tabs.addTab(self.dashboard_view, "DASHBOARD")
        
        # Tab Clientes
        self.clientes_view = ClientesView()
        self.tabs.addTab(self.clientes_view, "CLIENTES")
        
        # Tab Estoque
        self.estoque_view = EstoqueView()
        self.tabs.addTab(self.estoque_view, "ESTOQUE")

        # Tab PDV
        self.pdv_view = PDVView()
        self.tabs.addTab(self.pdv_view, "PDV")
        
        # Tab Fornecedores
        self.fornecedores_view = FornecedoresView()
        self.tabs.addTab(self.fornecedores_view, "FORNECEDORES")
        
        # Tab Relatórios
        self.relatorio_view = RelatorioView()
        self.tabs.addTab(self.relatorio_view, "RELATORIOS")
        
        # Tab Vendas Fiadas
        self.vendas_fiadas_view = VendasFiadasView()
        self.tabs.addTab(self.vendas_fiadas_view, "VENDAS FIADAS")

        # Tab Caixa
        self.caixa_view = CaixaView()
        self.tabs.addTab(self.caixa_view, "CAIXA")

        # Tab Automacoes
        self.automacoes_view = AutomacoesView()
        self.tabs.addTab(self.automacoes_view, "AUTOMACOES")
        
        main_layout.addWidget(self.tabs)
        
        # Botão de atualização rápida
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Atualizar Tudo")
        style_button(refresh_btn)
        refresh_btn.clicked.connect(self._refresh_all)
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(button_layout)
    
    def _setup_menu(self):
        """Configura o menu da aplicação"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        arquivo_menu = menubar.addMenu("Arquivo")
        
        backup_action = QAction("Fazer Backup Agora", self)
        backup_action.triggered.connect(self._fazer_backup_manual)
        arquivo_menu.addAction(backup_action)
        
        arquivo_menu.addSeparator()
        
        sair_action = QAction("Sair", self)
        sair_action.triggered.connect(self.close)
        arquivo_menu.addAction(sair_action)
        
        # Menu Gerenciar
        gerenciar_menu = menubar.addMenu("Gerenciar")
        
        novo_cliente_action = QAction("Novo Cliente", self)
        novo_cliente_action.triggered.connect(self._novo_cliente)
        gerenciar_menu.addAction(novo_cliente_action)
        
        novo_produto_action = QAction("Novo Produto", self)
        novo_produto_action.triggered.connect(self._novo_produto)
        gerenciar_menu.addAction(novo_produto_action)
        
        # Menu Visualizar
        visualizar_menu = menubar.addMenu("Visualizar")
        
        tema_claro_action = QAction("☀️ Tema Claro", self)
        tema_claro_action.triggered.connect(lambda: self._mudar_tema('light'))
        visualizar_menu.addAction(tema_claro_action)
        
        tema_escuro_action = QAction("🌙 Tema Escuro", self)
        tema_escuro_action.triggered.connect(lambda: self._mudar_tema('dark'))
        visualizar_menu.addAction(tema_escuro_action)
        
        # Menu Ajuda
        ajuda_menu = menubar.addMenu("Ajuda")
        
        sobre_action = QAction("Sobre o Sistema", self)
        sobre_action.triggered.connect(self._show_about)
        ajuda_menu.addAction(sobre_action)
    
    def _setup_status_bar(self):
        """Configura a barra de status"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
            }
        """)
        status_bar.showMessage("Casa Guarani - Sistema Pronto | v0.6")
    
    def _refresh_all(self):
        """Atualiza todas as abas"""
        try:
            self.dashboard_view.carregar_dados()
            self.clientes_view.carregar_clientes()
            self.estoque_view.carregar_produtos()
            self.pdv_view.carregar_produtos()
            self.pdv_view.carregar_historico()
            self.vendas_fiadas_view.carregar_clientes()
            self.vendas_fiadas_view.carregar_inadimplentes()
            self.caixa_view.carregar_dados()
            self.automacoes_view.carregar_automacoes()
            self.statusBar().showMessage("Dados atualizados com sucesso!", 5000)
        except Exception as e:
            print(f"Erro ao atualizar: {e}")
    
    def _novo_cliente(self):
        """Muda para aba de clientes e abre novo cliente"""
        self.tabs.setCurrentIndex(1)
        self.clientes_view.new_cliente()
    
    def _novo_produto(self):
        """Muda para aba de estoque e abre novo produto"""
        self.tabs.setCurrentIndex(2)
        self.estoque_view.new_produto()
    
    def _show_about(self):
        """Mostra informações sobre o sistema"""
        about_text = """
        <h2 style='color: #1976D2;'>Balcão Inteligente</h2>
        <p><b>Versão:</b> 0.6 (Beta)</p>
        <p><b>Data de criação:</b> Janeiro 2026</p>
        <hr style='border: 1px solid #FFC107;'>
        <p><b style='color: #1976D2;'>Modulos Inclusos:</b></p>
        <ul>
            <li>Gerenciamento de Clientes</li>
            <li>Gerenciamento de Estoque</li>
            <li>Dashboard Visual</li>
            <li>Vendas Fiadas / Credito</li>
            <li>Relatorios e Analises</li>
            <li>Sistema de Alertas Inteligentes</li>
            <li>Backup Automatico</li>
            <li>Otimizacao de Banco de Dados</li>
            <li>Gestão de fornecedores</li>
            <li>PDV Integrado</li>
            <li>Automacoes Personalizadas</li>
            <li>Caixa e Fluxo de Caixa</li>
            <li>Importação XML de Notas Fiscais</li>
            <li>Relatorios gerenciais avançados</li>

        </ul>
        <p><i style='color: #FFC107;'>Balcão Inteligente 0.6 (Beta)</i></p>
        """
        
        QMessageBox.about(self, "Sobre", about_text)
    
    def _fazer_backup_manual(self):
        """Faz backup manual com notificação"""
        try:
            resultado = fazer_backup()
            if resultado['sucesso']:
                QMessageBox.information(
                    self,
                    "Backup Concluido",
                    resultado['mensagem'] + f"\n\nLocal: {resultado['caminho']}"
                )
            else:
                QMessageBox.warning(self, "Erro", resultado['mensagem'])
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao fazer backup: {e}")
    
    def _mudar_tema(self, tema):
        """Alterna entre tema claro e escuro"""
        try:
            self.theme_service.set_theme(tema)
            self.setStyleSheet(self.theme_service.get_stylesheet())
            
            nome_tema = "Claro ☀️" if tema == 'light' else "Escuro 🌙"
            QMessageBox.information(
                self,
                "Tema Alterado",
                f"Tema {nome_tema} ativado!\n\nAlgumas abas podem precisar ser recarregadas."
            )
            self._refresh_all()
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao mudar tema: {e}")
    
    def closeEvent(self, event):
        """Evento ao fechar a aplicação"""
        # Fazer backup antes de fechar
        self._fazer_backup_silencioso()
        
        reply = QMessageBox.question(
            self,
            "Sair",
            "Tem certeza que deseja sair?\n(Backup automatico realizado)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    
    # Estilo da aplicação
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
