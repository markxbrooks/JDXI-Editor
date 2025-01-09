import rtmidi
import logging

class MIDIPort:
    """Wrapper for rtmidi ports to store additional info"""
    def __init__(self, port, port_name):
        self.port = port
        self.port_name = port_name
        
    def send_message(self, message):
        """Send MIDI message"""
        try:
            # Send directly through rtmidi port
            self.port.send_message(message)
            logging.debug(f"Successfully sent MIDI message: {' '.join([hex(b)[2:].upper() for b in message])}")
            
            # Notify main window if available (for UI updates)
            if hasattr(self, 'main_window'):
                try:
                    self.main_window._send_midi_message(message)
                except Exception as e:
                    logging.debug(f"UI update failed: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Failed to send MIDI message: {str(e)}")
        
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
    def __init__(self, main_window=None):
        self.midi_out = None
        self.midi_in = None
        self.main_window = main_window  # Store reference to main window

    # Add constants for preset retrieval
    DIGITAL_PRESET_START = 0x10  # Starting address for digital presets
    PRESET_SIZE = 0x80          # Size of each preset in bytes

    # Add Pan constants
    PAN_LEFT = 0x00
    PAN_CENTER = 0x40
    PAN_RIGHT = 0x7F
    
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
    def open_input(port_name, main_window=None):
        """Open a MIDI input port by name"""
        try:
            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()
            
            if port_name in ports:
                port_num = ports.index(port_name)
                midi_in.open_port(port_num)
                port = MIDIPort(midi_in, port_name)
                port.main_window = main_window  # Set main window reference
                logging.info(f"Opened MIDI input port: {port_name}")
                return port
                
            midi_in.delete()
            logging.warning(f"MIDI input port not found: {port_name}")
            return None
            
        except Exception as e:
            logging.error(f"Error opening MIDI input port {port_name}: {str(e)}")
            return None
        
    @staticmethod
    def open_output(port_name, main_window=None):
        """Open a MIDI output port by name"""
        try:
            midi_out = rtmidi.MidiOut()
            ports = midi_out.get_ports()
            
            if port_name in ports:
                port_num = ports.index(port_name)
                midi_out.open_port(port_num)
                port = MIDIPort(midi_out, port_name)
                port.main_window = main_window  # Set main window reference
                logging.info(f"Opened MIDI output port: {port_name}")
                return port
                
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
        # F0 41 10 00 00 00 0E 12 <addr> <param> <val> <checksum> F7
        msg = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12]  # Added DT1 command (0x12)
        
        # Add address bytes
        msg.append(address)  # Base address
        msg.append(0x00)     # Bank MSB
        msg.append(partial if partial is not None else 0x00)  # Bank LSB
        msg.append(parameter)  # Parameter number
        
        # Add value
        msg.append(value)
        
        # Calculate checksum (Roland algorithm)
        checksum = 0
        for byte in msg[8:]:  # Start after SysEx header
            checksum = (checksum + byte) & 0x7F
        checksum = (128 - checksum) & 0x7F
        
        # Add checksum and end of message
        msg.append(checksum)
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

    def request_preset_data(self, synth_type, preset_number):
        """Request preset data from JD-Xi"""
        if not self.midi_out:
            logging.error("No MIDI output port set")
            return

        # Set up address based on synth type
        if synth_type == 'digital1':
            addr = [0x19, 0x02, preset_number, 0x00]
        elif synth_type == 'digital2':
            addr = [0x19, 0x03, preset_number, 0x00]
        elif synth_type == 'analog':
            addr = [0x19, 0x01, preset_number, 0x00]
        elif synth_type == 'drums':
            addr = [0x19, 0x04, preset_number, 0x00]  # Added drums address
        else:
            logging.error(f"Invalid synth type: {synth_type}")
            return

        # Create RQ1 message
        sysex = [
            0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E,  # Header
            0x11,  # Command ID (RQ1)
            *addr,  # Address
            0x00, 0x00, 0x40,  # Size
            0xF7   # End of SysEx
        ]
        
        self.midi_out.send_message(sysex)
        logging.debug(f"Requested preset data for {synth_type} #{preset_number}") 

    def send_pan(self, channel, value):
        """Send Pan (Panpot) control change message
        
        Args:
            channel (int): MIDI channel (0-15)
            value (int): Pan value (0=Left, 64=Center, 127=Right)
        """
        if not self.midi_out:
            return
            
        # Construct Control Change message for Pan (CC#10)
        status = 0xB0 | (channel & 0x0F)  # 0xBn where n is channel
        controller = 0x0A  # CC#10 for Pan
        value = max(0, min(127, value))  # Clamp value to 0-127
        
        message = [status, controller, value]
        self.midi_out.send_message(message)
        logging.debug(f"Sent Pan CC message - Channel: {channel}, Value: {value}") 

    def load_digital_preset(self, preset_number):
        """Load a digital preset from the JD-Xi's memory"""
        if not self.midi_out:
            logging.error("No MIDI output port set")
            return False
            
        try:
            # Initial setup messages
            setup_messages = [
                # First message: Set parameter 0x06 to 0x5F
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
                 0x18, 0x00, 0x20, 0x06, 0x5F, 0x63, 0xF7],
                
                # Second message: Set parameter 0x07 to 0x40
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
                 0x18, 0x00, 0x20, 0x07, 0x40, 0x01, 0xF7],
                
                # Third message: Set parameter 0x08 to 0x00
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
                 0x18, 0x00, 0x20, 0x08, 0x00, 0x40, 0xF7]
            ]
            
            # Send setup messages
            for msg in setup_messages:
                self.midi_out.send_message(msg)
                
            # Request messages for different sections
            request_messages = [
                # Common parameters
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11,
                 0x19, 0x01, 0x00, 0x00, 0x00, 0x00, 0x40, 0x26, 0xF7],
                
                # Part 1 parameters
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11,
                 0x19, 0x01, 0x20, 0x00, 0x00, 0x00, 0x3D, 0x09, 0xF7],
                
                # Part 2 parameters
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11,
                 0x19, 0x01, 0x21, 0x00, 0x00, 0x00, 0x3D, 0x08, 0xF7],
                
                # Part 3 parameters
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11,
                 0x19, 0x01, 0x22, 0x00, 0x00, 0x00, 0x3D, 0x07, 0xF7],
                
                # Effects parameters
                [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11,
                 0x19, 0x01, 0x50, 0x00, 0x00, 0x00, 0x25, 0x71, 0xF7]
            ]
            
            # Send request messages
            for msg in request_messages:
                self.midi_out.send_message(msg)
                logging.debug(f"Sent preset data request: {' '.join([hex(b)[2:].upper() for b in msg])}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error loading digital preset {preset_number}: {str(e)}")
            return False

    def handle_sysex_response(self, message):
        """Handle incoming SysEx response"""
        try:
            # Verify it's a Roland message
            if (len(message) < 8 or 
                message[0] != 0xF0 or  # SysEx start
                message[1] != 0x41 or  # Roland ID
                message[7] != 0x12):   # DT1 response
                return
                
            # Extract address and data
            addr = message[8:12]  # 4 bytes of address
            data = message[12:-2]  # Data excluding checksum and F7
            
            # Log the received data
            addr_str = ' '.join([hex(b)[2:].upper() for b in addr])
            logging.debug(f"Received SysEx data for address {addr_str}")
            
            response = {
                'address': addr,
                'data': data
            }
            
            # Parse the parameters
            params = self.parse_digital_preset_data(response)
            if params:
                logging.debug(f"Parsed parameters: {params}")
                return params
                
            return response
            
        except Exception as e:
            logging.error(f"Error handling SysEx response: {str(e)}")
            return None

    def parse_digital_preset_data(self, response):
        """Parse digital preset SysEx response data
        
        Args:
            response (dict): Response from handle_sysex_response
            
        Returns:
            dict: Parsed parameters or None if invalid
        """
        if not response or 'address' not in response or 'data' not in response:
            return None
            
        addr = response['address']
        data = response['data']
        
        # Common parameters (0x19, 0x01, 0x00, 0x00)
        if addr[0] == 0x19 and addr[1] == 0x01 and addr[2] == 0x00:
            return self._parse_common_parameters(data)
            
        # Part 1 parameters (0x19, 0x01, 0x20, 0x00)
        elif addr[0] == 0x19 and addr[1] == 0x01 and addr[2] == 0x20:
            return self._parse_part_parameters(data)
            
        # Part 2 parameters (0x19, 0x01, 0x21, 0x00)
        elif addr[0] == 0x19 and addr[1] == 0x01 and addr[2] == 0x21:
            return self._parse_part_parameters(data)
            
        # Part 3 parameters (0x19, 0x01, 0x22, 0x00)
        elif addr[0] == 0x19 and addr[1] == 0x01 and addr[2] == 0x22:
            return self._parse_part_parameters(data)
            
        # Effects parameters (0x19, 0x01, 0x50, 0x00)
        elif addr[0] == 0x19 and addr[1] == 0x01 and addr[2] == 0x50:
            return self._parse_effects_parameters(data)
            
        return None
        
    def _parse_common_parameters(self, data):
        """Parse common section parameters"""
        try:
            name_bytes = data[3:27]  # 24 bytes for name
            name = bytes(name_bytes).decode('ascii').strip('\x00')
            
            return {
                'name': name,
                'category': data[27],
                'key_shift': data[28] - 64,  # Convert from 0-127 to -64-63
                'tempo': data[29] + (data[30] << 7),  # Combine MSB/LSB
                'tempo_sync': bool(data[31]),
                'arp_style': data[32],
                'arp_beat': data[33],
                'arp_range': data[34],
                'arp_pattern': data[35]
            }
        except Exception as e:
            logging.error(f"Error parsing common parameters: {str(e)}")
            return None
            
    def _parse_part_parameters(self, data):
        """Parse digital synth part parameters"""
        try:
            return {
                # OSC 1
                'osc1_wave': data[0],
                'osc1_range': data[1] - 64,
                'osc1_fine': data[2] - 64,
                
                # OSC 2
                'osc2_wave': data[3],
                'osc2_range': data[4] - 64,
                'osc2_fine': data[5] - 64,
                
                # Filter
                'cutoff': data[6],
                'resonance': data[7],
                'key_follow': data[8] - 64,
                
                # Filter Envelope
                'filter_attack': data[9],
                'filter_decay': data[10],
                'filter_sustain': data[11],
                'filter_release': data[12],
                
                # Amp Envelope
                'amp_attack': data[13],
                'amp_decay': data[14],
                'amp_sustain': data[15],
                'amp_release': data[16],
                
                # Modulation
                'mod_depth': data[17],
                'mod_rate': data[19],
                
                # Common
                'volume': data[18],
                'pan': data[20] - 64,
                'portamento': data[21]
            }
        except Exception as e:
            logging.error(f"Error parsing part parameters: {str(e)}")
            return None
            
    def _parse_effects_parameters(self, data):
        """Parse effects section parameters"""
        try:
            return {
                'delay_type': data[0],
                'delay_time': data[1],
                'delay_feedback': data[2],
                'delay_level': data[3],
                
                'reverb_type': data[4],
                'reverb_time': data[5],
                'reverb_level': data[6]
            }
        except Exception as e:
            logging.error(f"Error parsing effects parameters: {str(e)}")
            return None 

    def send_message(self, message):
        """Send MIDI message"""
        if not self.midi_out:
            return
            
        try:
            self.midi_out.send_message(message)
            # Log to debug window if it exists
            if hasattr(self, 'main_window') and self.main_window.midi_message_debug:
                self.main_window.midi_message_debug.log_message(message, "→")
                # Use blink instead of flash
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
            logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper() for b in message])}")
        except Exception as e:
            logging.error(f"Failed to send MIDI message: {str(e)}")
            
    def handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI message"""
        # Log to debug window if it exists
        if hasattr(self, 'main_window') and self.main_window.midi_message_debug:
            self.main_window.midi_message_debug.log_message(message, "←") 