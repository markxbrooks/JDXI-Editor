import bisect
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Callable, List

import mido


@dataclass
class ScheduledEvent:
    """A MIDI event at a given file tick, for one track."""

    absolute_tick: int
    message: mido.Message
    track_index: int = 0


class TransportState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()
    

class PlaybackEngine:
    """
    Pure MIDI playback engine.

    No Qt. No UI. No threads. Drives playback using absolute tick scheduling
    with a single merged event list and segment-wise tempo.

    How the engine is driven:
    - The owner (e.g. a worker or controller) loads a file with load_file(),
      then calls start(start_tick) to begin playback.
    - On a timer or tick (e.g. every 10–20 ms), the owner calls
      process_until_now(). The engine advances over events whose scheduled
      time has passed and invokes the on_event callback for each that passes
      _should_send (mute/suppress).
    - The owner sets engine.on_event to a callable (e.g. lambda msg: send(msg))
      so that messages are actually sent (e.g. to a MIDI port).
    - Transport (play/pause/stop/scrub) is handled by the owner: stop() and
      scrub_to_tick() are called by the transport/controller; the owner
      simply stops calling process_until_now() when paused.
    """

    def __init__(self):
        self.midi_file: Optional[mido.MidiFile] = None
        self.ticks_per_beat: int = 480

        self.tempo_us: int = 500000  # default 120 BPM
        self._tempo_map: dict[int, int] = {}
        self._tick_to_time: List[tuple[int, float]] = []  # (tick, cumulative seconds from 0)

        self._events: List[ScheduledEvent] = []
        self._event_index: int = 0

        self._start_tick: int = 0
        self._start_time: float = 0.0

        self._muted_tracks: set[int] = set()
        self._muted_channels: set[int] = set()

        self.suppress_program_changes = False
        self.suppress_control_changes = False

        self._state = TransportState.STOPPED
        self._is_playing = False  # True only when _state == PLAYING

        # callback hook (UI/worker attaches to this)
        self.on_event: Optional[Callable[[mido.Message], None]] = None

    @property
    def state(self) -> TransportState:
        return self._state

    def _set_state(self, new_state: TransportState) -> None:
        if self._state == new_state:
            return
        self._state = new_state
        if new_state == TransportState.PLAYING:
            self._enter_playing()
        elif new_state == TransportState.STOPPED:
            self._enter_stopped()
        elif new_state == TransportState.PAUSED:
            self._enter_paused()

    def _enter_playing(self) -> None:
        self._is_playing = True

    def _enter_stopped(self) -> None:
        self._is_playing = False

    def _enter_paused(self) -> None:
        self._is_playing = False

    def load_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.ticks_per_beat = midi_file.ticks_per_beat

        self._build_tempo_map()
        self._build_event_list()
        self._build_time_map()
        self.reset()

    def reset(self) -> None:
        """Reset playback state (position, play flag). Mute/suppress settings are unchanged."""
        self._event_index = 0
        self._start_tick = 0
        self._start_time = 0.0
        self._set_state(TransportState.STOPPED)

    def _build_tempo_map(self) -> None:
        """Build a single global tempo map from all tracks (Type 0/1: merge set_tempo by tick)."""
        self._tempo_map.clear()
        tempo_events: List[tuple[int, int]] = []

        for track in self.midi_file.tracks:
            absolute_tick = 0
            for msg in track:
                absolute_tick += msg.time
                if msg.type == "set_tempo":
                    tempo_events.append((absolute_tick, msg.tempo))

        tempo_events.sort(key=lambda x: x[0])
        for tick, tempo in tempo_events:
            self._tempo_map[tick] = tempo

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
                        ScheduledEvent(
                            absolute_tick=absolute_tick,
                            message=msg.copy(),
                            track_index=track_index,
                        )
                    )

        self._events.sort(key=lambda e: e.absolute_tick)

        # cache ticks for binary search
        self._event_ticks = [e.absolute_tick for e in self._events]

    def start(self, start_tick: int = 0) -> None:
        self._start_tick = start_tick
        self._event_index = self._find_start_index(start_tick)
        self._start_time = time.time()
        self._set_state(TransportState.PLAYING)

    def _find_start_index(self, start_tick: int) -> int:
        return bisect.bisect_left(self._event_ticks, start_tick)

    def stop(self) -> None:
        self._set_state(TransportState.STOPPED)

    def pause(self) -> None:
        """Pause playback; position is preserved."""
        self._set_state(TransportState.PAUSED)

    def _build_time_map(self) -> None:
        """Build cumulative time (seconds) at each tempo change for segment-wise tick→time."""
        if not self._tempo_map:
            self._tick_to_time = [(0, 0.0)]
            return
        ticks_sorted = sorted(self._tempo_map.keys())
        out: List[tuple[int, float]] = []
        time_sec = 0.0
        prev_tick = 0
        prev_tempo = self._tempo_map[0] if 0 in self._tempo_map else 500000
        for t in ticks_sorted:
            if t == 0:
                out.append((0, 0.0))
                prev_tempo = self._tempo_map[0]
                continue
            segment_ticks = t - prev_tick
            time_sec += segment_ticks * (prev_tempo / 1_000_000) / self.ticks_per_beat
            out.append((t, time_sec))
            prev_tick = t
            prev_tempo = self._tempo_map[t]
        self._tick_to_time = out if out else [(0, 0.0)]

    def _tick_to_seconds(self, tick: int) -> float:
        """Seconds from 0 to tick using segment-wise tempo (variable tempo safe)."""
        if tick <= 0:
            return 0.0
        if not self._tick_to_time:
            return tick * (self._get_tempo_at_tick(0) / 1_000_000) / self.ticks_per_beat
        # Find segment: last (t, time) where t <= tick
        idx = bisect.bisect_right([t for t, _ in self._tick_to_time], tick) - 1
        if idx < 0:
            return 0.0
        seg_tick, seg_time = self._tick_to_time[idx]
        tempo = self._get_tempo_at_tick(seg_tick)
        delta_ticks = tick - seg_tick
        return seg_time + delta_ticks * (tempo / 1_000_000) / self.ticks_per_beat

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
            self._set_state(TransportState.STOPPED)

    def _should_send(self, event: ScheduledEvent) -> bool:
        msg = event.message

        if event.track_index in self._muted_tracks:
            return False

        channel = getattr(msg, "channel", None)
        if channel is not None and channel in self._muted_channels:
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

    def mute_track(self, track_index: int, muted: bool) -> None:
        if muted:
            self._muted_tracks.add(track_index)
        else:
            self._muted_tracks.discard(track_index)

    def scrub_to_tick(self, tick: int) -> None:
        self._event_index = self._find_start_index(tick)
        self._start_tick = tick
        self._start_time = time.time()

