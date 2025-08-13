# controllers/familiar_editor_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox

class FamiliarEditorController(QObject):
    """
    Controller para FamiliarEditor (views/familiares_views.py) y
    FamiliarDialogView (ui/views/familiar_dialog.py).
    Valida y decide accept()/reject(). No toca DB.
    """
    def __init__(self, view, initial_data: dict | None = None):
        super().__init__(view)
        self.view = view
        if initial_data:
            set_data = getattr(self.view, "set_data", None)
            if callable(set_data):
                self.view.set_data(initial_data)
        self._connect()

    def _connect(self):
        self.view.saveRequested.connect(self._on_save)
        self.view.cancelRequested.connect(self.view.reject)

    def _on_save(self):
        data = self.view.get_data()

        # Validaciones mínimas
        if not (data.get("nombre") or "").strip():
            QMessageBox.warning(self.view, "Validación", "El nombre es obligatorio.")
            return

        edad = data.get("edad", None)
        if edad is not None:
            try:
                edad = int(edad)
            except Exception:
                QMessageBox.warning(self.view, "Validación", "La edad debe ser un número.")
                return
            if not (0 <= edad <= 120):
                QMessageBox.warning(self.view, "Validación", "La edad debe estar entre 0 y 120.")
                return

        # OK
        self.view.accept()

    def get_data(self) -> dict:
        return self.view.get_data()
