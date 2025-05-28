"""
message_debug module
====================

MIDIMessageDebug is a Qt-based main window for logging and displaying MIDI messages.
It provides a real-time log view where MIDI messages can be logged with timestamps,
allowing for easy debugging of MIDI communication.

Attributes:
    log_view (QTextEdit): A text edit widget used to display the MIDI message log.

Methods:
    log.message(message, direction="→"): Logs a MIDI message with a timestamp.
    Optionally, the direction (input or output) of the message can be specified.
    clear_log(): Clears the message log view.
"""
from typing import Optional
from datetime import datetime

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.io.helper import MidiIOHelper


class MIDIMessageMonitor(QMainWindow):
    """ MIDIMessageMonitor """
    def __init__(
        self, midi_helper: MidiIOHelper = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setWindowTitle("MIDI Message Monitor")
        self.setMinimumSize(600, 400)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Create log view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QTextEdit.NoWrap)
        self.log_view.setStyleSheet(JDXiStyle.MIDI_MESSAGE_MONITOR)
        layout.addWidget(self.log_view)
        self.midi_helper = midi_helper
        self.midi_helper.midi_message_incoming.connect(self.process_incoming_message)
        self.midi_helper.midi_message_outgoing.connect(self.process_outgoing_message)

    def process_incoming_message(self, message: str) -> None:
        """
        process_incoming_message
        :param message: str
        :return: None
        """
        self.log_message(message, direction="←")

    def process_outgoing_message(self, message: str) -> None:
        """
        process_outgoing_message
        :param message: str
        :return: None
        """
        self.log_message(message)

    def log_message(self, message: str, direction="→"):
        """
        Log address MIDI message with timestamp and hex formatting if possible
        :param message: str
        :param direction: str
        :return: None
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        if isinstance(message, (list, bytes)):
            try:
                hex_str = " ".join([f"{int(b):02X}" for b in message])
            except (ValueError, TypeError):
                hex_str = str(message)
            self.log_view.append(f"{timestamp} {direction} {hex_str}")
        else:
            self.log_view.append(f"{timestamp} {direction} {message}")

    def clear_log(self):
        """Clear the log view"""
        self.log_view.clear()
