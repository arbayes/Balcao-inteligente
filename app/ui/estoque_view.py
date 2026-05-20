"""
SISTEMA DE GERENCIAMENTO - Tela de Estoque
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QDialog, QFormLayout,
    QMessageBox, QHeaderView, QSpinBox, QDialogButtonBox, QDoubleSpinBox,
    QTabWidget, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from app.services.estoque_service import (
    cadastrar_produto, buscar_produtos, obter_produto, editar_produto,
    entrada_estoque, saida_estoque, deletar_produto
)
from app.services.xml_import_service import importar_nfe_xml
from app.ui.categorias_view import CategoriasView
from app.ui.styles import apply_table_style, dialog_style, style_button, tab_style


class EstoqueView(QWidget):
    """Tela de gerenciamento de estoque"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_produtos()
    
    def _setup_ui(self):
        """Configura a interface com sub-abas"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(tab_style(compact=True))
        
        # Aba de Produtos
        produtos_widget = QWidget()
        self._setup_produtos_tab(produtos_widget)
        self.tabs.addTab(produtos_widget, "📦 PRODUTOS")
        
        # Aba de Categorias
        self.categorias_view = CategoriasView()
        self.tabs.addTab(self.categorias_view, "📂 CATEGORIAS")
        
        main_layout.addWidget(self.tabs)
    
    def _setup_produtos_tab(self, widget):
        """Configura a aba de produtos"""
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Seção de busca
        search_layout = QHBoxLayout()
        
        label_busca = QLabel("🔍 Buscar por:")
        search_layout.addWidget(label_busca)
        
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos os campos", "Nome", "Código do Produto"])
        search_layout.addWidget(self.combo_filtro)
        
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Digite o termo de busca...")
        self.input_busca.textChanged.connect(self._on_busca_changed)
        search_layout.addWidget(self.input_busca)
        
        btn_limpar = QPushButton("🗑️ Limpar")
        style_button(btn_limpar, "neutral")
        btn_limpar.clicked.connect(self._limpar_busca)
        search_layout.addWidget(btn_limpar)
        
        main_layout.addLayout(search_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(10)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Categoria", "Nome", "Código do Produto", "Qtd", "Preço Compra", "Preço Venda", "Margem %", "Margem Alvo", "Status"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        apply_table_style(self.tabela)
        main_layout.addWidget(self.tabela)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        btn_novo = QPushButton("➕ Novo Produto")
        style_button(btn_novo, "success")
        btn_novo.clicked.connect(self.new_produto)
        buttons_layout.addWidget(btn_novo)

        btn_importar_xml = QPushButton("📄 Importar XML")
        style_button(btn_importar_xml, "purple")
        btn_importar_xml.clicked.connect(self.importar_xml)
        buttons_layout.addWidget(btn_importar_xml)
        
        btn_editar = QPushButton("✏️ Editar")
        style_button(btn_editar)
        btn_editar.clicked.connect(self.editar_produto)
        buttons_layout.addWidget(btn_editar)
        
        btn_entrada = QPushButton("📥 Entrada")
        style_button(btn_entrada, "success")
        btn_entrada.clicked.connect(self.entrada_produto)
        buttons_layout.addWidget(btn_entrada)
        
        btn_saida = QPushButton("📤 Saída")
        style_button(btn_saida, "warning")
        btn_saida.clicked.connect(self.saida_produto)
        buttons_layout.addWidget(btn_saida)
        
        btn_deletar = QPushButton("🗑️ Deletar")
        style_button(btn_deletar, "danger")
        btn_deletar.clicked.connect(self.deletar_produto)
        buttons_layout.addWidget(btn_deletar)
        
        main_layout.addLayout(buttons_layout)
    
    def carregar_produtos(self):
        """Carrega produtos na tabela"""
        produtos = buscar_produtos()
        self.tabela.setRowCount(0)
        
        for produto in produtos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # ID
            item_id = QTableWidgetItem(str(produto["id"]))
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 0, item_id)
            
            # Categoria
            item_categoria = QTableWidgetItem(produto.get("categoria", "Geral"))
            item_categoria.setFlags(item_categoria.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 1, item_categoria)
            
            # Nome
            self.tabela.setItem(row, 2, QTableWidgetItem(produto["nome"]))
            
            # Código do Produto
            item_sku = QTableWidgetItem(produto["sku"])
            item_sku.setFlags(item_sku.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 3, item_sku)
            
            # Quantidade
            item_qtd = QTableWidgetItem(str(produto["quantidade"]))
            item_qtd.setFlags(item_qtd.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if produto["quantidade"] <= 5:
                item_qtd.setBackground(QColor("#f4657a"))
                item_qtd.setForeground(QColor("#000000"))
            self.tabela.setItem(row, 4, item_qtd)
            
            # Preço Compra
            item_compra = QTableWidgetItem(f"R$ {produto['preco_compra']:.2f}")
            item_compra.setFlags(item_compra.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 5, item_compra)
            
            # Preço Venda
            item_venda = QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}")
            item_venda.setFlags(item_venda.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 6, item_venda)
            
            # Margem %
            item_margem = QTableWidgetItem(f"{produto['margem_lucro']:.1f}%")
            item_margem.setFlags(item_margem.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if produto['margem_lucro'] >= 50:
                item_margem.setBackground(QColor("#4ce94a"))
                item_margem.setForeground(QColor("#000000"))
            else:
                item_margem.setBackground(QColor("#f15151"))
                item_margem.setForeground(QColor("#000000"))
            self.tabela.setItem(row, 7, item_margem)
            
            # Margem Alvo
            margem_alvo = produto.get("margem_alvo")
            margem_alvo_texto = f"{margem_alvo * 100:.1f}%" if margem_alvo is not None else "-"
            item_margem_alvo = QTableWidgetItem(margem_alvo_texto)
            item_margem_alvo.setFlags(item_margem_alvo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 8, item_margem_alvo)

            # Status
            status = "✅ Ativo" if produto["ativo"] else "❌ Inativo"
            item_status = QTableWidgetItem(status)
            item_status.setFlags(item_status.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if not produto["ativo"]:
                item_status.setBackground(QColor("#ffebee"))
                item_status.setForeground(QColor("#000000"))
            self.tabela.setItem(row, 9, item_status)
    
    def _on_busca_changed(self):
        """Realiza busca conforme usuario digita"""
        termo = self.input_busca.text()
        campo_selecionado = self.combo_filtro.currentText()
        
        campo = None
        if campo_selecionado == "Nome":
            campo = "nome"
        elif campo_selecionado == "Código do Produto":
            campo = "sku"
        
        produtos = buscar_produtos(termo if termo else None, campo)
        self.tabela.setRowCount(0)
        
        for produto in produtos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            self.tabela.setItem(row, 0, QTableWidgetItem(str(produto["id"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto.get("categoria", "Geral")))
            self.tabela.setItem(row, 2, QTableWidgetItem(produto["nome"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(produto["sku"]))
            
            item_qtd = QTableWidgetItem(str(produto["quantidade"]))
            if produto["quantidade"] <= 5:
                item_qtd.setBackground(QColor("#ffebee"))
                item_qtd.setForeground(QColor("#000000"))
            self.tabela.setItem(row, 4, item_qtd)
            
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {produto['preco_compra']:.2f}"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}"))
            
            item_margem = QTableWidgetItem(f"{produto['margem_lucro']:.1f}%")
            item_margem.setFlags(item_margem.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if produto['margem_lucro'] >= 50:
                item_margem.setBackground(QColor("#c8e6c9"))
                item_margem.setForeground(QColor("#000000"))
            else:
                item_margem.setBackground(QColor("#ffffff"))
            self.tabela.setItem(row, 7, item_margem)
            
            margem_alvo = produto.get("margem_alvo")
            margem_alvo_texto = f"{margem_alvo * 100:.1f}%" if margem_alvo is not None else "-"
            item_margem_alvo = QTableWidgetItem(margem_alvo_texto)
            item_margem_alvo.setFlags(item_margem_alvo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 8, item_margem_alvo)

            status = "✅ Ativo" if produto["ativo"] else "❌ Inativo"
            item_status = QTableWidgetItem(status)
            item_status.setFlags(item_status.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if not produto["ativo"]:
                item_status.setBackground(QColor("#ffebee"))
                item_status.setForeground(QColor("#000000"))
            self.tabela.setItem(row, 9, item_status)
    
    def _limpar_busca(self):
        """Limpa o campo de busca"""
        self.input_busca.clear()
        self.combo_filtro.setCurrentIndex(0)
        self.carregar_produtos()
    
    def new_produto(self):
        """Abre diálogo para novo produto"""
        dialog = ProdutoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nome = dialog.input_nome.text()
            sku = dialog.input_sku.text()
            preco_compra = dialog.input_preco_compra.value()
            preco_venda = dialog.input_preco_venda.value()
            quantidade = dialog.input_quantidade.value()
            descricao = dialog.input_descricao.text() or None
            categoria = dialog.input_categoria.currentText() or "Geral"
            margem_alvo = dialog.input_margem_alvo.value() / 100.0 if dialog.input_margem_alvo.value() > 0 else None
            
            resultado = cadastrar_produto(nome, sku, preco_compra, preco_venda, quantidade, descricao, categoria, margem_alvo)
            
            if resultado.get("sucesso"):
                mensagem = f"{resultado['mensagem']}\n\n📊 Margem de Lucro: {resultado['margem_lucro']:.1f}%"
                QMessageBox.information(self, "Sucesso", mensagem)
                self.carregar_produtos()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def editar_produto(self):
        """Edita produto selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um produto para editar!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = obter_produto(produto_id)
        
        if not produto:
            QMessageBox.warning(self, "Erro", "Produto não encontrado!")
            return
        
        dialog = ProdutoDialog(self, produto=produto)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nome = dialog.input_nome.text()
            sku = dialog.input_sku.text()
            preco_compra = dialog.input_preco_compra.value()
            preco_venda = dialog.input_preco_venda.value()
            quantidade = dialog.input_quantidade.value()
            descricao = dialog.input_descricao.text() or None
            categoria = dialog.input_categoria.currentText() or "Geral"
            margem_alvo = dialog.input_margem_alvo.value() / 100.0 if dialog.input_margem_alvo.value() > 0 else None
            
            resultado = editar_produto(produto_id, nome, sku, descricao, preco_compra, preco_venda, quantidade, categoria, margem_alvo)
            
            if resultado.get("sucesso"):
                mensagem = resultado["mensagem"]
                if "margem_lucro" in resultado:
                    mensagem += f"\n\n📊 Nova Margem: {resultado['margem_lucro']:.1f}%"
                QMessageBox.information(self, "Sucesso", mensagem)
                self.carregar_produtos()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def entrada_produto(self):
        """Registra entrada de produto"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um produto!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = obter_produto(produto_id)
        
        dialog = MovimentacaoDialog(self, produto["nome"], "Entrada")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            quantidade = dialog.spin_quantidade.value()
            
            resultado = entrada_estoque(produto_id, quantidade)
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_produtos()
    
    def saida_produto(self):
        """Registra saída de produto"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um produto!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = obter_produto(produto_id)
        
        dialog = MovimentacaoDialog(self, produto["nome"], "Saída")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            quantidade = dialog.spin_quantidade.value()
            
            resultado = saida_estoque(produto_id, quantidade)
            if resultado.get("sucesso"):
                QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                self.carregar_produtos()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def deletar_produto(self):
        """Deleta produto selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione um produto para deletar!")
            return
        
        produto_id = int(self.tabela.item(row, 0).text())
        produto = obter_produto(produto_id)
        
        reply = QMessageBox.question(
            self,
            "Confirmar Deleção",
            f"Tem certeza que deseja deletar {produto['nome']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            resultado = deletar_produto(produto_id)
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_produtos()

    def importar_xml(self):
        """Importa itens de uma NF-e via XML e atualiza o estoque"""
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Importar NF-e (XML)",
            "",
            "XML Files (*.xml);;Todos os arquivos (*.*)"
        )
        if not caminho:
            return

        resposta = QMessageBox.question(
            self,
            "Atualizar preço de venda?",
            "Deseja atualizar automaticamente o preço de venda sugerido\n"
            "com base na margem atual (ou 30% padrão)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        auto_ajustar = resposta == QMessageBox.StandardButton.Yes

        margem_alvo = None
        if auto_ajustar:
            margem_valor, ok = QInputDialog.getDouble(
                self,
                "Margem alvo",
                "Defina a margem alvo (%) para ajustar o preço de venda:",
                30.0,
                0.0,
                300.0,
                1
            )
            if ok:
                margem_alvo = margem_valor / 100.0

        resposta_auto_cat = QMessageBox.question(
            self,
            "Auto-categorizar?",
            "Deseja criar categorias automáticas baseadas nos nomes?\n"
            "(ex: 'Cerveja 600ml' → 'Cerveja/600ml')",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        auto_categorizar = resposta_auto_cat == QMessageBox.StandardButton.Yes
        
        # Perguntar sobre cálculo de preço unitário
        resposta_unitario = QMessageBox.question(
            self,
            "Calcular preço unitário?",
            "Deseja calcular preço unitário?\n"
            "(ex: 16 caixas com 24 unidades cada = 384 unidades)\n\n"
            "Útil quando o XML mostra preço da caixa mas você vende unidades.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        unidades_por_embalagem = None
        if resposta_unitario == QMessageBox.StandardButton.Yes:
            unidades, ok = QInputDialog.getInt(
                self,
                "Unidades por embalagem",
                "Quantas unidades vêm em cada embalagem?\n"
                "(ex: caixa com 24 unidades = digite 24)",
                24,
                1,
                1000,
                1
            )
            if ok:
                unidades_por_embalagem = unidades
        
        resultado = importar_nfe_xml(
            caminho,
            auto_atualizar_preco_venda=auto_ajustar,
            margem_alvo=margem_alvo,
            auto_categorizar=auto_categorizar,
            unidades_por_embalagem=unidades_por_embalagem
        )
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Importação concluída", resultado["mensagem"])
            self.carregar_produtos()
        else:
            QMessageBox.warning(self, "Erro na importação", resultado.get("mensagem", "Erro desconhecido"))


class ProdutoDialog(QDialog):
    """Diálogo para criar/editar produto"""
    
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.setWindowTitle("Produto")
        self.setGeometry(200, 200, 450, 350)
        self.setStyleSheet(dialog_style())
        self.produto = produto
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura o diálogo"""
        layout = QFormLayout()
        
        self.input_nome = QLineEdit()
        layout.addRow("Nome:", self.input_nome)
        
        self.input_sku = QLineEdit()
        layout.addRow("Código do Produto:", self.input_sku)
        
        self.input_categoria = QComboBox()
        self.input_categoria.setEditable(True)
        # Carregar categorias do banco de dados
        from app.services.categorias_service import obter_nomes_categorias
        categorias = obter_nomes_categorias(ativas_apenas=True)
        self.input_categoria.addItems(categorias)
        layout.addRow("Categoria:", self.input_categoria)
        
        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("(Opcional - deixe em branco se não houver descrição)")
        layout.addRow("Descrição:", self.input_descricao)
        
        self.input_preco_compra = QDoubleSpinBox()
        self.input_preco_compra.setRange(0, 999999)
        self.input_preco_compra.setDecimals(2)
        layout.addRow("Preço Compra (R$):", self.input_preco_compra)
        
        self.input_preco_venda = QDoubleSpinBox()
        self.input_preco_venda.setRange(0, 999999)
        self.input_preco_venda.setDecimals(2)
        layout.addRow("Preço Venda (R$):", self.input_preco_venda)
        
        self.input_quantidade = QSpinBox()
        self.input_quantidade.setRange(0, 999999)
        layout.addRow("Quantidade:", self.input_quantidade)

        self.input_margem_alvo = QDoubleSpinBox()
        self.input_margem_alvo.setRange(0, 300)
        self.input_margem_alvo.setDecimals(1)
        self.input_margem_alvo.setSuffix(" %")
        layout.addRow("Margem Alvo:", self.input_margem_alvo)
        
        # Carregar dados se estiver editando
        if self.produto:
            self.input_nome.setText(self.produto["nome"])
            self.input_sku.setText(self.produto["sku"])
            self.input_sku.setReadOnly(True)
            categoria = self.produto.get("categoria", "Geral")
            index = self.input_categoria.findText(categoria)
            if index >= 0:
                self.input_categoria.setCurrentIndex(index)
            else:
                self.input_categoria.setEditText(categoria)
            self.input_descricao.setText(self.produto.get("descricao") or "")
            self.input_preco_compra.setValue(self.produto["preco_compra"])
            self.input_preco_venda.setValue(self.produto["preco_venda"])
            self.input_quantidade.setValue(self.produto["quantidade"])
            margem = self.produto.get("margem_alvo")
            if margem is not None:
                self.input_margem_alvo.setValue(margem * 100)
        
        # Botões
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)


class MovimentacaoDialog(QDialog):
    """Diálogo para entrada/saída de estoque"""
    
    def __init__(self, parent=None, produto_nome="", tipo="Entrada"):
        super().__init__(parent)
        self.setWindowTitle(f"{tipo} de Estoque")
        self.setGeometry(250, 250, 350, 150)
        self.setStyleSheet(dialog_style())
        self.tipo = tipo
        self._setup_ui(produto_nome)
    
    def _setup_ui(self, produto_nome):
        """Configura o diálogo"""
        layout = QFormLayout()
        
        label_info = QLabel(f"Produto: {produto_nome}")
        layout.addRow(label_info)
        
        label_tipo = QLabel(f"Tipo: {self.tipo}")
        layout.addRow(label_tipo)
        
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setRange(1, 999999)
        self.spin_quantidade.setValue(1)
        layout.addRow("Quantidade:", self.spin_quantidade)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
