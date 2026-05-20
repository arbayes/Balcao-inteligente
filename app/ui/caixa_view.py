from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QDoubleSpinBox, QTextEdit, QComboBox, QLineEdit, QMessageBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from app.services.caixa_service import (
    TIPOS_MOVIMENTO,
    FORMAS_PAGAMENTO,
    abrir_caixa,
    registrar_movimento,
    fechar_caixa,
    obter_resumo_caixa,
    historico_caixas,
)
from app.ui.styles import apply_table_style, dialog_style, style_button, style_card, title_style


def _moeda(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class CaixaView(QWidget):
    """Tela de abertura, movimentacao e fechamento de caixa."""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_dados()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        title = QLabel("FECHAMENTO DE CAIXA")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(title_style())
        main_layout.addWidget(title)

        self.status_label = QLabel("Caixa fechado")
        self.status_label.setStyleSheet("font-weight: bold; color: #0D47A1; padding: 4px;")
        main_layout.addWidget(self.status_label)

        cards_layout = QGridLayout()
        self.card_esperado = self._criar_card("Saldo esperado", "R$ 0,00", "#1976D2")
        self.card_entradas = self._criar_card("Entradas", "R$ 0,00", "#2e7d32")
        self.card_saidas = self._criar_card("Saidas", "R$ 0,00", "#b71c1c")
        self.card_movimentos = self._criar_card("Movimentos", "0", "#bf4f00")
        cards_layout.addWidget(self.card_esperado, 0, 0)
        cards_layout.addWidget(self.card_entradas, 0, 1)
        cards_layout.addWidget(self.card_saidas, 0, 2)
        cards_layout.addWidget(self.card_movimentos, 0, 3)
        main_layout.addLayout(cards_layout)

        buttons_layout = QHBoxLayout()
        self.btn_abrir = QPushButton("Abrir Caixa")
        style_button(self.btn_abrir, "success")
        self.btn_abrir.clicked.connect(self.abrir_caixa_dialog)
        buttons_layout.addWidget(self.btn_abrir)

        self.btn_movimento = QPushButton("Registrar Movimento")
        style_button(self.btn_movimento)
        self.btn_movimento.clicked.connect(self.movimento_dialog)
        buttons_layout.addWidget(self.btn_movimento)

        self.btn_fechar = QPushButton("Fechar Caixa")
        style_button(self.btn_fechar, "danger")
        self.btn_fechar.clicked.connect(self.fechar_caixa_dialog)
        buttons_layout.addWidget(self.btn_fechar)

        self.btn_atualizar = QPushButton("Atualizar")
        style_button(self.btn_atualizar, "neutral")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        buttons_layout.addWidget(self.btn_atualizar)
        main_layout.addLayout(buttons_layout)

        self.tabela_movimentos = QTableWidget()
        self.tabela_movimentos.setColumnCount(6)
        self.tabela_movimentos.setHorizontalHeaderLabels([
            "Hora", "Tipo", "Descricao", "Valor", "Forma", "Origem"
        ])
        apply_table_style(self.tabela_movimentos)
        main_layout.addWidget(QLabel("Movimentos do caixa atual"))
        main_layout.addWidget(self.tabela_movimentos)

        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(7)
        self.tabela_historico.setHorizontalHeaderLabels([
            "ID", "Abertura", "Fechamento", "Esperado", "Contado", "Diferenca", "Status"
        ])
        apply_table_style(self.tabela_historico)
        main_layout.addWidget(QLabel("Historico recente"))
        main_layout.addWidget(self.tabela_historico)

    def _criar_card(self, titulo, valor, cor):
        widget = QWidget()
        style_card(widget, cor)
        layout = QVBoxLayout(widget)
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("color: #555; font-weight: bold;")
        label_valor = QLabel(valor)
        label_valor.setObjectName("valor")
        label_valor.setStyleSheet(f"color: {cor}; font-size: 16px; font-weight: bold;")
        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)
        widget.valor_label = label_valor
        return widget

    def carregar_dados(self):
        resumo = obter_resumo_caixa()
        self.btn_movimento.setEnabled(bool(resumo))
        self.btn_fechar.setEnabled(bool(resumo))
        self.btn_abrir.setEnabled(not bool(resumo))

        if resumo:
            caixa = resumo["caixa"]
            self.status_label.setText(f"Caixa aberto #{caixa['id']} desde {self._formatar_data(caixa['data_abertura'])}")
            self.card_esperado.valor_label.setText(_moeda(resumo["saldo_esperado"]))
            self.card_entradas.valor_label.setText(_moeda(resumo["total_entradas"]))
            self.card_saidas.valor_label.setText(_moeda(resumo["total_saidas"]))
            self.card_movimentos.valor_label.setText(str(len(resumo["movimentos"])))
            self._carregar_movimentos(resumo["movimentos"])
        else:
            self.status_label.setText("Caixa fechado")
            self.card_esperado.valor_label.setText("R$ 0,00")
            self.card_entradas.valor_label.setText("R$ 0,00")
            self.card_saidas.valor_label.setText("R$ 0,00")
            self.card_movimentos.valor_label.setText("0")
            self.tabela_movimentos.setRowCount(0)

        self._carregar_historico()

    def _carregar_movimentos(self, movimentos):
        self.tabela_movimentos.setRowCount(0)
        for movimento in movimentos:
            row = self.tabela_movimentos.rowCount()
            self.tabela_movimentos.insertRow(row)
            valores = [
                self._formatar_data(movimento["criado_em"]),
                TIPOS_MOVIMENTO.get(movimento["tipo"], movimento["tipo"]),
                movimento["descricao"],
                _moeda(movimento["valor"]),
                movimento["forma_pagamento"],
                movimento["origem"],
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 3:
                    cor = "#b71c1c" if movimento["tipo"] in ("SAIDA", "SANGRIA") else "#2e7d32"
                    item.setForeground(QColor(cor))
                self.tabela_movimentos.setItem(row, col, item)

    def _carregar_historico(self):
        caixas = historico_caixas()
        self.tabela_historico.setRowCount(0)
        for caixa in caixas:
            row = self.tabela_historico.rowCount()
            self.tabela_historico.insertRow(row)
            valores = [
                caixa["id"],
                self._formatar_data(caixa["data_abertura"]),
                self._formatar_data(caixa["data_fechamento"]) if caixa["data_fechamento"] else "-",
                _moeda(caixa["saldo_esperado"] if caixa["saldo_esperado"] is not None else caixa["saldo_inicial"]),
                _moeda(caixa["saldo_contado"]) if caixa["saldo_contado"] is not None else "-",
                _moeda(caixa["diferenca"]) if caixa["diferenca"] is not None else "-",
                caixa["status"],
            ]
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 5 and caixa["diferenca"] is not None:
                    item.setForeground(QColor("#b71c1c" if abs(caixa["diferenca"]) > 0.009 else "#2e7d32"))
                self.tabela_historico.setItem(row, col, item)

    def abrir_caixa_dialog(self):
        dialog = AbrirCaixaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = abrir_caixa(dialog.saldo.value(), dialog.obs.toPlainText() or None)
            self._mostrar_resultado(resultado)

    def movimento_dialog(self):
        dialog = MovimentoCaixaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = registrar_movimento(
                dialog.tipo.currentData(),
                dialog.descricao.text(),
                dialog.valor.value(),
                dialog.forma.currentText(),
            )
            self._mostrar_resultado(resultado)

    def fechar_caixa_dialog(self):
        resumo = obter_resumo_caixa()
        dialog = FecharCaixaDialog(resumo["saldo_esperado"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = fechar_caixa(dialog.saldo.value(), dialog.obs.toPlainText() or None)
            if resultado.get("sucesso"):
                QMessageBox.information(
                    self,
                    "Caixa Fechado",
                    f"Esperado: {_moeda(resultado['saldo_esperado'])}\n"
                    f"Contado: {_moeda(resultado['saldo_contado'])}\n"
                    f"Diferenca: {_moeda(resultado['diferenca'])}"
                )
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])

    def _mostrar_resultado(self, resultado):
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_dados()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])

    def _formatar_data(self, valor):
        if not valor:
            return "-"
        texto = str(valor)
        return texto[:16].replace("T", " ")


class AbrirCaixaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Abrir Caixa")
        self.setStyleSheet(dialog_style())
        layout = QFormLayout(self)
        self.saldo = QDoubleSpinBox()
        self.saldo.setRange(0, 999999)
        self.saldo.setDecimals(2)
        self.saldo.setPrefix("R$ ")
        layout.addRow("Saldo inicial:", self.saldo)
        self.obs = QTextEdit()
        self.obs.setMaximumHeight(80)
        layout.addRow("Observacoes:", self.obs)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class MovimentoCaixaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Movimento")
        self.setMinimumWidth(420)
        self.setStyleSheet(dialog_style())
        layout = QFormLayout(self)
        self.tipo = QComboBox()
        for chave, texto in TIPOS_MOVIMENTO.items():
            if chave != "ENTRADA":
                self.tipo.addItem(texto, chave)
        self.tipo.insertItem(0, "Entrada", "ENTRADA")
        layout.addRow("Tipo:", self.tipo)
        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex: venda avulsa, compra pequena, sangria")
        layout.addRow("Descricao:", self.descricao)
        self.valor = QDoubleSpinBox()
        self.valor.setRange(0.01, 999999)
        self.valor.setDecimals(2)
        self.valor.setPrefix("R$ ")
        layout.addRow("Valor:", self.valor)
        self.forma = QComboBox()
        self.forma.addItems(FORMAS_PAGAMENTO)
        layout.addRow("Forma:", self.forma)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class FecharCaixaDialog(QDialog):
    def __init__(self, saldo_esperado, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fechar Caixa")
        self.setStyleSheet(dialog_style())
        layout = QFormLayout(self)
        esperado = QLabel(_moeda(saldo_esperado))
        esperado.setStyleSheet("font-weight: bold; color: #1976D2;")
        layout.addRow("Saldo esperado:", esperado)
        self.saldo = QDoubleSpinBox()
        self.saldo.setRange(0, 999999)
        self.saldo.setDecimals(2)
        self.saldo.setPrefix("R$ ")
        self.saldo.setValue(float(saldo_esperado or 0))
        layout.addRow("Saldo contado:", self.saldo)
        self.obs = QTextEdit()
        self.obs.setMaximumHeight(80)
        layout.addRow("Observacoes:", self.obs)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
