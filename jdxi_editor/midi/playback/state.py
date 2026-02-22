"""
MIDI playback state management.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from mido import MidiFile
from picomidi.constant import Midi
from PySide6.QtCore import QThread, QTimer

from jdxi_editor.midi.channel.channel import MidiChannel


@dataclass
class MidiPlaybackState:
    """State container for MIDI file playback."""

    active_notes: dict = field(default_factory=lambda: defaultdict(set))
    buffered_msgs: list = field(default_factory=list)
    buffer_end_time: float = 0.0
    channel_selected: MidiChannel = MidiChannel.DIGITAL_SYNTH_1
    events: list = field(default_factory=list)
    event_index_current: int = 0
    event_index: Optional[int] = None
    event_buffer: list = field(default_factory=list)
    file: Optional[MidiFile] = None
    file_duration_seconds: float = 0.0
    # New attributes for playback state
    suppress_control_changes: bool = field(default=True)
    suppress_program_changes: bool = field(default=False)  # False = send PCs so inserted PCs are heard
    custom_tempo_force: bool = field(default=False)
    custom_tempo: int = field(
        default=Midi.TEMPO.BPM_162_USEC
    )  # Default custom tempo in microseconds
    tempo_initial: int = field(default=Midi.TEMPO.BPM_120_USEC)
    tempo_at_position: int = field(default=Midi.TEMPO.BPM_120_USEC)
    timer: Optional[QTimer] = field(default=None)
    # end of new attributes
    muted_tracks: set[int] = field(default_factory=set)
    muted_channels: set[int] = field(default_factory=set)
    playback_thread: Optional[QThread] = None
    playback_paused_time: Optional[float] = None
    playback_start_time: Optional[float] = None
    playback_paused: bool = False

    def __post_init__(self) -> None:
        if self.custom_tempo_force:
            self.tempo_at_position = self.custom_tempo  # Use custom tempo if forced
        else:
            self.tempo_at_position = Midi.TEMPO.BPM_120_USEC  # Default of 120 bpm
