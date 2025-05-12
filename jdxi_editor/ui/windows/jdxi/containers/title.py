from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


def add_title_container(central_widget):
    """add container for main title"""
    title_container = QWidget(central_widget)
    title_container.setGeometry(
        JDXiDimensions.TITLE_X,
        JDXiDimensions.TITLE_Y,
        JDXiDimensions.TITLE_WIDTH,
        JDXiDimensions.TITLE_HEIGHT,
    )
    title_container.setStyleSheet(JDXiStyle.TRANSPARENT_WHITE)
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
