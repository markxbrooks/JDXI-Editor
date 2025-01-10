import rtmidi
import logging
import time
from jdxi_manager.midi.messages import (
    create_parameter_message, 
    create_sysex_message, 
    create_patch_load_message
)


class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, main_window=None):
        """Initialize MIDI helper"""
        self.midi_in = None
        self.midi_out = None
        self.main_window = main_window
        self._last_message = None
        self._last_message_time = 0
        
    @staticmethod
    def get_input_ports():
        """List available MIDI input ports"""
        try:
            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()
            midi_in.delete()
            return ports
        except Exception as e:
            logging.error(f"Error getting MIDI input ports: {str(e)}")
            return []
            
    @staticmethod
    def get_output_ports():
        """List available MIDI output ports"""
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            midi_out.delete()
            return ports
        except Exception as e:
            logging.error(f"Error getting MIDI output ports: {str(e)}")
            return []
    
    @staticmethod
    def list_ports():
        """List all available MIDI ports"""
        in_ports = MIDIHelper.get_input_ports()
        out_ports = MIDIHelper.get_output_ports()
        return in_ports, out_ports
        
    @staticmethod
    def open_input(port_name, main_window=None):
        """Open MIDI input port by name"""
        try:
            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()
            
            if port_name in ports:
                port_num = ports.index(port_name)
                midi_in.open_port(port_num)
                midi_in.ignore_types(sysex=False)
                logging.info(f"Opened MIDI input port: {port_name}")
                return midi_in
            else:
                midi_in.delete()
                logging.warning(f"MIDI input port not found: {port_name}")
                return None
                
        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")
            return None
            
    @staticmethod
    def open_output(port_name, main_window=None):
        """Open MIDI output port by name"""
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            
            if port_name in ports:
                port_num = ports.index(port_name)
                midi_out.open_port(port_num)
                logging.info(f"Opened MIDI output port: {port_name}")
                return midi_out
            else:
                midi_out.delete()
                logging.warning(f"MIDI output port not found: {port_name}")
                return None
                
        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return None

    def send_message(self, message):
        """Send MIDI message"""
        if self.midi_out:
            try:
                self.midi_out.send_message(message)
                
                # Set indicator active
                if self.main_window and hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.set_active()
                    
            except Exception as e:
                logging.error(f"Error sending MIDI message: {str(e)}")
            
    def handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI message"""
        # Forward to main window if available
        if self.main_window and hasattr(self.main_window, '_handle_midi_message'):
            self.main_window._handle_midi_message(message, timestamp)


if __name__ == '__main__':
    # Add any test code here if needed
    pass 