# views/home_view.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize

PALETTE = {
    "bg": "#f7f2e8",           # beige papel arroz
    "panel": "#efdfc6",        # pergamino
    "border": "#5b3a29",       # café oscuro
    "text": "#2b1d16",
    "accent": "#b63b3b",       # rojo sello
}

ICONS = {
    "casas": "assets/icons/house_japan.svg",
    "hospedados": "assets/icons/family.svg",
    "asignaciones": "assets/icons/assignments.svg",
    "sync": "assets/icons/synchronization.svg",
}

def set_btn_icon(btn, path_key, size=QSize(28, 28)):
    btn.setIcon(QIcon(ICONS[path_key]))
    btn.setIconSize(size)
    btn.setStyleSheet(btn.styleSheet() + "padding-left: 10px; text-align: left;")

QSS = f"""
QWidget {{
    background: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: "Noto Sans", "Segoe UI", sans-serif;
    font-size: 16px;
}}
QWidget#Header {{
    padding: 24px 16px 8px 16px;
}}
QLabel#Title {{
    font-size: 36px;
    font-weight: 700;
}}
QLabel#Kana {{
    font-size: 14px;
    letter-spacing: 2px;
    color: #6b594c;
}}
QPushButton[class="MenuBtn"] {{
    background: {PALETTE['panel']};
    border: 2px solid {PALETTE['border']};
    border-radius: 14px;
    padding: 18px 22px;
    text-align: left;
    font-size: 22px;
    font-weight: 600;
}}
QPushButton[class="MenuBtn"]:hover {{
    background: #f2e6d2;
}}
QPushButton[class="MenuBtn"]:pressed {{
    background: #ead7b7;
}}
QWidget#MenuWrap {{
    max-width: 720px;
}}
"""

class HomeView(QWidget):
    """Vista pura. No abre ventanas por sí sola: expone botones para que el Controller actúe."""
    def __init__(self):
        super().__init__()
        self.setObjectName("HomeView")
        self.setWindowTitle("Minshuku+ — Menú Principal")
        self.setStyleSheet(QSS)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 24, 40, 40)
        root.setSpacing(12)

        # ---------- Header ----------
        header = QVBoxLayout()
        header_w = QWidget(objectName="Header")
        header_w.setLayout(header)

        logo_line = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/image.png").scaledToHeight(92, Qt.SmoothTransformation))
        logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        title_box = QVBoxLayout()
        title = QLabel("Minshuku+")
        title.setObjectName("Title")
        kana = QLabel("みんしゅく＋")
        kana.setObjectName("Kana")
        title_box.addWidget(title)
        title_box.addWidget(kana)
        title_box.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        logo_line.addWidget(logo)
        logo_line.addLayout(title_box)
        logo_line.addStretch(1)
        header.addLayout(logo_line)

        # ---------- Menú central ----------
        menu_wrap = QWidget(objectName="MenuWrap")
        menu = QVBoxLayout(menu_wrap)
        menu.setSpacing(16)

        self.casas_btn = QPushButton("Casas disponibles")
        self.hospedado_btn = QPushButton("Personas hospedadas")
        self.asignaciones_btn = QPushButton("Asignaciones")
        self.sync_btn = QPushButton("Sincronizar")

        for b in (self.casas_btn, self.hospedado_btn, self.asignaciones_btn, self.sync_btn):
            b.setProperty("class", "MenuBtn")
            b.setMinimumHeight(64)

        set_btn_icon(self.casas_btn, "casas")
        set_btn_icon(self.hospedado_btn, "hospedados")
        set_btn_icon(self.asignaciones_btn, "asignaciones")
        set_btn_icon(self.sync_btn, "sync")

        menu.addWidget(self.casas_btn)
        menu.addWidget(self.hospedado_btn)
        menu.addWidget(self.asignaciones_btn)
        menu.addWidget(self.sync_btn)

        # Layout raíz
        root.addWidget(header_w)
        root.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(menu_wrap)
        row.addStretch(1)
        root.addLayout(row)
        root.addStretch(2)
