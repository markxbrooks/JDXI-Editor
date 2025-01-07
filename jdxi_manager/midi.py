import rtmidi
import logging

class MIDIPort:
    """Wrapper for rtmidi ports to store additional info"""
    def __init__(self, port, port_name):
        self.port = port
        self.port_name = port_name
        
    def send_message(self, message):
        """Send MIDI message"""
        self.port.send_message(message)
        
    def set_callback(self, callback):
        """Set callback for incoming MIDI messages"""
        if isinstance(self.port, rtmidi.MidiIn):
            self.port.set_callback(callback)
            logging.debug(f"Set MIDI input callback for {self.port_name}")
        else:
            logging.warning("Attempted to set callback on non-input port")
        
    def close(self):
        """Close the port"""
        if isinstance(self.port, rtmidi.MidiIn):
            self.port.cancel_callback()
        self.port.close_port()
        self.port.delete()
        logging.debug(f"Closed MIDI port {self.port_name}")

class MIDIHelper:
    @staticmethod
    def get_input_ports():
        """Get list of available MIDI input ports"""
        midi_in = rtmidi.MidiIn()
        ports = midi_in.get_ports()
        midi_in.delete()
        return ports or ["No MIDI inputs available"]
        
    @staticmethod
    def get_output_ports():
        """Get list of available MIDI output ports"""
        midi_out = rtmidi.MidiOut()
        ports = midi_out.get_ports()
        midi_out.delete()
        return ports or ["No MIDI outputs available"]
        
    @staticmethod
    def open_input(port_name):
        """Open a MIDI input port by name"""
        try:
            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()
            
            if port_name in ports:
                port_num = ports.index(port_name)
                midi_in.open_port(port_num)
                logging.info(f"Opened MIDI input port: {port_name}")
                return MIDIPort(midi_in, port_name)
                
            midi_in.delete()
            logging.warning(f"MIDI input port not found: {port_name}")
            return None
            
        except Exception as e:
            logging.error(f"Error opening MIDI input port {port_name}: {str(e)}")
            return None
        
    @staticmethod
    def open_output(port_name):
        """Open a MIDI output port by name"""
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            
            if port_name in ports:
                port_num = ports.index(port_name)
                midi_out.open_port(port_num)
                logging.info(f"Opened MIDI output port: {port_name}")
                return MIDIPort(midi_out, port_name)
                
            midi_out.delete()
            logging.warning(f"MIDI output port not found: {port_name}")
            return None
            
        except Exception as e:
            logging.error(f"Error opening MIDI output port {port_name}: {str(e)}")
            return None
        
    @staticmethod
    def create_identity_request():
        """Create MIDI identity request message"""
        # Universal System Exclusive
        # F0 7E 7F 06 01 F7 (Device Identity Request)
        return [0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7]
        
    @staticmethod
    def create_parameter_message(address, partial, parameter, value):
        """Create Roland parameter change message"""
        # Roland System Exclusive
        # F0 41 10 00 00 00 0E <addr> <param> <val> F7
        msg = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]
        
        # Add address bytes
        msg.append(address)  # Base address
        msg.append(0x00)     # Bank MSB
        msg.append(partial if partial is not None else 0x00)  # Bank LSB
        msg.append(parameter)  # Parameter number
        
        # Add value and end of message
        msg.append(value)
        msg.append(0xF7)
        
        return msg
        
    @staticmethod
    def create_sysex_message(address, data):
        """Create Roland System Exclusive message"""
        # F0 41 10 00 00 00 0E <addr> <data> F7
        msg = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]
        msg.extend(address)
        msg.extend(data)
        msg.append(0xF7)
        return msg 