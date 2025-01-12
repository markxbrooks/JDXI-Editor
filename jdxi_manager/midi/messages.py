from .constants import *  # Import all constants
from dataclasses import dataclass
from typing import List, Optional

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

    @staticmethod
    def create_program_change_message(area: int, program: int) -> list:
        """Create program change SysEx message
        
        Args:
            area: Memory area (DIGITAL_SYNTH_1, DIGITAL_SYNTH_2, etc.)
            program: Program number (0-255)
        """
        return [
            START_OF_SYSEX,
            ROLAND_ID,
            DEVICE_ID,
            MODEL_ID_1,
            MODEL_ID_2,
            MODEL_ID,
            JD_XI_ID,
            DT1_COMMAND_12,
            area,           # Memory area
            PROGRAM_GROUP,  # Program group
            0x00,          # MSB of program number
            program,       # Program number
            END_OF_SYSEX
        ]

    @staticmethod
    def create_parameter_request(area: int, part: int, group: int, param: int, size: int = 0x100) -> List[int]:
        """Create parameter request message
        
        Args:
            area: Memory area (ANALOG_SYNTH_AREA, etc.)
            part: Part number
            group: Parameter group (first byte of parameter address)
            param: Parameter number (second byte of parameter address)
            size: Number of bytes to request (default: 256)
        """
        size_msb = (size >> 7) & 0x7F
        size_lsb = size & 0x7F
        
        return [
            START_OF_SYSEX,
            ROLAND_ID,
            DEVICE_ID,
            MODEL_ID_1,
            MODEL_ID_2,
            MODEL_ID,
            JD_XI_ID,
            RQ1_COMMAND_11,
            area,           # Memory area
            part,          # Part number
            0x00,          # First byte of parameter address
            param,         # Second byte of parameter address
            size_msb,      # Size MSB
            size_lsb,      # Size LSB
            END_OF_SYSEX
        ]

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

@dataclass
class RolandSysEx:
    """Base Roland System Exclusive message structure"""
    START_OF_SYSEX: int = START_OF_SYSEX
    ROLAND_ID: int = ROLAND_ID
    DEVICE_ID: int = DEVICE_ID
    MODEL_ID_1: int = MODEL_ID_1
    MODEL_ID_2: int = MODEL_ID_2
    MODEL_ID: int = MODEL_ID
    JD_XI_ID: int = JD_XI_ID
    command: int = 0x00
    address: List[int] = None
    data: List[int] = None
    END_OF_SYSEX: int = END_OF_SYSEX

    def to_list(self) -> List[int]:
        """Convert to list of bytes"""
        message = [
            self.START_OF_SYSEX,
            self.ROLAND_ID,
            self.DEVICE_ID,
            self.MODEL_ID_1,
            self.MODEL_ID_2,
            self.MODEL_ID,
            self.JD_XI_ID,
            self.command
        ]
        
        if self.address:
            message.extend(self.address)
            
        if self.data:
            message.extend(self.data)
            
        # Calculate checksum for DT1 messages
        if self.command == DT1_COMMAND_12 and self.address:
            checksum = sum(self.address + (self.data or [])) & 0x7F
            checksum = (128 - checksum) & 0x7F
            message.append(checksum)
            
        message.append(self.END_OF_SYSEX)
        return message

@dataclass
class ParameterMessage(RolandSysEx):
    """Parameter change message"""
    command: int = DT1_COMMAND_12
    area: int = 0x00
    part: int = 0x00
    group: int = 0x00
    param: int = 0x00
    value: int = 0x00

    def __post_init__(self):
        """Set up address and data"""
        self.address = [self.area, self.part, self.group, self.param]
        self.data = [self.value]

@dataclass
class ProgramChangeMessage(RolandSysEx):
    """Program change message"""
    command: int = DT1_COMMAND_12
    program_number: int = 1

    def __post_init__(self):
        """Set up program change message"""
        # Adjust to 0-based index
        program = (self.program_number - 1) & 0x7F
        self.address = [
            DIGITAL_SYNTH_1,  # Digital synth 1 area
            DIGITAL_PART_1,   # Part 1
            PROGRAM_GROUP,    # Program change group
            0x00             # Parameter number
        ]
        self.data = [program]

@dataclass
class PatchLoadMessage(RolandSysEx):
    """Patch load message"""
    command: int = DT1_COMMAND_12
    area: int = 0x00
    patch_number: int = 1

    def __post_init__(self):
        """Set up patch load message"""
        self.address = [
            self.area,   # Synth area
            0x01,       # Part 1
            0x00,       # Group
            0x10        # Load command
        ]
        self.data = [self.patch_number - 1]  # Convert to 0-based

@dataclass
class PatchSaveMessage(RolandSysEx):
    """Patch save message"""
    command: int = DT1_COMMAND_12
    area: int = 0x00
    patch_number: int = 1

    def __post_init__(self):
        """Set up patch save message"""
        self.address = [
            self.area,   # Synth area
            0x01,       # Part 1
            0x00,       # Group
            0x20        # Save command
        ]
        self.data = [self.patch_number - 1]  # Convert to 0-based

@dataclass 
class IdentityRequest(RolandSysEx):
    """Identity Request message"""
    command: int = 0x7E  # Universal System Exclusive
    address: List[int] = None
    data: List[int] = None

    def __post_init__(self):
        """Initialize with identity request data"""
        self.address = [
            0x7F,  # All channels
            0x06,  # Identity Request
            0x01   # Identity Request command
        ]
        self.data = [0x00, 0x00, 0x00, 0x00, 0x00]  # Sub IDs 1-5 