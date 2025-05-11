from typing import List, Iterable

from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.address import CommandID, JD_XI_HEADER_LIST
from jdxi_editor.midi.data.address.sysex import END_OF_SYSEX, START_OF_SYSEX, LOW_7_BITS_MASK, MAX_EIGHT_BIT_VALUE
from jdxi_editor.midi.sysex.parse_utils import ONE_BYTE_SYSEX_DATA_LENGTH, FOUR_BYTE_SYSEX_DATA_LENGTH


def validate_raw_sysex_message(message: List[int]) -> bool:
    """Validate JD-Xi SysEx message format"""
    try:
        # Check length
        if len(message) not in [ONE_BYTE_SYSEX_DATA_LENGTH, FOUR_BYTE_SYSEX_DATA_LENGTH]:
            log_message(f"Invalid SysEx length: {len(message)}")
            return False

        # Check header
        if message[:JDXiSysExOffset.COMMAND_ID] != [START_OF_SYSEX] + JD_XI_HEADER_LIST:
            log_message("Invalid SysEx header")
            return False

        # Check DT1 command
        if message[JDXiSysExOffset.COMMAND_ID] not in [CommandID.DT1, CommandID.RQ1]:
            log_message("Invalid command byte")
            return False

        # Check end marker
        if message[JDXiSysExOffset.SYSEX_END] != END_OF_SYSEX:
            log_message("Invalid SysEx end marker")
            return False

        # Verify checksum
        data_sum = sum(message[JDXiSysExOffset.ADDRESS_MSB:JDXiSysExOffset.CHECKSUM]) & LOW_7_BITS_MASK  # Sum from area to value
        checksum = (128 - data_sum) & LOW_7_BITS_MASK
        if message[JDXiSysExOffset.CHECKSUM] != checksum:
            log_message(f"Invalid checksum: expected {checksum}, got {message[JDXiSysExOffset.CHECKSUM]}")
            return False

        return True

    except Exception as ex:
        log_error(f"Error validating SysEx message: {str(ex)}")
        return False


def validate_raw_midi_message(message: Iterable[int]) -> bool:
    """
    Validate a raw MIDI message.

    This function checks that the message is non-empty and all values are
    within the valid MIDI byte range (0–255).

    :param message: A MIDI message represented as a list of integers or a bytes object.
    :type message: Iterable[int], can be a list, bytes, tuple, set
    :return: True if the message is valid, False otherwise.
    :rtype: bool
    """
    if not message:
        log_message("MIDI message is empty.")
        return False

    for byte in message:
        if not isinstance(byte, int) or not (0 <= byte <= MAX_EIGHT_BIT_VALUE):
            log_parameter("Invalid MIDI value detected:", message)
            return False

    return True
