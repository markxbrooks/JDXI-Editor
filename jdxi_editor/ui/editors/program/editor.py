"""
ProgramEditor Module

This module defines the `ProgramEditor` class, a PySide6-based GUI for
managing and selecting MIDI programs.

It allows users to browse, filter, and load programs based on bank, genre,
and program number.

The class also facilitates MIDI integration by sending Program Change (PC)
and Bank Select (CC#0, CC#32) messages.

Key Features:
- Graphical UI for selecting and managing MIDI programs.
- Filtering options based on bank and genre.
- MIDI integration for program selection and loading.
- Image display for program categories.
- Program list population based on predefined program data.

Classes:
    ProgramEditor(QMainWindow)
        A main window class for handling MIDI program selection and management.

Signals:
    program_changed (int, str, int)
        Emitted when a program selection changes. Parameters:
        - MIDI channel (int)
        - Preset name (str)
        - Program number (int)

Dependencies:
- PySide6.QtWidgets
- PySide6.QtCore
- MIDIHelper for MIDI message handling
- PresetHandler for managing program presets
- JDXiProgramList.PROGRAM_LIST for predefined program data

"""

from typing import Dict, Optional

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetSuperNATURALLMB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_MAP
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital import DigitalCommonParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.midi.sysex.partial.switch import PartialSelectState, PartialSwitchState
from jdxi_editor.midi.sysex.request.data import SYNTH_PARTIAL_MAP
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys, get_partial_number
from jdxi_editor.ui.editors.playlist.editor import PlaylistEditor
from jdxi_editor.ui.editors.playlist.table import PlaylistTable
from jdxi_editor.ui.editors.preset.type import PresetTitle
from jdxi_editor.ui.editors.preset.widget import PresetWidget
from jdxi_editor.ui.editors.program.group import ProgramGroup
from jdxi_editor.ui.editors.program.helper import create_placeholder_icon
from jdxi_editor.ui.editors.program.mixer import ProgramMixer
from jdxi_editor.ui.editors.program.user_programs_widget import UserProgramsWidget
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.preset.tone.lists import JDXiUIPreset
from jdxi_editor.ui.programs.programs import JDXiUIProgramList
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget


class ProgramEditor(BasicEditor):
    """Program Editor Window"""

    program_changed = Signal(int, str, int)  # (channel, preset_name, program_number)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
        preset_helper: JDXiPresetHelper = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.title_right_vlayout = None
        self.program_list = None
        """
        Initialize the ProgramEditor

        :param midi_helper: Optional[MidiIOHelper]
        :param parent: Optional[QWidget]
        :param preset_helper: JDXIPresetHelper
        """
        self.setWindowFlag(Qt.Window)
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.channel = (
            MidiChannel.PROGRAM  # Default MIDI channel: 16 for programs, 0-based
        )
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL
        self.default_image = "programs.png"
        self.instrument_icon_folder = "programs"
        self.instrument_title_label = QLabel()  # Just to stop error messages for now
        self.layout = None
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL
        self.midi_channel = 0  # Defaults to DIGITAL 1
        self.genre_label = None
        self.program_name = ""
        self.bank_combo_box = None
        self.save_button = None
        self.title_label = None
        self.bank_label = None
        self.program_label = None
        self.genre_combo_box = None

        # program_preset will be set up in setup_ui() via ProgramGroupWidget
        self.program_preset: Optional[PresetWidget] = None
        self.preset_type = None
        self.programs = {}  # Maps program names to numbers
        self._actual_preset_list = (
            JDXi.UI.Preset.Digital.PROGRAM_CHANGE  # Default preset list for combo box
        )
        # Initialize widget references before setup_ui() to prevent AttributeError
        # if callbacks are triggered during widget creation
        self.controls: Dict[AddressParameter, QWidget] = {}
        self.mixer_widget: Optional[ProgramMixer] = None
        self.program_group_widget: Optional[ProgramGroup] = None
        self.user_programs_widget: Optional[UserProgramsWidget] = None
        self.playlist_widget: Optional[PlaylistTable] = None
        self.playlist_editor_widget: Optional[PlaylistEditor] = None
        self.setup_ui()
        self.midi_helper.update_program_name.connect(self.set_current_program_name)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)

    def setup_ui(self):
        """set up ui elements"""
        self.setWindowTitle("Program Editor")
        self.setMinimumSize(400, 400)
        main_vlayout = QVBoxLayout()

        # Create main tab widget for top-level tabs
        self.main_tab_widget = QTabWidget()
        main_vlayout.addWidget(self.main_tab_widget)

        # --- Use EditorBaseWidget for Programs/Presets tab
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        # container_layout = self.base_widget.get_container_layout()

        # Create centered content widget
        centered_content = QWidget()
        self.title_vlayout = QVBoxLayout(centered_content)
        self.title_vlayout.addStretch()

        self.title_hlayout = QHBoxLayout()
        self.title_hlayout.addStretch()

        self.title_left_vlayout = QVBoxLayout()
        self.title_hlayout.addLayout(self.title_left_vlayout)

        self.title_right_vlayout = QVBoxLayout()
        self.title_hlayout.addLayout(self.title_right_vlayout)

        self.title_hlayout.addStretch()
        self.title_vlayout.addLayout(self.title_hlayout)
        self.title_vlayout.addStretch()

        # Add centered content to base widget
        self.base_widget.add_centered_content(centered_content)

        # Add Programs/Presets tab to main tab widget (base widget contains the scroll area)
        try:
            programs_presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC_NOTE_MULTIPLE, color=JDXi.UI.Style.GREY
            )
            if programs_presets_icon is None or programs_presets_icon.isNull():
                raise ValueError("Icon is null")
        except:
            programs_presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC, color=JDXi.UI.Style.GREY
            )
        self.main_tab_widget.addTab(
            self.base_widget, programs_presets_icon, "Programs & Presets"
        )

        # Add User Programs tab to main tab widget
        try:
            log.message(
                "🔨Creating User Programs tab for main window...",
                scope=self.__class__.__name__,
            )
            self.user_programs_widget = UserProgramsWidget(
                midi_helper=self.midi_helper,
                channel=self.channel,
                parent=self,
                on_program_loaded=self._on_user_program_loaded,
            )
            user_programs_icon = JDXi.UI.Icon.get_icon(
                "mdi.account-music", color=JDXi.UI.Style.GREY
            )
            self.main_tab_widget.addTab(
                self.user_programs_widget, user_programs_icon, "User Programs"
            )
            log.message(
                f"✅ Added 'User Programs' tab to main window (total tabs: {self.main_tab_widget.count()})",
                scope=self.__class__.__name__,
            )
            # Log all tab names for debugging
            for i in range(self.main_tab_widget.count()):
                log.message(
                    message=f"Main Tab {i}: '{self.main_tab_widget.tabText(i)}'",
                    scope=self.__class__.__name__,
                )
        except Exception as e:
            log.error(
                f"❌Error creating User Programs tab: {e}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.error(traceback.format_exc())
            placeholder_widget, user_programs_icon = create_placeholder_icon(
                e,
                error_message="Error loading user programs:",
                icon_name="mdi.account-music",
            )
            self.main_tab_widget.addTab(
                placeholder_widget, user_programs_icon, "User Programs"
            )
            log.message(
                f"✅ Added 'User Programs' tab (placeholder) (total tabs: {self.main_tab_widget.count()})",
                scope=self.__class__.__name__,
            )

        # --- Add Playlist tab to main tab widget
        try:
            log.message(
                "🔨Creating Playlist tab for main window...",
                scope=self.__class__.__name__,
            )
            self.playlist_widget = PlaylistTable(
                parent=self,
                on_playlist_changed=self._on_playlist_changed,
            )
            playlist_icon = JDXi.UI.Icon.get_icon(
                "mdi.playlist-music", color=JDXi.UI.Style.GREY
            )
            self.main_tab_widget.addTab(self.playlist_widget, playlist_icon, "Playlist")
            log.message(
                f"✅ Added 'Playlist' tab to main window (total tabs: {self.main_tab_widget.count()})",
                scope=self.__class__.__name__,
            )
        except Exception as e:
            log.error(
                f"❌Error creating Playlist tab: {e}", scope=self.__class__.__name__
            )
            import traceback

            log.error(traceback.format_exc())
            placeholder_widget, playlist_icon = create_placeholder_icon(
                e,
                error_message="Error loading playlists: ",
                icon_name="mdi.playlist-music",
            )
            self.main_tab_widget.addTab(placeholder_widget, playlist_icon, "Playlist")
            log.message(
                f"✅ Added 'Playlist' tab (placeholder) (total tabs: {self.main_tab_widget.count()})",
                scope=self.__class__.__name__,
            )

        # Add Playlist Editor tab to main tab widget
        try:
            log.message(
                "🔨Creating Playlist Editor tab for main window...",
                scope=self.__class__.__name__,
            )
            self.playlist_editor_widget = PlaylistEditor(
                midi_helper=self.midi_helper,
                channel=self.channel,
                parent=self,
                on_program_loaded=self._on_playlist_program_loaded,
                on_refresh_playlist_combo=self._populate_playlist_editor_combo,
                get_parent_instrument=lambda: self._get_parent_instrument(),
            )
            playlist_editor_icon = JDXi.UI.Icon.get_icon(
                "mdi.playlist-edit", color=JDXi.UI.Style.GREY
            )
            self.main_tab_widget.addTab(
                self.playlist_editor_widget, playlist_editor_icon, "Playlist Editor"
            )
            log.message(
                f"✅ Added 'Playlist Editor' tab to main window (total tabs: {self.main_tab_widget.count()})",
                scope=self.__class__.__name__,
            )
        except Exception as e:
            log.error(
                f"❌Error creating Playlist Editor tab: {e}",
                scope=self.__class__.__name__,
            )
            import traceback

            log.error(traceback.format_exc())
            # Create a placeholder widget so the tab still appears
            placeholder_widget, playlist_editor_icon = create_placeholder_icon(
                e,
                error_message="Error loading playlist editor: ",
                icon_name="mdi.playlist-edit",
            )
            self.main_tab_widget.addTab(
                placeholder_widget, playlist_editor_icon, "Playlist Editor"
            )
            log.message(
                f"✅Added 'Playlist Editor' tab (placeholder) (total tabs: {self.main_tab_widget.count()})",
                scope=self.__class__.__name__,
            )

        self.setLayout(main_vlayout)
        self.setStyleSheet(JDXi.UI.Style.EDITOR)

        program_preset_hlayout = QHBoxLayout()
        program_preset_hlayout.addStretch()

        # Create ProgramGroupWidget
        self.program_group_widget = ProgramGroup(parent=self)
        self.program_group_widget.channel = self.channel
        # Sync program_preset reference for backward compatibility
        self.program_preset = self.program_group_widget.preset
        program_preset_hlayout.addStretch()
        program_preset_hlayout.addWidget(self.program_group_widget)

        program_preset_hlayout.addStretch()

        # Create PresetWidget and add it to the tab widget
        # Note: The preset widget is already created inside ProgramGroupWidget
        # We need to add it to the program_preset_tab_widget
        try:
            presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC_NOTE_MULTIPLE, color=JDXi.UI.Style.GREY
            )
            if presets_icon.isNull():
                raise ValueError("Icon is null")
        except:
            presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC, color=JDXi.UI.Style.GREY
            )
        self.program_group_widget.program_preset_tab_widget.addTab(
            self.program_group_widget.preset, presets_icon, "Presets"
        )
        log.message(
            f"📑Added 'Presets' tab to program_preset_tab_widget (total tabs: {self.program_group_widget.program_preset_tab_widget.count()})",
            scope="ProgramEditor ",
        )
        program_preset_hlayout.addStretch()

        self.title_left_vlayout.addLayout(program_preset_hlayout)
        self.title_left_vlayout.addStretch()

        self.populate_programs()

        # Create mixer widget
        self.mixer_widget = ProgramMixer(
            midi_helper=self.midi_helper, parent=self
        )
        mixer_group = self.mixer_widget.create_mixer_widget()

        # Merge mixer widget's controls into ProgramEditor's controls dict
        self.controls.update(self.mixer_widget.get_controls())

        # Wire mixer widget to program group widget
        self.program_group_widget.mixer_widget = self.mixer_widget

        self.right_hlayout = QHBoxLayout()
        self.right_hlayout.addWidget(mixer_group)
        self.title_right_vlayout.addLayout(self.right_hlayout)
        self.title_hlayout.addStretch()
        self.title_vlayout.addStretch()
        preset_type = PresetTitle.DIGITAL_SYNTH1
        self.set_channel_and_preset_lists(preset_type)
        self._populate_presets()
        self.midi_helper.update_tone_name.connect(
            lambda tone_name, synth_type: self.update_tone_name_for_synth(
                tone_name, synth_type
            )
        )
        self.update_instrument_image()

    def on_category_changed(self, _: int) -> None:
        """Handle category selection change - no longer needed, handled by SearchableFilterableComboBox."""
        pass

    def on_preset_type_changed(self, index: int) -> None:
        """
        on_preset_type_changed

        :param index: int
        Handle preset type selection change
        Note: This delegates to PresetWidget's on_preset_type_changed, but also
        updates ProgramEditor's internal state.
        """
        preset_type = (
            self.program_group_widget.preset.digital_preset_type_combo.currentText()
        )
        log.message(f"preset_type: {preset_type}")
        # Update ProgramEditor's channel and preset lists
        self.set_channel_and_preset_lists(preset_type)
        # PresetWidget handles its own combo box update via its on_preset_type_changed
        # But we also need to update ProgramEditor's combo box if it exists
        if hasattr(self, "_update_preset_combo_box"):
            self._update_preset_combo_box()

    def set_channel_and_preset_lists(self, preset_type: str) -> None:
        """
        set_channel_and_preset_lists

        :param preset_type:
        :return: None
        """
        if preset_type == PresetTitle.DIGITAL_SYNTH1:
            self.midi_channel = MidiChannel.DIGITAL_SYNTH_1
            self.program_group_widget.preset.preset_list = (
                JDXiUIPreset.Digital.PROGRAM_CHANGE
            )
        elif preset_type == PresetTitle.DIGITAL_SYNTH2:
            self.midi_channel = MidiChannel.DIGITAL_SYNTH_2
            self.program_group_widget.preset.preset_list = (
                JDXiUIPreset.Digital.PROGRAM_CHANGE
            )
        elif preset_type == PresetTitle.DRUMS:
            self.midi_channel = MidiChannel.DRUM_KIT
            self.program_group_widget.preset.preset_list = (
                JDXiUIPreset.Drum.PROGRAM_CHANGE
            )
        elif preset_type == PresetTitle.ANALOG_SYNTH:
            self.midi_channel = MidiChannel.ANALOG_SYNTH
            self.program_group_widget.preset.preset_list = (
                JDXiUIPreset.Analog.PROGRAM_CHANGE
            )

    def _update_preset_combo_box(self) -> None:
        """
        Update the SearchableFilterableComboBox with current preset list.
        Called when preset type changes.
        Note: This method is now handled by PresetWidget._update_preset_combo_box(),
        but kept here for backward compatibility if needed.
        """
        # Delegate to PresetWidget's method
        if hasattr(self.program_group_widget.preset, "_update_preset_combo_box"):
            self.program_group_widget.preset._update_preset_combo_box()

    def _populate_programs(self, search_text: str = "") -> None:
        """
        Populate the program list with available presets.
        Now delegates to populate_programs() which uses _update_program_combo_box().

        :param search_text: str
        :return: None
        """
        # Delegate to populate_programs which handles the combo box update
        self.populate_programs(search_text)

    def _populate_presets(self, search_text: str = "") -> None:
        """
        Populate the program list with available presets.
        Now handled by SearchableFilterableComboBox, so this just updates the combo box.

        :param search_text: str (ignored, handled by SearchableFilterableComboBox)
        :return: None
        """
        self._update_preset_combo_box()

    def _init_synth_data(
        self,
        synth_type: str = JDXiSynth.DIGITAL_SYNTH_1,
        partial_number: Optional[int] = 0,
    ) -> None:
        """

        :param synth_type: JDXiSynth
        :param partial_number: int
        :return: None
        Initialize synth-specific data
        """
        from jdxi_editor.core.synth.factory import create_synth_data

        self.synth_data = create_synth_data(synth_type, partial_number=partial_number)

        # Dynamically assign attributes
        for attr in [
            "address",
            "preset_type",
            "instrument_default_image",
            "instrument_icon_folder",
            "presets",
            "preset_list",
            "midi_requests",
            "midi_channel",
        ]:
            setattr(self, attr, getattr(self.synth_data, attr))

    def update_tone_name_for_synth(self, tone_name: str, synth_type: str) -> None:
        """
        Update the tone name.

        :param tone_name: str
        :param synth_type: str
        """
        if self.mixer_widget:
            self.mixer_widget.update_tone_name_for_synth(tone_name, synth_type)

    def set_current_program_name(
        self, program_name: str, synth_type: str = None
    ) -> None:
        """
        Set the current program name in the file label

        :param program_name: str
        :param synth_type: str (optional), discarded for now
        :return: None
        """
        self.program_name = program_name or "Untitled Program"
        # Update program group widget's file label
        if self.program_group_widget:
            self.program_group_widget.set_current_program_name(program_name)
        if self.mixer_widget:
            self.mixer_widget.update_program_name(program_name)

    def start_playback(self):
        """Start playback of the MIDI file."""
        self.midi_helper.send_raw_message([Midi.SONG.START])

    def stop_playback(self):
        """Stop playback of the MIDI file."""
        self.midi_helper.send_raw_message([Midi.SONG.STOP])

    def _update_program_combo_box(self) -> None:
        """
        Update the SearchableFilterableComboBox with current program list.
        Handles both ROM banks (A-D) and user banks (E-H) with SQLite integration.
        """
        if not self.preset_helper:
            return

        # --- Get all programs (ROM + user from database)
        all_programs = JDXiUIProgramList.list_rom_and_user_programs()
        if self.program_group_widget:
            self.program_group_widget._program_list_data = all_programs

        # --- Build program options, values, and filter data
        program_options = []
        program_values = []
        program_genres = set()
        program_banks = set()

        # --- Process ROM programs
        for program in all_programs:
            if program.id and len(program.id) >= 1:
                bank = program.id[0]
                program_banks.add(bank)
                if program.genre:
                    program_genres.add(program.genre)
                program_options.append(f"{program.id} - {program.name}")
                program_values.append(len(program_options) - 1)  # Use index as value

        # --- Add user bank placeholders (E, F, G, H) - these will be handled dynamically
        # but we need to ensure they're in the banks list
        program_banks.update(["E", "F", "G", "H"])

        # Bank filter function for programs
        def program_bank_filter(program_display: str, bank: str) -> bool:
            """Check if a program matches a bank."""
            if not bank:
                return True
            # --- Extract bank from display string (format: "A01 - Program Name")
            if " - " in program_display:
                program_id = program_display.split(" - ")[0]
            else:
                program_id = (
                    program_display.split()[0] if program_display.split() else ""
                )
            if program_id and len(program_id) >= 1:
                return program_id[0].upper() == bank.upper()
            return False

        # --- Genre filter function for programs
        def program_genre_filter(program_display: str, genre: str) -> bool:
            """Check if a program matches a genre."""
            if not genre:
                return True
            # --- Find the program in the list and check its genre
            # --- Extract program ID from display string
            if " - " in program_display:
                program_id = program_display.split(" - ")[0]
            else:
                program_id = (
                    program_display.split()[0] if program_display.split() else ""
                )

            # ---Find program in list
            program_list_data = (
                self.program_group_widget._program_list_data
                if self.program_group_widget
                else []
            )
            for program in program_list_data:
                if program.id == program_id:
                    return program.genre == genre if program.genre else False
            return False

        # --- Update the combo box by recreating it (since SearchableFilterableComboBox doesn't have update methods)
        # --- Get parent widget and layout from program_group_widget
        if not self.program_group_widget:
            return

        program_widget = self.program_group_widget.edit_program_name_button.parent()
        program_vlayout = program_widget.layout() if program_widget else None

        if program_vlayout:
            # --- Remove old combo box from layout
            program_vlayout.removeWidget(
                self.program_group_widget.program_number_combo_box
            )
            self.program_group_widget.program_number_combo_box.deleteLater()

            # ---Create new combo box with updated data
            self.program_group_widget.program_number_combo_box = (
                SearchableFilterableComboBox(
                    label="Program",
                    options=program_options,
                    values=program_values,
                    categories=sorted(program_genres),
                    banks=sorted(program_banks),
                    bank_filter_func=program_bank_filter,
                    category_filter_func=program_genre_filter,
                    show_label=True,
                    show_search=True,
                    show_category=True,
                    show_bank=True,
                    search_placeholder="Search programs...",
                    category_label="Genre:",
                    bank_label="Bank:",
                )
            )

            # --- Insert after edit_program_name_button
            index = program_vlayout.indexOf(
                self.program_group_widget.edit_program_name_button
            )
            program_vlayout.insertWidget(
                index + 1, self.program_group_widget.program_number_combo_box
            )

    def populate_programs(self, search_text: str = ""):
        """Populate the program list with available presets.
        Now handled by SearchableFilterableComboBox, so this just updates the combo box.
        Uses SQLite database to ensure all user bank programs are loaded correctly.
        """
        if not self.preset_helper:
            return

        # --- Update the combo box with current program data
        self._update_program_combo_box()

    def add_user_banks(
        self, filtered_list: list, bank: str, search_text: str = None
    ) -> None:
        """Add user banks to the program list.
        Only adds generic entries for programs that don't exist in the database.
        Uses SQLite database for reliable lookups.
        :param search_text:
        :param filtered_list: list of programs already loaded from database
        :param bank: str
        """
        from jdxi_editor.ui.programs.database import get_database

        user_banks = ["E", "F", "G", "H"]
        # --- Create sets for quick lookup
        existing_program_ids_in_filtered = {program.id for program in filtered_list}
        # --- Also check what's already in the combo box to avoid duplicates
        if (
            not self.program_group_widget
            or not self.program_group_widget.program_number_combo_box
        ):
            return
        existing_combo_items = {
            self.program_group_widget.program_number_combo_box.itemText(i)[
                :3
            ]  # --- Extract program ID (e.g., "E01")
            for i in range(self.program_group_widget.program_number_combo_box.count())
        }

        # --- Get database instance for direct queries
        db = get_database()

        for user_bank in user_banks:
            if bank in ["No Bank Selected", user_bank]:
                for i in range(1, 65):
                    program_id = f"{user_bank}{i:02}"

                    # --- Skip if already in combo box (avoid duplicates)
                    if program_id in existing_combo_items:
                        continue

                    # --- Check if program exists in filtered_list (already added)
                    if program_id in existing_program_ids_in_filtered:
                        continue

                    # --- Check database directly using SQLite
                    # --- Only add programs that exist in the database (single source of truth)
                    existing_program = db.get_program_by_id(program_id)
                    if not existing_program:
                        # --- If program doesn't exist in database, skip it (no placeholders)
                        continue

                    # --- Program exists in database, add it with real name
                    program_name = existing_program.name
                    if search_text and search_text.lower() not in program_name.lower():
                        continue
                    index = len(self.programs)
                    if (
                        self.program_group_widget
                        and self.program_group_widget.program_number_combo_box
                    ):
                        self.program_group_widget.program_number_combo_box.addItem(
                            f"{program_id} - {program_name}", index
                        )
                    self.programs[program_name] = index

    def _get_table_style(self) -> str:
        """
        Get custom styling for tables with rounded corners and charcoal embossed cells.

        :return: str CSS style string
        """
        return JDXi.UI.Style.DATABASE_TABLE_STYLE

    def _on_user_program_loaded(self, program: JDXiProgram) -> None:
        """
        Handle when a user program is loaded from the table.

        :param program: JDXiProgram that was loaded
        """
        # Request program data
        if hasattr(self, "program_helper") and self.program_helper:
            self.program_helper.data_request()
        elif hasattr(self, "data_request"):
            self.data_request()

        # Update UI
        self.set_current_program_name(program.name)
        if hasattr(self, "update_current_synths"):
            self.update_current_synths(program)

        # Also update the program combo box to reflect the selected program
        # Find the program in the combo box and select it
        if self.program_group_widget and hasattr(
            self.program_group_widget, "program_number_combo_box"
        ):
            for i in range(self.program_group_widget.program_number_combo_box.count()):
                item_text = self.program_group_widget.program_number_combo_box.itemText(
                    i
                )
                if item_text.startswith(program.id):
                    self.program_group_widget.program_number_combo_box.setCurrentIndex(
                        i
                    )
                    break

    def _on_playlist_changed(self) -> None:
        """
        Handle when a playlist is created, deleted, or updated.
        Refreshes the playlist editor combo if it exists.
        """
        if self.playlist_editor_widget:
            self.playlist_editor_widget.populate_playlist_combo()
            # Clear the programs table if the deleted playlist was selected
            if self.playlist_editor_widget.playlist_editor_combo:
                # Use .value() for SearchableFilterableComboBox (0 means no playlist selected)
                current_value = self.playlist_editor_widget.playlist_editor_combo.value()
                playlist_id = self.playlist_editor_widget._playlist_value_to_id.get(current_value)
                if (
                    playlist_id is None
                    and self.playlist_editor_widget.playlist_programs_table
                ):
                    self.playlist_editor_widget.playlist_programs_table.setRowCount(0)

    def _on_playlist_program_loaded(self, program: JDXiProgram) -> None:
        """
        Handle when a program is loaded from the playlist editor.
        Updates UI to reflect the loaded program.

        :param program: JDXiProgram that was loaded
        """
        self.set_current_program_name(program.name)
        if hasattr(self, "update_current_synths"):
            self.update_current_synths(program)
        # Request program data if program_helper exists
        if hasattr(self, "program_helper") and self.program_helper:
            self.program_helper.data_request()

    def _populate_playlist_editor_combo(self) -> None:
        """Populate the playlist editor combo (callback for playlist editor widget)."""
        if self.playlist_editor_widget:
            self.playlist_editor_widget.populate_playlist_combo()

    def _get_parent_instrument(self) -> Optional[QWidget]:
        """
        Get the parent instrument widget for accessing MidiFileEditor.

        :return: Optional[QWidget] parent instrument or None
        """
        parent_instrument = getattr(self, "parent", None)
        # Walk up the parent chain to find JDXiInstrument if needed
        while parent_instrument and not hasattr(
            parent_instrument, "get_existing_editor"
        ):
            next_parent = getattr(parent_instrument, "parent", None)
            if not next_parent:
                break
            parent_instrument = next_parent
        return (
            parent_instrument
            if hasattr(parent_instrument, "get_existing_editor")
            else None
        )

    def on_bank_changed(self, _: int) -> None:
        """Handle bank selection change - no longer needed, handled by SearchableFilterableComboBox."""
        pass

    def on_program_number_changed(self, index: int) -> None:
        """Handle program number selection change.
        :param index: int
        """
        # self.load_program()

    def load_program(self):
        """Load the selected program based on bank and number.
        Delegates to ProgramGroupWidget's load_program method.
        """
        if self.program_group_widget:
            self.program_group_widget.load_program()

    def update_current_synths(self, program_details: JDXiProgram) -> None:
        """Update the current synth labels in the mixer widget.
        :param program_details: JDXiProgram
        :return: None
        """
        if not self.mixer_widget:
            log.warning(
                "Mixer widget not available, cannot update synth labels",
                scope=self.__class__.__name__,
            )
            return

        try:
            if self.mixer_widget.digital_synth_1_current_label:
                self.mixer_widget.digital_synth_1_current_label.setText(
                    program_details.digital_1
                )
            if self.mixer_widget.digital_synth_2_current_label:
                self.mixer_widget.digital_synth_2_current_label.setText(
                    program_details.digital_2
                )
            if self.mixer_widget.drum_kit_current_label:
                self.mixer_widget.drum_kit_current_label.setText(program_details.drums)
            if self.mixer_widget.analog_synth_current_label:
                self.mixer_widget.analog_synth_current_label.setText(
                    program_details.analog
                )
        except (AttributeError, KeyError) as e:
            log.message(
                f"Error updating synth labels: {e}", scope=self.__class__.__name__
            )
            log.message(
                f"Program details: {program_details}", scope=self.__class__.__name__
            )
            # Set fallback values if labels exist
            if self.mixer_widget.digital_synth_1_current_label:
                self.mixer_widget.digital_synth_1_current_label.setText("Unknown")
            if self.mixer_widget.digital_synth_2_current_label:
                self.mixer_widget.digital_synth_2_current_label.setText("Unknown")
            if self.mixer_widget.drum_kit_current_label:
                self.mixer_widget.drum_kit_current_label.setText("Unknown")
            if self.mixer_widget.analog_synth_current_label:
                self.mixer_widget.analog_synth_current_label.setText("Unknown")

    def load_preset(self, program_number: int) -> None:
        """
        load_preset

        :param program_number: int
        :return: None
        Load preset data and update UI
        """
        if not self.preset_helper:
            return
        self.preset_helper.load_preset(program_number)
        self.data_request()

    def _update_program_list(self) -> None:
        """Update the program list with available presets."""
        self.populate_programs()

    def on_genre_changed(self, _: int) -> None:
        """
        Handle genre selection change - no longer needed, handled by SearchableFilterableComboBox.
        """
        pass

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """
        Dispatch SysEx data to the appropriate area for processing.

        :param json_sysex_data:
        :return: None
        """
        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        # current_synth = get_area([self.address.msb, self.address.umb])
        temporary_area = sysex_data.get(SysExSection.TEMPORARY_AREA)
        synth_tone = sysex_data.get(SysExSection.SYNTH_TONE)

        log.header_message(
            scope=self.__class__.__name__,
            message=f"Updating UI components from SysEx data for {temporary_area} {synth_tone}",
        )

        sysex_data = filter_sysex_keys(sysex_data)

        successes, failures = [], []

        if temporary_area == JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT.name:
            partial_map = DRUM_PARTIAL_MAP
        else:
            partial_map = SYNTH_PARTIAL_MAP

        # Define a mapping between temporary_area and their corresponding handlers
        # Get sliders from mixer_widget if available
        master_slider = (
            self.mixer_widget.master_level_slider if self.mixer_widget else None
        )
        analog_slider = (
            self.mixer_widget.analog_level_slider if self.mixer_widget else None
        )
        drums_slider = (
            self.mixer_widget.drums_level_slider if self.mixer_widget else None
        )
        digital1_slider = (
            self.mixer_widget.digital1_level_slider if self.mixer_widget else None
        )
        digital2_slider = (
            self.mixer_widget.digital2_level_slider if self.mixer_widget else None
        )

        temporary_area_handlers = {
            JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM.name: {
                "PROGRAM_LEVEL": (
                    ProgramCommonParam.PROGRAM_LEVEL,
                    master_slider,
                )
            },
            JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH.name: {
                "AMP_LEVEL": (AnalogParam.get_by_name, analog_slider)
            },
            JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT.name: {
                "KIT_LEVEL": (DrumCommonParam.KIT_LEVEL, drums_slider)
            },
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name: {
                SysExSection.TONE_LEVEL: (
                    DigitalCommonParam.get_by_name,
                    digital1_slider,
                )
            },
            JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name: {
                SysExSection.TONE_LEVEL: (
                    DigitalCommonParam.get_by_name,
                    digital2_slider,
                )
            },
        }

        partial_tone_names = [
            JDXiSysExOffsetSuperNATURALLMB.PARTIAL_1.name,
            JDXiSysExOffsetSuperNATURALLMB.PARTIAL_2.name,
            JDXiSysExOffsetSuperNATURALLMB.PARTIAL_3.name,
        ]

        # Get the partial number
        partial_number = get_partial_number(synth_tone, partial_map=partial_map)

        # Handle the temporary_area cases
        if temporary_area in temporary_area_handlers:
            handler = temporary_area_handlers[temporary_area]
            for param_name, param_value in sysex_data.items():
                if param_name in handler:
                    param_info = handler[param_name]
                    param = (
                        param_info[0](param_name)
                        if callable(param_info[0])
                        else param_info[0]
                    )
                    self._update_slider(
                        param, param_value, successes, failures, param_info[1]
                    )

        # Partial tone data (PARTIAL_1/2/3) is updated by SynthEditor, not here.
        # This widget's self.controls only has mixer sliders (PROGRAM_LEVEL, TONE_LEVEL,
        # KIT_LEVEL, AMP_LEVEL). Do not call _update_common_controls for partial tones,
        # or every partial param (OSC_*, FILTER_*, etc.) would be reported as failure.
        if synth_tone in partial_tone_names:
            pass  # SynthEditor handles partial updates via editor._update_controls()
        elif synth_tone == JDXiSysExOffsetSuperNATURALLMB.COMMON.name:
            self._update_common_controls(
                partial_number, sysex_data, successes, failures
            )

        log.debug_info(successes, failures, scope=self.__class__.__name__)

    def _update_common_controls(
        self,
        partial_number: int,
        sysex_data: Dict,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Update the UI components for tone common and modify parameters.

        :param partial_number: int partial number
        :param sysex_data: Dictionary containing SysEx data
        :param successes: List of successful parameters
        :param failures: List of failed parameters
        :return: None
        """
        log.message(
            f"Updating controls for partial {partial_number}",
            scope=self.__class__.__name__,
        )
        log.parameter("self.controls", self.controls, scope=self.__class__.__name__)
        for control in self.controls:
            log.parameter(
                "control", control, silent=False, scope=self.__class__.__name__
            )
        sysex_data.pop(SysExSection.SYNTH_TONE, None)
        for param_name, param_value in sysex_data.items():
            log.parameter(
                f"{param_name} {param_value}",
                param_value,
                silent=True,
                scope=self.__class__.__name__,
            )
            param = DigitalCommonParam.get_by_name(param_name)
            if not param:
                log.parameter(
                    f"param not found: {param_name} ",
                    param_value,
                    silent=True,
                    scope=self.__class__.__name__,
                )
                failures.append(param_name)
                continue
            log.parameter(
                f"found {param_name}",
                param_name,
                silent=True,
                scope=self.__class__.__name__,
            )
            try:
                if param.name in [
                    PartialSwitchState.PARTIAL1_SWITCH,
                    PartialSwitchState.PARTIAL2_SWITCH,
                    PartialSwitchState.PARTIAL3_SWITCH,
                ]:
                    pass
                    """self._update_partial_selection_switch(
                        param, param_value, successes, failures
                    )"""
                if param.name in [
                    PartialSelectState.PARTIAL1_SELECT,
                    PartialSelectState.PARTIAL2_SELECT,
                    PartialSelectState.PARTIAL3_SELECT,
                ]:
                    pass
                    """self._update_partial_selected_state(
                        param, param_value, successes, failures
                    )"""
                elif "SWITCH" in param_name:
                    self._update_switch(param, param_value, successes, failures)
                else:
                    self._update_slider(param, param_value, successes, failures)
            except Exception as ex:
                log.error(f"Error {ex} occurred")

    def _update_slider(
        self,
        param: AddressParameter,
        midi_value: int,
        successes: list = None,
        failures: list = None,
        slider: QWidget = None,
    ) -> None:
        """
        Update slider based on parameter and value.

        :param param: AddressParameter
        :param midi_value: int value
        :param successes: list
        :param failures: list
        :return: None
        """
        if slider is None:
            slider = self.controls.get(param)
        if slider:
            slider.blockSignals(True)
            slider.setValue(midi_value)
            slider.blockSignals(False)
            successes.append(param.name)
        else:
            failures.append(param.name)
