"""
MIDI value constants and validation utilities.
"""

from picomidi.values import MaxValues, MinValues


class MidiValue:
    """Common MIDI value constants."""

    MAX = MaxValues
    MIN = MinValues
    ZERO = 0x00
    ON = 0x01
    OFF = 0x00

    # ------------------------------------------------------------------------
    # Signed Values
    # ------------------------------------------------------------------------
    class SignedSixteenBit:
        """Signed 16-bit integer constants."""

        MAX = 0x7FFF  # 32767, max positive signed 16-bit
        MIN = -0x8000  # -32768, two's complement min signed

    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    @staticmethod
    def is_within_seven_bit_range(value):
        """
        Check if the given value falls within the range of a 7-bit unsigned integer.
        :param value: The value to validate.
        :return: True if the value is within range, False otherwise.
        """
        return 0 <= value <= MidiValue.MAX.SEVEN_BIT

    @staticmethod
    def is_within_sixteen_bit_range(value, signed=False):
        """
        Check if the given value falls within the range of a 16-bit integer.
        :param value: The value to validate.
        :param signed: If True, treat as signed range, otherwise unsigned.
        :return: True if the value is within range, False otherwise.
        """
        if signed:
            return (
                MidiValue.SignedSixteenBit.MIN
                <= value
                <= MidiValue.SignedSixteenBit.MAX
            )
        return 0 <= value <= MidiValue.MAX.SIXTEEN_BIT
