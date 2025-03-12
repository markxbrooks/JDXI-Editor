"""
ProgramEditor Module

This module defines the `ProgramEditor` class, a PySide6-based GUI for managing and selecting MIDI programs.
It allows users to browse, filter, and load programs based on bank, genre, and program number.
The class also facilitates MIDI integration by sending Program Change (PC) and Bank Select (CC#0, CC#32) messages.

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
from typing import Optional, Dict

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtCore import Signal, Qt

from jdxi_manager.midi.data.programs.programs import PROGRAM_LIST
from jdxi_manager.midi.data.constants import MIDI_CHANNEL_PROGRAMS
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.midi.preset.handler import PresetHandler
from jdxi_manager.ui.style import Style


def get_program_index_by_id(program_id: str) -> Optional[int]:
    """Retrieve the index of a program by its ID from PROGRAM_LIST."""
    logging.info(f"Getting program index for {program_id}")
    for index, program in enumerate(PROGRAM_LIST):
        if program["id"] == program_id:
            logging.info(f"index for {program_id} is {index}")
            return index - 1  # convert to 0-based index
    logging.warning(f"Program with ID {program_id} not found.")
    return None


def get_program_by_id(program_id: str) -> Optional[Dict[str, str]]:
    """Retrieve a program by its ID from PROGRAM_LIST."""
    for index, program in enumerate(PROGRAM_LIST):
        if program["id"] == program_id:
            return program
    logging.warning(f"Program with ID {program_id} not found.")
    return None


def calculate_midi_values(bank, program_number):
    """Calculate MSB, LSB, and PC based on bank and program number."""
    if bank in ["A", "B"]:
        msb = 85
        lsb = 64
        pc = program_number if bank == "A" else program_number + 64
    elif bank in ["C", "D"]:
        msb = 85
        lsb = 65
        pc = program_number if bank == "C" else program_number + 64
    elif bank in ["E", "F"]:
        msb = 85
        lsb = 0
        pc = program_number if bank == "E" else program_number + 64
    elif bank in ["G", "H"]:
        msb = 85
        lsb = 1
        pc = program_number if bank == "G" else program_number + 64
    else:
        msb, lsb, pc = None, None, None

    # Ensure PC is within range
    if not (0 <= pc <= 127):
        logging.error(f"Invalid Program Change value: {pc}")
        raise ValueError(f"Program Change value {pc} is out of range")

    return msb, lsb, pc


def calculate_index(bank, program_number: int):
    """Calculate the index based on bank and program number."""
    bank_offset = (ord(bank) - ord("A")) * 64
    program_index = program_number - 1
    return bank_offset + program_index


def log_midi_info(msb, lsb, pc):
    """Helper function to log MIDI information."""
    logging.info(f"msb: {msb}, lsb: {lsb}, pc: {pc}")


def log_program_info(program_name, program_id=None, program_details=None):
    """Helper function to log program info."""
    logging.info(f"load_program: program_name: {program_name}")
    if program_id:
        logging.info(f"load_program: program_id: {program_id}")
    if program_details:
        logging.info(f"load_program: program_details: {program_details}")


def get_msb_lsb_pc(program_number: int):
    """Get MSB, LSB, and PC based on bank and program number."""
    msb, lsb, pc = (
        PROGRAM_LIST[program_number]["msb"],  # Tone Bank Select MSB (CC# 0)
        PROGRAM_LIST[program_number]["lsb"],  # Tone Bank Select LSB (CC# 32)
        PROGRAM_LIST[program_number]["pc"],  # Tone Program Number (PC)
    )
    return int(msb), int(lsb), int(pc)


class ProgramEditor(QMainWindow):
    """ Program Editor Window """
    program_changed = Signal(int, str, int)  # (channel, preset_name, program_number)

    def __init__(
        self,
        midi_helper: Optional[MIDIHelper] = None,
        parent: Optional[QWidget] = None,
        preset_handler: PresetHandler = None,
    ):
        super().__init__(parent)
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
        self.midi_helper = midi_helper
        self.channel = MIDI_CHANNEL_PROGRAMS  # Default MIDI channel: 16 for programs?
        self.preset_type = None
        self.preset_handler = preset_handler
        self.programs = {}  # Maps program names to numbers
        self.setup_ui()
        self.populate_programs()
        self.show()

    def setup_ui(self):
        self.setWindowTitle("Program Editor")
        self.setMinimumSize(400, 400)
        center_widget = QWidget()
        layout = QVBoxLayout()
        self.setCentralWidget(center_widget)
        center_widget.setLayout(layout)
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
        layout.addWidget(self.image_label)
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
        self.load_button = QPushButton("Load Program")
        self.load_button.clicked.connect(self.load_program)
        layout.addWidget(self.load_button)
        self.setLayout(layout)

        self.digital_synth_1_hlayout = QHBoxLayout()
        layout.addLayout(self.digital_synth_1_hlayout)

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

    def update_instrument_image(self):
        """ tart up the UI with a picture """
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

        # Get the selected bank and genre
        bank = self.bank_combo_box.currentText()
        selected_genre = self.genre_combo_box.currentText()

        print(f"Selected bank: {bank}, Genre: {selected_genre}")

        # Clear the current program list
        self.program_number_combo_box.clear()
        self.programs.clear()

        # Filter programs based on bank and genre
        updated_list = [
            program for program in PROGRAM_LIST
            if (bank == "No Bank Selected" or program["id"][0] == bank) and
               (selected_genre == "No Genre Selected" or program["genre"] == selected_genre)
        ]

        # Add programs to the combo box
        for program in updated_list:
            program_name = program["name"]
            program_id = program["id"]
            print(f"Adding program: {program_name} with ID: {program_id}")
            index = len(self.programs)  # Use the current number of programs
            self.program_number_combo_box.addItem(f"{program_id} - {program_name}", index)
            self.programs[program_name] = index

        # Handle user banks if necessary
        if bank in ["No Bank Selected", "E", "F", "G", "H"] and selected_genre == "No Genre Selected":
            self.add_user_banks(updated_list, bank)

        # Update the UI with the new program list
        self.program_number_combo_box.setCurrentIndex(0)

    def add_user_banks(self, updated_list, bank):
        """Add user banks to the program list."""
        user_banks = ["E", "F", "G", "H"]
        for user_bank in user_banks:
            if bank == "No Bank Selected" or bank == user_bank:
                for i in range(1, 65):
                    msb, lsb, pc = calculate_midi_values(user_bank, i-1) # 0-based (0-127)
                    program = {
                        "id": f"{user_bank}{i:02}",
                        "name": f"User bank {user_bank} program {i:02}",
                        "genre": "User",
                        "msb": msb,
                        "lsb": lsb,
                        "pc": pc,
                    }
                    updated_list.append(program)
                    program_name = program["name"]
                    program_id = program["id"]
                    index = len(self.programs)
                    self.program_number_combo_box.addItem(f"{program_id} - {program_name}", index)
                    self.programs[program_name] = index

    def on_bank_changed(self, index):
        """Handle bank selection change."""
        self.populate_programs()

    def on_program_number_changed(self, index):
        """Handle program number selection change."""
        # self.load_program()

    def load_program(self):
        """Load the selected program based on bank and number."""
        program_name = self.program_number_combo_box.currentText()
        program_id = program_name[:3]

        # Logging program details
        log_program_info(program_name, program_id)

        # Get program list number and details
        program_list_number = get_program_index_by_id(program_id)
        program_details = get_program_by_id(program_id)

        # Logging program index and details
        log_program_info(program_name, program_list_number, program_details)

        # Get MSB, LSB, and PC
        msb, lsb, pc = get_msb_lsb_pc(program_list_number)

        # Logging MSB, LSB, PC values
        log_midi_info(msb, lsb, pc)

        # Send MIDI Bank Select and Program Change messages
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        self.update_current_synths(program_details)

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

    def _update_program_list(self):
        """Update the program list with available presets."""
        self.populate_programs()

    def _update_program_display(self, program_name: str, program_number: int):
        """Update the program display with the selected program name and number."""
        self.program_number_combo_box.setCurrentText(program_name)

    def on_genre_changed(self, _):
        """Handle genre selection change."""
        self.populate_programs()
