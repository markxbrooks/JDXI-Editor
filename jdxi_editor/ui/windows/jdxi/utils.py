"""
Utility functions for the JDXI editor UI.

These functions are used to digital messages, handle MIDI communication
and manage MIDI input/output ports.
"""

from decologr import Decologr as log
from picoui.specs.widgets import MessageBoxSpec
from PySide6.QtWidgets import QMessageBox

from jdxi_editor.ui.style import JDXiUIStyle

_ICON_MAP = {
    "Information": QMessageBox.Icon.Information,
    "Warning": QMessageBox.Icon.Warning,
    "Critical": QMessageBox.Icon.Critical,
    "Question": QMessageBox.Icon.Question,
}


def show_message_box(
    title: str, text: str, icon: object = QMessageBox.Icon.Critical
) -> None:
    """Helper method to display a QMessageBox."""
    log.message(text)
    msg_box = QMessageBox()
    msg_box.setStyleSheet(JDXiUIStyle.WINDOW_DEBUGGER)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.exec()


def show_message_box_from_spec(
    spec: MessageBoxSpec,
    *,
    title: str | None = None,
    message: str | None = None,
) -> None:
    """Show a QMessageBox from a MessageBoxSpec; optionally call spec.slot after dismiss.
    Pass title= or message= to override the spec's value (for dynamic content).
    """
    t = title if title is not None else spec.title
    m = message if message is not None else spec.message
    icon = _ICON_MAP.get(spec.type_attr, QMessageBox.Icon.Information)
    show_message_box(t, m, icon)
    if getattr(spec, "slot", None) is not None:
        spec.slot()
