# ui/views/anfitrion_views.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QCheckBox, QSizePolicy, QListWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal

ICONS = {
    "add": "assets/icons/add.svg",
    "delete": "assets/icons/delete.svg",
    "user": "assets/icons/user.svg",
}

class AnfitrionViews(QWidget):
    # Señales para el controller
    refreshRequested    = pyqtSignal()
    addRequested        = pyqtSignal()
    deleteRequested     = pyqtSignal()
    openDetailRequested = pyqtSignal(str)   # rut

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(400)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(10)

        # ========== IZQUIERDA ==========
        left = QVBoxLayout()
        left.setSpacing(8)

        lbl_list = QLabel("Anfitriones registrados")
        lbl_list.setStyleSheet("font-weight: 700;")
        self.search = QLineEdit(placeholderText="Buscar por nombre o RUT…")
        self.search.textChanged.connect(self._filter_list)

        self.lista = QListWidget()
        self.lista.setAlternatingRowColors(True)
        self.lista.setStyleSheet(
            "background:#fff; border:2px solid #5b3a29; border-radius:12px; padding:6px;")
        self.lista.itemDoubleClicked.connect(self._emit_open_detail)

        left.addWidget(lbl_list)
        left.addWidget(self.search)
        left.addWidget(self.lista, 1)

        # ========== DERECHA ==========
        right_card = QWidget(objectName="Card")
        right_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        form_wrap = QVBoxLayout(right_card)
        form_wrap.setContentsMargins(14, 14, 14, 14)
        form_wrap.setSpacing(10)

        title = QLabel("Nuevo anfitrión")
        title.setStyleSheet("font-size:18px; font-weight:700;")
        form_wrap.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)

        self.nombre_input   = QLineEdit(placeholderText="Nombre y apellido")
        self.rut_input      = QLineEdit(placeholderText="12.345.678-9 o 12345678-9")
        self.telefono_input = QLineEdit(placeholderText="+56 9 1234 5678")
        self.correo_input   = QLineEdit(placeholderText="correo@ejemplo.com")
        self.sexo_input     = QComboBox(); self.sexo_input.addItems(["Hombre", "Mujer"])
        self.casado_check   = QCheckBox("Casado")

        form.addRow("Nombre completo:", self.nombre_input)
        form.addRow("RUT:",              self.rut_input)
        form.addRow("Teléfono:",         self.telefono_input)
        form.addRow("Correo:",           self.correo_input)
        form.addRow("Sexo:",             self.sexo_input)
        form.addRow("Estado civil:",     self.casado_check)
        form_wrap.addLayout(form)

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

        # Ensamble
        root.addLayout(left, 6)
        root.addWidget(right_card, 5)
        self.setLayout(root)

        # Conexiones → sólo señales (el controller hace el trabajo)
        self.agregar_btn.clicked.connect(self.addRequested.emit)
        self.eliminar_btn.clicked.connect(self.deleteRequested.emit)

    # -------- API para controller --------
    def refresh(self):
        self.refreshRequested.emit()

    def clear_list(self):
        self.lista.clear()

    def add_list_item(self, display: str, rut: str):
        it = QListWidgetItem(display)
        it.setData(Qt.UserRole, rut)
        self.lista.addItem(it)

    def current_selected_rut(self) -> str:
        it = self.lista.currentItem()
        if not it:
            return ""
        rut = it.data(Qt.UserRole)
        return rut or (it.text().split(" - ")[0]).strip()

    def get_form_data(self) -> dict:
        return {
            "nombre":   self.nombre_input.text().strip(),
            "rut":      self.rut_input.text().strip(),
            "telefono": self.telefono_input.text().strip(),
            "correo":   self.correo_input.text().strip(),
            "sexo":     self.sexo_input.currentText(),
            "casado":   self.casado_check.isChecked(),
        }

    def clear_inputs(self):
        self.nombre_input.clear()
        self.rut_input.clear()
        self.telefono_input.clear()
        self.correo_input.clear()
        self.sexo_input.setCurrentIndex(0)
        self.casado_check.setChecked(False)

    # -------- UI interno --------
    def _filter_list(self, text):
        txt = (text or "").strip().lower()
        for i in range(self.lista.count()):
            it = self.lista.item(i)
            it.setHidden(txt not in it.text().lower())

    def _emit_open_detail(self, item):
        rut = item.data(Qt.UserRole) or item.text().split(" - ")[0].strip()
        if rut:
            self.openDetailRequested.emit(rut)
