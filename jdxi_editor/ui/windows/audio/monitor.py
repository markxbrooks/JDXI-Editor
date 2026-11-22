"""
Audio Monitor
=============

A rack window for the oscilloscope, the VU meters, and the spectrum.
It listens to an audio input. It does not listen to MIDI.
"""

from typing import Optional

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from jdxi_editor.ui.widgets.audio.audio_monitor import AudioMonitor
from jdxi_editor.ui.widgets.rack import RackPanel
from picoui.helpers import create_layout_with_items


class AudioMonitorWindow(QMainWindow):
    """AudioMonitorWindow"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Audio Monitor")
        _apply_dark_controls(self)
        self.setMinimumSize(760, 520)
        central = QWidget()
        self.monitor = AudioMonitor()
        self.setCentralWidget(RackPanel(central))
        _layout = create_layout_with_items(parent=central, items=[self.monitor])

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Release the input when the window closes.

        :param event: QCloseEvent
        :return: None
        """
        self.monitor.stop()
        super().closeEvent(event)


def _apply_dark_controls(window: QWidget) -> None:
    """
    Dark controls for this window only.

    This used to call ThemeManager().apply_theme(), whose qdarktheme
    setup_theme replaces the whole application's stylesheet: opening the
    monitor re-polished every widget of every open editor (seconds, longer
    the more editors are open) and restyled them all. The same stylesheet set
    on the window reaches only the monitor's own controls.

    :param window: QWidget
    :return: None
    """
    try:
        import qdarktheme
    except ImportError:
        return
    try:
        window.setPalette(qdarktheme.load_palette("dark"))
        window.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    except Exception:
        pass  # plain controls are still usable
