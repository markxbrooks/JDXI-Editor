from enum import IntEnum


class MidiChannel(IntEnum):
    MIDI_CHANNEL_DIGITAL1 = 0  # Corresponds to channel 1
    MIDI_CHANNEL_DIGITAL2 = 1  # Corresponds to channel 2
    MIDI_CHANNEL_ANALOG = 2  # Corresponds to channel 3
    MIDI_CHANNEL_DRUMS = 9  # Corresponds to channel 10
    MIDI_CHANNEL_PROGRAMS = 15 # Program list