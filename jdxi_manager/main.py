import sys
import os
import logging 
from logging.handlers import RotatingFileHandler
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QColor

def setup_logging():
    """Set up logging configuration"""
    try:
        # Create logs directory in user's home directory
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
            maxBytes=1024*1024,  # 1MB per file
            backupCount=5,       # Keep 5 backup files
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Configure console logging
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        logging.root.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)
        
        print("Logging setup complete")
        logging.info("JDXi Manager starting up...")
        logging.debug(f"Log file: {log_file}")
        
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        raise

def main():
    try:
        # Set up logging first
        setup_logging()
        
        # Create application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("JDXi Manager")
        app.setApplicationVersion("0.30")
        app.setOrganizationName("LinuxTECH.NET")
        app.setOrganizationDomain("jdxi-manager.linuxtech.net")
        
        logging.debug("Application initialized")
        
        # Set application icon
        icon_locations = [
            Path(__file__).parent / "assets" / "jdxi_128.png",  # Package location
            Path(__file__).parent.parent / "assets" / "jdxi_128.png",  # Development location
        ]
        
        icon_found = False
        for icon_path in icon_locations:
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                logging.debug(f"Loaded icon from {icon_path}")
                icon_found = True
                break
                
        if not icon_found:
            logging.warning(f"Icon not found in any of: {[str(p) for p in icon_locations]}")
            # Create a fallback icon
            icon = QIcon()
            pixmap = QPixmap(128, 128)
            pixmap.fill(QColor("#2897B7"))  # Use the app's theme color
            icon.addPixmap(pixmap)
            app.setWindowIcon(icon)
            logging.info("Using fallback icon")
        
        # Create and show main window
        from jdxi_manager.ui.main_window import MainWindow
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
        print(f"Application crashed: {str(e)}")  # Fallback if logging fails
        logging.exception("Application crashed")
        sys.exit(1) 