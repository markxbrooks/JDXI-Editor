"""Utility functions for the JDXI editor UI.

These functions are used to display messages, handle MIDI communication
and manage MIDI input/output ports."""


from PySide6.QtWidgets import QMessageBox

from jdxi_editor.log.logger import Logger as log


def show_message_box(title, text, icon=QMessageBox.Critical):
    """Helper method to display a QMessageBox."""
    log.message(text)
    msg_box = QMessageBox()
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.exec()
