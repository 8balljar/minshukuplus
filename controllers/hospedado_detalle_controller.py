# controllers/hospedado_detalle_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.hospedado_detalle import HospedadoDetalleView
from ui.views.familiares_views import FamiliarEditor   # diálogo (vista pura)
from controllers.familiar_editor_controller import FamiliarEditorController
from core.db import Hospedado, Familiar
import re
import os

class HospedadoDetalleController(QObject):
    def __init__(self, view: HospedadoDetalleView, rut: str):
        super().__init__(view)
        self.view = view
        self.model = Hospedado.get_or_none(Hospedado.rut == rut)
        if not self.model:
            QMessageBox.critical(self.view, "Error", f"No existe hospedado con RUT {rut}")
            self.view.reject()
            return
        self._snapshot = {}
        self._connect()
        self._populate()
        self.view.set_edit_mode(False)

    # ---------- Wiring ----------
    def _connect(self):
        v = self.view
        v.editRequested.connect(lambda: v.set_edit_mode(True))
        v.saveRequested.connect(self._on_save)
        v.cancelRequested.connect(self._on_cancel)
        v.closeRequested.connect(v.reject)
        v.addFamiliarRequested.connect(self._on_add_familiar)
        v.deleteFamiliarRequested.connect(self._on_delete_familiar)

    # ---------- Populate ----------
    def _populate(self):
        data = {
            "nombre":   self.model.nombre_completo or "",
            "rut":      self.model.rut or "",
            "correo":   self.model.correo or "",
            "telefono": str(self.model.telefono or ""),
            "sexo":     self.model.sexo or "Hombre",
            "edad":     int(self.model.edad or 0) if self.model.edad is not None else "",
        }
        self.view.set_data(data)
        self._snapshot = data.copy()

        # Avatar opcional (assets/user.png)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.join(os.path.dirname(os.path.dirname(base_dir)), "assets", "user.png")
        self.view.set_avatar(candidate if os.path.exists(candidate) else None)

        self._reload_familiares()

    def _reload_familiares(self):
        fams = []
        for f in Familiar.select().where(Familiar.hospedado == self.model):
            fams.append({
                "id": f.id,
                "nombre": f.nombre,
                "relacion": f.relacion,
                "edad": f.edad
            })
        self.view.set_familiares(fams)

    # ---------- Actions ----------
    def _on_save(self):
        try:
            form = self.view.get_data()
            nombre = form["nombre"]
            correo = form["correo"]
            tel    = re.sub(r"\D", "", form["telefono"] or "")
            edad   = int(form["edad"]) if (form["edad"] or "").isdigit() else None
            sexo   = form["sexo"]

            if edad is not None and not (0 <= edad <= 120):
                raise ValueError("La edad debe estar entre 0 y 120.")
            if not nombre:
                raise ValueError("El nombre no puede estar vacío.")
            if correo and "@" not in correo:
                raise ValueError("Correo no válido.")

            self.model.nombre_completo = nombre
            self.model.correo = correo or None
            self.model.telefono = tel or None
            self.model.edad = edad
            self.model.sexo = sexo
            self.model.save()

            QMessageBox.information(self.view, "Listo", "Cambios guardados.")
            self._snapshot = form
            self.view.set_edit_mode(False)
            self.view.accept()  # el caller puede refrescar la lista
        except ValueError as ve:
            QMessageBox.warning(self.view, "Validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"No se pudo guardar: {e}")

    def _on_cancel(self):
        self.view.set_data(self._snapshot)
        self.view.set_edit_mode(False)

    # --------- Familiares ---------
    def _on_add_familiar(self):
        dlg = FamiliarEditor(parent=self.view)
        ctrl = FamiliarEditorController(dlg)
        if dlg.exec_():
            data = ctrl.get_data()
            try:
                Familiar.create(
                    hospedado=self.model,
                    nombre=data["nombre"],
                    edad=data["edad"],
                    sexo=data["sexo"],
                    relacion=data["relacion"],
                )
                self._reload_familiares()
            except Exception as e:
                QMessageBox.critical(self.view, "Error al guardar", f"No se pudo guardar el familiar:\n{e}")

    def _on_delete_familiar(self, fam_id: int):
        if not fam_id:
            return
        try:
            Familiar.get_by_id(fam_id).delete_instance()
            self._reload_familiares()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"No se pudo eliminar: {e}")
