# controllers/menu_casa_controller.py
from PyQt5.QtCore import QObject

# OJO con el nombre del archivo de la vista:
# si tu archivo es ui/views/menu_casa_view.py usa esta import;
# si aún lo tienes como menu_casaviews.py, cambia la import de abajo.
from ui.views.menu_casaviews import Menu_Casa_View

from controllers.casa_controller import CasaController
from controllers.anfitrion_controller import AnfitrionController


class MenuCasaController(QObject):
    """
    Orquesta la vista de pestañas (Anfitriones / Casas).
    - Cablea los sub-controladores correctos.
    - Refresca la pestaña activa al cambiar.
    """
    def __init__(self, view: Menu_Casa_View):
        super().__init__(view)
        self.view = view

        # Subcontroladores: ¡guarda referencias para que no los recoja el GC!
        self.anfitrion_controller = AnfitrionController(self.view.anfitrion_tab)
        self.casa_controller = CasaController(self.view.casa_tab)

        # Señales de la vista principal
        self.view.tabs.currentChanged.connect(self._on_tab_changed)

        # Refresco inicial
        self._safe_refresh_current()

    def _on_tab_changed(self, _index: int):
        self._safe_refresh_current()

    def _safe_refresh_current(self):
        """Refresca usando el SUB-CONTROLLER adecuado (no la vista)."""
        current = self.view.tabs.currentWidget()

        if current is self.view.anfitrion_tab:
            # Anfitriones
            if hasattr(self.anfitrion_controller, "refresh"):
                self.anfitrion_controller.refresh()
            else:
                # Fallback (por si cambias nombres en el futuro)
                self._call_if_exists(current, ("refresh", "load_data", "reload"))

        elif current is self.view.casa_tab:
            # Casas
            if hasattr(self.casa_controller, "refresh"):
                self.casa_controller.refresh()
            else:
                self._call_if_exists(current, ("refresh", "load_data", "reload", "load_casas"))

    # Helpers opcionales para refrescar explícitamente cada pestaña
    def _refresh_anfitriones_if_needed(self):
        if hasattr(self.anfitrion_controller, "refresh"):
            self.anfitrion_controller.refresh()
        else:
            self._call_if_exists(self.view.anfitrion_tab, ("refresh", "load_data", "reload"))

    def _refresh_casas_if_needed(self):
        if hasattr(self.casa_controller, "refresh"):
            self.casa_controller.refresh()
        else:
            self._call_if_exists(self.view.casa_tab, ("refresh", "load_data", "reload", "load_casas"))

    @staticmethod
    def _call_if_exists(target, names: tuple[str, ...]):
        for name in names:
            fn = getattr(target, name, None)
            if callable(fn):
                fn()
                break
