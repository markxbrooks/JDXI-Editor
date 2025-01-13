import rtmidi
import logging
from typing import Optional, List, Union

from PySide6.QtWidgets import QWidget

from jdxi_manager.midi.constants import (
    START_OF_SYSEX, END_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID,
    DT1_COMMAND, DIGITAL_SYNTH_AREA, OSC_1_GROUP,
    BANK_SELECT_MSB, BANK_SELECT_LSB, PROGRAM_CHANGE,
    ANALOG_BANK_MSB, DIGITAL_BANK_MSB, DRUM_BANK_MSB,
    PRESET_BANK_LSB, PRESET_BANK_2_LSB, USER_BANK_LSB
)
from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx,
    IdentityRequest,
    create_parameter_message
)

class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize MIDI input/output"""
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.current_in_port = None
        self.current_out_port = None
        self.parent = parent
        self.callbacks = []
        
        # Initialize bank select values
        self._last_bank_msb = 0
        self._last_bank_lsb = 0
        self._last_channel = 0

    def send_message(self, message: Union[bytes, List[int]]) -> bool:
        """Send MIDI message
        
        Args:
            message: MIDI message as bytes or list of integers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.midi_out or not self.midi_out.is_port_open():
                logging.error("No MIDI output port open")
                return False
                
            # Convert to list if needed
            if isinstance(message, bytes):
                message = list(message)
                
            # Send message
            self.midi_out.send_message(message)
            
            # Trigger MIDI out indicator if available
            if hasattr(self.parent, 'midi_out_indicator'):
                self.parent.midi_out_indicator.blink()
                
            return True
            
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
            return False

    def register_callback(self, callback):
        """Register a callback function for MIDI messages"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            logging.debug(f"Registered MIDI callback: {callback.__qualname__}")

    def unregister_callback(self, callback):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logging.debug(f"Unregistered MIDI callback: {callback.__qualname__}")

    def _midi_callback(self, message, timestamp):
        """Internal callback that distributes messages to all registered callbacks"""
        try:
            # Call all registered callbacks
            for callback in self.callbacks:
                callback(message[0], timestamp)  # message[0] contains the actual MIDI data
                
            # Trigger MIDI in indicator if available
            if hasattr(self.parent, 'midi_in_indicator'):
                self.parent.midi_in_indicator.blink()
                
        except Exception as e:
            logging.error(f"Error in MIDI callback: {str(e)}")

    def get_input_ports(self) -> List[str]:
        """Get list of available MIDI input ports"""
        return self.midi_in.get_ports()
        
    def get_output_ports(self) -> List[str]:
        """Get list of available MIDI output ports"""
        return self.midi_out.get_ports()

    def open_input_port(self, port_name: str) -> bool:
        """Open MIDI input port"""
        try:
            # Close existing port if any
            if self.current_in_port is not None:
                self.midi_in.close_port()
                
            # Find and open new port
            port_names = self.midi_in.get_ports()
            if port_name in port_names:
                port_num = port_names.index(port_name)
                self.midi_in.open_port(port_num)
                self.midi_in.set_callback(self._midi_callback)
                self.current_in_port = port_name
                logging.info(f"Opened MIDI input port: {port_name}")
                return True
                
            logging.error(f"MIDI input port not found: {port_name}")
            return False
            
        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")
            return False

    def open_output_port(self, port_name: str) -> bool:
        """Open MIDI output port"""
        try:
            # Close existing port if any
            if self.current_out_port is not None:
                self.midi_out.close_port()
                
            # Find and open new port
            port_names = self.midi_out.get_ports()
            if port_name in port_names:
                port_num = port_names.index(port_name)
                self.midi_out.open_port(port_num)
                self.current_out_port = port_name
                logging.info(f"Opened MIDI output port: {port_name}")
                return True
                
            logging.error(f"MIDI output port not found: {port_name}")
            return False
            
        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return False

    def close_ports(self):
        """Close all MIDI ports"""
        try:
            if self.current_in_port is not None:
                self.midi_in.close_port()
                self.current_in_port = None
            if self.current_out_port is not None:
                self.midi_out.close_port()
                self.current_out_port = None
                
        except Exception as e:
            logging.error(f"Error closing MIDI ports: {str(e)}")

    def send_identity_request(self) -> bool:
        """Send Identity Request message to identify connected device
        
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            request = IdentityRequest()
            return self.send_message(request.to_list())
            
        except Exception as e:
            logging.error(f"Error sending identity request: {str(e)}")
            return False

    def send_parameter(self, area: int, part: int, group: int, param: int, value: int) -> bool:
        """Send parameter change message"""
        try:
            # Debug log the values
            logging.debug(f"Sending parameter message:")
            logging.debug(f"Area: {area:02X}")
            logging.debug(f"Part: {part:02X}")
            logging.debug(f"Group: {group:02X}")  # Should be 0x20 for OSC1
            logging.debug(f"Param: {param:02X}")
            logging.debug(f"Value: {value:02X}")
            
            message = create_parameter_message(
                area=area,
                part=part,
                group=group,
                param=param,
                value=value
            )
            
            # Debug log the final message
            logging.debug("Message: " + " ".join([f"{b:02X}" for b in message]))
            
            return self.send_message(message)
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            return False

    def send_bank_select(self, msb: int, lsb: int, program: int, channel: int = 0) -> bool:
        """Send bank select and program change messages
        
        Args:
            msb: Bank select MSB value
            lsb: Bank select LSB value
            program: Program number (0-127)
            channel: MIDI channel (0-15)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate parameters
            if not 0 <= channel <= 15:
                raise ValueError(f"Invalid MIDI channel: {channel}")
            
            if not 0 <= program <= 127:
                raise ValueError(f"Invalid program number: {program}")
            
            # Validate bank values based on synth type
            if msb == ANALOG_BANK_MSB:
                if lsb not in [PRESET_BANK_LSB, USER_BANK_LSB]:
                    raise ValueError(f"Invalid LSB for analog synth: {lsb:02X}")
                
            elif msb == DIGITAL_BANK_MSB:
                if lsb not in [PRESET_BANK_LSB, PRESET_BANK_2_LSB, USER_BANK_LSB]:
                    raise ValueError(f"Invalid LSB for digital synth: {lsb:02X}")
                
            elif msb == DRUM_BANK_MSB:
                if lsb not in [PRESET_BANK_LSB, USER_BANK_LSB]:
                    raise ValueError(f"Invalid LSB for drum kit: {lsb:02X}")
                
            else:
                raise ValueError(f"Invalid bank MSB: {msb:02X}")
            
            # Send messages
            self.send_message([0xB0 | channel, BANK_SELECT_MSB, msb])
            self.send_message([0xB0 | channel, BANK_SELECT_LSB, lsb])
            self.send_message([0xC0 | channel, program])
            
            logging.debug(f"Sent bank select - MSB: {msb:02X}, LSB: {lsb:02X}, PC: {program:02X}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending bank select: {str(e)}")
            return False

    def send_program_change(self, program: int, channel: int = 0) -> bool:
        """Send program change message
        
        Args:
            program: Program number (0-127)
            channel: MIDI channel (0-15)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.send_message([0xC0 | channel, program])
            logging.debug(f"Sent program change: {program:02X}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending program change: {str(e)}")
            return False