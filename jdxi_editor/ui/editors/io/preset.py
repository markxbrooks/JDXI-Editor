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
- PROGRAM_LIST for predefined program data

"""

import os
import logging
from typing import Optional

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout, QLineEdit,
)
from PySide6.QtCore import Signal, Qt
import qtawesome as qta

from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST, get_preset_parameters
from jdxi_editor.midi.data.programs.programs import PROGRAM_LIST
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_PROGRAMS, MIDI_CHANNEL_DIGITAL1, \
    MIDI_CHANNEL_DIGITAL2, MIDI_CHANNEL_DRUMS, MIDI_CHANNEL_ANALOG
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.midi.sysex.requests import PROGRAM_TONE_NAME_PARTIAL_REQUESTS, PROGRAM_TONE_NAME_REQUESTS
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.editors.helpers.program import (
    get_program_by_id,
    calculate_midi_values,
    log_midi_info, get_preset_parameter_value
)
from jdxi_editor.ui.style import Style


class PresetEditor(SynthEditor):
    """Program Editor Window"""

    program_changed = Signal(int, str, int)  # (channel, preset_name, program_number)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
        preset_helper: PresetHelper = None,
    ):
        super().__init__()
        self.digital_preset_type_combo = None
        self.setWindowFlag(Qt.Window)
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.midi_channel = (
            MIDI_CHANNEL_DIGITAL1  # Default MIDI channel: 16 for programs, 0-based
        )
        self.midi_requests = PROGRAM_TONE_NAME_REQUESTS
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
        self.presets = {}  # Maps program names to numbers
        self.setup_ui()
        self.data_request()

    def setup_ui(self):
        """set up ui elements"""
        self.setWindowTitle("Preset Editor")
        self.setMinimumSize(400, 400)
        # center_widget = QWidget()
        layout = QVBoxLayout()
        # self.setCentralWidget(center_widget)
        self.setLayout(layout)
        self.setStyleSheet(Style.JDXI_EDITOR)

        self.title_label = QLabel("Presets:")
        self.title_label.setStyleSheet(
            """
                font-size: 16px;
                font-weight: bold;
            """
        )
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        layout.addLayout(title_layout)
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        title_layout.addWidget(self.image_label)
        self.update_instrument_image()
        
        # Synth type selection combo box
        self.digital_preset_type_combo = QComboBox()
        self.digital_preset_type_combo.addItems(["Digital Synth 1", "Digital Synth 2", "Drums", "Analog Synth"])
        self.digital_preset_type_combo.currentIndexChanged.connect(self.on_preset_type_changed)
        layout.addWidget(self.digital_preset_type_combo)

        # Search Box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._populate_presets)
        search_row.addWidget(self.search_box)
        layout.addLayout(search_row)

        self.digital_preset_label = QLabel("Preset")
        layout.addWidget(self.digital_preset_label)

        # Program number selection combo box
        self.preset_combo_box = QComboBox()
        self.preset_combo_box.addItems([f"{i:02}" for i in range(1, 65)])
        self.preset_combo_box.currentIndexChanged.connect(
            self.on_preset_number_changed
        )
        layout.addWidget(self.preset_combo_box)

        self.genre_label = QLabel("Category")
        layout.addWidget(self.genre_label)

        # Category selection combo box
        self.category_combo_box = QComboBox()
        self.category_combo_box.addItem("No Category Selected")
        categories = set(preset["category"] for preset in DIGITAL_PRESET_LIST)
        self.category_combo_box.addItems(sorted(categories))
        self.category_combo_box.currentIndexChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo_box)

        # Load button
        self.load_button = QPushButton(qta.icon("ph.folder-notch-open-fill"), "Load Preset")
        self.load_button.clicked.connect(self.load_preset_by_program_change)
        layout.addWidget(self.load_button)
        self.setLayout(layout)

        self.digital_synth_1_hlayout = QHBoxLayout()
        layout.addLayout(self.digital_synth_1_hlayout)

        self.digital_synth_1_icon = QLabel()
        self.digital_synth_1_icon.setPixmap(qta.icon("msc.piano").pixmap(40, 40))
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_icon)

        self.digital_synth_1_title = QLabel("Digital Synth 1")
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_title)
        self.digital_synth_1_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT};
            """
        )
        self.digital_synth_1_current_synth = QLabel("Current Synth:")
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_current_synth)
        self.digital_synth_1_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT};
            """
        )
        self.digital_synth_2_hlayout = QHBoxLayout()
        layout.addLayout(self.digital_synth_2_hlayout)

        self.digital_synth_2_icon = QLabel()
        self.digital_synth_2_icon.setPixmap(qta.icon("msc.piano").pixmap(40, 40))
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_icon)

        self.digital_synth_2_title = QLabel("Digital Synth 2")
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_title)
        self.digital_synth_2_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT};
            """
        )
        self.digital_synth_2_current_synth = QLabel("Current Synth:")
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_current_synth)
        self.digital_synth_2_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;  
                color: {Style.ACCENT};
            """
        )
        self.drum_kit_hlayout = QHBoxLayout()
        layout.addLayout(self.drum_kit_hlayout)

        self.drum_kit_icon = QLabel()
        self.drum_kit_icon.setPixmap(qta.icon("fa5s.drum").pixmap(40, 40))
        self.drum_kit_hlayout.addWidget(self.drum_kit_icon)

        self.drum_kit_title = QLabel("Drums")
        self.drum_kit_hlayout.addWidget(self.drum_kit_title)
        self.drum_kit_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT};
            """
        )
        self.drum_kit_current_synth = QLabel("Current Synth:")
        self.drum_kit_hlayout.addWidget(self.drum_kit_current_synth)
        self.drum_kit_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT};
            """
        )
        self.analog_synth_hlayout = QHBoxLayout()

        self.analog_synth_icon = QLabel()
        self.analog_synth_icon.setPixmap(qta.icon("msc.piano").pixmap(40, 40))
        self.analog_synth_hlayout.addWidget(self.analog_synth_icon)

        layout.addLayout(self.analog_synth_hlayout)

        self.analog_synth_title = QLabel("Analog Synth")
        self.analog_synth_hlayout.addWidget(self.analog_synth_title)
        self.analog_synth_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT_ANALOG};
            """
        )
        self.analog_synth_current_synth = QLabel("Current Synth:")
        self.analog_synth_hlayout.addWidget(self.analog_synth_current_synth)
        self.analog_synth_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {Style.ACCENT_ANALOG};
            """
        )
        self._populate_presets()
        self.midi_helper.update_digital1_tone_name.connect(self.update_digital1_tone_name)
        self.midi_helper.update_digital2_tone_name.connect(self.update_digital2_tone_name)
        self.midi_helper.update_drums_tone_name.connect(self.update_drums_tone_name)
        self.midi_helper.update_analog_tone_name.connect(self.update_analog_tone_name)
        
    def on_preset_type_changed(self, index):
        """Handle preset type selection change."""
        preset_type = self.digital_preset_type_combo.currentText()
        logging.info(f"preset_type: {preset_type}")
        if preset_type == "Digital Synth 1":
            self.midi_channel = MIDI_CHANNEL_DIGITAL1
        elif preset_type == "Digital Synth 2":
            self.midi_channel = MIDI_CHANNEL_DIGITAL2
        elif preset_type == "Drums":
            self.midi_channel = MIDI_CHANNEL_DRUMS
        elif preset_type == "Analog Synth":
            self.midi_channel = MIDI_CHANNEL_ANALOG
        self._populate_presets()
        self.update_category_combo_box_categories()

    def update_digital1_tone_name(self, tone_name):
        self.digital_synth_1_current_synth.setText(tone_name)

    def update_digital2_tone_name(self, tone_name):
        self.digital_synth_2_current_synth.setText(tone_name)

    def update_drums_tone_name(self, tone_name):
        self.drum_kit_current_synth.setText(tone_name)

    def update_analog_tone_name(self, tone_name):
        self.analog_synth_current_synth.setText(tone_name)

    def load_preset_by_program_change(self, preset_index):
        """Load a preset by program change."""
        preset_name = self.preset_combo_box.currentText()
        logging.info(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        logging.info(f"combo box program_number : {program_number}")
        
        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number)
        lsb = get_preset_parameter_value("lsb", program_number)
        pc = get_preset_parameter_value("pc", program_number)
        
        if None in [msb, lsb, pc]:
            logging.error(f"Could not retrieve preset parameters for program {program_number}")
            return
        
        logging.info(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)
        
        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def update_instrument_image(self):
        """tart up the UI with a picture"""
        image_loaded = False

        def load_and_set_image(image_path):
            """Helper function to load and set the image on the label."""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    200, Qt.TransformationMode.SmoothTransformation
                )  # Resize to 250px height
                self.image_label.setPixmap(scaled_pixmap)
                return True
            return False

        # Define paths
        default_image_path = os.path.join("resources", "presets", "presets.png")

        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def _populate_presets(self, search_text: str = ""):
        """Populate the program list with available presets."""
        if not self.preset_helper:
            return

        selected_part = self.digital_preset_type_combo.currentText()
        if selected_part in ["Digital Synth 1", "Digital Synth 2"]:
            self.preset_list = DIGITAL_PRESET_LIST
        elif selected_part == "Drums":
            self.preset_list = DRUM_KIT_LIST
        elif selected_part == "Analog Synth":
            self.preset_list = ANALOG_PRESET_LIST
        else:
            self.preset_list = DIGITAL_PRESET_LIST  # Default to digital synth 1
        # self.update_category_combo_box_categories()

        selected_category = self.category_combo_box.currentText()
        logging.info(f"Selected Category: {selected_category}")

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
            self.preset_combo_box.addItem(
                f"{preset_id} - {preset_name}", index
            )
            self.presets[preset_name] = index
        self.preset_combo_box.setCurrentIndex(
            0
        )  # Update the UI with the new program list
        self.preset_combo_box.setCurrentIndex(0)  # Select "No Category Selected" as default

    def update_category_combo_box_categories(self):
        # Update the category combo box
        categories = set(preset["category"] for preset in self.preset_list)
        self.category_combo_box.blockSignals(True)  # Block signals during update

        # Clear and update items
        self.category_combo_box.clear()
        self.category_combo_box.addItem("No Category Selected")  # Add the default option
        self.category_combo_box.addItems(sorted(categories))  # Add the sorted categories

        # Set the default selected index
        self.category_combo_box.setCurrentIndex(0)  # Select "No Category Selected" as default

        self.category_combo_box.blockSignals(False)  # Unblock signals after update

    def on_bank_changed(self, _):
        """Handle bank selection change."""
        self._populate_presets()

    def on_preset_number_changed(self, index):
        """Handle program number selection change."""
        # self.load_program()

    def load_program(self):
        """Load the selected program based on bank and number."""
        program_name = self.preset_combo_box.currentText()
        program_id = program_name[:3]
        bank_letter = program_name[0]
        bank_number = int(program_name[1:3])
        logging.info(f"combo box bank_letter : {bank_letter}")
        logging.info(f"combo box  bank_number : {bank_number}")
        if bank_letter in ["A", "B", "C", "D"]:
            program_details = get_program_by_id(program_id)
            self.update_current_synths(program_details)
        msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        logging.info(f"calculated msb, lsb, pc : {msb}, {lsb}, {pc} ")
        log_midi_info(msb, lsb, pc)
        self.midi_helper.send_bank_select_and_program_change(self.midi_channel, msb, lsb, pc)
        self.data_request()

    def update_current_synths(self, program_details: dict):
        """Update the current synth label."""
        try:
            self.digital_synth_1_current_synth.setText(program_details["digital_1"])
            self.digital_synth_2_current_synth.setText(program_details["digital_2"])
            self.drum_kit_current_synth.setText(program_details["drum"])
            self.analog_synth_current_synth.setText(program_details["analog"])
        except KeyError:
            logging.error(f"Program details missing required keys: {program_details}")
            self.digital_synth_1_current_synth.setText("Unknown")
            self.digital_synth_2_current_synth.setText("Unknown")
            self.drum_kit_current_synth.setText("Unknown")
            self.analog_synth_current_synth.setText("Unknown")

    def load_preset_temp(self, preset_number: int):
        """Load preset data and update UI."""
        if not self.preset_helper:
            return
        self.preset_helper.load_preset(preset_number)
        self.data_request()

    def _update_preset_list(self):
        """Update the preset list with available presets."""
        self._populate_presets()

    def on_category_changed(self, _):
        """Handle category selection change."""
        self._populate_presets()
