"""
MIDI I/O Controller for JD-Xi

This module provides the `MidiIOController` class, which facilitates MIDI communication
with the Roland JD-Xi synthesizer. It allows users to list, open, and manage MIDI input
and output ports, automatically detect JD-Xi ports, and handle MIDI message reception.

Features:
- Retrieve available MIDI input and output ports.
- Automatically detect JD-Xi MIDI ports.
- Open and close MIDI input and output ports by name or index.
- Check the status of open MIDI ports.
- Set a callback for incoming MIDI messages.

Dependencies:
- `rtmidi` for MIDI communication.
- `PyQt6.QtCore` for QObject-based structure.

Example Usage:
    controller = MidiIOController()
    controller.open_ports("JD-Xi MIDI IN", "JD-Xi MIDI OUT")
    print(controller.current_in_port, controller.current_out_port)

"""

import time
from typing import Optional, List, Tuple

import rtmidi
from PySide6.QtCore import QObject

from jdxi_editor.log.logger import Logger as log


class MidiIOController(QObject):
    """Helper class for MIDI communication with the JD-Xi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.input_port_number: Optional[int] = None
        self.output_port_number: Optional[int] = None

    @property
    def current_in_port(self) -> Optional[str]:
        """
        Get current input port name

        :return: Optional[str], MIDI input port name
        """
        if self.input_port_number is not None and self.is_input_open:
            ports = self.midi_in.get_ports()
            if 0 <= self.input_port_number < len(ports):
                return ports[self.input_port_number]
        return None

    @property
    def current_out_port(self) -> Optional[str]:
        """
        Get current output port name

        :return: Optional[str], MIDI output port name
        """
        if self.output_port_number is not None and self.is_output_open:
            ports = self.midi_out.get_ports()
            if 0 <= self.output_port_number < len(ports):
                return ports[self.output_port_number]
        return None

    def get_input_ports(self) -> List[str]:
        """
        Get available MIDI input ports

        :return: List[str], MIDI input ports
        """
        return self.midi_in.get_ports()

    def get_output_ports(self) -> List[str]:
        """
        Get available MIDI output ports

        :return: List[str], MIDI output ports
        """
        return self.midi_out.get_ports()

    def find_jdxi_ports(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Find JD-Xi input and output ports

        :return: Tuple[Optional[str], Optional[str]], JD-Xi input and output ports
        """
        in_ports = self.get_input_ports()
        out_ports = self.get_output_ports()

        jdxi_in = next((p for p in in_ports if "jd-xi" in p.lower()), None)
        jdxi_out = next((p for p in out_ports if "jd-xi" in p.lower()), None)

        return (jdxi_in, jdxi_out)

    def open_input(self, port_name_or_index) -> bool:
        """
        Open MIDI input port by name or index

        :param port_name_or_index: str, MIDI input port name or index
        :return: bool True if successful, False otherwise
        """
        return self.open_input_port(port_name_or_index)

    def open_output(self, port_name_or_index: str) -> bool:
        """
        Open MIDI output port by name or index

        :param port_name_or_index: str
        :return: bool True if successful, False otherwise
        """
        return self.open_output_port(port_name_or_index)

    def open_input_port(self, port_name_or_index: str) -> bool:
        """
        Open MIDI input port by name or index

        :param port_name_or_index: str
        :return: bool
        """
        try:
            ports = self.get_input_ports()
            port_index = port_name_or_index

            if isinstance(port_name_or_index, str):
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
                else:
                    log.error(f"MIDI input port not found: {port_name_or_index}")
                    return False

            if not isinstance(port_index, int) or not (0 <= port_index < len(ports)):
                log.parameter("Invalid MIDI input port index:", port_index)
                return False

            self.midi_in.open_port(port_index)
            self.input_port_number = port_index
            log.parameter("Opened MIDI input port:", ports[port_index])
            return True

        except Exception as ex:
            log.error(f"Error opening MIDI input port: {str(ex)}")
            return False

    def open_output_port(self, port_name_or_index: str) -> bool:
        """
        Open MIDI output port by name or index

        :param port_name_or_index: str, MIDI output port name or index
        :return: bool True if successful, False otherwise
        """
        try:
            ports = self.get_output_ports()

            port_index = None
            if isinstance(port_name_or_index, str):
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
            elif isinstance(port_name_or_index, int):
                if 0 <= port_name_or_index < len(ports):
                    port_index = port_name_or_index

            if port_index is None:
                log.error(f"Invalid or missing MIDI output port: {port_name_or_index}")
                return False

            # Safely close if already open
            if self.midi_out.is_port_open():
                self.midi_out.close_port()
                time.sleep(0.1)  # Give time for the port to be released

            self.midi_out = rtmidi.MidiOut()  # <- reinitialize
            self.midi_out.open_port(port_index)
            self.output_port_number = port_index
            log.parameter("Opened MIDI output port:", ports[port_index])
            return True

        except Exception as ex:
            log.error(f"Error opening MIDI output port: {str(ex)}")
            return False

    def close_ports(self):
        """
        Close MIDI ports

        :return: None
        """
        if self.midi_in.is_port_open():
            self.midi_in.close_port()
            time.sleep(0.1)
        if self.midi_out.is_port_open():
            self.midi_out.close_port()
            time.sleep(0.1)
        self.input_port_number = None
        self.output_port_number = None

    @property
    def is_input_open(self) -> bool:
        """
        Check if MIDI input port is open

        :return: bool
        """
        return self.midi_in.is_port_open()

    @property
    def is_output_open(self) -> bool:
        """
        Check if MIDI output port is open

        :return: bool
        """
        return self.midi_out.is_port_open()

    def open_ports(self, in_port: str, out_port: str) -> bool:
        """
        Open both input and output ports by name

        :param in_port: str, Input port name or None
        :param out_port: str, Output port name or None
        :return: bool
        """
        try:
            input_success = True
            output_success = True

            if in_port:
                input_success = self.open_input_port(in_port)
            if out_port:
                output_success = self.open_output_port(out_port)

            return input_success and output_success

        except Exception as ex:
            log.error(f"Error opening MIDI ports: {str(ex)}")
            return False
