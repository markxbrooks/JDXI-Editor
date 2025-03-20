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
    QFrame,
    QButtonGroup,
    QGridLayout,
)
from PySide6.QtCore import Qt, QSettings, QRect
from PySide6.QtGui import (
    QAction,
    QFontDatabase,
)
from jdxi_editor.midi.preset.type import PresetType
from jdxi_editor.ui.image.instrument import draw_instrument_pixmap
from jdxi_editor.ui.style.style import Style
from jdxi_editor.ui.style.helpers import generate_sequencer_button_style, toggle_button_style
from jdxi_editor.ui.widgets.button import SequencerSquare
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay
from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
from jdxi_editor.ui.widgets.button.channel import ChannelButton
from jdxi_editor.ui.widgets.indicator import MIDIIndicator, LEDIndicator
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.ui.windows.jdxi.helpers.button_row import create_button_row
from jdxi_editor.ui.windows.jdxi.dimensions import JDXI_MARGIN, JDXI_DISPLAY_X, JDXI_DISPLAY_Y, JDXI_DISPLAY_WIDTH, \
    JDXI_DISPLAY_HEIGHT


class JdxiUi(QMainWindow):
    """ JDXI UI setup, with little or no actual functionality, which is superclassed"""
    def __init__(self):
        super().__init__()
        # Add preset & program tracking
        self.current_preset_number = 1
        self.current_preset_name = "Init Tone"
        self.current_program_number = 1
        self.current_program_name = "Init Program"
        self.current_digital1_tone_name = "Init Tone"
        self.current_digital2_tone_name = "Init Tone"
        self.current_analog_tone_name = "Init Tone"
        self.current_drums_tone_name = "Init Tone"
        # Initialize synth preset_type
        self.current_synth_type = PresetType.DIGITAL_1
        # Initialize octave
        self.current_octave = 0  # Initialize octave tracking first

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.log_file = None
        self.setWindowTitle("JD-Xi Manager")
        self.setMinimumSize(1000, 400)
        # Store window dimensions
        self.width = 1000
        self.height = 400
        self.margin = 15
        # Store display coordinates as class variables
        self.display_x = 35  # margin + 20
        self.display_y = 50  # margin + 20 + title height
        self.display_width = 180
        self.display_height = 70
        self.digital_font_family = None

        # Initialize MIDI helper
        self.midi_helper = MidiIOHelper(parent=self)
        # Initialize MIDI indicators
        self.midi_in_indicator = MIDIIndicator()
        self.midi_out_indicator = MIDIIndicator()

        # pub.subscribe(self._update_display_preset, "update_display_preset")

        # Set black background for entire application
        self.setStyleSheet(Style.JDXI)

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

        # Initial display
        self._update_display_image()

        # Add display to layout
        if hasattr(self, "main_layout"):
            self.main_layout.addWidget(self.display_label)

        # Create channel indicator
        self.channel_button = ChannelButton()

        # Add to status bar before piano keyboard
        # self.statusBar().addPermanentWidget(self.channel_button)
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
        # self.statusBar().addPermanentWidget(self.favorites_widget)
        # self.statusBar().addPermanentWidget(self.channel_button)
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
        self.image_label.setPixmap(
            draw_instrument_pixmap(
                (
                    self.digital_font_family
                    if hasattr(self, "digital_font_family")
                    else None
                ),
                self.current_octave,
            )
        )
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.layout().addWidget(self.image_label)

        # Add overlaid controls
        self._add_overlaid_controls(container)

        layout.addWidget(container)

        # Initialize current preset index
        self.current_preset_index = 0

    def _create_program_buttons_row(self):
        # create program navigation buttons
        # self.program_label = QLabel("Program")
        self.program_down_button = QPushButton("-")
        self.program_spacer = QLabel(" ")
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
        program_layout.addWidget(self.program_spacer)
        program_layout.addWidget(self.program_up_button)
        program_layout.addStretch()
        return program_layout

    def _create_tone_buttons_row(self):
        # Create Tone navigation buttons
        # self.tone_label = QLabel("Tone")
        self.tone_down_button = QPushButton("-")
        self.tone_spacer = QLabel(" ")
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
        button_label_layout.addWidget(self.tone_spacer)
        button_label_layout.addStretch()
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.tone_down_button)
        button_layout.addWidget(self.tone_spacer)
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
    
    def _create_sequencer_buttons_row_layout(self):
        """Create address row with label and circular button"""
        row_layout = QHBoxLayout()
        sequencer_buttons = []

        grid = QGridLayout()
        grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
        grid.setGeometry(QRect(1, 1, 300, 150))
        for i in range(16):
            # button = QPushButton()
            button = SequencerSquare(i, self.midi_helper)
            button.setFixedSize(25, 25)
            button.setCheckable(True)  # Ensure the button is checkable
            button.setStyleSheet(generate_sequencer_button_style(button.isChecked()))
            button.customContextMenuRequested.connect(
                lambda pos, b=button: self._show_favorite_context_menu(pos, b)
            )
            if not button.isChecked():
                button.setToolTip(f"Save Favorite {i}")
            else:
                button.setToolTip(f"Load Favorite {i}")
            button.toggled.connect(
                lambda checked, btn=button: toggle_button_style(btn, checked)
            )
            button.clicked.connect(lambda _, idx=i, but=button: self._save_favorite(but, idx))
            grid.addWidget(button, 0, i)  # Row 0, column i with spacing
            grid.setHorizontalSpacing(2)  # Add spacing between columns
            sequencer_buttons.append(button)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row_layout.addLayout(grid)

        return row_layout, sequencer_buttons

    def _create_sequencer_buttons_row_layout_new(self):
        """Create address row with label and circular button"""
        row_layout = QHBoxLayout()
        sequencer_buttons = []

        grid = QGridLayout()
        grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
        grid.setGeometry(QRect(1, 1, 300, 150))
        
        # Assuming you have a way to get the current preset name or ID
        current_presets = self.get_current_presets()  # This should return a list or dict of current presets

        for i in range(16):
            button = QPushButton()
            button.setFixedSize(25, 25)
            button.setCheckable(True)  # Ensure the button is checkable
            button.setStyleSheet(generate_sequencer_button_style(button.isChecked()))
            
            # Set the initial tooltip based on the button's checked state
            if not button.isChecked():
                button.setToolTip(f"Save Favorite {i}")
            else:
                preset_name = current_presets.get(i, f"Preset {i}")  # Get the preset name or default
                button.setToolTip(f"Load {preset_name}")

            # Connect the toggled signal to update the tooltip
            button.toggled.connect(
                lambda checked, btn=button, idx=i: self.update_tooltip(btn, checked, idx)
            )
            
            button.clicked.connect(lambda _, idx=i: self._save_favorite(button, idx))
            grid.addWidget(button, 0, i)  # Row 0, column i with spacing
            grid.setHorizontalSpacing(2)  # Add spacing between columns
            sequencer_buttons.append(button)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row_layout.addLayout(grid)

        return row_layout, sequencer_buttons

    def update_tooltip(self, button, checked, index):
        """Update the tooltip based on the button's checked state and current preset"""
        if checked:
            preset_name = self.get_current_presets().get(index, f"Preset {index}")
            button.setToolTip(f"Load {preset_name}")
        else:
            button.setToolTip(f"Save Favorite {index}")

    def get_current_presets(self):
        """Retrieve the current presets. This is a placeholder for actual implementation."""
        # This should return a dictionary or list with the current preset names or IDs
        return {0: "Preset A", 1: "Preset B", 2: "Preset C"}  # Example data

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

        # Create MIDI indicators
        self.midi_in_indicator = LEDIndicator()
        self.midi_out_indicator = LEDIndicator()

        # Add labels and indicators
        status_bar.addPermanentWidget(QLabel("MIDI IN:"))
        status_bar.addPermanentWidget(self.midi_in_indicator)
        status_bar.addPermanentWidget(QLabel("MIDI OUT:"))
        status_bar.addPermanentWidget(self.midi_out_indicator)

        # Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)

    def _add_arpeggiator_buttons(self, widget):
        """Add arpeggiator up/down buttons to the interface"""
        # Create container
        arpeggiator_buttons_container = QWidget(widget)

        # Position to align with sequencer but 25% higher (increased from 20%)
        seq_y = self.height - 50 - self.height * 0.1  # Base sequencer Y position
        offset_y = self.height * 0.3  # 25% of window height (increased from 0.2)
        arpeggiator_x = self.width - self.width * 0.8 - 60  # Position left of sequencer

        # Apply the height offset to the Y position
        arpeggiator_buttons_container.setGeometry(
            arpeggiator_x,
            seq_y - 60 - offset_y,  # Move up by offset_y (now 25% instead of 20%)
            100,
            100,
        )

        arpeggiator_layout = QVBoxLayout(arpeggiator_buttons_container)
        arpeggiator_layout.setSpacing(5)

        # Add "ARPEGGIO" label at the top
        arpeggiator_label = QLabel("ARPEGGIO")
        arpeggiator_label.setStyleSheet(Style.JDXI_LABEL)
        arpeggiator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arpeggiator_layout.addWidget(arpeggiator_label)

        # Create horizontal layout for Down/Up labels
        labels_row = QHBoxLayout()
        labels_row.setSpacing(20)  # Space between labels

        # On label
        on_label = QLabel("On")
        on_label.setStyleSheet(Style.JDXI_LABEL_SUB)
        labels_row.addWidget(on_label)

        # Add labels row
        arpeggiator_layout.addLayout(labels_row)

        # Create horizontal layout for buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(20)  # Space between buttons

        # Down label
        key_hold_label = QLabel("Key Hold")
        key_hold_label.setStyleSheet(Style.JDXI_LABEL_SUB)
        labels_row.addWidget(key_hold_label)

        # Create and store arpeggiator  button
        self.arpeggiator_button = QPushButton()
        self.arpeggiator_button.setFixedSize(30, 30)
        self.arpeggiator_button.setCheckable(True)
        self.arpeggiator_button.setStyleSheet(Style.JDXI_BUTTON_ROUND)
        buttons_row.addWidget(self.arpeggiator_button)

        # Create and store octave down button
        self.key_hold = QPushButton()
        self.key_hold.setFixedSize(30, 30)
        self.key_hold.setCheckable(True)
        self.key_hold.setStyleSheet(Style.JDXI_BUTTON_ROUND)
        buttons_row.addWidget(self.key_hold)

        # Add buttons row
        arpeggiator_layout.addLayout(buttons_row)

        # Make container transparent
        arpeggiator_buttons_container.setStyleSheet("background: transparent;")

    def _add_octave_buttons(self, widget):
        """Add octave up/down buttons to the interface"""
        # Create container
        octave_buttons_container = QWidget(widget)

        # Position to align with sequencer but 25% higher (increased from 20%)
        seq_y = self.height - 50 - int(self.height * 0.1)  # Base sequencer Y position
        offset_y = int(self.height * 0.3)  # 25% of window height (increased from 0.2)
        octave_x = self.width - int(self.width * 0.8) - 150  # Position left of sequencer

        # Apply the height offset to the Y position
        octave_buttons_container.setGeometry(
            octave_x,
            seq_y - 60 - offset_y,  # Move up by offset_y
            100,
            100,
        )

        octave_layout = QVBoxLayout(octave_buttons_container)
        octave_layout.setSpacing(5)

        # Create horizontal layout for Down/Up labels
        labels_row = QHBoxLayout()
        labels_row.setSpacing(20)  # Space between labels

        # Add "OCTAVE" label at the top
        octave_label = QLabel("OCTAVE")
        octave_label.setStyleSheet(Style.JDXI_LABEL)
        octave_label.setAlignment(Qt.AlignCenter)
        octave_layout.addWidget(octave_label)

        # Down label
        down_label = QLabel("Down")
        down_label.setStyleSheet(Style.JDXI_LABEL_SUB)
        labels_row.addWidget(down_label)

        # Up label
        up_label = QLabel("Up")
        up_label.setStyleSheet(Style.JDXI_LABEL_SUB)
        labels_row.addWidget(up_label)

        # Add labels row
        octave_layout.addLayout(labels_row)

        # Create horizontal layout for buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(20)  # Space between buttons

        # Create and store octave down button
        self.octave_down = QPushButton()
        self.octave_down.setFixedSize(30, 30)
        self.octave_down.setCheckable(True)
        self.octave_down.clicked.connect(lambda: self._send_octave(-1))
        self.octave_down.setStyleSheet(Style.JDXI_BUTTON_ROUND)
        buttons_row.addWidget(self.octave_down)

        # Create and store octave up button
        self.octave_up = QPushButton()
        self.octave_up.setFixedSize(30, 30)
        self.octave_up.setCheckable(True)
        self.octave_up.clicked.connect(lambda: self._send_octave(1))
        self.octave_up.setStyleSheet(Style.JDXI_BUTTON_ROUND)
        buttons_row.addWidget(self.octave_up)

        # Add buttons row
        octave_layout.addLayout(buttons_row)

        # Make container transparent
        octave_buttons_container.setStyleSheet("background: transparent;")

    def _add_overlaid_controls(self, central_widget):
        """Add interactive controls overlaid on the JD-Xi image"""
        # Create absolute positioning layout
        central_widget.setLayout(QVBoxLayout())

        digital_display_container = QWidget(central_widget)
        digital_display_container.setGeometry(JDXI_DISPLAY_X, JDXI_DISPLAY_Y, JDXI_DISPLAY_WIDTH, JDXI_DISPLAY_HEIGHT)
        digital_display_layout = QHBoxLayout()
        digital_display_container.setLayout(digital_display_layout)
        self.digital_display = DigitalDisplay(parent=self)
        digital_display_layout.addWidget(self.digital_display)

        # Parts Select section with Arpeggiator
        parts_container = QWidget(central_widget)
        parts_x = self.display_x + self.display_width + 30
        parts_y = int(self.display_y - (
            self.height * 0.15
        ))  # Move up by 20% of window height

        parts_container.setGeometry(parts_x, parts_y, 220, 250)
        parts_layout = QVBoxLayout(parts_container)
        parts_layout.setSpacing(15)  # Increased from 5 to 15 for more vertical spacing

        # Add Parts Select label
        parts_label = QLabel("Parts Select")
        parts_label.setStyleSheet(Style.JDXI_PARTS_SELECT)
        parts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parts_layout.addWidget(parts_label)

        # Parts buttons
        digital1_row, self.digital1_button = create_button_row(
            "Digital Synth 1", self._open_digital_synth1
        )
        digital2_row, self.digital2_button = create_button_row(
            "Digital Synth 2", self._open_digital_synth2
        )
        drums_row, self.drums_button = create_button_row(
            "Drums", self._open_drums
        )
        analog_row, self.analog_button = create_button_row(
            "Analog Synth", self._open_analog_synth
        )
        arp_row, self.arp_button = create_button_row(
            "Arpeggiator", self._open_arpeggiator
        )

        self.analog_button.clicked.connect(
            lambda: self._select_synth(PresetType.ANALOG)
        )
        self.digital1_button.clicked.connect(
            lambda: self._select_synth(PresetType.DIGITAL_1)
        )
        self.digital2_button.clicked.connect(
            lambda: self._select_synth(PresetType.DIGITAL_2)
        )
        self.drums_button.clicked.connect(lambda: self._select_synth(PresetType.DRUMS))

        # Create address button area
        button_group = QButtonGroup()
        button_group.addButton(self.digital1_button)
        button_group.addButton(self.digital2_button)
        button_group.addButton(self.analog_button)
        button_group.addButton(self.drums_button)

        # Ensure only one button can be checked at address time
        button_group.setExclusive(True)

        parts_layout.addLayout(digital1_row)
        parts_layout.addLayout(digital2_row)
        parts_layout.addLayout(drums_row)
        parts_layout.addLayout(analog_row)
        parts_layout.addLayout(arp_row)

        self._add_octave_buttons(central_widget)
        self._add_arpeggiator_buttons(central_widget)

        # Effects button in top row
        fx_container = QWidget(central_widget)
        fx_container.setGeometry(self.width - 200, self.margin + 20, 200, 80)
        fx_layout = QHBoxLayout(fx_container)
        vocal_effects_row, self.vocal_effects_button = create_button_row(
            "Vocoder", self._open_vocal_fx, vertical=True,
        )
        effects_row, self.effects_button = create_button_row(
            "Effects", self._open_effects, vertical=True, spacing=10
        )

        fx_layout.setSpacing(15)
        fx_layout.addLayout(vocal_effects_row)
        fx_layout.addLayout(effects_row)

        program_container = QWidget(central_widget)
        program_container.setGeometry(self.width - 525, self.margin + 15, 150, 100)
        program_container_layout = QVBoxLayout(program_container)
        program_label_layout = QHBoxLayout()
        program_label = QLabel("Program")
        program_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        program_label.setStyleSheet(Style.JDXI_LABEL)
        program_label_layout.addWidget(program_label)
        program_container_layout.addLayout(program_label_layout)
        program_layout = QHBoxLayout()
        program_row = self._create_program_buttons_row()
        program_layout.addLayout(program_row)
        program_container_layout.addLayout(program_layout)

        # For tone buttons
        tone_container = QWidget(central_widget)
        tone_container.setGeometry(self.width - 380, self.margin + 15, 150, 100)
        tone_container_layout = QVBoxLayout(tone_container)
        tone_label_layout = QHBoxLayout()
        tone_label = QLabel("Tone")
        tone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tone_label.setStyleSheet(Style.JDXI_LABEL)
        tone_label_layout.addWidget(tone_label)
        tone_container_layout.addLayout(tone_label_layout)
        tone_layout = QHBoxLayout()
        tone_row = self._create_tone_buttons_row()
        tone_layout.addLayout(tone_row)
        tone_container_layout.addLayout(tone_layout)

        # Beginning of sequencer section
        sequencer_container = QWidget(central_widget)
        sequencer_container.setGeometry(self.width - 500, self.margin + 150, 500, 100)
        sequencer_container_layout = QHBoxLayout(sequencer_container)
        sequencer_label_layout = QHBoxLayout()
        sequencer_label = QLabel("Sequencer")
        sequencer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sequencer_label.setStyleSheet(Style.JDXI_SEQUENCER)
        # sequencer_label_layout.addWidget(sequencer_label)
        # sequencer_container_layout.addLayout(sequencer_label_layout)
        sequencer_layout = QHBoxLayout()
        favorites_button_row = self._create_favorite_button_row()
        sequencer, self.sequencer_buttons = self._create_sequencer_buttons_row_layout()
        sequencer_layout.addLayout(sequencer)
        sequencer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        sequencer_container_layout.addLayout(favorites_button_row)
        sequencer_container_layout.addLayout(sequencer_layout)
        # End of sequencer section

        # Make containers transparent
        parts_container.setStyleSheet("background: transparent;")
        fx_container.setStyleSheet("background: transparent;")

    def _create_other(self):
        """Create other controls section"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # Create buttons for Effects and Vocal FX
        others = [
            ("Effects", self._open_effects),
            ("Vocal FX", self._open_vocal_fx),
        ]

        for text, slot in others:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        # Create horizontal layout for Arpeggiator
        arp_row = QHBoxLayout()

        # Arpeggiator button
        arp_btn = QPushButton("Arpeggio")
        arp_btn.setFixedHeight(40)
        arp_btn.clicked.connect(self._open_arpeggiator)
        arp_row.addWidget(arp_btn)

        # Add the horizontal row to the main layout
        layout.addLayout(arp_row)

        # Add stretch at the bottom
        layout.addStretch()

        return frame

    def _update_display(self):
        """Update the JD-Xi display image"""
        if self.current_synth_type == PresetType.DIGITAL_1:
            self.current_preset_name = self.current_digital1_tone_name
        elif self.current_synth_type == PresetType.DIGITAL_2:
            self.current_preset_name = self.current_digital2_tone_name
        elif self.current_synth_type == PresetType.DRUMS:
            self.current_preset_name = self.current_drums_tone_name
        elif self.current_synth_type == PresetType.ANALOG:
            self.current_preset_name = self.current_analog_tone_name

        self.digital_display.repaint_display(
            current_octave=self.current_octave,
            preset_num=self.current_preset_number,
            preset_name=self.current_preset_name,
            program_name=self.current_program_name,
            program_num=self.current_program_number
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
        self.current_preset_number = preset_number
        self.current_preset_name = preset_name
        self._update_display()

    def update_program_display(self, program_number, program_name):
        """Update the current preset display"""
        self.current_program_number = program_number
        self.current_program_name = program_name
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

    def _create_midi_indicators(self):
        """Create MIDI activity indicators"""
        # Create indicators
        self.midi_in_indicator = MIDIIndicator()
        self.midi_out_indicator = MIDIIndicator()

        # Create labels
        in_label = QLabel("MIDI IN")
        out_label = QLabel("MIDI OUT")
        in_label.setStyleSheet("color: white; font-size: 10px;")
        out_label.setStyleSheet("color: white; font-size: 10px;")

        # Create container widget
        indicator_widget = QWidget(self)
        indicator_layout = QVBoxLayout(indicator_widget)
        indicator_layout.setSpacing(4)
        indicator_layout.setContentsMargins(0, 0, 0, 0)

        # Add indicators with labels
        for label, indicator in [
            (in_label, self.midi_in_indicator),
            (out_label, self.midi_out_indicator),
        ]:
            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(indicator)
            indicator_layout.addLayout(row)

        # Position the container - moved right by 20px and down by 50px from original position
        indicator_widget.move(
            self.width() - 80, 120
        )  # Original was (self.width() - 100, 70)

        return indicator_widget

    def _update_display_program(
        self, program_name: str, program_number: int
    ):
        self.current_program_number = program_number
        self.current_program_name = program_name
        self._update_display()

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

            # Update channel indicator if it exists
            #if hasattr(self, "channel_button"):
            #    self.channel_button.set_channel(channel)

            logging.debug(
                f"Updated display: {preset_number:03d}:{preset_name} (channel {channel})"
            )

        except Exception as ex:
            logging.error(f"Error updating display: {str(ex)}")

    def _update_display_image(
        self, preset_num: int = 1, preset_name: str = "INIT PATCH"
    ):
        """Update the digital display image

        Args:
            preset_num: Preset number to display (1-128)
            preset_name: Name of preset to display
        """
        try:
            # Create new image with updated preset info
            image = draw_instrument_pixmap(
                digital_font_family=self.digital_font_family,
                current_octave=self.current_octave,
                preset_num=preset_num,
                preset_name=preset_name,
            )

            # Update display label
            if hasattr(self, "display_label"):
                self.display_label.setPixmap(image)

            logging.debug(f"Updated display: {preset_num:03d}:{preset_name}")

        except Exception as ex:
            logging.error(f"Error updating display image: {str(ex)}")

    def _save_favorite(self, button, idx):
        pass # to be implemented in subclass

    def _load_settings(self):
        pass
