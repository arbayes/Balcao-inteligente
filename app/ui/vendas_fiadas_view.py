"""
VENDAS FIADAS - Gerenciamento de crédito ao cliente
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QDialog, QFormLayout,
    QMessageBox, QHeaderView, QSpinBox, QDoubleSpinBox, QComboBox,
    QTextEdit, QDialogButtonBox, QListWidget, QListWidgetItem, QTabWidget,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from datetime import datetime

from app.services.clientes_service import buscar_clientes, obter_cliente
from app.services.estoque_service import buscar_produtos
from app.services.vendas_fiadas_service import (
    criar_venda_fiada, obter_divida_cliente, pagar_venda,
    marcar_inadimplente, obter_resumo_inadimplentes, deletar_venda,
    listar_vendas_fiadas_por_cliente
)
from app.database.vendas_fiadas_repository import listar_vendas_fiadas_pendentes
from app.ui.styles import dialog_style, info_panel_style, style_button, style_card, tab_style, table_style, title_style


def _item_tabela(texto, cor_texto="#111111", cor_fundo=None):
    item = QTableWidgetItem(str(texto))
    item.setForeground(QColor(cor_texto))
    if cor_fundo:
        item.setBackground(QColor(cor_fundo))
    return item


def _aplicar_estilo_tabela(tabela):
    tabela.setStyleSheet(table_style())
    tabela.setAlternatingRowColors(True)


def _reforcar_contraste(tabela):
    for row in range(tabela.rowCount()):
        for col in range(tabela.columnCount()):
            item = tabela.item(row, col)
            if not item:
                continue

            texto = item.text().upper()
            if "INADIMPLENTE" in texto:
                item.setForeground(QColor("#b71c1c"))
            elif "PENDENTE" in texto or "PARCIAL" in texto:
                item.setForeground(QColor("#bf4f00"))
            elif "PAGO" in texto or "ATIVO" in texto or "SEM" in texto:
                item.setForeground(QColor("#2e7d32"))
            elif item.background().color().isValid() and item.background().color().name() != "#000000":
                item.setForeground(QColor("#111111"))
            else:
                item.setForeground(QColor("#111111"))


class VendasFiadasView(QWidget):
    """View para gerenciar vendas fiadas/crédito ao cliente"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_clientes()
    
    def _setup_ui(self):
        """Configura a interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Título com estilo do app
        title = QLabel("💳 VENDAS FIADAS / CRÉDITO AO CLIENTE")
        title.setStyleSheet(title_style())
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(tab_style(compact=True))
        
        # Aba 1: Lista de Clientes com Débito
        self._setup_tab_clientes()
        
        # Aba 2: Resumo de Inadimplentes
        self._setup_tab_inadimplentes()
        
        main_layout.addWidget(self.tabs)
    
    def _setup_tab_clientes(self):
        """Aba com lista de clientes e opção de criar venda fiada"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Busca de clientes
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Buscar cliente:"))
        self.input_busca_cliente = QLineEdit()
        self.input_busca_cliente.setPlaceholderText("Nome, CPF ou Email...")
        self.input_busca_cliente.textChanged.connect(self.carregar_clientes)
        search_layout.addWidget(self.input_busca_cliente)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Tabela de clientes
        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.setColumnCount(5)
        self.tabela_clientes.setHorizontalHeaderLabels([
            "ID", "Nome", "Dívida Total", "Qt. Vendas", "Status"
        ])
        self.tabela_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_clientes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_clientes.cellDoubleClicked.connect(self._on_cliente_selecionado)
        # Estilo com cores do app
        self.tabela_clientes.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #000;
                border: 1px solid #1976D2;
                border-radius: 5px;
            }
            QTableWidget::item {
                color: #000;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #FFC107;
                color: #0D47A1;
            }
        """)
        
        # Alternância de cores das linhas
        self.tabela_clientes.setAlternatingRowColors(True)
        palette = self.tabela_clientes.palette()
        palette.setColor(palette.ColorRole.AlternateBase, QColor("#e3f2fd"))
        self.tabela_clientes.setPalette(palette)
        _aplicar_estilo_tabela(self.tabela_clientes)
        
        layout.addWidget(self.tabela_clientes)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        btn_novo = QPushButton("➕ Nova Venda Fiada")
        style_button(btn_novo)
        btn_novo.clicked.connect(self._novo_venda_fiada)
        btn_layout.addWidget(btn_novo)
        
        btn_marcar = QPushButton("⚠️ Marcar Inadimplente")
        style_button(btn_marcar, "danger")
        btn_marcar.clicked.connect(self._marcar_inadimplente)
        btn_layout.addWidget(btn_marcar)
        
        btn_ver = QPushButton("📋 Ver Detalhes")
        style_button(btn_ver)
        btn_ver.clicked.connect(self._ver_detalhes)
        btn_layout.addWidget(btn_ver)

        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "👥 CLIENTES")
    
    def _setup_tab_inadimplentes(self):
        """Aba com resumo de inadimplentes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info
        info = QLabel("⚠️ Clientes com débito pendente que podem estar inadimplentes")
        info.setStyleSheet(info_panel_style())
        layout.addWidget(info)
        
        # Tabela de inadimplentes
        self.tabela_inadimplentes = QTableWidget()
        self.tabela_inadimplentes.setColumnCount(4)
        self.tabela_inadimplentes.setHorizontalHeaderLabels([
            "Cliente ID", "Nome", "Dívida Total", "Qt. Vendas"
        ])
        self.tabela_inadimplentes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Estilo com cores do app
        self.tabela_inadimplentes.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: #000;
                border: 1px solid #1976D2;
                border-radius: 5px;
            }
            QTableWidget::item {
                color: #000;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #FFC107;
                color: #0D47A1;
            }
        """)
        
        # Alternância de cores das linhas
        self.tabela_inadimplentes.setAlternatingRowColors(True)
        palette = self.tabela_inadimplentes.palette()
        palette.setColor(palette.ColorRole.AlternateBase, QColor("#e3f2fd"))
        self.tabela_inadimplentes.setPalette(palette)
        _aplicar_estilo_tabela(self.tabela_inadimplentes)
        
        layout.addWidget(self.tabela_inadimplentes)
        
        # Botão refresh
        btn_refresh = QPushButton("🔄 Atualizar")
        style_button(btn_refresh)
        btn_refresh.clicked.connect(self.carregar_inadimplentes)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "⚠️ INADIMPLENTES")
    
    def carregar_clientes(self):
        """Carrega lista de TODOS os clientes (destacando quem tem débito)"""
        termo = self.input_busca_cliente.text().strip() if hasattr(self, 'input_busca_cliente') else ""
        clientes = buscar_clientes(termo if termo else None)
        
        # Adicionar informações de dívida a todos os clientes
        clientes_com_divida = []
        
        for cliente in clientes:
            divida = obter_divida_cliente(cliente['id'])
            cliente['divida'] = divida
            clientes_com_divida.append(cliente)
        
        # Ordenar: com dívida primeiro
        clientes_com_divida.sort(key=lambda c: c['divida']['divida_total'], reverse=True)
        
        # Atualizar tabela
        self.tabela_clientes.setRowCount(0)
        
        for cliente in clientes_com_divida:
            row = self.tabela_clientes.rowCount()
            self.tabela_clientes.insertRow(row)
            
            divida = cliente['divida']
            tem_divida = divida['divida_total'] > 0
            
            # ID
            item_id = QTableWidgetItem(str(cliente['id']))
            self.tabela_clientes.setItem(row, 0, item_id)
            
            # Nome
            item_nome = QTableWidgetItem(cliente['nome'])
            if tem_divida:
                item_nome.setBackground(QColor("#fff3e0"))
            self.tabela_clientes.setItem(row, 1, item_nome)
            
            # Dívida Total
            divida_item = QTableWidgetItem(f"R$ {divida['divida_total']:.2f}" if tem_divida else "—")
            if divida['inadimplente']:
                divida_item.setBackground(QColor("#ffebee"))
                divida_item.setForeground(QColor("#c62828"))
            elif tem_divida:
                divida_item.setBackground(QColor("#fff3e0"))
                divida_item.setForeground(QColor("#e65100"))
            self.tabela_clientes.setItem(row, 2, divida_item)
            
            # Quantidade de vendas
            item_qt = QTableWidgetItem(str(divida['quantidade_vendas']) if tem_divida else "—")
            if tem_divida:
                item_qt.setBackground(QColor("#fff3e0"))
            self.tabela_clientes.setItem(row, 3, item_qt)
            
            # Status
            if tem_divida:
                status_text = "⚠️ INADIMPLENTE" if divida['inadimplente'] else "⏳ Pendente"
                status_item = QTableWidgetItem(status_text)
                if divida['inadimplente']:
                    status_item.setForeground(QColor("#f44336"))
                    status_item.setBackground(QColor("#ffebee"))
                else:
                    status_item.setForeground(QColor("#ff6f00"))
                    status_item.setBackground(QColor("#fff3e0"))
            else:
                status_item = QTableWidgetItem("✅ Ativo")
                status_item.setForeground(QColor("#4CAF50"))
            self.tabela_clientes.setItem(row, 4, status_item)
        _reforcar_contraste(self.tabela_clientes)
    
    def carregar_inadimplentes(self):
        """Carrega resumo de inadimplentes"""
        resumo = obter_resumo_inadimplentes()
        
        self.tabela_inadimplentes.setRowCount(0)
        
        for cliente_id, info in resumo.items():
            cliente = obter_cliente(cliente_id)
            if cliente:
                row = self.tabela_inadimplentes.rowCount()
                self.tabela_inadimplentes.insertRow(row)
                
                self.tabela_inadimplentes.setItem(row, 0, QTableWidgetItem(str(cliente_id)))
                self.tabela_inadimplentes.setItem(row, 1, QTableWidgetItem(cliente['nome']))
                
                divida_item = QTableWidgetItem(f"R$ {info['divida_total']:.2f}")
                divida_item.setBackground(QColor("#ffebee"))
                divida_item.setForeground(QColor("#c62828"))
                self.tabela_inadimplentes.setItem(row, 2, divida_item)
                
                self.tabela_inadimplentes.setItem(row, 3, QTableWidgetItem(str(info['quantidade_vendas'])))
        _reforcar_contraste(self.tabela_inadimplentes)
    
    def _on_cliente_selecionado(self, row, col):
        """Abre detalhes do cliente ao clicar"""
        cliente_id = int(self.tabela_clientes.item(row, 0).text())
        self._abrir_detalhes_cliente(cliente_id)
    
    def _abrir_detalhes_cliente(self, cliente_id: int):
        """Abre janela com detalhes de um cliente"""
        cliente = obter_cliente(cliente_id)
        if not cliente:
            QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
            return
        
        dialog = ClienteDetalhesDialog(cliente, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_clientes()
            self.carregar_inadimplentes()
    
    def _ver_detalhes(self):
        """Ver detalhes do cliente selecionado"""
        row = self.tabela_clientes.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione um cliente!")
            return
        
        cliente_id = int(self.tabela_clientes.item(row, 0).text())
        self._abrir_detalhes_cliente(cliente_id)
    
    def _novo_venda_fiada(self):
        """Cria nova venda fiada"""
        row = self.tabela_clientes.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione um cliente!")
            return
        
        cliente_id = int(self.tabela_clientes.item(row, 0).text())
        cliente = obter_cliente(cliente_id)
        
        dialog = NovaVendaFiadaDialog(cliente, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_clientes()
            self.carregar_inadimplentes()
    
    def _marcar_inadimplente(self):
        """Marca cliente como inadimplente"""
        row = self.tabela_clientes.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione um cliente!")
            return
        
        cliente_id = int(self.tabela_clientes.item(row, 0).text())
        cliente_nome = self.tabela_clientes.item(row, 1).text()
        
        resposta = QMessageBox.question(
            self,
            "⚠️ Marcar Inadimplente",
            f"Marcar '{cliente_nome}' como inadimplente?\n\nTodas suas vendas pendentes serão marcadas como inadimplentes.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            resultado = marcar_inadimplente(cliente_id)
            if resultado['sucesso']:
                QMessageBox.information(self, "✅ Sucesso", resultado['mensagem'])
                self.carregar_clientes()
                self.carregar_inadimplentes()
            else:
                QMessageBox.warning(self, "❌ Erro", resultado['mensagem'])

class NovaVendaFiadaDialog(QDialog):
    """Diálogo para criar nova venda fiada"""
    
    def __init__(self, cliente: dict, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.produtos_selecionados = []
        self.produtos_disponiveis = buscar_produtos()
        self.setWindowTitle(f"Nova Venda Fiada - {cliente['nome']}")
        self.setMinimumWidth(600)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura o formulário"""
        layout = QVBoxLayout(self)
        
        # Estilo geral com cores do app
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #0D47A1;
                font-weight: bold;
            }
            QComboBox {
                color: #000;
                background-color: white;
                border: 1px solid #1976D2;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox {
                color: #000;
                background-color: white;
                border: 1px solid #1976D2;
                border-radius: 3px;
                padding: 5px;
            }
            QTextEdit {
                color: #000;
                background-color: white;
                border: 1px solid #1976D2;
                border-radius: 3px;
            }
            QListWidget {
                color: #000;
                background-color: white;
                border: 1px solid #1976D2;
                border-radius: 3px;
            }
            QListWidget::item {
                color: #000;
            }
        """)
        self.setStyleSheet(dialog_style())
        
        # Info do cliente
        info = QLabel(f"Cliente: {self.cliente['nome']} (ID: {self.cliente['id']})")
        info.setStyleSheet(title_style())
        info_font = QFont()
        info_font.setBold(True)
        info.setFont(info_font)
        layout.addWidget(info)
        
        # Seleção de produtos
        layout.addWidget(QLabel("📦 Selecione produtos:"))
        
        produtos_layout = QHBoxLayout()
        
        # Combo de produtos
        self.combo_produtos = QComboBox()
        for produto in self.produtos_disponiveis:
            self.combo_produtos.addItem(
                f"{produto['nome']} (R$ {produto['preco_venda']:.2f}) - Estoque: {produto['quantidade']}",
                produto['id']
            )
        produtos_layout.addWidget(self.combo_produtos)
        
        # Quantidade
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setMinimum(1)
        self.spin_quantidade.setValue(1)
        produtos_layout.addWidget(QLabel("Qt:"))
        produtos_layout.addWidget(self.spin_quantidade)
        
        # Botão adicionar
        btn_add = QPushButton("➕ Adicionar")
        style_button(btn_add)
        btn_add.clicked.connect(self._adicionar_produto)
        produtos_layout.addWidget(btn_add)
        
        layout.addLayout(produtos_layout)
        
        # Lista de produtos adicionados
        self.lista_produtos = QListWidget()
        layout.addWidget(QLabel("✅ Produtos na venda:"))
        layout.addWidget(self.lista_produtos)
        
        # Total
        self.label_total = QLabel("Total: R$ 0,00")
        self.label_total.setStyleSheet("""
            background-color: #e3f2fd;
            color: #0D47A1;
            padding: 10px;
            border-left: 4px solid #1976D2;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        """)
        self.label_total.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.label_total)
        
        # Notas
        layout.addWidget(QLabel("📝 Notas (opcional):"))
        self.text_notas = QTextEdit()
        self.text_notas.setMaximumHeight(60)
        layout.addWidget(self.text_notas)
        
        # Botões
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.setStyleSheet("""
            QDialogButtonBox > QPushButton {
                min-width: 70px;
                background-color: #1976D2;
                color: white;
                font-weight: bold;
                border: 2px solid #FFC107;
                border-radius: 5px;
                padding: 8px;
            }
            QDialogButtonBox > QPushButton:hover {
                background-color: #0D47A1;
                border: 2px solid #FFA000;
            }
            QDialogButtonBox > QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        button_box.setStyleSheet("")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _adicionar_produto(self):
        """Adiciona produto à lista"""
        produto_id = self.combo_produtos.currentData()
        quantidade = self.spin_quantidade.value()
        
        produto = next((p for p in self.produtos_disponiveis if p['id'] == produto_id), None)
        
        if produto:
            quantidade_ja_adicionada = sum(
                item['quantidade']
                for item in self.produtos_selecionados
                if item['produto_id'] == produto_id
            )
            if quantidade_ja_adicionada + quantidade > produto['quantidade']:
                QMessageBox.warning(
                    self,
                    "Estoque insuficiente",
                    f"Disponivel em estoque: {produto['quantidade']}. Ja adicionado: {quantidade_ja_adicionada}."
                )
                return

            self.produtos_selecionados.append({
                'produto_id': produto_id,
                'nome': produto['nome'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco_venda']
            })
            
            self._atualizar_lista()
    
    def _atualizar_lista(self):
        """Atualiza a lista e o total"""
        self.lista_produtos.clear()
        total = 0
        
        for item in self.produtos_selecionados:
            subtotal = item['quantidade'] * item['preco_unitario']
            total += subtotal
            texto = f"{item['nome']} x{item['quantidade']} = R$ {subtotal:.2f}"
            self.lista_produtos.addItem(texto)
        
        self.label_total.setText(f"Total: R$ {total:.2f}")
    
    def accept(self):
        """Salva a venda fiada"""
        if not self.produtos_selecionados:
            QMessageBox.warning(self, "⚠️ Aviso", "Adicione pelo menos um produto!")
            return
        
        resultado = criar_venda_fiada(
            self.cliente['id'],
            self.produtos_selecionados,
            self.text_notas.toPlainText() or None
        )
        
        if resultado['sucesso']:
            QMessageBox.information(self, "✅ Sucesso", resultado['mensagem'])
            super().accept()
        else:
            QMessageBox.warning(self, "❌ Erro", resultado['mensagem'])


class ClienteDetalhesDialog(QDialog):
    """Diálogo com detalhes e histórico de vendas fiadas"""
    
    def __init__(self, cliente: dict, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.setWindowTitle(f"Perfil do Cliente - {cliente['nome']}")
        self.setMinimumWidth(900)
        self.setMinimumHeight(650)
        self.setModal(True)
        self._setup_ui()
        self._carregar_vendas()
    
    def _setup_ui(self):
        """Configura a interface profissional"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Estilo geral da dialog com cores do app
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                color: #111111;
            }
            QLabel {
                background-color: transparent;
                color: #111111;
            }
            QWidget {
                color: #111111;
            }
            QTableWidget {
                color: #111111;
            }
            QTableWidget::item {
                color: #111111;
            }
        """)
        
        # ===== SEÇÃO: INFORMAÇÕES DO CLIENTE =====
        self.setStyleSheet(dialog_style())
        info_widget = self._criar_widget_info_cliente()
        layout.addWidget(info_widget)
        
        layout.addSpacing(10)
        
        # ===== SEÇÃO: DÍVIDA ATUAL =====
        divida_widget = self._criar_widget_divida()
        layout.addWidget(divida_widget)
        
        layout.addSpacing(10)
        
        # ===== SEÇÃO: HISTÓRICO DE VENDAS =====
        titulo_vendas = QLabel("📋 HISTÓRICO DE VENDAS FIADAS")
        titulo_vendas.setStyleSheet(title_style())
        titulo_font = QFont()
        titulo_font.setPointSize(11)
        titulo_font.setBold(True)
        titulo_vendas.setFont(titulo_font)
        layout.addWidget(titulo_vendas)
        
        self.tabela_vendas = QTableWidget()
        self.tabela_vendas.setColumnCount(5)
        self.tabela_vendas.setHorizontalHeaderLabels([
            "ID", "Data", "Produtos", "Valor", "Status"
        ])
        self.tabela_vendas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_vendas.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #1976D2;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #FFC107;
                color: #0D47A1;
            }
        """)
        
        # Alternância de cores das linhas
        self.tabela_vendas.setAlternatingRowColors(True)
        palette = self.tabela_vendas.palette()
        palette.setColor(palette.ColorRole.AlternateBase, QColor("#e3f2fd"))
        self.tabela_vendas.setPalette(palette)
        _aplicar_estilo_tabela(self.tabela_vendas)
        
        self.tabela_vendas.setMinimumHeight(300)
        layout.addWidget(self.tabela_vendas)
        
        # ===== SEÇÃO: BOTÕES DE AÇÃO =====
        btn_layout = self._criar_botoes_acao()
        layout.addLayout(btn_layout)
    
    def _criar_widget_info_cliente(self):
        """Cria widget com informações do cliente"""
        widget = QFrame()
        widget.setObjectName("clienteInfoCard")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Estilo do widget
        style_card(widget, "#1976D2")
        
        # Formatar data de cadastro
        data_cadastro = self.cliente.get('data_cadastro', '—')
        if data_cadastro:
            if isinstance(data_cadastro, str):
                data_cadastro = data_cadastro[:10]
            else:
                data_cadastro = data_cadastro.strftime("%d/%m/%Y")
        else:
            data_cadastro = '—'
        
        # Info texto
        info_text = f"""<html>
        <b style="font-size: 14px; color: #000;">👤 {self.cliente['nome']}</b><br>
        <span style="font-size: 11px; color: #000;">ID: {self.cliente['id']}</span><br><br>
        <span style="color: #000; font-size: 12px;">
        📧 <b>Email:</b> {self.cliente.get('email', '—') or '—'}<br>
        📞 <b>Telefone:</b> {self.cliente.get('telefone', '—') or '—'}<br>
        🏠 <b>Endereço:</b> {self.cliente.get('endereco', '—') or '—'}<br>
        📅 <b>Cadastrado:</b> {data_cadastro}
        </span>
        </html>"""
        
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)
        
        return widget
    
    def _criar_widget_divida(self):
        """Cria widget com informações de dívida"""
        divida = obter_divida_cliente(self.cliente['id'])
        
        widget = QFrame()
        widget.setObjectName("dividaCard")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Cor de fundo baseada em status
        if divida['inadimplente']:
            cor_bg = "#ffebee"
            cor_borda = "#ef5350"
            cor_texto = "#b71c1c"
        elif divida['divida_total'] > 0:
            cor_bg = "#fff3e0"
            cor_borda = "#ffb74d"
            cor_texto = "#bf4f00"
        else:
            cor_bg = "#e8f5e9"
            cor_borda = "#81c784"
            cor_texto = "#2e7d32"
        
        widget.setStyleSheet(f"""
            QFrame#dividaCard {{
                background-color: {cor_bg};
                border: 2px solid {cor_borda};
                border-radius: 6px;
            }}
            QFrame#dividaCard QLabel {{
                color: #111111;
                border: none;
                background: transparent;
            }}
        """)
        
        # Conteúdo
        divida_html = f"""<html>
        <b style="font-size: 16px; color: #000;">💳 SITUAÇÃO DE CRÉDITO</b><br><br>
        <table style="width: 100%; color: #000;">
            <tr>
                <td><b>Dívida Total:</b></td>
                <td style="text-align: right; font-size: 14px; font-weight: bold; color: {cor_texto};">R$ {divida['divida_total']:.2f}</td>
            </tr>
            <tr>
                <td><b>Vendas Pendentes:</b></td>
                <td style="text-align: right; color: #111111;">{divida['quantidade_vendas']}</td>
            </tr>
            <tr>
                <td><b>Status:</b></td>
                <td style="text-align: right; color: {cor_texto}; font-weight: bold;">
                    {'⚠️ INADIMPLENTE' if divida['inadimplente'] else ('⏳ PENDENTE' if divida['quantidade_vendas'] > 0 else '✅ SEM DÉBITO')}
                </td>
            </tr>
        </table>
        </html>"""
        
        divida_label = QLabel(divida_html)
        divida_label.setStyleSheet("color: #111111; background-color: transparent; border: none;")
        layout.addWidget(divida_label)
        layout.addStretch()
        
        return widget
    
    def _criar_botoes_acao(self):
        """Cria layout com botões de ação"""
        layout = QHBoxLayout()
        
        # Botão Nova Venda
        btn_nova = QPushButton("➕ NOVA VENDA FIADA")
        style_button(btn_nova, "primary", min_height=40)
        btn_nova.clicked.connect(self._nova_venda)
        layout.addWidget(btn_nova)
        
        # Botão Pagar
        btn_pagar = QPushButton("✅ MARCAR COMO PAGO")
        style_button(btn_pagar, "success", min_height=40)
        btn_pagar.clicked.connect(self._pagar_selecionado)
        layout.addWidget(btn_pagar)
        
        # Botão Deletar
        btn_deletar = QPushButton("🗑️ DELETAR")
        style_button(btn_deletar, "danger", min_height=40)
        btn_deletar.clicked.connect(self._deletar_selecionado)
        layout.addWidget(btn_deletar)
        
        # Botão Fechar
        btn_fechar = QPushButton("Fechar")
        style_button(btn_fechar, "neutral", min_height=40)
        btn_fechar.clicked.connect(self.accept)
        layout.addWidget(btn_fechar)
        
        return layout
    def _carregar_vendas(self):
        """Carrega vendas fiadas do cliente"""
        vendas = listar_vendas_fiadas_por_cliente(self.cliente['id'])
        
        self.tabela_vendas.setRowCount(0)
        
        if not vendas:
            # Sem vendas
            row = self.tabela_vendas.rowCount()
            self.tabela_vendas.insertRow(row)
            item = QTableWidgetItem("— Nenhuma venda fiada criada —")
            item.setForeground(QColor("#999"))
            self.tabela_vendas.setItem(row, 0, item)
            self.tabela_vendas.setSpan(row, 0, 1, 5)
            _reforcar_contraste(self.tabela_vendas)
            return
        
        for venda in vendas:
            row = self.tabela_vendas.rowCount()
            self.tabela_vendas.insertRow(row)
            
            # ID
            self.tabela_vendas.setItem(row, 0, QTableWidgetItem(str(venda.id)))
            
            # Data
            if isinstance(venda.data_venda, str):
                data_str = venda.data_venda[:10]
            else:
                data_str = venda.data_venda.strftime("%d/%m/%Y")
            self.tabela_vendas.setItem(row, 1, QTableWidgetItem(data_str))
            
            # Produtos (resumo)
            produtos_resumo = ", ".join([p['nome'] for p in venda.produtos[:2]])
            if len(venda.produtos) > 2:
                produtos_resumo += f" +{len(venda.produtos)-2}"
            self.tabela_vendas.setItem(row, 2, QTableWidgetItem(produtos_resumo))
            
            # Valor
            valor_item = QTableWidgetItem(f"R$ {venda.valor_total:.2f}")
            valor_item.setForeground(QColor("#333"))
            self.tabela_vendas.setItem(row, 3, valor_item)
            
            # Status
            status_item = QTableWidgetItem(venda.status)
            if venda.status == "PAGO":
                status_item.setForeground(QColor("#4CAF50"))
                status_item.setBackground(QColor("#e8f5e9"))
            elif venda.status == "INADIMPLENTE":
                status_item.setForeground(QColor("#f44336"))
                status_item.setBackground(QColor("#ffebee"))
            elif venda.status == "PENDENTE":
                status_item.setForeground(QColor("#ff6f00"))
                status_item.setBackground(QColor("#fff3e0"))
            self.tabela_vendas.setItem(row, 4, status_item)
            
            # Armazenar venda_id
            self.tabela_vendas.item(row, 0).venda_id = venda.id
        _reforcar_contraste(self.tabela_vendas)
    
    def _nova_venda(self):
        """Cria nova venda para este cliente"""
        dialog = NovaVendaFiadaDialog(self.cliente, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._carregar_vendas()
    
    def _pagar_selecionado(self):
        """Marca venda selecionada como paga"""
        row = self.tabela_vendas.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione uma venda!")
            return
        
        # Verificar se o item existe e tem o atributo venda_id
        item = self.tabela_vendas.item(row, 0)
        if not item or not hasattr(item, 'venda_id'):
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione uma venda válida!")
            return
        
        venda_id = item.venda_id
        resultado = pagar_venda(venda_id)
        
        if resultado['sucesso']:
            QMessageBox.information(self, "✅ Sucesso", resultado['mensagem'])
            self._carregar_vendas()
        else:
            QMessageBox.warning(self, "❌ Erro", resultado['mensagem'])
    
    def _deletar_selecionado(self):
        """Deleta venda selecionada"""
        row = self.tabela_vendas.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione uma venda!")
            return
        
        # Verificar se o item existe e tem o atributo venda_id
        item = self.tabela_vendas.item(row, 0)
        if not item or not hasattr(item, 'venda_id'):
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione uma venda válida!")
            return
        
        venda_id = item.venda_id
        
        resposta = QMessageBox.question(
            self,
            "⚠️ Confirmar",
            "Tem certeza que deseja deletar esta venda?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            resultado = deletar_venda(venda_id)
            if resultado['sucesso']:
                QMessageBox.information(self, "✅ Sucesso", resultado['mensagem'])
                self._carregar_vendas()
            else:
                QMessageBox.warning(self, "❌ Erro", resultado['mensagem'])
