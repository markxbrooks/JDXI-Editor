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
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox, QSplashScreen, QFrame,
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


def main() -> None:
    """Main entry point for the JD-Xi Editor application."""
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

        setup_splash_screen(app)

        # Start event loop
        return app.exec()

    except Exception as ex:
        logging.exception(f"Fatal error {ex} occurred")
        raise


def setup_splash_screen(app: QApplication) -> None:
    """Setup and display a professional application splash screen with rotating status text."""
    splash = QSplashScreen()
    splash.setWindowFlags(
        Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    )
    splash.setFixedSize(720, 480)

    splash.setStyleSheet("""
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
    """)

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
    title = QLabel(__program__)
    title.setObjectName("TitleLabel")
    title.setAlignment(Qt.AlignCenter)
    card_layout.addWidget(title)

    # Image
    image_path = resource_path(os.path.join("resources", "jdxi_cartoon_600.png"))
    pixmap = QPixmap(image_path).scaled(360, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    logo = QLabel()
    logo.setPixmap(pixmap)
    logo.setAlignment(Qt.AlignCenter)
    card_layout.addWidget(logo)

    # Subtitle
    subtitle = QLabel("An editor & toolkit for the Roland JD-Xi instrument")
    subtitle.setObjectName("SubtitleLabel")
    subtitle.setAlignment(Qt.AlignCenter)
    card_layout.addWidget(subtitle)

    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setFixedWidth(420)
    progress_bar.setStyleSheet(JDXiStyle.PROGRESS_BAR)
    progress_row = QHBoxLayout()
    progress_row.addStretch()
    progress_row.addWidget(progress_bar)
    progress_row.addStretch()
    card_layout.addLayout(progress_row)

    # Rotating status label
    status_label = QLabel("Starting...")
    status_label.setObjectName("StatusLabel")
    status_label.setAlignment(Qt.AlignCenter)
    card_layout.addWidget(status_label)

    # Footer credits
    credits = QLabel(
        f"{__program__}  •  Version {__version__}\n"
        "Developed by Mark Brooks — Inspired by modern instrument editors"
    )
    credits.setObjectName("CreditLabel")
    credits.setAlignment(Qt.AlignCenter)

    root.addWidget(card)
    root.addWidget(credits)

    splash.show()
    splash.raise_()
    splash.activateWindow()

    # Rotating messages
    messages = [
        "Initializing MIDI subsystem…",
        "Loading instrument presets…",
        "Connecting to synthesizer…",
        "Preparing editor interface…",
        "Finalizing setup…",
    ]
    number_range = 101
    number_messages = len(messages)
    import time
    for i in range(number_range + 1):
        progress_bar.setValue(i)

        # Determine which message to show based on progress
        segment_length = number_range // number_messages
        message_no = min(i // segment_length, number_messages - 1)
        status_label.setText(messages[message_no])

        app.processEvents()
        time.sleep(0.03)

    splash.close()
    window = JDXiInstrument()
    window.show()
    splash.finish(window)


def setup_splash_screen_new(app: QApplication) -> None:
    """Setup and display the application splash screen."""
    splash = QSplashScreen()
    splash.setWindowFlags(
        Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    )
    splash.setFixedSize(700, 500)
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


def setup_splash_screen_old(app: QApplication) -> None:
    """Setup and display the application splash screen."""
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
