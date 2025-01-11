from .constants import *  # Import all constants
from dataclasses import dataclass
from typing import List

@dataclass
class JDXiSysEx:
    """JD-Xi SysEx message structure"""
    START_OF_SYSEX: int = 0xF0
    ROLAND_ID: int = 0x41
    DEVICE_ID: int = 0x10
    MODEL_ID_1: int = 0x00
    MODEL_ID_2: int = 0x00
    MODEL_ID: int = 0x00
    JD_XI_ID: int = 0x0E
    COMMAND: int = 0x12  # DT1 command
    area: int = 0x19     # Digital Synth 1
    part: int = 0x01     # Part 1
    group: int = 0x20    # Partial parameters
    param: int = 0x00    # Parameter number
    value: int = 0x00    # Parameter value
    END_OF_SYSEX: int = 0xF7

    def to_bytes(self) -> bytes:
        """Convert to bytes message"""
        msg = [
            self.START_OF_SYSEX,
            self.ROLAND_ID,
            self.DEVICE_ID,
            self.MODEL_ID_1, self.MODEL_ID_2, self.MODEL_ID, self.JD_XI_ID,
            self.COMMAND,
            self.area,
            self.part,
            self.group,
            self.param,
            self.value
        ]
        
        # Calculate checksum (sum from area to value)
        checksum = sum(msg[8:]) & 0x7F
        checksum = (128 - checksum) & 0x7F
        
        msg.extend([checksum, self.END_OF_SYSEX])
        return bytes(msg)

    @classmethod
    def create_parameter_message(cls, area: int, part: int, group: int, param: int, value: int) -> bytes:
        """Create parameter change message"""
        msg = cls(
            area=area,
            part=part,
            group=group,
            param=param,
            value=value
        )
        return msg.to_bytes()

def create_sysex_message(address, data):
    """Create Roland SysEx message
    
    Args:
        address (bytes): Address bytes
        data (bytes): Data bytes
        
    Returns:
        list: Complete MIDI message
    """
    # Calculate checksum
    checksum = sum(address) + sum(data)
    checksum = (0x80 - (checksum & 0x7F)) & 0x7F
    
    # Construct message using named constants
    msg = [
        START_OF_SYSEX,        # Start of SysEx
        ROLAND_ID,        # Roland ID
        DEVICE_ID,      # Device ID
        MODEL_ID_1,    # Device ID 1
        MODEL_ID_2,    # Device ID 2
        MODEL_ID,       # Model ID
        JD_XI_ID,      # JD-Xi ID
        DT1_COMMAND_12  # Command ID (DT1)
    ]
    msg.extend(address)  # Add address bytes
    msg.extend(data)     # Add data bytes
    msg.append(checksum) # Add checksum
    msg.append(END_OF_SYSEX)  # End of SysEx
    
    return msg

def create_patch_load_message(patch_number):
    """Create MIDI message to load a patch
    
    Args:
        patch_number (int): Patch number (1-based)
        
    Returns:
        list: MIDI program change message
    """
    return [0xC0, patch_number - 1]  # Convert 1-based to 0-based

def create_patch_save_message(patch_number):
    """Create MIDI message to save current settings as a patch
    
    Args:
        patch_number (int): Patch number (1-based)
        
    Returns:
        list: Complete MIDI message
    """
    # Create address bytes
    address = bytes([
        0x19,   # Digital synth
        0x01,   # Part 1
        0x00,   # Group
        0x20    # Save command
    ])
    
    # Create data byte (patch number)
    data = bytes([patch_number - 1])  # Convert to 0-based
    
    return create_sysex_message(address, data) 

def create_program_change_message(program_number: int) -> bytes:
    """Create program change SysEx message"""
    # Adjust program number to 0-based index
    program = (program_number - 1) & 0x7F
    
    msg = [
        START_OF_SYSEX,
        ROLAND_ID,
        DEVICE_ID,
        MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID,
        DT1_COMMAND_12,
        DIGITAL_SYNTH_1,  # Digital synth 1 area (0x19)
        DIGITAL_PART_1,   # Part 1 (0x01)
        PROGRAM_GROUP,    # Program change group (0x20)
        0x00,            # Parameter number
        program          # Program number (0-127)
    ]
    
    # Calculate checksum
    checksum = sum(msg[8:]) & 0x7F
    checksum = (128 - checksum) & 0x7F
    
    msg.extend([checksum, END_OF_SYSEX])
    return bytes(msg) 