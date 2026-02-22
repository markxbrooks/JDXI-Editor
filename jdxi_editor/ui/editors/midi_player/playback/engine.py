import bisect
import time
from typing import Optional, Callable, List

import mido


class ScheduledEvent:
    pass


class PlaybackEngine:
    """
    Pure MIDI playback engine.

    No Qt.
    No UI.
    No threads.

    Drives playback using absolute tick scheduling.
    """

    def __init__(self):
        self.midi_file: Optional[mido.MidiFile] = None
        self.ticks_per_beat: int = 480

        self.tempo_us: int = 500000  # default 120 BPM
        self._tempo_map: dict[int, int] = {}

        self._events: List[ScheduledEvent] = []
        self._event_index: int = 0

        self._start_tick: int = 0
        self._start_time: float = 0.0

        self._muted_tracks: set[int] = set()
        self._muted_channels: set[int] = set()

        self.suppress_program_changes = False
        self.suppress_control_changes = False

        self._is_playing = False

        # callback hook (UI/worker attaches to this)
        self.on_event: Optional[Callable[[mido.Message], None]] = None

    def load_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.ticks_per_beat = midi_file.ticks_per_beat

        self._build_tempo_map()
        self._build_event_list()

        self.reset()

    def _build_tempo_map(self) -> None:
        self._tempo_map.clear()

        absolute_tick = 0

        for track in self.midi_file.tracks:
            absolute_tick = 0
            for msg in track:
                absolute_tick += msg.time
                if msg.type == "set_tempo":
                    self._tempo_map[absolute_tick] = msg.tempo

        if 0 not in self._tempo_map:
            self._tempo_map[0] = 500000  # default

    def _build_event_list(self) -> None:
        self._events.clear()

        for track_index, track in enumerate(self.midi_file.tracks):
            absolute_tick = 0

            for msg in track:
                absolute_tick += msg.time

                if not msg.is_meta:
                    self._events.append(
                        ScheduledEvent(absolute_tick, msg.copy())
                    )

        self._events.sort(key=lambda e: e.absolute_tick)

        # cache ticks for binary search
        self._event_ticks = [e.absolute_tick for e in self._events]

    def start(self, start_tick: int = 0) -> None:
        self._start_tick = start_tick
        self._event_index = self._find_start_index(start_tick)
        self._start_time = time.time()
        self._is_playing = True

    def _find_start_index(self, start_tick: int) -> int:
        return bisect.bisect_left(self._event_ticks, start_tick)

    def stop(self) -> None:
        self._is_playing = False

    def _tick_to_seconds(self, tick: int) -> float:
        tempo = self._get_tempo_at_tick(tick)
        seconds_per_tick = tempo / 1_000_000 / self.ticks_per_beat
        return tick * seconds_per_tick

    def _get_tempo_at_tick(self, tick: int) -> int:
        applicable = [t for t in self._tempo_map if t <= tick]
        if not applicable:
            return 500000
        return self._tempo_map[max(applicable)]

    def process_until_now(self) -> None:
        if not self._is_playing:
            return

        current_time = time.time()
        elapsed = current_time - self._start_time

        while self._event_index < len(self._events):
            event = self._events[self._event_index]

            event_time = self._tick_to_seconds(
                event.absolute_tick - self._start_tick
            )

            if event_time > elapsed:
                break

            if self._should_send(event):
                if self.on_event:
                    self.on_event(event.message)

            self._event_index += 1

        if self._event_index >= len(self._events):
            self.stop()

    def _should_send(self, event: ScheduledEvent) -> bool:
        msg = event.message

        if msg.channel in self._muted_channels:
            return False

        if self.suppress_program_changes and msg.type == "program_change":
            return False

        if self.suppress_control_changes and msg.type == "control_change":
            return False

        return True

    def mute_channel(self, channel: int, muted: bool) -> None:
        if muted:
            self._muted_channels.add(channel)
        else:
            self._muted_channels.discard(channel)

    def scrub_to_tick(self, tick: int):
        self._event_index = self._find_start_index(tick)
        self._start_tick = tick
        self._start_time = time.time()

