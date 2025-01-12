import sys
import os
import logging 
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

def setup_logging() -> str:
    """Set up logging configuration"""
    # Create logs directory in user's home directory
    log_dir = Path.home() / ".jdxi_manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = log_dir / "jdxi_manager.log"
    
    # Reset root handlers
    logging.root.handlers = []
    
    # Configure file logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Less verbose for console
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    logging.root.setLevel(logging.DEBUG)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)
    
    # Log startup message
    logging.info("JDXi Manager starting up...")
    logging.debug(f"Log file: {log_file}")
    return log_file


def main():
    # Set up logging first
    self.log_file = setup_logging()
    print("setting up logging")
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("JDXi Manager")
    app.setApplicationVersion("0.30")
    app.setOrganizationName("LinuxTECH.NET")
    app.setOrganizationDomain("jdxi-manager.linuxtech.net")
    
    logging.debug("Application initialized")
    
    # Load application icon
    icon_path = Path(__file__).parent.parent / "assets" / "jdxi_128.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        logging.debug(f"Loaded icon from {icon_path}")
    else:
        logging.warning(f"Icon not found at {icon_path}")
    
    try:
        # Create and show main window
        from .ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        logging.info("Main window displayed")
        
        # Start event loop
        return app.exec()
        
    except Exception as e:
        logging.exception("Fatal error occurred")
        raise


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.exception("Application crashed")
        sys.exit(1) 