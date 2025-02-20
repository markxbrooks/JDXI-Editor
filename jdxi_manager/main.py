"""
main entry point of jdxi_manager
"""

import os
import sys
import logging
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
import mido
from pubsub import pub
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QColor

from jdxi_manager.ui.main_window import MainWindow

os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"


def midi_callback(msg):
    """
    Your custom callback function to handle MIDI messages.
    """
    # logging.debug(f"Callback received message: {msg}")
    pub.sendMessage(
        "midi_incoming_message", message=msg
    )  # Publish the message to subscribers


def listen_midi(port_name, callback):
    """
    Function to listen for MIDI messages and call a callback.
    """
    with mido.open_input(port_name) as inport:
        logging.info(f"Listening on port: {port_name}")
        for msg in inport:
            callback(msg)  # Call the provided callback function


def setup_logging():
    """Set up logging configuration"""
    try:
        # Create logs directory in user's home directory
        _ = logging.getLogger("jdxi_manager")
        log_dir = Path.home() / ".jdxi_manager" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log file path
        log_file = log_dir / "jdxi_manager.log"
        print(f"Setting up logging to: {log_file}")

        # Reset root handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configure rotating file logging
        file_handler = RotatingFileHandler(
            str(log_file),
            maxBytes=1024 * 1024,  # 1MB per file
            backupCount=5,  # Keep 5 backup files
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s|%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        # Configure console logging
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(filename)-20s| %(lineno)-5s| %(levelname)-8s| %(message)-24s"
        )
        console_handler.setFormatter(console_formatter)

        # Configure root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)

        logging.info("Logging setup complete")
        logging.info("JDXi Manager starting up...")
        logging.debug(f"Log file: {log_file}")
        return log_file

    except Exception as ex:
        print(f"Error setting up logging: {str(ex)}")
        raise


def main():
    try:
        # Set up logging first
        log_file = setup_logging()

        # Create application
        app = QApplication(sys.argv)

        # Set application metadata
        app.setApplicationName("JD-Xi Manager")
        app.setApplicationVersion("0.30")
        app.setOrganizationName("jdximanager")
        app.setOrganizationDomain("com.mabinc")

        logging.debug("Application initialized")

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
                logging.debug(f"Loaded icon from {icon_path}")
                icon_found = True
                break

        if not icon_found:
            logging.warning(
                f"Icon not found in any of: {[str(p) for p in icon_locations]}"
            )
            # Create a fallback icon
            icon = QIcon()
            pixmap = QPixmap(128, 128)
            pixmap.fill(QColor("#2897B7"))  # Use the app's theme color
            icon.addPixmap(pixmap)
            app.setWindowIcon(icon)
            logging.info("Using fallback icon")

        window = MainWindow()
        window.show()
        logging.info("Main window displayed")
        window.set_log_file(log_file)
        # Start event loop
        return app.exec()

    except Exception as ex:
        logging.exception(f"Fatal error {ex} occurred")
        raise


if __name__ == "__main__":
    # List available MIDI input ports
    input_ports = mido.get_input_names()
    if not input_ports:
        print("No MIDI input ports available!")
        # exit()

    print("Available MIDI input ports:")
    for i, port in enumerate(input_ports):
        print(f"{i}: {port}")

    # Choose the first available port
    try:
        port_name = input_ports[0]
        print(f"Using port: {port_name}")

        # Start the listener in a separate thread
        listener_thread = threading.Thread(
            target=listen_midi, args=(port_name, midi_callback), daemon=True
        )
        listener_thread.start()
    except Exception as ex:
        print(f"Error starting listener thread: {str(ex)}")
    try:
        sys.exit(main())
    except Exception as ex:
        print(f"Application crashed: {str(ex)}")  # Fallback if logging fails
        logging.exception("Application crashed")
        sys.exit(1)
