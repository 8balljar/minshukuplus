# views/casa_views.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QSizePolicy, QListWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal

ICONS = {
    "add": "assets/icons/add.svg",
    "delete": "assets/icons/delete.svg",
    "house": "assets/icons/house_japan.svg",
}

class CasaView(QWidget):
    # Señales para el controller
    refreshRequested = pyqtSignal()
    addRequested = pyqtSignal()
    deleteRequested = pyqtSignal()
    openDetailRequested = pyqtSignal(int)  # casa_id

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 400)
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(10)

        # Izquierda: lista + búsqueda
        left = QVBoxLayout()
        left.setSpacing(8)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar por dirección o anfitrión…")
        self.search.textChanged.connect(self._filter_list)

        self.lista = QListWidget()
        self.lista.setAlternatingRowColors(True)
        self.lista.setStyleSheet(
            "background:#fff; border:2px solid #5b3a29; border-radius:12px; padding:6px;")
        self.lista.itemDoubleClicked.connect(self._emit_open_detail)

        left.addWidget(self.search)
        left.addWidget(self.lista, 1)

        # Derecha: card con formulario
        right_card = QWidget(objectName="Card")
        right_card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        card = QVBoxLayout(right_card)
        card.setContentsMargins(14, 14, 14, 14)
        card.setSpacing(10)

        title = QLabel("Nueva casa")
        title.setStyleSheet("font-size:18px; font-weight:700;")
        card.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección completa")
        self.anfitrion_combo = QComboBox()

        form.addRow("Dirección:", self.direccion_input)
        form.addRow("Anfitrión:", self.anfitrion_combo)
        card.addLayout(form)

        # Botones
        btns = QHBoxLayout()
        self.add_btn = QPushButton("Agregar Casa")
        self.del_btn = QPushButton("Eliminar Casa")
        self.add_btn.setProperty("class", "Primary")
        self.del_btn.setProperty("class", "Danger")
        self.add_btn.setIcon(QIcon(ICONS["add"]))
        self.del_btn.setIcon(QIcon(ICONS["delete"]))
        self.add_btn.setMinimumHeight(40)
        self.del_btn.setMinimumHeight(40)
        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)

        card.addSpacing(6)
        card.addLayout(btns)
        card.addStretch(1)

        root.addLayout(left, 6)
        root.addWidget(right_card, 5)

        # Conexiones (solo señales)
        self.add_btn.clicked.connect(self.addRequested.emit)
        self.del_btn.clicked.connect(self.deleteRequested.emit)

        self.setLayout(root)

    # ---------- API para controller ----------
    def set_hosts(self, items):
        """Carga anfitriones en el combo.
        items: lista de tuplas [(id, 'Nombre visible'), ...]
        """
        self.anfitrion_combo.clear()
        for host_id, label in items:
            self.anfitrion_combo.addItem(label, host_id)

    def add_list_item(self, casa_id: int, direccion: str, anfitrion_nombre: str):
        text = f"{casa_id}: {direccion} (Anf: {anfitrion_nombre})"
        it = QListWidgetItem(text)
        it.setData(Qt.UserRole, casa_id)
        self.lista.addItem(it)

    def clear_form(self):
        self.direccion_input.clear()
        if self.anfitrion_combo.count() > 0:
            self.anfitrion_combo.setCurrentIndex(0)

    def get_form_data(self):
        host_id = self.anfitrion_combo.currentData()
        return {
            "direccion": self.direccion_input.text().strip(),
            "anfitrion_id": int(host_id) if host_id is not None else None
        }

    def current_selected_id(self) -> int:
        it = self.lista.currentItem()
        if not it:
            return 0
        cid = it.data(Qt.UserRole)
        if cid:
            return int(cid)
        # fallback por si llega texto plano
        try:
            return int(it.text().split(":")[0])
        except Exception:
            return 0

    # ---------- Internos UI ----------
    def _filter_list(self, text):
        text = (text or "").strip().lower()
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            item.setHidden(text not in item.text().lower())

    def _emit_open_detail(self, item):
        cid = item.data(Qt.UserRole)
        if cid is None:
            try:
                cid = int(item.text().split(":")[0])
            except Exception:
                cid = 0
        if cid:
            self.openDetailRequested.emit(int(cid))

    def refresh(self):
        self.refreshRequested.emit()
