# ui/views/casa_detalle_view.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QGroupBox, QWidget, QListWidgetItem
)
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
QGroupBox {{
    font-weight: 700;
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
QListWidget {{
    background:#fff; border:2px solid {PALETTE['border']}; border-radius:12px; padding:6px;
}}
QPushButton[class="Primary"] {{
    background: {PALETTE['panel']};
    border: 2px solid {PALETTE['border']};
    border-radius: 12px;
    padding: 8px 12px; font-weight: 700;
}}
QPushButton[class="Primary"]:hover {{ background: #f2e6d2; }}
QPushButton[class="Danger"] {{
    background: #ffe8e8;
    border: 2px solid #a43c3c;
    color: #5a1111;
    border-radius: 12px;
    padding: 8px 12px; font-weight: 700;
}}
"""

class CasaDetalleView(QDialog):
    # Señales para el controller
    editRequested         = pyqtSignal()
    saveRequested         = pyqtSignal()
    cancelRequested       = pyqtSignal()
    closeRequested        = pyqtSignal()

    addHabitacionRequested    = pyqtSignal()
    editHabitacionRequested   = pyqtSignal(int)  # index
    deleteHabitacionRequested = pyqtSignal(int)  # index

    addBanoRequested    = pyqtSignal()
    editBanoRequested   = pyqtSignal(int)       # index
    deleteBanoRequested = pyqtSignal(int)       # index

    def __init__(self, casa_id=None, parent=None):
        super().__init__(parent)
        self.casa_id = casa_id
        self.setStyleSheet(QSS)
        self.setWindowTitle(f"Casa {'(editar)' if casa_id else '(nueva)'}")
        self._build_ui()
        self.set_edit_mode(False)

    # ---------- UI ----------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Top
        top = QHBoxLayout()
        title = QLabel("Detalle de casa")
        title.setStyleSheet("font-size:18px; font-weight:700;")
        self.edit_btn = QPushButton("Editar casa"); self.edit_btn.setProperty("class", "Primary")
        top.addWidget(title); top.addStretch(1); top.addWidget(self.edit_btn)
        layout.addLayout(top)

        # Form general
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        self.direccion_edit = QLineEdit()
        self.anfitrion_combo = QComboBox()
        form.addRow("Dirección:", self.direccion_edit)
        form.addRow("Anfitrión:", self.anfitrion_combo)
        layout.addLayout(form)

        # Capacidad total
        self.total_cap_lbl = QLabel("Capacidad total: 0")
        layout.addWidget(self.total_cap_lbl)

        # Habitaciones
        hab_group = QGroupBox("Habitaciones")
        hab_layout = QVBoxLayout(hab_group)
        self.hab_list = QListWidget()
        self.hab_list.itemDoubleClicked.connect(self._emit_edit_hab)
        hab_layout.addWidget(self.hab_list)
        hb = QHBoxLayout()
        self.btn_add_hab = QPushButton("Agregar habitación"); self.btn_add_hab.setProperty("class", "Primary")
        self.btn_edit_hab = QPushButton("Editar");            self.btn_edit_hab.setProperty("class", "Primary")
        self.btn_del_hab  = QPushButton("Eliminar");          self.btn_del_hab.setProperty("class", "Danger")
        hb.addWidget(self.btn_add_hab); hb.addStretch(1); hb.addWidget(self.btn_edit_hab); hb.addWidget(self.btn_del_hab)
        hab_layout.addLayout(hb)
        layout.addWidget(hab_group)

        # Baños
        ban_group = QGroupBox("Baños")
        ban_layout = QVBoxLayout(ban_group)
        self.bano_list = QListWidget()
        self.bano_list.itemDoubleClicked.connect(self._emit_edit_bano)
        ban_layout.addWidget(self.bano_list)
        bb = QHBoxLayout()
        self.btn_add_bano = QPushButton("Agregar baño"); self.btn_add_bano.setProperty("class", "Primary")
        self.btn_edit_bano = QPushButton("Editar");      self.btn_edit_bano.setProperty("class", "Primary")
        self.btn_del_bano  = QPushButton("Eliminar");    self.btn_del_bano.setProperty("class", "Danger")
        bb.addWidget(self.btn_add_bano); bb.addStretch(1); bb.addWidget(self.btn_edit_bano); bb.addWidget(self.btn_del_bano)
        ban_layout.addLayout(bb)
        layout.addWidget(ban_group)

        # Footer
        ft = QHBoxLayout()
        self.save_btn   = QPushButton("Guardar");  self.save_btn.setProperty("class", "Primary")
        self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setProperty("class", "Danger")
        self.close_btn  = QPushButton("Cerrar");   self.close_btn.setProperty("class", "Primary")
        ft.addStretch(1); ft.addWidget(self.save_btn); ft.addWidget(self.cancel_btn); ft.addWidget(self.close_btn)
        layout.addLayout(ft)

        # Enlaces → señales
        self.edit_btn.clicked.connect(self.editRequested.emit)
        self.save_btn.clicked.connect(self.saveRequested.emit)
        self.cancel_btn.clicked.connect(self.cancelRequested.emit)
        self.close_btn.clicked.connect(self.closeRequested.emit)

        self.btn_add_hab.clicked.connect(self.addHabitacionRequested.emit)
        self.btn_edit_hab.clicked.connect(lambda: self.editHabitacionRequested.emit(self.current_hab_index()))
        self.btn_del_hab.clicked.connect(lambda: self.deleteHabitacionRequested.emit(self.current_hab_index()))

        self.btn_add_bano.clicked.connect(self.addBanoRequested.emit)
        self.btn_edit_bano.clicked.connect(lambda: self.editBanoRequested.emit(self.current_bano_index()))
        self.btn_del_bano.clicked.connect(lambda: self.deleteBanoRequested.emit(self.current_bano_index()))

    # ---------- API para controller ----------
    def set_edit_mode(self, enabled: bool):
        self.direccion_edit.setReadOnly(not enabled)
        self.anfitrion_combo.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.cancel_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(not enabled)

    def set_hosts(self, items):
        """items = [(id, 'Nombre'), ...]"""
        self.anfitrion_combo.clear()
        for host_id, label in items:
            self.anfitrion_combo.addItem(label, host_id)

    def set_selected_host_by_id(self, host_id: int):
        for i in range(self.anfitrion_combo.count()):
            if int(self.anfitrion_combo.itemData(i)) == int(host_id):
                self.anfitrion_combo.setCurrentIndex(i)
                break

    def set_form_data(self, direccion: str, anfitrion_id: int):
        self.direccion_edit.setText(direccion or "")
        if anfitrion_id is not None:
            self.set_selected_host_by_id(anfitrion_id)

    def get_form_data(self):
        host_id = self.anfitrion_combo.currentData()
        return {
            "direccion": self.direccion_edit.text().strip(),
            "anfitrion_id": int(host_id) if host_id is not None else None
        }

    def set_habitaciones(self, habs):
        """habs = [{'capacidad': int, 'camas': [str,...]}]"""
        self.hab_list.clear()
        total = 0
        for i, h in enumerate(habs, 1):
            cap = int(h.get('capacidad', 0) or 0)
            camas = len(h.get('camas', []))
            total += cap
            it = QListWidgetItem(f"H{i}: capacidad={cap} pax, camas={camas}")
            it.setData(Qt.UserRole, i-1)  # índice lógico
            self.hab_list.addItem(it)
        self.total_cap_lbl.setText(f"Capacidad total: {total}")

    def set_banos(self, banos):
        """banos = [{'ubicacion': str, 'tina': bool}]"""
        self.bano_list.clear()
        for i, b in enumerate(banos, 1):
            tina = "Sí" if b.get('tina') else "No"
            it = QListWidgetItem(f"B{i}: {b.get('ubicacion','')} (Tina: {tina})")
            it.setData(Qt.UserRole, i-1)
            self.bano_list.addItem(it)

    def current_hab_index(self) -> int:
        it = self.hab_list.currentItem()
        if not it: return -1
        idx = it.data(Qt.UserRole)
        return int(idx) if idx is not None else self.hab_list.currentRow()

    def current_bano_index(self) -> int:
        it = self.bano_list.currentItem()
        if not it: return -1
        idx = it.data(Qt.UserRole)
        return int(idx) if idx is not None else self.bano_list.currentRow()

    # Doble clic ediciones
    def _emit_edit_hab(self, *_):
        self.editHabitacionRequested.emit(self.current_hab_index())

    def _emit_edit_bano(self, *_):
        self.editBanoRequested.emit(self.current_bano_index())
