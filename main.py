# main.py
import sys
from PyQt5.QtWidgets import QApplication

def main():
    # 1) Inicializa la base de datos (crea archivo y tablas si no existen)
    from core.db import init_db, close_db, DB_PATH
    try:
        init_db(create_tables=True)
        print(f"[DB] Lista en: {DB_PATH}")
    except Exception as e:
        print(f"[DB] Error al inicializar: {e}")

    # 2) Crea la app de Qt
    app = QApplication(sys.argv)

    # 3) Importa vistas/controladores DESPUÉS de init_db
    from ui.views.homeviews import HomeView
    from controllers.home_controller import HomeController
    from core.router import AppRouter

    view = HomeView()
    view.showMaximized()

    router = AppRouter(parent=view)
    controller = HomeController(view, router)

    # 4) Ejecuta y cierra DB al salir
    exit_code = app.exec_()
    close_db()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
