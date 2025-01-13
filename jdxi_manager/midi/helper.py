from typing import Optional, List, Union
import rtmidi
import logging

from PySide6.QtWidgets import QWidget

from jdxi_manager.midi.constants import (
    START_OF_SYSEX, END_OF_SYSEX,
    ROLAND_ID, DEVICE_ID, MODEL_ID,
    BANK_SELECT_MSB, BANK_SELECT_LSB,
    ANALOG_BANK_MSB, DIGITAL_BANK_MSB, DRUM_BANK_MSB,
    PRESET_BANK_LSB, PRESET_BANK_2_LSB, USER_BANK_LSB
)
from jdxi_manager.midi.messages import (
    AnalogToneMessage,
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message
)

class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize MIDI in/out ports
        
        Args:
            parent: Parent widget with optional MIDI indicators
        """
        self._midi_in = rtmidi.MidiIn()
        self._midi_out = rtmidi.MidiOut()
        self._current_in_port = None
        self._current_out_port = None
        self._callbacks = []
        self._parent = parent
        
    @property
    def midi_in(self) -> rtmidi.MidiIn:
        """Get MIDI input object"""
        return self._midi_in
        
    @property
    def midi_out(self) -> rtmidi.MidiOut:
        """Get MIDI output object"""
        return self._midi_out
        
    def open_input(self, port_name: str) -> bool:
        """Alias for open_input_port for backwards compatibility"""
        return self.open_input_port(port_name)
        
    def open_output(self, port_name: str) -> bool:
        """Alias for open_output_port for backwards compatibility"""
        return self.open_output_port(port_name)

    def open_input_port(self, port_name: str) -> bool:
        """Open MIDI input port
        
        Args:
            port_name: Name of port to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Close existing port
            if self._current_in_port:
                self._midi_in.close_port()
                
            # Find port number
            ports = self._midi_in.get_ports()
            if port_name not in ports:
                logging.error(f"MIDI input port not found: {port_name}")
                return False
                
            port_num = ports.index(port_name)
            
            # Open port
            self._midi_in.open_port(port_num)
            self._current_in_port = port_name
            
            # Set callback if any registered
            if self._callbacks:
                self._midi_in.set_callback(self._midi_callback)
                
            logging.info(f"Opened MIDI input port: {port_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")
            return False

    def open_output_port(self, port_name: str) -> bool:
        """Open MIDI output port
        
        Args:
            port_name: Name of port to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Close existing port
            if self._current_out_port:
                self._midi_out.close_port()
                
            # Find port number
            ports = self._midi_out.get_ports()
            if port_name not in ports:
                logging.error(f"MIDI output port not found: {port_name}")
                return False
                
            port_num = ports.index(port_name)
            
            # Open port
            self._midi_out.open_port(port_num)
            self._current_out_port = port_name
            
            logging.info(f"Opened MIDI output port: {port_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return False

    def close_ports(self):
        """Close all MIDI ports"""
        try:
            if self._current_in_port:
                self._midi_in.close_port()
                self._current_in_port = None
                
            if self._current_out_port:
                self._midi_out.close_port()
                self._current_out_port = None
                
            logging.info("Closed all MIDI ports")
            
        except Exception as e:
            logging.error(f"Error closing MIDI ports: {str(e)}")

    @property
    def current_in_port(self) -> Optional[str]:
        """Get current input port name"""
        return self._current_in_port
        
    @property
    def current_out_port(self) -> Optional[str]:
        """Get current output port name"""
        return self._current_out_port
        
    @property
    def is_input_open(self) -> bool:
        """Check if input port is open"""
        return self._midi_in and self._midi_in.is_port_open()
        
    @property
    def is_output_open(self) -> bool:
        """Check if output port is open"""
        return self._midi_out and self._midi_out.is_port_open()

    def get_input_ports(self) -> List[str]:
        """Get available MIDI input ports"""
        return self._midi_in.get_ports()
        
    def get_output_ports(self) -> List[str]:
        """Get available MIDI output ports"""
        return self._midi_out.get_ports()

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
        """Send parameter change message
        
        Args:
            area: Memory area (e.g. ANALOG_SYNTH_AREA)
            part: Part number
            group: Parameter group
            param: Parameter number
            value: Parameter value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = AnalogToneMessage(
                area=area,
                part=part,
                group=group,
                param=param,
                value=value
            )
            
            # Convert to SysEx
            sysex = msg.to_sysex()
            
            # Calculate checksum
            checksum = msg.calculate_checksum(sysex)
            sysex[-2] = checksum
            
            # Send message
            return self.send_message(sysex)
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            return False

    def send_bank_select(self, msb: int, lsb: int, program: int, channel: int = 0) -> bool:
        """Send bank select and program change messages
        
        Args:
            msb: Bank select MSB value (94=Analog, 95=Digital, 86=Drum)
            lsb: Bank select LSB value (0=Preset1, 1=Preset2, 16=User)
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

            if msb not in [94, 95, 86]:
                raise ValueError(f"Error: msb {msb} not one of 95, 95, 86")

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
                valid_msb = [ANALOG_BANK_MSB, DIGITAL_BANK_MSB, DRUM_BANK_MSB]
                raise ValueError(f"Invalid bank MSB: {msb:02X}, must be one of {[f'{x:02X}' for x in valid_msb]}")
            
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

    def request_data(self, area: int, part: int, address: list, size: list):
        """Request data from device using RQ1 message
        
        Args:
            area: Memory area (e.g. ANALOG_SYNTH_AREA)
            part: Part number
            address: Starting address bytes [msb, lsb]
            size: Size of data to request [msb, lsb]
        """
        # Create RQ1 message
        msg = [
            0xF0,           # SysEx start
            0x41,           # Roland ID
            0x10,           # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID
            0x11,           # RQ1 command
            area,           # Memory area
            part,           # Part number
            *address,       # Starting address
            *size,         # Data size
            0xF7            # SysEx end
        ]
        
        # Calculate checksum
        checksum = 0
        for byte in msg[8:-2]:  # From area to size
            checksum += byte
        checksum = (128 - (checksum % 128)) & 0x7F
        
        # Insert checksum before end
        msg.insert(-1, checksum)
        
        # Send message
        self.send_message(bytes(msg))

    def send_message(self, message: Union[bytes, List[int]]) -> bool:
        """Send MIDI message
        
        Args:
            message: MIDI message as bytes or list of integers
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._midi_out or not self._midi_out.is_port_open():
                logging.error("No MIDI output port open")
                return False
                
            # Convert to list if needed
            if isinstance(message, bytes):
                message = list(message)
                
            # Send message
            self._midi_out.send_message(message)
            
            # Trigger MIDI out indicator if available
            if self._parent and hasattr(self._parent, 'midi_out_indicator'):
                self._parent.midi_out_indicator.blink()
                
            return True
            
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
            return False

    def _midi_callback(self, message, timestamp):
        """Internal callback that distributes messages to all registered callbacks"""
        try:
            # Call all registered callbacks
            for callback in self._callbacks:
                callback(message[0], timestamp)  # message[0] contains the actual MIDI data
                
            # Trigger MIDI in indicator if available
            if self._parent and hasattr(self._parent, 'midi_in_indicator'):
                self._parent.midi_in_indicator.blink()
                
        except Exception as e:
            logging.error(f"Error in MIDI callback: {str(e)}")

    def register_callback(self, callback):
        """Register a callback function for MIDI messages"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            logging.debug(f"Registered MIDI callback: {callback.__qualname__}")

    def unregister_callback(self, callback):
        """Remove a callback function"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            logging.debug(f"Unregistered MIDI callback: {callback.__qualname__}")