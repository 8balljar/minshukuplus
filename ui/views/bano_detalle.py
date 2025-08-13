# ui/views/bano_detalle_view.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QPushButton, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal

class BanoDetalleView(QDialog):
    saveRequested = pyqtSignal()
    cancelRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Baño")
        self._build_ui()

    def _build_ui(self):
        L = QVBoxLayout(self)
        form = QFormLayout()

        self.ubic_input = QLineEdit()
        self.ubic_input.setPlaceholderText("Ubicación (ej. “Piso 1 – pasillo”)")
        form.addRow("Ubicación:", self.ubic_input)

        self.tina_check = QCheckBox("Tina")
        form.addRow("", self.tina_check)

        L.addLayout(form)

        footer = QHBoxLayout()
        ok_btn = QPushButton("OK", clicked=self.saveRequested.emit)
        cancel_btn = QPushButton("Cancelar", clicked=self.cancelRequested.emit)
        footer.addWidget(ok_btn)
        footer.addWidget(cancel_btn)
        L.addLayout(footer)

    # ---- API para el controller ----
    def set_data(self, data: dict):
        self.ubic_input.setText(data.get("ubicacion", ""))
        self.tina_check.setChecked(bool(data.get("tina", False)))

    def get_data(self) -> dict:
        return {
            "ubicacion": self.ubic_input.text().strip(),
            "tina": self.tina_check.isChecked(),
        }
