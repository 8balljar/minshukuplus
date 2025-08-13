# controllers/casa_detalle_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.casa_detalle import CasaDetalleView
from ui.views.habitacion_detalle import HabitacionDetalle
from ui.views.bano_detalle import BanoDetalle
from core.db import Casa, anfitrion, Habitacion, Cama, Bano
from ui.views.bano_detalle import BanoDetalleView
from controllers.bano_detalle_controller import BanoDetalleController
from ui.views.habitacion_detalle import HospedadoDetalle
from controllers.habitacion_detalle_controller import HabitacionDetalleController

import re


class CasaDetalleController(QObject):
    """
    Orquesta el diálogo de detalle de casa:
    - Carga anfitriones
    - Carga/crea casa, habitaciones y baños
    - Maneja edición, guardado, cancelación
    """
    def __init__(self, view: CasaDetalleView, casa_id=None):
        super().__init__(view)
        self.view = view
        self.casa_id = casa_id
        self.model = None
        # Estado editable (se mantiene aquí, no en la vista)
        self.habs_data = []   # [{'capacidad':int,'camas':[str,...]}]
        self.banos_data = []  # [{'ubicacion':str,'tina':bool}]
        self._snapshot = None

        self._connect()
        self._load_hosts()
        self._load_or_init_model()
        self._populate_view()
        self.view.set_edit_mode(False)

    # -------- wiring --------
    def _connect(self):
        v = self.view
        v.editRequested.connect(lambda: v.set_edit_mode(True))
        v.saveRequested.connect(self._on_save)
        v.cancelRequested.connect(self._on_cancel)
        v.closeRequested.connect(v.reject)

        v.addHabitacionRequested.connect(self._on_add_hab)
        v.editHabitacionRequested.connect(self._on_edit_hab)
        v.deleteHabitacionRequested.connect(self._on_del_hab)

        v.addBanoRequested.connect(self._on_add_bano)
        v.editBanoRequested.connect(self._on_edit_bano)
        v.deleteBanoRequested.connect(self._on_del_bano)

    # -------- data load --------
    def _load_hosts(self):
        items = [(a.id, a.nombre_completo) for a in anfitrion.select().order_by(anfitrion.nombre_completo.asc())]
        self.view.set_hosts(items)

    def _load_or_init_model(self):
        if self.casa_id:
            self.model = Casa.get_or_none(Casa.id == self.casa_id)
            if not self.model:
                QMessageBox.critical(self.view, "Error", f"No existe casa con id {self.casa_id}")
                self.view.reject()
                return
            # cargar habitaciones
            self.habs_data = []
            for h in Habitacion.select().where(Habitacion.casa == self.model):
                camas = [cam.tipo for cam in Cama.select().where(Cama.habitacion == h)]
                self.habs_data.append({"capacidad": int(h.capacidad or 0), "camas": camas})
            # cargar baños
            self.banos_data = []
            for b in Bano.select().where(Bano.casa == self.model):
                self.banos_data.append({"ubicacion": b.ubicacion or "", "tina": bool(b.tiene_tina)})
        else:
            # nuevo
            self.model = None
            self.habs_data = []
            self.banos_data = []

    def _populate_view(self):
        direccion = self.model.direccion if self.model else ""
        anfitrion_id = self.model.anfitrion.id if self.model else None
        self.view.set_form_data(direccion, anfitrion_id if anfitrion_id else (self.view.anfitrion_combo.currentData() or None))
        self.view.set_habitaciones(self.habs_data)
        self.view.set_banos(self.banos_data)

        self._snapshot = {
            "direccion": direccion,
            "anfitrion_id": anfitrion_id,
            "habs": [dict(capacidad=h["capacidad"], camas=list(h.get("camas", []))) for h in self.habs_data],
            "banos": [dict(ubicacion=b["ubicacion"], tina=bool(b["tina"])) for b in self.banos_data],
        }

    # -------- handlers (habitaciones/baños) --------
    def _on_add_hab(self):
        dlg = HabitacionDetalle(parent=self.view)
        ctrl = HabitacionDetalleController(dlg)
        if dlg.exec_():
            self.habs_data.append(ctrl.get_data())
            self.view.set_habitaciones(self.habs_data)

    def _on_edit_hab(self, idx: int):
        if idx is None or idx < 0 or idx >= len(self.habs_data):
            return
        dlg = HabitacionDetalle(parent=self.view)
        ctrl = HabitacionDetalleController(dlg, data=self.habs_data[idx])
        if dlg.exec_():
            self.habs_data[idx] = ctrl.get_data()
            self.view.set_habitaciones(self.habs_data)


    def _on_del_hab(self, idx: int):
        if idx is None or idx < 0 or idx >= len(self.habs_data):
            return
        del self.habs_data[idx]
        self.view.set_habitaciones(self.habs_data)

    def _on_add_bano(self):
        dlg = BanoDetalleView(parent=self.view)
        ctrl = BanoDetalleController(dlg)
        if dlg.exec_():
            self.banos_data.append(ctrl.get_data())
            self.view.set_banos(self.banos_data)

    def _on_edit_bano(self, idx: int):
        if idx is None or idx < 0 or idx >= len(self.banos_data):
            return
        dlg = BanoDetalleView(parent=self.view)
        ctrl = BanoDetalleController(dlg, data=self.banos_data[idx])
        if dlg.exec_():
            self.banos_data[idx] = ctrl.get_data()
            self.view.set_banos(self.banos_data)

    def _on_del_bano(self, idx: int):
        if idx is None or idx < 0 or idx >= len(self.banos_data):
            return
        del self.banos_data[idx]
        self.view.set_banos(self.banos_data)

    # -------- save / cancel --------
    def _on_save(self):
        try:
            form = self.view.get_form_data()
            direccion = form["direccion"]
            anfitrion_id = form["anfitrion_id"]

            if not direccion:
                raise ValueError("La dirección es obligatoria.")
            if not anfitrion_id:
                raise ValueError("Debes seleccionar un anfitrión.")

            host = anfitrion.get_by_id(anfitrion_id)

            # Crear/actualizar casa
            if self.model:
                c = self.model
                c.direccion = direccion
                c.anfitrion = host
                c.save()
                # resetear detalles previos
                for h in Habitacion.select().where(Habitacion.casa == c):
                    h.delete_instance(recursive=True)
                for b in Bano.select().where(Bano.casa == c):
                    b.delete_instance()
            else:
                c = Casa.create(direccion=direccion, anfitrion=host)
                self.model = c
                self.casa_id = c.id

            # Guardar habitaciones/camas
            for hdata in self.habs_data:
                h = Habitacion.create(casa=self.model, capacidad=int(hdata.get("capacidad", 0) or 0))
                for tipo in hdata.get("camas", []):
                    Cama.create(habitacion=h, tipo=tipo)

            # Guardar baños
            for bdata in self.banos_data:
                Bano.create(
                    casa=self.model,
                    ubicacion=bdata.get("ubicacion", ""),
                    tiene_tina=bool(bdata.get("tina", False))
                )

            QMessageBox.information(self.view, "Guardado", "Cambios guardados.")
            self.view.set_edit_mode(False)
            # propagamos "ok" al caller (CasaController) para refrescar
            self.view.accept()

        except ValueError as ve:
            QMessageBox.warning(self.view, "Validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", str(e))

    def _on_cancel(self):
        if not self._snapshot:
            self.view.set_edit_mode(False)
            return
        self.view.set_form_data(self._snapshot["direccion"], self._snapshot["anfitrion_id"])
        self.habs_data = [dict(capacidad=h["capacidad"], camas=list(h["camas"])) for h in self._snapshot["habs"]]
        self.banos_data = [dict(ubicacion=b["ubicacion"], tina=bool(b["tina"])) for b in self._snapshot["banos"]]
        self.view.set_habitaciones(self.habs_data)
        self.view.set_banos(self.banos_data)
        self.view.set_edit_mode(False)
