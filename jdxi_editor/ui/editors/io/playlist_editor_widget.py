"""
Playlist Editor Widget Module

This module defines the `PlaylistEditorWidget` class, a widget for editing
playlist contents including adding/removing programs, managing MIDI file paths,
cheat presets, and playing playlist programs.

Classes:
    PlaylistEditorWidget(QWidget)
        A widget for editing playlist contents.
"""

import os
import random
from pathlib import Path
from typing import Any, Callable, Optional

from decologr import Decologr as log
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.ui.editors.helpers.program import calculate_midi_values
from jdxi_editor.ui.editors.io.transport.spec import TransportSpec
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from jdxi_editor.ui.widgets.combo_box import SearchableFilterableComboBox
from jdxi_editor.ui.widgets.delegates.midi_file import MidiFileDelegate
from jdxi_editor.ui.widgets.delegates.play_button import PlayButtonDelegate
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items


class PlaylistEditorWidget(QWidget):
    """Widget for editing playlist contents."""

    # Signal emitted when playlist programs change (for refreshing combo)
    playlist_programs_changed = Signal()

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        channel: int = 16,  # Default PROGRAM channel (0-based)
        parent: Optional[QWidget] = None,
        on_program_loaded: Optional[Callable[[JDXiProgram], None]] = None,
        on_refresh_playlist_combo: Optional[Callable[[], None]] = None,
        get_parent_instrument: Optional[Callable[[], Optional[QWidget]]] = None,
    ):
        """
        Initialize the PlaylistEditorWidget.

        :param midi_helper: Optional[MidiIOHelper] for MIDI communication
        :param channel: int MIDI channel (0-based, default 16 for PROGRAM)
        :param parent: Optional[QWidget] parent widget
        :param on_program_loaded: Optional callback when program is loaded (for UI updates)
        :param on_refresh_playlist_combo: Optional callback to refresh playlist combo
        :param get_parent_instrument: Optional callback to get parent instrument for MidiFileEditor
        """
        super().__init__(parent)
        self.playlist_id = None
        self.midi_helper = midi_helper
        self.channel = channel
        self.on_program_loaded_callback = on_program_loaded
        self.on_refresh_playlist_combo_callback = on_refresh_playlist_combo
        self.get_parent_instrument_callback = get_parent_instrument

        # Playback tracking state
        self._current_playlist_row: Optional[int] = None
        self._playlist_midi_editor = None

        # UI components
        self.playlist_editor_combo: Optional[SearchableFilterableComboBox] = None
        self.add_to_playlist_button: Optional[QPushButton] = None
        self.delete_from_playlist_button: Optional[QPushButton] = None
        self.playlist_programs_table: Optional[QTableWidget] = None

        # Mapping of combo box values to playlist IDs
        self._playlist_value_to_id: dict = {0: None}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the playlist editor UI."""
        layout = QVBoxLayout(self)

        # Add icon row at the top (transfer items to avoid "already has a parent" errors)
        icon_row_container = QHBoxLayout()
        icon_row = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        layout.addLayout(icon_row_container)

        # Playlist selection
        self.playlist_select_layout = QHBoxLayout()
        self.playlist_select_layout.addWidget(QLabel("Select Playlist:"))
        # Initialize with empty options - will be populated by populate_playlist_combo()
        self.playlist_editor_combo = SearchableFilterableComboBox(
            label="",
            options=["-- Select a Playlist --"],
            values=[0],  # Use 0 as placeholder value for "no selection"
            categories=None,
            category_filter_func=None,
            show_label=False,
            show_search=True,
            show_category=False,
            search_placeholder="Search playlists...",
        )
        # Connect to valueChanged signal (emits the value, not the index)
        self.playlist_editor_combo.valueChanged.connect(self._on_playlist_value_changed)
        self.playlist_select_layout.addWidget(self.playlist_editor_combo)
        self.playlist_select_layout.addStretch()
        layout.addLayout(self.playlist_select_layout)

        # Add/Delete buttons (round style + icon + label)
        button_layout = QHBoxLayout()
        self._add_round_action_button(
            JDXi.UI.Icon.PLUS_CIRCLE,
            "Add to Playlist",
            self.add_program_to_playlist,
            button_layout,
            name="add_to_playlist",
        )
        self.add_to_playlist_button.setEnabled(
            False
        )  # Disabled until playlist is selected
        self._add_round_action_button(
            JDXi.UI.Icon.TRASH_FILL,
            "Delete from Playlist",
            self.delete_program_from_playlist,
            button_layout,
            name="delete_from_playlist",
        )
        self.delete_from_playlist_button.setEnabled(
            False
        )  # Disabled until playlist is selected
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Transport group (Play, Stop, Pause, Shuffle Play)
        layout.addWidget(self._init_transport_controls())

        # Create playlist programs table
        self.playlist_programs_table = QTableWidget()
        self.playlist_programs_table.setColumnCount(6)
        self.playlist_programs_table.setHorizontalHeaderLabels(
            ["Bank", "Number", "Program Name", "MIDI File Name", "Cheat Preset", "Play"]
        )

        # Apply custom styling
        self.playlist_programs_table.setStyleSheet(self._get_table_style())

        # Enable sorting
        self.playlist_programs_table.setSortingEnabled(True)

        # Set column widths
        header = self.playlist_programs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Bank
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # Number
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Program Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # MIDI File Name
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )  # Cheat Preset
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Play

        # Set delegates
        midi_file_delegate = MidiFileDelegate(
            table_widget=self.playlist_programs_table,
            parent=self.playlist_programs_table,
        )
        self.playlist_programs_table.setItemDelegateForColumn(3, midi_file_delegate)

        play_button_delegate = PlayButtonDelegate(
            self.playlist_programs_table, play_callback=self._play_playlist_program
        )
        self.playlist_programs_table.setItemDelegateForColumn(5, play_button_delegate)

        # Connect item changed to save MIDI file paths
        self.playlist_programs_table.itemChanged.connect(
            self._on_playlist_program_item_changed
        )

        # Connect double-click to show Program Editor when Program Name is clicked
        self.playlist_programs_table.itemDoubleClicked.connect(
            self._on_playlist_program_double_clicked
        )

        # Connect selection changed to enable/disable delete button
        self.playlist_programs_table.selectionModel().selectionChanged.connect(
            self._on_playlist_programs_selection_changed
        )

        layout.addWidget(self.playlist_programs_table)

        # Populate playlist combo box
        self.populate_playlist_combo()

    def _get_table_style(self) -> str:
        """
        Get custom styling for tables with rounded corners and charcoal embossed cells.

        :return: str CSS style string
        """
        return JDXi.UI.Style.DATABASE_TABLE_STYLE

    def _add_round_action_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        layout: QHBoxLayout,
        *,
        name: Optional[str] = None,
        checkable: bool = False,
    ) -> QPushButton:
        """Create a round button with icon + text label (same style as Transport)."""
        btn = QPushButton()
        btn.setCheckable(checkable)
        btn.setStyleSheet(JDXiUIStyle.BUTTON_ROUND)
        btn.setFixedSize(
            JDXiUIDimensions.BUTTON_ROUND.WIDTH,
            JDXiUIDimensions.BUTTON_ROUND.HEIGHT,
        )
        if slot is not None:
            btn.clicked.connect(slot)
        if name:
            setattr(self, f"{name}_button", btn)
        layout.addWidget(btn)
        label_row = QWidget()
        label_layout = QHBoxLayout(label_row)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(4)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        if pixmap and not pixmap.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            label_layout.addWidget(icon_label)
        text_label = QLabel(text)
        text_label.setStyleSheet(JDXi.UI.Style.STYLE_FOREGROUND)
        label_layout.addWidget(text_label)
        layout.addWidget(label_row)
        return btn

    def _create_transport_control(
        self,
        spec: TransportSpec,
        layout: QHBoxLayout,
        button_group: Optional[QButtonGroup],
    ) -> None:
        """Create a transport button + label row (same pattern as Midi File Player)."""
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setStyleSheet(JDXiUIStyle.BUTTON_ROUND)
        btn.setFixedSize(
            JDXiUIDimensions.BUTTON_ROUND.WIDTH,
            JDXiUIDimensions.BUTTON_ROUND.HEIGHT,
        )
        btn.clicked.connect(spec.slot)
        if spec.grouped and button_group:
            button_group.addButton(btn)
        layout.addWidget(btn)

        label_row = QWidget()
        label_layout = QHBoxLayout(label_row)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(4)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            spec.icon, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        if pixmap and not pixmap.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            label_layout.addWidget(icon_label)
        text_label = QLabel(spec.text)
        text_label.setStyleSheet(JDXi.UI.Style.STYLE_FOREGROUND)
        label_layout.addWidget(text_label)
        layout.addWidget(label_row)

    def _init_transport_controls(self) -> QGroupBox:
        """Build Transport group with Play, Stop, Pause, Shuffle Play (same style as Midi File Player)."""
        group = QGroupBox("Transport")
        centered_layout = QHBoxLayout(group)
        transport_layout = QHBoxLayout()
        centered_layout.addStretch()
        centered_layout.addLayout(transport_layout)
        centered_layout.addStretch()

        transport_button_group = QButtonGroup(self)
        transport_button_group.setExclusive(True)

        controls = [
            TransportSpec(
                "play", JDXi.UI.Icon.PLAY, "Play", self._playlist_transport_play, True
            ),
            TransportSpec(
                "stop", JDXi.UI.Icon.STOP, "Stop", self._playlist_transport_stop, True
            ),
            TransportSpec(
                "pause",
                JDXi.UI.Icon.PAUSE,
                "Pause",
                self._playlist_transport_pause_toggle,
                False,
            ),
            TransportSpec(
                "shuffle",
                JDXi.UI.Icon.SHUFFLE,
                "Shuffle Play",
                self._playlist_shuffle_play,
                True,
            ),
        ]
        for spec in controls:
            self._create_transport_control(
                spec, transport_layout, transport_button_group
            )
        return group

    def _playlist_transport_play(self) -> None:
        """Play first playlist row that has a MIDI file, or selected row if one is selected."""
        if not self.playlist_programs_table:
            return
        row = -1
        selection = self.playlist_programs_table.selectionModel().selectedRows()
        if selection:
            row = selection[0].row()
        if row < 0:
            for r in range(self.playlist_programs_table.rowCount()):
                midi_item = self.playlist_programs_table.item(r, 3)
                if midi_item and midi_item.text().strip():
                    row = r
                    break
        if row >= 0:
            model = self.playlist_programs_table.model()
            if model:
                index = model.index(row, 5)
                self._play_playlist_program(index)

    def _playlist_transport_stop(self) -> None:
        """Stop current playlist playback."""
        if self._playlist_midi_editor and hasattr(
            self._playlist_midi_editor, "midi_playback_stop"
        ):
            self._playlist_midi_editor.midi_playback_stop()
        self._current_playlist_row = None
        self._playlist_midi_editor = None

    def _playlist_transport_pause_toggle(self) -> None:
        """Pause or resume current playlist playback."""
        if self._playlist_midi_editor and hasattr(
            self._playlist_midi_editor, "midi_playback_pause_toggle"
        ):
            self._playlist_midi_editor.midi_playback_pause_toggle()

    def _playlist_shuffle_play(self) -> None:
        """Pick a random row that has a MIDI file and play it."""
        if not self.playlist_programs_table:
            return
        rows_with_midi = []
        for r in range(self.playlist_programs_table.rowCount()):
            midi_item = self.playlist_programs_table.item(r, 3)
            if midi_item and midi_item.text().strip():
                rows_with_midi.append(r)
        if not rows_with_midi:
            log.message(
                "No rows with MIDI file for shuffle play", scope=self.__class__.__name__
            )
            return
        row = random.choice(rows_with_midi)
        model = self.playlist_programs_table.model()
        if model:
            index = model.index(row, 5)
            self._play_playlist_program(index)

    def populate_playlist_combo(self) -> None:
        """Populate the playlist selection combo box."""
        if not self.playlist_editor_combo:
            return

        try:
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            playlists = db.get_all_playlists()

            # Build options and values lists for SearchableFilterableComboBox
            playlist_options = ["-- Select a Playlist --"]
            playlist_values = [0]  # 0 = no selection
            # Store mapping of value to playlist_id for lookup
            self._playlist_value_to_id = {0: None}

            for playlist in playlists:
                playlist_id = playlist["id"]
                display_text = (
                    f"{playlist['name']} ({playlist.get('program_count', 0)} programs)"
                )
                # Use playlist_id as value (but ensure it's an int)
                value = (
                    int(playlist_id)
                    if isinstance(playlist_id, (int, str))
                    else len(playlist_options)
                )
                playlist_options.append(display_text)
                playlist_values.append(value)
                self._playlist_value_to_id[value] = playlist_id

            # Recreate the combo box with new data
            # Use the stored playlist_select_layout reference
            if hasattr(self, "playlist_select_layout") and self.playlist_select_layout:
                # Find the combo box in the layout
                combo_index = -1
                for i in range(self.playlist_select_layout.count()):
                    item = self.playlist_select_layout.itemAt(i)
                    if item and item.widget() == self.playlist_editor_combo:
                        combo_index = i
                        break

                if combo_index >= 0:
                    # Remove old combo box
                    self.playlist_select_layout.removeWidget(self.playlist_editor_combo)
                    self.playlist_editor_combo.deleteLater()

                    # Create new combo box with updated data
                    self.playlist_editor_combo = SearchableFilterableComboBox(
                        label="",
                        options=playlist_options,
                        values=playlist_values,
                        categories=None,
                        category_filter_func=None,
                        show_label=False,
                        show_search=True,
                        show_category=False,
                        search_placeholder="Search playlists...",
                    )
                    # Reconnect signal
                    self.playlist_editor_combo.valueChanged.connect(
                        self._on_playlist_value_changed
                    )
                    # Re-insert into layout at same position
                    self.playlist_select_layout.insertWidget(
                        combo_index, self.playlist_editor_combo
                    )
        except Exception as e:
            log.error(f"Error populating playlist editor combo: {e}")

    def _on_playlist_programs_selection_changed(self) -> None:
        """Handle selection change in playlist programs table."""
        if not self.delete_from_playlist_button or not self.playlist_editor_combo:
            return

        selected_rows = self.playlist_programs_table.selectionModel().selectedRows()
        # Get current value and map to playlist_id
        current_value = self.playlist_editor_combo.value()
        playlist_id = self._playlist_value_to_id.get(current_value)

        # Enable delete button only if playlist is selected and rows are selected
        self.delete_from_playlist_button.setEnabled(
            playlist_id is not None and len(selected_rows) > 0
        )

    def _on_playlist_value_changed(self, value: int) -> None:
        """Handle playlist selection change in the editor.

        :param value: The value from the combo box (mapped to playlist_id)
        """
        if not self.playlist_editor_combo:
            return

        # Map value to playlist_id
        playlist_id = self._playlist_value_to_id.get(value)
        if playlist_id:
            self.populate_playlist_programs_table(playlist_id)
            # Enable add button when playlist is selected
            if self.add_to_playlist_button:
                self.add_to_playlist_button.setEnabled(True)
            # Delete button state will be updated by selection change handler
            self._on_playlist_programs_selection_changed()
        else:
            if self.playlist_programs_table:
                self.playlist_programs_table.setRowCount(0)
            # Disable buttons when no playlist is selected
            if self.add_to_playlist_button:
                self.add_to_playlist_button.setEnabled(False)
            if self.delete_from_playlist_button:
                self.delete_from_playlist_button.setEnabled(False)

    def populate_playlist_programs_table(self, playlist_id: int) -> None:
        """
        Populate the playlist programs table with programs from the selected playlist.

        :param playlist_id: Playlist ID
        """
        if not self.playlist_programs_table:
            return

        try:
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            playlist_items = db.get_playlist_programs(playlist_id)
        except Exception as e:
            log.error(f"Error loading playlist programs: {e}")
            import traceback

            log.error(traceback.format_exc())
            playlist_items = []

        # Clear table
        self.playlist_programs_table.setRowCount(0)

        # Populate table
        for item_data in playlist_items:
            program = item_data["program"]
            midi_file_path = item_data.get("midi_file_path")
            cheat_preset_id = item_data.get("cheat_preset_id")
            row = self.playlist_programs_table.rowCount()
            self.playlist_programs_table.insertRow(row)

            # Extract bank and number from program ID
            bank_letter = program.id[0] if program.id else ""
            try:
                program_number = int(program.id[1:3]) if len(program.id) >= 3 else 0
            except ValueError:
                program_number = 0

            # Bank
            bank_item = QTableWidgetItem(bank_letter)
            bank_item.setFlags(bank_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.playlist_programs_table.setItem(row, 0, bank_item)

            # Number
            number_item = QTableWidgetItem(str(program_number))
            number_item.setFlags(number_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.playlist_programs_table.setItem(row, 1, number_item)

            # Program Name
            name_item = QTableWidgetItem(program.name or "")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.playlist_programs_table.setItem(row, 2, name_item)

            # MIDI File Name (editable via delegate)
            midi_file_item = QTableWidgetItem(midi_file_path if midi_file_path else "")
            midi_file_item.setFlags(midi_file_item.flags() | Qt.ItemFlag.ItemIsEditable)
            # Store playlist_id and program_id for saving
            midi_file_item.setData(
                Qt.ItemDataRole.UserRole + 1,
                {"playlist_id": playlist_id, "program_id": program.id},
            )
            self.playlist_programs_table.setItem(row, 3, midi_file_item)

            # Cheat Preset ComboBox
            cheat_preset_combo = QComboBox()
            cheat_preset_combo.addItem("None", None)  # No cheat preset
            # Add Digital Synth presets

            for preset in JDXi.UI.Preset.Digital.LIST:
                preset_id = preset["id"]
                preset_name = preset["name"]
                cheat_preset_combo.addItem(f"{preset_id} - {preset_name}", preset_id)
            # Set current selection
            if cheat_preset_id:
                index = cheat_preset_combo.findData(cheat_preset_id)
                if index >= 0:
                    cheat_preset_combo.setCurrentIndex(index)
            # Connect change handler
            cheat_preset_combo.currentIndexChanged.connect(
                lambda idx, r=row: self._on_cheat_preset_changed(
                    r, cheat_preset_combo.itemData(idx)
                )
            )
            # Store playlist_id and program_id for saving
            cheat_preset_combo.setProperty("playlist_id", playlist_id)
            cheat_preset_combo.setProperty("program_id", program.id)
            self.playlist_programs_table.setCellWidget(row, 4, cheat_preset_combo)

            # Play button (delegate handles this)
            play_item = QTableWidgetItem("")
            play_item.setFlags(play_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.playlist_programs_table.setItem(row, 5, play_item)

            # Store program object in item data (except MIDI file column which has its own data)
            for col in [0, 1, 2, 5]:  # Bank, Number, Program Name, Play columns
                table_item = self.playlist_programs_table.item(row, col)
                if table_item:
                    table_item.setData(Qt.ItemDataRole.UserRole, program)

        log.message(
            f"✅ Populated playlist programs table with {len(playlist_items)} programs"
        )

    def _on_cheat_preset_changed(
        self, row: int, cheat_preset_id: Optional[str]
    ) -> None:
        """
        Handle cheat preset selection change.

        :param row: Table row index
        :param cheat_preset_id: Selected cheat preset ID or None
        """
        if not self.playlist_programs_table:
            return

        combo = self.playlist_programs_table.cellWidget(row, 4)
        if not combo:
            return

        playlist_id = combo.property("playlist_id")
        program_id = combo.property("program_id")

        if not playlist_id or not program_id:
            return

        try:
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            db.update_playlist_item_cheat_preset(
                playlist_id, program_id, cheat_preset_id
            )
            log.message(
                f"✅ Updated cheat preset for playlist {playlist_id}, program {program_id}: {cheat_preset_id}"
            )
        except Exception as e:
            log.error(f"❌ Failed to update cheat preset: {e}")
            import traceback

            log.error(traceback.format_exc())

    def _on_playlist_program_item_changed(self, item: QTableWidgetItem) -> None:
        """
        Handle changes to playlist program items (e.g., MIDI file path).

        :param item: The table item that was changed
        """
        col = item.column()

        # Only handle MIDI file column (col 3)
        if col != 3:
            return

        # Get playlist/program data
        playlist_data = item.data(Qt.ItemDataRole.UserRole + 1)
        if not playlist_data:
            return

        playlist_id = playlist_data["playlist_id"]
        program_id = playlist_data["program_id"]
        midi_file_path = item.text().strip() if item.text() else None

        # Save to database
        from jdxi_editor.ui.programs.database import get_database

        db = get_database()
        if db.update_playlist_item_midi_file(playlist_id, program_id, midi_file_path):
            log.message(
                f"✅ Saved MIDI file path for playlist {playlist_id}, program {program_id}: {midi_file_path}"
            )
        else:
            log.error(
                f"❌ Failed to save MIDI file path for playlist {playlist_id}, program {program_id}"
            )

    def add_program_to_playlist(self) -> None:
        """Add a program to the selected playlist."""
        if not self.playlist_editor_combo:
            return

        # Check if a playlist is selected
        current_value = self.playlist_editor_combo.value()
        playlist_id = self._playlist_value_to_id.get(current_value)
        if not playlist_id:
            QMessageBox.information(
                self, "No Playlist Selected", "Please select a playlist first."
            )
            return
        self.show_select_programs_dialog(playlist_id=playlist_id)

    def show_select_programs_dialog(self, playlist_id: int):
        """Show a dialog to select programs from User Programs table"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Programs to Playlist")
        dialog_layout = QVBoxLayout(dialog)

        # Get playlist name from combo box text
        playlist_text = self.playlist_editor_combo.combo_box.currentText()
        playlist_name = (
            playlist_text.split(" (")[0] if " (" in playlist_text else playlist_text
        )
        dialog_layout.addWidget(
            QLabel(f"Select a program to add to '{playlist_name}':")
        )
        program_options = []
        program_values = []
        program_value_to_id = {}  # Map combo box values to program IDs

        try:
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            all_programs = db.get_all_programs()

            # --- Get programs already in playlist
            existing_programs = db.get_playlist_programs(playlist_id)
            existing_program_ids = {item["program"].id for item in existing_programs}

            # --- Add programs that aren't already in the playlist
            for idx, program in enumerate(all_programs):
                if program.id not in existing_program_ids:
                    display_text = f"{program.id} - {program.name}"
                    program_options.append(display_text)
                    # Use index as value (0-based)
                    value = len(program_values)
                    program_values.append(value)
                    program_value_to_id[value] = program.id
        except Exception as e:
            log.error(f"Error loading programs for playlist: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load programs: {e}")
            return

        if not program_options:
            QMessageBox.information(
                self,
                "No Programs Available",
                "All programs are already in this playlist.",
            )
            return

        # Create combo box with all available programs
        program_list = SearchableFilterableComboBox(
            label="",
            options=program_options,
            values=program_values,
            categories=None,
            category_filter_func=None,
            show_label=False,
            show_search=True,
            show_category=False,
            search_placeholder="Search programs...",
        )
        dialog_layout.addWidget(program_list)

        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected value from combo box
            selected_value = program_list.value()
            program_id = program_value_to_id.get(selected_value)

            if not program_id:
                QMessageBox.information(
                    self, "No Selection", "Please select a program to add."
                )
                return

            # --- Add selected program to playlist
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            added_count = 0
            if db.add_program_to_playlist(playlist_id, program_id):
                added_count = 1

            if added_count > 0:
                log.message(f"✅ Added {added_count} program(s) to playlist")
                # --- Refresh the table
                self.populate_playlist_programs_table(playlist_id)
                # Refresh combo to update program count
                self.populate_playlist_combo()
                if self.on_refresh_playlist_combo_callback:
                    self.on_refresh_playlist_combo_callback()
                # --- Restore selection by finding the value that maps to playlist_id
                value_to_select = None
                for value, pid in self._playlist_value_to_id.items():
                    if pid == playlist_id:
                        value_to_select = value
                        break
                if value_to_select is not None:
                    self.playlist_editor_combo.setValue(value_to_select)
                self.playlist_programs_changed.emit()
            else:
                QMessageBox.warning(
                    self, "Error", "Failed to add programs to playlist."
                )

    def delete_program_from_playlist(self) -> None:
        """Delete selected program(s) from the playlist."""
        if not self.playlist_editor_combo or not self.playlist_programs_table:
            return

        # --- Check if a playlist is selected
        current_value = self.playlist_editor_combo.value()
        playlist_id = self._playlist_value_to_id.get(current_value)
        if not playlist_id:
            QMessageBox.information(
                self, "No Playlist Selected", "Please select a playlist first."
            )
            return

        # --- Get selected rows
        selected_rows = self.playlist_programs_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Please select at least one program to delete."
            )
            return

        # --- Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Programs",
            f"Are you sure you want to delete {len(selected_rows)} program(s) from the playlist?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            from jdxi_editor.ui.programs.database import get_database

            db = get_database()
            deleted_count = 0

            # Delete in reverse order to maintain row indices
            for row_index in sorted([row.row() for row in selected_rows], reverse=True):
                # Get program ID from the table
                program_item = self.playlist_programs_table.item(
                    row_index, 0
                )  # Bank column has program data
                if program_item:
                    program = program_item.data(Qt.ItemDataRole.UserRole)
                    if program and isinstance(program, JDXiProgram):
                        if db.remove_program_from_playlist(playlist_id, program.id):
                            deleted_count += 1

            if deleted_count > 0:
                log.message(f"✅ Deleted {deleted_count} program(s) from playlist")
                # Refresh the table
                self.populate_playlist_programs_table(playlist_id)
                # Refresh combo to update program count
                self.populate_playlist_combo()
                if self.on_refresh_playlist_combo_callback:
                    self.on_refresh_playlist_combo_callback()
                # Restore selection by finding the value that maps to playlist_id
                value_to_select = None
                for value, pid in self._playlist_value_to_id.items():
                    if pid == playlist_id:
                        value_to_select = value
                        break
                if value_to_select is not None:
                    self.playlist_editor_combo.setValue(value_to_select)
                self.playlist_programs_changed.emit()
            else:
                QMessageBox.warning(
                    self, "Error", "Failed to delete programs from playlist."
                )

    def _play_playlist_program(self, index) -> None:
        """
        Play the MIDI file associated with a playlist program.

        :param index: QModelIndex of the play button
        """
        if not self.playlist_programs_table:
            return

        row = index.row()
        program_item = self.playlist_programs_table.item(row, 2)  # Program name column
        if not program_item:
            return

        program = program_item.data(Qt.ItemDataRole.UserRole)
        if not program:
            return

        # Get MIDI file path from the MIDI file column
        midi_file_item = self.playlist_programs_table.item(row, 3)
        midi_file_path = midi_file_item.text() if midi_file_item else None

        # Always load the program via MIDI Program Change first
        self._load_program_from_table(row)

        # Load cheat preset if selected (send on Analog Synth channel 3)
        # Add a delay to ensure the main program change is processed first
        cheat_preset_combo = self.playlist_programs_table.cellWidget(row, 4)
        log.message(
            f"🔍 Checking cheat preset for row {row}: combo={cheat_preset_combo}"
        )
        if cheat_preset_combo:
            cheat_preset_id = cheat_preset_combo.currentData()
            log.message(
                f"🔍 Cheat preset ID from combo: {cheat_preset_id} (type: {type(cheat_preset_id)})"
            )
            if cheat_preset_id:
                log.message(
                    f"🎹 Scheduling cheat preset load: {cheat_preset_id} (delayed by 500ms)"
                )
                # Delay cheat preset loading to ensure main program change is processed first
                QTimer.singleShot(500, lambda: self._load_cheat_preset(cheat_preset_id))
            else:
                log.message("ℹ️ No cheat preset selected (None)")
        else:
            log.warning(f"⚠️ Cheat preset combo box not found for row {row}")

        # If MIDI file is specified, load and play it
        if midi_file_path:
            from mido import MidiFile

            # Check if file exists
            if not os.path.exists(midi_file_path):
                log.warning(f"⚠️ MIDI file not found: {midi_file_path}")
                QMessageBox.warning(
                    self, "File Not Found", f"MIDI file not found:\n{midi_file_path}"
                )
                return

            log.message(
                f"🎵 Loading and playing MIDI file: {midi_file_path} for program {program.id}"
            )

            # Get the parent instrument to access MidiFileEditor
            parent_instrument = None
            if self.get_parent_instrument_callback:
                parent_instrument = self.get_parent_instrument_callback()
            else:
                # Fallback: try to get from parent widget
                parent_instrument = getattr(self, "parent", None)
                # Walk up the parent chain to find JDXiInstrument if needed
                while parent_instrument and not hasattr(
                    parent_instrument, "get_existing_editor"
                ):
                    next_parent = getattr(parent_instrument, "parent", None)
                    if not next_parent:
                        break
                    parent_instrument = next_parent

            if parent_instrument and hasattr(parent_instrument, "get_existing_editor"):
                # Get or create MidiFileEditor
                from jdxi_editor.ui.editors.io.player import MidiFileEditor

                midi_file_editor = parent_instrument.get_existing_editor(MidiFileEditor)

                if not midi_file_editor:
                    # Create the editor if it doesn't exist
                    parent_instrument.show_editor("midi_file")
                    midi_file_editor = parent_instrument.get_existing_editor(
                        MidiFileEditor
                    )

                if midi_file_editor:
                    # Load the MIDI file directly (bypassing the file dialog)
                    try:
                        # Disconnect any existing finished signal from previous playlist playback
                        if self._playlist_midi_editor and hasattr(
                            self._playlist_midi_editor, "midi_playback_worker"
                        ):
                            if self._playlist_midi_editor.midi_playback_worker:
                                try:
                                    self._playlist_midi_editor.midi_playback_worker.finished.disconnect(
                                        self._on_playlist_playback_finished
                                    )
                                except:
                                    pass

                        # Stop any current playback
                        if hasattr(midi_file_editor, "midi_stop_playback"):
                            midi_file_editor.midi_playback_stop()
                        if hasattr(midi_file_editor, "midi_playback_worker_stop"):
                            midi_file_editor.midi_playback_worker_stop()

                        # Reset tracking if we're starting a new playback
                        self._current_playlist_row = None
                        self._playlist_midi_editor = None

                        # Load MIDI file
                        midi_file_editor.midi_state.file = MidiFile(midi_file_path)
                        midi_file_editor.ui.digital_title_file_name.setText(
                            f"Loaded: {Path(midi_file_path).name}"
                        )
                        midi_file_editor.ui.midi_track_viewer.clear()
                        midi_file_editor.ui.midi_track_viewer.set_midi_file(
                            midi_file_editor.midi_state.file
                        )

                        # Initialize MIDI file parameters (similar to midi_load_file)
                        midi_file_editor.ticks_per_beat = (
                            midi_file_editor.midi_state.file.ticks_per_beat
                        )

                        # Detect initial tempo
                        if hasattr(midi_file_editor, "detect_initial_tempo"):
                            initial_track_tempos = (
                                midi_file_editor.detect_initial_tempo()
                            )

                        midi_file_editor.ui_display_set_tempo_usecs(
                            midi_file_editor.midi_state.tempo_initial
                        )
                        midi_file_editor.midi_state.tempo_at_position = (
                            midi_file_editor.midi_state.tempo_initial
                        )

                        midi_file_editor.midi_channel_select()
                        midi_file_editor.midi_extract_events()
                        midi_file_editor.setup_worker()
                        midi_file_editor.calculate_duration()
                        midi_file_editor.calculate_tick_duration()
                        midi_file_editor.ui_position_slider_reset()

                        # Store current playlist row and editor for auto-advance
                        self._current_playlist_row = row
                        self._playlist_midi_editor = midi_file_editor

                        # Connect to worker's finished signal for auto-advance
                        if (
                            hasattr(midi_file_editor, "midi_playback_worker")
                            and midi_file_editor.midi_playback_worker
                        ):
                            try:
                                # Disconnect any existing connection
                                midi_file_editor.midi_playback_worker.finished.disconnect()
                            except:
                                pass
                            # Connect to finished signal
                            midi_file_editor.midi_playback_worker.finished.connect(
                                self._on_playlist_playback_finished
                            )

                        # Start playback
                        midi_file_editor.midi_playback_start()

                        log.message(
                            f"✅ Started playing MIDI file: {Path(midi_file_path).name}"
                        )
                    except Exception as e:
                        log.error(f"❌ Error loading/playing MIDI file: {e}")
                        import traceback

                        log.error(traceback.format_exc())
                        QMessageBox.warning(
                            self, "Error", f"Failed to load MIDI file:\n{str(e)}"
                        )
                        # Reset tracking on error
                        self._current_playlist_row = None
                        self._playlist_midi_editor = None
                else:
                    log.error("❌ Could not access MidiFileEditor")
            else:
                log.warning("⚠️ Could not access parent instrument to load MIDI file")
        else:
            log.message(
                f"ℹ️ No MIDI file selected for program {program.id}, only program loaded"
            )

    def _on_playlist_playback_finished(self):
        """Called when MIDI playback finishes. Advances to the next playlist item."""
        if self._current_playlist_row is None or not self.playlist_programs_table:
            return

        # Disconnect the finished signal
        if self._playlist_midi_editor and hasattr(
            self._playlist_midi_editor, "midi_playback_worker"
        ):
            try:
                if self._playlist_midi_editor.midi_playback_worker:
                    self._playlist_midi_editor.midi_playback_worker.finished.disconnect(
                        self._on_playlist_playback_finished
                    )
            except:
                pass

        # Advance to next row
        next_row = self._current_playlist_row + 1

        # Check if there's a next row
        if next_row >= self.playlist_programs_table.rowCount():
            log.message("✅ Playlist playback completed - reached end of playlist")
            self._current_playlist_row = None
            self._playlist_midi_editor = None
            return

        # Check if next row has a MIDI file
        midi_file_item = self.playlist_programs_table.item(next_row, 3)
        if not midi_file_item or not midi_file_item.text():
            log.message(
                f"⚠️ Next playlist item (row {next_row}) has no MIDI file, stopping auto-advance"
            )
            self._current_playlist_row = None
            self._playlist_midi_editor = None
            return

        # Play the next item
        log.message(f"🎵 Auto-advancing to next playlist item (row {next_row})")
        # Create a QModelIndex for the play button column (column 5)
        model = self.playlist_programs_table.model()
        if model:
            next_index = model.index(next_row, 5)  # Play button column
            self._play_playlist_program(next_index)
        else:
            log.error("❌ Could not get table model for auto-advance")
            self._current_playlist_row = None
            self._playlist_midi_editor = None

    def _on_playlist_program_double_clicked(self, item: QTableWidgetItem) -> None:
        """
        Handle double-click on a playlist program item.
        If the Program Name column (column 2) is clicked, show the Program Editor.

        :param item: The table item that was double-clicked
        """
        column = item.column()

        # Only handle double-click on Program Name column (column 2)
        if column != 2:
            return

        log.message("📝 Opening Program Editor from playlist double-click")

        # Try to get the parent instrument to show the Program Editor
        parent_instrument = None
        if self.get_parent_instrument_callback:
            parent_instrument = self.get_parent_instrument_callback()
        else:
            parent_instrument = getattr(self, "parent", None)

        # Walk up the parent chain to find JDXiInstrument if needed
        while parent_instrument:
            if hasattr(parent_instrument, "show_editor") and hasattr(
                parent_instrument, "get_existing_editor"
            ):
                # Found JDXiInstrument
                try:
                    # Check if ProgramEditor is already open
                    from jdxi_editor.ui.editors.io.program import ProgramEditor

                    existing_editor = parent_instrument.get_existing_editor(
                        ProgramEditor
                    )
                    if existing_editor:
                        # Already open, just raise it
                        # Ensure window is in normal state (not minimized)
                        from PySide6.QtCore import Qt
                        from PySide6.QtWidgets import QApplication

                        window_state = existing_editor.windowState()
                        if window_state & Qt.WindowState.WindowMinimized:
                            existing_editor.setWindowState(
                                window_state & ~Qt.WindowState.WindowMinimized
                            )

                        # Make sure the window is visible and on top
                        existing_editor.showNormal()  # Restore if minimized
                        existing_editor.show()
                        existing_editor.raise_()
                        existing_editor.activateWindow()

                        # On macOS, also activate the application
                        app = QApplication.instance()
                        if app:
                            app.setActiveWindow(existing_editor)

                        # Load the program from the double-clicked row
                        row = item.row()
                        self._load_program_from_table(row)
                        log.message("✅ Raised existing Program Editor window")
                    else:
                        # Not open, show it via parent
                        parent_instrument.show_editor("program")
                        log.message("✅ Opened Program Editor via parent")
                    return
                except Exception as e:
                    log.error(f"❌ Error showing Program Editor: {e}")
                    import traceback

                    log.error(traceback.format_exc())
                    return

            # Try to get parent's parent
            next_parent = getattr(parent_instrument, "parent", None)
            if not next_parent:
                # Try QWidget.parent() method as fallback
                try:
                    if hasattr(parent_instrument, "parent"):
                        next_parent = parent_instrument.parent()
                except:
                    pass

            if not next_parent or next_parent == parent_instrument:
                break
            parent_instrument = next_parent

        # If we couldn't find JDXiInstrument, try to show/raise this window itself
        log.warning(
            "⚠️ Could not find parent JDXiInstrument, trying to show current window"
        )
        try:
            self.show()
            self.raise_()
            self.activateWindow()
            log.message("✅ Raised current Program Editor window")
        except Exception as e:
            log.error(f"❌ Error raising Program Editor window: {e}")

    def _load_program_from_table(self, row: int) -> None:
        """
        Load a program from the playlist programs table and send MIDI Program Change.

        :param row: Row index in the table
        """
        if (
            not self.playlist_programs_table
            or row < 0
            or row >= self.playlist_programs_table.rowCount()
        ):
            return

        # Get program from first column's user data
        item = self.playlist_programs_table.item(row, 0)
        if not item:
            return

        program = item.data(Qt.ItemDataRole.UserRole)
        if not program or not isinstance(program, JDXiProgram):
            return

        # Get program ID and extract bank/number
        program_id = program.id
        if not program_id or len(program_id) < 3:
            log.warning(f"Invalid program ID: {program_id}")
            return

        bank_letter = program_id[0]
        try:
            bank_number = int(program_id[1:3])
        except ValueError:
            log.warning(f"Invalid program number in ID: {program_id}")
            return

        log.message(f"🎹 Loading program from playlist: {program_id} - {program.name}")

        # Calculate MIDI values
        try:
            msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        except (ValueError, TypeError) as e:
            log.error(f"Error calculating MIDI values for {program_id}: {e}")
            return

        # Send MIDI Program Change
        if self.midi_helper:
            log.message(f"Sending Program Change: MSB={msb}, LSB={lsb}, PC={pc}")
            self.midi_helper.send_bank_select_and_program_change(
                self.channel, msb, lsb, pc
            )

        # Emit signal and call callback
        if self.on_program_loaded_callback:
            self.on_program_loaded_callback(program)

    def _load_cheat_preset(self, preset_id: str) -> None:
        """
        Load a cheat preset (Digital Synth preset) on the Analog Synth channel (Ch3).

        :param preset_id: Preset ID (e.g., "113")
        """
        log.message(
            f"🎹 _load_cheat_preset called with preset_id: {preset_id} (type: {type(preset_id)})"
        )

        if not self.midi_helper:
            log.warning("⚠️ MIDI helper not available for cheat preset loading")
            return

        if not preset_id:
            log.warning("⚠️ Preset ID is None or empty")
            return

        log.message(
            f"🎹 Loading cheat preset {preset_id} on Analog Synth channel (Ch3)"
        )

        # Get preset parameters from JDXi.UI.Preset.Digital.LIST
        from jdxi_editor.log.midi_info import log_midi_info
        from jdxi_editor.midi.channel.channel import MidiChannel

        # Find preset in JDXi.UI.Preset.Digital.LIST
        preset = None
        for p in JDXi.UI.Preset.Digital.LIST:
            if str(p["id"]) == str(
                preset_id
            ):  # Compare as strings to handle any type mismatches
                preset = p
                break

        if not preset:
            log.warning(
                f"⚠️ Cheat preset {preset_id} not found in JDXi.UI.Preset.Digital.LIST"
            )
            log.message(
                f"🔍 Available preset IDs (first 10): {[p['id'] for p in JDXi.UI.Preset.Digital.LIST[:10]]}"
            )
            return

        # Get MSB, LSB, PC values and convert to integers (preset data has floats)
        msb = int(preset.get("msb", 95))
        lsb = int(preset.get("lsb", 64))
        pc = int(preset.get("pc", int(preset_id)))

        log.message(f"📊 Cheat preset parameters: MSB={msb}, LSB={lsb}, PC={pc}")
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change on ANALOG_SYNTH channel (Ch3)
        # Note: PC is 0-based in MIDI, so subtract 1
        try:
            self.midi_helper.send_bank_select_and_program_change(
                MidiChannel.ANALOG_SYNTH,  # Send to Analog Synth channel (Ch3)
                msb,  # MSB (typically 95 for Digital Synth presets)
                lsb,  # LSB (typically 64)
                pc - 1,  # Convert 1-based PC to 0-based
            )
            log.message(
                f"✅ Sent cheat preset Program Change: Ch3, MSB={msb}, LSB={lsb}, PC={pc - 1} (0-based)"
            )
        except Exception as e:
            log.error(f"❌ Error sending cheat preset Program Change: {e}")
            import traceback

            log.error(traceback.format_exc())
