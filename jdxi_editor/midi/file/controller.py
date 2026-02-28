"""
MIDI File Controller Module

Manages MIDI file operations including saving, loading, and pattern conversion.
Handles tempo management, bar detection, and note-to-button mapping.
"""

from typing import Callable, Dict, List, Optional, Tuple

from decologr import Decologr as log
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, tempo2bpm
from picomidi import MidiTempo
from picomidi.message.type import MidoMessageType

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.conversion.note import MidiNoteConverter


class MidiFileControllerConfig:
    """Configuration for MIDI file controller."""

    def __init__(
        self,
        ticks_per_beat: int = 480,
        beats_per_measure: int = 4,
        default_bpm: int = 120,
        default_velocity: int = 100,
    ):
        """
        Initialize controller configuration.

        :param ticks_per_beat: MIDI ticks per beat (standard is 480)
        :param beats_per_measure: Number of beats per measure (typically 4)
        :param default_bpm: Default tempo in BPM
        :param default_velocity: Default note velocity
        """
        self.ticks_per_beat = ticks_per_beat
        self.beats_per_measure = beats_per_measure
        self.default_bpm = default_bpm
        self.default_velocity = default_velocity

    @property
    def ticks_per_measure(self) -> int:
        """Calculate ticks per bar."""
        return self.ticks_per_beat * self.beats_per_measure


class MidiFileLoadResult:
    """Result of loading a MIDI file."""

    def __init__(
        self,
        success: bool,
        num_bars: int = 0,
        notes_loaded: int = 0,
        tempo_bpm: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        """
        Initialize load result.

        :param success: Whether loading succeeded
        :param num_bars: Number of bars detected
        :param notes_loaded: Number of notes loaded
        :param tempo_bpm: Detected tempo in BPM
        :param error_message: Error message if loading failed
        """
        self.success = success
        self.num_bars = num_bars
        self.notes_loaded = notes_loaded
        self.tempo_bpm = tempo_bpm
        self.error_message = error_message


class MidiFileController:
    """
    Manages MIDI file I/O operations for pattern sequencer.

    Handles:
    - Loading MIDI files and converting to patterns
    - Saving patterns to MIDI files
    - Tempo management
    - Bar/measure detection
    - MIDI note-to-button mapping
    """

    # MIDI channel mapping
    CHANNEL_TO_ROW = {
        MidiChannel.DIGITAL_SYNTH_1: 0,  # Channel 0
        MidiChannel.DIGITAL_SYNTH_2: 1,  # Channel 1
        MidiChannel.ANALOG_SYNTH: 2,  # Channel 2
        MidiChannel.DRUM_KIT: 3,  # Channel 9
    }

    ROW_TO_CHANNEL = {v: k for k, v in CHANNEL_TO_ROW.items()}

    def __init__(
        self,
        config: Optional[MidiFileControllerConfig] = None,
        midi_converter: Optional[MidiNoteConverter] = None,
        scope: str = "MidiFileController",
    ):
        """
        Initialize MIDI file controller.

        :param config: Controller configuration
        :param midi_converter: MIDI note converter for validation
        :param scope: Logging scope name
        """
        self.config = config or MidiFileControllerConfig()
        self.midi_converter = midi_converter
        self.scope = scope

        # Current MIDI file in memory
        self.midi_file: Optional[MidiFile] = None
        self.current_bpm = self.config.default_bpm

        # Callbacks for file operations
        self.on_file_loaded: Optional[Callable[[MidiFileLoadResult], None]] = None
        self.on_file_saved: Optional[Callable[[str], None]] = None
        self.on_tempo_changed: Optional[Callable[[int], None]] = None

    def create_new_file(self) -> MidiFile:
        """
        Create a new MIDI file with default settings.

        :return: New MidiFile object
        """
        midi_file = MidiFile(
            type=1,
            ticks_per_beat=self.config.ticks_per_beat,
        )

        # Add default track with tempo
        track = MidiTrack()
        midi_file.tracks.append(track)
        self._add_tempo_to_track(track, self.config.default_bpm)

        self.midi_file = midi_file
        self.current_bpm = self.config.default_bpm

        log.message(
            message="Created new MIDI file",
            scope=self.scope,
        )

        return midi_file

    def set_tempo(self, bpm: int) -> None:
        """
        Set the MIDI file tempo.

        Updates the current file's tempo and triggers callback.

        :param bpm: Tempo in beats per minute (20-300)
        """
        bpm = max(20, min(300, bpm))  # Constrain to valid range
        self.current_bpm = bpm

        if self.midi_file and self.midi_file.tracks:
            # Remove existing tempo messages
            track = self.midi_file.tracks[0]
            track[:] = [msg for msg in track if msg.type != MidoMessageType.SET_TEMPO.value]

            # Add new tempo message
            self._add_tempo_to_track(track, bpm)

        log.message(
            message=f"Tempo set to {bpm} BPM",
            scope=self.scope,
        )

        if self.on_tempo_changed:
            self.on_tempo_changed(bpm)

    def get_tempo(self) -> int:
        """
        Get the current MIDI file tempo.

        :return: Tempo in BPM
        """
        if not self.midi_file or not self.midi_file.tracks:
            return self.current_bpm

        # Search for SET_TEMPO message in first track
        track = self.midi_file.tracks[0]
        for msg in track:
            if msg.type == MidoMessageType.SET_TEMPO.value:
                return int(tempo2bpm(msg.tempo))

        return self.current_bpm

    def save_pattern(
        self,
        filename: str,
        measures: List,
        pattern_name: Optional[str] = None,
    ) -> bool:
        """
        Save pattern to a MIDI file.

        Creates a MIDI file from the current pattern with proper formatting.

        :param filename: Path to save file
        :param measures: List of PatternMeasure objects to save
        :param pattern_name: Optional name for the pattern (used as metadata)
        :return: True if successful, False otherwise
        """
        try:
            midi_file = MidiFile(
                type=1,
                ticks_per_beat=self.config.ticks_per_beat,
            )

            # Create one track for all notes
            track = MidiTrack()
            midi_file.tracks.append(track)

            # Add metadata
            self._add_tempo_to_track(track, self.current_bpm)
            track.append(
                MetaMessage(
                    "time_signature",
                    numerator=self.config.beats_per_measure,
                    denominator=4,
                )
            )

            if pattern_name:
                track.append(MetaMessage("sequence_name", text=pattern_name))

            # Convert pattern to MIDI events
            notes_saved = 0
            for bar_index, measure in enumerate(measures):
                for row in range(4):
                    channel = self.ROW_TO_CHANNEL.get(row, row)

                    for step in range(min(16, len(measure.buttons[row]))):
                        button = measure.buttons[row][step]

                        if not button.isChecked():
                            continue

                        # Get note spec
                        spec = self._get_button_note_spec(button)
                        if not spec.is_active:
                            continue

                        # Calculate timing
                        global_step = bar_index * 16 + step
                        time = global_step * (self.config.ticks_per_beat // 4)

                        # Add note on/off
                        track.append(
                            Message(
                                MidoMessageType.NOTE_ON.value,
                                note=spec.note,
                                velocity=spec.velocity,
                                time=time,
                                channel=channel,
                            )
                        )

                        # Note off after duration
                        duration_ticks = int(
                            (spec.duration_ms / 1000.0)
                            * self.config.ticks_per_beat
                            * (self.current_bpm / 60.0)
                        )
                        track.append(
                            Message(
                                MidoMessageType.NOTE_OFF.value,
                                note=spec.note,
                                velocity=0,
                                time=time + duration_ticks,
                                channel=channel,
                            )
                        )

                        notes_saved += 1

            # Save to file
            midi_file.save(filename)
            self.midi_file = midi_file

            log.message(
                message=f"Saved pattern to {filename} ({notes_saved} notes, {len(measures)} bars)",
                scope=self.scope,
            )

            if self.on_file_saved:
                self.on_file_saved(filename)

            return True

        except Exception as ex:
            log.error(
                message=f"Error saving pattern: {ex}",
                scope=self.scope,
            )
            return False

    def load_pattern(
        self,
        filename: str,
        measures_container: Optional[List] = None,
    ) -> MidiFileLoadResult:
        """
        Load pattern from a MIDI file.

        Parses MIDI file and returns data for populating measures/buttons.

        :param filename: Path to MIDI file
        :param measures_container: Optional list to populate with loaded measures
        :return: MidiFileLoadResult with load status and metadata
        """
        try:
            midi_file = MidiFile(filename)

            # Detect structure
            num_bars = self._detect_bars_from_midi(midi_file)
            ppq = midi_file.ticks_per_beat
            ticks_per_measure = self.config.ticks_per_measure

            # Parse MIDI to extract notes
            notes_data = self._parse_midi_file(
                midi_file,
                ppq,
                ticks_per_measure,
            )

            # Extract tempo
            tempo_bpm = self._extract_tempo_from_midi(midi_file)
            if tempo_bpm:
                self.current_bpm = tempo_bpm

            log.message(
                message=f"Loaded MIDI file: {num_bars} bars, {len(notes_data)} notes, {tempo_bpm} BPM",
                scope=self.scope,
            )

            self.midi_file = midi_file

            result = MidiFileLoadResult(
                success=True,
                num_bars=num_bars,
                notes_loaded=len(notes_data),
                tempo_bpm=tempo_bpm,
            )

            if self.on_file_loaded:
                self.on_file_loaded(result)

            return result

        except FileNotFoundError:
            error_msg = f"File not found: {filename}"
            log.error(message=error_msg, scope=self.scope)
            return MidiFileLoadResult(
                success=False,
                error_message=error_msg,
            )
        except Exception as ex:
            error_msg = f"Error loading MIDI file: {ex}"
            log.error(message=error_msg, scope=self.scope)
            return MidiFileLoadResult(
                success=False,
                error_message=error_msg,
            )

    def load_from_midi_file_editor(
        self,
        midi_file_editor,
    ) -> MidiFileLoadResult:
        """
        Load pattern from a MidiFileEditor instance.

        Useful for sharing MIDI files between editor windows.

        :param midi_file_editor: MidiFileEditor instance with loaded file
        :return: MidiFileLoadResult with load status
        """
        try:
            if not hasattr(midi_file_editor, "midi_state"):
                return MidiFileLoadResult(
                    success=False,
                    error_message="MidiFileEditor missing midi_state",
                )

            midi_file = midi_file_editor.midi_state.file
            if not midi_file:
                return MidiFileLoadResult(
                    success=False,
                    error_message="No MIDI file loaded in editor",
                )

            # Try to get filename
            filename = None
            if hasattr(midi_file, "filename"):
                filename = midi_file.filename

            if filename:
                return self.load_pattern(filename)
            else:
                # Load from MidiFile object directly
                return self._load_from_midi_file_object(midi_file)

        except Exception as ex:
            error_msg = f"Error loading from MidiFileEditor: {ex}"
            log.error(message=error_msg, scope=self.scope)
            return MidiFileLoadResult(
                success=False,
                error_message=error_msg,
            )

    def _load_from_midi_file_object(
        self,
        midi_file: MidiFile,
    ) -> MidiFileLoadResult:
        """
        Load pattern from a MidiFile object (internal method).

        :param midi_file: MidiFile instance
        :return: MidiFileLoadResult with load status
        """
        try:
            num_bars = self._detect_bars_from_midi(midi_file)
            ppq = midi_file.ticks_per_beat
            ticks_per_measure = self.config.ticks_per_measure

            notes_data = self._parse_midi_file(
                midi_file,
                ppq,
                ticks_per_measure,
            )

            tempo_bpm = self._extract_tempo_from_midi(midi_file)
            if tempo_bpm:
                self.current_bpm = tempo_bpm

            self.midi_file = midi_file

            return MidiFileLoadResult(
                success=True,
                num_bars=num_bars,
                notes_loaded=len(notes_data),
                tempo_bpm=tempo_bpm,
            )

        except Exception as ex:
            error_msg = f"Error loading from MidiFile object: {ex}"
            log.error(message=error_msg, scope=self.scope)
            return MidiFileLoadResult(
                success=False,
                error_message=error_msg,
            )

    def _detect_bars_from_midi(self, midi_file: MidiFile) -> int:
        """
        Detect the number of bars in a MIDI file.

        Counts the maximum absolute time and divides by ticks per bar.

        :param midi_file: MidiFile to analyze
        :return: Number of bars detected (minimum 1)
        """
        ppq = midi_file.ticks_per_beat
        ticks_per_measure = ppq * self.config.beats_per_measure

        max_time = 0
        for track in midi_file.tracks:
            absolute_time = 0
            for msg in track:
                absolute_time += msg.time
                if not msg.is_meta:
                    max_time = max(max_time, absolute_time)

        num_bars = int((max_time / ticks_per_measure) + 1) if max_time > 0 else 1
        return max(1, num_bars)

    def _parse_midi_file(
        self,
        midi_file: MidiFile,
        ppq: int,
        ticks_per_measure: int,
    ) -> List[Dict]:
        """
        Parse MIDI file and extract note events.

        Returns list of note dictionaries with timing and metadata.

        :param midi_file: MidiFile to parse
        :param ppq: Ticks per beat from the file
        :param ticks_per_measure: Ticks per bar calculation
        :return: List of parsed note events
        """
        notes = []

        # First pass: collect all note events with timing
        note_events = []
        current_tempo = 500000  # Default 120 BPM in microseconds

        for track in midi_file.tracks:
            absolute_time = 0
            for msg in track:
                absolute_time += msg.time

                if msg.type == MidoMessageType.SET_TEMPO.value:
                    current_tempo = msg.tempo

                if hasattr(msg, "channel") and (
                    msg.type == MidoMessageType.NOTE_ON.value
                    or msg.type == MidoMessageType.NOTE_OFF.value
                ):
                    note_events.append((absolute_time, msg, msg.channel, current_tempo))

        # Second pass: match note-on with note-off to get durations
        active_notes = {}  # (channel, note) -> (on_time, on_tempo)
        note_durations = {}  # (channel, note, on_time) -> duration_ms

        for abs_time, msg, channel, tempo in note_events:
            note_key = (channel, msg.note)

            if msg.type == MidoMessageType.NOTE_ON.value and msg.velocity > 0:
                active_notes[note_key] = (abs_time, tempo)
            elif msg.type == MidoMessageType.NOTE_OFF.value or (
                msg.type == MidoMessageType.NOTE_ON.value and msg.velocity == 0
            ):
                if note_key in active_notes:
                    on_time, on_tempo = active_notes[note_key]
                    duration_ticks = abs_time - on_time
                    duration_ms = (duration_ticks / ppq) * (on_tempo / 1000.0)
                    note_durations[(channel, msg.note, on_time)] = duration_ms
                    del active_notes[note_key]

        # Third pass: assign notes to measures/steps
        for abs_time, msg, channel, tempo in note_events:
            if msg.type == MidoMessageType.NOTE_ON.value and msg.velocity > 0:
                if channel not in self.CHANNEL_TO_ROW:
                    continue

                row = self.CHANNEL_TO_ROW[channel]
                bar_index = int(abs_time / ticks_per_measure)
                step_in_bar = int(
                    (abs_time % ticks_per_measure) / (ticks_per_measure / 16)
                )

                duration_key = (channel, msg.note, abs_time)
                duration_ms = note_durations.get(
                    duration_key,
                    (ticks_per_measure / 16.0 / ppq) * (tempo / 1000.0),
                )

                notes.append(
                    {
                        "bar": bar_index,
                        "step": step_in_bar,
                        "row": row,
                        "note": msg.note,
                        "velocity": msg.velocity,
                        "duration_ms": duration_ms,
                        "channel": channel,
                    }
                )

        return notes

    def _extract_tempo_from_midi(self, midi_file: MidiFile) -> Optional[int]:
        """
        Extract tempo from MIDI file.

        Searches all tracks for the first SET_TEMPO message.

        :param midi_file: MidiFile to search
        :return: Tempo in BPM, or None if not found
        """
        for track in midi_file.tracks:
            for msg in track:
                if msg.type == MidoMessageType.SET_TEMPO.value:
                    return int(tempo2bpm(msg.tempo))

        return None

    def _add_tempo_to_track(self, track: MidiTrack, bpm: int) -> None:
        """
        Add tempo message to a track.

        :param track: MidiTrack to add tempo to
        :param bpm: Tempo in BPM
        """
        microseconds_per_beat = int(MidiTempo.MICROSECONDS_PER_MINUTE / bpm)
        tempo_msg = MetaMessage(
            MidoMessageType.SET_TEMPO.value,
            tempo=microseconds_per_beat,
            time=0,
        )
        track.insert(0, tempo_msg)

    def _get_button_note_spec(self, button):
        """
        Get note specification from a button.

        :param button: SequencerButton instance
        :return: NoteButtonSpec with note, duration_ms, velocity, is_active
        """
        from jdxi_editor.ui.editors.pattern.helper import get_button_note_spec

        return get_button_note_spec(button)

    def set_config(self, config: MidiFileControllerConfig) -> None:
        """
        Update controller configuration.

        :param config: New configuration
        """
        self.config = config

    def set_midi_converter(self, converter: MidiNoteConverter) -> None:
        """
        Set or update the MIDI converter.

        :param converter: MidiNoteConverter instance
        """
        self.midi_converter = converter

    def get_current_file(self) -> Optional[MidiFile]:
        """
        Get the currently loaded MIDI file.

        :return: MidiFile instance or None
        """
        return self.midi_file
