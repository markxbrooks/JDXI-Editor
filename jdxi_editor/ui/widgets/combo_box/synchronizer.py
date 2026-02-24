"""
ComboBox Synchronizer Module

Manages synchronization between MIDI input/output and combo box selectors.
Handles real-time note-to-selector mapping and drum kit selection updates.
"""

from typing import Callable, Dict, List, Optional

import mido

from decologr import Decologr as log
from mido import Message
from picomidi.message.type import MidoMessageType
from PySide6.QtWidgets import QComboBox
from rtmidi.midiconstants import CONTROL_CHANGE, NOTE_OFF, NOTE_ON

from jdxi_editor.globals import silence_midi_note_logging
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.conversion.note import MidiNoteConverter
from jdxi_editor.midi.message import MidiMessage


class ComboBoxUpdateConfig:
    """Configuration for combo box synchronization."""

    def __init__(
        self,
        silence_logging: bool = False,
        min_note: int = 36,  # C2
        update_interval_ms: int = 100,
    ):
        """
        Initialize synchronizer configuration.

        :param silence_logging: Whether to suppress MIDI note logging
        :param min_note: Minimum MIDI note to process (default C2 = 36)
        :param update_interval_ms: Minimum time between updates (milliseconds)
        """
        self.silence_logging = silence_logging
        self.min_note = min_note
        self.update_interval_ms = update_interval_ms


class ComboBoxState:
    """Represents the state of a combo box selector."""

    def __init__(
        self,
        row: int,
        current_index: int,
        current_text: str,
        note: Optional[int] = None,
    ):
        """
        Initialize combo box state.

        :param row: Row index (0-3)
        :param current_index: Currently selected item index
        :param current_text: Currently selected item text
        :param note: Associated MIDI note (if any)
        """
        self.row = row
        self.current_index = current_index
        self.current_text = current_text
        self.note = note


class ComboBoxSynchronizer:
    """
    Synchronizes MIDI messages with combo box selectors.

    Handles:
    - Incoming MIDI note-to-selector mapping
    - Outgoing MIDI message parsing
    - Drum kit selection updates
    - Selector state management
    - Channel-to-selector routing
    """

    # Channel to row mapping
    CHANNEL_TO_ROW = {
        MidiChannel.DIGITAL_SYNTH_1: 0,  # Channel 0
        MidiChannel.DIGITAL_SYNTH_2: 1,  # Channel 1
        MidiChannel.ANALOG_SYNTH: 2,  # Channel 2
        MidiChannel.DRUM_KIT: 3,  # Channel 9
    }

    ROW_TO_CHANNEL = {v: k for k, v in CHANNEL_TO_ROW.items()}

    def __init__(
        self,
        config: Optional[ComboBoxUpdateConfig] = None,
        midi_converter: Optional[MidiNoteConverter] = None,
        scope: str = "ComboBoxSynchronizer",
    ):
        """
        Initialize the synchronizer.

        :param config: Synchronizer configuration
        :param midi_converter: MIDI note converter
        :param scope: Logging scope name
        """
        self.config = config or ComboBoxUpdateConfig()
        self.midi_converter = midi_converter
        self.scope = scope

        # Selector mapping: row (0-3) -> QComboBox
        self.selectors: Dict[int, QComboBox] = {}

        # Options for each row
        self.row_options: Dict[int, List[str]] = {
            0: [],  # Digital Synth 1
            1: [],  # Digital Synth 2
            2: [],  # Analog Synth
            3: [],  # Drums
        }

        # Last update times for rate limiting
        self.last_update_time: Dict[int, float] = {}

        # Callbacks
        self.on_selector_changed: Optional[Callable[[ComboBoxState], None]] = None
        self.on_drum_kit_changed: Optional[Callable[[str], None]] = None
        self.on_note_received: Optional[Callable[[int, int], None]] = None

    def set_selector(self, row: int, combo_box: QComboBox) -> None:
        """
        Register a selector combo box for a row.

        :param row: Row index (0-3)
        :param combo_box: QComboBox widget
        """
        if 0 <= row <= 3:
            self.selectors[row] = combo_box
            log.debug(
                message=f"Registered selector for row {row}",
                scope=self.scope,
            )

    def set_selector_options(self, row: int, options: List[str]) -> None:
        """
        Set the available options for a selector.

        :param row: Row index (0-3)
        :param options: List of option strings
        """
        if 0 <= row <= 3:
            self.row_options[row] = options
            log.debug(
                message=f"Set {len(options)} options for row {row}",
                scope=self.scope,
            )

    def set_all_selectors(
        self,
        digital1: QComboBox,
        digital2: QComboBox,
        analog: QComboBox,
        drums: QComboBox,
    ) -> None:
        """
        Set all selector combo boxes at once.

        :param digital1: Digital Synth 1 selector
        :param digital2: Digital Synth 2 selector
        :param analog: Analog Synth selector
        :param drums: Drum kit selector
        """
        self.selectors[0] = digital1
        self.selectors[1] = digital2
        self.selectors[2] = analog
        self.selectors[3] = drums

        log.message(
            message="Set all selectors",
            scope=self.scope,
        )

    def process_incoming_midi(self, message) -> None:
        """
        Process an incoming MIDI message.

        Updates selectors based on incoming notes.

        :param message: Mido Message object
        """
        try:
            if not isinstance(message, Message):
                return

            if message.type == MidoMessageType.NOTE_ON and message.velocity > 0:
                self._handle_note_on(message)

        except Exception as ex:
            log.debug(
                message=f"Error processing incoming MIDI: {ex}",
                scope=self.scope,
            )

    def process_outgoing_midi(self, message) -> None:
        """
        Process an outgoing MIDI message.

        Converts raw or partial messages to mido Message and updates selectors.

        :param message: List[int], tuple, or mido.Message
        """
        try:
            if isinstance(message, Message):
                self._handle_note_on(message)
                return

            # Convert raw message list to mido Message
            if isinstance(message, (list, tuple)) and len(message) >= 2:
                status_byte = message[0]
                note = message[1]
                velocity = message[2] if len(message) > 2 else 0

                # Extract message type and channel from status byte
                msg_status = status_byte & MidiMessage.MIDI_STATUS_MASK

                if msg_status in (NOTE_ON, NOTE_OFF):
                    channel = status_byte & 0x0F
                    msg_type = (
                        MidoMessageType.NOTE_ON
                        if msg_status == NOTE_ON and velocity > 0
                        else MidoMessageType.NOTE_OFF
                    )

                    # Create mido Message
                    mido_msg = Message(
                        msg_type,
                        note=note,
                        velocity=velocity,
                        channel=channel,
                    )
                    self._handle_note_on(mido_msg)

        except Exception as ex:
            log.debug(
                message=f"Error processing outgoing MIDI: {ex}",
                scope=self.scope,
            )

    def set_selector_by_note(
        self,
        row: int,
        midi_note: int,
    ) -> bool:
        """
        Update a selector based on a MIDI note.

        :param row: Row index (0-3)
        :param midi_note: MIDI note number
        :return: True if selector was updated
        """
        try:
            if row not in self.selectors:
                return False

            combo_index = self._note_to_combo_index(row, midi_note)
            if combo_index is None:
                return False

            selector = self.selectors[row]
            if combo_index < selector.count():
                self._set_selector_index_silent(selector, combo_index)
                return True

        except Exception as ex:
            log.debug(
                message=f"Error setting selector by note: {ex}",
                scope=self.scope,
            )

        return False

    def set_selector_by_text(
        self,
        row: int,
        text: str,
    ) -> bool:
        """
        Update a selector by text value.

        :param row: Row index (0-3)
        :param text: Item text to select
        :return: True if selector was updated
        """
        try:
            if row not in self.selectors:
                return False

            selector = self.selectors[row]
            index = selector.findText(text)

            if index >= 0:
                self._set_selector_index_silent(selector, index)
                return True

        except Exception as ex:
            log.debug(
                message=f"Error setting selector by text: {ex}",
                scope=self.scope,
            )

        return False

    def set_drum_kit(self, kit_name: str) -> bool:
        """
        Change the drum kit selection.

        :param kit_name: Name of the drum kit
        :return: True if drum kit was changed
        """
        try:
            if 3 not in self.selectors:
                return False

            return self.set_selector_by_text(3, kit_name)

        except Exception as ex:
            log.error(
                message=f"Error setting drum kit: {ex}",
                scope=self.scope,
            )

        return False

    def get_selector_state(self, row: int) -> Optional[ComboBoxState]:
        """
        Get the current state of a selector.

        :param row: Row index (0-3)
        :return: ComboBoxState or None
        """
        try:
            if row not in self.selectors:
                return None

            selector = self.selectors[row]
            return ComboBoxState(
                row=row,
                current_index=selector.currentIndex(),
                current_text=selector.currentText(),
                note=self._text_to_note(row, selector.currentText()),
            )

        except Exception:
            return None

    def get_all_selector_states(self) -> Dict[int, ComboBoxState]:
        """
        Get the state of all selectors.

        :return: Dictionary mapping row to ComboBoxState
        """
        states = {}
        for row in range(4):
            state = self.get_selector_state(row)
            if state:
                states[row] = state
        return states

    def get_selected_note(self, row: int) -> Optional[int]:
        """
        Get the MIDI note corresponding to the currently selected item in a selector.

        :param row: Row index (0-3)
        :return: MIDI note number or None
        """
        try:
            if row not in self.selectors:
                return None

            selector = self.selectors[row]
            note_name = selector.currentText()
            return self._text_to_note(row, note_name)

        except Exception:
            return None

    def enable_selector(self, row: int, enabled: bool = True) -> None:
        """
        Enable or disable a selector.

        :param row: Row index (0-3)
        :param enabled: Whether to enable the selector
        """
        try:
            if row in self.selectors:
                self.selectors[row].setEnabled(enabled)

        except Exception as ex:
            log.debug(
                message=f"Error enabling selector: {ex}",
                scope=self.scope,
            )

    def enable_all_selectors(self, enabled: bool = True) -> None:
        """
        Enable or disable all selectors.

        :param enabled: Whether to enable selectors
        """
        for row in range(4):
            self.enable_selector(row, enabled)

    def reset_selectors(self) -> None:
        """Reset all selectors to their first item."""
        try:
            for row in range(4):
                if row in self.selectors:
                    self._set_selector_index_silent(self.selectors[row], 0)

            log.message(
                message="Reset all selectors",
                scope=self.scope,
            )

        except Exception as ex:
            log.error(
                message=f"Error resetting selectors: {ex}",
                scope=self.scope,
            )

    def _handle_note_on(self, message: mido.Message) -> None:
        """
        Handle a NOTE_ON message.

        Updates the appropriate selector based on channel and note.

        :param message: Mido NOTE_ON message with velocity > 0
        """
        note = message.note
        channel = message.channel

        # Log the message if not silenced
        if not silence_midi_note_logging():
            log.message(
                message=f"MIDI note: {note}, channel: {channel}",
                scope=self.scope,
            )

        # Skip notes below minimum
        if note < self.config.min_note:
            log.debug(
                message=f"Note {note} is below minimum {self.config.min_note}, skipping",
                scope=self.scope,
            )
            return

        # Map channel to row
        if channel not in self.CHANNEL_TO_ROW:
            log.debug(
                message=f"Channel {channel} not mapped to any row",
                scope=self.scope,
            )
            return

        row = self.CHANNEL_TO_ROW[channel]

        # Update the selector for this row
        if self.set_selector_by_note(row, note):
            # Trigger callback
            state = self.get_selector_state(row)
            if state and self.on_selector_changed:
                self.on_selector_changed(state)

            # Trigger note received callback
            if self.on_note_received:
                self.on_note_received(row, note)

    def _note_to_combo_index(self, row: int, midi_note: int) -> Optional[int]:
        """
        Convert a MIDI note to a combo box index.

        :param row: Row index (0-3)
        :param midi_note: MIDI note number
        :return: Combo box index or None
        """
        try:
            # Use MIDI converter if available
            if self.midi_converter:
                options = self.row_options.get(row, [])
                return self.midi_converter.midi_note_to_combo_index(
                    row,
                    midi_note,
                    options,
                )

            # Fallback: convert to note name and find in options
            if row == 3:  # Drums
                note_name = self._midi_to_drum_name(midi_note)
            else:
                note_name = self._midi_to_note_name(midi_note)

            options = self.row_options.get(row, [])
            try:
                return options.index(note_name)
            except ValueError:
                return None

        except Exception:
            return None

    def _text_to_note(self, row: int, text: str) -> Optional[int]:
        """
        Convert selector text to a MIDI note.

        :param row: Row index
        :param text: Text from selector
        :return: MIDI note or None
        """
        try:
            if row == 3:  # Drums
                # For drums, try to find in options and convert index to MIDI note
                options = self.row_options.get(row, [])
                try:
                    index = options.index(text)
                    return 36 + index  # Drums start at MIDI note 36
                except ValueError:
                    return None

            # For melodic instruments, use MIDI converter
            if self.midi_converter:
                return self.midi_converter.note_name_to_midi(text)

            # Fallback: basic conversion
            return self._basic_note_name_to_midi(text)

        except Exception:
            return None

    def _midi_to_note_name(self, midi_note: int) -> str:
        """
        Convert MIDI note to note name.

        :param midi_note: MIDI note number
        :return: Note name (e.g., 'C4')
        """
        if self.midi_converter:
            return self.midi_converter.midi_to_note_name(midi_note, drums=False)

        # Fallback
        semitone_to_note = [
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]

        octave = (midi_note // 12) - 1
        semitone = midi_note % 12
        note = semitone_to_note[semitone]

        return f"{note}{octave}"

    def _midi_to_drum_name(self, midi_note: int) -> str:
        """
        Convert MIDI note to drum name.

        :param midi_note: MIDI note number
        :return: Drum name or fallback
        """
        if self.midi_converter:
            return self.midi_converter.midi_to_note_name(midi_note, drums=True)

        return f"Drum({midi_note})"

    def _basic_note_name_to_midi(self, note_name: str) -> Optional[int]:
        """
        Basic fallback for note name to MIDI conversion.

        :param note_name: Note name (e.g., 'C4')
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

    def _set_selector_index_silent(self, combo_box: QComboBox, index: int) -> None:
        """
        Set combo box index without triggering signals.

        :param combo_box: QComboBox to update
        :param index: Index to set
        """
        combo_box.blockSignals(True)
        combo_box.setCurrentIndex(index)
        combo_box.blockSignals(False)

    def set_config(self, config: ComboBoxUpdateConfig) -> None:
        """
        Update synchronizer configuration.

        :param config: New ComboBoxUpdateConfig
        """
        self.config = config

    def set_midi_converter(self, converter: MidiNoteConverter) -> None:
        """
        Set the MIDI converter.

        :param converter: MidiNoteConverter instance
        """
        self.midi_converter = converter
