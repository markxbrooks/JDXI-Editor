"""
Pattern Learner Module

Handles MIDI input learning for the Pattern Sequencer. Captures incoming MIDI notes
and records them into the pattern grid in real-time, supporting both note-on and
note-off events with automatic step advancement.
"""

from typing import Callable, Dict, List, Optional

from decologr import Decologr as log
from mido import Message
from picomidi.message.type import MidoMessageType

from jdxi_editor.midi.conversion.note import MidiNoteConverter


class PatternLearnerState:
    """Enumeration of learning states."""

    IDLE = "idle"
    LEARNING = "learning"
    STOPPED = "stopped"


class PatternLearnerConfig:
    """Configuration for the pattern learner."""

    def __init__(
        self,
        total_steps: int = 16,
        total_rows: int = 4,
        default_velocity: int = 100,
        default_duration_ms: float = 120.0,
    ):
        """
        Initialize learner configuration.

        :param total_steps: Number of steps per bar (default 16)
        :param total_rows: Number of rows (default 4)
        :param default_velocity: Default velocity for learned notes
        :param default_duration_ms: Default duration in milliseconds
        """
        self.total_steps = total_steps
        self.total_rows = total_rows
        self.default_velocity = default_velocity
        self.default_duration_ms = default_duration_ms


class PatternLearnerEvent:
    """Represents a learned pattern event."""

    def __init__(
        self,
        step: int,
        row: int,
        note: int,
        velocity: int,
        duration_ms: float,
    ):
        """
        Initialize a learned event.

        :param step: Step number (0-15)
        :param row: Row number (0-3)
        :param note: MIDI note number
        :param velocity: Note velocity (0-127)
        :param duration_ms: Note duration in milliseconds
        """
        self.step = step
        self.row = row
        self.note = note
        self.velocity = velocity
        self.duration_ms = duration_ms


class PatternLearner:
    """
    Learns pattern from incoming MIDI messages.

    Captures MIDI note-on and note-off events and records them into a pattern grid.
    Automatically advances through steps as notes are released.
    """

    def __init__(
        self,
        config: Optional[PatternLearnerConfig] = None,
        midi_converter: Optional[MidiNoteConverter] = None,
        scope: str = "PatternLearner",
    ):
        """
        Initialize the pattern learner.

        :param config: Learner configuration. Defaults to standard 16-step, 4-row configuration
        :param midi_converter: MIDI note converter for validating notes. If not provided,
                              uses default conversion without drum validation
        :param scope: Logging scope name
        """
        self.config = config or PatternLearnerConfig()
        self.midi_converter = midi_converter
        self.scope = scope

        # Learning state
        self.state = PatternLearnerState.IDLE
        self.current_step = 0
        self.current_measure_index = 0

        # Learned pattern storage
        # learned_pattern[row][step] = MIDI note number or None
        self.learned_pattern: List[List[Optional[int]]] = [
            [None] * self.config.total_steps for _ in range(self.config.total_rows)
        ]

        # Track which notes are currently active (for matching note-off events)
        # active_notes[midi_note] = row_index
        self.active_notes: Dict[int, int] = {}

        # MIDI track for recording raw messages
        from mido import MidiTrack
        self.midi_track = MidiTrack()

        # Callbacks for external event handling
        self.on_step_advance: Optional[Callable[[int], None]] = None
        self.on_note_learned: Optional[Callable[[PatternLearnerEvent], None]] = None
        self.on_learning_stopped: Optional[Callable[[], None]] = None
        self.on_learning_started: Optional[Callable[[], None]] = None

        # Events that occurred during learning
        self.learned_events: List[PatternLearnerEvent] = []

    def start_learning(self) -> None:
        """Start the pattern learning process."""
        if self.state == PatternLearnerState.LEARNING:
            log.debug(
                message="Learning already in progress",
                scope=self.scope,
            )
            return

        self.state = PatternLearnerState.LEARNING
        self.current_step = 0
        self.active_notes.clear()
        self.learned_pattern = [
            [None] * self.config.total_steps for _ in range(self.config.total_rows)
        ]
        self.learned_events.clear()
        self.midi_track = __import__("mido").MidiTrack()

        log.message(
            message="Pattern learning started",
            scope=self.scope,
        )

        if self.on_learning_started:
            self.on_learning_started()

    def stop_learning(self) -> None:
        """Stop the pattern learning process."""
        if self.state != PatternLearnerState.LEARNING:
            log.debug(
                message="No learning in progress",
                scope=self.scope,
            )
            return

        self.state = PatternLearnerState.STOPPED

        log.message(
            message=f"Pattern learning stopped after {self.current_step} steps",
            scope=self.scope,
        )

        if self.on_learning_stopped:
            self.on_learning_stopped()

    def process_midi_message(self, message: Message) -> None:
        """
        Process an incoming MIDI message during learning.

        Handles NOTE_ON (velocity > 0) and NOTE_OFF messages.
        Automatically advances the step when a note-off is received.

        :param message: Mido Message object
        """
        if self.state != PatternLearnerState.LEARNING:
            return

        try:
            if message.type == MidoMessageType.NOTE_ON and message.velocity > 0:
                self._handle_note_on(message)
            elif message.type == MidoMessageType.NOTE_OFF or (
                message.type == MidoMessageType.NOTE_ON and message.velocity == 0
            ):
                self._handle_note_off(message)
        except Exception as ex:
            log.error(
                message=f"Error processing MIDI message: {ex}",
                scope=self.scope,
            )

    def _handle_note_on(self, message: Message) -> None:
        """
        Handle a NOTE_ON message.

        Records the note in the learned pattern and marks it as active.

        :param message: Mido NOTE_ON message with velocity > 0
        """
        note = message.note
        velocity = message.velocity

        # Determine which row this note belongs to
        row = self._find_row_for_note(note)
        if row is None:
            log.debug(
                message=f"Note {note} does not match any row range",
                scope=self.scope,
            )
            return

        step_in_bar = self.current_step % self.config.total_steps

        # Record the note in the learned pattern
        self.learned_pattern[row][step_in_bar] = note
        self.active_notes[note] = row

        # Get default duration
        duration_ms = self.config.default_duration_ms

        # Create and store learned event
        event = PatternLearnerEvent(
            step=step_in_bar,
            row=row,
            note=note,
            velocity=velocity,
            duration_ms=duration_ms,
        )
        self.learned_events.append(event)

        # Add to MIDI track
        self.midi_track.append(
            Message(
                MidoMessageType.NOTE_ON,
                note=note,
                velocity=velocity,
                time=0,
            )
        )

        log.message(
            message=f"Note learned: row {row}, step {step_in_bar}, note {note}, velocity {velocity}",
            scope=self.scope,
        )

        if self.on_note_learned:
            self.on_note_learned(event)

    def _handle_note_off(self, message: Message) -> None:
        """
        Handle a NOTE_OFF message or NOTE_ON with velocity 0.

        Marks the note as inactive and advances to the next step.

        :param message: Mido NOTE_OFF message or NOTE_ON with velocity 0
        """
        note = message.note

        if note not in self.active_notes:
            log.debug(
                message=f"Note off for unrecognized note {note}",
                scope=self.scope,
            )
            return

        # Remove the note from active notes
        row = self.active_notes.pop(note)

        log.message(
            message=f"Note off: note {note} (row {row}) at step {self.current_step}",
            scope=self.scope,
        )

        # Add note_off to MIDI track
        self.midi_track.append(
            Message(MidoMessageType.NOTE_OFF, note=note, velocity=0, time=0)
        )

        # Advance to next step
        self._advance_step()

    def _advance_step(self) -> None:
        """Advance to the next step in the pattern."""
        prev_step = self.current_step
        self.current_step = (self.current_step + 1) % self.config.total_steps

        # Stop learning after completing one full bar (16 steps)
        if self.current_step == 0:
            log.message(
                message="Learning complete after one full bar (16 steps)",
                scope=self.scope,
            )
            self.stop_learning()
            return

        log.message(
            message=f"Advanced to step {self.current_step}",
            scope=self.scope,
        )

        if self.on_step_advance:
            self.on_step_advance(self.current_step)

    def _find_row_for_note(self, midi_note: int) -> Optional[int]:
        """
        Find the row that corresponds to a MIDI note.

        Uses the MIDI converter if available, otherwise falls back to hardcoded ranges.

        :param midi_note: MIDI note number
        :return: Row index (0-3) or None if note doesn't match any row
        """
        if self.midi_converter:
            for row in range(self.config.total_rows):
                if self.midi_converter.is_note_in_row_range(row, midi_note):
                    return row
            return None

        # Fallback to hardcoded ranges
        ranges = {
            0: range(60, 72),   # C4 to B4 (Digital Synth 1)
            1: range(60, 72),   # C4 to B4 (Digital Synth 2)
            2: range(48, 60),   # C3 to B3 (Analog Synth)
            3: range(36, 48),   # C2 to B2 (Drums)
        }

        for row, note_range in ranges.items():
            if midi_note in note_range:
                return row

        return None

    def clear_learned_pattern(self) -> None:
        """Clear the learned pattern and reset state."""
        self.learned_pattern = [
            [None] * self.config.total_steps for _ in range(self.config.total_rows)
        ]
        self.learned_events.clear()
        self.active_notes.clear()
        self.current_step = 0
        self.midi_track = __import__("mido").MidiTrack()

        log.message(
            message="Cleared learned pattern",
            scope=self.scope,
        )

    def get_learned_pattern(self) -> List[List[Optional[int]]]:
        """
        Get the learned pattern.

        :return: 2D list where pattern[row][step] = MIDI note number or None
        """
        return self.learned_pattern

    def get_learned_events(self) -> List[PatternLearnerEvent]:
        """
        Get all events that occurred during learning.

        :return: List of PatternLearnerEvent objects
        """
        return self.learned_events

    def get_pattern_for_row(self, row: int) -> List[Optional[int]]:
        """
        Get the learned pattern for a specific row.

        :param row: Row index (0-3)
        :return: List of MIDI notes for the row (or None for empty steps)
        """
        if 0 <= row < len(self.learned_pattern):
            return self.learned_pattern[row]
        return [None] * self.config.total_steps

    def get_midi_track(self):
        """
        Get the recorded MIDI track.

        :return: MidiTrack object with NOTE_ON and NOTE_OFF messages
        """
        return self.midi_track

    def is_learning(self) -> bool:
        """Check if currently learning."""
        return self.state == PatternLearnerState.LEARNING

    def set_config(self, config: PatternLearnerConfig) -> None:
        """
        Update the learner configuration.

        :param config: New configuration
        """
        self.config = config

    def set_midi_converter(self, converter: MidiNoteConverter) -> None:
        """
        Set or update the MIDI converter.

        :param converter: MidiNoteConverter instance
        """
        self.midi_converter = converter


# Example usage
if __name__ == "__main__":
    from jdxi_editor.midi.conversion.note import MidiNoteConverter

    # Create converter and learner
    converter = MidiNoteConverter()
    learner = PatternLearner(midi_converter=converter)

    # Set up callbacks
    def on_note_learned(event: PatternLearnerEvent):
        log.message(
            f"Note learned: Row {event.row}, Step {event.step}, "
            f"Note {event.note}, Velocity {event.velocity}"
        )

    def on_step_advance(step: int):
        log.message(f"Advanced to step {step}")

    learner.on_note_learned = on_note_learned
    learner.on_step_advance = on_step_advance

    # Simulate learning
    learner.start_learning()

    # Simulate some MIDI input
    learner.process_midi_message(
        Message(MidoMessageType.NOTE_ON, note=60, velocity=100)
    )
    learner.process_midi_message(
        Message(MidoMessageType.NOTE_OFF, note=60, velocity=0)
    )
    learner.process_midi_message(
        Message(MidoMessageType.NOTE_ON, note=64, velocity=80)
    )
    learner.process_midi_message(
        Message(MidoMessageType.NOTE_OFF, note=64, velocity=0)
    )

    # Get results
    log.message("\nLearned pattern:", learner.get_learned_pattern())
    log.message("Learned events:", len(learner.get_learned_events()))