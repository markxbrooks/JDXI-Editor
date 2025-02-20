import logging
from typing import Optional, List, Tuple

import rtmidi
from PySide6.QtCore import QObject


class MIDIBase(QObject):
    """Helper class for MIDI communication with the JD-Xi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.input_port_number: Optional[int] = None
        self.output_port_number: Optional[int] = None

    @property
    def current_in_port(self) -> Optional[str]:
        """Get current input port name"""
        if self.input_port_number is not None and self.is_input_open:
            ports = self.midi_in.get_ports()
            if 0 <= self.input_port_number < len(ports):
                return ports[self.input_port_number]
        return None

    @property
    def current_out_port(self) -> Optional[str]:
        """Get current output port name"""
        if self.output_port_number is not None and self.is_output_open:
            ports = self.midi_out.get_ports()
            if 0 <= self.output_port_number < len(ports):
                return ports[self.output_port_number]
        return None

    def get_input_ports(self) -> List[str]:
        """Get available MIDI input ports"""
        return self.midi_in.get_ports()

    def get_output_ports(self) -> List[str]:
        """Get available MIDI output ports"""
        return self.midi_out.get_ports()

    # def get_ports(self) -> Tuple[List[str], List[str]]:
    #    return self.midi_in.get_ports(), self.midi_out.get_ports()

    def find_jdxi_ports(self) -> Tuple[Optional[str], Optional[str]]:
        """Find JD-Xi input and output ports"""
        in_ports = self.get_input_ports()
        out_ports = self.get_output_ports()

        jdxi_in = next((p for p in in_ports if "jd-xi" in p.lower()), None)
        jdxi_out = next((p for p in out_ports if "jd-xi" in p.lower()), None)

        return (jdxi_in, jdxi_out)

    def open_input(self, port_name_or_index) -> bool:
        """Open MIDI input port by name or index"""
        return self.open_input_port(port_name_or_index)

    def open_output(self, port_name_or_index) -> bool:
        """Open MIDI output port by name or index"""
        return self.open_output_port(port_name_or_index)

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
            self.input_port_number = port_index
            self.midi_in.set_callback(self.midi_callback)
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
                # Find port index by name
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
                else:
                    logging.error(f"MIDI output port not found: {port_name_or_index}")
                    return False

            # Validate port index
            if not isinstance(port_index, int) or not (0 <= port_index < len(ports)):
                logging.error(f"Invalid MIDI output port index: {port_index}")
                return False

            self.midi_out.open_port(port_index)
            self.output_port_number = port_index
            logging.info(f"Opened MIDI output port: {ports[port_index]}")
            return True

        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return False

    def close_ports(self):
        """Close MIDI ports"""
        if self.midi_in.is_port_open():
            self.midi_in.close_port()
        if self.midi_out.is_port_open():
            self.midi_out.close_port()
        self.input_port_number = None
        self.output_port_number = None

    @property
    def is_input_open(self) -> bool:
        """Check if MIDI input port is open"""
        return self.midi_in.is_port_open()

    @property
    def is_output_open(self) -> bool:
        """Check if MIDI output port is open"""
        return self.midi_out.is_port_open()

    def open_ports(self, in_port: str, out_port: str) -> bool:
        """Open both input and output ports by name

        Args:
            in_port: Input port name or None
            out_port: Output port name or None
        """
        try:
            input_success = True
            output_success = True

            if in_port:
                input_success = self.open_input_port(in_port)
            if out_port:
                output_success = self.open_output_port(out_port)

            return input_success and output_success

        except Exception as e:
            logging.error(f"Error opening MIDI ports: {str(e)}")
            return False
