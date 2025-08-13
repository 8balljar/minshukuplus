# ui/views/hospedados_view.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QSizePolicy, QListWidgetItem
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

PALETTE = {
    "bg": "#f7f2e8", "panel": "#efdfc6", "border": "#5b3a29",
    "text": "#2b1d16", "muted": "#6b594c"
}

QSS = f"""
QWidget {{
    background: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: "Noto Sans", "Segoe UI", sans-serif;
    font-size: 15px;
}}
QWidget#Header {{ padding: 12px 18px; border-bottom: 2px solid {PALETTE['border']}; }}
QLabel#Title {{ font-size: 22px; font-weight: 700; }}
QWidget#Card {{ background: #ffffff; border: 2px solid {PALETTE['border']}; border-radius: 12px; }}
QListWidget {{ background:#fff; border:2px solid {PALETTE['border']}; border-radius:12px; padding:6px; }}
QLineEdit, QComboBox {{ background:#fff; border:1px solid #c7b299; border-radius:8px; padding:6px 8px; }}
QLineEdit:focus, QComboBox:focus {{ border:2px solid {PALETTE['border']}; }}
QPushButton[class="Primary"] {{
    background: {PALETTE['panel']}; border:2px solid {PALETTE['border']};
    border-radius:12px; padding:10px 14px; font-weight:700;
}}
QPushButton[class="Primary"]:hover {{ background:#f2e6d2; }}
QPushButton[class="Danger"] {{
    background:#ffe8e8; border:2px solid #a43c3c; color:#5a1111;
    border-radius:12px; padding:10px 14px; font-weight:700;
}}
"""

ICONS = {
    "add": "assets/icons/add.svg",
    "delete": "assets/icons/delete.svg",
    "user": "assets/icons/user.svg",
}

class HospedadoView(QWidget):
    # Señales → el controller se suscribe
    refreshRequested   = pyqtSignal()
    addRequested       = pyqtSignal()
    deleteRequested    = pyqtSignal()
    openDetailRequested= pyqtSignal(str)  # rut

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospedados")
        self.setStyleSheet(QSS)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 8, 16, 16)
        root.setSpacing(10)

        # Header
        headerw = QWidget(objectName="Header")
        header = QHBoxLayout(headerw); header.setContentsMargins(0,0,0,0)
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logo_min.png").scaledToHeight(36, Qt.SmoothTransformation))
        logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title = QLabel("Hospedados"); title.setObjectName("Title")
        header.addWidget(logo); header.addSpacing(8); header.addWidget(title); header.addStretch(1)

        # Cuerpo
        body = QHBoxLayout(); body.setSpacing(10)

        # Izquierda
        left = QVBoxLayout(); left.setSpacing(8)
        lbl_list = QLabel("Hospedados registrados"); lbl_list.setStyleSheet("font-weight:700;")
        self.search = QLineEdit(placeholderText="Buscar por nombre o RUT…")
        self.search.textChanged.connect(self._filter_list)

        self.lista = QListWidget()
        self.lista.setAlternatingRowColors(True)
        self.lista.itemDoubleClicked.connect(self._emit_open_detail)

        left.addWidget(lbl_list)
        left.addWidget(self.search)
        left.addWidget(self.lista, 1)

        # Derecha: card + form
        right_card = QWidget(objectName="Card")
        form_wrap = QVBoxLayout(right_card); form_wrap.setContentsMargins(14,14,14,14)
        form_wrap.setSpacing(10)

        title_form = QLabel("Nuevo hospedado")
        title_form.setStyleSheet("font-size:18px; font-weight:700;")
        form_wrap.addWidget(title_form)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignTop)

        self.nombre_input   = QLineEdit(placeholderText="Nombre y apellido")
        self.rut_input      = QLineEdit(placeholderText="123456789 o 12345678-9")
        self.correo_input   = QLineEdit(placeholderText="correo@ejemplo.com")
        self.telefono_input = QLineEdit(placeholderText="+56 9 1234 5678")
        self.sexo_input     = QComboBox(); self.sexo_input.addItems(["Hombre", "Mujer"])
        self.edad_input     = QLineEdit(placeholderText="Edad")

        form_layout.addRow("Nombre completo:", self.nombre_input)
        form_layout.addRow("RUT:",              self.rut_input)
        form_layout.addRow("Correo:",           self.correo_input)
        form_layout.addRow("Teléfono:",         self.telefono_input)
        form_layout.addRow("Sexo:",             self.sexo_input)
        form_layout.addRow("Edad:",             self.edad_input)
        form_wrap.addLayout(form_layout)

        # Botones
        btns = QHBoxLayout()
        self.agregar_btn  = QPushButton("Agregar");  self.agregar_btn.setProperty("class", "Primary")
        self.eliminar_btn = QPushButton("Eliminar"); self.eliminar_btn.setProperty("class", "Danger")
        self.agregar_btn.setMinimumHeight(40); self.eliminar_btn.setMinimumHeight(40)
        if ICONS.get("add"):    self.agregar_btn.setIcon(QIcon(ICONS["add"]))
        if ICONS.get("delete"): self.eliminar_btn.setIcon(QIcon(ICONS["delete"]))
        btns.addWidget(self.agregar_btn); btns.addWidget(self.eliminar_btn)

        form_wrap.addSpacing(6)
        form_wrap.addLayout(btns)
        form_wrap.addStretch(1)

        body.addLayout(left, 6)
        body.addWidget(right_card, 5)

        root.addWidget(headerw)
        root.addLayout(body)
        self.setLayout(root)

        # Conexiones → solo señales
        self.agregar_btn.clicked.connect(self.addRequested.emit)
        self.eliminar_btn.clicked.connect(self.deleteRequested.emit)

    # ---------- API para controller ----------
    def refresh(self):
        self.refreshRequested.emit()

    def add_list_item(self, display: str, rut: str):
        it = QListWidgetItem(display)
        it.setData(Qt.UserRole, rut)
        self.lista.addItem(it)

    def current_selected_rut(self) -> str:
        it = self.lista.currentItem()
        if not it:
            return ""
        rut = it.data(Qt.UserRole)
        if rut:
            return rut
        return (it.text().split(" - ")[0]).strip()

    def get_form_data(self) -> dict:
        return {
            "nombre": self.nombre_input.text().strip(),
            "rut": self.rut_input.text().strip(),
            "correo": self.correo_input.text().strip(),
            "telefono": self.telefono_input.text().strip(),
            "sexo": self.sexo_input.currentText(),
            "edad": self.edad_input.text().strip(),
        }

    def clear_inputs(self):
        self.nombre_input.clear()
        self.rut_input.clear()
        self.correo_input.clear()
        self.telefono_input.clear()
        self.sexo_input.setCurrentIndex(0)
        self.edad_input.clear()

    # ---------- internos UI ----------
    def _filter_list(self, text):
        txt = (text or "").strip().lower()
        for i in range(self.lista.count()):
            it = self.lista.item(i)
            it.setHidden(txt not in it.text().lower())

    def _emit_open_detail(self, item):
        rut = item.data(Qt.UserRole) or item.text().split(" - ")[0].strip()
        if rut:
            self.openDetailRequested.emit(rut)
