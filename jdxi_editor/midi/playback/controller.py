"""
Pattern Playback Controller Module

Manages MIDI pattern playback using the PlaybackEngine. Handles:
- Starting/stopping/pausing playback
- Building MIDI files from patterns
- UI synchronization during playback
- Muting/unmuting channels
- Shuffle play functionality
"""

import random
from typing import Callable, Dict, List, Optional, Any

from decologr import Decologr as log
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo
from picomidi.core.tempo import bpm_to_ticks
from picomidi.message.type import MidoMetaMessageType
from picomidi.messages.note import note_off, note_on, build_midi_note
from picomidi.playback.engine import (
    PlaybackEngine,
    TransportState,
)
from picomidi.playback.worker import MidiPlaybackWorker
from picomidi.sequencer.event import SequencerEvent
from picomidi.ui.widget.button.note import NoteButtonEvent
from PySide6.QtCore import QObject, Qt, QTimer


class PlaybackConfig:
    """Configuration for playback controller."""

    def __init__(
        self,
        ticks_per_beat: int = 480,
        beats_per_measure: int = 4,
        measure_beats: int = 16,
        default_bpm: int = 120,
        playback_interval_ms: int = 20,
    ):
        """
        Initialize playback configuration.

        :param ticks_per_beat: MIDI ticks per beat
        :param beats_per_measure: Beats per measure (4/4 time)
        :param measure_beats: Beats per measure for sequencer display
        :param default_bpm: Default tempo
        :param playback_interval_ms: Timer interval for playback updates
        """
        self.ticks_per_beat = ticks_per_beat
        self.beats_per_measure = beats_per_measure
        self.measure_beats = measure_beats
        self.default_bpm = default_bpm
        self.playback_interval_ms = playback_interval_ms

    @property
    def ticks_per_measure(self) -> int:
        """Calculate ticks per bar."""
        return self.ticks_per_beat * self.beats_per_measure


class PlaybackPosition:
    """Represents the current playback position."""

    def __init__(self, global_step: int = 0, bar_index: int = 0, step_in_bar: int = 0):
        """
        Initialize playback position.

        :param global_step: Current step across all bars
        :param bar_index: Current bar index
        :param step_in_bar: Current step within bar
        """
        self.global_step = global_step
        self.bar_index = bar_index
        self.step_in_bar = step_in_bar


class PatternPlaybackController(QObject):
    """
    Controls pattern playback and synchronization.

    Manages:
    - PlaybackEngine operation
    - UI updates during playback (bar/step highlighting)
    - Muting/unmuting channels
    - Pause/resume functionality
    - Shuffle play
    """

    def __init__(
        self,
        config: Optional[PlaybackConfig] = None,
        playback_engine: Optional[PlaybackEngine] = None,
        scope: str = "PatternPlaybackController",
    ):
        """
        Initialize playback controller.

        :param config: Playback configuration
        :param playback_engine: PlaybackEngine instance. If not provided, creates one
        :param scope: Logging scope name
        """
        super().__init__()
        self.config = config or PlaybackConfig()
        self.playback_engine = playback_engine or PlaybackEngine()
        self.scope = scope

        # Playback state
        self.is_playing = False
        self.is_paused = False
        self.current_bpm = self.config.default_bpm

        # Position tracking
        self.current_position = PlaybackPosition()
        self.last_bar_index = -1
        self.last_step_in_bar = -1

        # Mute state
        self.muted_channels: List[int] = []

        # Timer for driving playback
        self.timer: Optional[QTimer] = None

        self.worker = MidiPlaybackWorker(parent=self)

        # Callbacks for UI updates
        self.on_playback_started: Optional[Callable[[], None]] = None
        self.on_playback_stopped: Optional[Callable[[], None]] = None
        self.on_playback_paused: Optional[Callable[[], None]] = None
        self.on_playback_resumed: Optional[Callable[[], None]] = None
        self.on_position_changed: Optional[Callable[[PlaybackPosition], None]] = None
        self.on_bar_changed: Optional[Callable[[int], None]] = None
        self.on_step_changed: Optional[Callable[[int], None]] = None

        # Callback for MIDI event sending
        self.on_midi_event: Optional[Callable[[Message], Any]] = None

    def start_playback(
        self,
        measures: List,
        bpm: Optional[int] = None,
    ) -> bool:
        """
        Start pattern playback.

        :param measures: List of PatternMeasure objects to play
        :param bpm: Optional tempo override
        :return: True if playback started successfully
        """
        if self.is_playing:
            log.debug(
                message="Playback already in progress",
                scope=self.scope,
            )
            return False

        if not measures:
            log.warning(
                message="No measures to play",
                scope=self.scope,
            )
            return False

        try:
            # Set tempo if provided
            if bpm is not None:
                self.current_bpm = bpm

            # Build MIDI file from measures
            midi_file = self._build_midi_file_for_playback(measures)

            # Check if there are any notes to play
            if len(midi_file.tracks[0]) <= 1:
                log.message(
                    message="Pattern has no notes to play",
                    scope=self.scope,
                )
                return False

            # Configure and start engine
            self.playback_engine.load_file(midi_file)

            # Apply mute state
            for channel in range(16):
                self.playback_engine.mute_channel(
                    channel, channel in self.muted_channels
                )

            # Set MIDI event callback
            if self.on_midi_event:
                self.playback_engine.on_event = lambda msg: self.on_midi_event(msg)

            # Start engine
            self.playback_engine.start(0)

            # Setup worker for MIDI playback (drives engine.process_until_now)
            self.worker.setup(
                buffered_msgs=[],
                midi_out_port=None,
                ticks_per_beat=midi_file.ticks_per_beat,
                play_program_changes=True,
                start_time=None,
                initial_tempo=bpm2tempo(self.current_bpm),
                playback_engine=self.playback_engine,
            )
            self.worker.finished.connect(self._on_worker_finished)

            # Initialize position tracking
            self.current_position = PlaybackPosition()
            self.last_bar_index = -1
            self.last_step_in_bar = -1

            # Start timer
            self._start_timer()

            # Mark as playing
            self.is_playing = True
            self.is_paused = False

            tempo_us = bpm2tempo(self.current_bpm)
            log.message(
                message=(
                    f"Pattern playback started: {self.current_bpm} BPM "
                    f"(tempo={tempo_us} µs/beat)"
                ),
                scope=self.scope,
            )

            if self.on_playback_started:
                self.on_playback_started()

            return True

        except Exception as ex:
            log.error(
                message=f"Error starting playback: {ex}",
                scope=self.scope,
            )
            return False

    def _on_worker_finished(self) -> None:
        """Handle worker.finished when engine stops playing."""
        if self.is_playing:
            self.stop_playback()

    def stop_playback(self) -> None:
        """Stop pattern playback."""
        if not self.is_playing:
            return

        try:
            self.worker.stop()
            self.playback_engine.stop()
            try:
                self.worker.finished.disconnect(self._on_worker_finished)
            except (TypeError, RuntimeError):
                pass

            # Stop timer
            self._stop_timer()

            # Reset state
            self.is_playing = False
            self.is_paused = False
            self.current_position = PlaybackPosition()

            log.message(
                message="Pattern playback stopped",
                scope=self.scope,
            )

            if self.on_playback_stopped:
                self.on_playback_stopped()

        except Exception as ex:
            log.error(
                message=f"Error stopping playback: {ex}",
                scope=self.scope,
            )

    def pause_playback(self) -> None:
        """Pause pattern playback (can be resumed)."""
        if not self.is_playing or self.is_paused:
            return

        try:
            if self.timer:
                self.timer.stop()
            self.is_paused = True

            log.message(
                message="Pattern playback paused",
                scope=self.scope,
            )

            if self.on_playback_paused:
                self.on_playback_paused()

        except Exception as ex:
            log.error(
                message=f"Error pausing playback: {ex}",
                scope=self.scope,
            )

    def resume_playback(self) -> None:
        """Resume paused playback."""
        if not self.is_playing or not self.is_paused:
            return

        try:
            if self.timer:
                self._update_timer_interval()
                self.timer.start()
            self.is_paused = False

            log.message(
                message="Pattern playback resumed",
                scope=self.scope,
            )

            if self.on_playback_resumed:
                self.on_playback_resumed()

        except Exception as ex:
            log.error(
                message=f"Error resuming playback: {ex}",
                scope=self.scope,
            )

    def toggle_pause(self) -> None:
        """Toggle pause/resume state."""
        if self.is_paused:
            self.resume_playback()
        else:
            self.pause_playback()

    def shuffle_play(
        self,
        measures: List,
        bpm: Optional[int] = None,
    ) -> bool:
        """
        Select a random bar and start playback.

        :param measures: List of PatternMeasure objects
        :param bpm: Optional tempo override
        :return: True if playback started
        """
        if not measures:
            log.warning(
                message="No measures for shuffle play",
                scope=self.scope,
            )
            return False

        try:
            # Select random bar
            random_bar_index = random.randint(0, len(measures) - 1)

            log.message(
                message=f"Shuffle play: starting from bar {random_bar_index + 1}",
                scope=self.scope,
            )

            # Trigger callback for UI to select the bar
            if self.on_bar_changed:
                self.on_bar_changed(random_bar_index)

            # Start playback
            return self.start_playback(measures, bpm)

        except Exception as ex:
            log.error(
                message=f"Error starting shuffle play: {ex}",
                scope=self.scope,
            )
            return False

    def mute_channel(self, channel: int, mute: bool = True) -> None:
        """
        Mute or unmute a specific MIDI channel.

        :param channel: MIDI channel (0-15)
        :param mute: True to mute, False to unmute
        """
        if mute:
            if channel not in self.muted_channels:
                self.muted_channels.append(channel)
                log.message(
                    message=f"Channel {channel} muted",
                    scope=self.scope,
                )
        else:
            if channel in self.muted_channels:
                self.muted_channels.remove(channel)
                log.message(
                    message=f"Channel {channel} unmuted",
                    scope=self.scope,
                )

        # Update engine if playing
        if self.is_playing:
            self.playback_engine.mute_channel(channel, mute)

    def mute_row(self, row: int, mute: bool = True) -> None:
        """
        Mute or unmute a sequencer row.

        Row to channel mapping:
        - Row 0: Channel 0 (Digital Synth 1)
        - Row 1: Channel 1 (Digital Synth 2)
        - Row 2: Channel 2 (Analog Synth)
        - Row 3: Channel 9 (Drums)

        :param row: Row index (0-3)
        :param mute: True to mute, False to unmute
        """
        channel = row if row < 3 else 9
        self.mute_channel(channel, mute)

    def toggle_mute_row(self, row: int) -> bool:
        """
        Toggle mute for a row.

        :param row: Row index (0-3)
        :return: New mute state (True if now muted)
        """
        channel = row if row < 3 else 9
        is_muted = channel in self.muted_channels
        self.mute_channel(channel, not is_muted)
        return not is_muted

    def is_row_muted(self, row: int) -> bool:
        """
        Check if a row is muted.

        :param row: Row index (0-3)
        :return: True if row is muted
        """
        channel = row if row < 3 else 9
        return channel in self.muted_channels

    def process_playback_tick(self, total_steps: int) -> Optional[PlaybackPosition]:
        """
        Process a playback timer tick.

        Called by timer. Updates engine and returns current position.

        :param total_steps: Total steps in pattern (bars * steps_per_bar)
        :return: Updated PlaybackPosition or None if playback has stopped
        """
        if not self.is_playing or self.is_paused:
            return None

        try:
            # Drive engine via worker (same pattern as MIDI file editor)
            self.worker.do_work()

            # Calculate current position from engine state
            tick = self._get_engine_tick()
            ticks_per_step = self.config.ticks_per_beat // 4  # 16th notes
            global_step = (
                (tick // ticks_per_step) % total_steps if total_steps > 0 else 0
            )

            self.current_position.global_step = global_step
            self.current_position.bar_index = global_step // self.config.measure_beats
            self.current_position.step_in_bar = global_step % self.config.measure_beats

            # Trigger callbacks for changes
            if self.current_position.bar_index != self.last_bar_index:
                self.last_bar_index = self.current_position.bar_index
                if self.on_bar_changed:
                    self.on_bar_changed(self.current_position.bar_index)

            if self.current_position.step_in_bar != self.last_step_in_bar:
                self.last_step_in_bar = self.current_position.step_in_bar
                if self.on_step_changed:
                    self.on_step_changed(self.current_position.step_in_bar)

            if self.on_position_changed:
                self.on_position_changed(self.current_position)

            # Check if engine has finished
            if self.playback_engine.state == TransportState.STOPPED:
                self.stop_playback()
                return None

            return self.current_position

        except Exception as ex:
            log.error(
                message=f"Error during playback tick: {ex}",
                scope=self.scope,
            )
            return None

    def get_current_position(self) -> PlaybackPosition:
        """
        Get the current playback position.

        :return: PlaybackPosition object
        """
        return self.current_position

    def get_playback_state(self) -> Dict[str, bool]:
        """
        Get the current playback state.

        :return: Dictionary with is_playing, is_paused, muted_channels
        """
        return {
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "muted_channels": self.muted_channels.copy(),
        }

    def set_tempo(self, bpm: int) -> None:
        """
        Set playback tempo.

        :param bpm: Tempo in BPM
        """
        bpm = max(20, min(300, bpm))
        self.current_bpm = bpm

        # Update timer interval if playing
        if self.is_playing and self.timer:
            self._update_timer_interval()

        log.message(
            message=f"Playback tempo set to {bpm} BPM",
            scope=self.scope,
        )

    def reload_playback_with_tempo(self, measures: List, bpm: int) -> bool:
        """
        Rebuild MIDI with new tempo and resume from current position.
        Call when tempo changes during playback.

        :param measures: Current pattern measures
        :param bpm: New tempo in BPM
        :return: True if reload succeeded
        """
        if not self.is_playing or self.is_paused:
            return False
        try:
            tick = self._get_engine_tick()
            self.current_bpm = max(20, min(300, bpm))
            midi_file = self._build_midi_file_for_playback(measures)
            self.playback_engine.load_file(midi_file)
            for ch in range(16):
                self.playback_engine.mute_channel(ch, ch in self.muted_channels)
            if self.on_midi_event:
                self.playback_engine.on_event = lambda m: self.on_midi_event(m)
            self.playback_engine.start(tick)
            return True
        except Exception as ex:
            log.error(
                message=f"Error reloading playback tempo: {ex}",
                scope=self.scope,
            )
            return False

    def get_tempo(self) -> int:
        """Get current playback tempo."""
        return self.current_bpm

    def _build_midi_file_for_playback(self, measures: List) -> MidiFile:
        """
        Build a MIDI file from the pattern for playback.

        :param measures: List of PatternMeasure objects
        :return: MidiFile ready for playback
        """
        midi_file = MidiFile(
            type=1,
            ticks_per_beat=self.config.ticks_per_beat,
        )
        track = MidiTrack()
        midi_file.tracks.append(track)

        # Add tempo (use mido.bpm2tempo to match Playback Worker / MIDI editor)
        tempo_us = bpm2tempo(self.current_bpm)
        track.append(
            MetaMessage(
                MidoMetaMessageType.SET_TEMPO.value,
                tempo=tempo_us,
                time=0,
            )
        )

        # Collect all events
        events: List[SequencerEvent] = self._collect_sequencer_events(measures)

        if not events:
            return midi_file

        # Convert events to MIDI messages with absolute timing
        midi_events = []

        for e in events:
            note = build_midi_note(event=e, channel=e.channel, bpm=self.current_bpm)
            midi_events.extend(
                [
                    (e.tick, note_on(note)),
                    (e.tick + e.duration_ticks, note_off(note)),
                ]
            )

        # Sort by tick and convert to relative time
        midi_events.sort(key=lambda x: x[0])

        prev_tick = 0
        for tick, msg in midi_events:
            msg.time = tick - prev_tick
            track.append(msg)
            prev_tick = tick

        return midi_file

    def _collect_sequencer_events(self, measures: List) -> List[SequencerEvent]:
        """
        Collect all note events from measures.

        :param measures: List of PatternMeasure objects
        :return: List of SequencerEvent objects
        """
        ticks_per_step = self.config.ticks_per_beat // 4
        events: List[SequencerEvent] = []

        for bar_index, measure in enumerate(measures):
            for step in range(min(self.config.measure_beats, 16)):
                # Skip if step is beyond measure buttons
                tick = (bar_index * self.config.measure_beats + step) * ticks_per_step

                for row in range(4):
                    # Skip if row is muted
                    channel = row if row < 3 else 9
                    if channel in self.muted_channels:
                        continue

                    # Skip if step is beyond buttons in row
                    if step >= len(measure.buttons[row]):
                        continue

                    button = measure.buttons[row][step]

                    # Skip unchecked buttons
                    if not button.isChecked():
                        continue

                    # Get note spec
                    spec = self._get_button_note_spec(button)
                    if not spec or not spec.is_active:
                        continue

                    # Validate velocity
                    velocity = max(0, min(127, spec.velocity))

                    # Calculate duration
                    duration_ticks = (
                        self._ms_to_ticks(spec.duration_ms) or ticks_per_step
                    )

                    events.append(
                        self._sequencer_event(
                            channel, duration_ticks, spec, tick, velocity
                        )
                    )

        return events

    def _sequencer_event(
        self,
        channel: int,
        duration_ticks: int,
        spec: NoteButtonEvent,
        tick: int,
        velocity: int,
    ) -> SequencerEvent:
        """add sequencer event"""
        return SequencerEvent(
            tick=tick,
            note=spec.note,
            velocity=velocity,
            channel=channel,
            duration_ticks=duration_ticks,
        )

    def _ms_to_ticks(self, duration_ms: float) -> int:
        """
        Convert milliseconds to MIDI ticks.

        Formula: ticks = (duration_ms / 1000) * (bpm / 60) * ticks_per_beat

        :param duration_ms: Duration in milliseconds
        :return: Duration in MIDI ticks
        """
        if duration_ms <= 0:
            return 0
        bpm = self.current_bpm
        ticks_per_beat = self.config.ticks_per_beat
        ticks = bpm_to_ticks(bpm, duration_ms, ticks_per_beat)
        return max(1, int(ticks))

    def _get_button_note_spec(self, button):
        """
        Get note specification from a button.

        :param button: SequencerButton instance
        :return: NoteButtonSpec with note, duration_ms, velocity, is_active
        """
        from jdxi_editor.ui.editors.pattern.helper import get_button_note_spec

        return get_button_note_spec(button)

    def _get_engine_tick(self) -> int:
        """
        Get the current tick position from the playback engine.

        :return: Absolute tick position
        """
        try:
            if self.playback_engine.events:
                idx = self.playback_engine.event_index
                if idx > 0 and idx <= len(self.playback_engine.events):
                    return self.playback_engine.events[idx - 1].absolute_tick
                else:
                    return self.playback_engine.start_tick
            return 0
        except Exception:
            return 0

    def _start_timer(self) -> None:
        """Start the playback timer."""
        if self.timer and self.timer.isActive():
            return

        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._update_timer_interval()
        # Note: timeout connection must be handled by the UI

    def _stop_timer(self) -> None:
        """Stop the playback timer."""
        if self.timer:
            self.timer.stop()
            self.timer = None

    def _update_timer_interval(self) -> None:
        """Update timer interval based on current tempo."""
        if self.timer:
            # Use a short interval for smooth playback
            self.timer.setInterval(self.config.playback_interval_ms)

    def set_config(self, config: PlaybackConfig) -> None:
        """
        Update controller configuration.

        :param config: New PlaybackConfig
        """
        self.config = config

    def get_engine(self) -> PlaybackEngine:
        """
        Get the underlying PlaybackEngine.

        Useful for advanced control if needed.

        :return: PlaybackEngine instance
        """
        return self.playback_engine
