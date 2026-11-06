"""
MIDI playback state management.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional

from mido import MidiFile

from jdxi_editor.midi.channel.channel import MidiChannel
from picomidi.constant import Midi


@dataclass
class MidiPlaybackState:
    """State container for MIDI file playback."""

    channel_selected: Literal[
        MidiChannel.DIGITAL_SYNTH_1,
        MidiChannel.DIGITAL_SYNTH_2,
        MidiChannel.ANALOG_SYNTH,
        MidiChannel.DRUM_KIT,
    ] = MidiChannel.DIGITAL_SYNTH_1
    events: list = field(default_factory=list)
    file: Optional[MidiFile] = None
    file_duration_seconds: float = 0.0
    # New attributes for playback state
    suppress_control_changes: bool = field(default=True)
    suppress_program_changes: bool = field(
        default=False
    )  # False = send PCs so inserted PCs are heard
    custom_tempo_force: bool = field(default=False)
    custom_tempo: int = field(
        default=Midi.tempo.BPM_162_USEC
    )  # Default custom tempo in microseconds
    tempo_initial: int = field(default=Midi.tempo.BPM_120_USEC)
    tempo_at_position: int = field(default=Midi.tempo.BPM_120_USEC)
    # end of new attributes
    muted_tracks: set[int] = field(default_factory=set)
    muted_channels: set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.custom_tempo_force:
            self.tempo_at_position = self.custom_tempo  # Use custom tempo if forced
        else:
            self.tempo_at_position = Midi.tempo.BPM_120_USEC  # Default of 120 bpm
