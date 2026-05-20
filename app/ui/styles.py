from PyQt6.QtWidgets import QHeaderView, QTableWidget


COLORS = {
    "primary": "#1976D2",
    "primary_dark": "#0D47A1",
    "accent": "#FFC107",
    "accent_dark": "#FFA000",
    "success": "#2e7d32",
    "success_light": "#e8f5e9",
    "danger": "#b71c1c",
    "danger_bg": "#ffebee",
    "warning": "#bf4f00",
    "warning_bg": "#fff3e0",
    "purple": "#6A1B9A",
    "neutral": "#616161",
    "text": "#111111",
    "muted": "#555555",
    "line": "#bbdefb",
    "soft": "#e3f2fd",
    "white": "#ffffff",
}


BUTTON_VARIANTS = {
    "primary": (COLORS["primary"], COLORS["primary_dark"], "white", COLORS["accent"]),
    "success": (COLORS["success"], "#1b5e20", "white", COLORS["accent"]),
    "danger": ("#d32f2f", COLORS["danger"], "white", COLORS["accent"]),
    "warning": (COLORS["accent"], COLORS["accent_dark"], COLORS["primary_dark"], COLORS["primary"]),
    "purple": (COLORS["purple"], "#4A148C", "white", COLORS["accent"]),
    "neutral": ("#757575", COLORS["neutral"], "white", COLORS["accent"]),
}


def button_style(variant="primary"):
    bg, hover, text, border = BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS["primary"])
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text};
            border: 2px solid {border};
            border-radius: 5px;
            padding: 8px 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover};
            border: 2px solid {COLORS["accent_dark"]};
        }}
        QPushButton:pressed {{
            background-color: {hover};
        }}
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #666666;
            border: 1px solid #bbbbbb;
        }}
    """


def window_style():
    return """
        QWidget {
            background-color: #f5f5f5;
        }
    """


def title_style():
    return f"""
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["primary"]}, stop:1 {COLORS["accent"]});
        color: white;
        padding: 12px;
        border-radius: 6px;
        font-weight: bold;
    """


def section_title_style():
    return f"""
        color: {COLORS["primary"]};
        font-weight: bold;
        padding: 5px 0;
    """


def tab_style(compact=False):
    padding = "6px 15px" if compact else "8px 20px"
    border_radius = "4px 4px 0 0" if compact else "6px 6px 0 0"
    return f"""
        QTabBar::tab {{
            background-color: {COLORS["soft"]};
            color: {COLORS["primary_dark"]};
            padding: {padding};
            margin-right: 2px;
            border: 1px solid {COLORS["primary"]};
            border-bottom: none;
            border-radius: {border_radius};
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS["primary"]};
            color: white;
            font-weight: bold;
            border: 1px solid {COLORS["accent"]};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: #fff9c4;
            color: {COLORS["primary_dark"]};
        }}
        QTabWidget::pane {{
            border: 1px solid {COLORS["primary"]};
            background-color: white;
        }}
    """


def table_style():
    return f"""
        QTableWidget {{
            background-color: {COLORS["white"]};
            alternate-background-color: {COLORS["soft"]};
            color: {COLORS["text"]};
            border: 1px solid {COLORS["primary"]};
            border-radius: 5px;
            gridline-color: {COLORS["line"]};
            selection-background-color: {COLORS["accent"]};
            selection-color: {COLORS["primary_dark"]};
        }}
        QTableWidget::item {{
            color: {COLORS["text"]};
            padding: 5px;
        }}
        QTableWidget::item:selected {{
            background-color: {COLORS["accent"]};
            color: {COLORS["primary_dark"]};
        }}
        QHeaderView::section {{
            background-color: {COLORS["primary"]};
            color: white;
            padding: 5px;
            border: none;
            font-weight: bold;
        }}
    """


def card_style(color=None):
    color = color or COLORS["primary"]
    return f"""
        QFrame, QWidget {{
            background-color: white;
            border-left: 4px solid {color};
            border-top: 1px solid {COLORS["primary"]};
            border-right: 1px solid {COLORS["primary"]};
            border-bottom: 2px solid {COLORS["accent"]};
            border-radius: 6px;
        }}
        QLabel {{
            border: none;
            background: transparent;
            color: {COLORS["text"]};
        }}
    """


def style_card(widget, color=None, background="white"):
    color = color or COLORS["primary"]
    widget.setObjectName("appCard")
    widget.setStyleSheet(f"""
        QWidget#appCard, QFrame#appCard {{
            background-color: {background};
            border-left: 4px solid {color};
            border-top: 1px solid {COLORS["primary"]};
            border-right: 1px solid {COLORS["primary"]};
            border-bottom: 2px solid {COLORS["accent"]};
            border-radius: 6px;
        }}
        QWidget#appCard QLabel, QFrame#appCard QLabel {{
            border: none;
            background: transparent;
            color: {COLORS["text"]};
        }}
    """)


def info_panel_style():
    return f"""
        background-color: {COLORS["soft"]};
        color: {COLORS["primary_dark"]};
        padding: 10px;
        border-left: 4px solid {COLORS["primary"]};
        border-radius: 4px;
        font-weight: bold;
    """


def dialog_style():
    return f"""
        QDialog {{
            background-color: #f5f5f5;
            color: {COLORS["text"]};
        }}
        QLabel {{
            color: {COLORS["text"]};
            background-color: transparent;
        }}
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QListWidget {{
            color: {COLORS["text"]};
            background-color: white;
            border: 1px solid {COLORS["primary"]};
            border-radius: 3px;
            padding: 5px;
        }}
        QDialog QPushButton {{
            background-color: {COLORS["primary"]};
            color: white;
            border: 2px solid {COLORS["accent"]};
            border-radius: 5px;
            padding: 7px 14px;
            font-weight: bold;
            min-width: 70px;
        }}
        QDialog QPushButton:hover {{
            background-color: {COLORS["primary_dark"]};
            border: 2px solid {COLORS["accent_dark"]};
        }}
        QDialog QPushButton:disabled {{
            background-color: #cccccc;
            color: #666666;
            border: 1px solid #bbbbbb;
        }}
        QListWidget::item {{
            color: {COLORS["text"]};
        }}
    """


def apply_table_style(table, stretch=True):
    table.setAlternatingRowColors(True)
    table.setStyleSheet(table_style())
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    if stretch:
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


def style_button(button, variant="primary", min_height=35):
    button.setMinimumHeight(min_height)
    button.setStyleSheet(button_style(variant))


def icon_button_style(variant="primary"):
    bg, hover, text, border = BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS["primary"])
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {text};
            border: 1px solid {border};
            border-radius: 4px;
            padding: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover};
            border: 1px solid {COLORS["accent_dark"]};
        }}
        QPushButton:pressed {{
            background-color: {hover};
        }}
    """


def style_icon_button(button, variant="primary", size=30):
    button.setFixedWidth(size)
    button.setMinimumHeight(28)
    button.setStyleSheet(icon_button_style(variant))
