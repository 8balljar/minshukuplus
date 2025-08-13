# controllers/home_controller.py
from typing import Optional, Callable
from PyQt5.QtCore import Qt
from ui.views.homeviews import HomeView
from core.router import AppRouter

class HomeController:
    """Orquesta la navegación: escucha la vista y usa el router para abrir módulos."""
    def __init__(self, view: HomeView, router: AppRouter):
        self.view = view
        self.router = router
        self._connect_signals()

    def _connect_signals(self):
        self.view.hospedado_btn.clicked.connect(self._open_hospedados)
        self.view.casas_btn.clicked.connect(self._open_casas)
        self.view.asignaciones_btn.clicked.connect(self._open_asignaciones)
        self.view.sync_btn.clicked.connect(self._sync)

    # Helpers
    def _before_open(self):
        # Puedes elegir: self.view.hide() o self.view.setEnabled(False)
        self.view.hide()

    def _after_close(self):
        # Reaparece el menú principal al cerrar cualquier módulo
        self.view.showNormal()
        self.view.raise_()
        self.view.activateWindow()

    # Actions
    def _open_hospedados(self):
        self._before_open()
        self.router.open_module("hospedados", on_close=self._after_close, modal=True)

    def _open_casas(self):
        self._before_open()
        self.router.open_module("casas", on_close=self._after_close, modal=True)

    def _open_asignaciones(self):
        # Cuando tengas la vista, solo activa la clave en el router
        self._before_open()
        self.router.open_module("asignaciones", on_close=self._after_close, modal=True)

    def _sync(self):
        # Aquí pondrás la lógica de sincronización (servicio/UseCase)
        # Por ahora, solo reactivamos la vista
        self.view.setEnabled(True)
