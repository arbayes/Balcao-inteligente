"""
VIEW DE COMPRAS DE FORNECEDOR
Interface para gerenciar compras/pedidos de um fornecedor específico
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QSpinBox, QDoubleSpinBox, QMessageBox, QComboBox, QDateEdit,
    QHeaderView, QCheckBox, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from datetime import datetime
from app.models.compra_fornecedor import ItemCompra, CompraFornecedor
from app.database.estoque_repository import listar_produtos
from app.database.compras_repository import (
    listar_compras_fornecedor,
    obter_compra_por_id,
    atualizar_compra
)
from app.services.compras_service import (
    registrar_compra,
    marcar_entregue,
    registrar_pagamento,
    deletar_compra_com_estoque
)
from app.ui.styles import apply_table_style, button_style, dialog_style, style_button, style_icon_button, title_style, window_style


class ComprasFornecedorView(QWidget):
    """View para gerenciar compras de um fornecedor"""
    
    def __init__(self, fornecedor_id: int, fornecedor_nome: str):
        super().__init__()
        self.fornecedor_id = fornecedor_id
        self.fornecedor_nome = fornecedor_nome
        self.setWindowTitle(f"📦 COMPRAS - {fornecedor_nome}")
        self.setMinimumSize(400, 300)
        self.resize(400, 300)
        self.setStyleSheet(window_style())
        self.setup_ui()
        self.carregar_compras()
    
    def setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title_label = QLabel(f"📦 COMPRAS - {self.fornecedor_nome}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(title_style())
        layout.addWidget(title_label)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.btn_nova_compra = QPushButton("➕ Nova Compra")
        style_button(self.btn_nova_compra, "success")
        self.btn_nova_compra.clicked.connect(self.nova_compra)
        buttons_layout.addWidget(self.btn_nova_compra)
        
        buttons_layout.addStretch()
        
        self.btn_atualizar = QPushButton("🔄 Atualizar")
        style_button(self.btn_atualizar, "neutral")
        self.btn_atualizar.clicked.connect(self.carregar_compras)
        buttons_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(buttons_layout)
        
        # Tabela de compras
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Data", "Valor Total", "Status", "Pagamento", "Ações"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        apply_table_style(self.table, stretch=False)
        
        self.table.doubleClicked.connect(self.editar_compra_selected)
        layout.addWidget(self.table)
    
    def _get_button_style(self):
        """Retorna estilo dos botões"""
        return button_style()
    
    def carregar_compras(self):
        """Carrega compras do fornecedor"""
        self.table.setRowCount(0)
        
        try:
            compras = listar_compras_fornecedor(self.fornecedor_id)
            
            for compra in compras:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(compra.id)))
                
                # Data
                data_texto = compra.data_pedido.strftime("%d/%m/%Y") if compra.data_pedido else "-"
                self.table.setItem(row, 1, QTableWidgetItem(data_texto))
                
                # Valor
                self.table.setItem(row, 2, QTableWidgetItem(f"R$ {compra.valor_total:.2f}"))
                
                # Status
                status_item = QTableWidgetItem(compra.status)
                if compra.status == "PENDENTE":
                    status_item.setForeground(QColor("#FF6B6B"))
                elif compra.status == "ENTREGUE":
                    status_item.setForeground(QColor("#51CF66"))
                self.table.setItem(row, 3, status_item)
                
                # Pagamento
                pag_texto = "✓ Pago" if compra.pago else "⏳ Pendente"
                pag_item = QTableWidgetItem(pag_texto)
                if compra.pago:
                    pag_item.setForeground(QColor("#51CF66"))
                else:
                    pag_item.setForeground(QColor("#FF6B6B"))
                self.table.setItem(row, 4, pag_item)
                
                # Botões
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(2, 2, 2, 2)
                
                btn_editar = QPushButton("✏️ Editar")
                style_button(btn_editar, "primary", min_height=28)
                btn_editar.clicked.connect(lambda checked, cid=compra.id: self.editar_compra(cid))
                btn_editar.setMaximumWidth(80)
                btn_layout.addWidget(btn_editar)
                
                if compra.status == "PENDENTE":
                    btn_entregar = QPushButton("📦 Entregue")
                    style_button(btn_entregar, "success", min_height=28)
                    btn_entregar.clicked.connect(lambda checked, cid=compra.id: self.marcar_entregue(cid))
                    btn_entregar.setMaximumWidth(100)
                    btn_layout.addWidget(btn_entregar)
                
                if compra.status == "ENTREGUE" and not compra.pago:
                    btn_pagar = QPushButton("💰 Pagar")
                    style_button(btn_pagar, "success", min_height=28)
                    btn_pagar.clicked.connect(lambda checked, cid=compra.id: self.registrar_pagamento(cid))
                    btn_pagar.setMaximumWidth(80)
                    btn_layout.addWidget(btn_pagar)
                
                btn_deletar = QPushButton("🗑️ Deletar")
                style_button(btn_deletar, "danger", min_height=28)
                btn_deletar.clicked.connect(lambda checked, cid=compra.id: self.deletar_compra(cid))
                btn_deletar.setMaximumWidth(80)
                btn_layout.addWidget(btn_deletar)
                
                btn_layout.addStretch()
                
                widget = QWidget()
                widget.setLayout(btn_layout)
                self.table.setCellWidget(row, 5, widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar compras: {str(e)}")
    
    def nova_compra(self):
        """Abre dialog para criar nova compra"""
        dialog = NovaCompraDialog(self, self.fornecedor_id)
        if dialog.exec():
            self.carregar_compras()
    
    def editar_compra(self, compra_id: int):
        """Abre dialog para editar compra"""
        compra = obter_compra_por_id(compra_id)
        if compra:
            dialog = EditarCompraDialog(self, compra)
            if dialog.exec():
                self.carregar_compras()
    
    def editar_compra_selected(self):
        """Edita a compra selecionada"""
        row = self.table.currentRow()
        if row >= 0:
            compra_id = int(self.table.item(row, 0).text())
            self.editar_compra(compra_id)
    
    def marcar_entregue(self, compra_id: int):
        """Marca compra como entregue"""
        resultado = marcar_entregue(compra_id)
        if resultado["sucesso"]:
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_compras()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def registrar_pagamento(self, compra_id: int):
        """Registra pagamento da compra"""
        resultado = registrar_pagamento(compra_id)
        if resultado["sucesso"]:
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_compras()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def deletar_compra(self, compra_id: int):
        """Deleta uma compra"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja realmente deletar esta compra?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            resultado = deletar_compra_com_estoque(compra_id)
            if resultado.get("sucesso"):
                QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                self.carregar_compras()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])


class NovaCompraDialog(QDialog):
    """Dialog para criar nova compra"""
    
    def __init__(self, parent, fornecedor_id):
        super().__init__(parent)
        self.fornecedor_id = fornecedor_id
        self.itens = []
        self.produtos_disponiveis = listar_produtos()
        self.setWindowTitle("➕ Nova Compra")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setStyleSheet(dialog_style())
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)
        
        # Form para dados da compra
        form = QFormLayout()
        
        self.forma_pag_combo = QComboBox()
        self.forma_pag_combo.addItems(["", "À vista", "Boleto 7 dias", "Boleto 14 dias", "Boleto 30 dias", "Pix", "Outro"])
        form.addRow("Forma de Pagamento:", self.forma_pag_combo)
        
        self.data_entrega_edit = QDateEdit()
        self.data_entrega_edit.setDate(QDate.currentDate())
        form.addRow("Data Entrega Esperada:", self.data_entrega_edit)
        
        self.observacoes_edit = QTextEdit()
        self.observacoes_edit.setMaximumHeight(80)
        form.addRow("Observações:", self.observacoes_edit)
        
        layout.addLayout(form)
        
        # Tabela de itens
        label_itens = QLabel("Produtos da Compra:")
        label_itens.setStyleSheet("font-weight: bold;")
        layout.addWidget(label_itens)
        
        self.table_itens = QTableWidget()
        self.table_itens.setColumnCount(5)
        self.table_itens.setHorizontalHeaderLabels(["Produto", "Quantidade", "Preço Unit.", "Subtotal", "Ações"])
        self.table_itens.setMaximumHeight(200)
        apply_table_style(self.table_itens)
        layout.addWidget(self.table_itens)
        
        # Botão adicionar item
        btn_add_item = QPushButton("➕ Adicionar Item")
        style_button(btn_add_item, "success")
        btn_add_item.clicked.connect(self.adicionar_item)
        layout.addWidget(btn_add_item)
        
        # Total
        self.label_total = QLabel("Total: R$ 0.00")
        self.label_total.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.label_total)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("❌ Cancelar")
        style_button(btn_cancelar, "neutral")
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton("💾 Salvar")
        style_button(btn_salvar, "success")
        btn_salvar.clicked.connect(self.salvar)
        buttons_layout.addWidget(btn_salvar)
        
        layout.addLayout(buttons_layout)
    
    def adicionar_item(self):
        """Abre dialog para adicionar item"""
        dialog = ItemCompraDialog(self, self.produtos_disponiveis)
        if dialog.exec():
            item = dialog.obter_item()
            self.itens.append(item)
            self._atualizar_tabela_itens()
    
    def _atualizar_tabela_itens(self):
        """Atualiza tabela de itens"""
        self.table_itens.setRowCount(0)
        total = 0
        
        for i, item in enumerate(self.itens):
            self.table_itens.insertRow(i)
            
            self.table_itens.setItem(i, 0, QTableWidgetItem(item.produto_nome))
            self.table_itens.setItem(i, 1, QTableWidgetItem(str(item.quantidade)))
            self.table_itens.setItem(i, 2, QTableWidgetItem(f"R$ {item.preco_unitario:.2f}"))
            self.table_itens.setItem(i, 3, QTableWidgetItem(f"R$ {item.subtotal:.2f}"))
            
            btn_remover = QPushButton("🗑️")
            style_icon_button(btn_remover, "danger")
            btn_remover.clicked.connect(lambda checked, idx=i: self._remover_item(idx))
            self.table_itens.setCellWidget(i, 4, btn_remover)
            
            total += item.subtotal
        
        self.label_total.setText(f"Total: R$ {total:.2f}")
    
    def _remover_item(self, index):
        """Remove item da lista"""
        if 0 <= index < len(self.itens):
            self.itens.pop(index)
            self._atualizar_tabela_itens()
    
    def salvar(self):
        """Salva a nova compra"""
        if not self.itens:
            QMessageBox.warning(self, "Atenção", "Adicione pelo menos um item!")
            return
        
        resultado = registrar_compra(
            self.fornecedor_id,
            self.itens,
            self.forma_pag_combo.currentText() or None,
            self.observacoes_edit.toPlainText() or None
        )
        
        if resultado["sucesso"]:
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])


class ItemCompraDialog(QDialog):
    """Dialog para adicionar item à compra"""
    
    def __init__(self, parent, produtos):
        super().__init__(parent)
        self.produtos = produtos
        self.setWindowTitle("Adicionar Item")
        self.setMinimumWidth(400)
        self.setStyleSheet(dialog_style())
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.produto_combo = QComboBox()
        for produto in self.produtos:
            self.produto_combo.addItem(f"{produto.nome} (R$ {produto.preco_venda:.2f})", produto.id)
        form.addRow("Produto:", self.produto_combo)
        
        self.quantidade_spin = QSpinBox()
        self.quantidade_spin.setMinimum(1)
        self.quantidade_spin.setValue(1)
        form.addRow("Quantidade:", self.quantidade_spin)
        
        self.preco_double = QDoubleSpinBox()
        self.preco_double.setMinimum(0)
        self.preco_double.setDecimals(2)
        self.preco_double.setValue(0)
        form.addRow("Preço Unitário:", self.preco_double)
        
        layout.addLayout(form)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        style_button(btn_cancelar, "neutral")
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        btn_adicionar = QPushButton("Adicionar")
        style_button(btn_adicionar, "success")
        btn_adicionar.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_adicionar)
        
        layout.addLayout(buttons_layout)
    
    def obter_item(self):
        """Retorna o item criado"""
        produto_id = self.produto_combo.currentData()
        produto_nome = self.produto_combo.currentText().split(" (")[0]
        
        return ItemCompra(
            produto_id=produto_id,
            produto_nome=produto_nome,
            quantidade=self.quantidade_spin.value(),
            preco_unitario=self.preco_double.value()
        )


class EditarCompraDialog(QDialog):
    """Dialog para editar compra existente"""
    
    def __init__(self, parent, compra):
        super().__init__(parent)
        self.compra = compra
        self.status_original = compra.status
        self.setWindowTitle("✏️ Editar Compra")
        self.setMinimumWidth(500)
        self.setStyleSheet(dialog_style())
        self.setup_ui()
        self.preencher_dados()
    
    def setup_ui(self):
        """Configura interface"""
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["PENDENTE", "ENTREGUE", "CANCELADA"])
        form.addRow("Status:", self.status_combo)
        
        self.forma_pag_combo = QComboBox()
        self.forma_pag_combo.addItems(["", "À vista", "Boleto 7 dias", "Boleto 14 dias", "Boleto 30 dias", "Pix", "Outro"])
        form.addRow("Forma de Pagamento:", self.forma_pag_combo)
        
        self.data_entrega_edit = QDateEdit()
        form.addRow("Data Entrega Esperada:", self.data_entrega_edit)
        
        self.pago_check = QCheckBox("Pago")
        form.addRow("Situação de Pagamento:", self.pago_check)
        
        self.data_pagamento_edit = QDateEdit()
        form.addRow("Data do Pagamento:", self.data_pagamento_edit)
        
        self.observacoes_edit = QTextEdit()
        self.observacoes_edit.setMaximumHeight(80)
        form.addRow("Observações:", self.observacoes_edit)
        
        layout.addLayout(form)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        btn_cancelar = QPushButton("❌ Cancelar")
        style_button(btn_cancelar, "neutral")
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton("💾 Salvar")
        style_button(btn_salvar, "success")
        btn_salvar.clicked.connect(self.salvar)
        buttons_layout.addWidget(btn_salvar)
        
        layout.addLayout(buttons_layout)
    
    def preencher_dados(self):
        """Preenche os campos com dados da compra"""
        self.status_combo.setCurrentText(self.compra.status)
        
        if self.compra.forma_pagamento:
            idx = self.forma_pag_combo.findText(self.compra.forma_pagamento)
            if idx >= 0:
                self.forma_pag_combo.setCurrentIndex(idx)
        
        if self.compra.data_entrega_esperada:
            self.data_entrega_edit.setDate(self.compra.data_entrega_esperada.date())
        
        self.pago_check.setChecked(self.compra.pago)
        
        if self.compra.data_pagamento_real:
            self.data_pagamento_edit.setDate(self.compra.data_pagamento_real.date())
        
        self.observacoes_edit.setPlainText(self.compra.observacoes or "")
    
    def salvar(self):
        """Salva alterações"""
        novo_status = self.status_combo.currentText()
        if self.status_original == "ENTREGUE" and novo_status != "ENTREGUE":
            QMessageBox.warning(
                self,
                "Estoque ja atualizado",
                "Esta compra ja entrou no estoque. Para desfazer, ajuste o estoque manualmente antes de mudar o status."
            )
            return

        self.compra.status = self.status_original if (
            self.status_original != "ENTREGUE" and novo_status == "ENTREGUE"
        ) else novo_status
        self.compra.forma_pagamento = self.forma_pag_combo.currentText() or None
        self.compra.data_entrega_esperada = datetime.combine(self.data_entrega_edit.date().toPyDate(), datetime.min.time())
        self.compra.pago = self.pago_check.isChecked()
        
        if self.pago_check.isChecked():
            self.compra.data_pagamento_real = datetime.combine(self.data_pagamento_edit.date().toPyDate(), datetime.min.time())
        
        self.compra.observacoes = self.observacoes_edit.toPlainText() or None
        
        if atualizar_compra(self.compra):
            if self.status_original != "ENTREGUE" and novo_status == "ENTREGUE":
                resultado = marcar_entregue(self.compra.id)
                if not resultado.get("sucesso"):
                    QMessageBox.warning(self, "Erro", resultado["mensagem"])
                    return
            QMessageBox.information(self, "Sucesso", "Compra atualizada")
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", "Erro ao atualizar compra")
