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

from typing import Optional

from PySide6.QtWidgets import (
    QVBoxLayout,
    QComboBox,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout,
    QGroupBox, QFormLayout,
)
from PySide6.QtCore import Signal, Qt
from rtmidi.midiconstants import SONG_START, SONG_STOP
import qtawesome as qta

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.programs.programs import JDXiProgramList
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.editors.helpers.program import (
    get_program_by_id,
    calculate_midi_values,
)
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.ui.editors.synth.simple import BasicEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.display.digital import DigitalTitle


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
        self.midi_helper.update_program_name.connect(self.set_current_program_name)

    def setup_ui(self):
        """set up ui elements"""
        self.setWindowTitle("Program Editor")
        self.setMinimumSize(400, 400)
        # center_widget = QWidget()
        main_vlayout = QVBoxLayout()
        title_hlayout = QHBoxLayout()

        self.title_left_group = QGroupBox()
        title_left_vlayout = QVBoxLayout()
        self.title_left_group.setLayout(title_left_vlayout)
        self.title_label = QLabel("Programs:")
        title_left_vlayout.addWidget(self.title_label)
        title_hlayout.addWidget(self.title_left_group)

        title_right_vlayout = QVBoxLayout()
        title_hlayout.addLayout(title_right_vlayout)

        main_vlayout.addLayout(title_hlayout)
        # self.setCentralWidget(center_widget)
        self.setLayout(main_vlayout)
        self.setStyleSheet(JDXiStyle.EDITOR)

        self.title_label.setStyleSheet(JDXiStyle.EDITOR_TITLE_LABEL)
        self.midi_helper.update_tone_name.connect(
            lambda title, synth_type: self.set_instrument_title_label(title, synth_type))

        self.file_label = DigitalTitle("No file loaded")
        title_left_vlayout.addWidget(self.file_label)
        title_left_vlayout.addStretch()

        # Image display
        self.title_group = QGroupBox()
        title_image_layout = QFormLayout()
        self.title_group.setLayout(title_image_layout)
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )  # Center align the image
        title_image_layout.addWidget(self.image_label)
        title_right_vlayout.addWidget(self.title_group)
        self.update_instrument_image()

        self.program_label = QLabel("Program")
        main_vlayout.addWidget(self.program_label)

        # Program number selection combo box
        self.program_number_combo_box = QComboBox()
        self.program_number_combo_box.addItems([f"{i:02}" for i in range(1, 65)])
        self.program_number_combo_box.currentIndexChanged.connect(
            self.on_program_number_changed
        )
        main_vlayout.addWidget(self.program_number_combo_box)

        self.genre_label = QLabel("Genre")
        main_vlayout.addWidget(self.genre_label)

        # Genre selection combo box
        self.genre_combo_box = QComboBox()
        self.genre_combo_box.addItem("No Genre Selected")
        genres = set(program["genre"] for program in JDXiProgramList.PROGRAM_LIST)
        self.genre_combo_box.addItems(sorted(genres))
        self.genre_combo_box.currentIndexChanged.connect(self.on_genre_changed)
        main_vlayout.addWidget(self.genre_combo_box)

        self.bank_label = QLabel("Bank")
        main_vlayout.addWidget(self.bank_label)

        # Bank selection combo box
        self.bank_combo_box = QComboBox()
        self.bank_combo_box.addItem("No Bank Selected")
        self.bank_combo_box.addItems(["A", "B", "C", "D", "E", "F", "G", "H"])
        self.bank_combo_box.currentIndexChanged.connect(self.on_bank_changed)
        main_vlayout.addWidget(self.bank_combo_box)

        # Load button
        self.load_button = QPushButton(
            qta.icon("ph.folder-notch-open-fill", color=JDXiStyle.FOREGROUND),
            "Load Program",
        )
        self.load_button.clicked.connect(self.load_program)
        main_vlayout.addWidget(self.load_button)
        self.setLayout(title_hlayout)

        # Transport controls area
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
        # left_layout.addWidget(transport_group) # I guess we need to send the MIDI clock also for midi sart to work

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
        self.digital_synth_1_current_synth = QLabel("Current Synth:")
        self.digital_synth_1_hlayout.addWidget(self.digital_synth_1_current_synth)
        self.digital_synth_1_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.digital_synth_2_hlayout = QHBoxLayout()

        self.digital_synth_2_icon = QLabel()
        self.digital_synth_2_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_icon)

        main_vlayout.addLayout(self.digital_synth_2_hlayout)

        self.digital_synth_2_title = QLabel("Digital Synth 2")
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_title)
        self.digital_synth_2_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.digital_synth_2_current_synth = QLabel("Current Synth:")
        self.digital_synth_2_hlayout.addWidget(self.digital_synth_2_current_synth)
        self.digital_synth_2_current_synth.setStyleSheet(
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
        self.drum_kit_current_synth = QLabel("Current Synth:")
        self.drum_kit_hlayout.addWidget(self.drum_kit_current_synth)
        self.drum_kit_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT};
            """
        )
        self.analog_synth_hlayout = QHBoxLayout()
        main_vlayout.addLayout(self.analog_synth_hlayout)
        main_vlayout.addStretch()

        self.analog_synth_icon = QLabel()
        self.analog_synth_icon.setPixmap(
            qta.icon("msc.piano", color=JDXiStyle.FOREGROUND).pixmap(40, 40)
        )
        self.analog_synth_hlayout.addWidget(self.analog_synth_icon)

        self.analog_synth_title = QLabel("Analog Synth")
        self.analog_synth_hlayout.addWidget(self.analog_synth_title)
        self.analog_synth_title.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT_ANALOG};
            """
        )
        self.analog_synth_current_synth = QLabel("Current Synth:")
        self.analog_synth_hlayout.addWidget(self.analog_synth_current_synth)
        self.analog_synth_current_synth.setStyleSheet(
            f"""
                font-size: 16px;
                font-weight: bold;
                color: {JDXiStyle.ACCENT_ANALOG};
            """
        )
        self.populate_programs()

    def set_current_program_name(self, program_name: str, synth_type: str = None) -> None:
        """
        Set the current program name in the file label
        :param program_name: str
        :param synth_type: str (optional), discarded for now
        :return: None
        """
        if self.file_label:
            self.file_label.setText(program_name)
        else:
            log.message("File label not initialized.")

    def start_playback(self):
        """Start playback of the MIDI file."""
        self.midi_helper.send_raw_message([SONG_START])

    def stop_playback(self):
        """Stop playback of the MIDI file."""
        self.midi_helper.send_raw_message([SONG_STOP])

    def populate_programs(self):
        """Populate the program list with available presets."""
        if not self.preset_helper:
            return

        selected_bank = self.bank_combo_box.currentText()
        selected_genre = self.genre_combo_box.currentText()

        log.parameter("selected bank", selected_bank)
        log.parameter("selected genre", selected_genre)

        self.program_number_combo_box.clear()
        self.programs.clear()

        filtered_list = [  # Filter programs based on bank and genre
            program
            for program in JDXiProgramList.PROGRAM_LIST
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

    def add_user_banks(self, filtered_list: list, bank: str) -> None:
        """Add user banks to the program list.
        :param filtered_list: list
        :param bank: str
        """
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
        msb, lsb, pc = calculate_midi_values(bank_letter, bank_number)
        log.message("calculated msb, lsb, pc :")
        log.parameter("msb", msb)
        log.parameter("lsb", lsb)
        log.parameter("pc", pc)
        log_midi_info(msb, lsb, pc)
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        self.data_request()

    def update_current_synths(self, program_details: dict) -> None:
        """Update the current synth label.
        :param program_details: dict
        """
        try:
            self.digital_synth_1_current_synth.setText(program_details["digital_1"])
            self.digital_synth_2_current_synth.setText(program_details["digital_2"])
            self.drum_kit_current_synth.setText(program_details["drum"])
            self.analog_synth_current_synth.setText(program_details["analog"])
        except KeyError:
            log.message(f"Program details missing required keys: {program_details}")
            self.digital_synth_1_current_synth.setText("Unknown")
            self.digital_synth_2_current_synth.setText("Unknown")
            self.drum_kit_current_synth.setText("Unknown")
            self.analog_synth_current_synth.setText("Unknown")

    def load_preset(self, program_number: int) -> None:
        """Load preset data and update UI.
        :param program_number: int
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
