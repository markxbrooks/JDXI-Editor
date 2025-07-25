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


import os
import platform
import sys
import logging
from pathlib import Path
import cProfile
import pstats
import io

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QApplication,
    QProgressBar,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox, QSplashScreen,
)
from PySide6.QtGui import QIcon, QPixmap, QColor, Qt, QFont, QFontInfo

from jdxi_editor.log.message import log_message
from jdxi_editor.log.setup import setup_logging
from jdxi_editor.project import __program__, __version__
from jdxi_editor.resources import resource_path
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument
from jdxi_editor.project import __version__, __program__, __organization_name__

os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"


def main():
    try:
        # Set up logging first
        settings = QSettings(__organization_name__, __program__)
        log_level = settings.value("log_level", logging.DEBUG)
        logger = setup_logging(log_level=log_level)

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

        splash = QSplashScreen()
        splash.setWindowFlags(
            Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        splash.setFixedSize(500, 400)
        splash.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(splash)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Title
        group_box = QGroupBox(__program__)
        group_box.setAlignment(Qt.AlignHCenter)
        group_box.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        preferred_fonts = ["Myriad Pro", "Segoe UI", "Arial"]
        if platform.system() == "Windows":
            font_size = 18
        else:
            font_size = 20
        for font_name in preferred_fonts:
            font = QFont(font_name, font_size)
            font.setBold(True)
            if QFontInfo(font).family() == font_name:
                group_box.setFont(font)
                break
        layout.addWidget(group_box)

        group_layout = QVBoxLayout()
        group_layout.setAlignment(Qt.AlignCenter)
        group_box.setLayout(group_layout)

        # Image
        image_path = resource_path(os.path.join("resources", "jdxi_cartoon_600.png"))
        pixmap = QPixmap(image_path).scaled(
            250, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(image_label)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setFixedHeight(30)
        progress_bar.setFixedWidth(400)
        progress_bar.setAlignment(Qt.AlignCenter)
        progress_bar.setStyleSheet(JDXiStyle.PROGRESS_BAR)
        group_box.setStyleSheet(JDXiStyle.SPLASH_SCREEN)
        progress_container = QHBoxLayout()
        progress_container.addStretch()
        progress_container.addWidget(progress_bar)
        progress_container.addStretch()
        group_layout.addLayout(progress_container)
        from jdxi_editor.ui.widgets.display.digital import DigitalTitle

        sub_text_label = DigitalTitle(
            "An editor & toolkit for the Roland JD-Xi instrument", show_upper_text=False
        )
        sub_text_label.setMinimumHeight(80)
        sub_text_label.setFixedSize(475, 80)
        group_layout.addWidget(sub_text_label)

        splash.show()
        splash.raise_()  # Ensure the splash screen is raised
        splash.activateWindow()  # Activate the splash screen window
        import time

        for i in range(101):
            progress_bar.setValue(i)
            app.processEvents()
            time.sleep(0.03)

        splash.close()

        window = JDXiInstrument()
        window.show()
        splash.finish(window)

        # Start event loop
        return app.exec()

    except Exception as ex:
        logging.exception(f"Fatal error {ex} occurred")
        raise


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
            sortby = 'cumtime'  # or 'tottime'
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats(50)  # Top 50 entries
            print(s.getvalue())

        sys.exit(exit_code)

    except Exception as ex:
        print(f"Application crashed: {str(ex)}")  # Fallback if logging fails
        logging.exception("Application crashed")
        sys.exit(1)

