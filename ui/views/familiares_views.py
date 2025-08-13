# views/familiares_views.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QHBoxLayout, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

RELACIONES = [
    "Cónyuge", "Hijo/a", "Padre", "Madre",
    "Hermano/a", "Abuelo/a", "Nieto/a", "Tío/tía", "Primo/a", "Otro"
]

class FamiliarForm(QWidget):
    """
    Formulario reutilizable para crear/editar un Familiar.
    - Usa QSpinBox para edad (0–120).
    - Métodos: get_data(), set_data(), clear(), is_valid()
    - Señal submitted(dict) si se usa el botón interno (with_submit=True).
    """
    submitted = pyqtSignal(dict)

    def __init__(self, with_submit: bool = True, parent=None):
        super().__init__(parent)
        self._build_ui(with_submit)

    def _build_ui(self, with_submit: bool):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre y apellido")

        self.edad = QSpinBox()
        self.edad.setRange(0, 120)
        self.edad.setValue(0)

        self.sexo = QComboBox()
        self.sexo.addItems(["Hombre", "Mujer"])

        self.relacion = QComboBox()
        self.relacion.addItems(RELACIONES)

        form.addRow("Nombre:",   self.nombre)
        form.addRow("Edad:",     self.edad)
        form.addRow("Sexo:",     self.sexo)
        form.addRow("Relación:", self.relacion)
        root.addLayout(form)

        if with_submit:
            row = QHBoxLayout()
            row.addStretch(1)
            self.submit_btn = QPushButton("Guardar familiar")
            self.submit_btn.setProperty("class", "Primary")
            row.addWidget(self.submit_btn)
            root.addLayout(row)
            self.submit_btn.clicked.connect(self._emit_submit)

        self.setLayout(root)

    # ---------- API ----------
    def get_data(self) -> dict:
        return {
            "nombre":   self.nombre.text().strip(),
            "edad":     int(self.edad.value()),
            "sexo":     self.sexo.currentText(),
            "relacion": self.relacion.currentText(),
        }

    def set_data(self, data: dict):
        self.nombre.setText(data.get("nombre", ""))
        self.edad.setValue(int(data.get("edad", 0) or 0))
        self.sexo.setCurrentText(data.get("sexo", "Hombre"))
        rel = data.get("relacion", RELACIONES[0])
        if rel not in RELACIONES:
            self.relacion.addItem(rel)
        self.relacion.setCurrentText(rel)

    def clear(self):
        self.nombre.clear()
        self.edad.setValue(0)
        self.sexo.setCurrentIndex(0)
        self.relacion.setCurrentIndex(0)

    def is_valid(self) -> bool:
        return bool(self.nombre.text().strip())

    # ---------- Interno ----------
    def _emit_submit(self):
        if not self.is_valid():
            return
        self.submitted.emit(self.get_data())


class FamiliarEditor(QDialog):
    """
    Diálogo para crear/editar un familiar usando FamiliarForm.
    VISTA PURA: emite señales; no valida ni toca DB por sí sola.
    """
    saveRequested = pyqtSignal()
    cancelRequested = pyqtSignal()

    def __init__(self, data: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Familiar")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        self.form = FamiliarForm(with_submit=False)
        layout.addWidget(self.form)

        # Botones
        row = QHBoxLayout()
        self.ok_btn = QPushButton("OK");        self.ok_btn.setProperty("class", "Primary")
        self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setProperty("class", "Danger")
        row.addStretch(1); row.addWidget(self.ok_btn); row.addWidget(self.cancel_btn)
        layout.addLayout(row)

        if data:
            self.form.set_data(data)

        # Señales en vez de accept/reject directos (lo hace el controller)
        self.ok_btn.clicked.connect(self.saveRequested.emit)
        self.cancel_btn.clicked.connect(self.cancelRequested.emit)

    # API consistente con otras vistas de diálogo
    def get_data(self) -> dict:
        return self.form.get_data()

    def set_data(self, data: dict):
        self.form.set_data(data)
