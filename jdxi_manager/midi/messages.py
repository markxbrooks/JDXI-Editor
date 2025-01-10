from .constants import *  # Import all constants

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

def create_parameter_message(area: int, part: int, param: int, value: int) -> list:
    """Create a parameter change message
    
    Args:
        area: Memory area (e.g. DIGITAL_SYNTH_AREA)
        part: Part number (1 or 2 for digital, 3 for analog)
        param: Parameter number
        value: Parameter value (0-127)
        
    Returns:
        List of bytes representing the MIDI message
    """
    msg = [
        START_OF_SYSEX,
        ROLAND_ID,
        DEVICE_ID,
        MODEL_ID_1,
        MODEL_ID_2,
        MODEL_ID,
        JD_XI_ID,
        DT1_COMMAND_12,
        area,
        part,
        param & 0x7F,  # Parameter LSB
        param >> 7,    # Parameter MSB
        value & 0x7F,  # Value LSB
        value >> 7,    # Value MSB
        END_OF_SYSEX
    ]
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