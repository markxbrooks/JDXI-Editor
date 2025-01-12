import rtmidi
import logging
from typing import Optional, List, Union

from PySide6.QtWidgets import QWidget

from jdxi_manager.midi.constants import START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2, JD_XI_ID, \
    END_OF_SYSEX
from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)
from jdxi_manager.midi.sysex import DT1_COMMAND_12


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
        
        # Initialize bank select values
        self._last_bank_msb = 0
        self._last_bank_lsb = 0
        self._last_channel = 0

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
            # Trigger MIDI in indicator
            if hasattr(self.parent, 'midi_in_indicator'):
                self.parent.midi_in_indicator.blink()
                
            # Process message...
            
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

    def send_message(self, message):
        """Send a MIDI message"""
        try:
            if self.midi_out and self.midi_out.is_port_open():
                # Debug print the actual bytes being sent
                print(f"Raw MIDI bytes: {[hex(b) for b in message]}")
                logging.debug(f"Sending MIDI message: {' '.join([f'{b:02X}' for b in message])}")
                
                # Decode and log the message
                decoded = self.decode_message(message)
                logging.debug("Decoded message:\n" + decoded)
                
                # Send to log viewer if available and visible
                if (hasattr(self.parent, 'log_viewer') and 
                    self.parent.log_viewer and 
                    self.parent.log_viewer.isVisible()):
                    self.parent.log_viewer.append_message(decoded, decoded=True)
                
                # Send the message
                self.midi_out.send_message(message)
                
                # Trigger MIDI out indicator
                if hasattr(self.parent, 'midi_out_indicator'):
                    self.parent.midi_out_indicator.blink()
                
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")

    def send_bank_select(self, msb, lsb, channel):
        """Send bank select messages"""
        try:
            if self.current_out_port:
                # Send Bank Select MSB (CC 0)
                self.send_message([0xB0 | channel, 0x00, msb])
                # Send Bank Select LSB (CC 32)
                self.send_message([0xB0 | channel, 0x20, lsb])
                logging.debug(f"Sent bank select MSB:{msb:02X} LSB:{lsb:02X} on channel {channel}")
        except Exception as e:
            logging.error(f"Error sending bank select: {str(e)}")

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

    def send_test_message(self):
        """Send a test MIDI message to verify connection"""
        try:
            # Send a simple note on/off message on channel 1
            if self.midi_out and self.midi_out.is_port_open():
                # Note On - Channel 1, Note C4 (60), Velocity 100
                self.send_message([0x90, 60, 100])
                logging.debug("Sent test Note On message: 90 3C 64")
                
                # Small delay
                import time
                time.sleep(0.1)
                
                # Note Off - Channel 1, Note C4 (60), Velocity 0
                self.send_message([0x90, 60, 0])
                logging.debug("Sent test Note Off message: 90 3C 00")
                
                return True
            else:
                logging.warning("No MIDI output port available or port is closed")
                return False
            
        except Exception as e:
            logging.error(f"Error sending test message: {str(e)}")
            return False

    def set_input_port(self, port_name: str) -> bool:
        """Set MIDI input port"""
        try:
            # Set port...
            success = super().set_input_port(port_name)
            
            # Update indicator
            if hasattr(self.parent, 'midi_in_indicator'):
                self.parent.midi_in_indicator.set_connected(success)
            
            return success
            
        except Exception as e:
            logging.error(f"Error setting input port: {str(e)}")
            return False

    def set_output_port(self, port_name: str) -> bool:
        """Set MIDI output port"""
        try:
            # Set port...
            success = super().set_output_port(port_name)
            
            # Update indicator
            if hasattr(self.parent, 'midi_out_indicator'):
                self.parent.midi_out_indicator.set_connected(success)
            
            return success
            
        except Exception as e:
            logging.error(f"Error setting output port: {str(e)}")
            return False

    def send_parameter(self, area: int, part: int, group: int, param: int, value: int):
        """Send parameter change via SysEx
        
        Args:
            area: Memory area (e.g. ANALOG_SYNTH_AREA)
            part: Part number
            group: Parameter group
            param: Parameter address
            value: Parameter value
        """
        try:
            if self.midi_out and self.midi_out.is_port_open():
                # Construct SysEx message
                message = [
                    START_OF_SYSEX,    # F0
                    ROLAND_ID,         # 41 Roland
                    DEVICE_ID,         # 10 Device ID
                    MODEL_ID_1,        # 00 Model ID MSB
                    MODEL_ID_2,        # 00 Model ID LSB
                    JD_XI_ID,          # 0E JD-Xi ID
                    DT1_COMMAND_12,    # 12 DT1 Command
                    area,              # Memory area
                    part,              # Part number
                    group,             # Parameter group
                    param,             # Parameter address
                    value,             # Parameter value
                    0x00,             # Checksum placeholder
                    END_OF_SYSEX      # F7
                ]
                
                # Calculate checksum
                checksum = self._calculate_checksum(message[7:-2])  # From area to value
                message[-2] = checksum
                
                # Send message
                self.send_message(message)
                
                logging.debug(
                    f"Sent parameter change: Area:{area:02X} Part:{part:02X} "
                    f"Group:{group:02X} Param:{param:02X} Value:{value:02X}"
                )
                
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            raise

    def _calculate_checksum(self, data: List[int]) -> int:
        """Calculate Roland checksum for SysEx message
        
        Args:
            data: List of bytes to checksum (excluding F0, manufacturer ID, etc)
            
        Returns:
            Checksum byte
        """
        checksum = 0
        for byte in data:
            checksum = (checksum + byte) & 0x7F
        return (128 - checksum) & 0x7F

    def decode_message(self, message: List[int]) -> str:
        """Decode MIDI message into human-readable format"""
        try:
            if not message:
                return "Empty message"
            
            # Regular MIDI messages
            if message[0] < 0xF0:
                status = message[0] & 0xF0
                channel = message[0] & 0x0F
                
                # Note names for better readability
                NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                def note_name(note_num):
                    octave = (note_num // 12) - 1
                    note = NOTE_NAMES[note_num % 12]
                    return f"{note}{octave} ({note_num})"
                
                # CC names for common controllers
                CC_NAMES = {
                    0: "Bank Select MSB",
                    1: "Modulation",
                    7: "Volume",
                    10: "Pan",
                    11: "Expression",
                    32: "Bank Select LSB",
                    64: "Sustain",
                    65: "Portamento",
                    71: "Resonance",
                    74: "Cutoff",
                    91: "Reverb",
                    93: "Chorus"
                }
                
                if status == 0x80:
                    return f"Note Off - Channel {channel+1}, Note {note_name(message[1])}, Velocity {message[2]}"
                elif status == 0x90:
                    if message[2] == 0:
                        return f"Note Off - Channel {channel+1}, Note {note_name(message[1])} (zero velocity)"
                    return f"Note On - Channel {channel+1}, Note {note_name(message[1])}, Velocity {message[2]}"
                elif status == 0xB0:
                    cc_name = CC_NAMES.get(message[1], f"CC {message[1]}")
                    if message[1] in [0, 32]:  # Bank Select MSB/LSB
                        # Store bank select values for program changes
                        if message[1] == 0:  # MSB
                            self._last_bank_msb = message[2]
                        else:  # LSB
                            self._last_bank_lsb = message[2]
                        self._last_channel = channel + 1  # Store channel for program changes
                    return f"Control Change - Channel {channel+1}, {cc_name}, Value {message[2]}"
                elif status == 0xC0:
                    preset_name = "Unknown"
                    # Only use stored bank values if they're for the same channel
                    if channel + 1 == self._last_channel:
                        preset_name = self.get_preset_name(
                            channel + 1,
                            self._last_bank_msb,
                            self._last_bank_lsb,
                            message[1]
                        )
                        # Add synth type info
                        synth_type = "Unknown"
                        if channel + 1 == 1:
                            synth_type = "Analog Synth"
                        elif channel + 1 == 2:
                            synth_type = "Digital Synth 1"
                        elif channel + 1 == 3:
                            synth_type = "Digital Synth 2"
                        elif channel + 1 == 10:
                            synth_type = "Drums"
                        return (f"Program Change - Channel {channel+1} ({synth_type})\n"
                               f"Bank MSB: {self._last_bank_msb}, LSB: {self._last_bank_lsb}\n"
                               f"Program: {message[1]}\n"
                               f"Preset: {preset_name}")
                    else:
                        return f"Program Change - Channel {channel+1}, Program {message[1]}"
                elif status == 0xE0:
                    value = (message[2] << 7) + message[1]
                    return f"Pitch Bend - Channel {channel+1}, Value {value} ({value-8192:+d})"
                
            # SysEx messages
            elif message[0] == 0xF0:
                if len(message) < 3:
                    return "Incomplete SysEx message"
                
                parts = ["SysEx Message:"]
                
                # Check if it's a Roland message
                if message[1] == 0x41:  # Roland ID
                    parts.append("Manufacturer: Roland")
                    parts.append(f"Device ID: {message[2]:02X}")
                    
                    # Check if it's a JD-Xi message
                    if len(message) > 6 and message[5] == 0x0E:  # JD-Xi ID
                        parts.append("Device: JD-Xi")
                        
                        # Command type
                        if message[6] == 0x12:
                            parts.append("Command: DT1 (Parameter Write)")
                        elif message[6] == 0x11:
                            parts.append("Command: RQ1 (Parameter Request)")
                            
                        # Memory area
                        if len(message) > 7:
                            area_names = {
                                0x19: "Digital Synth 1",
                                0x1A: "Digital Synth 2",
                                0x18: "Analog Synth",
                                0x17: "Drum Kit",
                                0x16: "Effects",
                                0x15: "Arpeggiator",
                                0x14: "Vocal FX"
                            }
                            area = message[7]
                            area_name = area_names.get(area, f"Unknown Area ({area:02X})")
                            parts.append(f"Area: {area_name}")
                            
                            # Part/Parameter info
                            if len(message) > 11:
                                parts.append(f"Part: {message[8]:02X}")
                                parts.append(f"Parameter Group: {message[9]:02X}")
                                
                                # Try to get parameter name based on area
                                param_name = "Unknown"
                                if area in [0x19, 0x1A]:  # Digital
                                    from jdxi_manager.data.digital import DigitalParameter
                                    try:
                                        param = DigitalParameter(message[10])
                                        param_name = param.name
                                    except ValueError:
                                        param_name = f"Unknown Digital ({message[10]:02X})"
                                elif area == 0x18:  # Analog
                                    from jdxi_manager.data.analog import AnalogParameter
                                    try:
                                        param = AnalogParameter(message[10])
                                        param_name = param.name
                                    except ValueError:
                                        param_name = f"Unknown Analog ({message[10]:02X})"
                                    
                                parts.append(f"Parameter: {param_name} ({message[10]:02X})")
                                parts.append(f"Value: {message[11]:02X}")
                                
                                # Add checksum verification
                                if len(message) > 12:
                                    calc_checksum = self._calculate_checksum(message[7:-2])
                                    checksum_valid = calc_checksum == message[-2]
                                    parts.append(f"Checksum: {message[-2]:02X} ({'Valid' if checksum_valid else 'Invalid'})")
                
                else:
                    # Generic SysEx decode
                    parts.append(f"Manufacturer ID: {message[1]:02X}")
                    parts.append("Data: " + " ".join([f"{b:02X}" for b in message[2:-1]]))
                    
                return "\n".join(parts)
                
            return "Unknown message type: " + " ".join([f"{b:02X}" for b in message])
            
        except Exception as e:
            logging.error(f"Error decoding MIDI message: {str(e)}")
            return f"Error decoding message: {str(e)}"

    def get_preset_name(self, channel: int, bank_msb: int, bank_lsb: int, program: int) -> str:
        """Get preset name from channel and program numbers
        
        Args:
            channel: MIDI channel (1-16)
            bank_msb: Bank Select MSB value
            bank_lsb: Bank Select LSB value
            program: Program number (0-127)
            
        Returns:
            Preset name or "Unknown Preset"
        """
        try:
            from jdxi_manager.data.analog import AN_PRESETS
            from jdxi_manager.data.digital import DIGITAL_PRESETS
            from jdxi_manager.data.drums import DRUM_PRESETS
            
            # Map channel to synth type
            if channel == 1:  # Analog Synth
                preset_list = AN_PRESETS
                preset_index = (bank_lsb * 7) + program
            elif channel in [2, 3]:  # Digital Synth 1 & 2
                preset_list = DIGITAL_PRESETS
                preset_index = (bank_lsb * 16) + program
            elif channel == 10:  # Drums
                preset_list = DRUM_PRESETS
                preset_index = (bank_lsb * 16) + program
            else:
                return "Unknown Channel"
            
            # Get preset name if index is valid
            if 0 <= preset_index < len(preset_list):
                return preset_list[preset_index]
            else:
                return f"Invalid Preset Index ({preset_index})"
            
        except Exception as e:
            logging.error(f"Error getting preset name: {str(e)}")
            return "Error Getting Preset Name"