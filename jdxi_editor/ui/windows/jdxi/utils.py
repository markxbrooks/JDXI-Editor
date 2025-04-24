import logging

from PySide6.QtWidgets import QMessageBox


def show_message_box(title, text, icon=QMessageBox.Critical):
    """Helper method to display a QMessageBox."""
    logging.info(text)
    msg_box = QMessageBox()
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.exec()
