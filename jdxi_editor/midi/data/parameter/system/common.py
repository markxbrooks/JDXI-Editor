from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterSystemCommon(AddressParameter):
    """System Common parameters"""

    MASTER_TUNE = (0x00, -100.0, 100.0)  # Master Tune (24-2024: -100.0 to +100.0 cents)
    MASTER_KEY_SHIFT = (0x04, -24, 24)  # Master Key Shift (40-88: -24 to +24 semitones)
    MASTER_LEVEL = (0x05, 0, 127)  # Master Level (0-127)

    # Reserved space (0x06-0x10)

    PROGRAM_CTRL_CH = (0x11, 0, 16)  # Program Control Channel (0-16: 1-16, OFF)

    # Reserved space (0x12-0x28)

    RX_PROGRAM_CHANGE = (0x29, 0, 1)  # Receive Program Change (0: OFF, 1: ON)
    RX_BANK_SELECT = (0x2A, 0, 1)  # Receive Bank Select (0: OFF, 1: ON)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == AddressParameterSystemCommon.MASTER_TUNE:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == AddressParameterSystemCommon.MASTER_KEY_SHIFT:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == AddressParameterSystemCommon.PROGRAM_CTRL_CH:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (
                AddressParameterSystemCommon.RX_PROGRAM_CHANGE,
                AddressParameterSystemCommon.RX_BANK_SELECT,
        ):  # Switches
            return "ON" if value else "OFF"
        return str(value)

    def get_nibbled_byte_size(self) -> int:
        """Get the nibbled byte size of the parameter"""
        if self.max_value - self.min_value <= 255:
            return 1
        else:
            return 4  # I don't know of any 2 byte parameters
