"""
Main entry point for the JD-Xi Editor application.

This module sets up the application environment, including logging, MIDI message listening,
and application window initialization. It also manages the application's lifecycle,
from initialization to event loop execution.

Functions:
    midi_callback(msg): Callback function for handling incoming MIDI messages.

    listen_midi(port_name, callback): Listens for MIDI messages on the specified port
    and triggers the provided callback function.

    setup_logging(): Configures logging for the application, including console and file
     logging with rotation.

    main(): Main entry point to initialize and run the JD-Xi Editor application,
    set up the window, and handle MIDI message listening.

"""

import cProfile
import io
import logging
import os
import platform
import pstats
import sys
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor, QIcon, QPixmap, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSplashScreen,
    QVBoxLayout,
)

from decologr import setup_logging
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.message import log_message
from jdxi_editor.project import __organization_name__, __program__, __version__
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.editor.helper import create_hlayout_with_widgets, create_icon_label_with_pixmap
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"


def main() -> None:
    """Main entry point for the JD-Xi Editor application."""
    try:
        # Set up logging first
        settings = QSettings(__organization_name__, __program__)
        log_level = int(str(settings.value("log_level", logging.DEBUG)))
        logger = setup_logging(use_rich=True, project_name="jdxi_editor")

        # Create application
        app = QApplication(sys.argv)

        # Set application metadata
        app.setApplicationName(__program__)
        app.setApplicationVersion(__version__)
        app.setOrganizationName("mabsoft")
        app.setOrganizationDomain("com.mabsoft")
        app.setStyleSheet(
            """
            QLabel {
                color: red;
                font-weight: bold;
            }
        """
        )

        logger.debug("Application initialized")

        # Set application icon
        icon_locations = [
            Path(__file__).parent / "resources" / "jdxi_icon.png",  # Package location
            Path(__file__).parent.parent
            / "resources"
            / "jdxi_icon.png",  # Development location
        ]

        icon_found = False
        for icon_path in icon_locations:
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                log_message(f"Loaded icon from {icon_path}")
                icon_found = True
                break

        if not icon_found:
            logging.warning(
                f"Icon not found in any of: {[str(p) for p in icon_locations]}"
            )
            # Create address fallback icon only for windows, not macOS
            if platform.system() == "Windows":
                icon = QIcon()
                pixmap = QPixmap(128, 128)
                pixmap.fill(QColor("#2897B7"))  # Use the app's theme color
                icon.addPixmap(pixmap)
                app.setWindowIcon(icon)
                log_message("Using fallback icon")

        splash, progress_bar, status_label = setup_splash_screen(app)

        # Update splash screen with initial progress
        status_label.setText("Initializing MIDI subsystem…")
        progress_bar.setValue(10)
        app.processEvents()

        # Create window and pass splash screen components
        window = JDXiInstrument(
            splash=splash, progress_bar=progress_bar, status_label=status_label
        )

        # Finalize splash screen
        splash.finish(window)
        window.show()

        # Start event loop
        return app.exec()

    except Exception as ex:
        logging.exception(f"Fatal error {ex} occurred")
        raise


def setup_splash_screen(
    app: QApplication,
) -> tuple[QSplashScreen, QProgressBar, DigitalTitle]:
    """Setup and display a professional application splash screen with rotating status text.

    Returns:
        tuple: (splash_screen, progress_bar, status_label) for updating progress
    """
    splash = QSplashScreen()
    # Need to use the screen center to display the splash screen
    # In Qt 6, QApplication.desktop() was removed, use QScreen instead
    screen = app.primaryScreen()
    if screen:
        screen_geometry = screen.availableGeometry()
        screen_center = screen_geometry.center()
        splash.move(
            int(screen_center.x() - JDXiDimensions.SPLASH_WIDTH / 2),
            int(screen_center.y() - JDXiDimensions.SPLASH_HEIGHT / 2),
        )
    splash.setWindowFlags(
        Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    )
    splash.setFixedSize(JDXiDimensions.SPLASH_WIDTH, JDXiDimensions.SPLASH_HEIGHT)

    splash.setStyleSheet(
        """
        QSplashScreen { background-color: #111111; border: 1px solid #2c2c2c; }
        QLabel#TitleLabel { color: #f3f3f3; font-size: 28px; font-weight: 600; letter-spacing: 1px; }
        QLabel#SubtitleLabel { color: #bbbbbb; font-size: 14px; }
        QLabel#StatusLabel { color: #88ccff; font-size: 12px; font-style: italic; }
        QLabel#CreditLabel { color: #888888; font-size: 12px; }
        QFrame#Card { 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1c1c1c, stop:1 #0f0f0f);
            border-radius: 14px; border: 1px solid #2a2a2a; 
        }
        QProgressBar { 
            background: #2a2a2a; border-radius: 6px; height: 14px; text-align: center; color: #cccccc; font-size: 10px;
        }
        QProgressBar::chunk {
            border-radius: 6px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7ac1ff, stop:1 #3b8fe8);
        }
    """
    )

    root = QVBoxLayout(splash)
    root.setContentsMargins(28, 28, 28, 28)
    root.setSpacing(16)

    # --- Card container ---
    card = QFrame()
    card.setObjectName("Card")
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(32, 32, 32, 32)
    card_layout.setSpacing(18)

    # Title
    title = DigitalTitle(
        __program__,
        digital_font_family=JDXiStyle.FONT_FAMILY_MONOSPACE,
        show_upper_text=False,
    )
    card_layout.addWidget(title)
    title.setStyleSheet(JDXiStyle.INSTRUMENT_TITLE_LABEL)

    # Image
    image_path = resource_path(os.path.join("resources", "jdxi_cartoon_600.png"))
    pixmap = QPixmap(image_path).scaled(
        360, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation
    )
    logo = create_icon_label_with_pixmap(pixmap)
    card_layout.addWidget(logo)

    # Subtitle
    subtitle = QLabel("An editor & toolkit for the Roland JD-Xi instrument")
    card_layout.addWidget(subtitle)
    subtitle.setStyleSheet(JDXiStyle.INSTRUMENT_SUBTITLE_LABEL)

    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setFixedWidth(420)
    progress_bar.setStyleSheet(JDXiStyle.PROGRESS_BAR)
    progress_row = create_hlayout_with_widgets([progress_bar])
    card_layout.addLayout(progress_row)

    # Rotating status label
    status_label = DigitalTitle(
        "Starting...", digital_font_family=JDXiStyle.FONT_FAMILY_MONOSPACE
    )
    status_label.setStyleSheet(JDXiStyle.INSTRUMENT_SUBTITLE_LABEL)
    card_layout.addWidget(status_label)

    # Footer credits
    credits = QLabel(
        f"{__program__}  •  Version {__version__}\n"
        "Developed by mabsoft.com — Inspired by modern instrument editors"
    )
    credits.setObjectName("CreditLabel")
    credits.setAlignment(Qt.AlignCenter)

    root.addWidget(card)
    root.addWidget(credits)

    splash.show()
    splash.raise_()
    splash.activateWindow()

    # Return splash screen components for updating progress
    return splash, progress_bar, status_label


if __name__ == "__main__":
    try:
        profiling = False

        if profiling:
            profiler = cProfile.Profile()
            profiler.enable()

        exit_code = main()

        if profiling:
            profiler.disable()
            s = io.StringIO()
            sortby = "cumtime"  # or 'tottime'
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats(50)  # Top 50 entries
            print(s.getvalue())

        sys.exit(exit_code)

    except Exception as ex:
        print(f"Application crashed: {str(ex)}")  # Fallback if logging fails
        logging.exception("Application crashed")
        sys.exit(1)
