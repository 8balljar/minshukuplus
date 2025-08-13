# ui/views/hospedado_detalle_view.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFormLayout,
    QPushButton, QListWidget, QWidget, QComboBox, QTabWidget, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal

PALETTE = {"bg": "#f7f2e8", "panel": "#efdfc6", "border": "#5b3a29", "text": "#2b1d16"}
QSS = f"""
QDialog {{ background:{PALETTE['bg']}; color:{PALETTE['text']}; font-family:"Noto Sans","Segoe UI",sans-serif; font-size:15px; }}
QWidget#Card {{ background:#fff; border:2px solid {PALETTE['border']}; border-radius:12px; }}
QLineEdit, QComboBox {{ background:#fff; border:1px solid #c7b299; border-radius:8px; padding:6px 8px; }}
QLineEdit:focus, QComboBox:focus {{ border:2px solid {PALETTE['border']}; }}
QListWidget {{ background:#fff; border:2px solid {PALETTE['border']}; border-radius:12px; padding:6px; }}
QTabWidget::pane {{ border:none; margin-top:8px; }}
QTabBar::tab {{ background:{PALETTE['panel']}; border:2px solid {PALETTE['border']}; padding:6px 12px; margin-right:6px; border-top-left-radius:10px; border-top-right-radius:10px; font-weight:600; }}
QTabBar::tab:selected {{ background:#f2e6d2; }}
QPushButton[class="Primary"] {{ background:{PALETTE['panel']}; border:2px solid {PALETTE['border']}; border-radius:12px; padding:10px 14px; font-weight:700; }}
QPushButton[class="Danger"]  {{ background:#ffe8e8; border:2px solid #a43c3c; color:#5a1111; border-radius:12px; padding:10px 14px; font-weight:700; }}
"""

class HospedadoDetalle(QDialog):
    # Señales
    editRequested   = pyqtSignal()
    saveRequested   = pyqtSignal()
    cancelRequested = pyqtSignal()
    closeRequested  = pyqtSignal()
    addFamiliarRequested    = pyqtSignal()
    deleteFamiliarRequested = pyqtSignal(int)  # familiar_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(720, 560)
        self.setStyleSheet(QSS)
        self._build_ui()
        self.set_edit_mode(False)

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(10)

        # Título
        top = QHBoxLayout()
        title = QLabel("Detalle de hospedado"); title.setStyleSheet("font-size:20px; font-weight:700;")
        self.edit_btn = QPushButton("Editar"); self.edit_btn.setProperty("class","Primary")
        self.edit_btn.clicked.connect(self.editRequested.emit)
        top.addWidget(title); top.addStretch(1); top.addWidget(self.edit_btn)
        root.addLayout(top)

        body = QHBoxLayout(); body.setSpacing(12)

        # Izquierda (avatar + sexo/edad)
        left_card = QWidget(objectName="Card"); left = QVBoxLayout(left_card); left.setContentsMargins(14,14,14,14)

        self.avatar = QLabel()
        self.avatar.setFixedSize(140, 140)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setStyleSheet("background:#fff; border:2px solid #c7b299; border-radius:12px;")

        self.sexo_combo = QComboBox(); self.sexo_combo.addItems(["Hombre","Mujer"])
        self.edad_edit  = QLineEdit(placeholderText="Edad"); self.edad_edit.setValidator(QIntValidator(0,120,self))
        left.addWidget(self.avatar, alignment=Qt.AlignHCenter)
        left.addWidget(QLabel("Sexo")); left.addWidget(self.sexo_combo)
        left.addWidget(QLabel("Edad")); left.addWidget(self.edad_edit)
        left.addStretch(1)

        # Derecha (form)
        right_card = QWidget(objectName="Card"); right = QVBoxLayout(right_card); right.setContentsMargins(14,14,14,14)
        form = QFormLayout(); form.setLabelAlignment(Qt.AlignRight)
        self.nombre_edit = QLineEdit(); self.nombre_edit.setPlaceholderText("Nombre y apellido")
        self.rut_edit    = QLineEdit(); self.rut_edit.setReadOnly(True)
        self.correo_edit = QLineEdit(); self.correo_edit.setPlaceholderText("correo@ejemplo.com")
        self.tel_edit    = QLineEdit(); self.tel_edit.setInputMask("+56 9 0000 0000;_")
        form.addRow("Nombre completo:", self.nombre_edit)
        form.addRow("RUT:", self.rut_edit)
        form.addRow("Correo:", self.correo_edit)
        form.addRow("Teléfono:", self.tel_edit)
        right.addLayout(form); right.addStretch(1)

        body.addWidget(left_card, 4); body.addWidget(right_card, 8)
        root.addLayout(body)

        # Familiares
        self.tabs = QTabWidget(); self.tabs.setTabBarAutoHide(True)
        tab_list = QWidget(); t1 = QVBoxLayout(tab_list)
        t1.addWidget(QLabel("Familiares"))
        self.fam_list = QListWidget(); self.fam_list.setAlternatingRowColors(True)
        t1.addWidget(self.fam_list, 1)

        row = QHBoxLayout()
        self.btn_add_fam = QPushButton("Agregar familiar"); self.btn_add_fam.setProperty("class","Primary")
        self.btn_del_fam = QPushButton("Eliminar");         self.btn_del_fam.setProperty("class","Danger")
        self.btn_add_fam.clicked.connect(self.addFamiliarRequested.emit)
        self.btn_del_fam.clicked.connect(self._emit_delete_familiar)
        row.addWidget(self.btn_add_fam); row.addStretch(1); row.addWidget(self.btn_del_fam)
        t1.addLayout(row)

        self.tabs.addTab(tab_list, "Familiares")
        root.addWidget(self.tabs, 1)

        # Botonera
        btns = QHBoxLayout()
        self.save_btn   = QPushButton("Guardar");  self.save_btn.setProperty("class","Primary"); self.save_btn.clicked.connect(self.saveRequested.emit)
        self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setProperty("class","Danger"); self.cancel_btn.clicked.connect(self.cancelRequested.emit)
        self.close_btn  = QPushButton("Cerrar");   self.close_btn.setProperty("class","Primary"); self.close_btn.clicked.connect(self.closeRequested.emit)
        btns.addStretch(1); btns.addWidget(self.save_btn); btns.addWidget(self.cancel_btn); btns.addWidget(self.close_btn)
        root.addLayout(btns)

    # ---------- API ----------
    def set_edit_mode(self, enabled: bool):
        self.nombre_edit.setReadOnly(not enabled)
        self.correo_edit.setReadOnly(not enabled)
        self.tel_edit.setReadOnly(not enabled)
        self.edad_edit.setReadOnly(not enabled)
        self.sexo_combo.setEnabled(enabled)
        self.save_btn.setEnabled(enabled); self.cancel_btn.setEnabled(enabled); self.edit_btn.setEnabled(not enabled)

    def set_avatar(self, pix_or_path=None):
        if isinstance(pix_or_path, str):
            pix = QPixmap(pix_or_path)
        else:
            pix = pix_or_path or QPixmap()
        if pix.isNull():
            self.avatar.setText("Sin\nfoto")
        else:
            size = min(self.avatar.width(), self.avatar.height())
            scaled = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = max(0, (scaled.width() - size) // 2); y = max(0, (scaled.height() - size) // 2)
            self.avatar.setPixmap(scaled.copy(x, y, size, size))

    def set_data(self, data: dict):
        self.nombre_edit.setText(data.get("nombre",""))
        self.rut_edit.setText(data.get("rut",""))
        self.correo_edit.setText(data.get("correo",""))
        self.tel_edit.setText(data.get("telefono",""))
        self.sexo_combo.setCurrentText(data.get("sexo","Hombre"))
        self.edad_edit.setText("" if data.get("edad") in (None,"") else str(data.get("edad")))

    def get_data(self) -> dict:
        return {
            "nombre":    self.nombre_edit.text().strip(),
            "rut":       self.rut_edit.text().strip(),  # readonly
            "correo":    self.correo_edit.text().strip(),
            "telefono":  self.tel_edit.text().strip(),
            "sexo":      self.sexo_combo.currentText(),
            "edad":      self.edad_edit.text().strip(),
        }

    def set_familiares(self, fams):
        """fams = [{'id':int,'nombre':str,'relacion':str,'edad':Optional[int]}]"""
        self.fam_list.clear()
        for f in fams:
            label = f"{f.get('nombre','')} — {f.get('relacion','')} — {f.get('edad','') if f.get('edad') is not None else ''}"
            it = QListWidgetItem(label)
            it.setData(Qt.UserRole, f.get("id"))
            self.fam_list.addItem(it)

    def current_familiar_id(self) -> int:
        it = self.fam_list.currentItem()
        return int(it.data(Qt.UserRole)) if it and it.data(Qt.UserRole) is not None else 0

    def _emit_delete_familiar(self):
        fam_id = self.current_familiar_id()
        if fam_id:
            self.deleteFamiliarRequested.emit(fam_id)
