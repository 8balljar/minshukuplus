# controllers/anfitrion_detalle_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.anfitrion_detalle import AnfitrionDetalleView
from core.db import anfitrion as Anfitrion, Casa
import re

class AnfitrionDetalleController(QObject):
    """
    Carga el modelo, popula la vista, maneja edición y guardado.
    """
    def __init__(self, view: AnfitrionDetalleView, rut: str):
        super().__init__(view)
        self.view = view
        self._load_model(rut)
        self._snapshot = {}
        self._populate()
        self.view.set_edit_mode(False)
        self._connect()

    # ---------- Modelo ----------
    def _load_model(self, rut: str):
        self.model = Anfitrion.get_or_none(Anfitrion.rut == rut)
        if not self.model:
            QMessageBox.critical(self.view, "Error", f"No existe anfitrión con RUT {rut}")
            # Cierra el diálogo si no hay modelo
            self.view.reject()

    # ---------- Poblado ----------
    def _populate(self):
        if not self.model:
            return
        data = {
            "nombre":  self.model.nombre_completo or "",
            "rut":     self.model.rut or "",
            "telefono": self.model.telefono or "",
            "correo":   self.model.correo or "",
            "sexo":     "Mujer" if (self.model.sexo or "").lower().startswith("muj") else "Hombre",
            "casado":   bool(self.model.casado),
        }
        self.view.set_data(data)

        casas_items = [f"{c.id}: {c.direccion}" for c in Casa.select().where(Casa.anfitrion == self.model)]
        self.view.set_casas(casas_items)

        # snapshot para Cancelar
        self._snapshot = data.copy()

    # ---------- Señales ----------
    def _connect(self):
        self.view.editRequested.connect(self._on_edit)
        self.view.saveRequested.connect(self._on_save)
        self.view.cancelRequested.connect(self._on_cancel)
        self.view.closeRequested.connect(self._on_close)

    # ---------- Handlers ----------
    def _on_edit(self):
        self.view.set_edit_mode(True)

    def _on_save(self):
        if not self.model:
            return
        try:
            form = self.view.get_form_data()

            nombre = form["nombre"]
            correo = form["correo"]
            teltxt = form["telefono"]
            sexo   = form["sexo"]
            casado = form["casado"]

            if not nombre:
                raise ValueError("El nombre no puede estar vacío.")

            # normaliza teléfono (solo dígitos)
            tel_digits = re.sub(r"\D", "", teltxt or "")
            telefono = int(tel_digits) if tel_digits else 0

            self.model.nombre_completo = nombre
            self.model.telefono = telefono
            self.model.correo = correo
            self.model.sexo = sexo
            self.model.casado = casado
            self.model.save()

            # repoblar y bloquear edición
            self._populate()
            self.view.set_edit_mode(False)
            QMessageBox.information(self.view, "Guardado", "Cambios guardados correctamente.")
            # Devuelve código de aceptación al exec_() para refrescar listas arriba
            self.view.accept()

        except ValueError as ve:
            QMessageBox.warning(self.view, "Validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Error al guardar", str(e))

    def _on_cancel(self):
        # restaura snapshot y vuelve a lectura
        if self._snapshot:
            self.view.set_data(self._snapshot)
        self.view.set_edit_mode(False)

    def _on_close(self):
        self.view.reject()
