from typing import Iterable, List

from decologr import Decologr as log
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.jdxi.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.midi.data.address.address import CommandID
from jdxi_editor.midi.message.jdxi import JDXiSysexHeader
from picomidi.constant import Midi
from picomidi.core.bitmask import BitMask


def validate_raw_sysex_message(message: List[int]) -> bool:
    """Validate JD-Xi SysEx message format"""
    try:
        # Check length
        if len(message) not in [
            JDXi.Midi.SYSEX.PARAMETER.LENGTH.ONE_BYTE,
            JDXi.Midi.SYSEX.PARAMETER.LENGTH.FOUR_BYTE,
        ]:
            log.message(f"Invalid SysEx length: {len(message)}")
            return False

        # Check header
        if (
            message[: JDXiSysExMessageLayout.COMMAND_ID]
            != [Midi.SYSEX.START] + JDXiSysexHeader.to_list()
        ):
            log.message("Invalid SysEx header")
            return False

        # Check DT1 command
        if message[JDXiSysExMessageLayout.COMMAND_ID] not in [
            CommandID.DT1,
            CommandID.RQ1,
        ]:
            log.message("Invalid command byte")
            return False

        # Check end marker
        if message[JDXiSysExMessageLayout.END] != Midi.SYSEX.END:
            log.message("Invalid SysEx end marker")
            return False

        # Verify checksum
        data_sum = (
            sum(
                message[
                    JDXiSysExMessageLayout.ADDRESS.MSB : JDXiSysExMessageLayout.CHECKSUM
                ]
            )
            & BitMask.LOW_7_BITS
        )  # Sum from area to value
        checksum = (128 - data_sum) & BitMask.LOW_7_BITS
        if message[JDXiSysExMessageLayout.CHECKSUM] != checksum:
            log.message(
                f"Invalid checksum: expected {checksum}, got {message[JDXiSysExMessageLayout.CHECKSUM]}"
            )
            return False

        return True

    except Exception as ex:
        log.error(f"Error validating SysEx message: {str(ex)}")
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
        log.message("MIDI message is empty.")
        return False

    for byte in message:
        if not isinstance(byte, int) or not (0 <= byte <= Midi.VALUE.MAX.EIGHT_BIT):
            log.parameter("Invalid MIDI value detected:", message)
            return False

    return True


def validate_midi_message(message: Iterable[int]) -> bool:
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
        log.message("MIDI message is empty.")
        return False

    for byte in message:
        if not isinstance(byte, int) or not (0 <= byte <= 255):
            log.parameter("Invalid MIDI value detected:", message)
            return False

    return True
