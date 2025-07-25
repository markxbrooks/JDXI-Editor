"""
PresetEditor Module

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

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout,
    QLineEdit, QGroupBox,
)
from PySide6.QtCore import Signal, Qt
import qtawesome as qta

from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.editors.helpers.program import (
    get_program_by_id,
    calculate_midi_values,
)
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.jdxi.style import JDXiStyle


class PresetEditor(BasicEditor):
    """Program Editor Window"""

    program_changed = Signal(int, str, int)  # (channel, preset_name, program_number)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
        preset_helper: JDXiPresetHelper = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent)
        """
        Initialize the PresetEditor

        :param midi_helper: Optional[MidiIOHelper]
        :param parent: Optional[QWidget]
        :param preset_helper: JDXIPresetHelper
        """
        self.digital_preset_type_combo = None
        self.setWindowFlag(Qt.Window)
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.midi_channel = (
            MidiChannel.DIGITAL_SYNTH_1  # Default MIDI channel: 16 for programs, 0-based
        )
        self.default_image = "presets.png"
        self.instrument_icon_folder = "presets"
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL
        self.layout = None
        self.genre_label = None
        self.preset_combo_box = None
        self.load_button = None
        self.save_button = None
        self.image_label = None
        self.title_label = None
        self.bank_label = None
        self.digital_preset_label = None
        self.category_combo_box = None
        self.preset_type = None
        self.synth_label_map = {
            JDXiSynth.DIGITAL_SYNTH_1: self.digital_synth_1_current_label,
            JDXiSynth.DIGITAL_SYNTH_2: self.digital_synth_2_current_label,
            JDXiSynth.DRUM_KIT: self.drum_kit_current_label,
            JDXiSynth.ANALOG_SYNTH: self.analog_synth_current_label,
        }
        self.presets = {}  # Maps program names to numbers
        self.setup_ui()
        self.data_request()

    def setup_ui(self):
        """set up UI elements"""
        self.setWindowTitle("Preset Editor")
        self.setMinimumSize(400, 400)
        # center_widget = QWidget()
        main_vlayout = QVBoxLayout()
        # self.setCentralWidget(center_widget)
        self.setLayout(main_vlayout)
        self.setStyleSheet(JDXiStyle.EDITOR)

        self.title_label = QLabel("Presets:")
        self.title_label.setStyleSheet(
            """
                font-size: 16px;
                font-weight: bold;
            """
        )
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        main_vlayout.addLayout(title_layout)
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        title_layout.addWidget(self.image_label)
        self.update_instrument_image()

        preset_group = self._create_preset_selection_group()
        main_vlayout.addWidget(preset_group)

        self.digital_synth_1_hlayout = QHBoxLayout()
        main_vlayout.addLayout(self.digital_synth_1_hlayout)

        self.digital_synth_1_icon = QLabel()
        self.digital_synth_1_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_icon)

        self.digital_synth_1_title = QLabel("Digital Synth 1")
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_title)
        self.digital_synth_1_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.digital_synth_1_current_label = QLabel("Current Tone:")
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_current_label)
        self.digital_synth_1_current_label.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.digital_synth_2_hlayout = QHBoxLayout()
        main_vlayout.addLayout(self.digital_synth_2_hlayout)

        self.digital_synth_2_icon = QLabel()
        self.digital_synth_2_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_icon)

        self.digital_synth_2_title = QLabel("Digital Synth 2")
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_title)
        self.digital_synth_2_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.digital_synth_2_current_label = QLabel("Current Tone:")
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_current_label)
        self.digital_synth_2_current_label.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;  
                color: {JDXiStyle.ACCENT};
            """
        )
        self.drum_kit_hlayout = QHBoxLayout()
        main_vlayout.addLayout(self.drum_kit_hlayout)

        self.drum_kit_icon = QLabel()
        self.drum_kit_icon.setPixmap(
            qta.icon("fa5s.drum", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.drum_kit_hlayout.addWidget(self.drum_kit_icon)

        self.drum_kit_title = QLabel("Drums")
        self.drum_kit_hlayout.addWidget(self.drum_kit_title)
        self.drum_kit_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.drum_kit_current_label = QLabel("Current Tone:")
        self.drum_kit_hlayout.addWidget(self.drum_kit_current_label)
        self.drum_kit_current_label.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.analog_synth_hlayout = QHBoxLayout()

        self.analog_synth_icon = QLabel()
        self.analog_synth_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.analog_synth_hlayout.addWidget(self.analog_synth_icon)

        main_vlayout.addLayout(self.analog_synth_hlayout)

        self.analog_synth_title = QLabel("Analog Synth")
        self.analog_synth_hlayout.addWidget(self.analog_synth_title)
        self.analog_synth_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT_ANALOG};
            """
        )
        self.analog_synth_current_label = QLabel("Current Tone:")
        self.analog_synth_hlayout.addWidget(self.analog_synth_current_label)
        self.analog_synth_current_label.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT_ANALOG};
            """
        )
        self._populate_presets()
        self.midi_helper.update_tone_name.connect(
             lambda tone_name, synth_type: self.update_tone_name_for_synth(tone_name, synth_type)
        )

    def _create_preset_selection_group(self) -> QGroupBox:
        """
        create_preset_selection_group

        :return: QGroupBox
        """
        # Program controls group
        preset_group = QGroupBox("Load a program")
        preset_vlayout = QVBoxLayout()
        preset_group.setLayout(preset_vlayout)
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
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._populate_presets)
        search_row.addWidget(self.search_box)
        preset_vlayout.addLayout(search_row)
        self.digital_preset_label = QLabel("Preset")
        preset_vlayout.addWidget(self.digital_preset_label)
        # Program number selection combo box
        self.preset_combo_box = QComboBox()
        self.preset_combo_box.addItems([f"{i:02}" for i in range(1, 65)])
        self.preset_combo_box.currentIndexChanged.connect(self.on_preset_number_changed)
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
        return preset_group

    def on_preset_type_changed(self, index: int) -> None:
        """Handle preset type selection change."""
        preset_type = self.digital_preset_type_combo.currentText()
        log.message(f"preset_type: {preset_type}")
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
        self._populate_presets()
        self.update_category_combo_box_categories()

    def update_tone_name_for_synth(self, tone_name: str, synth_type: str) -> None:
        """
        Update the tone name.

        :param tone_name: str
        :param synth_type: str
        """
        log.message(f"Update tone name triggered: tone_name {tone_name} {synth_type}")

        label = self.synth_label_map.get(synth_type)
        if label:
            label.setText(tone_name)
        else:
            log.warning(f"synth type: {synth_type} not found in mapping. Cannot update tone name.")

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

    def _populate_presets(self, search_text: str = ""):
        """
        Populate the program list with available presets.

        :param search_text: str
        """
        if not self.preset_helper:
            return

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
        self.presets.clear()

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
            index = len(self.presets)  # Use the current number of programs
            self.preset_combo_box.addItem(f"{preset_id} - {preset_name}", index)
            self.presets[preset_name] = index
        self.preset_combo_box.setCurrentIndex(
            0
        )  # Update the UI with the new program list
        self.preset_combo_box.setCurrentIndex(
            0
        )  # Select "No Category Selected" as default

    def update_category_combo_box_categories(self) -> None:
        """
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

    def on_bank_changed(self, _: int) -> None:
        """Handle bank selection change."""
        self._populate_presets()

    def on_preset_number_changed(self, index: int) -> None:
        """Handle program number selection change."""
        # self.load_program()

    def load_program(self) -> None:
        """Load the selected program based on bank and number."""
        program_name = self.preset_combo_box.currentText()
        program_id = program_name[:3]
        bank_letter = program_name[0]
        bank_number = int(program_name[1:3])
        log.parameter("combo box bank_letter", bank_letter)
        log.parameter("combo box bank_number", bank_number)
        if bank_letter in ["A", "B", "C", "D"]:
            program_details = get_program_by_id(program_id)
            log.parameter("program_details", program_details)
            self.update_current_synths(program_details)
        msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        log.message("calculated msb, lsb, pc :")
        log.parameter("combo box msb", msb)
        log.parameter("combo box lsb", lsb)
        log.parameter("combo box pc", pc)
        log_midi_info(msb, lsb, pc)
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel, msb, lsb, pc
        )
        self.data_request()

    def update_current_synths(self, program_details: dict) -> None:
        """Update the current synth label.
        :param program_details: dict
        """
        try:
            self.digital_synth_1_current_label.setText(program_details["digital_1"])
            self.digital_synth_2_current_label.setText(program_details["digital_2"])
            self.drum_kit_current_label.setText(program_details["drum"])
            self.analog_synth_current_label.setText(program_details["analog"])
        except KeyError:
            log.message(f"Program details missing required keys: {program_details}")
            self.digital_synth_1_current_label.setText("Unknown")
            self.digital_synth_2_current_label.setText("Unknown")
            self.drum_kit_current_label.setText("Unknown")
            self.analog_synth_current_label.setText("Unknown")

    def load_preset_temp(self, preset_number: int) -> None:
        """Load preset data and update UI.
        :param preset_number: int
        """
        if not self.preset_helper:
            return
        self.preset_helper.load_preset(preset_number)
        self.data_request()

    def _update_preset_list(self) -> None:
        """Update the preset list with available presets."""
        self._populate_presets()

    def on_category_changed(self, _: int) -> None:
        """Handle category selection change."""
        self._populate_presets()
