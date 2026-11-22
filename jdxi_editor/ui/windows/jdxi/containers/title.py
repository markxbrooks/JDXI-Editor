"""
title.py

Add a title container to the instrument
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.project import __program__


def add_title_container(host: QWidget) -> QLabel:
    """add the main title to ``host``"""
    host.setStyleSheet(JDXi.UI.Style.TRANSPARENT_WHITE)
    title_layout = QHBoxLayout(host)
    title_label = QLabel(__program__)
    title_label.setObjectName("instrument_title")
    font = QFont()
    font.setFamilies(["Myriad Pro", "Segoe UI"])  # Qt 6+
    font.setStyleHint(QFont.SansSerif)
    font.setPointSize(24)
    font.setBold(True)  # Optionally make it bold

    # Apply the font to the QLabel
    title_label.setFont(font)
    title_layout.addWidget(title_label)
    return title_label
