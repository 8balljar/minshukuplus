# ui/views/familiar_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QHBoxLayout, QPushButton
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal

_RELACIONES = ["Cónyuge","Hijo/a","Padre/Madre","Hermano/a","Abuelo/a","Nieto/a","Tío/tía","Primo/a","Otro"]

class FamiliarDialogView(QDialog):
    saveRequested = pyqtSignal()
    cancelRequested = pyqtSignal()

    def __init__(self, parent=None, title="Familiar"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 300)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        form = QFormLayout(); form.setLabelAlignment(Qt.AlignRight)

        self.nombre = QLineEdit(placeholderText="Nombre y apellido")
        self.edad   = QLineEdit(placeholderText="Edad"); self.edad.setValidator(QIntValidator(0,120,self))
        self.sexo   = QComboBox(); self.sexo.addItems(["Hombre","Mujer"])
        self.rel    = QComboBox(); self.rel.addItems(_RELACIONES)

        form.addRow("Nombre:", self.nombre)
        form.addRow("Edad:",   self.edad)
        form.addRow("Sexo:",   self.sexo)
        form.addRow("Relación:", self.rel)
        root.addLayout(form)

        row = QHBoxLayout()
        self.btn_ok = QPushButton("Guardar");     self.btn_ok.setProperty("class","Primary")
        self.btn_cancel = QPushButton("Cancelar"); self.btn_cancel.setProperty("class","Danger")
        row.addStretch(1); row.addWidget(self.btn_ok); row.addWidget(self.btn_cancel)
        root.addLayout(row)

        self.btn_cancel.clicked.connect(self.cancelRequested.emit)
        self.btn_ok.clicked.connect(self.saveRequested.emit)

    # ---- API para el controller ----
    def set_data(self, data: dict):
        # data: {"nombre", "edad", "sexo", "relacion"}
        self.nombre.setText(data.get("nombre",""))
        self.edad.setText("" if data.get("edad") in (None, "") else str(data.get("edad")))
        self.sexo.setCurrentText(data.get("sexo","Hombre"))
        rel = data.get("relacion","Otro")
        if self.rel.findText(rel) == -1:
            self.rel.addItem(rel)
        self.rel.setCurrentText(rel)

    def get_data(self) -> dict:
        edad_txt = (self.edad.text() or "").strip()
        return {
            "nombre": self.nombre.text().strip(),
            "edad": int(edad_txt) if edad_txt else None,
            "sexo": self.sexo.currentText(),
            "relacion": self.rel.currentText(),
        }
