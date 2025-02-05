import logging
import sys
from pathlib import Path

import mido
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QApplication,
    QHBoxLayout,
)
from PySide6.QtGui import QPixmap, QPainter, QImage, QColor, QFont, QPen, QIcon
from PySide6.QtCore import Qt

from jdxi_manager.main import setup_logging


def get_button_styles(active):
    """Returns the appropriate style for active/inactive states"""
    if active:
        return """
            QPushButton {
                background-color: #333333;
                border: 4px solid #ff6666;
                border-radius: 15px;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #222222;
                border: 4px solid #666666;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border: 4px solid #ff4d4d;
            }
            QPushButton:pressed {
                background-color: #333333;
                border: 4px solid #ff6666;
            }
        """


def update_button_style(button, checked):
    """Toggle the button style based on the state"""
    button.setStyleSheet(get_button_styles(checked))


def create_sequencer_widget(seq_x, seq_y, seq_width):
    step_count = 16
    step_size = 40  # Smaller square size
    total_spacing = seq_width - (step_count * step_size)
    step_spacing = total_spacing / (step_count - 1)

    sequencer_widget = QWidget()
    sequencer_layout = QHBoxLayout()
    sequencer_layout.setSpacing(step_spacing)
    sequencer_layout.setContentsMargins(seq_x, seq_y, 0, 0)

    buttons = []

    for i in range(step_count):
        button = QPushButton("")
        button.setFixedSize(step_size, step_size)
        button.setCheckable(True)
        button.setStyleSheet(get_button_styles(False))
        button.toggled.connect(
            lambda checked, btn=button: update_button_style(btn, checked)
        )

        buttons.append(button)
        sequencer_layout.addWidget(button)

    sequencer_widget.setLayout(sequencer_layout)
    return sequencer_widget


class JD_XiInstrument(QWidget):
    def __init__(
        self,
        digital_font_family=None,
        current_octave=0,
        preset_num=1,
        preset_name="INIT PATCH",
    ):
        super().__init__()

        # Create the main instrument layout
        self.setFixedSize(1000, 400)
        layout = QVBoxLayout()

        # Create the pixmap with painted elements
        self.pixmap_label = QLabel()
        self.pixmap_label.setPixmap(
            self.draw_instrument_pixmap(
                digital_font_family, current_octave, preset_num, preset_name
            )
        )
        layout.addWidget(self.pixmap_label)

        # Create and add the step sequencer widget
        seq_width = 400  # Approximate width for sequencer
        self.sequencer = create_sequencer_widget(
            seq_x=100, seq_y=300, seq_width=seq_width
        )
        layout.addWidget(self.sequencer)

        self.setLayout(layout)

    def draw_instrument_pixmap(
        self, digital_font_family, current_octave, preset_num, preset_name
    ):
        """Create a QPixmap of the JD-Xi instrument display."""
        width, height = 1000, 400
        image = QImage(width, height, QImage.Format_RGB32)
        image.fill(Qt.black)

        pixmap = QPixmap.fromImage(image)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        margin = 15

        # Draw title
        title_x, title_y = margin + 20, margin + 15
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Myriad Pro, Arial", 28, QFont.Bold))
        painter.drawText(title_x, title_y, "JD-Xi Manager")

        # Draw LED display area
        display_x, display_y = margin + 20, title_y + 30
        display_width, display_height = 215, 70

        painter.setBrush(QColor("#1A1A1A"))
        painter.setPen(QPen(QColor("#FF8C00"), 1))
        painter.drawRect(display_x, display_y, display_width, display_height)

        # Set up digital font for display
        display_font = QFont(
            digital_font_family if digital_font_family else "Consolas", 16
        )
        painter.setFont(display_font)
        painter.setPen(QPen(QColor("#FF8C00")))  # Orange color for text

        # Draw preset number and name
        preset_text = f"{preset_num:03d}:{preset_name}"[:20]  # Truncate if too long
        painter.drawText(display_x + 10, display_y + 25, preset_text)

        # Draw octave display
        oct_text = f"Octave {'+' if current_octave > 0 else ''}{current_octave}"
        painter.drawText(display_x + display_width - 60, display_y + 50, oct_text)

        painter.end()
        return pixmap


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

        # Create and show main window
        # from jdxi_manager.ui.main_window import MainWindow

        window = JD_XiInstrument()
        # window = MainWindow()
        window.show()
        logging.info("Main window displayed")
        # window.set_log_file(log_file)
        # Start event loop
        return app.exec()

    except Exception as e:
        logging.exception("Fatal error occurred")
        raise


if __name__ == "__main__":
    # List available MIDI input ports
    # input_ports = mido.get_input_names()
    # if not input_ports:
    #    print("No MIDI input ports available!")
    #    # exit()
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Application crashed: {str(e)}")  # Fallback if logging fails
        logging.exception("Application crashed")
        sys.exit(1)
