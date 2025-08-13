# controllers/anfitrion_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.anfitrion_views import AnfitrionViews
from core.db import Anfitrion
import re

class AnfitrionController(QObject):
    def __init__(self, view: AnfitrionViews):
        super().__init__(view)
        self.view = view
        self._connect()
        self.refresh()

    def _connect(self):
        v = self.view
        v.refreshRequested.connect(self.refresh)
        v.addRequested.connect(self._add)
        v.deleteRequested.connect(self._delete)
        v.openDetailRequested.connect(self._open_detail)

    # -------- helpers --------
    def _normalize_rut(self, rut: str) -> str:
        r = (rut or "").upper().strip().replace(".", "").replace(" ", "")
        if "-" not in r and len(r) >= 2:
            r = f"{r[:-1]}-{r[-1]}"
        return r

    def _display(self, a: Anfitrion) -> str:
        if hasattr(a, "estado_civil"):
            casado = "Sí" if (a.estado_civil or "").lower() == "casado" else "No"
        else:
            casado = "Sí" if getattr(a, "casado", False) else "No"
        return f"{a.rut} - {a.nombre_completo} (Casado: {casado})"

    # -------- actions --------
    def refresh(self):
        self.view.clear_list()
        for a in Anfitrion.select().order_by(Anfitrion.nombre_completo.asc()):
            self.view.add_list_item(self._display(a), a.rut)
        self.view._filter_list(self.view.search.text())

    def _add(self):
        try:
            data = self.view.get_form_data()
            nombre = data["nombre"]
            rut    = self._normalize_rut(data["rut"])
            correo = data["correo"] or None
            sexo   = data["sexo"]
            casado = data["casado"]

            if not nombre or not rut:
                raise ValueError("Nombre y RUT son obligatorios.")
            if Anfitrion.get_or_none(Anfitrion.rut == rut):
                raise ValueError("Ya existe un anfitrión con ese RUT.")

            tel_digits = re.sub(r"\D", "", data["telefono"] or "")
            telefono = tel_digits or None

            a = Anfitrion.create(
                nombre_completo=nombre,
                rut=rut,
                telefono=telefono,
                correo=correo,
                sexo=sexo,
            )
            if hasattr(a, "estado_civil"):
                a.estado_civil = "Casado" if casado else "Soltero"
                a.save()
            elif hasattr(a, "casado"):
                a.casado = bool(casado)
                a.save()

            self.view.clear_inputs()
            self.refresh()
        except ValueError as ve:
            QMessageBox.warning(self.view, "Validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"No se pudo agregar: {e}")

    def _delete(self):
        rut = self.view.current_selected_rut()
        if not rut:
            return
        try:
            a = Anfitrion.get_or_none(Anfitrion.rut == rut)
            if a:
                a.delete_instance(recursive=True)
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"No se pudo eliminar: {e}")

    def _open_detail(self, rut: str):
        from ui.views.anfitrion_detalle import AnfitrionDetalle
        dlg = AnfitrionDetalle(rut=rut, parent=self.view)
        if dlg.exec_():
            self.refresh()
