"""
JD-Xi Manager UI setup.

This class defines the main user interface for the JD-Xi Manager application, inheriting from QMainWindow. It handles the creation of the UI elements, including the main layout, menus, status bar, and MIDI indicators. It also provides functionality for displaying and managing synth presets, favorites, and MIDI connectivity.

Key Features:
- Sets up a frameless window with a customizable layout.
- Initializes MIDI helper and indicators for MIDI input/output.
- Loads and displays a digital font for instrument displays.
- Allows users to manage and load favorite presets.
- Displays a virtual piano keyboard in the status bar.
- Integrates with MIDIHelper for MIDI communication.
- Loads and saves application settings and preferences.

Methods:
    - __init__: Initializes the UI, settings, MIDI components, and layout.
    - _create_main_layout: Sets up the central layout for displaying instrument images and overlays.

"""

import os
import logging
import re

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLabel,
    QPushButton,
    QGridLayout,
)
from PySide6.QtCore import Qt, QSettings, QRect
from PySide6.QtGui import (
    QAction,
    QFontDatabase,
)

from jdxi_editor.midi.data.editor.data import (
    DigitalSynthData,
    DrumsSynthData,
    AnalogSynthData,
)
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.ui.editors.helpers.program import get_preset_list_number_by_name
from jdxi_editor.ui.image.instrument import draw_instrument_pixmap
from jdxi_editor.ui.style.style import Style
from jdxi_editor.ui.style.helpers import (
    generate_sequencer_button_style,
    toggle_button_style,
)
from jdxi_editor.ui.widgets.button import SequencerSquare
from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
from jdxi_editor.ui.widgets.button.channel import ChannelButton
from jdxi_editor.ui.widgets.indicator import MIDIIndicator, LEDIndicator
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.ui.widgets.wheel.mod import ModWheel
from jdxi_editor.ui.widgets.wheel.pitch import PitchWheel
from jdxi_editor.ui.windows.jdxi.containers.arpeggiator import add_arpeggiator_buttons
from jdxi_editor.ui.windows.jdxi.containers.effects import add_effects_container
from jdxi_editor.ui.windows.jdxi.containers.octave import add_octave_buttons
from jdxi_editor.ui.windows.jdxi.containers.overlay import add_overlaid_controls
from jdxi_editor.ui.windows.jdxi.containers.parts import create_parts_container
from jdxi_editor.ui.windows.jdxi.containers.program import add_program_container
from jdxi_editor.ui.windows.jdxi.containers.sequencer import add_sequencer_container
from jdxi_editor.ui.windows.jdxi.containers.sliders import add_slider_container
from jdxi_editor.ui.windows.jdxi.containers.title import add_title_container
from jdxi_editor.ui.windows.jdxi.containers.tone import add_tone_container
from jdxi_editor.ui.windows.jdxi.dimensions import JDXI_MARGIN, JDXI_DISPLAY_WIDTH, JDXI_WIDTH, JDXI_DISPLAY_HEIGHT, \
    JDXI_HEIGHT


class JdxiUi(QMainWindow):
    """JDXI UI setup, with little or no actual functionality, which is superclassed"""

    def __init__(self):
        super().__init__()
        # Add preset & program tracking
        self.digital1_data = DigitalSynthData(synth_num=1)
        self.digital2_data = DigitalSynthData(synth_num=2)
        self.drums_data = DrumsSynthData()
        self.analog_data = AnalogSynthData()
        self.synth_data_map = {
            SynthType.DIGITAL_1: DigitalSynthData(synth_num=1),
            SynthType.DIGITAL_2: DigitalSynthData(synth_num=2),
            SynthType.DRUMS: DrumsSynthData(),
            SynthType.ANALOG: AnalogSynthData(),
        }

        self.sequencer_buttons = []
        self.current_program_bank_letter = "A"
        self.program_helper = None
        self.current_tone_number = 1
        self.current_tone_name = "Init Tone"
        self.current_program_number = 1
        self.current_program_name = "Init Program"
        self.current_digital1_tone_name = "Init Tone"
        self.current_digital2_tone_name = "Init Tone"
        self.current_analog_tone_name = "Init Tone"
        self.current_drums_tone_name = "Init Tone"
        # Initialize synth preset_type
        self.current_synth_type = SynthType.DIGITAL_1
        # Initialize octave
        self.current_octave = 0  # Initialize octave tracking first

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.log_file = None
        self.setWindowTitle("JD-Xi Manager")
        self.setMinimumSize(JDXIDimensions.WIDTH, JDXIDimensions.HEIGHT)
        # Store window dimensions
        self.width = JDXIDimensions.WIDTH
        self.height = JDXIDimensions.HEIGHT
        self.margin = JDXIDimensions.MARGIN
        # Store display coordinates as class variables
        self.display_x = JDXIDimensions.DISPLAY_X
        self.display_y = JDXIDimensions.DISPLAY_Y
        self.display_width = JDXIDimensions.DISPLAY_WIDTH
        self.display_height = JDXIDimensions.DISPLAY_HEIGHT
        self.digital_font_family = None

        # Initialize MIDI helper
        self.midi_helper = MidiIOHelper()

        # Set black background for entire application
        self.setStyleSheet(Style.JDXI_TRANSPARENT)

        # Load custom font
        self._load_digital_font()

        # Create UI
        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_layout()
        self._create_parts_menu()
        self._create_effects_menu()
        self._create_other_menu()
        self._create_help_menu()

        # Load settings
        self.settings = QSettings("mabsoft", "jdxi_editor")
        self._load_settings()

        # Show window
        self.show()

        # Add piano keyboard at bottom
        self.piano_keyboard = PianoKeyboard(parent=self)
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # Create display label
        self.display_label = QLabel()
        self.display_label.setMinimumSize(220, 100)  # Adjust size as needed

        # Add display to layout
        if hasattr(self, "main_layout"):
            self.main_layout.addWidget(self.display_label)

        # Add to status bar before piano keyboard
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # Load last used preset settings
        # self._load_last_preset()

        # Create favorite buttons container
        self.favorites_widget = QWidget()
        favorites_layout = QVBoxLayout(self.favorites_widget)
        favorites_layout.setSpacing(4)
        favorites_layout.setContentsMargins(0, 0, 0, 0)

        # Create favorite buttons
        self.favorite_buttons = []
        for i in range(4):  # Create 4 favorite slots
            button = FavoriteButton(i, self.midi_helper)
            button.clicked.connect(lambda checked, b=button: self._load_favorite(b))
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda pos, b=button: self._show_favorite_context_menu(pos, b)
            )
            favorites_layout.addWidget(button)
            self.favorite_buttons.append(button)

        # Add to status bar
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # Load saved favorites
        self._load_saved_favorites()

        # Initialize current preset index
        self.current_preset_index = 0

        # Initialize current preset index
        self.current_preset_index = 0
        self.old_pos = None

    def _create_main_layout(self):
        """Create the main dashboard"""
        central = QWidget()
        self.setCentralWidget(central)

        # Single layout to hold the image and overlays
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create container for image and overlays
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().setContentsMargins(0, 0, 0, 0)

        # Store reference to image label
        self.image_label = QLabel()
        self.image_label.setPixmap(draw_instrument_pixmap())
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.layout().addWidget(self.image_label)

        # Add overlaid controls
        self.digital_display = add_overlaid_controls(container, self)
        add_title_container(container)
        self.parts_container, self.part_buttons = create_parts_container(
            parent_widget=self,
            display_x=self.display_x,
            display_y=self.display_y,
            display_width=self.display_width,
            window_height=self.height,
            on_open_d1=self._open_digital_synth1,
            on_open_d2=self._open_digital_synth2,
            on_open_drums=self._open_drums,
            on_open_analog=self._open_analog_synth,
            on_open_arp=self._open_arpeggiator,
            on_select_synth=self._select_synth,
        )

        self.digital1_button = self.part_buttons["digital1"]
        self.digital2_button = self.part_buttons["digital2"]
        self.analog_button = self.part_buttons["analog"]
        self.drums_button = self.part_buttons["drums"]
        self.arp_button = self.part_buttons["arp"]

        self.octave_down, self.octave_up = add_octave_buttons(
            container, self.height, self.width, self._send_octave
        )
        self.arpeggiator_button, self.key_hold_button = add_arpeggiator_buttons(
            container, self.height, self.width
        )
        self.vocal_effects_button, self.effects_button = add_effects_container(
            container, self._open_vocal_fx, self._open_effects, self.width, self.margin
        )
        add_program_container(
            container, self._create_program_buttons_row, self.width, self.margin
        )
        add_tone_container(
            container, self._create_tone_buttons_row, self.width, self.margin
        )
        self.sequencer_buttons = add_sequencer_container(
            container,
            self.width,
            self.margin,
            self._create_favorite_button_row,
            midi_helper=self.midi_helper,
            on_context_menu=self._show_favorite_context_menu,
            on_save_favorite=self._save_favorite,
        )
        add_slider_container(container, self.midi_helper, self.width, self.margin)
        layout.addWidget(container)

        # Initialize current preset index
        self.current_preset_index = 0

    def _create_program_buttons_row(self):
        # create program navigation buttons
        self.program_down_button = QPushButton("-")
        program_spacer = QLabel(" ")
        self.program_up_button = QPushButton("+")

        # create program up button
        self.program_up_button.setFixedSize(25, 25)
        self.program_up_button.setStyleSheet(Style.JDXI_BUTTON_ROUND_SMALL)

        # create program down button
        self.program_down_button.setFixedSize(25, 25)
        self.program_down_button.setStyleSheet(Style.JDXI_BUTTON_ROUND_SMALL)

        # create program layout
        program_layout = QHBoxLayout()
        program_layout.addStretch()
        program_layout.addWidget(self.program_down_button)
        program_layout.addWidget(program_spacer)
        program_layout.addWidget(self.program_up_button)
        program_layout.addStretch()
        return program_layout

    def _create_tone_buttons_row(self):
        # Create Tone navigation buttons
        self.tone_down_button = QPushButton("-")
        tone_spacer = QLabel(" ")
        self.tone_up_button = QPushButton("+")

        # Calculate size for tone buttons
        tone_button_diameter = 25

        # Create tone up button
        self.tone_up_button.setFixedSize(tone_button_diameter, tone_button_diameter)
        self.tone_up_button.setStyleSheet(Style.JDXI_BUTTON_ROUND_SMALL)

        # Create tone down button
        self.tone_down_button.setFixedSize(tone_button_diameter, tone_button_diameter)
        self.tone_down_button.setStyleSheet(Style.JDXI_BUTTON_ROUND_SMALL)

        # Connect buttons to functions
        self.tone_down_button.clicked.connect(self._previous_tone)
        self.tone_up_button.clicked.connect(self._next_tone)

        button_label_layout = QHBoxLayout()
        button_label_layout.addStretch()
        button_label_layout.addWidget(tone_spacer)
        button_label_layout.addStretch()
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.tone_down_button)
        button_layout.addWidget(tone_spacer)
        button_layout.addWidget(self.tone_up_button)
        button_layout.addStretch()
        return button_layout

    def _create_favorite_button_row(self):
        """Create address row with label and circular button"""
        text = "Favorites"
        row = QHBoxLayout()
        row.setSpacing(10)

        # Add label with color based on text
        label = QLabel(text)
        if text == "Analog Synth":
            label.setStyleSheet(Style.JDXI_LABEL_ANALOG_SYNTH_PART)
        else:
            label.setStyleSheet(Style.JDXI_LABEL_SYNTH_PART)
        # Add spacer to push button to right
        row.addStretch()
        # Add button
        self.favourites_button = QPushButton()
        self.favourites_button.setFixedSize(30, 30)
        self.favourites_button.setCheckable(True)
        # Style the button with brighter hover/border_pressed/selected  states
        self.favourites_button.setStyleSheet(Style.JDXI_BUTTON_ROUND)
        row.addWidget(self.favourites_button)
        return row

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # Add MIDI file action
        midi_file_action = QAction("MIDI File", self)
        midi_file_action.triggered.connect(lambda: self.show_editor("midi_file"))
        file_menu.addAction(midi_file_action)

        load_program_action = QAction("Load Program...", self)
        load_program_action.triggered.connect(lambda: self.show_editor("program"))
        file_menu.addAction(load_program_action)

        load_preset_action = QAction("Load Preset...", self)
        load_preset_action.triggered.connect(lambda: self.show_editor("preset"))
        file_menu.addAction(load_preset_action)

        load_action = QAction("Load Patch...", self)
        load_action.triggered.connect(self._load_patch)
        file_menu.addAction(load_action)

        save_action = QAction("Save Patch...", self)
        save_action.triggered.connect(self._save_patch)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        midi_config_action = QAction("MIDI Configuration...", self)
        midi_config_action.triggered.connect(self._show_midi_config)
        edit_menu.addAction(midi_config_action)

    def _create_parts_menu(self):
        """Create editors menu"""
        self.parts_menu = self.menuBar().addMenu("Parts")

        digital1_action = QAction("Digital Synth 1", self)
        digital1_action.triggered.connect(self._open_digital_synth1)
        self.parts_menu.addAction(digital1_action)

        digital2_action = QAction("Digital Synth 2", self)
        digital2_action.triggered.connect(self._open_digital_synth2)
        self.parts_menu.addAction(digital2_action)

        drums_action = QAction("Drums", self)
        drums_action.triggered.connect(self._open_drums)
        self.parts_menu.addAction(drums_action)

        analog_action = QAction("Analog Synth", self)
        analog_action.triggered.connect(self._open_analog_synth)

        self.parts_menu.addAction(analog_action)

    def _create_effects_menu(self):
        """Create editors menu"""
        self.effects_menu = self.menuBar().addMenu("Effects")

        effects_action = QAction("Effects", self)
        effects_action.triggered.connect(self._open_effects)
        self.effects_menu.addAction(effects_action)

        vocal_effects_action = QAction("Vocal FX", self)
        vocal_effects_action.triggered.connect(self._open_vocal_fx)
        self.effects_menu.addAction(vocal_effects_action)

    def _create_other_menu(self):
        # Create editors menu
        editors_menu = self.menuBar().addMenu("Other")

        arpeggiator_action = editors_menu.addAction("Arpeggiator")
        arpeggiator_action.triggered.connect(lambda: self.show_editor("arpeggio"))

        sequencer_action = editors_menu.addAction("Pattern Sequencer")
        sequencer_action.triggered.connect(lambda: self.show_editor("pattern"))

    def _create_debug_menu(self):
        # Add debug menu
        self.debug_menu = self.menuBar().addMenu("Debug")

        # Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._open_midi_debugger)
        self.debug_menu.addAction(midi_debugger_action)

        # Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._open_midi_message_debug)
        self.debug_menu.addAction(midi_monitor_action)

        # Add log viewer action
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        self.debug_menu.addAction(log_viewer_action)

    def _create_help_menu(self):
        menubar = self.menuBar()

        # Help menu
        self.help_menu = menubar.addMenu("Help")
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        self.help_menu.addAction(log_viewer_action)

        # Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._open_midi_debugger)
        self.help_menu.addAction(midi_debugger_action)

        # Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._open_midi_message_debug)
        self.help_menu.addAction(midi_monitor_action)

    def _create_status_bar(self):
        """Create status bar with MIDI indicators"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(Style.JDXI_TRANSPARENT)
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.addStretch()
        pitch_label = QLabel("Pitch")
        pitch_label.setStyleSheet(Style.JDXI_TRANSPARENT)
        label_layout.addWidget(pitch_label)
        label_layout.addStretch()
        mod_label = QLabel("Mod")
        mod_label.setStyleSheet(Style.JDXI_TRANSPARENT)
        label_layout.addWidget(mod_label)
        label_layout.addStretch()
        wheel_layout = QHBoxLayout()
        wheel_layout.addStretch()
        # Create a pitch wheel
        pitch_wheel = PitchWheel(midi_helper=self.midi_helper, bidirectional=True)
        pitch_wheel.setMinimumWidth(20)
        wheel_layout.addWidget(pitch_wheel)
        wheel_layout.addStretch()
        # Create mod wheel
        mod_wheel = ModWheel(midi_helper=self.midi_helper, bidirectional=True)
        mod_wheel.setMinimumWidth(20)
        wheel_layout.addWidget(mod_wheel)
        wheel_layout.addStretch()

        # Create MIDI indicators
        self.midi_in_indicator = LEDIndicator()
        self.midi_out_indicator = LEDIndicator()

        # Add labels and indicators
        midi_indicator_container = QWidget()
        midi_indicator_container_vbox = QVBoxLayout()
        midi_indicator_container.setLayout(midi_indicator_container_vbox)
        status_bar.addPermanentWidget(midi_indicator_container)
        midi_indicator_container_vbox.addStretch()
        midi_indicator_container_vbox.addLayout(label_layout)
        midi_indicator_container_vbox.addStretch()
        midi_indicator_container_vbox.addLayout(wheel_layout)
        midi_indicator_container_vbox.addStretch()
        midi_indicator_row = QHBoxLayout()
        midi_indicator_container_vbox.addLayout(midi_indicator_row)
        midi_indicator_row.addWidget(QLabel("MIDI IN:"))
        midi_indicator_row.addWidget(self.midi_in_indicator)
        midi_indicator_row.addWidget(QLabel("MIDI OUT:"))
        midi_indicator_row.addWidget(self.midi_out_indicator)
        # Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
        self.statusBar().setStyleSheet('background: "black";')

    def _update_display(self):
        synth_data = self.synth_data_map.get(self.current_synth_type)
        if not synth_data:
            logging.warning("Unknown synth type. Defaulting to DIGITAL_1.")
            synth_data = self.synth_data_map[SynthType.DIGITAL_1]

        # Get the current tone name based on synth type
        if synth_data.preset_type == SynthType.DIGITAL_1:
            self.current_tone_name = self.current_digital1_tone_name
        elif synth_data.preset_type == SynthType.DIGITAL_2:
            self.current_tone_name = self.current_digital2_tone_name
        elif synth_data.preset_type == SynthType.DRUMS:
            self.current_tone_name = self.current_drums_tone_name
        elif synth_data.preset_type == SynthType.ANALOG:
            self.current_tone_name = self.current_analog_tone_name

        # Update tone number
        self.current_tone_number = get_preset_list_number_by_name(
            self.current_tone_name, synth_data.preset_list
        )

        logging.info(f"current tone number: {self.current_tone_number}")
        logging.info(f"current tone name: {self.current_tone_name}")

        self.digital_display.repaint_display(
            current_octave=self.current_octave,
            tone_number=self.current_tone_number,
            tone_name=self.current_tone_name,
            program_name=self.current_program_name,
            program_number=self.current_program_number,
            program_bank_letter=self.current_program_bank_letter,
            active_synth=synth_data.display_prefix,
        )

    def _load_digital_font(self):
        """Load the digital LCD font for the display"""

        font_name = "JdLCD.ttf"
        font_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "resources", "fonts", font_name
        )
        if os.path.exists(font_path):
            logging.debug(f"Found file, Loading {font_name}font from {font_path}")
            try:
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    logging.debug("Error loading {font_name} font")
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.digital_font_family = font_families[0]
                    logging.debug(
                        f"Successfully loaded font family: {self.digital_font_family}"
                    )
                else:
                    logging.debug("No font families found after loading font")
            except Exception as ex:
                logging.exception(
                    f"Error loading {font_name} font from {font_path}: {ex}"
                )
        else:
            logging.debug(f"File not found: {font_path}")

    def update_preset_display(self, preset_number, preset_name):
        """Update the current preset display"""
        self.current_tone_number = preset_number
        self.current_tone_name = preset_name
        self._update_display()

    def show_error(self, title: str, message: str):
        """Show error message dialog

        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        """Show warning message dialog

        Args:
            title: Dialog title
            message: Warning message
        """
        QMessageBox.warning(self, title, message)

    def show_info(self, title: str, message: str):
        """Show info message dialog

        Args:
            title: Dialog title
            message: Info message
        """
        QMessageBox.information(self, title, message)

    def _update_display_preset(
        self, preset_number: int, preset_name: str, channel: int
    ):
        """Update the display with the new preset information"""
        logging.info(
            f"Updating display preset: # {preset_number}, name: {preset_name}, channel: {channel}"
        )
        self.current_preset_index = preset_number
        self.preset_name = preset_name
        self.channel = channel
        if re.search(r"^\d{3}:", preset_name):
            preset_number = int(preset_name[:3])
            preset_name = preset_name[4:]
        try:
            # Update display
            self.update_preset_display(preset_number, preset_name)

            # Update piano keyboard channel if it exists
            if hasattr(self, "piano_keyboard"):
                self.piano_keyboard.set_midi_channel(channel)

            logging.debug(
                f"Updated display: {preset_number:03d}:{preset_name} (channel {channel})"
            )

        except Exception as ex:
            logging.error(f"Error updating display: {str(ex)}")

    def _save_favorite(self, button, idx):
        raise NotImplementedError("to be implemented in subclass")

    def _load_settings(self):
        raise NotImplementedError("to be implemented in subclass")

    def show_editor(self, param):
        raise NotImplementedError("to be implemented in subclass")

    def _open_vocal_fx(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _open_effects(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _send_octave(self, _):
        raise NotImplementedError("Should be implemented in subclass")

    def _previous_tone(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _next_tone(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _load_saved_favorites(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _open_digital_synth1(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _open_digital_synth2(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _open_analog_synth(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _open_drums(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _open_arpeggiator(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _select_synth(self):
        raise NotImplementedError("Should be implemented in subclass")
