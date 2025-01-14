import rtmidi
import logging
from typing import List, Optional, Callable
from dataclasses import dataclass

from jdxi_manager.midi.constants import (
    START_OF_SYSEX, END_OF_SYSEX, ROLAND_ID, DEVICE_ID,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, RQ1_COMMAND_11,
    DIGITAL_SYNTH_AREA, ANALOG_SYNTH_AREA, DRUM_KIT_AREA,
    EFFECTS_AREA
)

@dataclass
class MIDIPort:
    """MIDI port information"""
    name: str
    port_type: str  # 'in' or 'out'
    port_number: int

class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, parent=None):
        """Initialize MIDI helper
        
        Args:
            parent: Parent window for callbacks
        """
        self.midi_in = None
        self.midi_out = None
        self.current_in_port = None
        self.current_out_port = None
        self.parent = parent
        self.callbacks = []
        
    @property
    def is_input_open(self) -> bool:
        """Check if MIDI input port is open"""
        return self.midi_in is not None and self.current_in_port is not None

    @property 
    def is_output_open(self) -> bool:
        """Check if MIDI output port is open"""
        return self.midi_out is not None and self.current_out_port is not None

    @property
    def input_port_name(self) -> Optional[str]:
        """Get name of current input port"""
        return self.current_in_port

    @property
    def output_port_name(self) -> Optional[str]:
        """Get name of current output port"""
        return self.current_out_port
        
    @staticmethod
    def get_input_ports() -> List[str]:
        """Get list of available MIDI input ports"""
        try:
            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()
            midi_in.delete()  # Clean up
            return ports
        except Exception as e:
            logging.error(f"Error getting MIDI input ports: {str(e)}")
            return []
            
    @staticmethod
    def get_output_ports() -> List[str]:
        """Get list of available MIDI output ports"""
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            midi_out.delete()  # Clean up
            return ports
        except Exception as e:
            logging.error(f"Error getting MIDI output ports: {str(e)}")
            return []
            
    def open_ports(self, in_port: str, out_port: str) -> bool:
        """Open MIDI input and output ports
        
        Args:
            in_port: Input port name
            out_port: Output port name
            
        Returns:
            True if both ports opened successfully
        """
        try:
            # Close any existing ports
            self.close_ports()
            
            # Open input port
            if in_port:
                self.midi_in = rtmidi.MidiIn()
                ports = self.midi_in.get_ports()
                if in_port in ports:
                    port_num = ports.index(in_port)
                    self.midi_in.open_port(port_num)
                    self.midi_in.set_callback(self._midi_callback)
                    self.current_in_port = in_port
                    logging.info(f"Opened MIDI input port: {in_port}")
                else:
                    logging.error(f"MIDI input port not found: {in_port}")
                    return False
                    
            # Open output port
            if out_port:
                self.midi_out = rtmidi.MidiOut()
                ports = self.midi_out.get_ports()
                if out_port in ports:
                    port_num = ports.index(out_port)
                    self.midi_out.open_port(port_num)
                    self.current_out_port = out_port
                    logging.info(f"Opened MIDI output port: {out_port}")
                else:
                    logging.error(f"MIDI output port not found: {out_port}")
                    return False
                    
            return True
            
        except Exception as e:
            logging.error(f"Error opening MIDI ports: {str(e)}")
            return False
            
    def close_ports(self):
        """Close MIDI ports"""
        try:
            if self.midi_in:
                self.midi_in.close_port()
                self.midi_in.delete()
                self.midi_in = None
                self.current_in_port = None
                
            if self.midi_out:
                self.midi_out.close_port()
                self.midi_out.delete()
                self.midi_out = None
                self.current_out_port = None
                
            logging.info("Closed MIDI ports")
            
        except Exception as e:
            logging.error(f"Error closing MIDI ports: {str(e)}")
            
    def register_callback(self, callback: Callable):
        """Register callback for MIDI messages
        
        Args:
            callback: Function to call with (message, timestamp)
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            
    def _midi_callback(self, message, timestamp):
        """Handle incoming MIDI message
        
        Args:
            message: MIDI message data
            timestamp: Message timestamp
        """
        try:
            # Call all registered callbacks
            for callback in self.callbacks:
                callback(message, timestamp)
                
        except Exception as e:
            logging.error(f"Error in MIDI callback: {str(e)}")
            
    def send_message(self, message):
        """Send MIDI message
        
        Args:
            message: MIDI message to send
        """
        try:
            if self.midi_out:
                self.midi_out.send_message(message)
                logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in message])}")
            else:
                logging.warning("No MIDI output port available")
                
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
            
    def send_parameter(self, area: int, part: int, group: int, param: int, value: int):
        """Send parameter change message
        
        Args:
            area: Memory area
            part: Part number
            group: Parameter group
            param: Parameter number
            value: Parameter value
        """
        try:
            # Create parameter change message
            message = [
                START_OF_SYSEX,
                ROLAND_ID,
                DEVICE_ID,
                *MODEL_ID,
                DT1_COMMAND_12,
                area,
                part,
                group,
                param,
                value,
                self._calculate_checksum([area, part, group, param, value]),
                END_OF_SYSEX
            ]
            
            self.send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            
    def _calculate_checksum(self, data: List[int]) -> int:
        """Calculate Roland checksum
        
        Args:
            data: List of bytes to checksum
            
        Returns:
            Checksum value (0-127)
        """
        checksum = sum(data) % 128
        return (128 - checksum) & 0x7F