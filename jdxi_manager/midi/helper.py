import rtmidi
import logging
from typing import Optional, List, Union

from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)

class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, parent=None):
        """Initialize MIDI in/out ports
        
        Args:
            parent: Parent window for MIDI indicators
        """
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.current_in_port = None
        self.current_out_port = None
        self.parent = parent
        
    def get_input_ports(self) -> List[str]:
        """Get list of available MIDI input ports"""
        return self.midi_in.get_ports()
        
    def get_output_ports(self) -> List[str]:
        """Get list of available MIDI output ports"""
        return self.midi_out.get_ports()
        
    def open_input_port(self, port_name: str) -> bool:
        """Open MIDI input port by name"""
        try:
            ports = self.get_input_ports()
            if port_name in ports:
                port_num = ports.index(port_name)
                self.midi_in.open_port(port_num)
                self.current_in_port = port_name
                
                # Set callback for identity response
                self.midi_in.set_callback(self._handle_midi_message)
                
                logging.info(f"Opened MIDI input port: {port_name}")
                return True
                
        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")
        return False

    def _handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI messages"""
        try:
            data = message[0]
            
            # Check for identity response
            if (len(data) > 8 and
                data[0] == START_OF_SYSEX and
                data[1] == ROLAND_ID and
                data[4:8] == bytes([MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID])):
                logging.info("JD-Xi identity confirmed")
                
            # Forward message to parent window
            if self.parent:
                self.parent._handle_midi_message(message, timestamp)
                
        except Exception as e:
            logging.error(f"Error handling MIDI message: {str(e)}")
            
    def open_output_port(self, port_name: str) -> bool:
        """Open MIDI output port by name
        
        Args:
            port_name: Name of port to open
            
        Returns:
            True if port opened successfully
        """
        try:
            ports = self.get_output_ports()
            if port_name in ports:
                port_num = ports.index(port_name)
                
                # Close existing port if open
                if self.midi_out.is_port_open():
                    self.midi_out.close_port()
                    
                # Open new port
                self.midi_out.open_port(port_num)
                self.current_out_port = port_name
                logging.info(f"Opened MIDI output port: {port_name}")
                return True
            else:
                logging.error(f"MIDI output port not found: {port_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return False
            
    def send_message(self, msg: Union[bytes, List[int]]) -> bool:
        """Send MIDI message
        
        Args:
            msg: MIDI message as bytes or list of integers
            
        Returns:
            True if message sent successfully
        """
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
            
            # Log the sent message for debugging
            msg_hex = ' '.join([f'{b:02X}' for b in msg])
            logging.debug(f"Sent MIDI message: {msg_hex}")
            
            # Blink MIDI out indicator if available
            if self.parent and hasattr(self.parent, 'midi_out_indicator'):
                self.parent.midi_out_indicator.blink()
                
            return True
            
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
            return False
            
    def close(self):
        """Close MIDI ports"""
        if self.midi_in and self.midi_in.is_port_open():
            self.midi_in.close_port()
        if self.midi_out and self.midi_out.is_port_open():
            self.midi_out.close_port()
        logging.info("Closed MIDI ports")