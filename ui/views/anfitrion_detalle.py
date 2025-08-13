# views/anfitrion_detalle_view.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFormLayout,
    QPushButton, QSizePolicy, QListWidget, QWidget, QComboBox, QCheckBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

PALETTE = {
    "bg": "#f7f2e8",
    "panel": "#efdfc6",
    "border": "#5b3a29",
    "text": "#2b1d16",
}

QSS = f"""
QDialog {{
    background: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: "Noto Sans", "Segoe UI", sans-serif;
    font-size: 15px;
}}
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
QPushButton[class="Danger"] {{
    background: #ffe8e8;
    border: 2px solid #a43c3c;
    color: #5a1111;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}}
"""

class AnfitrionDetalleView(QDialog):
    """Vista pura: expone UI + señales. Nada de Peewee aquí."""
    # Señales para el controller
    editRequested   = pyqtSignal()
    saveRequested   = pyqtSignal()
    cancelRequested = pyqtSignal()
    closeRequested  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle de anfitrión")
        self.setMinimumSize(720, 520)
        self.setStyleSheet(QSS)
        self._build_ui()
        self.set_edit_mode(False)

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Título + botón Editar
        top = QHBoxLayout()
        title = QLabel("Detalle de anfitrión")
        title.setStyleSheet("font-size:20px; font-weight:700;")
        self.edit_btn = QPushButton("Editar")
        self.edit_btn.setProperty("class", "Primary")
        top.addWidget(title)
        top.addStretch(1)
        top.addWidget(self.edit_btn)
        root.addLayout(top)

        # Cuerpo: izquierda (avatar) + derecha (form + casas)
        body = QHBoxLayout()
        body.setSpacing(12)

        # ------- Columna izquierda ------
        left_card = QWidget(objectName="Card")
        left = QVBoxLayout(left_card)
        left.setContentsMargins(14, 14, 14, 14)
        left.setSpacing(10)

        self.avatar = QLabel()
        pix = QPixmap("assets/avatar_user.png")
        if pix.isNull():
            pix = QPixmap(160, 160)
            pix.fill(Qt.transparent)
        self.avatar.setPixmap(pix.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.avatar.setAlignment(Qt.AlignCenter)

        self.sexo_combo = QComboBox()
        self.sexo_combo.addItems(["Hombre", "Mujer"])
        self.casado_check = QCheckBox("Casado")

        left.addWidget(self.avatar, alignment=Qt.AlignHCenter)
        left.addWidget(QLabel("Sexo"))
        left.addWidget(self.sexo_combo)
        left.addWidget(self.casado_check)
        left.addStretch(1)

        # ------- Columna derecha ------
        right_card = QWidget(objectName="Card")
        right = QVBoxLayout(right_card)
        right.setContentsMargins(14, 14, 14, 14)
        right.setSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)

        self.nombre_edit   = QLineEdit()
        self.rut_edit      = QLineEdit()
        self.rut_edit.setReadOnly(True)  # RUT no editable
        self.tel_edit      = QLineEdit()
        self.correo_edit   = QLineEdit()

        self.nombre_edit.setPlaceholderText("Nombre y apellido")
        self.tel_edit.setPlaceholderText("+56 9 1234 5678")
        self.correo_edit.setPlaceholderText("correo@ejemplo.com")

        form.addRow("Nombre completo:", self.nombre_edit)
        form.addRow("RUT:",              self.rut_edit)
        form.addRow("Teléfono:",         self.tel_edit)
        form.addRow("Correo:",           self.correo_edit)
        right.addLayout(form)

        # Lista de casas
        lbl_casas = QLabel("Casas del anfitrión")
        lbl_casas.setStyleSheet("font-weight:700;")
        self.casas_list = QListWidget()
        self.casas_list.setStyleSheet(
            "background:#fff; border:2px solid #5b3a29; border-radius:12px; padding:6px;")
        right.addWidget(lbl_casas)
        right.addWidget(self.casas_list, 1)

        # Botonera inferior
        btns = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.setProperty("class", "Primary")
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setProperty("class", "Danger")
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setProperty("class", "Primary")

        btns.addStretch(1)
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.close_btn)

        body.addWidget(left_card, 4)
        body.addWidget(right_card, 8)

        root.addLayout(body)
        root.addLayout(btns)
        self.setLayout(root)

        # Señales de botones
        self.edit_btn.clicked.connect(self.editRequested.emit)
        self.save_btn.clicked.connect(self.saveRequested.emit)
        self.cancel_btn.clicked.connect(self.cancelRequested.emit)
        self.close_btn.clicked.connect(self.closeRequested.emit)

    # ---------- API para el controller ----------
    def set_edit_mode(self, enabled: bool):
        self.nombre_edit.setReadOnly(not enabled)
        self.tel_edit.setReadOnly(not enabled)
        self.correo_edit.setReadOnly(not enabled)
        self.sexo_combo.setEnabled(enabled)
        self.casado_check.setEnabled(enabled)

        self.save_btn.setEnabled(enabled)
        self.cancel_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(not enabled)

    def set_data(self, data: dict):
        # data: {"nombre","rut","telefono","correo","sexo","casado"}
        self.nombre_edit.setText(data.get("nombre",""))
        self.rut_edit.setText(data.get("rut",""))
        self.tel_edit.setText(str(data.get("telefono","") or ""))
        self.correo_edit.setText(data.get("correo",""))
        self.sexo_combo.setCurrentText(data.get("sexo","Hombre"))
        self.casado_check.setChecked(bool(data.get("casado", False)))

    def set_casas(self, items):
        self.casas_list.clear()
        for it in items:
            self.casas_list.addItem(it)

    def get_form_data(self) -> dict:
        return {
            "nombre":  self.nombre_edit.text().strip(),
            "rut":     self.rut_edit.text().strip(),  # solo lectura
            "telefono": self.tel_edit.text().strip(),
            "correo":   self.correo_edit.text().strip(),
            "sexo":     self.sexo_combo.currentText(),
            "casado":   self.casado_check.isChecked(),
        }
  
