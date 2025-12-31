"""
This module defines an enumeration for MIDI channels used in a synthesizer, specifically for a Roland JD-Xi-style instrument editor.

The `MidiChannel` class extends `IntEnum` and provides symbolic names for the common MIDI channels, including:
- DIGITAL1 (channel 1)
- DIGITAL2 (channel 2)
- ANALOG (channel 3)
- DRUM (channel 10)
- PROGRAM (channel 16)

The class also provides utility methods for handling MIDI channels, including:
- `__str__`: Returns a string representation of the channel.
- `midi_channel_number`: A property that returns the actual MIDI channel number (1-based).
- `from_midi_channel`: A class method that retrieves a `MidiChannel` from a given MIDI channel number.

Usage example:
    channel = MidiChannel.DIGITAL1
    print(str(channel))  # Output: "Digital 1 (Ch.1)"
    print(channel.midi_channel_number)  # Output: 1
    print(MidiChannel.from_midi_channel(9))  # Output: MidiChannel.DRUM_KIT

"""


from enum import IntEnum


class MidiChannel(IntEnum):
    """
    MIDI Channel Enum
    """

    DIGITAL_SYNTH_1 = 0  # Corresponds to channel 1
    DIGITAL_SYNTH_2 = 1  # Corresponds to channel 2
    ANALOG_SYNTH = 2  # Corresponds to channel 3
    DRUM_KIT = 9  # Corresponds to channel 10
    PROGRAM = 15  # Program list
    VOCAL_FX = 6  # Is this correct?!

    def __str__(self) -> str:
        return {
            self.DIGITAL_SYNTH_1: "Digital 1 (Ch.1)",
            self.DIGITAL_SYNTH_2: "Digital 2 (Ch.2)",
            self.ANALOG_SYNTH: "Analog (Ch.3)",
            self.DRUM_KIT: "Drums (Ch.10)",
            self.PROGRAM: "Programs (Ch.16)",
            self.VOCAL_FX: "Programs (Ch.3)",
        }.get(self, f"Unknown (Ch.{self.value + 1})")

    @property
    def midi_channel_number(self) -> int:
        return self.value + 1

    @classmethod
    def from_midi_channel(cls, channel: int) -> "MidiChannel | None":
        return next((m for m in cls if m.value == channel), None)
