"""
SISTEMA DE GERENCIAMENTO - Tela de Categorias
Interface para gerenciar categorias de produtos
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QDialog, QFormLayout,
    QMessageBox, QHeaderView, QTextEdit, QDialogButtonBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from app.services.categorias_service import (
    obter_todas_categorias, cadastrar_categoria, editar_categoria,
    remover_categoria, ativar_cat
)
from app.ui.styles import apply_table_style, dialog_style, section_title_style, style_button


class CategoriasView(QWidget):
    """Tela de gerenciamento de categorias"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_categorias()
    
    def _setup_ui(self):
        """Configura a interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        title_label = QLabel("📂 Gerenciamento de Categorias")
        title_label.setStyleSheet(section_title_style())
        main_layout.addWidget(title_label)
        
        # Seção de busca
        search_layout = QHBoxLayout()
        
        label_busca = QLabel("🔍 Buscar:")
        search_layout.addWidget(label_busca)
        
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Digite o nome da categoria...")
        self.input_busca.textChanged.connect(self._on_busca_changed)
        search_layout.addWidget(self.input_busca)
        
        btn_limpar = QPushButton("🗑️ Limpar")
        style_button(btn_limpar, "neutral")
        btn_limpar.clicked.connect(self._limpar_busca)
        search_layout.addWidget(btn_limpar)
        
        main_layout.addLayout(search_layout)
        
        # Tabela de categorias
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "Descrição", "Margem Alvo", "Produtos", "Status"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela.setMinimumHeight(300)
        apply_table_style(self.tabela)
        main_layout.addWidget(self.tabela)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        btn_novo = QPushButton("➕ Nova Categoria")
        style_button(btn_novo, "success")
        btn_novo.clicked.connect(self.nova_categoria)
        buttons_layout.addWidget(btn_novo)
        
        btn_editar = QPushButton("✏️ Editar")
        style_button(btn_editar)
        btn_editar.clicked.connect(self.editar_categoria)
        buttons_layout.addWidget(btn_editar)
        
        btn_ativar = QPushButton("✅ Ativar")
        style_button(btn_ativar, "success")
        btn_ativar.clicked.connect(self.ativar_categoria)
        buttons_layout.addWidget(btn_ativar)
        
        btn_deletar = QPushButton("🗑️ Excluir de Vez")
        btn_deletar.setToolTip("Remove a categoria do sistema. Se tiver produtos, eles podem ser movidos para Geral.")
        style_button(btn_deletar, "danger")
        btn_deletar.clicked.connect(self.deletar_categoria)
        buttons_layout.addWidget(btn_deletar)
        
        main_layout.addLayout(buttons_layout)
    
    def carregar_categorias(self, apenas_ativas=False):
        """Carrega categorias na tabela"""
        categorias = obter_todas_categorias(ativas_apenas=apenas_ativas)
        self.tabela.setRowCount(0)
        
        for categoria in categorias:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # ID
            item_id = QTableWidgetItem(str(categoria["id"]))
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 0, item_id)
            
            # Nome
            self.tabela.setItem(row, 1, QTableWidgetItem(categoria["nome"]))
            
            # Descrição
            descricao = categoria.get("descricao") or ""
            self.tabela.setItem(row, 2, QTableWidgetItem(descricao))

            # Margem Alvo
            margem = categoria.get("margem_alvo")
            margem_texto = f"{margem * 100:.1f}%" if margem is not None else "-"
            item_margem = QTableWidgetItem(margem_texto)
            item_margem.setFlags(item_margem.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 3, item_margem)
            
            # Produtos (contar)
            from app.database.categorias_repository import contar_produtos_por_categoria
            num_produtos = contar_produtos_por_categoria(categoria["id"])
            item_produtos = QTableWidgetItem(str(num_produtos))
            item_produtos.setFlags(item_produtos.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabela.setItem(row, 4, item_produtos)
            
            # Status
            status_text = "✅ Ativo" if categoria["ativo"] else "❌ Inativo"
            item_status = QTableWidgetItem(status_text)
            item_status.setFlags(item_status.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if not categoria["ativo"]:
                item_status.setBackground(QColor("#ffebee"))
            self.tabela.setItem(row, 5, item_status)
    
    def _on_busca_changed(self):
        """Realiza busca conforme usuário digita"""
        termo = self.input_busca.text().lower()
        categorias = obter_todas_categorias(ativas_apenas=False)
        self.tabela.setRowCount(0)
        
        for categoria in categorias:
            if termo in categoria["nome"].lower() or termo in (categoria.get("descricao") or "").lower():
                row = self.tabela.rowCount()
                self.tabela.insertRow(row)
                
                item_id = QTableWidgetItem(str(categoria["id"]))
                item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, 0, item_id)
                
                self.tabela.setItem(row, 1, QTableWidgetItem(categoria["nome"]))
                
                descricao = categoria.get("descricao") or ""
                self.tabela.setItem(row, 2, QTableWidgetItem(descricao))

                margem = categoria.get("margem_alvo")
                margem_texto = f"{margem * 100:.1f}%" if margem is not None else "-"
                item_margem = QTableWidgetItem(margem_texto)
                item_margem.setFlags(item_margem.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, 3, item_margem)
                
                from app.database.categorias_repository import contar_produtos_por_categoria
                num_produtos = contar_produtos_por_categoria(categoria["id"])
                item_produtos = QTableWidgetItem(str(num_produtos))
                item_produtos.setFlags(item_produtos.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, 4, item_produtos)
                
                status_text = "✅ Ativo" if categoria["ativo"] else "❌ Inativo"
                item_status = QTableWidgetItem(status_text)
                item_status.setFlags(item_status.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if not categoria["ativo"]:
                    item_status.setBackground(QColor("#ffebee"))
                self.tabela.setItem(row, 5, item_status)
    
    def _limpar_busca(self):
        """Limpa o campo de busca"""
        self.input_busca.clear()
        self.carregar_categorias()
    
    def nova_categoria(self):
        """Abre diálogo para nova categoria"""
        dialog = CategoriaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nome = dialog.input_nome.text()
            descricao = dialog.input_descricao.toPlainText() or None
            margem_alvo = dialog.input_margem.value() / 100.0 if dialog.input_margem.value() > 0 else None
            
            resultado = cadastrar_categoria(nome, descricao, margem_alvo)
            
            if resultado.get("sucesso"):
                QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                self.carregar_categorias()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def editar_categoria(self):
        """Edita categoria selecionada"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria para editar!")
            return
        
        categoria_id = int(self.tabela.item(row, 0).text())
        from app.database.categorias_repository import obter_categoria_por_id
        categoria = obter_categoria_por_id(categoria_id)
        
        if not categoria:
            QMessageBox.warning(self, "Erro", "Categoria não encontrada!")
            return
        
        dialog = CategoriaDialog(self, categoria=categoria)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nome = dialog.input_nome.text()
            descricao = dialog.input_descricao.toPlainText() or None
            margem_alvo = dialog.input_margem.value() / 100.0 if dialog.input_margem.value() > 0 else None
            
            resultado = editar_categoria(categoria_id, nome, descricao, margem_alvo)
            
            if resultado.get("sucesso"):
                QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                self.carregar_categorias()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def ativar_categoria(self):
        """Ativa categoria selecionada"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria para ativar!")
            return
        
        categoria_id = int(self.tabela.item(row, 0).text())
        resultado = ativar_cat(categoria_id)
        
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_categorias()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def deletar_categoria(self):
        """Exclui definitivamente a categoria selecionada."""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma categoria para excluir!")
            return
        
        categoria_id = int(self.tabela.item(row, 0).text())
        categoria_nome = self.tabela.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Excluir Categoria",
            (
                f"Tem certeza que deseja excluir de vez a categoria '{categoria_nome}'?\n\n"
                "Ela nao ficara apenas inativa."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            resultado = remover_categoria(categoria_id, forcado=False)
            
            if resultado.get("sucesso"):
                QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                self.carregar_categorias()
            else:
                # Se tem produtos, perguntar se quer mover para Geral e excluir.
                if resultado.get("num_produtos"):
                    reply2 = QMessageBox.question(
                        self,
                        "Mover Produtos e Excluir",
                        (
                            f"{resultado['mensagem']}\n\n"
                            "Deseja mover esses produtos para 'Geral' e excluir a categoria agora?"
                        ),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply2 == QMessageBox.StandardButton.Yes:
                        resultado = remover_categoria(categoria_id, forcado=True)
                        if resultado.get("sucesso"):
                            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                            self.carregar_categorias()
                        else:
                            QMessageBox.warning(self, "Erro", resultado["mensagem"])
                else:
                    QMessageBox.warning(self, "Erro", resultado["mensagem"])


class CategoriaDialog(QDialog):
    """Diálogo para criar/editar categoria"""
    
    def __init__(self, parent=None, categoria=None):
        super().__init__(parent)
        self.setWindowTitle("Categoria")
        self.setGeometry(200, 200, 500, 300)
        self.setStyleSheet(dialog_style())
        self.categoria = categoria
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura o diálogo"""
        layout = QFormLayout()
        
        self.input_nome = QLineEdit()
        self.input_nome.setMaxLength(50)
        layout.addRow("Nome:", self.input_nome)
        
        self.input_descricao = QTextEdit()
        self.input_descricao.setMaximumHeight(120)
        layout.addRow("Descrição:", self.input_descricao)

        self.input_margem = QDoubleSpinBox()
        self.input_margem.setRange(0, 300)
        self.input_margem.setDecimals(1)
        self.input_margem.setSuffix(" %")
        layout.addRow("Margem Alvo:", self.input_margem)
        
        # Carregar dados se estiver editando
        if self.categoria:
            self.input_nome.setText(self.categoria["nome"])
            self.input_descricao.setPlainText(self.categoria.get("descricao") or "")
            self.input_nome.setReadOnly(True)  # Não permite editar nome
            margem = self.categoria.get("margem_alvo")
            if margem is not None:
                self.input_margem.setValue(margem * 100)
        
        # Botões
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
