import rtmidi
import logging

class MIDIHelper:
    """Helper class for MIDI operations"""
    
    def __init__(self, main_window=None):
        """Initialize MIDI helper"""
        self.midi_in = None
        self.midi_out = None
        self.main_window = main_window
        
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
            
    @staticmethod
    def create_sysex_message(address, data):
        """Create Roland SysEx message"""
        # Roland SysEx format:
        # F0 41 10 00 00 00 0E 12 [address] [data] [checksum] F7
        
        # Calculate checksum
        checksum = sum(address) + sum(data)
        checksum = (0x80 - (checksum & 0x7F)) & 0x7F
        
        # Construct message
        msg = [
            0xF0,   # Start of SysEx
            0x41,   # Roland ID
            0x10,   # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID
            0x12,   # Command ID (DT1)
        ]
        msg.extend(address)  # Add address bytes
        msg.extend(data)     # Add data bytes
        msg.append(checksum) # Add checksum
        msg.append(0xF7)     # End of SysEx
        
        return msg
        
    @staticmethod
    def create_parameter_message(address1, address2, parameter, value):
        """Create parameter change message"""
        address = bytes([address1, address2, 0x00, parameter])
        data = bytes([value])
        return MIDIHelper.create_sysex_message(address, data)
        
    def send_message(self, message):
        """Send MIDI message and blink indicator"""
        if self.midi_out:
            self.midi_out.send_message(message)
            # Blink the output indicator
            if self.main_window and hasattr(self.main_window, 'midi_out_indicator'):
                self.main_window.midi_out_indicator.blink()
                
    def handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI message"""
        # Forward to main window if available
        if self.main_window and hasattr(self.main_window, '_handle_midi_message'):
            self.main_window._handle_midi_message(message, timestamp) 
        
    @staticmethod
    def create_patch_load_message(patch_number):
        """Create MIDI message to load a patch"""
        return [0xC0, patch_number - 1]  # Convert 1-based to 0-based
        
    @staticmethod
    def create_patch_save_message(patch_number):
        """Create MIDI message to save current settings as a patch"""
        # Calculate checksum
        checksum = (0x19 + 0x01 + 0x00 + 0x20 + (patch_number - 1))
        checksum = (0x80 - (checksum & 0x7F)) & 0x7F
        
        return [
            0xF0,   # Start of SysEx
            0x41,   # Roland ID
            0x10,   # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID
            0x12,   # Command ID (DT1)
            0x19,   # Address 1
            0x01,   # Address 2
            0x00,   # Address 3
            0x20,   # Address 4 (Save command)
            patch_number - 1,  # Parameter value (0-based patch number)
            checksum,  # Checksum
            0xF7    # End of SysEx
        ] 
        
    @staticmethod
    def create_patch_name_message(patch_number, name):
        """Create MIDI message to set patch name"""
        # Pad name to 12 chars with spaces
        name = name.ljust(12)[:12].upper()
        
        # Convert name to bytes
        name_bytes = [ord(c) for c in name]
        
        # Calculate address
        base_addr = 0x19  # Patch memory
        patch_offset = (patch_number - 1) * 0x20  # Each patch is 32 bytes
        name_addr = [base_addr, patch_offset & 0x7F, (patch_offset >> 7) & 0x7F, 0x00]
        
        # Calculate checksum
        checksum = sum(name_addr) + sum(name_bytes)
        checksum = (0x80 - (checksum & 0x7F)) & 0x7F
        
        return [
            0xF0,   # Start of SysEx
            0x41,   # Roland ID
            0x10,   # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID
            0x12,   # Command ID (DT1)
        ] + name_addr + name_bytes + [checksum, 0xF7] 
        
    @staticmethod
    def create_identity_request():
        """Create MIDI identity request message"""
        # Roland identity request format:
        # F0 7E 10 06 01 F7
        return [
            0xF0,   # Start of SysEx
            0x7E,   # Universal Non-realtime
            0x10,   # Device ID
            0x06,   # Identity Request
            0x01,   # Identity Request command
            0xF7    # End of SysEx
        ]
        
    @staticmethod
    def create_roland_identity_request():
        """Create Roland-specific identity request"""
        # Roland-specific identity request:
        # F0 41 10 00 00 00 0E 11 F7
        return [
            0xF0,   # Start of SysEx
            0x41,   # Roland ID
            0x10,   # Device ID
            0x00, 0x00, 0x00, 0x0E,  # Model ID (JD-Xi)
            0x11,   # Identity Request
            0xF7    # End of SysEx
        ] 