# views/menu_casa_view.py
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ui.views.anfitrion_views import AnfitrionViews
from ui.views.casa_views import CasaView

PALETTE = {
    "bg": "#f7f2e8",
    "panel": "#efdfc6",
    "border": "#5b3a29",
    "text": "#2b1d16",
    "muted": "#6b594c",
}

QSS = f"""
QWidget {{
    background: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: "Noto Sans", "Segoe UI", sans-serif;
    font-size: 15px;
}}
/* Header */
QWidget#Header {{
    padding: 12px 18px;
    border-bottom: 2px solid {PALETTE['border']};
}}
QLabel#Title {{
    font-size: 22px;
    font-weight: 700;
}}
/* Tabs */
QTabWidget::pane {{
    border: none;
    margin-top: 8px;
}}
QTabBar::tab {{
    background: {PALETTE['panel']};
    border: 2px solid {PALETTE['border']};
    border-bottom: 2px solid {PALETTE['border']};
    padding: 10px 18px;
    margin-right: 6px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: #f2e6d2;
}}
/* Card genérica para formularios */
QWidget#Card {{
    background: #ffffff;
    border: 2px solid {PALETTE['border']};
    border-radius: 12px;
}}
QLineEdit, QComboBox {{
    background: #ffffff;
    border: 1px solid #c7b299;
    border-radius: 8px;
    padding: 6px 8px;
}}
QLineEdit:focus, QComboBox:focus {{
    border: 2px solid {PALETTE['border']};
}}
QPushButton[class="Primary"] {{
    background: {PALETTE['panel']};
    border: 2px solid {PALETTE['border']};
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}}
QPushButton[class="Primary"]:hover {{ background: #f2e6d2; }}
QPushButton[class="Danger"]  {{
    background: #ffe8e8;
    border: 2px solid #a43c3c;
    color: #5a1111;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}}
QPushButton[class="Danger"]:hover {{ background: #ffdcdc; }}
"""

class Menu_Casa_View(QWidget):
    """
    Vista pura: contiene pestañas de Anfitriones y Casas.
    No hace navegación ni carga de datos por sí misma.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de anfitriones y casas — Minshuku+")
        self.setStyleSheet(QSS)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 8, 16, 16)
        root.setSpacing(8)

        # Header superior con logo + título
        headerw = QWidget(objectName="Header")
        header = QHBoxLayout(headerw)
        header.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logo_min.png").scaledToHeight(36, Qt.SmoothTransformation))
        logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        title = QLabel("Gestión de anfitriones y casas")
        title.setObjectName("Title")

        header.addWidget(logo)
        header.addSpacing(8)
        header.addWidget(title)
        header.addStretch(1)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Subvistas (también deberían ser vistas puras)
        self.anfitrion_tab = AnfitrionViews()
        self.casa_tab = CasaView()

        self.tabs.addTab(self.anfitrion_tab, "Anfitriones")
        self.tabs.addTab(self.casa_tab, "Casas")

        root.addWidget(headerw)
        root.addWidget(self.tabs)
