from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from app.services.estoque_service import buscar_produtos
from app.services.pdv_service import (
    FORMAS_PAGAMENTO,
    registrar_venda_produtos,
    registrar_venda_rapida,
    buscar_vendas_pdv,
)
from app.ui.styles import apply_table_style, style_button, tab_style, title_style


def _moeda(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


FORMAS_PAGAMENTO_PDV = [forma for forma in FORMAS_PAGAMENTO if forma != "Fiado"]


class PDVView(QWidget):
    """PDV opcional: venda por produto ou lancamento rapido por valor."""

    def __init__(self):
        super().__init__()
        self.produtos = []
        self.carrinho = []
        self._setup_ui()
        self.carregar_produtos()
        self.carregar_historico()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("PDV - VENDAS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet(title_style())
        main_layout.addWidget(title)

        dica = QLabel(
            "Use venda por produto quando der tempo. Na correria, use Venda Rapida para registrar o valor no caixa sem baixar estoque item por item."
        )
        dica.setWordWrap(True)
        dica.setStyleSheet("color: #555; padding: 4px;")
        main_layout.addWidget(dica)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(tab_style(compact=True))
        self.tabs.addTab(self._criar_tab_produtos(), "Venda por Produtos")
        self.tabs.addTab(self._criar_tab_rapida(), "Venda Rapida")
        self.tabs.addTab(self._criar_tab_historico(), "Historico")
        main_layout.addWidget(self.tabs)

    def _criar_tab_produtos(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        top = QGridLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Digite nome ou codigo do produto...")
        self.input_busca.textChanged.connect(self._filtrar_produtos)
        top.addWidget(QLabel("Produto:"), 0, 0)
        top.addWidget(self.input_busca, 0, 1, 1, 3)

        self.combo_produtos = QComboBox()
        top.addWidget(self.combo_produtos, 1, 0, 1, 3)

        self.spin_qtd = QSpinBox()
        self.spin_qtd.setRange(1, 9999)
        self.spin_qtd.setValue(1)
        top.addWidget(QLabel("Qtd:"), 1, 3)
        top.addWidget(self.spin_qtd, 1, 4)

        btn_add = QPushButton("Adicionar")
        style_button(btn_add)
        btn_add.clicked.connect(self.adicionar_produto)
        top.addWidget(btn_add, 1, 5)
        layout.addLayout(top)

        self.tabela_carrinho = QTableWidget()
        self.tabela_carrinho.setColumnCount(5)
        self.tabela_carrinho.setHorizontalHeaderLabels(["Produto", "Qtd", "Unitario", "Subtotal", "ID"])
        self.tabela_carrinho.setColumnHidden(4, True)
        apply_table_style(self.tabela_carrinho)
        layout.addWidget(self.tabela_carrinho)

        bottom = QHBoxLayout()
        self.total_label = QLabel("Total: R$ 0,00")
        self.total_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #0D47A1;")
        bottom.addWidget(self.total_label)
        bottom.addStretch()

        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(FORMAS_PAGAMENTO_PDV)
        bottom.addWidget(QLabel("Pagamento:"))
        bottom.addWidget(self.combo_pagamento)

        btn_remover = QPushButton("Remover Item")
        style_button(btn_remover, "neutral")
        btn_remover.clicked.connect(self.remover_item)
        bottom.addWidget(btn_remover)

        btn_limpar = QPushButton("Limpar")
        style_button(btn_limpar, "warning")
        btn_limpar.clicked.connect(self.limpar_carrinho)
        bottom.addWidget(btn_limpar)

        btn_finalizar = QPushButton("Finalizar Venda")
        style_button(btn_finalizar, "success")
        btn_finalizar.clicked.connect(self.finalizar_venda)
        bottom.addWidget(btn_finalizar)
        layout.addLayout(bottom)

        return widget

    def _criar_tab_rapida(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        form = QGridLayout()

        self.valor_rapido = QDoubleSpinBox()
        self.valor_rapido.setRange(0.01, 999999)
        self.valor_rapido.setDecimals(2)
        self.valor_rapido.setPrefix("R$ ")
        form.addWidget(QLabel("Valor recebido:"), 0, 0)
        form.addWidget(self.valor_rapido, 0, 1)

        self.forma_rapida = QComboBox()
        self.forma_rapida.addItems(FORMAS_PAGAMENTO_PDV)
        form.addWidget(QLabel("Pagamento:"), 1, 0)
        form.addWidget(self.forma_rapida, 1, 1)

        self.desc_rapida = QLineEdit()
        self.desc_rapida.setPlaceholderText("Ex: venda balcão sem detalhar itens")
        form.addWidget(QLabel("Descricao:"), 2, 0)
        form.addWidget(self.desc_rapida, 2, 1)

        self.obs_rapida = QTextEdit()
        self.obs_rapida.setMaximumHeight(80)
        form.addWidget(QLabel("Observacoes:"), 3, 0)
        form.addWidget(self.obs_rapida, 3, 1)
        layout.addLayout(form)

        btn = QPushButton("Registrar Venda Rapida")
        style_button(btn, "primary", min_height=42)
        btn.clicked.connect(self.registrar_rapida)
        layout.addWidget(btn)
        layout.addStretch()
        return widget

    def _criar_tab_historico(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(6)
        self.tabela_historico.setHorizontalHeaderLabels(["ID", "Data", "Tipo", "Total", "Pagamento", "Resumo"])
        apply_table_style(self.tabela_historico)
        layout.addWidget(self.tabela_historico)
        btn = QPushButton("Atualizar Historico")
        style_button(btn)
        btn.clicked.connect(self.carregar_historico)
        layout.addWidget(btn)
        return widget

    def carregar_produtos(self):
        self.produtos = buscar_produtos()
        self._popular_combo(self.produtos)

    def _filtrar_produtos(self):
        termo = self.input_busca.text().strip().lower()
        if not termo:
            self._popular_combo(self.produtos)
            return
        filtrados = [
            p for p in self.produtos
            if termo in p["nome"].lower() or termo in p["sku"].lower()
        ]
        self._popular_combo(filtrados)

    def _popular_combo(self, produtos):
        self.combo_produtos.clear()
        for produto in produtos:
            self.combo_produtos.addItem(
                f"{produto['nome']} | {produto['sku']} | {_moeda(produto['preco_venda'])} | Estoque {produto['quantidade']}",
                produto,
            )

    def adicionar_produto(self):
        produto = self.combo_produtos.currentData()
        if not produto:
            QMessageBox.warning(self, "Aviso", "Selecione um produto.")
            return
        qtd = self.spin_qtd.value()
        existente = next((i for i in self.carrinho if i["produto_id"] == produto["id"]), None)
        qtd_no_carrinho = existente["quantidade"] if existente else 0
        if qtd_no_carrinho + qtd > produto["quantidade"]:
            QMessageBox.warning(
                self,
                "Estoque insuficiente",
                f"Disponivel em estoque: {produto['quantidade']}. No carrinho: {qtd_no_carrinho}."
            )
            return
        if existente:
            existente["quantidade"] += qtd
            existente["subtotal"] = existente["quantidade"] * existente["preco_unitario"]
        else:
            self.carrinho.append({
                "produto_id": produto["id"],
                "nome": produto["nome"],
                "quantidade": qtd,
                "preco_unitario": produto["preco_venda"],
                "subtotal": qtd * produto["preco_venda"],
            })
        self._atualizar_carrinho()
        self.input_busca.clear()

    def _atualizar_carrinho(self):
        self.tabela_carrinho.setRowCount(0)
        total = 0
        for item in self.carrinho:
            row = self.tabela_carrinho.rowCount()
            self.tabela_carrinho.insertRow(row)
            valores = [item["nome"], item["quantidade"], _moeda(item["preco_unitario"]), _moeda(item["subtotal"]), item["produto_id"]]
            for col, valor in enumerate(valores):
                cell = QTableWidgetItem(str(valor))
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela_carrinho.setItem(row, col, cell)
            total += item["subtotal"]
        self.total_label.setText(f"Total: {_moeda(total)}")

    def remover_item(self):
        row = self.tabela_carrinho.currentRow()
        if row < 0:
            return
        del self.carrinho[row]
        self._atualizar_carrinho()

    def limpar_carrinho(self):
        self.carrinho = []
        self._atualizar_carrinho()

    def finalizar_venda(self):
        resultado = registrar_venda_produtos(self.carrinho, self.combo_pagamento.currentText())
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.limpar_carrinho()
            self.carregar_produtos()
            self.carregar_historico()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])

    def registrar_rapida(self):
        resultado = registrar_venda_rapida(
            self.valor_rapido.value(),
            self.forma_rapida.currentText(),
            self.desc_rapida.text() or "Venda rapida",
            self.obs_rapida.toPlainText() or None,
        )
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.valor_rapido.setValue(0.01)
            self.desc_rapida.clear()
            self.obs_rapida.clear()
            self.carregar_historico()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])

    def carregar_historico(self):
        vendas = buscar_vendas_pdv()
        self.tabela_historico.setRowCount(0)
        for venda in vendas:
            row = self.tabela_historico.rowCount()
            self.tabela_historico.insertRow(row)
            resumo = ", ".join([item.get("nome", "") for item in venda.get("itens", [])[:2]])
            if len(venda.get("itens", [])) > 2:
                resumo += f" +{len(venda['itens']) - 2}"
            valores = [
                venda["id"],
                str(venda["criado_em"])[:16],
                venda["tipo"],
                _moeda(venda["valor_total"]),
                venda["forma_pagamento"],
                resumo,
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 3:
                    item.setForeground(QColor("#2e7d32"))
                self.tabela_historico.setItem(row, col, item)
