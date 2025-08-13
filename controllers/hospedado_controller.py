# controllers/hospedado_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.hospedados_views import HospedadoView
from ui.views.hospedado_detalle import HospedadoDetalleView
from controllers.hospedado_detalle_controller import HospedadoDetalleController
from core.db import Hospedado
import re

# ---- RUT helpers (acepta con o sin guion) ----
def _normalize_rut(rut: str) -> str:
    r = (rut or "").upper().strip()
    r = r.replace(".", "").replace(" ", "")
    r = r.replace("‐", "-").replace("–", "-").replace("—", "-")
    if "-" not in r:
        # si viene todo junto, último dígito es DV
        if len(r) < 2 or not r[:-1].isdigit():
            return r
        r = f"{r[:-1]}-{r[-1]}"
    return r

def _compute_dv(number: str) -> str:
    seq = [2, 3, 4, 5, 6, 7]
    s = 0
    for i, d in enumerate(reversed(number)):
        s += int(d) * seq[i % len(seq)]
    r = 11 - (s % 11)
    if r == 11: return "0"
    if r == 10: return "K"
    return str(r)

def _is_valid_rut(rut: str) -> bool:
    r = _normalize_rut(rut)
    m = re.match(r"^(\d{7,8})-([0-9K])$", r)
    if not m: return False
    return _compute_dv(m.group(1)) == m.group(2)

def _display(h: Hospedado) -> str:
    return f"{h.rut} - {h.nombre_completo}"

class HospedadoController(QObject):
    def __init__(self, view: HospedadoView):
        super().__init__(view)
        self.view = view
        self._connect()
        self.refresh()

    def _connect(self):
        self.view.refreshRequested.connect(self.refresh)
        self.view.addRequested.connect(self._add)
        self.view.deleteRequested.connect(self._delete)
        self.view.openDetailRequested.connect(self._open_detail)

    # --------- LOAD ---------
    def refresh(self):
        self.view.lista.clear()
        for h in Hospedado.select().order_by(Hospedado.nombre_completo.asc()):
            self.view.add_list_item(_display(h), h.rut)
        self.view._filter_list(self.view.search.text())

    # --------- ADD ---------
    def _add(self):
        try:
            data = self.view.get_form_data()
            nombre = data["nombre"]
            rut_in = _normalize_rut(data["rut"])
            correo = data["correo"]
            telefono_txt = data["telefono"]
            sexo = data["sexo"]
            edad_txt = data["edad"]

            if not nombre or not rut_in or not correo:
                raise ValueError("Nombre, RUT y correo son obligatorios.")
            if not _is_valid_rut(rut_in):
                raise ValueError("RUT no válido. Usa 12345678-9 (con DV correcto).")
            if Hospedado.get_or_none(Hospedado.rut == rut_in):
                raise ValueError("Ya existe un hospedado con ese RUT.")

            tel_digits = re.sub(r"\D", "", telefono_txt or "")
            telefono = tel_digits  # si lo guardas como texto; usa int(...) si es entero en DB

            edad = int(edad_txt) if (edad_txt or "").isdigit() else 0

            Hospedado.create(
                nombre_completo=nombre,
                rut=rut_in,
                correo=correo,
                telefono=telefono,
                sexo=sexo,
                edad=edad
            )
            self.view.clear_inputs()
            self.refresh()
        except ValueError as ve:
            QMessageBox.warning(self.view, "Validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"No se pudo agregar: {e}")

    # --------- DELETE ---------
    def _delete(self):
        rut = self.view.current_selected_rut()
        if not rut:
            return
        try:
            h = Hospedado.get_or_none(Hospedado.rut == rut)
            if h:
                h.delete_instance(recursive=True)
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"No se pudo eliminar: {e}")

    # --------- DETAIL ---------
    def _open_detail(self, rut: str):
        dlg = HospedadoDetalleView(parent=self.view)
        ctrl = HospedadoDetalleController(dlg, rut=rut)
        if dlg.exec_():
            self.refresh()
