import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFormLayout,
    QPushButton, QListWidget, QWidget, QComboBox, QMessageBox, QTabWidget, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QIntValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp
from db import Hospedado, Familiar

# ----------------- Estilos -----------------
PALETTE = {
    "bg": "#f7f2e8", "panel": "#efdfc6", "border": "#5b3a29", "text": "#2b1d16",
}
QSS = f"""
QDialog {{
    background: {PALETTE['bg']}; color: {PALETTE['text']};
    font-family: "Noto Sans","Segoe UI",sans-serif; font-size: 15px;
}}
QWidget#Card {{
    background: #fff; border: 2px solid {PALETTE['border']}; border-radius: 12px;
}}
QLineEdit, QComboBox {{
    background: #fff; border: 1px solid #c7b299; border-radius: 8px; padding: 6px 8px;
}}
QLineEdit:focus, QComboBox:focus {{ border: 2px solid {PALETTE['border']}; }}
QListWidget {{
    background:#fff; border:2px solid {PALETTE['border']}; border-radius:12px; padding:6px;
}}
QTabWidget::pane {{ border:none; margin-top:8px; }}
QTabBar::tab {{
    background:{PALETTE['panel']}; border:2px solid {PALETTE['border']};
    padding:6px 12px; margin-right:6px; border-top-left-radius:10px; border-top-right-radius:10px; font-weight:600;
}}
QTabBar::tab:selected {{ background:#f2e6d2; }}
QPushButton[class="Primary"] {{
    background:{PALETTE['panel']}; border:2px solid {PALETTE['border']};
    border-radius:12px; padding:10px 14px; font-weight:700;
}}
QPushButton[class="Primary"]:hover {{ background:#f2e6d2; }}
QPushButton[class="Danger"] {{
    background:#ffe8e8; border:2px solid #a43c3c; color:#5a1111;
    border-radius:12px; padding:10px 14px; font-weight:700;
}}
"""

# ----------------- Diálogo de Agregar Familiar -----------------
class AddFamiliarDialog(QDialog):
    def __init__(self, parent, hospedado: Hospedado):
        super().__init__(parent)
        self.hospedado = hospedado
        self.setWindowTitle("Agregar familiar")
        self.setModal(True)
        self.setFixedSize(420, 300)
        self.setStyleSheet(QSS)

        lay = QVBoxLayout(self)
        card = QWidget(objectName="Card"); lay_card = QFormLayout(card); lay_card.setLabelAlignment(Qt.AlignRight)

        self.nombre = QLineEdit(); self.nombre.setPlaceholderText("Nombre y apellido")
        self.edad   = QLineEdit(); self.edad.setValidator(QIntValidator(0, 120, self)); self.edad.setPlaceholderText("Edad")
        self.sexo   = QComboBox(); self.sexo.addItems(["Hombre","Mujer"])
        self.rel    = QComboBox(); self.rel.addItems(["Cónyuge","Hijo/a","Padre/Madre","Hermano/a","Otro"])

        lay_card.addRow("Nombre:", self.nombre)
        lay_card.addRow("Edad:", self.edad)
        lay_card.addRow("Sexo:", self.sexo)
        lay_card.addRow("Relación:", self.rel)

        lay.addWidget(card)

        btns = QHBoxLayout()
        self.btn_save = QPushButton("Guardar familiar"); self.btn_save.setProperty("class","Primary")
        self.btn_cancel = QPushButton("Cancelar"); self.btn_cancel.setProperty("class","Danger")
        btns.addStretch(1); btns.addWidget(self.btn_save); btns.addWidget(self.btn_cancel)
        lay.addLayout(btns)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self._on_save)

    def _on_save(self):
        nombre = self.nombre.text().strip()
        edad_txt = self.edad.text().strip()
        edad = int(edad_txt) if edad_txt else None
        if not nombre:
            QMessageBox.warning(self, "Falta nombre", "Ingresa el nombre del familiar.")
            return
        try:
            Familiar.create(
                hospedado=self.hospedado,
                nombre=nombre,
                edad=edad,
                sexo=self.sexo.currentText(),
                relacion=self.rel.currentText(),
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar el familiar:\n{e}")
            return
        self.accept()

# ----------------- Vista de Detalle -----------------
class HospedadoDetalleView(QDialog):
    def __init__(self, hospedado: Hospedado, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de: {hospedado.nombre_completo}")
        self.setMinimumSize(720, 560)
        self.setStyleSheet(QSS)

        self.model = hospedado
        self._build_ui()
        self._populate()
        self._set_edit_mode(False)
        self._connect()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(10)

        # Título
        top = QHBoxLayout()
        title = QLabel("Detalle de hospedado"); title.setStyleSheet("font-size:20px; font-weight:700;")
        self.edit_btn = QPushButton("Editar"); self.edit_btn.setProperty("class","Primary")
        top.addWidget(title); top.addStretch(1); top.addWidget(self.edit_btn)
        root.addLayout(top)

        body = QHBoxLayout(); body.setSpacing(12)

        # Izquierda
        left_card = QWidget(objectName="Card"); left = QVBoxLayout(left_card); left.setContentsMargins(14,14,14,14)

        # Avatar cuadrado
        self.avatar = QLabel()
        self.avatar.setFixedSize(140, 140)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setStyleSheet("background:#fff; border:2px solid #c7b299; border-radius:12px;")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        avatar_path = os.path.join(base_dir, "assets", "user.png")
        self._set_avatar(avatar_path)
        left.addWidget(self.avatar, alignment=Qt.AlignHCenter)

        self.sexo_combo = QComboBox(); self.sexo_combo.addItems(["Hombre","Mujer"])
        self.edad_edit  = QLineEdit(placeholderText="Edad"); self.edad_edit.setValidator(QIntValidator(0,120,self))
        left.addWidget(QLabel("Sexo")); left.addWidget(self.sexo_combo)
        left.addWidget(QLabel("Edad")); left.addWidget(self.edad_edit)
        left.addStretch(1)

        # Derecha
        right_card = QWidget(objectName="Card"); right = QVBoxLayout(right_card); right.setContentsMargins(14,14,14,14)
        form = QFormLayout(); form.setLabelAlignment(Qt.AlignRight)
        self.nombre_edit = QLineEdit()
        self.rut_edit    = QLineEdit(); self.rut_edit.setReadOnly(True)
        self.correo_edit = QLineEdit()
        self.tel_edit    = QLineEdit(); self.tel_edit.setInputMask("+56 9 0000 0000;_")
        self.nombre_edit.setPlaceholderText("Nombre y apellido")
        self.correo_edit.setPlaceholderText("correo@ejemplo.com")
        self.tel_edit.setPlaceholderText("+56 9 1234 5678")
        form.addRow("Nombre completo:", self.nombre_edit)
        form.addRow("RUT:", self.rut_edit)
        form.addRow("Correo:", self.correo_edit)
        form.addRow("Teléfono:", self.tel_edit)
        right.addLayout(form); right.addStretch(1)

        body.addWidget(left_card, 4); body.addWidget(right_card, 8)
        root.addLayout(body)

        # Familiares (solo una pestaña visible)
        self.tabs = QTabWidget(); self.tabs.setTabBarAutoHide(True)
        self.tab_list = QWidget(); t1 = QVBoxLayout(self.tab_list)
        t1.addWidget(QLabel("Familiares"))
        self.fam_list = QListWidget(); self.fam_list.setAlternatingRowColors(True)
        t1.addWidget(self.fam_list, 1)

        row = QHBoxLayout()
        self.btn_add_fam = QPushButton("Agregar familiar"); self.btn_add_fam.setProperty("class","Primary")
        self.btn_del_fam = QPushButton("Eliminar"); self.btn_del_fam.setProperty("class","Danger")
        row.addWidget(self.btn_add_fam); row.addStretch(1); row.addWidget(self.btn_del_fam)
        t1.addLayout(row)

        self.tabs.addTab(self.tab_list, "Familiares")
        root.addWidget(self.tabs, 1)

        # Botonera
        btns = QHBoxLayout()
        self.save_btn   = QPushButton("Guardar");  self.save_btn.setProperty("class","Primary")
        self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setProperty("class","Danger")
        self.close_btn  = QPushButton("Cerrar");   self.close_btn.setProperty("class","Primary")
        btns.addStretch(1); btns.addWidget(self.save_btn); btns.addWidget(self.cancel_btn); btns.addWidget(self.close_btn)
        root.addLayout(btns)

        self.setLayout(root)

    # ---------- Helpers ----------
    def _s(self, v): return "" if v is None else str(v)

    def _sexo_text(self, v):
        s = (v or "").strip().lower()
        if s.startswith("muj") or s in {"f", "femenino"}: return "Mujer"
        if s.startswith("hom") or s in {"m", "masculino", "h"}: return "Hombre"
        return "Hombre"

    def _square_pixmap(self, pix: QPixmap, size: int) -> QPixmap:
        if pix.isNull(): return QPixmap()
        scaled = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = max(0, (scaled.width() - size) // 2)
        y = max(0, (scaled.height() - size) // 2)
        return scaled.copy(x, y, size, size)

    def _set_avatar(self, path_or_pix):
        pix = QPixmap(path_or_pix) if isinstance(path_or_pix, str) else path_or_pix
        if pix.isNull():
            self.avatar.setText("Sin\nfoto")
        else:
            size = min(self.avatar.width(), self.avatar.height())
            self.avatar.setPixmap(self._square_pixmap(pix, size))

    def _snapshot_now(self):
        return {
            "nombre": self.nombre_edit.text(),
            "rut": self.rut_edit.text(),
            "correo": self.correo_edit.text(),
            "telefono": self.tel_edit.text(),
            "edad": self.edad_edit.text(),
            "sexo": self.sexo_combo.currentText(),
        }

    # ---------- Datos ----------
    def _populate(self):
        h = self.model
        self.nombre_edit.setText(self._s(h.nombre_completo))
        self.rut_edit.setText(self._s(h.rut))
        self.correo_edit.setText(self._s(h.correo))
        self.tel_edit.setText(self._s(h.telefono))
        self.edad_edit.setText(self._s(h.edad))
        self.sexo_combo.setCurrentText(self._sexo_text(h.sexo))
        self._reload_familiares()
        self._snapshot = self._snapshot_now()

    # ---------- Modo edición ----------
    def _set_edit_mode(self, enabled: bool):
        self.nombre_edit.setReadOnly(not enabled)
        self.correo_edit.setReadOnly(not enabled)
        self.tel_edit.setReadOnly(not enabled)
        self.edad_edit.setReadOnly(not enabled)
        self.sexo_combo.setEnabled(enabled)
        self.save_btn.setEnabled(enabled); self.cancel_btn.setEnabled(enabled); self.edit_btn.setEnabled(not enabled)

    def _connect(self):
        self.edit_btn.clicked.connect(lambda: self._set_edit_mode(True))
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.save_btn.clicked.connect(self._on_save)
        self.close_btn.clicked.connect(self.close)
        self.btn_add_fam.clicked.connect(self._open_add_familiar)
        self.btn_del_fam.clicked.connect(self._on_delete_familiar)

    # ---------- Acciones ----------
    def _on_cancel(self):
        s = getattr(self, "_snapshot", None)
        if s:
            self.nombre_edit.setText(s["nombre"]); self.rut_edit.setText(s["rut"])
            self.correo_edit.setText(s["correo"]); self.tel_edit.setText(s["telefono"])
            self.edad_edit.setText(s["edad"]); self.sexo_combo.setCurrentText(s["sexo"])
        self._set_edit_mode(False)

    def _on_save(self):
        edad_txt = self.edad_edit.text().strip()
        try:
            edad_val = int(edad_txt) if edad_txt else None
            if edad_val is not None and not (0 <= edad_val <= 120): raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Edad inválida", "Ingresa una edad entre 0 y 120."); return

        h = self.model
        h.nombre_completo = self.nombre_edit.text().strip()
        h.correo = self.correo_edit.text().strip() or None
        h.telefono = self.tel_edit.text().strip() or None
        h.edad = edad_val
        h.sexo = self.sexo_combo.currentText()

        try:
            h.save()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}"); return

        self._snapshot = self._snapshot_now()
        self._set_edit_mode(False)
        QMessageBox.information(self, "Listo", "Cambios guardados.")

    # ---------- Familiares ----------
    def _reload_familiares(self):
        self.fam_list.clear()
        try:
            qs = Familiar.select().where(Familiar.hospedado == self.model)
            for f in qs:
                item = QListWidgetItem(f"{self._s(f.nombre)} — {self._s(f.relacion)} — {self._s(f.edad)}")
                item.setData(Qt.UserRole, f.id)
                self.fam_list.addItem(item)
        except Exception:
            pass

    def _open_add_familiar(self):
        dlg = AddFamiliarDialog(self, self.model)
        if dlg.exec_() == QDialog.Accepted:
            self._reload_familiares()

    def _on_delete_familiar(self):
        item = self.fam_list.currentItem()
        if not item:
            QMessageBox.information(self, "Selecciona un familiar", "Elige un elemento de la lista.")
            return
        fam_id = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Confirmar", "¿Eliminar el familiar seleccionado?") == QMessageBox.Yes:
            try:
                Familiar.get_by_id(fam_id).delete_instance()
                self._reload_familiares()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")
