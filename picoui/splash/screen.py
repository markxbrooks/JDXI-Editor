"""
JDXI-inspired spec-driven splash screen widget.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QProgressBar, QVBoxLayout, QWidget

from picoui.splash.config import SplashScreenConfig
from picoui.splash.panel import build_splash_panel
from picoui.splash.styles import (
    SPLASH_STYLESHEET,
    SPLASH_CONTENT_MARGINS,
    SPLASH_CONTENT_SPACING,
    SPLASH_TITLE_GEOMETRY,
)


class SplashScreen(QWidget):
    """Splash screen with a JDXI-style card layout."""

    def __init__(self, config: SplashScreenConfig):
        super().__init__()
        self.config = config
        self.progress_bar: QProgressBar | None = None
        self.status_label = None
        self.title_label = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("SplashRoot")
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(*self.config.dimensions.to_tuple())
        self.setStyleSheet(SPLASH_STYLESHEET)

        root = QVBoxLayout(self)
        root.setContentsMargins(*SPLASH_CONTENT_MARGINS)
        root.setSpacing(SPLASH_CONTENT_SPACING)

        panel = build_splash_panel(self, self.config)
        self.progress_bar = panel.progress_bar
        self.status_label = panel.status_label
        self.title_label = panel.title_label
        root.addWidget(panel.card)

        self.title_label.setGeometry(*SPLASH_TITLE_GEOMETRY)
        self.title_label.raise_()
