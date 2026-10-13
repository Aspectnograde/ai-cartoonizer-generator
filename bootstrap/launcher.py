"""PySide6 GUI launcher for the cartoonizer desktop app."""
from __future__ import annotations

import sys

from config.settings import load_settings
from utils.logging_setup import configure_logging


def run_gui() -> int:
    settings = load_settings()
    configure_logging(settings.logging_config)

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is required for the GUI. Install with: pip install PySide6", file=sys.stderr)
        return 1

    from services.ui.main_window import CartoonizerMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    app.setApplicationVersion(settings.app_version)

    window = CartoonizerMainWindow(settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_gui())