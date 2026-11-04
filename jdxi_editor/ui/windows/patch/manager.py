"""
Patch Manager Module
====================s

This module defines the `PatchManager` class, a PySide6-based GUI for loading
and saving MIDI patch files for the Roland JD-Xi synthesizer.

Features:
- Allows users to browse for patch files using a file dialog.
- Supports both saving and loading patches, depending on the mode.
- Integrates with `MIDIHelper` for handling MIDI patch operations.
- Implements a simple, dark-themed UI with action buttons.

Classes:
- PatchManager: A QMainWindow that provides a user interface for managing patch files.

Dependencies:
- PySide6
- jdxi_editor.midi.io.MIDIHelper
- jdxi_editor.ui.style.Style

"""

import json
import logging
import os
import random
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
)

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.json_composer import JDXiJSONComposer
from jdxi_editor.midi.sysex.request.read_session import (
    ReadResult,
    SectionStatus,
    collect_editor_requests,
    sections_from_requests,
    start_read_session,
)
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.project import __package_name__
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.editors import ProgramEditor
from jdxi_editor.ui.editors.midi_player.editor import MidiFilePlayer
from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor
from jdxi_editor.ui.style import JDXiUIDimensions
from picoui.specs.widgets import FileSelectionMode, FileSelectionSpec


def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Arcname ensures the directory structure is preserved
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)


class PatchManager(QMainWindow):
    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent=None,
        save_mode=False,
        editors=None,
    ):
        super().__init__(parent)
        self.load_file_name = str(Path.home() / "patch.msz")
        self.midi_helper = midi_helper
        self.save_mode = save_mode
        self.editors = editors
        self._last_read_result: Optional[ReadResult] = None
        self._read_session = None
        self._pending_save_after_read = False
        self._allow_partial_save = False

        # Set window properties
        self.setWindowTitle("Save Patch" if save_mode else "Load Patch")
        self.setMinimumSize(JDXiUIDimensions.patch.WIDTH, JDXiUIDimensions.patch.HEIGHT)

        # Apply dark theme styling
        self.setStyleSheet(JDXi.UI.Style.PATCH_MANAGER)

        # Create central widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Create file path row
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select file location...")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

        # Hardware read status (save mode only)
        self.read_status_list: Optional[QListWidget] = None
        self.read_status_label: Optional[QLabel] = None
        self.read_button: Optional[QPushButton] = None
        self.read_then_save_button: Optional[QPushButton] = None
        if save_mode:
            self.read_status_label = QLabel("Hardware read: not run")
            layout.addWidget(self.read_status_label)
            self.read_status_list = QListWidget()
            self.read_status_list.setMinimumHeight(120)
            layout.addWidget(self.read_status_list)
            read_row = QHBoxLayout()
            self.read_button = QPushButton("Read from JD-Xi")
            self.read_button.clicked.connect(self._on_read_from_jdxi)
            self.read_then_save_button = QPushButton("Read then Save")
            self.read_then_save_button.clicked.connect(self._on_read_then_save)
            read_row.addWidget(self.read_button)
            read_row.addWidget(self.read_then_save_button)
            layout.addLayout(read_row)

        # Create action buttons
        button_layout = QHBoxLayout()
        self.action_button = QPushButton("Save" if save_mode else "Load")
        self.action_button.clicked.connect(self._handle_action)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.action_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Set central widget
        self.setCentralWidget(main_widget)
        self.json_composer = JDXiJSONComposer()

    def _browse_file(self):
        """Open file dialog for selecting patch file"""
        try:
            patch_file_filter = "Music Bundle (*.msz);Patch Files (*.jsz);(*.syx);(*.json);All Files (*.*)"
            save_file_spec = FileSelectionSpec(
                mode=FileSelectionMode.SAVE,
                caption="Save Patch File",
                dir=self.load_file_name,
                filter=patch_file_filter,
            )
            load_file_spec = FileSelectionSpec(
                mode=FileSelectionMode.LOAD,
                caption="Load Patch File",
                dir=self.load_file_name,
                filter=patch_file_filter,
            )
            if self.save_mode:
                spec = save_file_spec
                func = QFileDialog.getSaveFileName
            else:
                spec = load_file_spec
                func = QFileDialog.getOpenFileName
            file_path, _ = func(
                self,
                spec.caption,
                spec.dir,
                spec.filter,
            )
            if file_path:
                self.path_input.setText(file_path)
        except Exception as ex:
            log.error(f"Error browsing for file: {str(ex)}")

    def _skip_editor_types(self) -> tuple:
        return (PatternSequenceEditor, ProgramEditor, MidiFilePlayer)

    def _collect_read_pairs(self) -> list[tuple[str, str]]:
        return collect_editor_requests(
            self.editors or [],
            skip_types=self._skip_editor_types(),
        )

    def _on_read_from_jdxi(self) -> None:
        """Request current tone/effect data from the JD-Xi and show section status."""
        self._pending_save_after_read = False
        self._start_hardware_read()

    def _on_read_then_save(self) -> None:
        """Read from hardware, then run save if a path is set."""
        if not self.path_input.text():
            QMessageBox.warning(self, "Save Patch", "Select a file path before Read then Save.")
            return
        self._pending_save_after_read = True
        self._start_hardware_read()

    def _start_hardware_read(self) -> None:
        if self.midi_helper is None:
            QMessageBox.warning(self, "Read from JD-Xi", "MIDI helper is not available.")
            return
        pairs = self._collect_read_pairs()
        if not pairs:
            QMessageBox.warning(
                self,
                "Read from JD-Xi",
                "No editors with MIDI requests are registered.",
            )
            return
        labels = [p[0] for p in pairs]
        requests = [p[1] for p in pairs]
        if self.read_button:
            self.read_button.setEnabled(False)
        if self.read_then_save_button:
            self.read_then_save_button.setEnabled(False)
        if self.read_status_label:
            self.read_status_label.setText("Hardware read: in progress…")
        self._update_read_status_list(
            ReadResult(sections=sections_from_requests(requests, labels=labels))
        )
        self._read_session = start_read_session(
            self.midi_helper,
            requests,
            labels=labels,
            timeout_ms=10000,
            on_progress=self._on_read_progress,
            on_finished=self._on_read_finished,
            parent=self,
        )

    def _update_read_status_list(self, result: ReadResult) -> None:
        if not self.read_status_list:
            return
        self.read_status_list.clear()
        for section in result.sections:
            item = QListWidgetItem(f"{section.label} — {section.status.value}")
            self.read_status_list.addItem(item)

    def _on_read_progress(self, result: ReadResult) -> None:
        self._update_read_status_list(result)
        if self.read_status_label:
            self.read_status_label.setText(
                f"Hardware read: {result.ok_count}/{len(result.sections)} sections ok"
            )

    def _on_read_finished(self, result: ReadResult) -> None:
        self._last_read_result = result
        self._update_read_status_list(result)
        if self.read_button:
            self.read_button.setEnabled(True)
        if self.read_then_save_button:
            self.read_then_save_button.setEnabled(True)
        if self.read_status_label:
            status = "complete" if result.complete else "partial / timed out"
            self.read_status_label.setText(
                f"Hardware read: {status} ({result.ok_count}/{len(result.sections)})"
            )
        if self._pending_save_after_read:
            self._pending_save_after_read = False
            if result.complete:
                self._allow_partial_save = True
                self._handle_action()
            elif self._confirm_partial_save(result):
                self._allow_partial_save = True
                self._handle_action()

    def _confirm_partial_save(self, result: ReadResult) -> bool:
        missing = [
            s.label
            for s in result.sections
            if s.status != SectionStatus.OK
        ]
        reply = QMessageBox.question(
            self,
            "Incomplete hardware read",
            "Some sections did not respond:\n\n"
            + "\n".join(missing)
            + "\n\nSave anyway using current UI values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _save_program_common(self, temp_folder: Path) -> None:
        """
        Save Program Common (PROGRAM_LEVEL) from the mixer.
        ProgramEditor is skipped in the main save loop, but the Master level
        must be included so patch load restores it correctly.
        """
        program_editor = next(
            (e for e in (self.editors or []) if isinstance(e, ProgramEditor)),
            None,
        )
        if not program_editor or not getattr(program_editor, "mixer_widget", None):
            return
        mixer = program_editor.mixer_widget
        master_slider = getattr(mixer, "master_level_slider", None)
        if not master_slider or not hasattr(master_slider, "value"):
            return
        program_level = master_slider.value()
        program_common = {
            SysExSection.JD_XI_HEADER: "f041100000000e",
            SysExSection.ADDRESS: "18000000",
            SysExSection.TEMPORARY_AREA: "TEMPORARY_PROGRAM",
            SysExSection.SYNTH_TONE: "COMMON",
            SysExSection.PROGRAM_LEVEL: program_level,
        }
        out_path = temp_folder / "jdxi_tone_data_18000000.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(program_common, f, indent=2)
        log.message(
            f"Saved Program Common PROGRAM_LEVEL={program_level} to {out_path.name}",
            scope=self.__class__.__name__,
        )

    def _handle_action(self):
        """Handle save/load action"""
        try:
            file_path = self.path_input.text()
            if not file_path:
                logging.warning("No file selected.")
                return

            if self.midi_helper is None:
                log.message("MIDI helper not initialized.")
                return
            random_int = random.randint(0, 10_000)
            today = datetime.today()
            date_str = today.strftime("%Y-%m-%d")
            temp_folder = (
                Path.home()
                / f".{__package_name__}"
                / "temp"
                / f"{date_str}_{random_int}/"
            )
            if not temp_folder.exists():
                temp_folder.mkdir(parents=True, exist_ok=True)
            if self.save_mode:
                if (
                    self._last_read_result is not None
                    and not self._last_read_result.complete
                    and not self._allow_partial_save
                    and not self._confirm_partial_save(self._last_read_result)
                ):
                    return
                self._allow_partial_save = False
                for editor in self.editors:
                    log.parameter("Editor", editor)
                    if isinstance(editor, PatternSequenceEditor):
                        continue
                    if isinstance(editor, ProgramEditor):
                        continue
                    if isinstance(editor, MidiFilePlayer):
                        continue
                    if not hasattr(editor, "address"):
                        log.warning(
                            f"Skipping invalid editor: {editor}, has no address"
                        )
                        continue
                    if not hasattr(editor, "get_controls_as_dict"):
                        log.warning(
                            f"Skipping invalid editor: {editor}, has no get_controls_as_dict method"
                        )
                        continue
                    self.json_composer.process_editor(editor, temp_folder)

                # Save Program Common (PROGRAM_LEVEL) from mixer - ProgramEditor is skipped above
                self._save_program_common(temp_folder)

                # Save MIDI file if available
                midi_file_saved = False
                if self.parent and hasattr(self.parent, "get_existing_editor"):
                    midi_file_editor = self.parent.get_existing_editor(MidiFilePlayer)
                    if midi_file_editor and hasattr(midi_file_editor, "midi_state"):
                        if (
                            hasattr(midi_file_editor.midi_state, "file")
                            and midi_file_editor.midi_state.file is not None
                        ):
                            try:
                                midi_file_path = temp_folder / "song.mid"
                                midi_file_editor.midi_state.file.save(
                                    str(midi_file_path)
                                )
                                midi_file_saved = True
                                log.message(
                                    f"MIDI file saved to bundle: {midi_file_path}"
                                )
                            except Exception as ex:
                                log.warning(f"Could not save MIDI file to bundle: {ex}")

                # Save as .syx (raw SysEx) or zip as .jsz/.msz
                temporary_files = list(temp_folder.glob("*"))
                if len(temporary_files) == 0:
                    log.warning("No temporary files found to save.")
                    return

                if file_path.lower().endswith(".syx"):
                    if self.midi_helper.save_patch_as_syx(file_path, temp_folder):
                        log.message(f"SysEx patch saved to {file_path}")
                    else:
                        log.warning("Failed to save .syx file")
                    return

                json_files = [f for f in temporary_files if f.suffix == ".json"]
                midi_files = [f for f in temporary_files if f.suffix == ".mid"]
                log.message(
                    f"Zipping {len(json_files)} JSON files"
                    + (f" and {len(midi_files)} MIDI file(s)" if midi_files else "")
                )
                zip_directory(temp_folder, file_path)

                file_type = "Music Bundle" if file_path.endswith(".msz") else "Patch"
                log.message(f"{file_type} saved to {file_path}")
            else:
                # Load patch (JSON files)
                self.midi_helper.load_patch(file_path)

                # Load MIDI file from bundle if it's an .msz file
                if file_path.endswith(".msz"):
                    try:
                        with zipfile.ZipFile(file_path, "r") as zip_ref:
                            midi_files = [
                                f for f in zip_ref.namelist() if f.endswith(".mid")
                            ]
                            if (
                                midi_files
                                and self.parent
                                and hasattr(self.parent, "get_existing_editor")
                            ):
                                # Extract MIDI file to temp location
                                midi_file_name = midi_files[0]  # Use first MIDI file
                                temp_midi_path = temp_folder / midi_file_name
                                with zip_ref.open(midi_file_name) as midi_source:
                                    temp_midi_path.parent.mkdir(
                                        parents=True, exist_ok=True
                                    )
                                    with open(temp_midi_path, "wb") as midi_dest:
                                        midi_dest.write(midi_source.read())

                                # Load MIDI file into editor
                                midi_file_editor = self.parent.get_existing_editor(
                                    MidiFilePlayer
                                )
                                if not midi_file_editor and hasattr(
                                    self.parent, "show_editor"
                                ):
                                    # Create editor if it doesn't exist (but don't show it yet)
                                    self.parent.show_editor("midi_player")
                                    midi_file_editor = self.parent.get_existing_editor(
                                        MidiFilePlayer
                                    )

                                if midi_file_editor:
                                    log.message(
                                        f"Loading MIDI file into editor: {midi_file_name}"
                                    )
                                    # Stop any current playback first
                                    if hasattr(midi_file_editor, "midi_stop_playback"):
                                        midi_file_editor.midi_playback_stop()
                                    if hasattr(
                                        midi_file_editor, "midi_playback_worker_stop"
                                    ):
                                        midi_file_editor.midi_playback_worker_stop()

                                    from mido import MidiFile

                                    # Load MIDI file (this does NOT send it to the instrument)
                                    midi_file_editor.midi_state.file = MidiFile(
                                        str(temp_midi_path)
                                    )
                                    midi_file_editor.ui.digital_title_file_name.setText(
                                        f"Loaded from bundle: {Path(midi_file_name).name}"
                                    )
                                    midi_file_editor.midi_file.midi_track_viewer.clear()
                                    midi_file_editor.midi_file.midi_track_viewer.set_midi_file(
                                        midi_file_editor.midi_state.file
                                    )

                                    # Initialize MIDI file in editor (similar to midi_load_file)
                                    # Ensure ticks_per_beat is available early
                                    midi_file_editor.ticks_per_beat = (
                                        midi_file_editor.midi_state.file.ticks_per_beat
                                    )

                                    # Detect initial tempo
                                    if hasattr(
                                        midi_file_editor, "detect_initial_tempo"
                                    ):
                                        initial_track_tempos = (
                                            midi_file_editor.detect_initial_tempo()
                                        )

                                    # Set tempo digital
                                    if hasattr(
                                        midi_file_editor, "ui_display_set_tempo_usecs"
                                    ):
                                        midi_file_editor.ui_display_set_tempo_usecs(
                                            midi_file_editor.midi_state.tempo_initial
                                        )

                                    # Set tempo at position
                                    midi_file_editor.midi_state.tempo_at_position = (
                                        midi_file_editor.midi_state.tempo_initial
                                    )

                                    # Channel selection
                                    if hasattr(midi_file_editor, "midi_channel_select"):
                                        midi_file_editor.midi_channel_select()

                                    # Extract events (this prepares the file for playback but doesn't start it)
                                    if hasattr(midi_file_editor, "midi_extract_events"):
                                        midi_file_editor.midi_extract_events()

                                    # Setup worker (this prepares playback but doesn't start it)
                                    if hasattr(midi_file_editor, "setup_worker"):
                                        midi_file_editor.setup_worker()

                                    # Calculate durations
                                    if hasattr(midi_file_editor, "calculate_duration"):
                                        midi_file_editor.calculate_duration()
                                    if hasattr(
                                        midi_file_editor, "calculate_tick_duration"
                                    ):
                                        midi_file_editor.calculate_tick_duration()

                                    # Reset position slider
                                    if hasattr(
                                        midi_file_editor, "ui_position_slider_reset"
                                    ):
                                        midi_file_editor.ui_position_slider_reset()

                                    # Ensure playback is NOT started - stop timer and worker
                                    if (
                                        hasattr(midi_file_editor.midi_state, "timer")
                                        and midi_file_editor.midi_state.timer
                                    ):
                                        if midi_file_editor.midi_state.timer.isActive():
                                            midi_file_editor.midi_state.timer.stop()
                                            log.message("Stopped MIDI playback timer")

                                    # Ensure worker is stopped
                                    if (
                                        hasattr(
                                            midi_file_editor, "midi_playback_worker"
                                        )
                                        and midi_file_editor.midi_playback_worker
                                    ):
                                        if hasattr(
                                            midi_file_editor.midi_playback_worker,
                                            "stop",
                                        ):
                                            midi_file_editor.midi_playback_worker.stop()

                                    # Reset playback state
                                    if hasattr(
                                        midi_file_editor.midi_state,
                                        "playback_start_time",
                                    ):
                                        midi_file_editor.midi_state.playback_start_time = (
                                            None
                                        )
                                    if hasattr(
                                        midi_file_editor.midi_state, "event_index"
                                    ):
                                        midi_file_editor.midi_state.event_index = None

                                    # Verify file is loaded
                                    if midi_file_editor.midi_state.file:
                                        track_count = len(
                                            midi_file_editor.midi_state.file.tracks
                                        )
                                        log.message(
                                            f"MIDI file loaded from bundle: {midi_file_name} ({track_count} tracks, ready for playback, NOT playing)"
                                        )
                                    else:
                                        log.warning(
                                            f"MIDI file failed to load: {midi_file_name}"
                                        )
                                else:
                                    log.message(
                                        "MIDI file found in bundle but MidiFileEditor not available"
                                    )
                    except Exception as ex:
                        log.warning(f"Could not load MIDI file from bundle: {ex}")

                file_type = "Music Bundle" if file_path.endswith(".msz") else "Patch"
                log.message(f"{file_type} loaded from {file_path}")

            self.close()

        except Exception as ex:
            log.error(
                f"Error {'saving' if self.save_mode else 'loading'} patch: {str(ex)}"
            )
