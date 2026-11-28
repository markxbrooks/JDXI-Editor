"""
MIDI File Transport Controller

Single owner of MIDI file playback state. Wraps a PlaybackEngine and handles:
- Play / pause / stop / seek, with the engine as the only clock
- Driving the engine from a deadline-based PlaybackScheduler thread
- Publishing state, position, tempo and end-of-song as Qt signals

UI code calls the transport methods and listens to the signals; it never
starts timers or reads clocks itself.

Example:
    >>> transport = TransportController(send=lambda msg: port.send_message(msg.bytes()))
    >>> transport.state_changed.connect(transport_widget.set_state)
    >>> transport.load(midi_file)
    >>> transport.play()
"""

import sys
import threading
import time
from typing import Callable, Optional

import mido
from decologr import Decologr as log
from PySide6.QtCore import QCoreApplication, QObject, QTimer, Signal

from jdxi_editor.midi.playback.activity import playback_activity
from picomidi.playback.engine import PlaybackEngine, TransportState
from picomidi.playback.scheduler import PlaybackScheduler

POSITION_INTERVAL_MS = 50

# The last part of a wait, done in short sleeps (Windows): a timed wait on an
# event ends on the system timer's tick (15.6 ms), a short sleep does not
FINE_WAIT_S = 0.020
FINE_STEP_S = 0.001


class PreciseClockEngine(PlaybackEngine):
    """
    PlaybackEngine on time.perf_counter().

    The engine reads time.monotonic(), which on Windows before Python 3.13
    moves in 15.6 ms steps: woken on time, the engine saw an older time and
    sent the note later (measured on Windows 11: ~8 ms late on average, up to
    19 ms). perf_counter() is precise to the microsecond everywhere.
    """

    @staticmethod
    def _now() -> float:
        return time.perf_counter()


class _PreciseWaitScheduler(PlaybackScheduler):
    """
    PlaybackScheduler whose waits end on time on Windows too.

    An Event.wait() there ends on the 15.6 ms timer tick, so the wait is an
    Event.wait() for all but its last 20 ms, then 1 ms sleeps that still look
    for a wake (pause, seek…) between them. Other systems: as is.
    """

    def _wait_for_wake(self, timeout):
        if timeout is None or sys.platform != "win32" or timeout <= 0:
            return super()._wait_for_wake(timeout)
        deadline = time.perf_counter() + timeout
        coarse = timeout - FINE_WAIT_S
        if coarse > 0 and self._wake.wait(coarse):
            self._wake.clear()
            return
        while not self._wake.is_set() and not self._stop.is_set():
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                break
            time.sleep(min(remaining, FINE_STEP_S))
        self._wake.clear()


class _PlayingTimerResolution:
    """
    Precise timers while playing.

    Windows: 1 ms timer resolution (timeBeginPeriod); a thread's timed wait
    otherwise ends on the 15.6 ms tick and the scheduler wakes up late.
    macOS: a latency-critical activity, so the system does not throttle the
    timers (App Nap, timer coalescing: notes were up to 150 ms late).
    Elsewhere nothing is needed.
    """

    def __init__(self) -> None:
        self._on = False
        self._activity = None

    def set(self, on: bool) -> None:
        if on == self._on:
            return
        if sys.platform == "darwin":
            from jdxi_editor.utils import macos_activity

            if on:
                self._activity = macos_activity.begin("JD-Xi Editor is playing MIDI")
            else:
                macos_activity.end(self._activity)
                self._activity = None
            self._on = on
            return
        if sys.platform != "win32":
            return
        try:
            import ctypes

            winmm = ctypes.WinDLL("winmm")
            result = (winmm.timeBeginPeriod if on else winmm.timeEndPeriod)(1)
            if result != 0:  # TIMERR_NOERROR
                log.warning(
                    f"timer resolution request returned {result}",
                    scope="TransportController",
                )
            self._on = on
        except (OSError, AttributeError) as ex:
            log.warning(f"Timer resolution not set: {ex}", scope="TransportController")


class TransportController(QObject):
    """
    Transport for MIDI file playback.

    Signals:
        state_changed(TransportState): after every transport state change
        position_changed(float): position in seconds, while playing and after seeks
        tempo_changed(int): tempo in µs per beat when it changes at the position
        finished(): playback reached the end of the file (position is rewound)
        loop_changed(): loop on/off or the A–B range changed
    """

    state_changed = Signal(object)
    position_changed = Signal(float)
    tempo_changed = Signal(int)
    finished = Signal()
    loop_changed = Signal()
    # Cross-thread: scheduler thread -> Qt main thread for EOF handling
    _scheduler_ended = Signal()

    def __init__(
        self,
        engine: Optional[PlaybackEngine] = None,
        send: Optional[Callable[[mido.Message], None]] = None,
        parent: Optional[QObject] = None,
        position_interval_ms: int = POSITION_INTERVAL_MS,
        scheduler_max_sleep_s: float = 1.0,
        # Kept for call-site compatibility; fixed-interval polling is gone.
        scheduler_interval_ms: int = 5,
    ):
        """
        Initialize the transport.

        :param engine: PlaybackEngine to drive. If not provided, creates one
        :param send: Callable that sends a mido.Message to the instrument
        :param parent: Optional QObject parent
        :param position_interval_ms: How often position_changed is emitted while playing
        :param scheduler_max_sleep_s: Cap on one scheduler wait between deadlines
        :param scheduler_interval_ms: Ignored (legacy); deadlines replace polling
        """
        super().__init__(parent)
        del scheduler_interval_ms  # legacy kw-only compatibility
        self.engine = engine or PreciseClockEngine()
        self.send = send
        self.engine.on_event = self._on_engine_event
        # (channel, note) keys sounding on the instrument: one voice per key
        self._sounding: dict[tuple[int, int], float] = {}
        self._timer_resolution = _PlayingTimerResolution()
        # Engine calls (and so MIDI sends) are serialised across both threads
        self._lock = threading.RLock()
        self._loaded = False
        self._last_state = self.engine.state
        self._last_tempo: Optional[int] = None
        self._scheduler: Optional[PlaybackScheduler] = None
        self._scheduler_max_sleep_s = scheduler_max_sleep_s
        self._loop_range_ticks: Optional[tuple[int, int]] = None

        self._scheduler_ended.connect(self._on_scheduler_ended)
        self._position_timer = QTimer(self)
        self._position_timer.setInterval(position_interval_ms)
        self._position_timer.timeout.connect(self._emit_position)

        app = QCoreApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.shutdown)

    # --- Queries ------------------------------------------------------------

    @property
    def state(self) -> TransportState:
        return self.engine.state

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def position_seconds(self) -> float:
        with self._lock:
            return self.engine.position_seconds

    @property
    def position_tick(self) -> int:
        with self._lock:
            return self.engine.position_tick

    @property
    def duration_seconds(self) -> float:
        return self.engine.duration_seconds

    @property
    def speed(self) -> float:
        return self.engine.speed

    @property
    def loop_enabled(self) -> bool:
        return self.engine.loop_enabled

    @property
    def loop_range_seconds(self) -> Optional[tuple[float, float]]:
        """A–B range in seconds, or None when the whole file loops."""
        if self._loop_range_ticks is None:
            return None
        start, end = self._loop_range_ticks
        return self.engine.tick_to_seconds(start), self.engine.tick_to_seconds(end)

    def bar_beat_at_seconds(self, seconds: float) -> tuple[int, int]:
        """1-based (bar, beat) at *seconds*, following tempo map and time signatures."""
        with self._lock:
            return self.engine.bar_beat_at_tick(self.engine.seconds_to_tick(seconds))

    def nearest_bar_seconds(self, seconds: float) -> float:
        """Time of the bar line nearest to *seconds*."""
        with self._lock:
            tick = self.engine.nearest_bar_tick(self.engine.seconds_to_tick(seconds))
            return self.engine.tick_to_seconds(tick)

    # --- Commands -----------------------------------------------------------

    def load(self, midi_file: mido.MidiFile, keep_position: bool = False) -> None:
        """
        Load *midi_file* into the engine.

        :param midi_file: File to play
        :param keep_position: Keep the current position (in ticks, so a tempo
            change stays on the same beat) and play/pause state, e.g. after
            editing the file that is playing
        """
        with self._lock:
            state = self.engine.state if keep_position else TransportState.STOPPED
            position = self.engine.position_tick if keep_position else 0
            self.engine.stop()
            self.engine.load_file(midi_file)
            if not keep_position:
                self._loop_range_ticks = None
            self.engine.set_loop(self.engine.loop_enabled, self._loop_range_ticks)
            self._loop_range_ticks = self.engine.loop_range
            if position:
                self.engine.seek_tick(position)
            if state != TransportState.STOPPED:
                self.engine.start(self.engine.start_tick)
                if state == TransportState.PAUSED:
                    self.engine.pause()
        self._loaded = True
        self._last_tempo = None
        self._wake_scheduler()
        self._after_command()
        self.loop_changed.emit()

    def play(self) -> bool:
        """
        Play from the current position, or resume if paused.

        :return: True if playing afterwards
        """
        if not self._loaded:
            return False
        with self._lock:
            if self.engine.state == TransportState.PAUSED:
                self.engine.resume()
            elif self.engine.state == TransportState.STOPPED:
                if self.engine.position_seconds >= self.engine.duration_seconds:
                    self.engine.seek_tick(0)
                self.engine.start(self.engine.start_tick)
        self._ensure_scheduler()
        self._wake_scheduler()
        self._after_command()
        return True

    def pause(self) -> None:
        """Pause, keeping the position; sounding notes are released."""
        with self._lock:
            self.engine.pause()
        self._wake_scheduler()
        self._after_command()

    def toggle_play_pause(self) -> None:
        """Pause if playing, otherwise play."""
        if self.engine.state == TransportState.PLAYING:
            self.pause()
        else:
            self.play()

    def stop(self) -> None:
        """Stop, silence the instrument and rewind to the start."""
        with self._lock:
            self.engine.stop()
            if self._loaded:
                self.engine.all_notes_off()
            self.engine.seek_tick(0)
        self._wake_scheduler()
        self._after_command()

    def seek_seconds(self, seconds: float) -> None:
        """Move to *seconds* without changing the play/pause/stop state."""
        with self._lock:
            self.engine.seek_seconds(seconds)
        self._wake_scheduler()
        self._after_command()

    def set_loop(
        self,
        enabled: bool,
        start_seconds: Optional[float] = None,
        end_seconds: Optional[float] = None,
    ) -> None:
        """
        Turn looping on or off.

        :param enabled: Loop when the end of the range is reached
        :param start_seconds: A point; with *end_seconds* sets an A–B loop
        :param end_seconds: B point; leave both None to keep the current range
        """
        with self._lock:
            loop_range = self._loop_range_ticks
            if start_seconds is not None and end_seconds is not None:
                loop_range = (
                    self.engine.seconds_to_tick(start_seconds),
                    self.engine.seconds_to_tick(end_seconds),
                )
            self.engine.set_loop(enabled, loop_range)
            self._loop_range_ticks = self.engine.loop_range
        self._wake_scheduler()
        self.loop_changed.emit()

    def clear_loop_range(self) -> None:
        """Loop the whole file instead of an A–B range (on/off is unchanged)."""
        with self._lock:
            self.engine.set_loop(self.engine.loop_enabled, None)
            self._loop_range_ticks = None
        self._wake_scheduler()
        self.loop_changed.emit()

    def set_speed(self, speed: float) -> None:
        """Set playback speed (1.0 = file tempo; 0.25–2.0)."""
        with self._lock:
            self.engine.set_speed(speed)
        self._last_tempo = None  # Re-announce the tempo for the new speed
        self._wake_scheduler()
        self._emit_position()

    def set_send_clock(self, enabled: bool) -> None:
        """Send MIDI clock, Start/Stop/Continue and Song Position Pointer."""
        with self._lock:
            self.engine.set_send_clock(enabled)
        self._wake_scheduler()

    def panic(self) -> None:
        """Send note-offs and All Sound Off / All Notes Off on every channel."""
        with self._lock:
            self.engine.all_notes_off()

    def set_mutes(self, muted_tracks: set[int], muted_channels: set[int]) -> None:
        """
        Apply mute state; takes effect immediately during playback.

        :param muted_tracks: 0-based track indexes to mute
        :param muted_channels: 0-based MIDI channels to mute
        """
        with self._lock:
            track_count = len(self.engine.midi_file.tracks) if self._loaded else 0
            for track_index in range(track_count):
                self.engine.mute_track(track_index, track_index in muted_tracks)
            for channel in range(16):
                self.engine.mute_channel(channel, channel in muted_channels)
        self._wake_scheduler()

    def set_track_velocity_scales(self, scales: dict[int, float]) -> None:
        """
        Scale tracks' note-on velocities; takes effect on the next notes.

        :param scales: 0-based track index -> factor (absent = 1.0)
        """
        with self._lock:
            track_count = len(self.engine.midi_file.tracks) if self._loaded else 0
            for track_index in range(track_count):
                self.engine.set_track_velocity_scale(
                    track_index, scales.get(track_index, 1.0)
                )

    def set_track_volumes(self, volumes: dict[int, float]) -> None:
        """
        Set tracks' overall note-on levels (0.0–1.0); next notes only.

        :param volumes: 0-based track index -> level (absent = 1.0)
        """
        with self._lock:
            track_count = len(self.engine.midi_file.tracks) if self._loaded else 0
            for track_index in range(track_count):
                self.engine.set_track_volume(
                    track_index, volumes.get(track_index, 1.0)
                )

    def set_track_transposes(self, semitones: dict[int, int]) -> None:
        """
        Transpose tracks by semitones; takes effect on the next notes.

        :param semitones: 0-based track index -> offset (absent = 0)
        """
        with self._lock:
            track_count = len(self.engine.midi_file.tracks) if self._loaded else 0
            for track_index in range(track_count):
                self.engine.set_track_transpose(
                    track_index, semitones.get(track_index, 0)
                )

    def set_track_channel_maps(
        self, channels: dict[int, Optional[int]]
    ) -> None:
        """
        Remap tracks to output MIDI channels; None restores the file channel.

        :param channels: 0-based track index -> channel 0–15 or None
        """
        with self._lock:
            track_count = len(self.engine.midi_file.tracks) if self._loaded else 0
            for track_index in range(track_count):
                self.engine.set_track_channel_map(
                    track_index, channels.get(track_index)
                )

    def set_suppression(self, program_changes: bool, control_changes: bool) -> None:
        """Choose whether program changes / control changes in the file are sent."""
        with self._lock:
            self.engine.suppress_program_changes = program_changes
            self.engine.suppress_control_changes = control_changes

    def shutdown(self) -> None:
        """Stop playback and the scheduler thread (safe to call more than once)."""
        if self._loaded and self.engine.state != TransportState.STOPPED:
            self.stop()
        self._position_timer.stop()
        playback_activity().set_playing(self, False)
        if self._scheduler is not None:
            self._scheduler.stop()
            self._scheduler = None
        self._timer_resolution.set(False)

    # --- Internals ----------------------------------------------------------

    def _on_engine_event(self, msg: mido.Message) -> None:
        if self.send is None:
            return
        for out in self._one_voice_per_key(msg):
            self.send(out)

    # A second note-on this soon after the first on the same key is the same
    # note played by a doubled track (left/right copies): dropped, not retriggered
    DOUBLED_WITHIN_S = 0.03

    def _one_voice_per_key(
        self, msg: mido.Message, now: Optional[float] = None
    ) -> list[mido.Message]:
        """
        Never start a second voice on a key that is already sounding.

        Two tracks on one channel playing the same note send two note-ons and,
        by design of the engine, a single note-off when the last one ends. The
        JD-Xi starts a voice per note-on and a note-off may end only one of
        them: the other hangs until Panic.

        - The same note started at the same moment by another track (within
          DOUBLED_WITHIN_S): the second note-on is dropped, as if the part
          were played once. Retriggering it cut every note of a doubled bass
          on the mono Analog part.
        - A later note-on on a key still sounding: the note is retriggered,
          its note-off first, still one voice for the one note-off to come.
        """
        if now is None:
            now = time.perf_counter()
        if msg.type == "note_on" and msg.velocity > 0:
            key = (msg.channel, msg.note)
            started = self._sounding.get(key)
            self._sounding[key] = now
            if started is not None:
                if now - started < self.DOUBLED_WITHIN_S:
                    self._sounding[key] = started
                    return []
                return [
                    mido.Message(
                        "note_off", channel=msg.channel, note=msg.note, velocity=0
                    ),
                    msg,
                ]
        elif msg.type in ("note_off", "note_on"):
            self._sounding.pop((msg.channel, msg.note), None)
        elif msg.type == "control_change" and msg.control in (120, 123):
            # All Sound Off / All Notes Off
            self._sounding = {
                key: t for key, t in self._sounding.items() if key[0] != msg.channel
            }
        return [msg]

    def _ensure_scheduler(self) -> None:
        if self._scheduler is not None and self._scheduler.is_running:
            return
        self._scheduler = _PreciseWaitScheduler(
            self.engine,
            lock=self._lock,
            on_ended=self._on_scheduler_ended_from_thread,
            max_sleep_s=self._scheduler_max_sleep_s,
        )
        self._scheduler.start()

    def _wake_scheduler(self) -> None:
        if self._scheduler is not None:
            self._scheduler.wake()

    def _on_scheduler_ended_from_thread(self) -> None:
        """EOF callback from the scheduler thread; marshal onto the Qt thread."""
        self._scheduler_ended.emit()

    def _on_scheduler_ended(self) -> None:
        """End of file reached (queued from the scheduler thread)."""
        with self._lock:
            if self.engine.state != TransportState.STOPPED:
                return  # Play was pressed again before this was delivered
            self.engine.seek_tick(0)
        self._after_command()
        self.finished.emit()

    def _after_command(self) -> None:
        """Publish state and position, and run the position timer only while playing."""
        playing = self.engine.state == TransportState.PLAYING
        self._timer_resolution.set(playing)
        if playing and not self._position_timer.isActive():
            self._position_timer.start()
        elif not playing:
            self._position_timer.stop()
        if self.engine.state != self._last_state:
            self._last_state = self.engine.state
            playback_activity().set_playing(self, playing)
            self.state_changed.emit(self._last_state)
        self._emit_position()

    def _emit_position(self) -> None:
        with self._lock:
            seconds = self.engine.position_seconds
            tempo = self.engine.tempo_at_tick(self.engine.seconds_to_tick(seconds))
        self.position_changed.emit(seconds)
        if self._loaded and tempo != self._last_tempo:
            self._last_tempo = tempo
            self.tempo_changed.emit(tempo)
