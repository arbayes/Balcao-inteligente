"""
Gerenciador de Atalhos de Teclado
"""

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

class KeyboardShortcuts:
    """Gerencia atalhos do teclado"""
    
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.atalhos = {}
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Define todos os atalhos"""
        
        # F2 - Novo registro (geral)
        self.criar_atalho(Qt.Key.Key_F2, "Novo Registro", self._novo_registro)
        
        # Delete - Remover selecionado
        self.criar_atalho(Qt.Key.Key_Delete, "Deletar Selecionado", self._deletar_selecionado)
        
        # Ctrl+F - Buscar/Pesquisar
        self.criar_atalho(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_F, "Buscar", self._abrir_busca)
        
        # Ctrl+N - Novo
        self.criar_atalho(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_N, "Novo", self._novo_registro)
        
        # Ctrl+S - Salvar (backup manual)
        self.criar_atalho(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_S, "Salvar", self._salvar)
        
        # Ctrl+P - Imprimir/Print
        self.criar_atalho(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_P, "Imprimir", self._imprimir)
        
        # Ctrl+E - Exportar
        self.criar_atalho(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_E, "Exportar", self._exportar)
        
        # F5 - Atualizar/Refresh
        self.criar_atalho(Qt.Key.Key_F5, "Atualizar", self._atualizar)
        
        # F1 - Ajuda
        self.criar_atalho(Qt.Key.Key_F1, "Ajuda", self._mostrar_ajuda)
        
        # Escape - Fechar dialog/modal
        self.criar_atalho(Qt.Key.Key_Escape, "Fechar", self._fechar_modal)
    
    def criar_atalho(self, sequencia, descricao: str, callback):
        """Cria um novo atalho"""
        shortcut = QShortcut(QKeySequence(sequencia), self.main_window)
        shortcut.activated.connect(callback)
        self.atalhos[descricao] = shortcut
    
    def _novo_registro(self):
        """Atalho: Novo registro"""
        # Verifica qual aba está ativa e dispara o novo
        if hasattr(self.main_window, 'tabs'):
            indice_atual = self.main_window.tabs.currentIndex()
            # Disparar novo no serviço correspondente
            print("F2 - Novo registro pressionado")
    
    def _deletar_selecionado(self):
        """Atalho: Delete selecionado"""
        print("Delete - Remover selecionado")
    
    def _abrir_busca(self):
        """Atalho: Abrir busca (Ctrl+F)"""
        print("Ctrl+F - Buscar")
    
    def _salvar(self):
        """Atalho: Salvar/Backup (Ctrl+S)"""
        print("Ctrl+S - Fazer backup")
        if hasattr(self.main_window, 'fazer_backup'):
            try:
                resultado = self.main_window.fazer_backup()
                QMessageBox.information(self.main_window, "Backup", 
                                       "Backup realizado com sucesso!")
            except Exception as e:
                QMessageBox.warning(self.main_window, "Erro", f"Erro ao fazer backup: {e}")
    
    def _imprimir(self):
        """Atalho: Imprimir (Ctrl+P)"""
        print("Ctrl+P - Imprimir")
        if hasattr(self.main_window, 'imprimir_relatorio'):
            try:
                self.main_window.imprimir_relatorio()
            except:
                pass
    
    def _exportar(self):
        """Atalho: Exportar (Ctrl+E)"""
        print("Ctrl+E - Exportar")
        if hasattr(self.main_window, 'exportar_dados'):
            try:
                self.main_window.exportar_dados()
            except:
                pass
    
    def _atualizar(self):
        """Atalho: Atualizar (F5)"""
        print("F5 - Atualizar tela")
        if hasattr(self.main_window, 'recarregar_dados'):
            try:
                self.main_window.recarregar_dados()
            except:
                pass
    
    def _mostrar_ajuda(self):
        """Atalho: Ajuda (F1)"""
        ajuda_texto = """
        <h2>Atalhos de Teclado</h2>
        <p><b>F2</b> - Novo Registro</p>
        <p><b>Delete</b> - Deletar Selecionado</p>
        <p><b>Ctrl+F</b> - Buscar</p>
        <p><b>Ctrl+N</b> - Novo</p>
        <p><b>Ctrl+S</b> - Salvar/Backup</p>
        <p><b>Ctrl+P</b> - Imprimir</p>
        <p><b>Ctrl+E</b> - Exportar</p>
        <p><b>F5</b> - Atualizar</p>
        <p><b>F1</b> - Ajuda</p>
        <p><b>Escape</b> - Fechar</p>
        """
        QMessageBox.information(self.main_window, "Atalhos de Teclado", ajuda_texto)
    
    def _fechar_modal(self):
        """Atalho: Fechar modal (Escape)"""
        # PyQt6 já gerencia isso, mas pode adicionar lógica customizada
        print("Escape - Fechar")
    
    def listar_atalhos(self):
        """Retorna lista de todos os atalhos"""
        return self.atalhos
