"""
Splash screen setup and progress animation helpers.
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from picoui.splash.config import SplashScreenConfig
from picoui.splash.screen import SplashScreen

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def create_splash_screen(config: SplashScreenConfig) -> SplashScreen:
    """Create a splash screen widget from *config*."""
    return SplashScreen(config)


def center_splash_on_screen(splash: SplashScreen, app: QApplication) -> None:
    """Center *splash* on the primary screen (Qt 6 / QScreen)."""
    screen = app.primaryScreen()
    if screen is None:
        return
    geometry = screen.availableGeometry()
    center = geometry.center()
    splash.move(
        int(center.x() - splash.width() / 2),
        int(center.y() - splash.height() / 2),
    )


def animate_splash_progress(
    splash: SplashScreen,
    app: QApplication,
    *,
    steps: int = 101,
    delay: float = 0.03,
) -> None:
    """Animate the splash progress bar from 0 to 100."""
    if splash.progress_bar is None:
        return
    for value in range(steps):
        splash.progress_bar.setValue(value)
        app.processEvents()
        time.sleep(delay)


def setup_splash_screen(app: QApplication, config: SplashScreenConfig) -> None:
    """Set up, center, animate, and close a JDXI-style splash screen."""
    splash = create_splash_screen(config)
    center_splash_on_screen(splash, app)
    splash.show()
    splash.raise_()
    splash.activateWindow()
    animate_splash_progress(splash, app)
    splash.close()
