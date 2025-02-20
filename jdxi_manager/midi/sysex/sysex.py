"""

Basic MIDI System Exclusive constants

# Example Usage
print(SysexParameter.get_address_by_name("TONE_1_LEVEL"))  # Outputs: 16 (0x10)
print(SysexParameter.get_name_by_address(0x11))           # Outputs: "TONE_2_LEVEL"

"""

from enum import Enum

# MIDI Constants
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
JD_XI_ID = 0x00
XI_HEADER = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E])

# Roland Commands
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1

PROGRAM_COMMON = 0x00


from enum import Enum


class SysexParameter(Enum):
    # MIDI Constants (Single Values)
    START_OF_SYSEX = 0xF0
    END_OF_SYSEX = 0xF7
    ROLAND_ID = 0x41
    JD_XI_ID = 0x00
    XI_HEADER = bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E])

    # Roland Commands (Command Type → Name Mapping)
    DT1_COMMAND_12 = ("Data Set 1", 0x12)
    RQ1_COMMAND_11 = ("Data Request 1", 0x11)

    # SysEx Parameters (Name, Address)
    PROGRAM_COMMON = ("PROGRAM_COMMON", 0x00)
    TONE_1_LEVEL = ("TONE_1_LEVEL", 0x10)
    TONE_2_LEVEL = ("TONE_2_LEVEL", 0x11)

    def __new__(cls, *args):
        if len(args) == 1:
            obj = object.__new__(cls)
            obj._value_ = args[0]  # Store value directly
            obj.param_name = None  # Set default param name
            return obj
        elif len(args) == 2:
            param_name, value = args
            obj = object.__new__(cls)
            obj._value_ = value
            obj.param_name = param_name
            return obj
        else:
            raise ValueError("Invalid number of arguments for SysexParameter Enum")

    @classmethod
    def get_command_name(cls, command_type):
        """Retrieve the command name given a command type (e.g., 0x12 -> 'Data Set 1')."""
        for item in cls:
            if hasattr(item, "param_name") and item.value == command_type:
                return item.param_name
        return None  # Return None if not found
