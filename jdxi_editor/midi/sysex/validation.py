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