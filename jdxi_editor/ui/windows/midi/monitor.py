"""
MIDI message monitor
====================

MIDIMessageMonitor is a Qt window that logs MIDI messages with timestamps:
messages to and from the JD-Xi and, when one is connected, messages from an
external controller such as the Arturia MiniLab 3 (prefixed with its port name).

Attributes:
    log_view (QTextEdit): read-only view of the message log.

Methods:
    log_message(message, direction="→"): log a MIDI message with a timestamp.
    log_status(): log which JD-Xi and controller ports are being watched.
    clear_log(): clear the message log view.
"""

from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget

from jdxi_editor.midi.io.external_controller import ExternalControllerInput
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.theme import ThemeManager


class MIDIMessageMonitor(QMainWindow):
    """MIDIMessageMonitor"""

    def __init__(
        self,
        midi_helper: MidiIOHelper = None,
        parent: Optional[QWidget] = None,
        external_controller: Optional[ExternalControllerInput] = None,
    ):
        """
        :param midi_helper: MidiIOHelper JD-Xi MIDI input and output
        :param parent: Optional[QWidget] parent widget
        :param external_controller: Optional[ExternalControllerInput] hardware controller input
        """
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
        ThemeManager.apply_midi_monitor(self.log_view)
        layout.addWidget(self.log_view)
        self.midi_helper = midi_helper
        if midi_helper is not None:
            midi_helper.midi_message_incoming.connect(self.process_incoming_message)
            midi_helper.midi_message_outgoing.connect(self.process_outgoing_message)
        self.external_controller = external_controller
        if external_controller is not None:
            external_controller.message_received.connect(
                self.process_controller_message
            )
            external_controller.ports_changed.connect(self.log_controller_ports)
        self.log_status()

    def log_status(self) -> None:
        """
        Log which ports the monitor is watching.

        An empty log otherwise reads the same whether nothing is being sent or
        nothing is connected, which is the first thing to rule out.

        :return: None
        """
        if self.midi_helper is None:
            self.log_view.append("JD-Xi: no MIDI helper")
        else:
            in_port = self.midi_helper.current_in_port
            out_port = self.midi_helper.current_out_port
            self.log_view.append(f"JD-Xi in:  {in_port or 'not connected'}")
            self.log_view.append(f"JD-Xi out: {out_port or 'not connected'}")
        if self.external_controller is None:
            return
        self.log_controller_ports(self.external_controller.port_names)

    def log_controller_ports(self, port_names: list) -> None:
        """
        Log the controller ports being listened to.

        :param port_names: list[str] controller input port names
        :return: None
        """
        ports = ", ".join(port_names) if port_names else "none connected"
        self.log_view.append(f"External controller: {ports}")

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

    def process_controller_message(self, port_name: str, message: object) -> None:
        """
        Log a message from the external controller, prefixed with its port.

        :param port_name: str controller input port name
        :param message: mido.Message
        :return: None
        """
        self.log_message(f"[{port_name}] {message}", direction="←")

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
