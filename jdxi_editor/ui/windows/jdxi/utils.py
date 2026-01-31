"""
Utility functions for the JDXI editor UI.

These functions are used to display messages, handle MIDI communication
and manage MIDI input/output ports.
"""

from decologr import Decologr as log
from PySide6.QtWidgets import QMessageBox

from jdxi_editor.ui.style import JDXiUIStyle


def show_message_box(
    title: str, text: str, icon: object = QMessageBox.Critical
) -> None:
    """Helper method to display a QMessageBox."""
    log.message(text)
    msg_box = QMessageBox()
    msg_box.setStyleSheet(JDXiUIStyle.WINDOW_DEBUGGER)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.exec()
