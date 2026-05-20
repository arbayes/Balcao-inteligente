"""
SISTEMA DE GERENCIAMENTO - Tela de Clientes (VERSÃO EXPANDIDA)
Suporta: Email, Endereço, VIP Status, Data última compra, Valor total gasto
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QDialog, QFormLayout,
    QMessageBox, QHeaderView, QCheckBox, QTextEdit, QDialogButtonBox,
    QStyledItemDelegate, QLineEdit as QLineEditDelegate
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
import re

from app.services.clientes_service import (
    cadastrar_cliente, buscar_clientes, obter_cliente, editar_cliente, deletar_cliente
)
from app.ui.styles import apply_table_style, dialog_style, style_button


class MoedaDelegate(QStyledItemDelegate):
    """Delegado customizado para células com moeda (R$)"""
    
    def createEditor(self, parent, option, index):
        """Cria editor para a célula"""
        editor = QLineEditDelegate(parent)
        # Remove R$ para edição
        texto_atual = index.data(Qt.ItemDataRole.DisplayRole) or "R$ 0,00"
        valor_numerico = re.sub(r'[^\d,.-]', '', texto_atual)
        editor.setText(valor_numerico)
        return editor
    
    def setEditorData(self, editor, index):
        """Define dados no editor"""
        pass  # Já feito no createEditor
    
    def setModelData(self, editor, model, index):
        """Salva dados do editor no modelo"""
        texto = editor.text().strip()
        
        # Remove caracteres não numéricos, mantém vírgula e ponto
        texto = re.sub(r'[^\d,.-]', '', texto)
        
        try:
            # Converte para float (aceitando , ou .)
            valor = float(texto.replace(',', '.')) if texto else 0.0
            # Formata para R$ novamente
            modelo = f"R$ {valor:.2f}"
            model.setData(index, modelo, Qt.ItemDataRole.DisplayRole)
        except ValueError:
            # Se não conseguir converter, mantém como estava
            model.setData(index, f"R$ 0,00", Qt.ItemDataRole.DisplayRole)


class ClientesView(QWidget):
    """Tela de gerenciamento de clientes com campos expandidos"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_clientes()
    
    def _setup_ui(self):
        """Configura a interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Seção de busca
        search_layout = QHBoxLayout()
        
        label_busca = QLabel("🔍 Buscar por:")
        search_layout.addWidget(label_busca)
        
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos os campos", "Nome", "CPF", "Telefone", "Email"])
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
        
        # Tabela de clientes com novos campos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "CPF", "Email", "VIP", 
            "Última Compra", "Total Gasto", "Status", "Telefone"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        apply_table_style(self.tabela)
        
        # DESABILITA edição geral na tabela
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Permite edição APENAS na coluna "Total Gasto" (índice 6) com delegado customizado
        self.tabela.setItemDelegateForColumn(6, MoedaDelegate())
        
        main_layout.addWidget(self.tabela)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        btn_novo = QPushButton("➕ Novo Cliente")
        style_button(btn_novo, "success")
        btn_novo.clicked.connect(self.new_cliente)
        buttons_layout.addWidget(btn_novo)
        
        btn_editar = QPushButton("✏️ Editar")
        style_button(btn_editar)
        btn_editar.clicked.connect(self.editar_cliente)
        buttons_layout.addWidget(btn_editar)
        
        btn_deletar = QPushButton("🗑️ Deletar")
        style_button(btn_deletar, "danger")
        btn_deletar.clicked.connect(self.deletar_cliente)
        buttons_layout.addWidget(btn_deletar)
        
        btn_reativar = QPushButton("♻️ Reativar")
        style_button(btn_reativar, "warning")
        btn_reativar.clicked.connect(self.reativar_cliente)
        buttons_layout.addWidget(btn_reativar)
        
        main_layout.addLayout(buttons_layout)
    
    def carregar_clientes(self):
        """Carrega clientes na tabela"""
        clientes = buscar_clientes()
        self.tabela.setRowCount(0)
        
        for cliente in clientes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # ID
            item_id = QTableWidgetItem(str(cliente["id"]))
            item_id.setForeground(QColor("#666"))
            self.tabela.setItem(row, 0, item_id)
            
            # Nome
            item_nome = QTableWidgetItem(cliente["nome"])
            self.tabela.setItem(row, 1, item_nome)
            
            # CPF
            item_cpf = QTableWidgetItem(cliente["cpf"])
            self.tabela.setItem(row, 2, item_cpf)
            
            # Email
            item_email = QTableWidgetItem(cliente.get("email", "") or "")
            self.tabela.setItem(row, 3, item_email)
            
            # VIP
            vip_status = "👑 VIP" if cliente.get("vip") else "—"
            item_vip = QTableWidgetItem(vip_status)
            if cliente.get("vip"):
                item_vip.setBackground(QColor("#FFD700"))
                item_vip.setForeground(QColor("#000"))
            self.tabela.setItem(row, 4, item_vip)
            
            # Última Compra
            data_ultima = cliente.get("data_ultima_compra")
            if data_ultima:
                if isinstance(data_ultima, str):
                    data_str = data_ultima.split(" ")[0]  # Apenas data, não hora
                else:
                    data_str = data_ultima.strftime("%d/%m/%Y") if data_ultima else "—"
            else:
                data_str = "—"
            item_data = QTableWidgetItem(data_str)
            self.tabela.setItem(row, 5, item_data)
            
            # Total Gasto
            total = cliente.get("valor_total_gasto", 0)
            item_total = QTableWidgetItem(f"R$ {total:.2f}")
            self.tabela.setItem(row, 6, item_total)
            
            # Status
            status_text = "✅ Ativo" if cliente["ativo"] else "❌ Inativo"
            item_status = QTableWidgetItem(status_text)
            if cliente["ativo"]:
                item_status.setForeground(QColor("#4CAF50"))
            else:
                item_status.setForeground(QColor("#f44336"))
            self.tabela.setItem(row, 7, item_status)
            
            # Telefone (coluna oculta mas disponível)
            item_telefone = QTableWidgetItem(cliente.get("telefone", "") or "")
            self.tabela.setItem(row, 8, item_telefone)
    
    def _on_busca_changed(self):
        """Realiza busca em tempo real"""
        termo = self.input_busca.text().strip()
        filtro = self.combo_filtro.currentText()
        
        if filtro == "Todos os campos":
            filtro = None
        else:
            filtro = filtro.lower()
        
        clientes = buscar_clientes(termo if termo else None, filtro)
        self.tabela.setRowCount(0)
        
        for cliente in clientes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # Mesmo formato de carregar_clientes
            self.tabela.setItem(row, 0, QTableWidgetItem(str(cliente["id"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente["nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(cliente["cpf"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(cliente.get("email", "") or ""))
            
            vip_status = "👑 VIP" if cliente.get("vip") else "—"
            item_vip = QTableWidgetItem(vip_status)
            if cliente.get("vip"):
                item_vip.setBackground(QColor("#FFD700"))
                item_vip.setForeground(QColor("#000"))
            self.tabela.setItem(row, 4, item_vip)
            
            data_ultima = cliente.get("data_ultima_compra")
            if data_ultima:
                if isinstance(data_ultima, str):
                    data_str = data_ultima.split(" ")[0]
                else:
                    data_str = data_ultima.strftime("%d/%m/%Y") if data_ultima else "—"
            else:
                data_str = "—"
            self.tabela.setItem(row, 5, QTableWidgetItem(data_str))
            
            total = cliente.get("valor_total_gasto", 0)
            self.tabela.setItem(row, 6, QTableWidgetItem(f"R$ {total:.2f}"))
            
            status_text = "✅ Ativo" if cliente["ativo"] else "❌ Inativo"
            item_status = QTableWidgetItem(status_text)
            if cliente["ativo"]:
                item_status.setForeground(QColor("#4CAF50"))
            else:
                item_status.setForeground(QColor("#f44336"))
            self.tabela.setItem(row, 7, item_status)
            
            self.tabela.setItem(row, 8, QTableWidgetItem(cliente.get("telefone", "") or ""))
    
    def _limpar_busca(self):
        """Limpa a busca"""
        self.input_busca.clear()
        self.carregar_clientes()
    
    def new_cliente(self):
        """Abre diálogo para novo cliente"""
        dialog = ClienteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = cadastrar_cliente(
                nome=dialog.input_nome.text(),
                cpf=dialog.input_cpf.text(),
                telefone=dialog.input_telefone.text(),
                email=dialog.input_email.text(),
                endereco=dialog.text_endereco.toPlainText(),
                vip=dialog.checkbox_vip.isChecked()
            )
            
            if resultado["sucesso"]:
                QMessageBox.information(self, "✅ Sucesso", resultado["mensagem"])
                self.carregar_clientes()
            else:
                QMessageBox.warning(self, "❌ Erro", resultado["mensagem"])
    
    def editar_cliente(self):
        """Abre diálogo para editar cliente"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione um cliente para editar.")
            return
        
        cliente_id = int(self.tabela.item(row, 0).text())
        cliente = obter_cliente(cliente_id)
        
        if not cliente:
            QMessageBox.warning(self, "❌ Erro", "Cliente não encontrado.")
            return
        
        dialog = ClienteDialog(self, cliente)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = editar_cliente(
                cliente_id=cliente_id,
                nome=dialog.input_nome.text(),
                cpf=dialog.input_cpf.text(),
                telefone=dialog.input_telefone.text(),
                email=dialog.input_email.text(),
                endereco=dialog.text_endereco.toPlainText(),
                vip=dialog.checkbox_vip.isChecked()
            )
            
            if resultado["sucesso"]:
                QMessageBox.information(self, "✅ Sucesso", resultado["mensagem"])
                self.carregar_clientes()
            else:
                QMessageBox.warning(self, "❌ Erro", resultado["mensagem"])
    
    def deletar_cliente(self):
        """Deleta cliente selecionado"""
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "⚠️ Aviso", "Selecione um cliente para deletar.")
            return
        
        cliente_id = int(self.tabela.item(row, 0).text())
        cliente_nome = self.tabela.item(row, 1).text()
        
        resposta = QMessageBox.question(
            self, 
            "⚠️ Confirmar Deleção",
            f"Tem certeza que deseja deletar '{cliente_nome}'?\n\nEsta ação não pode ser desfeita imediatamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            resultado = deletar_cliente(cliente_id)
            if resultado["sucesso"]:
                QMessageBox.information(self, "✅ Sucesso", resultado["mensagem"])
                self.carregar_clientes()
            else:
                QMessageBox.warning(self, "❌ Erro", resultado["mensagem"])
    
    def reativar_cliente(self):
        """Reativa cliente deletado"""
        QMessageBox.information(
            self, 
            "ℹ️ Informação",
            "Função de reativação será implementada em breve.\n\nContacte o administrador do sistema."
        )


class ClienteDialog(QDialog):
    """Diálogo para criar/editar cliente com todos os campos"""
    
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.cliente = cliente
        self.setWindowTitle("Novo Cliente" if not cliente else f"Editar - {cliente.get('nome', '')}")
        self.setMinimumWidth(400)
        self.setStyleSheet(dialog_style())
        self._setup_ui()
        
        if cliente:
            self._load_cliente_data(cliente)
    
    def _setup_ui(self):
        """Configura o formulário"""
        layout = QFormLayout(self)
        
        # Nome
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome completo do cliente")
        layout.addRow("👤 Nome:", self.input_nome)
        
        # CPF
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("11 dígitos sem pontos")
        layout.addRow("🔢 CPF:", self.input_cpf)
        
        # Telefone
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(opcional)")
        layout.addRow("📞 Telefone:", self.input_telefone)
        
        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("(opcional)")
        layout.addRow("📧 Email:", self.input_email)
        
        # Endereço
        self.text_endereco = QTextEdit()
        self.text_endereco.setPlaceholderText("(opcional - rua, número, complemento, cidade)")
        self.text_endereco.setMaximumHeight(80)
        layout.addRow("🏠 Endereço:", self.text_endereco)
        
        # VIP
        self.checkbox_vip = QCheckBox("Marcar como cliente VIP")
        layout.addRow("👑 VIP:", self.checkbox_vip)
        
        # Botões
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def _load_cliente_data(self, cliente):
        """Carrega dados do cliente no formulário"""
        self.input_nome.setText(cliente.get("nome", ""))
        self.input_cpf.setText(cliente.get("cpf", ""))
        self.input_telefone.setText(cliente.get("telefone", "") or "")
        self.input_email.setText(cliente.get("email", "") or "")
        self.text_endereco.setPlainText(cliente.get("endereco", "") or "")
        self.checkbox_vip.setChecked(cliente.get("vip", False))
