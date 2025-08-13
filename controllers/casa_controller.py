# controllers/casa_controller.py
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
from ui.views.casa_views import CasaView
from core.db import Casa, anfitrion
from ui.views.casa_detalle import CasaDetalleView
from controllers.casa_detalle_controller import CasaDetalleController

class CasaController(QObject):
    def __init__(self, view: CasaView):
        super().__init__(view)
        self.view = view
        self._connect_signals()
        # carga inicial
        self._load_hosts()
        self.refresh()

    def _connect_signals(self):
        self.view.refreshRequested.connect(self.refresh)
        self.view.addRequested.connect(self._add_casa)
        self.view.deleteRequested.connect(self._del_casa)
        self.view.openDetailRequested.connect(self._open_detail)

    # --------- DATA ---------
    def _load_hosts(self):
        items = []
        for a in anfitrion.select().order_by(anfitrion.nombre_completo.asc()):
            items.append((a.id, a.nombre_completo))
        self.view.set_hosts(items)

    def refresh(self):
        self.view.lista.clear()
        query = (Casa
                 .select(Casa, anfitrion)
                 .join(anfitrion)
                 .order_by(Casa.id.asc()))
        for c in query:
            self.view.add_list_item(c.id, c.direccion or "", c.anfitrion.nombre_completo or "")
        # re-aplicar filtro si hay búsqueda escrita
        self._apply_current_filter()

    def _apply_current_filter(self):
        self.view._filter_list(self.view.search.text())

    # --------- ACCIONES ---------
    def _add_casa(self):
        try:
            data = self.view.get_form_data()
            direccion = data["direccion"]
            host_id   = data["anfitrion_id"]

            if not direccion:
                raise ValueError("La dirección es obligatoria.")
            if not host_id:
                raise ValueError("Debes seleccionar un anfitrión.")

            host = anfitrion.get_by_id(host_id)
            Casa.create(direccion=direccion, anfitrion=host)
            self.view.clear_form()
            self.refresh()
        except ValueError as ve:
            QMessageBox.warning(self.view, "Validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self.view, "Error al agregar", str(e))

    def _del_casa(self):
        casa_id = self.view.current_selected_id()
        if not casa_id:
            return
        try:
            c = Casa.get_or_none(Casa.id == casa_id)
            if c:
                c.delete_instance(recursive=True)
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self.view, "Error al eliminar", str(e))

    def _open_detail(self, casa_id: int):
        dlg = CasaDetalleView(casa_id=casa_id, parent=self.view)
        _ctrl = CasaDetalleController(dlg, casa_id=casa_id)
        if dlg.exec_():   # el controller hace accept() tras guardar
            self.refresh()

