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
    QHBoxLayout, QGroupBox,
)
from PySide6.QtCore import Signal, Qt
from rtmidi.midiconstants import SONG_START, SONG_STOP
import qtawesome as qta

from jdxi_editor.midi.data.programs.programs import PROGRAM_LIST
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_PROGRAMS
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.midi.sysex.requests import PROGRAM_TONE_NAME_PARTIAL_REQUESTS
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.editors.helpers.program import (
    get_program_by_id,
    calculate_midi_values,
    log_midi_info
)
from jdxi_editor.ui.style import Style


class ProgramEditor(SynthEditor):
    """Program Editor Window"""

    program_changed = Signal(int, str, int)  # (channel, preset_name, program_number)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
        preset_handler: PresetHelper = None,
    ):
        super().__init__()
        self.setWindowFlag(Qt.Window)
        self.midi_helper = midi_helper
        self.preset_handler = preset_handler
        self.channel = (
            MIDI_CHANNEL_PROGRAMS  # Default MIDI channel: 16 for programs, 0-based
        )
        self.midi_requests = PROGRAM_TONE_NAME_PARTIAL_REQUESTS
        self.layout = None
        self.genre_label = None
        self.program_number_combo_box = None
        self.bank_combo_box = None
        self.load_button = None
        self.save_button = None
        self.image_label = None
        self.title_label = None
        self.bank_label = None
        self.program_label = None
        self.genre_combo_box = None
        self.preset_type = None
        self.programs = {}  # Maps program names to numbers
        self.setup_ui()

    def setup_ui(self):
        """set up ui elements"""
        self.setWindowTitle("Program Editor")
        self.setMinimumSize(400, 400)
        # center_widget = QWidget()
        layout = QVBoxLayout()
        # self.setCentralWidget(center_widget)
        self.setLayout(layout)
        self.setStyleSheet(Style.JDXI_EDITOR)

        self.title_label = QLabel("Programs:")
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

        self.program_label = QLabel("Program")
        layout.addWidget(self.program_label)

        # Program number selection combo box
        self.program_number_combo_box = QComboBox()
        self.program_number_combo_box.addItems([f"{i:02}" for i in range(1, 65)])
        self.program_number_combo_box.currentIndexChanged.connect(
            self.on_program_number_changed
        )
        layout.addWidget(self.program_number_combo_box)

        self.genre_label = QLabel("Genre")
        layout.addWidget(self.genre_label)

        # Genre selection combo box
        self.genre_combo_box = QComboBox()
        self.genre_combo_box.addItem("No Genre Selected")
        genres = set(program["genre"] for program in PROGRAM_LIST)
        self.genre_combo_box.addItems(sorted(genres))
        self.genre_combo_box.currentIndexChanged.connect(self.on_genre_changed)
        layout.addWidget(self.genre_combo_box)

        self.bank_label = QLabel("Bank")
        layout.addWidget(self.bank_label)

        # Bank selection combo box
        self.bank_combo_box = QComboBox()
        self.bank_combo_box.addItem("No Bank Selected")
        self.bank_combo_box.addItems(["A", "B", "C", "D", "E", "F", "G", "H"])
        self.bank_combo_box.currentIndexChanged.connect(self.on_bank_changed)
        layout.addWidget(self.bank_combo_box)

        # Load button
        self.load_button = QPushButton(qta.icon("ph.folder-notch-open-fill"), "Load Program")
        self.load_button.clicked.connect(self.load_program)
        layout.addWidget(self.load_button)
        self.setLayout(layout)

        # Transport controls area
        transport_group = QGroupBox("Transport")
        transport_layout = QHBoxLayout()

        self.start_button = QPushButton(qta.icon("ri.play-line"), "Play")
        self.stop_button = QPushButton(qta.icon("ri.stop-line"), "Stop")
        self.start_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)

        transport_layout.addWidget(self.start_button)
        transport_layout.addWidget(self.stop_button)
        transport_group.setLayout(transport_layout)
        layout.addWidget(transport_group)

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

        self.digital_synth_2_icon = QLabel()
        self.digital_synth_2_icon.setPixmap(qta.icon("msc.piano").pixmap(40, 40))
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_icon)

        layout.addLayout(self.digital_synth_2_hlayout)

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
        layout.addLayout(self.analog_synth_hlayout)

        self.analog_synth_icon = QLabel()
        self.analog_synth_icon.setPixmap(qta.icon("msc.piano").pixmap(40, 40))
        self.analog_synth_hlayout.addWidget(self.analog_synth_icon)

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
        self.populate_programs()

    def start_playback(self):
        self.midi_helper.send_raw_message([SONG_START])

    def stop_playback(self):
        self.midi_helper.send_raw_message([SONG_STOP])

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
        default_image_path = os.path.join("resources", "programs", "programs.png")

        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def populate_programs(self):
        """Populate the program list with available presets."""
        if not self.preset_handler:
            return

        selected_bank = self.bank_combo_box.currentText()
        selected_genre = self.genre_combo_box.currentText()
        logging.info(f"Selected bank: {selected_bank}, Genre: {selected_genre}")

        self.program_number_combo_box.clear()
        self.programs.clear()

        filtered_list = [  # Filter programs based on bank and genre
            program
            for program in PROGRAM_LIST
            if (selected_bank in ["No Bank Selected", program["id"][0]])
            and (selected_genre in ["No Genre Selected", program["genre"]])
        ]

        for program in filtered_list:  # Add programs to the combo box
            program_name = program["name"]
            program_id = program["id"]
            index = len(self.programs)  # Use the current number of programs
            self.program_number_combo_box.addItem(
                f"{program_id} - {program_name}", index
            )
            self.programs[program_name] = index

        if (
            selected_bank in ["No Bank Selected", "E", "F", "G", "H"]
            and selected_genre == "No Genre Selected"
        ):
            self.add_user_banks(
                filtered_list, selected_bank
            )  # Handle user banks if necessary

        self.program_number_combo_box.setCurrentIndex(
            0
        )  # Update the UI with the new program list

    def add_user_banks(self, filtered_list, bank):
        """Add user banks to the program list."""
        user_banks = ["E", "F", "G", "H"]
        for user_bank in user_banks:
            if bank in ["No Bank Selected", user_bank]:
                for i in range(1, 65):
                    msb, lsb, pc = calculate_midi_values(
                        user_bank, i - 1
                    )  # 0-based (0-127)
                    program = {
                        "id": f"{user_bank}{i:02}",
                        "name": f"User bank {user_bank} program {i:02}",
                        "genre": "User",
                        "msb": msb,
                        "lsb": lsb,
                        "pc": pc,
                    }
                    filtered_list.append(program)
                    program_name = program["name"]
                    program_id = program["id"]
                    index = len(self.programs)
                    self.program_number_combo_box.addItem(
                        f"{program_id} - {program_name}", index
                    )
                    self.programs[program_name] = index

    def on_bank_changed(self, _):
        """Handle bank selection change."""
        self.populate_programs()

    def on_program_number_changed(self, index):
        """Handle program number selection change."""
        # self.load_program()

    def load_program(self):
        """Load the selected program based on bank and number."""
        program_name = self.program_number_combo_box.currentText()
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
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
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

    def load_preset(self, program_number: int):
        """Load preset data and update UI."""
        if not self.preset_handler:
            return
        self.preset_handler.load_preset(program_number)
        self.data_request()

    def _update_program_list(self):
        """Update the program list with available presets."""
        self.populate_programs()

    def on_genre_changed(self, _):
        """Handle genre selection change."""
        self.populate_programs()
