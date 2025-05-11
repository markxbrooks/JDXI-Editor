 
def validate_sysex_message(message: List[int]) -> bool:
    """Validate JD-Xi SysEx message format"""
    try:
        # Check length
        if len(message) not in [15, 18]:
            log_message(f"Invalid SysEx length: {len(message)}")
            return False

        # Check header
        if message[:7] != [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]:
            log_message("Invalid SysEx header")
            return False

        # Check DT1 command
        if message[7] not in [0x12, 0x11]:
            log_message("Invalid command byte")
            return False

        # Check end marker
        if message[-1] != 0xF7:
            log_message("Invalid SysEx end marker")
            return False

        # Verify checksum
        data_sum = sum(message[8:-2]) & 0x7F  # Sum from area to value
        checksum = (128 - data_sum) & 0x7F
        if message[-2] != checksum:
            log_message(f"Invalid checksum: expected {checksum}, got {message[-2]}")
            return False

        return True

    except Exception as ex:
        log_error(f"Error validating SysEx message: {str(ex)}")
        return False

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
        log_message("MIDI message is empty.")
        return False

    for byte in message:
        if not isinstance(byte, int) or not (0 <= byte <= 255):
            log_parameter("Invalid MIDI value detected:", message)
            return False

    return True