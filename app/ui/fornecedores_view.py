"""
VIEW DE FORNECEDORES
Interface para gerenciamento de fornecedores
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
    QFormLayout, QTextEdit, QSpinBox, QMessageBox, QComboBox,
    QHeaderView, QCheckBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from app.models.fornecedor import Fornecedor
from app.services.fornecedores_service import (
    cadastrar_fornecedor,
    editar_fornecedor,
    remover_fornecedor,
    reativar_fornecedor,
    obter_todos_fornecedores,
    pesquisar_fornecedores,
    gerar_relatorio_fornecedores
)
from app.services.fornecedor_xml_service import (
    garantir_tabela_importacoes,
    registrar_importacao_fornecedor,
    listar_importacoes_fornecedor
)
from app.services.xml_import_service import importar_nfe_xml
from app.ui.compras_view import ComprasFornecedorView
from app.ui.styles import apply_table_style, button_style, dialog_style, style_button, style_icon_button, title_style


class FornecedoresView(QWidget):
    """View para gerenciamento de fornecedores"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.carregar_fornecedores()
    
    def setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel("📦 GESTÃO DE FORNECEDORES")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(title_style())
        layout.addWidget(title_label)
        
        # Barra de pesquisa e botões
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nome, CNPJ ou produtos...")
        self.search_input.textChanged.connect(self.buscar_fornecedor)
        self.search_input.setMinimumHeight(30)
        search_layout.addWidget(self.search_input)
        
        self.btn_novo = QPushButton("➕ Novo Fornecedor")
        self.btn_novo.clicked.connect(self.novo_fornecedor)
        self.btn_novo.setMinimumHeight(30)
        self.btn_novo.setStyleSheet(self._get_button_style())
        search_layout.addWidget(self.btn_novo)
        
        layout.addLayout(search_layout)
        
        # Checkbox para mostrar inativos
        self.check_inativos = QCheckBox("Mostrar fornecedores inativos")
        self.check_inativos.stateChanged.connect(self.carregar_fornecedores)
        self.check_inativos.setStyleSheet("""
            QCheckBox {
                color: #0D47A1;
                font-weight: 500;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        layout.addWidget(self.check_inativos)
        
        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "CNPJ", "Telefone", "Email", 
            "Cidade", "Produtos", "Status", "Ações"
        ])
        
        # Configurar header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        apply_table_style(self.table, stretch=False)
        
        # Conectar double click para abrir importação XML do fornecedor
        self.table.doubleClicked.connect(self.abrir_xml_fornecedor)
        
        layout.addWidget(self.table)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.btn_relatorio = QPushButton("📊 Relatório")
        self.btn_relatorio.clicked.connect(self.mostrar_relatorio)
        self.btn_relatorio.setMinimumHeight(30)
        self.btn_relatorio.setStyleSheet(self._get_button_style())
        button_layout.addWidget(self.btn_relatorio)
        
        button_layout.addStretch()
        
        self.btn_atualizar = QPushButton("🔄 Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_fornecedores)
        self.btn_atualizar.setMinimumHeight(30)
        self.btn_atualizar.setStyleSheet(self._get_button_style())
        button_layout.addWidget(self.btn_atualizar)
        
        layout.addLayout(button_layout)
    
    def _get_button_style(self):
        """Retorna estilo dos botões"""
        return button_style()
    
    def carregar_fornecedores(self):
        """Carrega fornecedores na tabela"""
        incluir_inativos = self.check_inativos.isChecked()
        fornecedores = obter_todos_fornecedores(incluir_inativos=incluir_inativos)
        
        self.table.setRowCount(0)
        
        for fornecedor in fornecedores:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(fornecedor.id)))
            self.table.setItem(row, 1, QTableWidgetItem(fornecedor.nome))
            self.table.setItem(row, 2, QTableWidgetItem(fornecedor.cnpj or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(fornecedor.telefone or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(fornecedor.email or "-"))
            self.table.setItem(row, 5, QTableWidgetItem(fornecedor.cidade or "-"))
            self.table.setItem(row, 6, QTableWidgetItem(fornecedor.produtos_fornecidos or "-"))
            
            # Status
            status_item = QTableWidgetItem("✅ Ativo" if fornecedor.ativo else "❌ Inativo")
            if fornecedor.ativo:
                status_item.setForeground(QColor("#1976D2"))
            else:
                status_item.setForeground(QColor("#999"))
            self.table.setItem(row, 7, status_item)
            
            # Botões de ação
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            btn_editar = QPushButton("✏️")
            btn_editar.setToolTip("Editar")
            btn_editar.clicked.connect(lambda checked, f=fornecedor: self.editar_fornecedor(f))
            style_icon_button(btn_editar)
            actions_layout.addWidget(btn_editar)
            
            if fornecedor.ativo:
                btn_desativar = QPushButton("🗑️")
                btn_desativar.setToolTip("Desativar")
                btn_desativar.clicked.connect(lambda checked, f_id=fornecedor.id: self.desativar_fornecedor(f_id))
                style_icon_button(btn_desativar, "danger")
                actions_layout.addWidget(btn_desativar)
            else:
                btn_ativar = QPushButton("✅")
                btn_ativar.setToolTip("Reativar")
                btn_ativar.clicked.connect(lambda checked, f_id=fornecedor.id: self.ativar_fornecedor(f_id))
                style_icon_button(btn_ativar, "success")
                actions_layout.addWidget(btn_ativar)
            
            self.table.setCellWidget(row, 8, actions_widget)
    
    def buscar_fornecedor(self):
        """Busca fornecedores"""
        termo = self.search_input.text()
        fornecedores = pesquisar_fornecedores(termo)
        
        self.table.setRowCount(0)
        
        for fornecedor in fornecedores:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(fornecedor.id)))
            self.table.setItem(row, 1, QTableWidgetItem(fornecedor.nome))
            self.table.setItem(row, 2, QTableWidgetItem(fornecedor.cnpj or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(fornecedor.telefone or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(fornecedor.email or "-"))
            self.table.setItem(row, 5, QTableWidgetItem(fornecedor.cidade or "-"))
            self.table.setItem(row, 6, QTableWidgetItem(fornecedor.produtos_fornecidos or "-"))
            
            status_item = QTableWidgetItem("✅ Ativo" if fornecedor.ativo else "❌ Inativo")
            if fornecedor.ativo:
                status_item.setForeground(QColor("#1976D2"))
            else:
                status_item.setForeground(QColor("#999"))
            self.table.setItem(row, 7, status_item)
    
    def novo_fornecedor(self):
        """Abre dialog para novo fornecedor"""
        dialog = FornecedorDialog(self)
        if dialog.exec():
            self.carregar_fornecedores()
    
    def editar_fornecedor(self, fornecedor: Fornecedor):
        """Abre dialog para editar fornecedor"""
        dialog = FornecedorDialog(self, fornecedor)
        if dialog.exec():
            self.carregar_fornecedores()
    
    def desativar_fornecedor(self, fornecedor_id: int):
        """Desativa um fornecedor"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja realmente desativar este fornecedor?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            resultado = remover_fornecedor(fornecedor_id)
            if resultado["sucesso"]:
                QMessageBox.information(self, "Sucesso", resultado["mensagem"])
                self.carregar_fornecedores()
            else:
                QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def ativar_fornecedor(self, fornecedor_id: int):
        """Reativa um fornecedor"""
        resultado = reativar_fornecedor(fornecedor_id)
        if resultado["sucesso"]:
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.carregar_fornecedores()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])
    
    def abrir_xml_fornecedor(self):
        """Abre o painel de XML do fornecedor ao dar double click"""
        row = self.table.currentRow()
        if row >= 0:
            fornecedor_id = int(self.table.item(row, 0).text())
            fornecedor_nome = self.table.item(row, 1).text()
            dialog = FornecedorXmlDialog(self, fornecedor_id, fornecedor_nome)
            dialog.exec()
    
    def mostrar_relatorio(self):
        """Mostra relatório de fornecedores"""
        relatorio = gerar_relatorio_fornecedores()
        
        msg = f"""
        📊 RELATÓRIO DE FORNECEDORES
        
        Total de Fornecedores: {relatorio['total_fornecedores']}
        Ativos: {relatorio['ativos']}
        Inativos: {relatorio['inativos']}
        
        Com última compra registrada: {relatorio['com_ultima_compra']}
        Sem compra registrada: {relatorio['sem_ultima_compra']}
        """
        
        QMessageBox.information(self, "Relatório", msg)


class FornecedorXmlDialog(QDialog):
    """Dialog para importação e histórico de XML por fornecedor"""

    def __init__(self, parent=None, fornecedor_id: int = 0, fornecedor_nome: str = ""):
        super().__init__(parent)
        self.fornecedor_id = fornecedor_id
        self.fornecedor_nome = fornecedor_nome
        self.importacoes = []
        self.setWindowTitle(f"📄 XML - {fornecedor_nome}")
        self.setMinimumSize(700, 420)
        self.setStyleSheet(dialog_style())
        garantir_tabela_importacoes()
        self.setup_ui()
        self.carregar_importacoes()

    def setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title_label = QLabel(f"📄 XML DO FORNECEDOR - {self.fornecedor_nome}")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(title_style())
        layout.addWidget(title_label)

        buttons_layout = QHBoxLayout()

        self.btn_importar_xml = QPushButton("📄 Importar XML")
        self.btn_importar_xml.clicked.connect(self.importar_xml_fornecedor)
        self.btn_importar_xml.setMinimumHeight(30)
        self.btn_importar_xml.setStyleSheet(self._get_button_style())
        buttons_layout.addWidget(self.btn_importar_xml)

        self.btn_compras = QPushButton("📦 Compras do Fornecedor")
        self.btn_compras.clicked.connect(self.abrir_compras)
        self.btn_compras.setMinimumHeight(30)
        self.btn_compras.setStyleSheet(self._get_button_style())
        buttons_layout.addWidget(self.btn_compras)

        buttons_layout.addStretch()

        self.btn_atualizar = QPushButton("🔄 Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_importacoes)
        self.btn_atualizar.setMinimumHeight(30)
        self.btn_atualizar.setStyleSheet(self._get_button_style())
        buttons_layout.addWidget(self.btn_atualizar)

        layout.addLayout(buttons_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Data", "Arquivo", "Itens", "Criados", "Atualizados"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        apply_table_style(self.table, stretch=False)

        self.table.doubleClicked.connect(self.mostrar_detalhes_importacao)

        layout.addWidget(self.table)

    def _get_button_style(self):
        return button_style()

    def carregar_importacoes(self):
        """Carrega histórico de importações XML"""
        self.importacoes = listar_importacoes_fornecedor(self.fornecedor_id)
        self.table.setRowCount(0)

        for imp in self.importacoes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            data_formatada = (imp.get("data_importacao") or "").replace("T", " ")[:19]

            self.table.setItem(row, 0, QTableWidgetItem(str(imp.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(data_formatada))
            self.table.setItem(row, 2, QTableWidgetItem(imp.get("nome_arquivo") or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(str(imp.get("total_itens", 0))))
            self.table.setItem(row, 4, QTableWidgetItem(str(imp.get("produtos_criados", 0))))
            self.table.setItem(row, 5, QTableWidgetItem(str(imp.get("produtos_atualizados", 0))))

    def importar_xml_fornecedor(self):
        """Importa XML e registra no histórico do fornecedor"""
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
            registrar_importacao_fornecedor(self.fornecedor_id, caminho, resultado)
            QMessageBox.information(self, "Importação concluída", resultado["mensagem"])
            self.carregar_importacoes()
        else:
            QMessageBox.warning(self, "Erro na importação", resultado.get("mensagem", "Erro desconhecido"))

    def mostrar_detalhes_importacao(self):
        """Mostra detalhes da importação selecionada"""
        row = self.table.currentRow()
        if row < 0 or row >= len(self.importacoes):
            return

        imp = self.importacoes[row]
        avisos = imp.get("avisos") or ""
        comparacoes = imp.get("comparacoes_preco") or ""

        detalhes = f"""📄 DETALHES DA IMPORTAÇÃO

Arquivo: {imp.get('nome_arquivo', '-')}
Data: {(imp.get('data_importacao') or '').replace('T', ' ')[:19]}
Itens: {imp.get('total_itens', 0)}
Criados: {imp.get('produtos_criados', 0)}
Atualizados: {imp.get('produtos_atualizados', 0)}
"""

        if comparacoes:
            detalhes += "\n\nComparação de preços:\n" + comparacoes
        if avisos:
            detalhes += "\n\nAvisos:\n" + avisos

        QMessageBox.information(self, "Detalhes da Importação", detalhes)

    def abrir_compras(self):
        """Abre a janela de compras do fornecedor"""
        self.compras_window = ComprasFornecedorView(self.fornecedor_id, self.fornecedor_nome)
        self.compras_window.show()


class FornecedorDialog(QDialog):
    """Dialog para cadastro/edição de fornecedor"""
    
    def __init__(self, parent=None, fornecedor: Fornecedor = None):
        super().__init__(parent)
        self.fornecedor = fornecedor
        self.setWindowTitle("✏️ Editar Fornecedor" if fornecedor else "➕ Novo Fornecedor")
        self.setMinimumWidth(500)
        self.setStyleSheet(dialog_style())
        self.setup_ui()
        
        if fornecedor:
            self.preencher_dados()
    
    def setup_ui(self):
        """Configura interface do dialog"""
        layout = QVBoxLayout(self)
        
        # Form
        form = QFormLayout()
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome da empresa... *Obrigatório")
        form.addRow("Nome *:", self.nome_input)
        
        self.cnpj_input = QLineEdit()
        self.cnpj_input.setPlaceholderText("00.000.000/0000-00 (Não obrigatório)")
        form.addRow("CNPJ:", self.cnpj_input)
        
        self.telefone_input = QLineEdit()
        self.telefone_input.setPlaceholderText("(00) 00000-0000 (Não obrigatório)")
        form.addRow("Telefone:", self.telefone_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("contato@fornecedor.com (Não obrigatório)")
        form.addRow("Email:", self.email_input)
        
        self.endereco_input = QLineEdit()
        self.endereco_input.setPlaceholderText("Rua, número, complemento... (Não obrigatório)")
        form.addRow("Endereço:", self.endereco_input)
        
        self.cidade_input = QLineEdit()
        self.cidade_input.setPlaceholderText("Nome da cidade... (Não obrigatório)")
        form.addRow("Cidade:", self.cidade_input)
        
        self.estado_combo = QComboBox()
        estados = ["", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
                  "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
                  "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
        self.estado_combo.addItems(estados)
        form.addRow("Estado:", self.estado_combo)
        
        self.produtos_input = QTextEdit()
        self.produtos_input.setPlaceholderText("Ex: Bebidas, Salgados, Produtos de limpeza...")
        self.produtos_input.setMaximumHeight(60)
        form.addRow("Produtos Fornecidos:", self.produtos_input)
        
        self.prazo_input = QSpinBox()
        self.prazo_input.setMinimum(0)
        self.prazo_input.setMaximum(365)
        self.prazo_input.setSuffix(" dias")
        form.addRow("Prazo de Entrega:", self.prazo_input)
        
        # Dias de entrega
        dias_widget = QWidget()
        dias_layout = QHBoxLayout(dias_widget)
        dias_layout.setContentsMargins(0, 0, 0, 0)
        
        self.dias_checks = {}
        dias_semana = [
            ("Seg", 0), ("Ter", 1), ("Qua", 2), ("Qui", 3),
            ("Sex", 4), ("Sáb", 5), ("Dom", 6)
        ]
        
        for nome, valor in dias_semana:
            check = QCheckBox(nome)
            check.setProperty("dia_valor", valor)
            self.dias_checks[valor] = check
            dias_layout.addWidget(check)
        
        dias_layout.addStretch()
        form.addRow("Dias de Entrega:", dias_widget)
        
        self.pagamento_combo = QComboBox()
        self.pagamento_combo.addItems([
            "",
            "À vista",
            "Boleto 7 dias",
            "Boleto 14 dias",
            "Boleto 30 dias",
            "Cartão de crédito",
            "Pix",
            "Outro"
        ])
        form.addRow("Forma de Pagamento:", self.pagamento_combo)
        
        self.obs_input = QTextEdit()
        self.obs_input.setPlaceholderText("Observações adicionais...")
        self.obs_input.setMaximumHeight(60)
        form.addRow("Observações:", self.obs_input)
        
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
        """Preenche campos com dados do fornecedor"""
        self.nome_input.setText(self.fornecedor.nome)
        self.cnpj_input.setText(self.fornecedor.cnpj or "")
        self.telefone_input.setText(self.fornecedor.telefone or "")
        self.email_input.setText(self.fornecedor.email or "")
        self.endereco_input.setText(self.fornecedor.endereco or "")
        self.cidade_input.setText(self.fornecedor.cidade or "")
        
        if self.fornecedor.estado:
            index = self.estado_combo.findText(self.fornecedor.estado)
            if index >= 0:
                self.estado_combo.setCurrentIndex(index)
        
        self.produtos_input.setPlainText(self.fornecedor.produtos_fornecidos or "")
        self.prazo_input.setValue(self.fornecedor.prazo_entrega or 0)
        
        # Dias de entrega
        if self.fornecedor.dias_entrega:
            dias = self.fornecedor.dias_entrega.split(',')
            for dia in dias:
                if dia.strip().isdigit():
                    dia_num = int(dia.strip())
                    if dia_num in self.dias_checks:
                        self.dias_checks[dia_num].setChecked(True)
        
        if self.fornecedor.forma_pagamento:
            index = self.pagamento_combo.findText(self.fornecedor.forma_pagamento)
            if index >= 0:
                self.pagamento_combo.setCurrentIndex(index)
        
        self.obs_input.setPlainText(self.fornecedor.observacoes or "")
    
    def salvar(self):
        """Salva o fornecedor"""
        nome = self.nome_input.text().strip()
        
        if not nome:
            QMessageBox.warning(self, "Atenção", "Nome do fornecedor é obrigatório!")
            return
        
        # Obter dias de entrega selecionados
        dias_selecionados = []
        for dia_num, checkbox in self.dias_checks.items():
            if checkbox.isChecked():
                dias_selecionados.append(str(dia_num))
        dias_entrega_str = ','.join(dias_selecionados) if dias_selecionados else None
        
        fornecedor = Fornecedor(
            id=self.fornecedor.id if self.fornecedor else None,
            nome=nome,
            cnpj=self.cnpj_input.text().strip() or None,
            telefone=self.telefone_input.text().strip() or None,
            email=self.email_input.text().strip() or None,
            endereco=self.endereco_input.text().strip() or None,
            cidade=self.cidade_input.text().strip() or None,
            estado=self.estado_combo.currentText() or None,
            produtos_fornecidos=self.produtos_input.toPlainText().strip() or None,
            prazo_entrega=self.prazo_input.value() if self.prazo_input.value() > 0 else None,
            dias_entrega=dias_entrega_str,
            forma_pagamento=self.pagamento_combo.currentText() or None,
            observacoes=self.obs_input.toPlainText().strip() or None
        )
        
        if self.fornecedor:
            resultado = editar_fornecedor(fornecedor)
        else:
            resultado = cadastrar_fornecedor(fornecedor)
        
        if resultado["sucesso"]:
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", resultado["mensagem"])
