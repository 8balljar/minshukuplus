# controllers/bano_detalle_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.bano_detalle import BanoDetalleView

class BanoDetalleController(QObject):
    """
    Orquesta el diálogo del baño:
    - inicializa datos (si vienen)
    - valida y acepta en 'OK'
    """
    def __init__(self, view: BanoDetalleView, data: dict | None = None):
        super().__init__(view)
        self.view = view
        if data:
            self.view.set_data(data)
        self._connect()

    def _connect(self):
        self.view.saveRequested.connect(self._on_save)
        self.view.cancelRequested.connect(self.view.reject)

    def _on_save(self):
        data = self.view.get_data()
        if not data["ubicacion"]:
            QMessageBox.warning(self.view, "Validación", "La ubicación no puede estar vacía.")
            return
        self.view.accept()

    # Útil si prefieres pedir los datos al controller
    def get_data(self) -> dict:
        return self.view.get_data()
