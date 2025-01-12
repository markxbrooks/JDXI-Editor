import rtmidi
import logging
from typing import Optional, List, Union

from PySide6.QtWidgets import QWidget

from jdxi_manager.midi.constants import START_OF_SYSEX
from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)

class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize MIDI input/output
        
        Args:
            parent: Parent window for MIDI indicators
        """
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.current_in_port = None
        self.current_out_port = None
        self.parent = parent
        self.callbacks = []

    def get_input_ports(self) -> List[str]:
        """Get list of available MIDI input ports"""
        return self.midi_in.get_ports()
        
    def get_output_ports(self) -> List[str]:
        """Get list of available MIDI output ports"""
        return self.midi_out.get_ports()
        
    def open_input_port(self, port_name: str = None, port_number: int = None):
        """Open MIDI input port"""
        try:
            # Close existing port if open
            if self.current_in_port is not None:
                self.midi_in.close_port()
                self.midi_in = rtmidi.MidiIn()  # Create new instance
                self.current_in_port = None
            
            # Find port by name or number
            available_ports = self.midi_in.get_ports()
            
            if port_name:
                for i, name in enumerate(available_ports):
                    if port_name.lower() in name.lower():
                        port_number = i
                        break
            
            if port_number is not None and 0 <= port_number < len(available_ports):
                self.midi_in.open_port(port_number)
                self.current_in_port = port_number
                self.midi_in.set_callback(self._midi_callback)
                logging.info(f"Opened MIDI input port: {available_ports[port_number]}")
            else:
                logging.error("Invalid MIDI input port specified")
                
        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")

    def open_output_port(self, port_name: str = None, port_number: int = None):
        """Open MIDI output port"""
        try:
            # Close existing port if open
            if self.current_out_port is not None:
                self.midi_out.close_port()
                self.midi_out = rtmidi.MidiOut()  # Create new instance
                self.current_out_port = None
            
            # Find port by name or number
            available_ports = self.midi_out.get_ports()
            
            if port_name:
                for i, name in enumerate(available_ports):
                    if port_name.lower() in name.lower():
                        port_number = i
                        break
            
            if port_number is not None and 0 <= port_number < len(available_ports):
                self.midi_out.open_port(port_number)
                self.current_out_port = port_number
                logging.info(f"Opened MIDI output port: {available_ports[port_number]}")
            else:
                logging.error("Invalid MIDI output port specified")
                
        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")

    def close_ports(self):
        """Close all MIDI ports"""
        try:
            if self.current_in_port is not None:
                self.midi_in.close_port()
                self.current_in_port = None
            if self.current_out_port is not None:
                self.midi_out.close_port()
                self.current_out_port = None
            logging.debug("Closed all MIDI ports")
        except Exception as e:
            logging.error(f"Error closing MIDI ports: {str(e)}")

    def _midi_callback(self, message, timestamp):
        """Handle incoming MIDI messages"""
        try:
            data = message[0]
            
            # Forward message to parent window if available
            if self.parent and hasattr(self.parent, '_handle_midi_message'):
                self.parent._handle_midi_message(message, timestamp)
                
            # Blink MIDI in indicator if available
            if self.parent and hasattr(self.parent, 'midi_in_indicator'):
                self.parent.midi_in_indicator.blink()
                
        except Exception as e:
            logging.error(f"Error in MIDI callback: {str(e)}")

    def _decode_sysex(self, msg: List[int]) -> str:
        """Decode SysEx message into human-readable format"""
        try:
            parts = []
            parts.append("MIDI Message Breakdown:")
            parts.append(f"F0 | SysEx Start")
            parts.append(f"{msg[1]:02X} | Roland ID")
            parts.append(f"{msg[2]:02X} | Device ID")
            parts.append(f"{msg[3]:02X} {msg[4]:02X} {msg[5]:02X} | Model ID")
            parts.append(f"{msg[6]:02X} | JD-Xi ID")
            
            # Command type
            cmd = msg[7]
            cmd_type = "DT1 Command" if cmd == 0x12 else "RQ1 Command" if cmd == 0x11 else f"Unknown Command"
            parts.append(f"{cmd:02X} | {cmd_type}")
            
            # Memory area
            area_names = {
                0x19: "Digital Synth 1",
                0x1A: "Digital Synth 2",
                0x18: "Analog Synth",
                0x17: "Drum Kit",
                0x16: "Effects",
                0x15: "Arpeggiator",
                0x14: "Vocal FX"
            }
            area = msg[8]
            area_name = area_names.get(area, "Unknown Area")
            parts.append(f"{area:02X} | {area_name} Area")
            
            # Part/Section/Parameter
            parts.append(f"{msg[9]:02X} | Part Number")
            parts.append(f"{msg[10]:02X} | Parameter Group")
            parts.append(f"{msg[11]:02X} | Parameter Address")
            
            # Value (if present)
            if len(msg) > 13:
                parts.append(f"{msg[12]:02X} | Parameter Value")
            
            # Checksum (if present)
            if len(msg) > 14:
                parts.append(f"{msg[-2]:02X} | Checksum")
                
            parts.append(f"{msg[-1]:02X} | End of SysEx")
            
            return "\n".join(parts)
            
        except Exception as e:
            logging.error(f"Error decoding SysEx: {str(e)}")
            return "Error decoding SysEx message"

    def send_message(self, msg: Union[bytes, List[int]]) -> bool:
        """Send MIDI message"""
        try:
            # Convert bytes to list if necessary
            if isinstance(msg, bytes):
                msg = list(msg)
                
            # Ensure midi_out is open and available    
            if not self.midi_out or not self.midi_out.is_port_open():
                logging.error("No MIDI output port open")
                return False
                
            # Send the message
            self.midi_out.send_message(msg)
            
            # Log the message
            msg_hex = ' '.join([f'{b:02X}' for b in msg])
            if msg[0] == START_OF_SYSEX:
                logging.debug(f"Sent MIDI message: {msg_hex}")
                logging.debug(self._decode_sysex(msg))
            else:
                logging.debug(f"Sent MIDI message: {msg_hex}")
                
            # Blink MIDI out indicator if available
            if self.parent and hasattr(self.parent, 'midi_out_indicator'):
                self.parent.midi_out_indicator.blink()
                
            return True
            
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
            return False

    def send_bank_select(self, msb: int, lsb: int, channel: int = 0):
        """Send bank select messages
        
        Args:
            msb: Bank select MSB (0-127)
            lsb: Bank select LSB (0-127)
            channel: MIDI channel (0-15)
        """
        try:
            # Bank Select MSB (CC 0)
            self.send_message([0xB0 | channel, 0x00, msb])
            
            # Bank Select LSB (CC 32)
            self.send_message([0xB0 | channel, 0x20, lsb])
            
            logging.debug(f"Sent bank select MSB:{msb} LSB:{lsb} on channel {channel}")
            
        except Exception as e:
            logging.error(f"Error sending bank select: {str(e)}")
            raise

    def send_program_change(self, program: int, channel: int = 0):
        """Send program change message
        
        Args:
            program: Program number (0-127)
            channel: MIDI channel (0-15)
        """
        try:
            # Program Change
            self.send_message([0xC0 | channel, program])
            
            logging.debug(f"Sent program change {program} on channel {channel}")
            
        except Exception as e:
            logging.error(f"Error sending program change: {str(e)}")
            raise