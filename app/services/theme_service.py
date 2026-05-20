"""
Gerenciador de temas - Light e Dark mode
"""

import json
import os
from pathlib import Path

class ThemeService:
    """Gerencia temas da aplicação"""
    
    THEME_FILE = Path(__file__).parent.parent.parent / "theme_config.json"
    
    LIGHT_THEME = {
        "name": "light",
        "colors": {
            "primary": "#1976D2",
            "accent": "#FFC107",
            "dark": "#0D47A1",
            "light_bg": "#e3f2fd",
            "bg": "#ffffff",
            "text": "#000000",
            "text_light": "#666666",
            "border": "#CCCCCC",
            "error": "#d32f2f",
            "success": "#4CAF50",
            "warning": "#ff6f00"
        }
    }
    
    DARK_THEME = {
        "name": "dark",
        "colors": {
            "primary": "#1976D2",
            "accent": "#FFC107",
            "dark": "#0D47A1",
            "light_bg": "#1e1e1e",
            "bg": "#2d2d2d",
            "text": "#e0e0e0",
            "text_light": "#b0b0b0",
            "border": "#404040",
            "error": "#ff5252",
            "success": "#66BB6A",
            "warning": "#ffb74d"
        }
    }
    
    def __init__(self):
        self.current_theme = self._load_theme()
    
    def _load_theme(self):
        """Carrega tema salvo ou usa light por padrão"""
        try:
            if self.THEME_FILE.exists():
                with open(self.THEME_FILE, 'r') as f:
                    config = json.load(f)
                    theme_name = config.get('theme', 'light')
                    return self.DARK_THEME if theme_name == 'dark' else self.LIGHT_THEME
        except Exception as e:
            print(f"Erro ao carregar tema: {e}")
        
        return self.LIGHT_THEME
    
    def set_theme(self, theme_name: str):
        """Define o tema atual (light ou dark)"""
        if theme_name == 'dark':
            self.current_theme = self.DARK_THEME
        else:
            self.current_theme = self.LIGHT_THEME
        
        self._save_theme(theme_name)
    
    def _save_theme(self, theme_name: str):
        """Salva tema em arquivo"""
        try:
            config = {'theme': theme_name}
            with open(self.THEME_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar tema: {e}")
    
    def get_stylesheet(self):
        """Retorna CSS do tema atual"""
        colors = self.current_theme['colors']
        
        return f"""
            QWidget {{
                background-color: {colors['bg']};
                color: {colors['text']};
            }}
            
            QMainWindow {{
                background-color: {colors['bg']};
            }}
            
            QLabel {{
                color: {colors['text']};
            }}
            
            QLineEdit {{
                background-color: {colors['light_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 5px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {colors['primary']};
            }}
            
            QComboBox {{
                background-color: {colors['light_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
                padding: 5px;
            }}
            
            QTableWidget {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                gridline-color: {colors['border']};
            }}
            
            QTableWidget::item {{
                padding: 5px;
                color: {colors['text']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {colors['accent']};
                color: {colors['primary']};
            }}
            
            QHeaderView::section {{
                background-color: {colors['primary']};
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }}
            
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: 2px solid {colors['accent']};
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {colors['dark']};
                border: 2px solid #FFA000;
            }}
            
            QPushButton:pressed {{
                background-color: {colors['dark']};
            }}

            QPushButton:disabled {{
                background-color: {colors['border']};
                color: {colors['text_light']};
                border: 1px solid {colors['border']};
            }}
            
            QTextEdit {{
                background-color: {colors['light_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            
            QDialog {{
                background-color: {colors['bg']};
            }}
            
            QTabWidget {{
                background-color: {colors['bg']};
            }}
            
            QTabBar::tab {{
                background-color: {colors['light_bg']};
                color: {colors['text']};
                padding: 8px;
                border: 1px solid {colors['border']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            QListWidget {{
                background-color: {colors['light_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}

            QListWidget::item:selected {{
                background-color: {colors['accent']};
                color: {colors['primary']};
            }}
            
            QSpinBox, QDoubleSpinBox {{
                background-color: {colors['light_bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 3px;
            }}
            
            QMessageBox {{
                background-color: {colors['bg']};
            }}
        """
    
    def get_color(self, color_name: str) -> str:
        """Retorna uma cor específica do tema"""
        return self.current_theme['colors'].get(color_name, "#1976D2")


# Singleton global
_theme_service = None

def get_theme_service():
    """Retorna instância global do serviço de temas"""
    global _theme_service
    if _theme_service is None:
        _theme_service = ThemeService()
    return _theme_service
