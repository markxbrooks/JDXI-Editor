from PySide6.QtCore import QObject
import rtmidi
from typing import List, Optional, Tuple, Callable
import logging

class MIDIBase(QObject):
    """Base class for MIDI handling."""

    def __init__(self, midi_in=None, midi_out=None, parent=None):
        # Initialize QObject first
        super().__init__(parent)
        
        # Initialize instance variables
        self._is_input_open = False
        self._is_output_open = False
        self._current_in_port = None
        self._current_out_port = None
        self._input_port_number = None
        self._output_port_number = None
        
        # Initialize MIDI objects
        self.midi_in = midi_in or rtmidi.MidiIn()
        self.midi_out = midi_out or rtmidi.MidiOut()

    @property
    def is_input_open(self) -> bool:
        return self._is_input_open

    @property
    def is_output_open(self) -> bool:
        return self._is_output_open

    @property
    def current_in_port(self) -> Optional[str]:
        return self._current_in_port

    @property
    def current_out_port(self) -> Optional[str]:
        return self._current_out_port

    @property
    def input_port_number(self) -> Optional[int]:
        return self._input_port_number

    @property
    def output_port_number(self) -> Optional[int]:
        return self._output_port_number

    def get_input_ports(self) -> List[str]:
        return self.midi_in.get_ports()

    def get_output_ports(self) -> List[str]:
        return self.midi_out.get_ports()

    def find_jdxi_ports(self) -> Tuple[Optional[str], Optional[str]]:
        """Find JD-Xi input and output ports."""
        in_ports, out_ports = self.get_input_ports(), self.get_output_ports()
        jdxi_in = next((p for p in in_ports if "jd-xi" in p.lower()), None)
        jdxi_out = next((p for p in out_ports if "jd-xi" in p.lower()), None)
        return jdxi_in, jdxi_out

    def open_input_port(self, port_name_or_index) -> bool:
        """Open MIDI input port by name or index"""
        try:
            ports = self.get_input_ports()
            port_index = port_name_or_index

            if isinstance(port_name_or_index, str):
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
                else:
                    logging.error(f"MIDI input port not found: {port_name_or_index}")
                    return False

            if not isinstance(port_index, int) or not (0 <= port_index < len(ports)):
                logging.error(f"Invalid MIDI input port index: {port_index}")
                return False

            self.midi_in.open_port(port_index)
            self._input_port_number = port_index
            self._current_in_port = ports[port_index]
            self._is_input_open = True
            logging.info(f"Opened MIDI input port: {ports[port_index]}")
            return True

        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")
            return False

    def open_output_port(self, port_name_or_index) -> bool:
        """Open MIDI output port by name or index"""
        try:
            ports = self.get_output_ports()
            port_index = port_name_or_index

            if isinstance(port_name_or_index, str):
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
                else:
                    logging.error(f"MIDI output port not found: {port_name_or_index}")
                    return False

            if not isinstance(port_index, int) or not (0 <= port_index < len(ports)):
                logging.error(f"Invalid MIDI output port index: {port_index}")
                return False

            self.midi_out.open_port(port_index)
            self._output_port_number = port_index
            self._current_out_port = ports[port_index]
            self._is_output_open = True
            logging.info(f"Opened MIDI output port: {ports[port_index]}")
            return True

        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return False

    def close_ports(self):
        """Close both input and output ports."""
        if self.midi_in.is_port_open():
            self.midi_in.close_port()
            self._is_input_open = False
            self._current_in_port = None
        if self.midi_out.is_port_open():
            self.midi_out.close_port()
            self._is_output_open = False
            self._current_out_port = None 