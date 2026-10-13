"""Main Qt window — drag-drop input, style picker, live render preview."""
from __future__ import annotations

from pathlib import Path

from config.settings import Settings


class CartoonizerMainWindow:
    """Thin wrapper so imports succeed without a display.

    The real Qt widget tree is built lazily inside ``_build_widgets`` and only
    when a QApplication exists — keeps headless CI and CLI-only installs happy.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._widget = None

    def _build_widgets(self):  # noqa: ANN202
        from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

        win = QMainWindow()
        win.setWindowTitle(f"{self.settings.app_name} v{self.settings.app_version}")
        win.resize(1180, 760)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Drag an image or video here to cartoonize."))
        win.setCentralWidget(central)
        return win

    def show(self) -> None:
        if self._widget is None:
            self._widget = self._build_widgets()
        self._widget.show()

    def close(self) -> None:
        if self._widget is not None:
            self._widget.close()