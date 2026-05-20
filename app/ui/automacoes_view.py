from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDialog, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QMessageBox, QHeaderView,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from app.services.automacoes_service import (
    obter_opcoes_automacao,
    buscar_automacoes,
    salvar_automacao,
    mudar_status_automacao,
    remover_automacao,
    testar_automacao,
)
from app.ui.styles import apply_table_style, dialog_style, style_button, title_style


class AutomacoesView(QWidget):
    """Tela para cadastrar e acompanhar automacoes simples."""

    def __init__(self):
        super().__init__()
        self.gatilhos, self.acoes = obter_opcoes_automacao()
        self._setup_ui()
        self.carregar_automacoes()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("AUTOMAÇÕES")
        title_label.setStyleSheet(title_style())
        main_layout.addWidget(title_label)

        subtitle = QLabel("Regras automaticas para avisos, fiado, estoque e backups.")
        subtitle.setStyleSheet("color: #555; padding-bottom: 6px;")
        main_layout.addWidget(subtitle)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Nome", "Gatilho", "Limite", "Acao", "Intervalo",
            "Status", "Ultima execucao", "Resultado"
        ])
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela.setMinimumHeight(320)
        apply_table_style(self.tabela)
        main_layout.addWidget(self.tabela)

        buttons_layout = QHBoxLayout()

        btn_nova = QPushButton("Nova")
        style_button(btn_nova, "success")
        btn_nova.clicked.connect(self.nova_automacao)
        buttons_layout.addWidget(btn_nova)

        btn_editar = QPushButton("Editar")
        style_button(btn_editar)
        btn_editar.clicked.connect(self.editar_automacao)
        buttons_layout.addWidget(btn_editar)

        btn_status = QPushButton("Ativar/Desativar")
        style_button(btn_status, "warning")
        btn_status.clicked.connect(self.alternar_status)
        buttons_layout.addWidget(btn_status)

        btn_testar = QPushButton("Testar")
        style_button(btn_testar, "purple")
        btn_testar.clicked.connect(self.testar_selecionada)
        buttons_layout.addWidget(btn_testar)

        btn_deletar = QPushButton("Deletar")
        style_button(btn_deletar, "danger")
        btn_deletar.clicked.connect(self.deletar_automacao)
        buttons_layout.addWidget(btn_deletar)

        btn_atualizar = QPushButton("Atualizar")
        style_button(btn_atualizar, "neutral")
        btn_atualizar.clicked.connect(self.carregar_automacoes)
        buttons_layout.addWidget(btn_atualizar)

        main_layout.addLayout(buttons_layout)

    def carregar_automacoes(self):
        automacoes = buscar_automacoes()
        self.tabela.setRowCount(0)

        for automacao in automacoes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)

            valores = [
                str(automacao["id"]),
                automacao["nome"],
                self.gatilhos.get(automacao["gatilho"], automacao["gatilho"]),
                self._formatar_limite(automacao),
                self.acoes.get(automacao["acao"], automacao["acao"]),
                f"{automacao['intervalo_minutos']} min",
                "Ativa" if automacao["ativo"] else "Inativa",
                automacao.get("ultima_execucao") or "-",
                automacao.get("ultima_mensagem") or "-",
            ]

            for col, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setForeground(QColor("#111111"))
                if col == 6:
                    item.setBackground(QColor("#E8F5E9") if automacao["ativo"] else QColor("#FFEBEE"))
                    item.setForeground(QColor("#2e7d32") if automacao["ativo"] else QColor("#b71c1c"))
                self.tabela.setItem(row, col, item)

    def _formatar_limite(self, automacao):
        limite = automacao.get("valor_limite") or 0
        if automacao["gatilho"] == "estoque_baixo":
            return f"<= {limite:g} un."
        if automacao["gatilho"] == "fiado_pendente":
            return f">= R$ {limite:.2f}"
        return "-"

    def _automacao_selecionada(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma automacao.")
            return None

        automacao_id = int(self.tabela.item(row, 0).text())
        for automacao in buscar_automacoes():
            if automacao["id"] == automacao_id:
                return automacao
        return None

    def nova_automacao(self):
        dialog = AutomacaoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = salvar_automacao(**dialog.obter_dados())
            self._mostrar_resultado(resultado)

    def editar_automacao(self):
        automacao = self._automacao_selecionada()
        if not automacao:
            return

        dialog = AutomacaoDialog(self, automacao=automacao)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dados = dialog.obter_dados()
            dados["automacao_id"] = automacao["id"]
            resultado = salvar_automacao(**dados)
            self._mostrar_resultado(resultado)

    def alternar_status(self):
        automacao = self._automacao_selecionada()
        if not automacao:
            return

        resultado = mudar_status_automacao(automacao["id"], not bool(automacao["ativo"]))
        self._mostrar_resultado(resultado)

    def testar_selecionada(self):
        automacao = self._automacao_selecionada()
        if not automacao:
            return

        resultado = testar_automacao(automacao["id"])
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Teste da Automacao", resultado["mensagem"])
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])
        self.carregar_automacoes()

    def deletar_automacao(self):
        automacao = self._automacao_selecionada()
        if not automacao:
            return

        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"Deletar a automacao '{automacao['nome']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        resultado = remover_automacao(automacao["id"])
        self._mostrar_resultado(resultado)

    def _mostrar_resultado(self, resultado):
        if resultado.get("sucesso"):
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_automacoes()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])


class AutomacaoDialog(QDialog):
    def __init__(self, parent=None, automacao=None):
        super().__init__(parent)
        self.automacao = automacao
        self.gatilhos, self.acoes = obter_opcoes_automacao()
        self.setWindowTitle("Automacao")
        self.setMinimumWidth(420)
        self.setStyleSheet(dialog_style())
        self._setup_ui()
        if automacao:
            self._preencher()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Ex: Avisar estoque baixo")
        layout.addRow("Nome:", self.input_nome)

        self.combo_gatilho = QComboBox()
        for chave, texto in self.gatilhos.items():
            self.combo_gatilho.addItem(texto, chave)
        layout.addRow("Quando:", self.combo_gatilho)

        self.input_limite = QDoubleSpinBox()
        self.input_limite.setRange(0, 999999)
        self.input_limite.setDecimals(2)
        self.input_limite.setValue(5)
        layout.addRow("Limite:", self.input_limite)

        self.combo_acao = QComboBox()
        for chave, texto in self.acoes.items():
            self.combo_acao.addItem(texto, chave)
        layout.addRow("Fazer:", self.combo_acao)

        self.input_intervalo = QSpinBox()
        self.input_intervalo.setRange(1, 10080)
        self.input_intervalo.setValue(30)
        self.input_intervalo.setSuffix(" min")
        layout.addRow("A cada:", self.input_intervalo)

        self.check_ativo = QCheckBox("Ativa")
        self.check_ativo.setChecked(True)
        layout.addRow("Status:", self.check_ativo)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _preencher(self):
        self.input_nome.setText(self.automacao["nome"])
        self._selecionar_combo(self.combo_gatilho, self.automacao["gatilho"])
        self.input_limite.setValue(float(self.automacao.get("valor_limite") or 0))
        self._selecionar_combo(self.combo_acao, self.automacao["acao"])
        self.input_intervalo.setValue(int(self.automacao.get("intervalo_minutos") or 30))
        self.check_ativo.setChecked(bool(self.automacao["ativo"]))

    def _selecionar_combo(self, combo, valor):
        index = combo.findData(valor)
        if index >= 0:
            combo.setCurrentIndex(index)

    def obter_dados(self):
        return {
            "nome": self.input_nome.text(),
            "gatilho": self.combo_gatilho.currentData(),
            "valor_limite": self.input_limite.value(),
            "acao": self.combo_acao.currentData(),
            "intervalo_minutos": self.input_intervalo.value(),
            "ativo": self.check_ativo.isChecked(),
        }
