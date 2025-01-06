import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.ui.main_window import MainWindow

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("JDXi Manager")
    app.setApplicationVersion("0.30")
    app.setOrganizationName("LinuxTECH.NET")
    app.setOrganizationDomain("jdxi-manager.linuxtech.net")
    
    # Load application icon
    icon_path = Path(__file__).parent.parent / "assets" / "jdxi_128.png"
    app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 