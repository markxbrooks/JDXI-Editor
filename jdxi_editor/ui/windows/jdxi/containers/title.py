from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from jdxi_editor.ui.style import Style
from jdxi_editor.ui.windows.jdxi.dimensions import JDXI_TITLE_X, JDXI_TITLE_Y


def add_title_container(central_widget):
    title_container = QWidget(central_widget)
    title_container.setGeometry(JDXI_TITLE_X + 10, JDXI_TITLE_Y, 200, 50)
    title_container.setStyleSheet(Style.JDXI_TRANSPARENT_WHITE)
    title_layout = QHBoxLayout()
    title_container.setLayout(title_layout)
    title_label = QLabel("JD-Xi Editor")
    font = QFont()
    font.setFamilies(["Myriad Pro", "Segoe UI"])  # Qt 6+
    font.setStyleHint(QFont.SansSerif)
    font.setPointSize(24)
    font.setBold(True)  # Optionally make it bold

    # Apply the font to the QLabel
    title_label.setFont(font)
    title_layout.addWidget(title_label)
