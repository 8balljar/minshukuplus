# controllers/habitacion_detalle_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.habitacion_detalle import HabitacionDetalleView

class HabitacionDetalleController(QObject):
    """
    Controla el diálogo de habitación:
    - carga datos iniciales (si hay)
    - valida y acepta al guardar
    """
    def __init__(self, view: HabitacionDetalleView, data: dict | None = None):
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
        cap = int(data.get("capacidad", 0))
        if cap < 1:
            QMessageBox.warning(self.view, "Validación", "La capacidad debe ser al menos 1.")
            return
        # (opcional) coherencia básica: no más camas que capacidad, si así lo deseas:
        # if len(data.get("camas", [])) > cap:
        #     QMessageBox.warning(self.view, "Validación", "No puede haber más camas que la capacidad.")
        #     return
        self.view.accept()

    # Útil si prefieres pedir los datos al controller
    def get_data(self) -> dict:
        return self.view.get_data()
