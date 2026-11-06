"""
MIDI File Transport Controller

Single owner of MIDI file playback state. Wraps a PlaybackEngine and handles:
- Play / pause / stop / seek, with the engine as the only clock
- Driving the engine from a dedicated thread with a precise timer
- Publishing state, position, tempo and end-of-song as Qt signals

UI code calls the transport methods and listens to the signals; it never
starts timers or reads clocks itself.

Example:
    >>> transport = TransportController(send=lambda msg: port.send_message(msg.bytes()))
    >>> transport.state_changed.connect(transport_widget.set_state)
    >>> transport.load(midi_file)
    >>> transport.play()
"""

import threading
from typing import Callable, Optional

import mido
from decologr import Decologr as log
from PySide6.QtCore import QCoreApplication, QObject, Qt, QThread, QTimer, Signal

from picomidi.playback.engine import PlaybackEngine, TransportState

SCHEDULER_INTERVAL_MS = 5
POSITION_INTERVAL_MS = 50


class _SchedulerThread(QThread):
    """Calls engine.process_until_now() on a precise timer in its own thread."""

    ended = Signal()

    def __init__(
        self,
        engine: PlaybackEngine,
        lock: threading.RLock,
        interval_ms: int,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._engine = engine
        self._lock = lock
        self._interval_ms = interval_ms

    def run(self) -> None:
        """Run a timer owned by this thread until quit() is called."""
        timer = QTimer()
        timer.setTimerType(Qt.TimerType.PreciseTimer)
        timer.setInterval(self._interval_ms)
        timer.timeout.connect(self._tick, Qt.ConnectionType.DirectConnection)
        timer.start()
        self.exec()
        timer.stop()

    def _tick(self) -> None:
        try:
            with self._lock:
                ended = self._engine.process_until_now()
        except Exception as ex:
            log.error(f"Error during MIDI playback: {ex}")
            return
        if ended:
            self.ended.emit()


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

    def __init__(
        self,
        engine: Optional[PlaybackEngine] = None,
        send: Optional[Callable[[mido.Message], None]] = None,
        parent: Optional[QObject] = None,
        scheduler_interval_ms: int = SCHEDULER_INTERVAL_MS,
        position_interval_ms: int = POSITION_INTERVAL_MS,
    ):
        """
        Initialize the transport.

        :param engine: PlaybackEngine to drive. If not provided, creates one
        :param send: Callable that sends a mido.Message to the instrument
        :param parent: Optional QObject parent
        :param scheduler_interval_ms: How often due events are sent
        :param position_interval_ms: How often position_changed is emitted while playing
        """
        super().__init__(parent)
        self.engine = engine or PlaybackEngine()
        self.send = send
        self.engine.on_event = self._on_engine_event
        # Engine calls (and so MIDI sends) are serialised across both threads
        self._lock = threading.RLock()
        self._loaded = False
        self._last_state = self.engine.state
        self._last_tempo: Optional[int] = None
        self._scheduler: Optional[_SchedulerThread] = None
        self._scheduler_interval_ms = scheduler_interval_ms
        self._loop_range_ticks: Optional[tuple[int, int]] = None

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
        self._after_command()
        return True

    def pause(self) -> None:
        """Pause, keeping the position; sounding notes are released."""
        with self._lock:
            self.engine.pause()
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
        self._after_command()

    def seek_seconds(self, seconds: float) -> None:
        """Move to *seconds* without changing the play/pause/stop state."""
        with self._lock:
            self.engine.seek_seconds(seconds)
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
        self.loop_changed.emit()

    def clear_loop_range(self) -> None:
        """Loop the whole file instead of an A–B range (on/off is unchanged)."""
        with self._lock:
            self.engine.set_loop(self.engine.loop_enabled, None)
            self._loop_range_ticks = None
        self.loop_changed.emit()

    def set_speed(self, speed: float) -> None:
        """Set playback speed (1.0 = file tempo; 0.25–2.0)."""
        with self._lock:
            self.engine.set_speed(speed)
        self._last_tempo = None  # Re-announce the tempo for the new speed
        self._emit_position()

    def set_send_clock(self, enabled: bool) -> None:
        """Send MIDI clock, Start/Stop/Continue and Song Position Pointer."""
        with self._lock:
            self.engine.set_send_clock(enabled)

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
        if self._scheduler is not None:
            self._scheduler.quit()
            self._scheduler.wait()
            self._scheduler = None

    # --- Internals ----------------------------------------------------------

    def _on_engine_event(self, msg: mido.Message) -> None:
        if self.send is not None:
            self.send(msg)

    def _ensure_scheduler(self) -> None:
        if self._scheduler is not None and self._scheduler.isRunning():
            return
        self._scheduler = _SchedulerThread(
            self.engine, self._lock, self._scheduler_interval_ms
        )
        self._scheduler.ended.connect(self._on_scheduler_ended)
        self._scheduler.start()

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
        if playing and not self._position_timer.isActive():
            self._position_timer.start()
        elif not playing:
            self._position_timer.stop()
        if self.engine.state != self._last_state:
            self._last_state = self.engine.state
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
