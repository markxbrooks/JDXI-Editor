from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from PySide6.QtCore import QTimer, QThread
from mido import MidiFile

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.midi.channel.channel import MidiChannel


@dataclass
class MidiPlaybackState:
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
    suppress_program_changes: bool = field(default=True)
    custom_tempo_force: bool = field(default=False)
    custom_tempo: int = field(default=MidiConstant.TEMPO_162_BPM_USEC)  # Default custom tempo in microseconds
    tempo_initial: int = field(default=MidiConstant.TEMPO_120_BPM_USEC)
    tempo_at_position: int = field(default=MidiConstant.TEMPO_120_BPM_USEC)
    timer: Optional[QTimer] = field(default=None)
    # end of new attributes
    muted_tracks: set[int] = field(default_factory=set)
    muted_channels: set[int] = field(default_factory=set)
    playback_thread: Optional[QThread] = None
    playback_paused_time: Optional[float] = None
    playback_start_time: Optional[float] = None
    paused: bool = False
