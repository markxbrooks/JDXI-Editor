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

from typing import Optional, Dict

from PySide6.QtWidgets import (
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout,
    QGroupBox, QFormLayout, QGridLayout, QScrollArea, QLineEdit, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QStyledItemDelegate, QFileDialog,
    QStyleOptionButton, QStyle,
)
from PySide6.QtCore import Signal, Qt, QRect, QSize, QTimer
from PySide6.QtGui import QPainter
import qtawesome as qta

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.jdxi.program.program import JDXiProgram
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB, AddressOffsetSuperNATURALLMB, \
    AddressStartMSB
from jdxi_editor.midi.data.address.program import ProgramCommonAddress
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_MAP
from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.data.parameter.digital import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.program.common import AddressParameterProgramCommon
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.programs import JDXiProgramList
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.midi.sysex.request.data import SYNTH_PARTIAL_MAP
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.editors.digital.utils import filter_sysex_keys, get_partial_number
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.ui.editors.helpers.program import (
    get_program_by_id,
    calculate_midi_values,
)
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.windows.patch.name_editor import PatchNameEditor


class MidiFileDelegate(QStyledItemDelegate):
    """Delegate for MIDI file selection with file dialog."""
    
    # Class-level flag to ensure only one dialog is open at a time
    _dialog_open = False
    
    def __init__(self, table_widget=None, parent=None):
        super().__init__(parent)
        self.table_widget = table_widget
    
    def paint(self, painter, option, index):
        """Paint the cell with a button-like appearance."""
        # Get the file path
        if self.table_widget:
            item = self.table_widget.item(index.row(), index.column())
            file_path = item.text() if item else None
        else:
            file_path = index.data(Qt.ItemDataRole.EditRole)
        
        if file_path:
            import os
            text = os.path.basename(file_path)
        else:
            text = "Select MIDI File..."
        
        # Draw button-like appearance
        button = QStyleOptionButton()
        button.rect = option.rect
        button.text = text
        button.state = QStyle.StateFlag.State_Enabled
        if option.state & QStyle.StateFlag.State_Selected:
            button.state |= QStyle.StateFlag.State_HasFocus
        
        if self.table_widget:
            self.table_widget.style().drawControl(QStyle.ControlElement.CE_PushButton, button, painter)
        else:
            QWidget().style().drawControl(QStyle.ControlElement.CE_PushButton, button, painter)
    
    def editorEvent(self, event, model, option, index):
        """Handle mouse clicks to open file dialog."""
        if event.type() == event.Type.MouseButtonPress:
            if option.rect.contains(event.pos()):
                # Check if dialog is already open (singleton)
                if MidiFileDelegate._dialog_open:
                    return True  # Ignore click if dialog is already open
                
                # Open file dialog
                if self.table_widget:
                    try:
                        MidiFileDelegate._dialog_open = True
                        file_path, _ = QFileDialog.getOpenFileName(
                            self.table_widget,
                            "Select MIDI File",
                            "",
                            "MIDI Files (*.mid *.midi);;All Files (*)"
                        )
                        if file_path:
                            # Update the table item directly
                            item = self.table_widget.item(index.row(), index.column())
                            if item:
                                item.setText(file_path)
                                # Trigger itemChanged signal to save to database
                                self.table_widget.itemChanged.emit(item)
                    finally:
                        MidiFileDelegate._dialog_open = False
                return True
        return super().editorEvent(event, model, option, index)
    
    def sizeHint(self, option, index):
        """Return appropriate size for the button."""
        return QSize(150, 30)


class PlayButtonDelegate(QStyledItemDelegate):
    """Delegate for Play button in table."""
    
    def __init__(self, parent=None, play_callback=None):
        super().__init__(parent)
        self.play_callback = play_callback
    
    def paint(self, painter, option, index):
        """Draw a play button."""
        if option.state & QStyle.StateFlag.State_Enabled:
            button = QStyleOptionButton()
            button.rect = option.rect
            button.text = "▶ Play"
            button.state = QStyle.StateFlag.State_Enabled
            if option.state & QStyle.StateFlag.State_Selected:
                button.state |= QStyle.StateFlag.State_HasFocus
            QWidget().style().drawControl(QStyle.ControlElement.CE_PushButton, button, painter)
    
    def editorEvent(self, event, model, option, index):
        """Handle button click."""
        if event.type() == event.Type.MouseButtonPress:
            if option.rect.contains(event.pos()):
                if self.play_callback:
                    self.play_callback(index)
                return True
        return super().editorEvent(event, model, option, index)
    
    def sizeHint(self, option, index):
        """Return button size."""
        return QSize(80, 30)


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
        self.file_label = None
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
        self.midi_channel = 0 # Defaults to DIGITAL 1
        self.genre_label = None
        self.program_number_combo_box = None
        self.program_name = ""
        self.bank_combo_box = None
        self.load_button = None
        self.save_button = None
        self.image_label = None
        self.title_label = None
        self.bank_label = None
        self.program_label = None
        self.genre_combo_box = None
        self.preset_type = None
        self.programs = {}
        self.programs = {}  # Maps program names to numbers
        # Playlist playback tracking
        self._current_playlist_row = None
        self._playlist_midi_editor = None
        self.setup_ui()
        self.midi_helper.update_program_name.connect(self.set_current_program_name)
        self.controls: Dict[AddressParameter, QWidget] = {}
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)

    def setup_ui(self):
        """set up ui elements"""
        self.setWindowTitle("Program Editor")
        self.setMinimumSize(400, 400)
        main_vlayout = QVBoxLayout()
        
        # Create main tab widget for top-level tabs
        self.main_tab_widget = QTabWidget()
        main_vlayout.addWidget(self.main_tab_widget)
        
        ### Scrolled area for Programs/Presets tab
        # Scrollable area setup
        scrolled_area = QScrollArea()
        scrolled_area.setWidgetResizable(True)

        scrolled_area_container = QWidget()
        scrolled_area_container_layout = QVBoxLayout(scrolled_area_container)

        scrolled_area.setWidget(scrolled_area_container)

        self.title_vlayout = QVBoxLayout()
        self.title_hlayout = QHBoxLayout()
        self.title_vlayout.addStretch()
        self.title_vlayout.addLayout(self.title_hlayout)
        self.title_hlayout.addStretch()

        self.title_left_vlayout = QVBoxLayout()
        self.title_hlayout.addLayout(self.title_left_vlayout)

        self.title_right_vlayout = QVBoxLayout()
        self.title_hlayout.addLayout(self.title_right_vlayout)

        scrolled_area_container_layout.addLayout(self.title_vlayout)
        
        # Add Programs/Presets tab to main tab widget
        self.main_tab_widget.addTab(scrolled_area, "Programs & Presets")
        
        # Add User Programs tab to main tab widget
        try:
            log.message("🔨 Creating User Programs tab for main window...")
            user_programs_widget = self._create_user_programs_tab()
            self.main_tab_widget.addTab(user_programs_widget, "User Programs")
            log.message(f"✅ Added 'User Programs' tab to main window (total tabs: {self.main_tab_widget.count()})")
            # Log all tab names for debugging
            for i in range(self.main_tab_widget.count()):
                log.message(f"  Main Tab {i}: '{self.main_tab_widget.tabText(i)}'")
        except Exception as e:
            log.error(f"❌ Error creating User Programs tab: {e}")
            import traceback
            log.error(traceback.format_exc())
            # Create a placeholder widget so the tab still appears
            placeholder_widget = QWidget()
            placeholder_layout = QVBoxLayout(placeholder_widget)
            placeholder_label = QLabel(f"Error loading user programs: {e}")
            placeholder_layout.addWidget(placeholder_label)
            self.main_tab_widget.addTab(placeholder_widget, "User Programs")
            log.message(f"✅ Added 'User Programs' tab (placeholder) (total tabs: {self.main_tab_widget.count()})")
        
        # Add Playlist tab to main tab widget
        try:
            log.message("🔨 Creating Playlist tab for main window...")
            playlist_widget = self._create_playlist_tab()
            self.main_tab_widget.addTab(playlist_widget, "Playlist")
            log.message(f"✅ Added 'Playlist' tab to main window (total tabs: {self.main_tab_widget.count()})")
        except Exception as e:
            log.error(f"❌ Error creating Playlist tab: {e}")
            import traceback
            log.error(traceback.format_exc())
            # Create a placeholder widget so the tab still appears
            placeholder_widget = QWidget()
            placeholder_layout = QVBoxLayout(placeholder_widget)
            placeholder_label = QLabel(f"Error loading playlists: {e}")
            placeholder_layout.addWidget(placeholder_label)
            self.main_tab_widget.addTab(placeholder_widget, "Playlist")
            log.message(f"✅ Added 'Playlist' tab (placeholder) (total tabs: {self.main_tab_widget.count()})")
        
        # Add Playlist Editor tab to main tab widget
        try:
            log.message("🔨 Creating Playlist Editor tab for main window...")
            playlist_editor_widget = self._create_playlist_editor_tab()
            self.main_tab_widget.addTab(playlist_editor_widget, "Playlist Editor")
            log.message(f"✅ Added 'Playlist Editor' tab to main window (total tabs: {self.main_tab_widget.count()})")
        except Exception as e:
            log.error(f"❌ Error creating Playlist Editor tab: {e}")
            import traceback
            log.error(traceback.format_exc())
            # Create a placeholder widget so the tab still appears
            placeholder_widget = QWidget()
            placeholder_layout = QVBoxLayout(placeholder_widget)
            placeholder_label = QLabel(f"Error loading playlist editor: {e}")
            placeholder_layout.addWidget(placeholder_label)
            self.main_tab_widget.addTab(placeholder_widget, "Playlist Editor")
            log.message(f"✅ Added 'Playlist Editor' tab (placeholder) (total tabs: {self.main_tab_widget.count()})")
        
        self.setLayout(main_vlayout)
        self.setStyleSheet(JDXiStyle.EDITOR)

        program_preset_hlayout = QHBoxLayout()
        program_preset_hlayout.addStretch()
        # scrolled_area_container_layout.addLayout(program_preset_hlayout)

        program_group = self._create_program_selection_box()
        program_preset_hlayout.addStretch()
        program_preset_hlayout.addWidget(program_group)

        program_preset_hlayout.addStretch()

        preset_group = self._create_preset_selection_widget()
        self.program_preset_tab_widget.addTab(preset_group, "Presets")
        program_preset_hlayout.addStretch()

        self.title_left_vlayout.addLayout(program_preset_hlayout)
        self.title_left_vlayout.addStretch()

        transport_group = self._create_transport_group()
        # scrolled_area_container_layout.addWidget(transport_group)
        self.populate_programs()

        mixer_section = self._create_mixer_section()
        self.right_hlayout = QHBoxLayout()
        self.right_hlayout.addWidget(mixer_section)
        self.title_right_vlayout.addLayout(self.right_hlayout)
        self.title_hlayout.addStretch()
        self.title_vlayout.addStretch()
        preset_type = "Digital Synth 1"
        self.set_channel_and_preset_lists(preset_type)
        self._populate_presets()
        self.midi_helper.update_tone_name.connect(
             lambda tone_name, synth_type: self.update_tone_name_for_synth(tone_name, synth_type)
        )
        self.update_instrument_image()

    def _create_preset_selection_widget(self) -> QWidget:
        """
        create_preset_selection_widget

        :return: QWidget
        """
        # Program controls group
        preset_widget = QWidget()
        preset_vlayout = QVBoxLayout()
        preset_widget.setLayout(preset_vlayout)
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )  # Center align the image
        preset_vlayout.addWidget(self.image_label)
        # Synth type selection combo box
        self.digital_preset_type_combo = QComboBox()
        self.digital_preset_type_combo.addItems(
            ["Digital Synth 1", "Digital Synth 2", "Drums", "Analog Synth"]
        )
        self.digital_preset_type_combo.currentIndexChanged.connect(
            self.on_preset_type_changed
        )
        preset_vlayout.addWidget(self.digital_preset_type_combo)
        # Search Box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setStyleSheet(JDXiStyle.QLINEEDIT)
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._populate_presets)
        search_row.addWidget(self.search_box)
        preset_vlayout.addLayout(search_row)
        self.digital_preset_label = QLabel("Preset")
        preset_vlayout.addWidget(self.digital_preset_label)
        # Program number selection combo box
        self.preset_combo_box = QComboBox()
        self.preset_combo_box.addItems([f"{i:02}" for i in range(1, 65)])
        # self.preset_combo_box.currentIndexChanged.connect(self.on_preset_number_changed)
        preset_vlayout.addWidget(self.preset_combo_box)
        self.genre_label = QLabel("Category")
        preset_vlayout.addWidget(self.genre_label)
        # Category selection combo box
        self.category_combo_box = QComboBox()
        self.category_combo_box.addItem("No Category Selected")
        categories = set(preset["category"] for preset in DIGITAL_PRESET_LIST)
        self.category_combo_box.addItems(sorted(categories))
        self.category_combo_box.currentIndexChanged.connect(self.on_category_changed)
        preset_vlayout.addWidget(self.category_combo_box)
        # Load button
        self.load_button = QPushButton(
            qta.icon("ph.folder-notch-open-fill", color=JDXiStyle.FOREGROUND),
            "Load Preset",
        )
        self.load_button.clicked.connect(self.load_preset_by_program_change)
        preset_vlayout.addWidget(self.load_button)
        return preset_widget

    def load_preset_by_program_change(self, preset_index: int) -> None:
        """
        Load a preset by program change.

        :param preset_index: int
        """
        preset_name = self.preset_combo_box.currentText()
        log.message("=======load_preset_by_program_change=======")
        log.parameter("combo box preset_name", preset_name)
        program_number = preset_name[:3]
        log.parameter("combo box program_number", program_number)

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number, self.preset_list)
        lsb = get_preset_parameter_value("lsb", program_number, self.preset_list)
        pc = get_preset_parameter_value("pc", program_number, self.preset_list)

        if None in [msb, lsb, pc]:
            log.message(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return

        log.message("retrieved msb, lsb, pc :")
        log.parameter("combo box msb", msb)
        log.parameter("combo box lsb", lsb)
        log.parameter("combo box pc", pc)
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1,  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def on_category_changed(self, _: int) -> None:
        """Handle category selection change."""
        self._populate_presets()

    def _create_transport_group(self) -> QGroupBox:
        """
        _create_transport_group

        :return: QGroupBox
        Transport controls area
        """
        transport_group = QGroupBox("Transport")
        transport_layout = QHBoxLayout()
        self.start_button = QPushButton(
            qta.icon("ri.play-line", color=JDXiStyle.FOREGROUND), "Play"
        )
        self.stop_button = QPushButton(
            qta.icon("ri.stop-line", color=JDXiStyle.FOREGROUND), "Stop"
        )
        self.start_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)
        transport_layout.addWidget(self.start_button)
        transport_layout.addWidget(self.stop_button)
        transport_group.setLayout(transport_layout)
        return transport_group

    def _create_program_selection_box(self) -> QGroupBox:
        """
        create_program_selection_box

        :return: QGroupBox
        """
        # Program controls group
        program_group = QGroupBox("Load a program")
        program_layout = QVBoxLayout()
        program_vlayout = QVBoxLayout()

        program_group.setLayout(program_layout)

        self.file_label = DigitalTitle("No file loaded")
        program_layout.addWidget(self.file_label)

        # program and presets tab widget (nested inside group box)
        self.program_preset_tab_widget = QTabWidget()
        self.program_preset_tab_widget.setMinimumHeight(300)  # Ensure tab widget is visible
        program_widget = QWidget()
        program_widget.setLayout(program_vlayout)
        program_layout.addWidget(self.program_preset_tab_widget)
        self.program_preset_tab_widget.addTab(program_widget, "Programs")
        log.message(f"📑 Created nested tab widget, added 'Programs' tab (total tabs: {self.program_preset_tab_widget.count()})")
        
        # update_program_name
        self.edit_program_name_button = QPushButton("Edit program name")
        self.edit_program_name_button.clicked.connect(self.edit_program_name)
        program_vlayout.addWidget(self.edit_program_name_button)

        # Search Box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search programs...")
        self.search_box.setStyleSheet(JDXiStyle.QLINEEDIT)
        self.search_box.textChanged.connect(self.populate_programs)  # @@
        search_row.addWidget(self.search_box)
        program_vlayout.addLayout(search_row)

        # Program number selection combo box
        # Note: This combo box is populated by populate_programs() which uses SQLite database
        # as the single source of truth. No need to add generic items here.
        self.program_number_combo_box = QComboBox()
        self.program_number_combo_box.currentIndexChanged.connect(
            self.on_program_number_changed
        )
        program_vlayout.addWidget(self.program_number_combo_box)
        self.genre_label = QLabel("Genre")
        program_vlayout.addWidget(self.genre_label)
        # Genre selection combo box
        self.genre_combo_box = QComboBox()
        self.genre_combo_box.addItem("No Genre Selected")
        genres = set(program.genre for program in JDXiProgramList.list_rom_and_user_programs())
        self.genre_combo_box.addItems(sorted(genres))
        self.genre_combo_box.currentIndexChanged.connect(self.on_genre_changed)
        program_vlayout.addWidget(self.genre_combo_box)
        self.bank_label = QLabel("Bank")
        program_vlayout.addWidget(self.bank_label)
        # Bank selection combo box
        self.bank_combo_box = QComboBox()
        self.bank_combo_box.addItem("No Bank Selected")
        self.bank_combo_box.addItems(["A", "B", "C", "D", "E", "F", "G", "H"])
        self.bank_combo_box.currentIndexChanged.connect(self.on_bank_changed)
        program_vlayout.addWidget(self.bank_combo_box)
        # Load button
        self.load_button = QPushButton(
            qta.icon("ph.folder-notch-open-fill", color=JDXiStyle.FOREGROUND),
            "Load Program",
        )
        self.load_button.clicked.connect(self.load_program)
        program_vlayout.addWidget(self.load_button)
        return program_group

    def edit_program_name(self):
        """
        edit_tone_name

        :return: None
        """
        program_name_dialog = PatchNameEditor(current_name=self.program_name)
        if program_name_dialog.exec():  # If the user clicks Save
            sysex_string = program_name_dialog.get_sysex_string()
            log.message(f"SysEx string: {sysex_string}")
            self.send_tone_name(AddressParameterProgramCommon, sysex_string)
            self.data_request()

    def on_preset_type_changed(self, index: int) -> None:
        """
        on_preset_type_changed
        
        :param index: int
        Handle preset type selection change
        """
        preset_type = self.digital_preset_type_combo.currentText()
        log.message(f"preset_type: {preset_type}")
        self.set_channel_and_preset_lists(preset_type)
        self._populate_presets()
        self.update_category_combo_box_categories()

    def set_channel_and_preset_lists(self, preset_type: str) -> None:
        """
        set_channel_and_preset_lists

        :param preset_type:
        :return: None
        """
        if preset_type == "Digital Synth 1":
            self.midi_channel = MidiChannel.DIGITAL_SYNTH_1
            self.preset_list = JDXiPresetToneList.DIGITAL_PROGRAM_CHANGE
        elif preset_type == "Digital Synth 2":
            self.midi_channel = MidiChannel.DIGITAL_SYNTH_2
            self.preset_list = JDXiPresetToneList.DIGITAL_PROGRAM_CHANGE
        elif preset_type == "Drums":
            self.midi_channel = MidiChannel.DRUM_KIT
            self.preset_list = JDXiPresetToneList.DRUM_PROGRAM_CHANGE
        elif preset_type == "Analog Synth":
            self.midi_channel = MidiChannel.ANALOG_SYNTH
            self.preset_list = JDXiPresetToneList.ANALOG_PROGRAM_CHANGE

    def update_category_combo_box_categories(self) -> None:
        """
        update_category_combo_box_categories

        :return: None
        Update the category combo box.
        """
        # Update the category combo box
        categories = set(preset["category"] for preset in self.preset_list)
        self.category_combo_box.blockSignals(True)  # Block signals during update

        # Clear and update items
        self.category_combo_box.clear()
        self.category_combo_box.addItem(
            "No Category Selected"
        )  # Add the default option
        self.category_combo_box.addItems(
            sorted(categories)
        )  # Add the sorted categories

        # Set the default selected index
        self.category_combo_box.setCurrentIndex(
            0
        )  # Select "No Category Selected" as default

        self.category_combo_box.blockSignals(False)  # Unblock signals after update

    def _populate_programs(self, search_text: str = "") -> None:
        """
        Populate the program list with available presets.

        :param search_text: str
        :return: None
        """
        if not self.preset_helper:
            return
        self.programs = {}  # reset dictionary each time
        selected_genre = self.category_combo_box.currentText()
        log.message(f"Selected Genre: {selected_genre}")

        self.program_number_combo_box.clear()

        filtered_list = [  # Filter programs based on bank and genre
            program
            for program in self.program_list
            if (selected_genre in ["No Category Selected", program["category"]])
        ]
        filtered_programs = []
        for i, program in enumerate(filtered_list):
            if search_text.lower() in program["name"].lower():
                filtered_programs.append(program)

        for program in filtered_programs:  # Add programs to the combo box
            program_name = program["name"]
            program_id = program["id"]
            index = len(self.programs)  # Use the current number of programs
            self.program_number_combo_box.addItem(f"{program_id} - {program_name}", index)
            self.programs[program_name] = index
        self.preset_combo_box.setCurrentIndex(
            0
        )  # Select "No Category Selected" as default

    def _populate_presets(self, search_text: str = "") -> None:
        """
        Populate the program list with available presets.

        :param search_text: str
        :return: None
        """
        if not self.preset_helper:
            return
        self.programs = {}  # reset dictionary each time
        preset_type = self.digital_preset_type_combo.currentText()
        if preset_type in ["Digital Synth 1", "Digital Synth 2"]:
            self.preset_list = DIGITAL_PRESET_LIST
        elif preset_type == "Drums":
            self.preset_list = DRUM_KIT_LIST
        elif preset_type == "Analog Synth":
            self.preset_list = ANALOG_PRESET_LIST
        else:
            self.preset_list = DIGITAL_PRESET_LIST  # Default to digital synth 1
        # self.update_category_combo_box_categories()

        selected_category = self.category_combo_box.currentText()
        log.message(f"Selected Category: {selected_category}")

        self.preset_combo_box.clear()

        filtered_list = [  # Filter programs based on bank and genre
            preset
            for preset in self.preset_list
            if (selected_category in ["No Category Selected", preset["category"]])
        ]
        filtered_presets = []
        for i, preset in enumerate(filtered_list):
            if search_text.lower() in preset["name"].lower():
                filtered_presets.append(preset)

        for preset in filtered_presets:  # Add programs to the combo box
            preset_name = preset["name"]
            preset_id = preset["id"]
            index = len(self.programs)  # Use the current number of programs
            self.preset_combo_box.addItem(f"{preset_id} - {preset_name}", index)
            self.programs[preset_name] = index
        self.preset_combo_box.setCurrentIndex(
            0
        )  # Select "No Category Selected" as default

    def _init_synth_data(self,
                         synth_type: JDXiSynth = JDXiSynth.DIGITAL_SYNTH_1,
                         partial_number: Optional[int] = 0) -> None:
        """

        :param synth_type: JDXiSynth
        :param partial_number: int
        :return: None
        Initialize synth-specific data
        """
        from jdxi_editor.jdxi.synth.factory import create_synth_data
        self.synth_data = create_synth_data(synth_type,
                                            partial_number=partial_number)

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

    def _create_mixer_section(self) -> QWidget:
        """
        _create_mixer_section

        :return: QWidget
        Create general vocal effect controls section with scrolling
        """

        mixer_section = QWidget()
        layout = QVBoxLayout(mixer_section)

        self.master_level_icon = QLabel()
        self.master_level_icon.setPixmap(
            qta.icon("mdi6.keyboard-settings-outline", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.master_level_title = QLabel("Master Level")
        self.master_level_title.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.master_level_current_label = QLabel("Current Program")
        self.master_level_current_label.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.digital_synth_1_icon = QLabel()
        self.digital_synth_1_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.digital_synth_1_title = QLabel("Digital Synth 1")
        self.digital_synth_1_title.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.digital_synth_1_current_label = QLabel("Current Synth:")
        self.digital_synth_1_current_label.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.digital_synth_2_icon = QLabel()
        self.digital_synth_2_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )

        self.digital_synth_2_title = QLabel("Digital Synth 2")
        self.digital_synth_2_title.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.digital_synth_2_current_label = QLabel("Current Synth:")
        self.digital_synth_2_current_label.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.drum_kit_icon = QLabel()
        self.drum_kit_icon.setPixmap(
            qta.icon("fa5s.drum", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.drum_kit_title = QLabel("Drums")
        self.drum_kit_title.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.drum_kit_current_label = QLabel("Current Synth:")
        self.drum_kit_current_label.setStyleSheet(JDXiStyle.MIXER_LABEL)
        self.analog_synth_icon = QLabel()
        self.analog_synth_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.analog_synth_title = QLabel("Analog Synth")
        self.analog_synth_title.setStyleSheet(JDXiStyle.MIXER_LABEL_ANALOG)
        self.analog_synth_current_label = QLabel("Current Synth:")
        self.analog_synth_current_label.setStyleSheet(JDXiStyle.MIXER_LABEL_ANALOG)

        # Mixer controls group
        mixer_group = QGroupBox("Mixer Level Settings")
        self.title_right_vlayout.addWidget(mixer_group)
        # self.title_right_vlayout.addStretch()
        mixer_layout = QGridLayout()
        mixer_group.setLayout(mixer_layout)

        # Sliders
        program_common_address = ProgramCommonAddress()
        self.address = program_common_address
        self.master_level_slider = self._create_parameter_slider(
            param=AddressParameterProgramCommon.PROGRAM_LEVEL,
            label="Master",
            vertical=True,
            address=program_common_address
        )
        self.controls[AddressParameterProgramCommon.PROGRAM_LEVEL] = self.master_level_slider

        self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_1)
        self.digital1_level_slider = self._create_parameter_slider(
            AddressParameterDigitalCommon.TONE_LEVEL, "Digital 1", vertical=True
        )
        self.controls[AddressParameterDigitalCommon.TONE_LEVEL] = self.digital1_level_slider
        self._init_synth_data(synth_type=JDXiSynth.DIGITAL_SYNTH_2)
        self.digital2_level_slider = self._create_parameter_slider(
            AddressParameterDigitalCommon.TONE_LEVEL, "Digital 2", vertical=True
        )
        self.controls[AddressParameterDigitalCommon.TONE_LEVEL] = self.digital2_level_slider
        self._init_synth_data(synth_type=JDXiSynth.DRUM_KIT)
        self.drums_level_slider = self._create_parameter_slider(
            AddressParameterDrumCommon.KIT_LEVEL, "Drums", vertical=True
        )
        self.controls[AddressParameterDrumCommon.KIT_LEVEL] = self.drums_level_slider
        self._init_synth_data(synth_type=JDXiSynth.ANALOG_SYNTH)
        self.analog_level_slider = self._create_parameter_slider(
            AddressParameterAnalog.AMP_LEVEL, "Analog", vertical=True
        )
        self.controls[AddressParameterAnalog.AMP_LEVEL] = self.analog_level_slider
        self.address = program_common_address
        # Mixer layout population
        mixer_layout.setColumnStretch(0, 1)
        mixer_layout.addWidget(self.master_level_slider, 0, 1)
        mixer_layout.addWidget(self.digital1_level_slider, 0, 2)
        mixer_layout.addWidget(self.digital2_level_slider, 0, 3)
        mixer_layout.addWidget(self.drums_level_slider, 0, 4)
        mixer_layout.addWidget(self.analog_level_slider, 0, 5)
        mixer_layout.setColumnStretch(6, 1)

        mixer_layout.addWidget(self.master_level_current_label, 1, 1)
        mixer_layout.addWidget(self.digital_synth_1_current_label, 1, 2)
        mixer_layout.addWidget(self.digital_synth_2_current_label, 1, 3)
        mixer_layout.addWidget(self.drum_kit_current_label, 1, 4)
        mixer_layout.addWidget(self.analog_synth_current_label, 1, 5)

        mixer_layout.addWidget(self.master_level_icon, 2, 1)
        mixer_layout.addWidget(self.digital_synth_1_icon, 2, 2)
        mixer_layout.addWidget(self.digital_synth_2_icon, 2, 3)
        mixer_layout.addWidget(self.drum_kit_icon, 2, 4)
        mixer_layout.addWidget(self.analog_synth_icon, 2, 5)

        mixer_group.setStyleSheet(JDXiStyle.ADSR)
        self.analog_level_slider.setStyleSheet(JDXiStyle.ADSR_ANALOG)

        return mixer_section

    def update_tone_name_for_synth(self, tone_name: str, synth_type: str) -> None:
        """
        Update the tone name.

        :param tone_name: str
        :param synth_type: str
        """
        log.message(f"Update tone name triggered: tone_name {tone_name} {synth_type}")
        synth_label_map = {
            JDXiSynth.DIGITAL_SYNTH_1: self.digital_synth_1_current_label,
            JDXiSynth.DIGITAL_SYNTH_2: self.digital_synth_2_current_label,
            JDXiSynth.DRUM_KIT: self.drum_kit_current_label,
            JDXiSynth.ANALOG_SYNTH: self.analog_synth_current_label,
        }

        label = synth_label_map.get(synth_type)
        if label:
            try:
                label.setText(tone_name)
            except Exception as ex:
                log.message(f"Error {ex} setting text")
        else:
            log.warning(f"synth type: {synth_type} not found in mapping. Cannot update tone name.")

    def set_current_program_name(self, program_name: str, synth_type: str = None) -> None:
        """
        Set the current program name in the file label

        :param program_name: str
        :param synth_type: str (optional), discarded for now
        :return: None
        """
        self.program_name = program_name or "Untitled Program"
        if self.file_label:
            self.file_label.setText(program_name)
        else:
            log.message("File label not initialized.")
        if hasattr(self, "master_level_current_label"):
            self.master_level_current_label.setText(program_name)

    def start_playback(self):
        """Start playback of the MIDI file."""
        self.midi_helper.send_raw_message([MidiConstant.SONG_START])

    def stop_playback(self):
        """Stop playback of the MIDI file."""
        self.midi_helper.send_raw_message([MidiConstant.SONG_STOP])

    def populate_programs(self, search_text: str = ""):
        """Populate the program list with available presets.
        Uses SQLite database to ensure all user bank programs are loaded correctly.
        """
        if not self.preset_helper:
            return

        selected_bank = self.bank_combo_box.currentText()
        selected_genre = self.genre_combo_box.currentText()

        log.parameter("selected bank", selected_bank)
        log.parameter("selected genre", selected_genre)

        self.program_number_combo_box.clear()
        self.programs.clear()

        # If a specific user bank is selected, load ALL programs from that bank from SQLite
        user_banks = ["E", "F", "G", "H"]
        if selected_bank in user_banks:
            # Load all programs from the selected user bank directly from SQLite
            from jdxi_editor.midi.data.programs.database import get_database
            from jdxi_editor.jdxi.program.program import JDXiProgram
            from jdxi_editor.ui.editors.helpers.program import calculate_midi_values

            db = get_database()
            bank_programs = db.get_programs_by_bank(selected_bank)
            log.message(f"🔍 Bank {selected_bank}: Found {len(bank_programs)} programs in database")

            # Create a dictionary of existing programs by ID for quick lookup
            existing_programs = {program.id: program for program in bank_programs}

            # Ensure all 64 programs are shown (create placeholders for missing ones)
            for i in range(1, 65):
                program_id = f"{selected_bank}{i:02}"

                # Check if program exists in database
                if program_id in existing_programs:
                    program = existing_programs[program_id]
                    # Filter by genre and search text
                    if selected_genre not in ["No Genre Selected", program.genre]:
                        continue
                    if search_text and search_text.lower() not in program.name.lower():
                        continue

                    program_name = program.name
                else:
                    # Create placeholder program for missing entry
                    try:
                        msb, lsb, pc = calculate_midi_values(selected_bank, i)
                    except:
                        msb, lsb, pc = 85, (0 if selected_bank in ["E", "F"] else 1), i

                    program = JDXiProgram(
                        id=program_id,
                        name=f"User bank {selected_bank} program {i:02}",
                        genre=None,
                        pc=pc,
                        msb=msb,
                        lsb=lsb,
                        digital_1=None,
                        digital_2=None,
                        analog=None,
                        drums=None,
                    )
                    program_name = program.name

                    # Filter placeholder by search text
                    if search_text and search_text.lower() not in program_name.lower():
                        continue

                # Add program to combo box
                index = len(self.programs)
                self.program_number_combo_box.addItem(
                    f"{program_id} - {program_name}", index
                )
                self.programs[program_name] = index

            log.message(
                f"🔍 Bank {selected_bank}: Populated {self.program_number_combo_box.count()} programs (including placeholders)")
        else:
            # For ROM banks (A, B, C, D) or "No Bank Selected", use standard filtering
            filtered_list = [  # Filter programs based on bank and genre
                program
                for program in JDXiProgramList.list_rom_and_user_programs()
                if (selected_bank in ["No Bank Selected", program.id[0]])
                   and (selected_genre in ["No Genre Selected", program.genre])
            ]

            for program in filtered_list:  # Add programs to the combo box
                if search_text and search_text.lower() not in program.name.lower():
                    continue
                program_name = program.name
                program_id = program.id
                index = len(self.programs)  # Use the current number of programs
                self.program_number_combo_box.addItem(
                    f"{program_id} - {program_name}", index
                )
                self.programs[program_name] = index

            # If "No Bank Selected" and no genre filter, add user banks
            if (
                    selected_bank == "No Bank Selected"
                    and selected_genre == "No Genre Selected"
            ):
                self.add_user_banks(
                    filtered_list, selected_bank, search_text
                )  # Handle user banks if necessary

        self.program_number_combo_box.setCurrentIndex(
            0
        )  # Update the UI with the new program list

    def add_user_banks(self, filtered_list: list, bank: str, search_text: str = None) -> None:
        """Add user banks to the program list.
        Only adds generic entries for programs that don't exist in the database.
        Uses SQLite database for reliable lookups.
        :param search_text:
        :param filtered_list: list of programs already loaded from database
        :param bank: str
        """
        from jdxi_editor.ui.editors.helpers.program import get_program_by_id
        from jdxi_editor.midi.data.programs.database import get_database
        
        user_banks = ["E", "F", "G", "H"]
        # Create sets for quick lookup
        existing_program_ids_in_filtered = {program.id for program in filtered_list}
        # Also check what's already in the combo box to avoid duplicates
        existing_combo_items = {
            self.program_number_combo_box.itemText(i)[:3]  # Extract program ID (e.g., "E01")
            for i in range(self.program_number_combo_box.count())
        }
        
        # Get database instance for direct queries
        db = get_database()
        
        for user_bank in user_banks:
            if bank in ["No Bank Selected", user_bank]:
                for i in range(1, 65):
                    program_id = f"{user_bank}{i:02}"
                    
                    # Skip if already in combo box (avoid duplicates)
                    if program_id in existing_combo_items:
                        continue
                    
                    # Check if program exists in filtered_list (already added)
                    if program_id in existing_program_ids_in_filtered:
                        continue
                    
                    # Check database directly using SQLite
                    # Only add programs that exist in the database (single source of truth)
                    existing_program = db.get_program_by_id(program_id)
                    if not existing_program:
                        # If program doesn't exist in database, skip it (no placeholders)
                        continue
                    
                    # Program exists in database, add it with real name
                    program_name = existing_program.name
                    if search_text and search_text.lower() not in program_name.lower():
                        continue
                    index = len(self.programs)
                    self.program_number_combo_box.addItem(
                        f"{program_id} - {program_name}", index
                    )
                    self.programs[program_name] = index

    def _create_user_programs_tab(self) -> QWidget:
        """
        Create the User Programs tab with a sortable, searchable table.
        
        :return: QWidget containing the user programs table
        """
        log.message("🔨 _create_user_programs_tab() called")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        log.message("✅ Created widget and layout")
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.user_programs_search_box = QLineEdit()
        self.user_programs_search_box.setPlaceholderText("Search by ID, name, genre, or tone...")
        self.user_programs_search_box.textChanged.connect(
            lambda text: self._populate_user_programs_table(text)
        )
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.user_programs_search_box)
        layout.addLayout(search_layout)
        
        # Create table
        self.user_programs_table = QTableWidget()
        self.user_programs_table.setColumnCount(12)
        self.user_programs_table.setHorizontalHeaderLabels([
            "ID", "Name", "Genre", "Bank", "PC", "MSB", "LSB",
            "Digital 1", "Digital 2", "Analog", "Drums", "Play"
        ])
        
        # Apply custom styling
        self.user_programs_table.setStyleSheet(self._get_table_style())
        
        # Enable sorting
        self.user_programs_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.user_programs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Genre
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Bank
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # PC
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # MSB
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # LSB
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Digital 1
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Digital 2
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Analog
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents)  # Drums
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents)  # Play
        
        # Set up Play button delegate for column 11
        play_button_delegate = PlayButtonDelegate(
            self.user_programs_table,
            play_callback=self._play_user_program
        )
        self.user_programs_table.setItemDelegateForColumn(11, play_button_delegate)
        
        # Make Genre column editable (column 2)
        # Note: We'll handle editing by making items editable
        
        # Connect double-click to load program
        self.user_programs_table.itemDoubleClicked.connect(self._on_user_program_selected)
        
        # Connect single-click to load program (alternative)
        self.user_programs_table.itemSelectionChanged.connect(self._on_user_program_selection_changed)
        
        layout.addWidget(self.user_programs_table)
        log.message("✅ Added table to layout")
        
        # Add save button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_user_programs_button = QPushButton(
            qta.icon("ph.floppy-disk-fill", color=JDXiStyle.FOREGROUND),
            "Save Changes"
        )
        self.save_user_programs_button.clicked.connect(self._save_user_programs_changes)
        button_layout.addWidget(self.save_user_programs_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Populate table (with error handling)
        try:
            log.message("🔨 Calling _populate_user_programs_table()...")
            self._populate_user_programs_table()
            log.message("✅ Table populated successfully")
        except Exception as e:
            log.error(f"❌ Error populating user programs table: {e}")
            import traceback
            log.error(traceback.format_exc())
            # Table will be empty but tab will still be visible
        
        log.message(f"✅ Returning User Programs tab widget (size: {widget.size()})")
        return widget
    
    def _get_table_style(self) -> str:
        """
        Get custom styling for tables with rounded corners and charcoal embossed cells.
        
        :return: str CSS style string
        """
        return """
            QTableWidget {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
                gridline-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #3a3a3a;
                selection-color: #ffffff;
            }
            
            QTableWidget::item {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a,
                    stop:0.5 #252525,
                    stop:1 #1f1f1f);
                border: 1px solid #1a1a1a;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }
            
            QTableWidget::item:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a,
                    stop:0.5 #353535,
                    stop:1 #2f2f2f);
                border: 1px solid #4a4a4a;
            }
            
            QTableWidget::item:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #323232,
                    stop:0.5 #2d2d2d,
                    stop:1 #282828);
                border: 1px solid #3a3a3a;
            }
            
            QTableWidget::item:focus {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a,
                    stop:0.5 #353535,
                    stop:1 #2f2f2f);
                border: 1px solid #ff2200;
            }
            
            QHeaderView::section {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a,
                    stop:1 #1f1f1f);
                color: #ffffff;
                padding: 6px;
                border: 1px solid #1a1a1a;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QHeaderView::section:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #323232,
                    stop:1 #272727);
            }
            
            QTableCornerButton::section {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px 0 0 0;
            }
        """
    
    def _populate_user_programs_table(self, search_text: str = "") -> None:
        """
        Populate the user programs table from SQLite database.
        
        :param search_text: Optional search text to filter programs
        """
        if not hasattr(self, 'user_programs_table'):
            log.warning("User programs table not initialized")
            return
        
        try:
            from jdxi_editor.midi.data.programs.database import get_database
            
            # Get all user programs from database
            db = get_database()
            all_programs = db.get_all_programs()
        except Exception as e:
            log.error(f"Error getting programs from database: {e}")
            all_programs = []
        
        # Filter by search text if provided
        if search_text:
            search_lower = search_text.lower()
            all_programs = [
                p for p in all_programs
                if (search_lower in p.id.lower() or
                    search_lower in p.name.lower() or
                    (p.genre and search_lower in p.genre.lower()) or
                    (p.digital_1 and search_lower in p.digital_1.lower()) or
                    (p.digital_2 and search_lower in p.digital_2.lower()) or
                    (p.analog and search_lower in p.analog.lower()) or
                    (p.drums and search_lower in p.drums.lower()))
            ]
        
        # Clear table
        try:
            self.user_programs_table.setRowCount(0)
        except Exception as e:
            log.error(f"Error clearing user programs table: {e}")
            return
        
        # Populate table
        for program in all_programs:
            row = self.user_programs_table.rowCount()
            self.user_programs_table.insertRow(row)
            
            # Extract bank letter from ID
            bank_letter = program.id[0] if program.id else ""
            
            # Create items
            self.user_programs_table.setItem(row, 0, QTableWidgetItem(program.id or ""))
            # Make Name column editable (column 1)
            name_item = QTableWidgetItem(program.name or "")
            name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.user_programs_table.setItem(row, 1, name_item)
            # Make Genre column editable (column 2)
            genre_item = QTableWidgetItem(program.genre or "")
            genre_item.setFlags(genre_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.user_programs_table.setItem(row, 2, genre_item)
            self.user_programs_table.setItem(row, 3, QTableWidgetItem(bank_letter))
            self.user_programs_table.setItem(row, 4, QTableWidgetItem(str(program.pc) if program.pc is not None else ""))
            self.user_programs_table.setItem(row, 5, QTableWidgetItem(str(program.msb) if program.msb is not None else ""))
            self.user_programs_table.setItem(row, 6, QTableWidgetItem(str(program.lsb) if program.lsb is not None else ""))
            self.user_programs_table.setItem(row, 7, QTableWidgetItem(program.digital_1 or ""))
            self.user_programs_table.setItem(row, 8, QTableWidgetItem(program.digital_2 or ""))
            self.user_programs_table.setItem(row, 9, QTableWidgetItem(program.analog or ""))
            self.user_programs_table.setItem(row, 10, QTableWidgetItem(program.drums or ""))
            
            # Store program object in item data for easy access
            for col in range(11):
                item = self.user_programs_table.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, program)
        
        log.message(f"✅ Populated user programs table with {len(all_programs)} programs")
    
    def _save_user_programs_changes(self) -> None:
        """
        Save changes made to the user programs table (e.g., genre edits) to the database.
        """
        if not hasattr(self, 'user_programs_table'):
            log.warning("User programs table not initialized")
            return
        
        from jdxi_editor.midi.data.programs.database import get_database
        from jdxi_editor.midi.io.input_handler import add_or_replace_program_and_save
        
        db = get_database()
        saved_count = 0
        error_count = 0
        
        # Iterate through all rows in the table
        for row in range(self.user_programs_table.rowCount()):
            # Get the program object from the first column's user data
            id_item = self.user_programs_table.item(row, 0)
            if not id_item:
                continue
            
            program = id_item.data(Qt.ItemDataRole.UserRole)
            if not program or not isinstance(program, JDXiProgram):
                continue
            
            # Get the updated name from the table (column 1)
            name_item = self.user_programs_table.item(row, 1)
            new_name = name_item.text().strip() if name_item else (program.name or "")
            
            # Get the updated genre from the table (column 2)
            genre_item = self.user_programs_table.item(row, 2)
            new_genre = genre_item.text().strip() if genre_item else (program.genre or "")
            
            # Check if name or genre has changed
            name_changed = new_name != (program.name or "")
            genre_changed = new_genre != (program.genre or "")
            
            if name_changed or genre_changed:
                # Create updated program object
                updated_program = JDXiProgram(
                    id=program.id,
                    name=new_name if new_name else None,
                    genre=new_genre if new_genre else None,
                    pc=program.pc,
                    msb=program.msb,
                    lsb=program.lsb,
                    tempo=program.tempo,
                    measure_length=program.measure_length,
                    scale=program.scale,
                    analog=program.analog,
                    digital_1=program.digital_1,
                    digital_2=program.digital_2,
                    drums=program.drums,
                )
                
                # Save to database
                if add_or_replace_program_and_save(updated_program):
                    saved_count += 1
                    changes = []
                    if name_changed:
                        changes.append(f"name: '{program.name}' -> '{new_name}'")
                    if genre_changed:
                        changes.append(f"genre: '{program.genre}' -> '{new_genre}'")
                    log.message(f"✅ Updated {program.id}: {', '.join(changes)}")
                    # Update the stored program object in item data
                    for col in range(11):
                        item = self.user_programs_table.item(row, col)
                        if item:
                            item.setData(Qt.ItemDataRole.UserRole, updated_program)
                else:
                    error_count += 1
                    log.error(f"❌ Failed to save update for {program.id}")
        
        # Show summary message
        if saved_count > 0:
            log.message(f"✅ Saved {saved_count} program update(s)")
            if error_count > 0:
                log.warning(f"⚠️ {error_count} program(s) failed to save")
        else:
            if error_count > 0:
                log.error(f"❌ Failed to save {error_count} program(s)")
            else:
                log.message("ℹ️ No changes to save")
    
    def _create_playlist_tab(self) -> QWidget:
        """
        Create the Playlist tab with a table showing all playlists.
        
        :return: QWidget containing the playlist table
        """
        log.message("🔨 _create_playlist_tab() called")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        log.message("✅ Created playlist widget and layout")
        
        # Button layout for create/delete actions
        button_layout = QHBoxLayout()
        self.create_playlist_button = QPushButton(
            qta.icon("ph.plus-circle-fill", color=JDXiStyle.FOREGROUND),
            "New Playlist"
        )
        self.create_playlist_button.clicked.connect(self._create_new_playlist)
        button_layout.addWidget(self.create_playlist_button)
        
        self.delete_playlist_button = QPushButton(
            qta.icon("ph.trash-fill", color=JDXiStyle.FOREGROUND),
            "Delete Playlist"
        )
        self.delete_playlist_button.clicked.connect(self._delete_selected_playlist)
        button_layout.addWidget(self.delete_playlist_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Create playlist table
        self.playlist_table = QTableWidget()
        self.playlist_table.setColumnCount(4)
        self.playlist_table.setHorizontalHeaderLabels([
            "ID", "Name", "Description", "Programs"
        ])
        
        # Apply custom styling
        self.playlist_table.setStyleSheet(self._get_table_style())
        
        # Enable sorting
        self.playlist_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.playlist_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Programs
        
        # Make Name and Description columns editable
        # (We'll handle this in the populate method)
        
        # Connect item changed to save edits
        self.playlist_table.itemChanged.connect(self._on_playlist_item_changed)
        
        # Connect double-click to edit playlist
        self.playlist_table.itemDoubleClicked.connect(self._on_playlist_selected)
        
        layout.addWidget(self.playlist_table)
        log.message("✅ Added playlist table to layout")
        
        # Populate table (with error handling)
        try:
            log.message("🔨 Calling _populate_playlist_table()...")
            self._populate_playlist_table()
            log.message("✅ Playlist table populated successfully")
        except Exception as e:
            log.error(f"❌ Error populating playlist table: {e}")
            import traceback
            log.error(traceback.format_exc())
        
        log.message(f"✅ Returning Playlist tab widget")
        return widget
    
    def _populate_playlist_table(self) -> None:
        """
        Populate the playlist table from SQLite database.
        """
        if not hasattr(self, 'playlist_table'):
            log.warning("Playlist table not initialized")
            return
        
        try:
            from jdxi_editor.midi.data.programs.database import get_database
            
            # Get all playlists from database
            db = get_database()
            all_playlists = db.get_all_playlists()
        except Exception as e:
            log.error(f"Error getting playlists from database: {e}")
            import traceback
            log.error(traceback.format_exc())
            all_playlists = []
        
        # Disable sorting while populating to prevent data misalignment
        was_sorting_enabled = self.playlist_table.isSortingEnabled()
        self.playlist_table.setSortingEnabled(False)
        
        try:
            # Clear table
            self.playlist_table.setRowCount(0)
            
            # Populate table
            for playlist in all_playlists:
                row = self.playlist_table.rowCount()
                self.playlist_table.insertRow(row)
                
                # Create items
                id_item = QTableWidgetItem(str(playlist["id"]))
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # ID not editable
                # Set data role for proper sorting (as integer)
                id_item.setData(Qt.ItemDataRole.DisplayRole, playlist["id"])
                id_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 0, id_item)
                
                # Name column - editable
                name_item = QTableWidgetItem(playlist["name"] or "")
                name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)
                name_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 1, name_item)
                
                # Description column - editable
                desc_item = QTableWidgetItem(playlist["description"] or "")
                desc_item.setFlags(desc_item.flags() | Qt.ItemFlag.ItemIsEditable)
                desc_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 2, desc_item)
                
                # Program count
                program_count = playlist.get("program_count", 0)
                count_item = QTableWidgetItem(str(program_count))
                count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Not editable
                # Set data role for proper sorting (as integer)
                count_item.setData(Qt.ItemDataRole.DisplayRole, program_count)
                count_item.setData(Qt.ItemDataRole.UserRole, playlist)
                self.playlist_table.setItem(row, 3, count_item)
        finally:
            # Re-enable sorting if it was enabled before
            self.playlist_table.setSortingEnabled(was_sorting_enabled)
        
        log.message(f"✅ Populated playlist table with {len(all_playlists)} playlists")
    
    def _create_new_playlist(self) -> None:
        """Create a new playlist."""
        from PySide6.QtWidgets import QInputDialog
        from jdxi_editor.midi.data.programs.database import get_database
        
        name, ok = QInputDialog.getText(
            self,
            "New Playlist",
            "Enter playlist name:"
        )
        
        if ok and name.strip():
            db = get_database()
            playlist_id = db.create_playlist(name.strip())
            if playlist_id:
                log.message(f"✅ Created playlist: {name}")
                self._populate_playlist_table()
                # Refresh playlist editor combo if it exists
                if hasattr(self, 'playlist_editor_combo'):
                    self._populate_playlist_editor_combo()
            else:
                log.error(f"❌ Failed to create playlist: {name}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Failed to create playlist '{name}'. It may already exist.")
    
    def _delete_selected_playlist(self) -> None:
        """Delete the selected playlist."""
        selected_rows = self.playlist_table.selectionModel().selectedRows()
        if not selected_rows:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Selection", "Please select a playlist to delete.")
            return
        
        row = selected_rows[0].row()
        id_item = self.playlist_table.item(row, 0)
        if not id_item:
            return
        
        playlist = id_item.data(Qt.ItemDataRole.UserRole)
        if not playlist:
            return
        
        playlist_id = playlist["id"]
        playlist_name = playlist["name"]
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Playlist",
            f"Are you sure you want to delete playlist '{playlist_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from jdxi_editor.midi.data.programs.database import get_database
            db = get_database()
            if db.delete_playlist(playlist_id):
                log.message(f"✅ Deleted playlist: {playlist_name}")
                self._populate_playlist_table()
                # Refresh playlist editor combo if it exists
                if hasattr(self, 'playlist_editor_combo'):
                    self._populate_playlist_editor_combo()
                    # Clear the programs table if the deleted playlist was selected
                    if self.playlist_editor_combo.currentData() == playlist_id:
                        self.playlist_programs_table.setRowCount(0)
            else:
                log.error(f"❌ Failed to delete playlist: {playlist_name}")
                QMessageBox.warning(self, "Error", f"Failed to delete playlist '{playlist_name}'.")
    
    def _on_playlist_item_changed(self, item: QTableWidgetItem) -> None:
        """
        Handle changes to playlist name or description.
        
        :param item: The table item that was changed
        """
        row = item.row()
        col = item.column()
        
        # Only handle name (col 1) and description (col 2) changes
        if col not in [1, 2]:
            return
        
        # Get playlist data
        playlist = item.data(Qt.ItemDataRole.UserRole)
        if not playlist:
            return
        
        playlist_id = playlist["id"]
        new_value = item.text().strip()
        
        from jdxi_editor.midi.data.programs.database import get_database
        db = get_database()
        
        if col == 1:  # Name column
            if db.update_playlist(playlist_id, name=new_value):
                try:
                    log.message(f"✅ Updated playlist {playlist_id} name to: {new_value}")
                    # Update stored playlist data
                    playlist["name"] = new_value
                    for c in range(4):
                        table_item = self.playlist_table.item(row, c)
                        if table_item:
                            table_item.setData(Qt.ItemDataRole.UserRole, playlist)
                except Exception as ex:
                    log.error(f"Error {ex} occurred updating playlist")
            else:
                log.error(f"❌ Failed to update playlist {playlist_id} name")
                # Revert the change
                self.playlist_table.blockSignals(True)
                item.setText(playlist.get("name", ""))
                self.playlist_table.blockSignals(False)
        elif col == 2:  # Description column
            value = new_value or ""  # never pass None
            if db.update_playlist(playlist_id, description=value):
                log.message(f"Updated playlist {playlist_id} description")
                playlist["description"] = value
                for c in range(4):
                    table_item = self.playlist_table.item(row, c)
                    if table_item:
                        table_item.setData(Qt.ItemDataRole.UserRole, playlist)
            else:
                log.error(f"Failed to update playlist {playlist_id} description")
                self.playlist_table.blockSignals(True)
                item.setText(playlist.get("description", "") or "")
                self.playlist_table.blockSignals(False)
    
    def _on_playlist_selected(self, item: QTableWidgetItem) -> None:
        """
        Handle double-click on a playlist.
        Could open playlist editor or show playlist programs.
        
        :param item: The table item that was double-clicked
        """
        # For now, just log it. Could be extended to show playlist contents
        playlist = item.data(Qt.ItemDataRole.UserRole)
        if playlist:
            log.message(f"📋 Selected playlist: {playlist['name']} (ID: {playlist['id']})")
    
    def _create_playlist_editor_tab(self) -> QWidget:
        """
        Create the Playlist Editor tab for editing playlist contents.
        
        :return: QWidget containing the playlist editor
        """
        log.message("🔨 _create_playlist_editor_tab() called")
        widget = QWidget()
        layout = QVBoxLayout(widget)
        log.message("✅ Created playlist editor widget and layout")
        
        # Playlist selection
        playlist_select_layout = QHBoxLayout()
        playlist_select_layout.addWidget(QLabel("Select Playlist:"))
        self.playlist_editor_combo = QComboBox()
        self.playlist_editor_combo.currentIndexChanged.connect(self._on_playlist_editor_playlist_changed)
        playlist_select_layout.addWidget(self.playlist_editor_combo)
        playlist_select_layout.addStretch()
        layout.addLayout(playlist_select_layout)
        
        # Add/Delete buttons
        button_layout = QHBoxLayout()
        self.add_to_playlist_button = QPushButton(
            qta.icon("ph.plus-circle-fill", color=JDXiStyle.FOREGROUND),
            "Add to Playlist"
        )
        self.add_to_playlist_button.clicked.connect(self._add_program_to_playlist)
        self.add_to_playlist_button.setEnabled(False)  # Disabled until playlist is selected
        button_layout.addWidget(self.add_to_playlist_button)
        
        self.delete_from_playlist_button = QPushButton(
            qta.icon("ph.trash-fill", color=JDXiStyle.FOREGROUND),
            "Delete from Playlist"
        )
        self.delete_from_playlist_button.clicked.connect(self._delete_program_from_playlist)
        self.delete_from_playlist_button.setEnabled(False)  # Disabled until playlist is selected
        button_layout.addWidget(self.delete_from_playlist_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Create playlist programs table
        self.playlist_programs_table = QTableWidget()
        self.playlist_programs_table.setColumnCount(6)
        self.playlist_programs_table.setHorizontalHeaderLabels([
            "Bank", "Number", "Program Name", "MIDI File Name", "Cheat Preset", "Play"
        ])
        
        # Apply custom styling
        self.playlist_programs_table.setStyleSheet(self._get_table_style())
        
        # Enable sorting
        self.playlist_programs_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.playlist_programs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Bank
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Number
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Program Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # MIDI File Name
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Cheat Preset
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Play
        
        # Set delegates
        midi_file_delegate = MidiFileDelegate(table_widget=self.playlist_programs_table, parent=self.playlist_programs_table)
        self.playlist_programs_table.setItemDelegateForColumn(3, midi_file_delegate)
        
        play_button_delegate = PlayButtonDelegate(
            self.playlist_programs_table,
            play_callback=self._play_playlist_program
        )
        self.playlist_programs_table.setItemDelegateForColumn(5, play_button_delegate)
        
        # Connect item changed to save MIDI file paths
        self.playlist_programs_table.itemChanged.connect(self._on_playlist_program_item_changed)
        
        # Connect double-click to show Program Editor when Program Name is clicked
        self.playlist_programs_table.itemDoubleClicked.connect(self._on_playlist_program_double_clicked)
        
        # Connect selection changed to enable/disable delete button
        self.playlist_programs_table.selectionModel().selectionChanged.connect(
            self._on_playlist_programs_selection_changed
        )
        
        layout.addWidget(self.playlist_programs_table)
        log.message("✅ Added playlist programs table to layout")
        
        # Populate playlist combo box
        self._populate_playlist_editor_combo()
        
        log.message(f"✅ Returning Playlist Editor tab widget")
        return widget
    
    def _populate_playlist_editor_combo(self) -> None:
        """Populate the playlist selection combo box."""
        if not hasattr(self, 'playlist_editor_combo'):
            return
        
        try:
            from jdxi_editor.midi.data.programs.database import get_database
            db = get_database()
            playlists = db.get_all_playlists()
            
            self.playlist_editor_combo.clear()
            self.playlist_editor_combo.addItem("-- Select a Playlist --", None)
            for playlist in playlists:
                self.playlist_editor_combo.addItem(
                    f"{playlist['name']} ({playlist.get('program_count', 0)} programs)",
                    playlist['id']
                )
        except Exception as e:
            log.error(f"Error populating playlist editor combo: {e}")
    
    def _on_playlist_programs_selection_changed(self) -> None:
        """Handle selection change in playlist programs table."""
        if not hasattr(self, 'delete_from_playlist_button'):
            return
        
        selected_rows = self.playlist_programs_table.selectionModel().selectedRows()
        playlist_id = self.playlist_editor_combo.currentData()
        
        # Enable delete button only if playlist is selected and rows are selected
        self.delete_from_playlist_button.setEnabled(
            playlist_id is not None and len(selected_rows) > 0
        )
    
    def _on_playlist_editor_playlist_changed(self, index: int) -> None:
        """Handle playlist selection change in the editor."""
        playlist_id = self.playlist_editor_combo.itemData(index)
        if playlist_id:
            self._populate_playlist_programs_table(playlist_id)
            # Enable add button when playlist is selected
            if hasattr(self, 'add_to_playlist_button'):
                self.add_to_playlist_button.setEnabled(True)
            # Delete button state will be updated by selection change handler
            self._on_playlist_programs_selection_changed()
        else:
            self.playlist_programs_table.setRowCount(0)
            # Disable buttons when no playlist is selected
            if hasattr(self, 'add_to_playlist_button'):
                self.add_to_playlist_button.setEnabled(False)
            if hasattr(self, 'delete_from_playlist_button'):
                self.delete_from_playlist_button.setEnabled(False)
    
    def _populate_playlist_programs_table(self, playlist_id: int) -> None:
        """
        Populate the playlist programs table with programs from the selected playlist.
        
        :param playlist_id: Playlist ID
        """
        if not hasattr(self, 'playlist_programs_table'):
            return
        
        try:
            from jdxi_editor.midi.data.programs.database import get_database
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
            midi_file_item.setData(Qt.ItemDataRole.UserRole + 1, {"playlist_id": playlist_id, "program_id": program.id})
            self.playlist_programs_table.setItem(row, 3, midi_file_item)
            
            # Cheat Preset ComboBox
            cheat_preset_combo = QComboBox()
            cheat_preset_combo.addItem("None", None)  # No cheat preset
            # Add Digital Synth presets
            from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
            for preset in DIGITAL_PRESET_LIST:
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
                lambda idx, r=row: self._on_cheat_preset_changed(r, cheat_preset_combo.itemData(idx))
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
        
        log.message(f"✅ Populated playlist programs table with {len(playlist_items)} programs")
    
    def _on_cheat_preset_changed(self, row: int, cheat_preset_id: Optional[str]) -> None:
        """
        Handle cheat preset selection change.
        
        :param row: Table row index
        :param cheat_preset_id: Selected cheat preset ID or None
        """
        combo = self.playlist_programs_table.cellWidget(row, 4)
        if not combo:
            return
        
        playlist_id = combo.property("playlist_id")
        program_id = combo.property("program_id")
        
        if not playlist_id or not program_id:
            return
        
        try:
            from jdxi_editor.midi.data.programs.database import get_database
            db = get_database()
            db.update_playlist_item_cheat_preset(playlist_id, program_id, cheat_preset_id)
            log.message(f"✅ Updated cheat preset for playlist {playlist_id}, program {program_id}: {cheat_preset_id}")
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
        from jdxi_editor.midi.data.programs.database import get_database
        db = get_database()
        if db.update_playlist_item_midi_file(playlist_id, program_id, midi_file_path):
            log.message(f"✅ Saved MIDI file path for playlist {playlist_id}, program {program_id}: {midi_file_path}")
        else:
            log.error(f"❌ Failed to save MIDI file path for playlist {playlist_id}, program {program_id}")
    
    def _add_program_to_playlist(self) -> None:
        """Add a program to the selected playlist."""
        # Check if a playlist is selected
        playlist_id = self.playlist_editor_combo.currentData()
        if not playlist_id:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Playlist Selected", "Please select a playlist first.")
            return
        
        # Show a dialog to select programs from User Programs table
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Programs to Playlist")
        dialog_layout = QVBoxLayout(dialog)
        
        # Get playlist name
        playlist_name = self.playlist_editor_combo.currentText().split(" (")[0]
        dialog_layout.addWidget(QLabel(f"Select programs to add to '{playlist_name}':"))
        
        # Create list widget with all user programs
        program_list = QListWidget()
        program_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        try:
            from jdxi_editor.midi.data.programs.database import get_database
            db = get_database()
            all_programs = db.get_all_programs()
            
            # Get programs already in playlist
            existing_programs = db.get_playlist_programs(playlist_id)
            existing_program_ids = {item["program"].id for item in existing_programs}
            
            # Add programs that aren't already in the playlist
            for program in all_programs:
                if program.id not in existing_program_ids:
                    program_list.addItem(f"{program.id} - {program.name}")
                    # Store program ID in item data
                    item = program_list.item(program_list.count() - 1)
                    item.setData(Qt.ItemDataRole.UserRole, program.id)
        except Exception as e:
            log.error(f"Error loading programs for playlist: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load programs: {e}")
            return
        
        dialog_layout.addWidget(program_list)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = program_list.selectedItems()
            if not selected_items:
                QMessageBox.information(self, "No Selection", "Please select at least one program to add.")
                return
            
            # Add selected programs to playlist
            from jdxi_editor.midi.data.programs.database import get_database
            db = get_database()
            added_count = 0
            
            for item in selected_items:
                program_id = item.data(Qt.ItemDataRole.UserRole)
                if db.add_program_to_playlist(playlist_id, program_id):
                    added_count += 1
            
            if added_count > 0:
                log.message(f"✅ Added {added_count} program(s) to playlist")
                # Refresh the table
                self._populate_playlist_programs_table(playlist_id)
                # Refresh combo to update program count
                self._populate_playlist_editor_combo()
                # Restore selection
                index = self.playlist_editor_combo.findData(playlist_id)
                if index >= 0:
                    self.playlist_editor_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Error", "Failed to add programs to playlist.")
    
    def _delete_program_from_playlist(self) -> None:
        """Delete selected program(s) from the playlist."""
        # Check if a playlist is selected
        playlist_id = self.playlist_editor_combo.currentData()
        if not playlist_id:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Playlist Selected", "Please select a playlist first.")
            return
        
        # Get selected rows
        selected_rows = self.playlist_programs_table.selectionModel().selectedRows()
        if not selected_rows:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Selection", "Please select at least one program to delete.")
            return
        
        # Confirm deletion
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Programs",
            f"Are you sure you want to delete {len(selected_rows)} program(s) from the playlist?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from jdxi_editor.midi.data.programs.database import get_database
            db = get_database()
            deleted_count = 0
            
            # Delete in reverse order to maintain row indices
            for row_index in sorted([row.row() for row in selected_rows], reverse=True):
                # Get program ID from the table
                program_item = self.playlist_programs_table.item(row_index, 0)  # Bank column has program data
                if program_item:
                    program = program_item.data(Qt.ItemDataRole.UserRole)
                    if program and isinstance(program, JDXiProgram):
                        if db.remove_program_from_playlist(playlist_id, program.id):
                            deleted_count += 1
            
            if deleted_count > 0:
                log.message(f"✅ Deleted {deleted_count} program(s) from playlist")
                # Refresh the table
                self._populate_playlist_programs_table(playlist_id)
                # Refresh combo to update program count
                self._populate_playlist_editor_combo()
                # Restore selection
                index = self.playlist_editor_combo.findData(playlist_id)
                if index >= 0:
                    self.playlist_editor_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Error", "Failed to delete programs from playlist.")
    
    def _play_playlist_program(self, index) -> None:
        """
        Play the MIDI file associated with a playlist program.
        
        :param index: QModelIndex of the play button
        """
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
        self._load_program_from_table_for_playlist(row)
        
        # Load cheat preset if selected (send on Analog Synth channel 3)
        # Add a delay to ensure the main program change is processed first
        cheat_preset_combo = self.playlist_programs_table.cellWidget(row, 4)
        log.message(f"🔍 Checking cheat preset for row {row}: combo={cheat_preset_combo}")
        if cheat_preset_combo:
            cheat_preset_id = cheat_preset_combo.currentData()
            log.message(f"🔍 Cheat preset ID from combo: {cheat_preset_id} (type: {type(cheat_preset_id)})")
            if cheat_preset_id:
                log.message(f"🎹 Scheduling cheat preset load: {cheat_preset_id} (delayed by 500ms)")
                # Delay cheat preset loading to ensure main program change is processed first
                # Use a longer delay to ensure the synthesizer has time to process the first program change
                QTimer.singleShot(500, lambda: self._load_cheat_preset(cheat_preset_id))
            else:
                log.message("ℹ️ No cheat preset selected (None)")
        else:
            log.warning(f"⚠️ Cheat preset combo box not found for row {row}")
        
        # If MIDI file is specified, load and play it
        if midi_file_path:
            import os
            from pathlib import Path
            from mido import MidiFile
            from PySide6.QtWidgets import QMessageBox
            
            # Check if file exists
            if not os.path.exists(midi_file_path):
                log.warning(f"⚠️ MIDI file not found: {midi_file_path}")
                QMessageBox.warning(self, "File Not Found", f"MIDI file not found:\n{midi_file_path}")
                return
            
            log.message(f"🎵 Loading and playing MIDI file: {midi_file_path} for program {program.id}")
            
            # Get the parent instrument to access MidiFileEditor
            # Note: parent is stored as an attribute (self.parent), not a method
            # The parent should be JDXiInstrument when ProgramEditor is opened from the main window
            parent_instrument = getattr(self, 'parent', None)
            
            # Walk up the parent chain to find JDXiInstrument if needed
            # (in case parent is not JDXiInstrument directly)
            while parent_instrument and not hasattr(parent_instrument, 'get_existing_editor'):
                # Get parent's parent (also stored as attribute in SynthBase)
                next_parent = getattr(parent_instrument, 'parent', None)
                if not next_parent:
                    break
                parent_instrument = next_parent
            
            if parent_instrument and hasattr(parent_instrument, 'get_existing_editor'):
                # Get or create MidiFileEditor
                from jdxi_editor.ui.editors.io.player import MidiFileEditor
                midi_file_editor = parent_instrument.get_existing_editor(MidiFileEditor)
                
                if not midi_file_editor:
                    # Create the editor if it doesn't exist
                    parent_instrument.show_editor("midi_file")
                    midi_file_editor = parent_instrument.get_existing_editor(MidiFileEditor)
                
                if midi_file_editor:
                    # Load the MIDI file directly (bypassing the file dialog)
                    
                    try:
                        # Disconnect any existing finished signal from previous playlist playback
                        if self._playlist_midi_editor and hasattr(self._playlist_midi_editor, 'midi_playback_worker'):
                            if self._playlist_midi_editor.midi_playback_worker:
                                try:
                                    self._playlist_midi_editor.midi_playback_worker.finished.disconnect(self._on_playlist_playback_finished)
                                except:
                                    pass
                        
                        # Stop any current playback
                        if hasattr(midi_file_editor, "midi_stop_playback"):
                            midi_file_editor.midi_stop_playback()
                        if hasattr(midi_file_editor, "midi_playback_worker_stop"):
                            midi_file_editor.midi_playback_worker_stop()
                        
                        # Reset tracking if we're starting a new playback
                        self._current_playlist_row = None
                        self._playlist_midi_editor = None
                        
                        # Load MIDI file
                        midi_file_editor.midi_state.file = MidiFile(midi_file_path)
                        midi_file_editor.ui.digital_title_file_name.setText(f"Loaded: {Path(midi_file_path).name}")
                        midi_file_editor.ui.midi_track_viewer.clear()
                        midi_file_editor.ui.midi_track_viewer.set_midi_file(midi_file_editor.midi_state.file)
                        
                        # Initialize MIDI file parameters (similar to midi_load_file)
                        midi_file_editor.ticks_per_beat = midi_file_editor.midi_state.file.ticks_per_beat
                        
                        # Detect initial tempo
                        if hasattr(midi_file_editor, "detect_initial_tempo"):
                            initial_track_tempos = midi_file_editor.detect_initial_tempo()
                        
                        midi_file_editor.ui_display_set_tempo_usecs(midi_file_editor.midi_state.tempo_initial)
                        midi_file_editor.midi_state.tempo_at_position = midi_file_editor.midi_state.tempo_initial
                        
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
                        if hasattr(midi_file_editor, 'midi_playback_worker') and midi_file_editor.midi_playback_worker:
                            try:
                                # Disconnect any existing connection
                                midi_file_editor.midi_playback_worker.finished.disconnect()
                            except:
                                pass
                            # Connect to finished signal
                            midi_file_editor.midi_playback_worker.finished.connect(self._on_playlist_playback_finished)
                        
                        # Start playback
                        midi_file_editor.midi_playback_start()
                        
                        log.message(f"✅ Started playing MIDI file: {Path(midi_file_path).name}")
                    except Exception as e:
                        log.error(f"❌ Error loading/playing MIDI file: {e}")
                        import traceback
                        log.error(traceback.format_exc())
                        QMessageBox.warning(self, "Error", f"Failed to load MIDI file:\n{str(e)}")
                        # Reset tracking on error
                        self._current_playlist_row = None
                        self._playlist_midi_editor = None
                else:
                    log.error("❌ Could not access MidiFileEditor")
            else:
                log.warning("⚠️ Could not access parent instrument to load MIDI file")
        else:
            log.message(f"ℹ️ No MIDI file selected for program {program.id}, only program loaded")
    
    def _on_playlist_playback_finished(self):
        """
        Called when MIDI playback finishes. Advances to the next playlist item.
        """
        if self._current_playlist_row is None:
            return
        
        # Disconnect the finished signal
        if self._playlist_midi_editor and hasattr(self._playlist_midi_editor, 'midi_playback_worker'):
            try:
                if self._playlist_midi_editor.midi_playback_worker:
                    self._playlist_midi_editor.midi_playback_worker.finished.disconnect(self._on_playlist_playback_finished)
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
            log.message(f"⚠️ Next playlist item (row {next_row}) has no MIDI file, stopping auto-advance")
            self._current_playlist_row = None
            self._playlist_midi_editor = None
            return
        
        # Play the next item
        log.message(f"🎵 Auto-advancing to next playlist item (row {next_row})")
        # Create a QModelIndex for the play button column (column 5)
        from PySide6.QtCore import QModelIndex
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
        parent_instrument = getattr(self, 'parent', None)
        
        # Walk up the parent chain to find JDXiInstrument if needed
        # JDXiInstrument should have both 'show_editor' and 'get_existing_editor' methods
        while parent_instrument:
            if hasattr(parent_instrument, 'show_editor') and hasattr(parent_instrument, 'get_existing_editor'):
                # Found JDXiInstrument
                try:
                    # Check if ProgramEditor is already open
                    from jdxi_editor.ui.editors.io.program import ProgramEditor
                    existing_editor = parent_instrument.get_existing_editor(ProgramEditor)
                    if existing_editor:
                        # Already open, just raise it
                        existing_editor.show()
                        existing_editor.raise_()
                        existing_editor.activateWindow()
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
            next_parent = getattr(parent_instrument, 'parent', None)
            if not next_parent:
                # Try QWidget.parent() method as fallback
                try:
                    if hasattr(parent_instrument, 'parent'):
                        next_parent = parent_instrument.parent()
                except:
                    pass
            
            if not next_parent or next_parent == parent_instrument:
                break
            parent_instrument = next_parent
        
        # If we couldn't find JDXiInstrument, try to show/raise this window itself
        log.warning("⚠️ Could not find parent JDXiInstrument, trying to show current window")
        try:
            self.show()
            self.raise_()
            self.activateWindow()
            log.message("✅ Raised current Program Editor window")
        except Exception as e:
            log.error(f"❌ Error raising Program Editor window: {e}")
    
    def _load_program_from_table_for_playlist(self, row: int) -> None:
        """
        Load a program from the playlist programs table and send MIDI Program Change.
        
        :param row: Row index in the table
        """
        if row < 0 or row >= self.playlist_programs_table.rowCount():
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
        log.message(f"Sending Program Change: MSB={msb}, LSB={lsb}, PC={pc}")
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        
        # Request program data
        if hasattr(self, 'program_helper') and self.program_helper:
            self.program_helper.data_request()
        
        # Update UI
        self.set_current_program_name(program.name)
        if hasattr(self, 'update_current_synths'):
            self.update_current_synths(program)
    
    def _load_cheat_preset(self, preset_id: str) -> None:
        """
        Load a cheat preset (Digital Synth preset) on the Analog Synth channel (Ch3).
        
        :param preset_id: Preset ID (e.g., "113")
        """
        log.message(f"🎹 _load_cheat_preset called with preset_id: {preset_id} (type: {type(preset_id)})")
        
        if not self.midi_helper:
            log.warning("⚠️ MIDI helper not available for cheat preset loading")
            return
        
        if not preset_id:
            log.warning("⚠️ Preset ID is None or empty")
            return
        
        log.message(f"🎹 Loading cheat preset {preset_id} on Analog Synth channel (Ch3)")
        
        # Get preset parameters from DIGITAL_PRESET_LIST
        from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
        from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
        from jdxi_editor.midi.channel.channel import MidiChannel
        from jdxi_editor.log.midi_info import log_midi_info
        
        # Find preset in DIGITAL_PRESET_LIST
        preset = None
        for p in DIGITAL_PRESET_LIST:
            if str(p["id"]) == str(preset_id):  # Compare as strings to handle any type mismatches
                preset = p
                break
        
        if not preset:
            log.warning(f"⚠️ Cheat preset {preset_id} not found in DIGITAL_PRESET_LIST")
            log.message(f"🔍 Available preset IDs (first 10): {[p['id'] for p in DIGITAL_PRESET_LIST[:10]]}")
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
            log.message(f"✅ Sent cheat preset Program Change: Ch3, MSB={msb}, LSB={lsb}, PC={pc-1} (0-based)")
        except Exception as e:
            log.error(f"❌ Error sending cheat preset Program Change: {e}")
            import traceback
            log.error(traceback.format_exc())
    
    def _on_user_program_selected(self, item: QTableWidgetItem) -> None:
        """
        Handle double-click on a program in the user programs table.
        Loads the program via MIDI Program Change.
        
        :param item: The table item that was double-clicked
        """
        self._load_program_from_table(item.row())
    
    def _on_user_program_selection_changed(self) -> None:
        """
        Handle selection change in the user programs table.
        Loads the program via MIDI Program Change when a row is selected.
        """
        selected_rows = self.user_programs_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self._load_program_from_table(row)
    
    def _play_user_program(self, index) -> None:
        """
        Callback for Play button delegate - loads and plays the program.
        
        :param index: QModelIndex from the delegate
        """
        row = index.row()
        log.message(f"🎹 Play button clicked for row {row}")
        self._load_program_from_table(row)
    
    def _load_program_from_table(self, row: int) -> None:
        """
        Load a program from the table and send MIDI Program Change.
        
        :param row: Row index in the table
        """
        if row < 0 or row >= self.user_programs_table.rowCount():
            return
        
        # Get program from first column's user data
        item = self.user_programs_table.item(row, 0)
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
        
        log.message(f"🎹 Loading program from table: {program_id} - {program.name}")
        
        # Calculate MIDI values
        try:
            msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        except (ValueError, TypeError) as e:
            log.error(f"Error calculating MIDI values for {program_id}: {e}")
            return
        
        # Send MIDI Program Change
        log.message(f"Sending Program Change: MSB={msb}, LSB={lsb}, PC={pc}")
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        
        # Request program data
        if hasattr(self, 'program_helper') and self.program_helper:
            self.program_helper.data_request()
        
        # Update UI
        self.set_current_program_name(program.name)
        if hasattr(self, 'update_current_synths'):
            self.update_current_synths(program)
        
        # Also update the program combo box to reflect the selected program
        # Find the program in the combo box and select it
        for i in range(self.program_number_combo_box.count()):
            item_text = self.program_number_combo_box.itemText(i)
            if item_text.startswith(program_id):
                self.program_number_combo_box.setCurrentIndex(i)
                break

    def on_bank_changed(self, _: int) -> None:
        """Handle bank selection change."""
        self.populate_programs()

    def on_program_number_changed(self, index: int) -> None:
        """Handle program number selection change.
        :param index: int
        """
        # self.load_program()

    def load_program(self):
        """Load the selected program based on bank and number."""
        program_name = self.program_number_combo_box.currentText()
        program_id = program_name[:3]
        bank_letter = program_name[0]
        bank_number = int(program_name[1:3])
        log.parameter("combo box bank_letter", bank_letter)
        log.parameter("combo box bank_number", bank_number)
        if bank_letter in ["A", "B", "C", "D"]:
            program_details = get_program_by_id(program_id)
            self.update_current_synths(program_details)
            self.set_current_program_name(program_details.name)
        msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        log.message("calculated msb, lsb, pc :")
        log.parameter("msb", msb)
        log.parameter("lsb", lsb)
        log.parameter("pc", pc)
        log_midi_info(msb, lsb, pc)
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        self.data_request()

    def update_current_synths(self, program_details: JDXiProgram) -> None:
        """Update the current synth label.
        :param program_details: dict
        :return: None
        """
        try:
            self.digital_synth_1_current_label.setText(program_details.digital_1)
            self.digital_synth_2_current_label.setText(program_details.digital_2)
            self.drum_kit_current_label.setText(program_details.drums)
            self.analog_synth_current_label.setText(program_details.analog)
        except KeyError:
            log.message(f"Program details missing required keys: {program_details}")
            self.digital_synth_1_current_label.setText("Unknown")
            self.digital_synth_2_current_label.setText("Unknown")
            self.drum_kit_current_label.setText("Unknown")
            self.analog_synth_current_label.setText("Unknown")

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
        Handle genre selection change.

        :param _: int
        """
        self.populate_programs()

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
        temporary_area = sysex_data.get("TEMPORARY_AREA")
        synth_tone = sysex_data.get("SYNTH_TONE")

        log.header_message(
            f"Updating UI components from SysEx data for \t{temporary_area} \t{synth_tone}"
        )

        sysex_data = filter_sysex_keys(sysex_data)

        successes, failures = [], []

        if temporary_area == AddressOffsetTemporaryToneUMB.DRUM_KIT.name:
            partial_map = DRUM_PARTIAL_MAP
        else:
            partial_map = SYNTH_PARTIAL_MAP

        # Define a mapping between temporary_area and their corresponding handlers
        temporary_area_handlers = {
            AddressStartMSB.TEMPORARY_PROGRAM.name: {
                "PROGRAM_LEVEL": (AddressParameterProgramCommon.PROGRAM_LEVEL, self.master_level_slider)
            },
            AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name: {
                "AMP_LEVEL": (AddressParameterAnalog.get_by_name, self.analog_level_slider)
            },
            AddressOffsetTemporaryToneUMB.DRUM_KIT.name: {
                "KIT_LEVEL": (AddressParameterDrumCommon.KIT_LEVEL, self.drums_level_slider)
            },
            AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name: {
                "TONE_LEVEL": (AddressParameterDigitalCommon.get_by_name, self.digital1_level_slider)
            },
            AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name: {
                "TONE_LEVEL": (AddressParameterDigitalCommon.get_by_name, self.digital2_level_slider)
            }
        }

        partial_tone_names = [
            AddressOffsetSuperNATURALLMB.PARTIAL_1.name,
            AddressOffsetSuperNATURALLMB.PARTIAL_2.name,
            AddressOffsetSuperNATURALLMB.PARTIAL_3.name,
        ]

        # Get the partial number
        partial_number = get_partial_number(synth_tone, partial_map=partial_map)

        # Handle the temporary_area cases
        if temporary_area in temporary_area_handlers:
            handler = temporary_area_handlers[temporary_area]
            for param_name, param_value in sysex_data.items():
                if param_name in handler:
                    param_info = handler[param_name]
                    param = param_info[0](param_name) if callable(param_info[0]) else param_info[0]
                    self._update_slider(param, param_value, successes, failures, param_info[1])

        # Handle the partial tone cases
        if synth_tone in partial_tone_names:
            self._update_common_controls(partial_number, sysex_data, successes, failures)

        log.debug_info(successes, failures)

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
        log.message(f"Updating controls for partial {partial_number}")
        log.parameter("self.controls", self.controls)
        for control in self.controls:
            log.parameter("control @@", control, silent=False)
        sysex_data.pop("SYNTH_TONE", None)
        for param_name, param_value in sysex_data.items():
            log.parameter(f"{param_name} {param_value}", param_value, silent=True)
            param = AddressParameterDigitalCommon.get_by_name(param_name)
            if not param:
                log.parameter(
                    f"param not found: {param_name} ", param_value, silent=True
                )
                failures.append(param_name)
                continue
            log.parameter(f"found {param_name}", param_name, silent=True)
            try:
                if param.name in [
                    "PARTIAL1_SWITCH",
                    "PARTIAL2_SWITCH",
                    "PARTIAL3_SWITCH",
                ]:
                    pass
                    """self._update_partial_selection_switch(
                        param, param_value, successes, failures
                    )"""
                if param.name in [
                    "PARTIAL1_SELECT",
                    "PARTIAL2_SELECT",
                    "PARTIAL3_SELECT",
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
            slider: QWidget = None) -> None:
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
