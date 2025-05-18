from jdxi_editor.log.logger import Logger as log


def log_midi_info(msb: int, lsb: int, pc: int) -> None:
    """
    Log MIDI information in a consistent format.
    :param msb: int most significant byte
    :param lsb: int least significant byte
    :param pc: int program
    :return: None
    """
    log.message(f"msb: {msb}, lsb: {lsb}, pc: {pc}")
