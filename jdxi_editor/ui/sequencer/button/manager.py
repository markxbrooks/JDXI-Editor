"""
Sequencer Button Manager Module

Manages sequencer button state, styling, and synchronization with pattern measures.
Handles button clicks, note assignment, and UI updates.
"""

from typing import Callable, Dict, List, Optional, Tuple

from decologr import Decologr as log
from PySide6.QtWidgets import QComboBox

from jdxi_editor.midi.conversion.note import MidiNoteConverter


class NoteButtonAttrs:
    """Button attribute names."""

    NOTE = "note"
    NOTE_DURATION = "note_duration"
    NOTE_VELOCITY = "note_velocity"


class ButtonState:
    """Represents the state of a sequencer button."""

    def __init__(
        self,
        is_checked: bool = False,
        note: Optional[int] = None,
        velocity: int = 100,
        duration_ms: float = 120.0,
    ):
        """
        Initialize button state.

        :param is_checked: Whether button is activated
        :param note: MIDI note number
        :param velocity: Note velocity (0-127)
        :param duration_ms: Note duration in milliseconds
        """
        self.is_checked = is_checked
        self.note = note
        self.velocity = velocity
        self.duration_ms = duration_ms

    def is_active(self) -> bool:
        """Check if button has an active note."""
        return self.is_checked and self.note is not None


class SequencerButtonManager:
    """
    Manages sequencer button state and synchronization.

    Handles:
    - Button click events and state updates
    - Note assignment from combo box selectors
    - Button styling and highlighting
    - Synchronization with measure data
    - Tooltip updates
    """

    def __init__(
        self,
        midi_converter: Optional[MidiNoteConverter] = None,
        scope: str = "SequencerButtonManager",
    ):
        """
        Initialize button manager.

        :param midi_converter: MIDI note converter for note name conversion
        :param scope: Logging scope name
        """
        self.midi_converter = midi_converter
        self.scope = scope

        # Button grid (4 rows x 16 columns)
        self.buttons: List[List] = [[] for _ in range(4)]

        # Channel to selector mapping
        self.channel_map: Dict[int, QComboBox] = {}

        # Current state
        self.current_measure_index = 0
        self.current_step = 0
        self.total_steps = 16

        # Style generator callback
        self.style_generator: Optional[Callable] = None

        # Callbacks for events
        self.on_button_changed: Optional[Callable[[int, int, ButtonState], None]] = None
        self.on_measure_synced: Optional[Callable[[int], None]] = None

        # Default values
        self.default_velocity = 100
        self.default_duration_ms = 120.0
        self.get_current_duration: Optional[Callable[[], float]] = None
        self.get_current_velocity: Optional[Callable[[], int]] = None

    def set_buttons(self, buttons: List[List]) -> None:
        """
        Set the button grid.

        :param buttons: 2D list of buttons (4 rows x 16+ columns)
        """
        self.buttons = buttons

    def set_channel_map(self, channel_map: Dict[int, QComboBox]) -> None:
        """
        Set the row-to-selector mapping.

        :param channel_map: Dictionary mapping row (0-3) to QComboBox
        """
        self.channel_map = channel_map

    def set_style_generator(
        self,
        generator: Callable[[bool, bool, bool], str],
    ) -> None:
        """
        Set the style generator callback.

        Called with (is_checked, is_current, is_selected_bar) returns stylesheet.

        :param generator: Callback function
        """
        self.style_generator = generator

    def handle_button_click(
        self,
        button,
        checked: bool,
        measures: Optional[List] = None,
    ) -> None:
        """
        Handle a button click event.

        Updates button state, measure data, and UI.

        :param button: SequencerButton that was clicked
        :param checked: New checked state
        :param measures: List of PatternMeasure objects (optional)
        """
        try:
            # Don't allow checking disabled buttons
            if not button.isEnabled():
                return

            # Get current selector for this row
            selector = self.channel_map.get(button.row)

            if checked and selector is not None:
                # Get note from selector
                note_name = selector.currentText()
                midi_note = self._note_name_to_midi(note_name)
                button.note = midi_note

                # Set duration and velocity
                if (
                    not hasattr(button, NoteButtonAttrs.NOTE_DURATION)
                    or button.note_duration is None
                ):
                    button.note_duration = self._get_duration()
                if (
                    not hasattr(button, NoteButtonAttrs.NOTE_VELOCITY)
                    or button.note_velocity is None
                ):
                    button.note_velocity = self._get_velocity()

                # Sync button note spec
                self._sync_button_note_spec(button)

                # Update tooltip
                self._update_button_tooltip(button)

            # Update state in measures if provided
            if measures and 0 <= self.current_measure_index < len(measures):
                self._store_note_in_measures(button, checked, measures)

            # Update button style
            self._update_button_style(button)

            # Trigger callback
            if self.on_button_changed:
                state = self._get_button_state(button)
                self.on_button_changed(button.row, button.column, state)

            log.message(
                message=f"Button clicked: row {button.row}, col {button.column}, checked {checked}",
                scope=self.scope,
            )

        except Exception as ex:
            log.error(
                message=f"Error handling button click: {ex}",
                scope=self.scope,
            )

    def sync_sequencer_with_measure(
        self,
        bar_index: int,
        measures: List,
    ) -> None:
        """
        Synchronize sequencer buttons with a measure's data.

        Copies note data from the measure to the main sequencer buttons.

        :param bar_index: Index of the bar to sync from
        :param measures: List of PatternMeasure objects
        """
        try:
            if bar_index < 0 or bar_index >= len(measures):
                log.debug(
                    message=f"Invalid bar index: {bar_index}",
                    scope=self.scope,
                )
                return

            measure = measures[bar_index]

            # Sync each button
            for row in range(4):
                for step in range(min(16, len(self.buttons[row]))):
                    if step >= len(measure.buttons[row]):
                        continue

                    sequencer_button = self.buttons[row][step]
                    measure_button = measure.buttons[row][step]

                    # Copy checked state
                    self._update_button_state_silent(
                        sequencer_button,
                        measure_button.isChecked(),
                    )

                    # Copy note properties
                    sequencer_button.note = getattr(
                        measure_button,
                        NoteButtonAttrs.NOTE,
                        None,
                    )
                    sequencer_button.note_duration = getattr(
                        measure_button,
                        NoteButtonAttrs.NOTE_DURATION,
                        None,
                    )
                    sequencer_button.note_velocity = getattr(
                        measure_button,
                        NoteButtonAttrs.NOTE_VELOCITY,
                        None,
                    )

                    # Sync note spec
                    self._sync_button_note_spec(sequencer_button)

                    # Update tooltip
                    self._update_button_tooltip(sequencer_button)

                    # Update style
                    self._update_button_style(sequencer_button)

            log.message(
                message=f"Synced sequencer with measure {bar_index + 1}",
                scope=self.scope,
            )

            if self.on_measure_synced:
                self.on_measure_synced(bar_index)

        except Exception as ex:
            log.error(
                message=f"Error syncing sequencer with measure: {ex}",
                scope=self.scope,
            )

    def highlight_current_step(self, step: int) -> None:
        """
        Highlight the current playback step.

        Updates button styles to show which step is currently playing.

        :param step: Current step in bar (0-15)
        """
        try:
            for row in range(4):
                for col in range(min(16, len(self.buttons[row]))):
                    button = self.buttons[row][col]
                    is_current = col == step
                    self._update_button_style(button, is_current=is_current)

        except Exception as ex:
            log.error(
                message=f"Error highlighting current step: {ex}",
                scope=self.scope,
            )

    def highlight_bar(self, bar_index: int) -> None:
        """
        Highlight all buttons in the current bar display.

        :param bar_index: Index of bar being displayed
        """
        try:
            for row in range(4):
                for col in range(min(16, len(self.buttons[row]))):
                    button = self.buttons[row][col]
                    is_current = col == self.current_step
                    self._update_button_style(
                        button,
                        is_current=is_current,
                        is_selected_bar=True,
                    )

        except Exception as ex:
            log.error(
                message=f"Error highlighting bar: {ex}",
                scope=self.scope,
            )

    def reset_button(self, button) -> None:
        """
        Reset a button to its default state.

        Clears note data and unchecks the button.

        :param button: SequencerButton to reset
        """
        try:
            button.row = button.row  # Preserve row/column
            button.note = None
            button.note_duration = None
            button.note_velocity = None

            # Clear note spec
            if hasattr(button, "note_spec"):
                button.note_spec = self._create_empty_note_spec()

            # Update state
            self._update_button_state_silent(button, False)
            self._update_button_style(button)
            button.setToolTip("")

            log.debug(
                message=f"Reset button: row {button.row}, col {button.column}",
                scope=self.scope,
            )

        except Exception as ex:
            log.error(
                message=f"Error resetting button: {ex}",
                scope=self.scope,
            )

    def reset_all_buttons(self) -> None:
        """Reset all sequencer buttons."""
        try:
            for row in range(4):
                for button in self.buttons[row]:
                    self.reset_button(button)

            log.message(
                message="Reset all sequencer buttons",
                scope=self.scope,
            )

        except Exception as ex:
            log.error(
                message=f"Error resetting all buttons: {ex}",
                scope=self.scope,
            )

    def clear_row(self, row: int) -> None:
        """
        Clear all buttons in a specific row.

        :param row: Row index (0-3)
        """
        try:
            if 0 <= row < len(self.buttons):
                for button in self.buttons[row]:
                    self.reset_button(button)

                log.message(
                    message=f"Cleared row {row}",
                    scope=self.scope,
                )

        except Exception as ex:
            log.error(
                message=f"Error clearing row: {ex}",
                scope=self.scope,
            )

    def get_button_state(self, row: int, col: int) -> Optional[ButtonState]:
        """
        Get the current state of a button.

        :param row: Row index
        :param col: Column index
        :return: ButtonState or None if button doesn't exist
        """
        try:
            if 0 <= row < len(self.buttons) and 0 <= col < len(self.buttons[row]):
                button = self.buttons[row][col]
                return self._get_button_state(button)
        except Exception:
            pass

        return None

    def get_row_state(self, row: int) -> List[Optional[ButtonState]]:
        """
        Get the state of all buttons in a row.

        :param row: Row index (0-3)
        :return: List of ButtonState objects
        """
        try:
            if 0 <= row < len(self.buttons):
                return [self._get_button_state(btn) for btn in self.buttons[row]]
        except Exception:
            pass

        return []

    def set_button_note(
        self,
        row: int,
        col: int,
        note: int,
        velocity: int = 100,
        duration_ms: float = 120.0,
    ) -> bool:
        """
        Set a button's note data programmatically.

        :param row: Row index
        :param col: Column index
        :param note: MIDI note number
        :param velocity: Note velocity
        :param duration_ms: Note duration
        :return: True if successful
        """
        try:
            if 0 <= row < len(self.buttons) and 0 <= col < len(self.buttons[row]):
                button = self.buttons[row][col]
                button.note = note
                button.note_velocity = velocity
                button.note_duration = duration_ms
                self._sync_button_note_spec(button)
                self._update_button_tooltip(button)
                return True
        except Exception as ex:
            log.error(
                message=f"Error setting button note: {ex}",
                scope=self.scope,
            )

        return False

    def set_button_checked(self, row: int, col: int, checked: bool) -> bool:
        """
        Set a button's checked state programmatically.

        :param row: Row index
        :param col: Column index
        :param checked: New checked state
        :return: True if successful
        """
        try:
            if 0 <= row < len(self.buttons) and 0 <= col < len(self.buttons[row]):
                button = self.buttons[row][col]
                self._update_button_state_silent(button, checked)
                self._update_button_style(button)
                return True
        except Exception as ex:
            log.error(
                message=f"Error setting button checked state: {ex}",
                scope=self.scope,
            )

        return False

    def _store_note_in_measures(
        self,
        button,
        checked: bool,
        measures: List,
    ) -> None:
        """
        Store button state in the corresponding measure.

        :param button: SequencerButton
        :param checked: Whether button is checked
        :param measures: List of PatternMeasure objects
        """
        try:
            if self.current_measure_index >= len(measures):
                return

            measure = measures[self.current_measure_index]
            step_in_bar = button.column

            if button.row < len(measure.buttons) and step_in_bar < len(
                measure.buttons[button.row]
            ):

                measure_button = measure.buttons[button.row][step_in_bar]
                self._update_button_state_silent(measure_button, checked)

                if checked:
                    # Copy note data
                    measure_button.note = button.note
                    if hasattr(button, NoteButtonAttrs.NOTE_DURATION):
                        measure_button.note_duration = button.note_duration
                    if hasattr(button, NoteButtonAttrs.NOTE_VELOCITY):
                        measure_button.note_velocity = button.note_velocity
                    self._sync_button_note_spec(measure_button)
                else:
                    # Reset button
                    self._reset_button_internal(measure_button)

        except Exception as ex:
            log.error(
                message=f"Error storing note in measures: {ex}",
                scope=self.scope,
            )

    def _update_button_style(
        self,
        button,
        is_current: Optional[bool] = None,
        is_selected_bar: bool = True,
    ) -> None:
        """
        Update button visual style.

        :param button: Button to style
        :param is_current: Whether button is current step (optional)
        :param is_selected_bar: Whether button is in selected bar
        """
        try:
            if is_current is None:
                is_current = (self.current_step % self.total_steps) == button.column

            if self.style_generator:
                is_checked = button.isChecked()
                stylesheet = self.style_generator(
                    is_checked,
                    is_current,
                    is_selected_bar,
                )
                button.setStyleSheet(stylesheet)

        except Exception as ex:
            log.error(
                message=f"Error updating button style: {ex}",
                scope=self.scope,
            )

    def _update_button_tooltip(self, button) -> None:
        """
        Update button tooltip to show note name.

        :param button: SequencerButton
        """
        try:
            if button.note is None:
                button.setToolTip("")
                return

            if button.row == 3:  # Drums
                note_name = self._midi_to_note_name(button.note, drums=True)
            else:
                note_name = self._midi_to_note_name(button.note)

            button.setToolTip(f"Note: {note_name}")

        except Exception as ex:
            log.debug(
                message=f"Error updating tooltip: {ex}",
                scope=self.scope,
            )

    def _update_button_state_silent(self, button, checked: bool) -> None:
        """
        Update button checked state without signals.

        :param button: Button to update
        :param checked: New checked state
        """
        button.blockSignals(True)
        button.setChecked(checked)
        button.blockSignals(False)

    def _get_button_state(self, button) -> ButtonState:
        """
        Extract button state.

        :param button: SequencerButton
        :return: ButtonState object
        """
        return ButtonState(
            is_checked=button.isChecked(),
            note=getattr(button, NoteButtonAttrs.NOTE, None),
            velocity=getattr(
                button, NoteButtonAttrs.NOTE_VELOCITY, self.default_velocity
            ),
            duration_ms=getattr(
                button, NoteButtonAttrs.NOTE_DURATION, self.default_duration_ms
            ),
        )

    def _sync_button_note_spec(self, button) -> None:
        """
        Sync the button's note_spec from attributes.

        :param button: SequencerButton
        """
        try:
            # Try to create/update note_spec if available
            if hasattr(button, "note_spec"):
                note_spec = self._create_note_spec(
                    note=getattr(button, NoteButtonAttrs.NOTE, None),
                    duration_ms=getattr(
                        button, NoteButtonAttrs.NOTE_DURATION, self.default_duration_ms
                    ),
                    velocity=getattr(
                        button, NoteButtonAttrs.NOTE_VELOCITY, self.default_velocity
                    ),
                )
                button.note_spec = note_spec

        except Exception as ex:
            log.debug(
                message=f"Error syncing button note spec: {ex}",
                scope=self.scope,
            )

    def _create_note_spec(self, note, duration_ms, velocity):
        """
        Create a note specification object.

        :param note: MIDI note number
        :param duration_ms: Duration in milliseconds
        :param velocity: Velocity (0-127)
        :return: NoteButtonSpec-like object
        """

        class NoteSpec:
            def __init__(self, note, duration_ms, velocity):
                self.note = note
                self.duration_ms = duration_ms or 120
                self.velocity = velocity or 100
                self.is_active = note is not None

        return NoteSpec(note, duration_ms, velocity)

    def _create_empty_note_spec(self):
        """Create an empty note spec."""
        return self._create_note_spec(
            None, self.default_duration_ms, self.default_velocity
        )

    def _reset_button_internal(self, button) -> None:
        """Internal button reset (without logging)."""
        button.note = None
        button.note_duration = None
        button.note_velocity = None

        if hasattr(button, "note_spec"):
            button.note_spec = self._create_empty_note_spec()

        self._update_button_state_silent(button, False)
        button.setToolTip("")

    def _note_name_to_midi(self, note_name: str) -> Optional[int]:
        """
        Convert note name to MIDI number.

        :param note_name: Note name (e.g., 'C4')
        :return: MIDI note number or None
        """
        if self.midi_converter:
            try:
                return self.midi_converter.note_name_to_midi(note_name)
            except Exception:
                return None

        # Fallback to basic conversion
        return self._basic_note_name_to_midi(note_name)

    def _midi_to_note_name(self, midi_note: int, drums: bool = False) -> str:
        """
        Convert MIDI number to note name.

        :param midi_note: MIDI note number
        :param drums: Whether to use drum names
        :return: Note name (e.g., 'C4')
        """
        if self.midi_converter:
            return self.midi_converter.midi_to_note_name(midi_note, drums=drums)

        # Fallback
        if drums:
            return f"Drum({midi_note})"
        return f"Note({midi_note})"

    def _basic_note_name_to_midi(self, note_name: str) -> Optional[int]:
        """
        Basic note name to MIDI conversion (fallback).

        :param note_name: Note name
        :return: MIDI note or None
        """
        try:
            note_to_semitone = {
                "C": 0,
                "C#": 1,
                "D": 2,
                "D#": 3,
                "E": 4,
                "F": 5,
                "F#": 6,
                "G": 7,
                "G#": 8,
                "A": 9,
                "A#": 10,
                "B": 11,
            }

            if "#" in note_name:
                note = note_name[:-1]
                octave = int(note_name[-1])
            else:
                note = note_name[0]
                octave = int(note_name[1:])

            if note not in note_to_semitone:
                return None

            return (octave + 1) * 12 + note_to_semitone[note]

        except Exception:
            return None

    def _get_duration(self) -> float:
        """Get current default duration."""
        if self.get_current_duration:
            return self.get_current_duration()
        return self.default_duration_ms

    def _get_velocity(self) -> int:
        """Get current default velocity."""
        if self.get_current_velocity:
            return self.get_current_velocity()
        return self.default_velocity

    def set_midi_converter(self, converter: MidiNoteConverter) -> None:
        """
        Set the MIDI converter.

        :param converter: MidiNoteConverter instance
        """
        self.midi_converter = converter

    def set_defaults(
        self,
        velocity: int = 100,
        duration_ms: float = 120.0,
    ) -> None:
        """
        Set default velocity and duration.

        :param velocity: Default velocity
        :param duration_ms: Default duration
        """
        self.default_velocity = velocity
        self.default_duration_ms = duration_ms

    def highlight_measure(self, measure_index: int) -> None:
        """
        Highlight the current measure/bar in the sequencer display.

        Updates button styles to show the selected measure and the current step.
        Equivalent to highlight_bar; "measure" and "bar" are interchangeable.

        :param measure_index: Index of the measure being displayed
        """
        self.current_measure_index = measure_index
        self.highlight_bar(measure_index)
