# core/router.py
from typing import Callable, Optional
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# ⚠️ Asegúrate que tu archivo se llame ui/views/menu_casa_view.py
# y tu clase Menu_Casa_View esté ahí.
# Si tu archivo sigue siendo "menu_casaviews.py", ajusta el import dentro del builder.

def _wrap_in_dialog(widget: QWidget, parent: Optional[QWidget] = None) -> QDialog:
    dlg = QDialog(parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose, True)
    dlg.setWindowTitle(widget.windowTitle() or "Módulo")
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(widget)
    dlg.resize(1200, 800)
    return dlg

# =========================
# Builders (vista + controller)
# =========================

def _build_casas() -> QWidget:
    from ui.views.menu_casaviews import Menu_Casa_View
    from controllers.menu_casa_controller import MenuCasaController
    w = Menu_Casa_View()
    w._controller = MenuCasaController(w)  # mantener referencia
    return w

def _build_hospedados() -> QWidget:
    """
    Construye el módulo Hospedados. Si ya migraste a MVC, cablea su controller aquí.
    Si aún usas una vista “todo en uno”, simplemente retorna la vista.
    """
    from ui.views.hospedados_views import HospedadoView
    # Si tienes un controller específico, descomenta y úsalo:
    # from controllers.hospedados_controller import HospedadosController
    w = HospedadoView()
    # w._controller = HospedadosController(w)  # si existe
    return w

# def _build_asignaciones() -> QWidget:
#     from ui.views.asignaciones_view import AsignacionesView
#     from controllers.asignaciones_controller import AsignacionesController
#     w = AsignacionesView()
#     w._controller = AsignacionesController(w)
#     return w

class AppRouter:
    """
    Abre módulos como diálogos modales (exec_) para:
    - ocultar temporalmente el menú principal;
    - ejecutar un callback al cierre para restaurar la UI.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        self._open_dialog: Optional[QDialog] = None
        self._parent = parent

        # Fábricas que retornan QWidget YA CABLEADO con su controller
        self._factories: dict[str, Callable[[], QWidget]] = {
            "hospedados": _build_hospedados,
            "casas": _build_casas,
            # "asignaciones": _build_asignaciones,
        }

    def open_module(self, key: str, on_close: Optional[Callable[[], None]] = None, modal: bool = True):
        if key not in self._factories:
            raise KeyError(f"Módulo desconocido: {key}")

        widget = self._factories[key]()  # vista (QWidget) ya cableada a su controller
        dialog = _wrap_in_dialog(widget, self._parent)

        def _finish(_code: int):
            self._open_dialog = None
            if callable(on_close):
                on_close()

        dialog.finished.connect(_finish)
        self._open_dialog = dialog

        if modal:
            dialog.setModal(True)
            dialog.exec_()
        else:
            dialog.show()
