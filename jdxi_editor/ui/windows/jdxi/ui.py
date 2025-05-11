"""
JD-Xi Editor UI setup.

This class defines the main user interface for the JD-Xi Editor application, inheriting from QMainWindow. It handles the creation of the UI elements, including the main layout, menus, status bar, and MIDI indicators. It also provides functionality for displaying and managing synth presets, favorites, and MIDI connectivity.

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
from typing import Union

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLabel,
    QLayout,
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import (
    QAction,
    QFontDatabase,
)
import qtawesome as qta

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.jdxi.synth.factory import create_synth_data
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.manager import JDXIPresetManager
from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.editors.helpers.program import (
    get_preset_list_number_by_name,
    get_program_name_by_id,
)
from jdxi_editor.ui.image.instrument import draw_instrument_pixmap
from jdxi_editor.jdxi.style.jdxi import JDXiStyle
from jdxi_editor.ui.widgets.button.sequencer import SequencerSquare
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton
from jdxi_editor.ui.widgets.piano.keyboard import PianoKeyboard
from jdxi_editor.ui.widgets.indicator.led import LEDIndicator
from jdxi_editor.ui.windows.jdxi.containers import (
    add_arpeggiator_buttons,
    add_slider_container,
    add_digital_display,
    add_effects_container,
    add_octave_buttons,
    add_program_container,
    add_sequencer_container,
    add_favorite_button_container,
    add_title_container,
    add_tone_container,
    build_wheel_row,
    build_wheel_label_row,
    create_tone_buttons_row,
    create_program_buttons_row,
    create_parts_container,
)
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


class JdxiUi(QMainWindow):
    """JDXI UI setup, with little or no actual functionality, which is super-classed"""

    def __init__(self):
        super().__init__()
        self.digital_font_family = None
        self.editor_registry = None
        self.editors = []
        self.log_viewer = None
        self.midi_debugger = None
        self.midi_message_monitor = None
        self.old_pos = None
        self.preset_helpers = None
        self.slot_number = None
        self.sequencer_buttons = []
        self.current_program_bank_letter = "A"
        # Set up programs
        self.current_program_id = "A01"
        self.current_program_number = int(self.current_program_id[1:])
        self.current_program_name = get_program_name_by_id(self.current_program_id)
        # Set up presets
        self.preset_manager = JDXIPresetManager()
        # Initialize synth preset_type
        self.current_synth_type = JDXISynth.DIGITAL_1
        # Initialize octave
        self.current_octave = 0  # Initialize octave tracking first
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("JD-Xi Editor")
        self.setMinimumSize(JDXIDimensions.WIDTH, JDXIDimensions.HEIGHT)

        # Initialize MIDI helper
        self.midi_helper = MidiIOHelper()
        #  Initialize MIDI connectivity
        if self.midi_helper:
            self.midi_helper.close_ports()
        self.channel = MidiChannel.DIGITAL1
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.midi_key_hold_latched = False
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL

        # Load custom font
        self._load_digital_font()

        # Create UI
        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_layout()
        self._create_parts_menu()
        self._create_effects_menu()
        self._create_playback_menu()
        self._create_help_menu()

        # Load settings
        self.settings = QSettings("mabsoft", "jdxi_editor")

        # Add piano keyboard at bottom
        self.piano_keyboard = PianoKeyboard(parent=self)
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # Load saved favorites
        self._load_saved_favorites()

    def _create_main_layout(self) -> None:
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
        self.digital_display = add_digital_display(container, self)
        add_title_container(container)
        self.parts_container, self.part_buttons = create_parts_container(
            parent_widget=self,
            on_open_d1=lambda: self.show_editor("digital1"),
            on_open_d2=lambda: self.show_editor("digital2"),
            on_open_drums=lambda: self.show_editor("drums"),
            on_open_analog=lambda: self.show_editor("analog"),
            on_open_arp=lambda: self.show_editor("arpeggio"),
            on_select_synth=self._select_synth,
        )
        self.synth_buttons = {
            JDXISynth.DIGITAL_1: self.part_buttons["digital1"],
            JDXISynth.DIGITAL_2: self.part_buttons["digital2"],
            JDXISynth.ANALOG: self.part_buttons["analog"],
            JDXISynth.DRUM: self.part_buttons["drums"],
        }
        self.arp_button = self.part_buttons["arp"]
        self.octave_down, self.octave_up = add_octave_buttons(
            container, self._midi_send_octave
        )
        self.arpeggiator_button, self.key_hold_button = add_arpeggiator_buttons(
            container
        )
        self.vocal_effects_button, self.effects_button = add_effects_container(
            container,
            lambda: self.show_editor("vocal_fx"),
            lambda: self.show_editor("effects"),
        )

        (self.program_down_button, self.program_up_button) = add_program_container(
            container, create_program_buttons_row
        )

        self.tone_down_button, self.tone_up_button = add_tone_container(
            container, create_tone_buttons_row, self._preset_previous, self._preset_next
        )
        self.sequencer_buttons = add_sequencer_container(
            container,
            midi_helper=self.midi_helper,
            on_context_menu=self._show_favorite_context_menu,
            on_save_favorite=self._save_favorite,
        )
        self.favorite_button = add_favorite_button_container(container)
        add_slider_container(container, self.midi_helper)
        layout.addWidget(container)

        # Initialize current preset index
        self.current_preset_index = 0

    def _create_menu_bar(self) -> None:
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        load_program_action = QAction(
            qta.icon("msc.folder-opened"), "Load Program...", self
        )
        load_program_action.triggered.connect(lambda: self.show_editor("program"))
        file_menu.addAction(load_program_action)

        load_preset_action = QAction("Load Preset...", self)
        load_preset_action.triggered.connect(lambda: self.show_editor("preset"))
        file_menu.addAction(load_preset_action)

        load_action = QAction("Load Patch...", self)
        load_action.triggered.connect(self._patch_load)
        file_menu.addAction(load_action)

        save_action = QAction("Save Patch...", self)
        save_action.triggered.connect(self._patch_save)
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

    def _create_parts_menu(self) -> None:
        """Create editors menu"""
        self.parts_menu = self.menuBar().addMenu("Parts")

        digital1_action = QAction("Digital Synth 1", self)
        digital1_action.triggered.connect(lambda: self.show_editor("digital1"))
        self.parts_menu.addAction(digital1_action)

        digital2_action = QAction("Digital Synth 2", self)
        digital2_action.triggered.connect(lambda: self.show_editor("digital2"))
        self.parts_menu.addAction(digital2_action)

        drums_action = QAction("Drums", self)
        drums_action.triggered.connect(lambda: self.show_editor("drums"))
        self.parts_menu.addAction(drums_action)

        analog_action = QAction("Analog Synth", self)
        analog_action.triggered.connect(lambda: self.show_editor("analog"))

        self.parts_menu.addAction(analog_action)

    def _create_effects_menu(self) -> None:
        """Create editors menu"""
        self.effects_menu = self.menuBar().addMenu("Effects")

        effects_action = QAction("Effects", self)
        effects_action.triggered.connect(lambda: self.show_editor("effects"))
        self.effects_menu.addAction(effects_action)

        vocal_effects_action = QAction("Vocal FX", self)
        vocal_effects_action.triggered.connect(lambda: self.show_editor("vocal_fx"))
        self.effects_menu.addAction(vocal_effects_action)

    def _create_playback_menu(self) -> None:
        # Create editors menu
        playback_menu = self.menuBar().addMenu("Playback")

        # Add MIDI file action
        midi_file_action = QAction("MIDI File", self)
        midi_file_action.triggered.connect(lambda: self.show_editor("midi_file"))
        playback_menu.addAction(midi_file_action)

        arpeggiator_action = playback_menu.addAction("Arpeggiator")
        arpeggiator_action.triggered.connect(lambda: self.show_editor("arpeggio"))

        sequencer_action = playback_menu.addAction("Pattern Sequencer")
        sequencer_action.triggered.connect(lambda: self.show_editor("pattern"))

    def _create_debug_menu(self) -> None:
        # Add debug menu
        self.debug_menu = self.menuBar().addMenu("Debug")

        # Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._show_midi_debugger)
        self.debug_menu.addAction(midi_debugger_action)

        # Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._show_midi_message_monitor)
        self.debug_menu.addAction(midi_monitor_action)

        # Add log viewer action
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        self.debug_menu.addAction(log_viewer_action)

        # Add About window action
        about_help_action = QAction("About", self)
        about_help_action.triggered.connect(self._show_about_help)
        self.debug_menu.addAction(about_help_action)

    def _create_help_menu(self) -> None:
        menubar = self.menuBar()

        # Help menu
        self.help_menu = menubar.addMenu("Help")
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        self.help_menu.addAction(log_viewer_action)

        # Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._show_midi_debugger)
        self.help_menu.addAction(midi_debugger_action)

        # Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._show_midi_message_monitor)
        self.help_menu.addAction(midi_monitor_action)

        # Add About window action
        about_help_action = QAction("About", self)
        about_help_action.triggered.connect(self._show_about_help)
        self.help_menu.addAction(about_help_action)

    def _create_status_bar(self):
        """Create status bar with MIDI indicators"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(JDXiStyle.TRANSPARENT)

        midi_indicator_container = QWidget()
        midi_indicator_container.setLayout(self._build_status_layout())
        status_bar.addPermanentWidget(midi_indicator_container)

        # Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
        status_bar.setStyleSheet('background: "black";')

    def _build_status_layout(self) -> None:
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(build_wheel_label_row())
        layout.addStretch()
        layout.addLayout(build_wheel_row(midi_helper=self.midi_helper))
        layout.addStretch()
        layout.addLayout(self._build_midi_indicator_row())
        return layout

    def _build_midi_indicator_row(self) -> QLayout:
        self.midi_in_indicator = LEDIndicator()
        self.midi_out_indicator = LEDIndicator()

        row = QHBoxLayout()
        row.addWidget(QLabel("MIDI IN:"))
        row.addWidget(self.midi_in_indicator)
        row.addWidget(QLabel("MIDI OUT:"))
        row.addWidget(self.midi_out_indicator)
        return row

    def _update_display(self):
        """Update the display with the current preset information"""
        # synth_data = self.synth_data_map.get(self.current_synth_type)
        synth_data = create_synth_data(self.current_synth_type)
        if not synth_data:
            logging.warning("MIDI_SLEEP_TIME. Defaulting to DIGITAL_1.")
            synth_data = self.synth_data_map[JDXISynth.DIGITAL_1]

        self.preset_manager.current_preset_name = (
            self.preset_manager.get_preset_name_by_type(self.current_synth_type)
        )
        # Update preset number
        self.preset_manager.current_preset_number = get_preset_list_number_by_name(
            self.preset_manager.current_preset_name, synth_data.preset_list
        )

        self.digital_display.repaint_display(
            current_octave=self.current_octave,
            tone_number=self.preset_manager.current_preset_number,
            tone_name=self.preset_manager.get_preset_name_by_type(
                self.current_synth_type
            ),
            program_name=self.current_program_name,
            active_synth=synth_data.display_prefix,
        )

    def _load_digital_font(self) -> None:
        """Load the digital LCD font for the display"""

        font_name = "JdLCD.ttf"
        font_path = resource_path(os.path.join("resources", "fonts", font_name))
        if os.path.exists(font_path):
            log_message("Success: found font file, loading...")
            log_message(f"font_name: \t{font_name}")
            log_message(f"font_path: \t{font_path}")
            try:
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    log_error(f"Error loading {font_name} font", level=logging.WARNING)
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.digital_font_family = font_families[0]
                    log_message(
                        f"Successfully loaded font family: \t{self.digital_font_family}",
                    )
                else:
                    log_message(
                        "No font families found after loading font",
                        level=logging.WARNING,
                    )
            except Exception as ex:
                log_error(f"Error loading {font_name} font from {font_path}: {ex}")
        else:
            log_message(f"File not found: {font_path}")

    def update_preset_display(self, preset_number: int, preset_name: str):
        """Update the current preset display"""
        self.preset_manager.current_preset_number = preset_number
        self.preset_manager.current_preset_name = preset_name
        self._update_display()

    def _update_display_preset(
        self, preset_number: int, preset_name: str, channel: int
    ):
        """Update the display with the new preset information."""
        log_message(
            f"Updating display preset: # {preset_number}, name: {preset_name}, channel: {channel}"
        )
        self.current_preset_index = preset_number
        self.channel = channel

        try:
            # Extract actual number and name if the preset_name is like '123:Some Name'
            match = re.match(r"^(\d{3}):(.*)", preset_name)
            if match:
                preset_number = int(match.group(1))
                preset_name = match.group(2).strip()

            self.preset_manager.current_preset_number = preset_number
            self.preset_manager.current_preset_name = preset_name
            self._update_display()

            # Update piano keyboard MIDI channel if available
            if hasattr(self, "piano_keyboard"):
                self.piano_keyboard.set_midi_channel(channel)

            log_message(
                f"Updated display: {preset_number:03d}:{preset_name} (channel {channel})"
            )

        except Exception as ex:
            log_error(f"Error updating display: {ex}")

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

    def _load_settings(self):
        raise NotImplementedError("to be implemented in subclass")

    def show_editor(self, param: str):
        raise NotImplementedError("to be implemented in subclass")

    def _show_midi_debugger(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_about_help(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_midi_message_monitor(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_log_viewer(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_midi_config(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _midi_send_octave(self, _):
        raise NotImplementedError("Should be implemented in subclass")

    def _preset_previous(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _preset_next(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _load_saved_favorites(self):
        raise NotImplementedError("Should be implemented in subclass")

    def _select_synth(self, synth_type):
        raise NotImplementedError("Should be implemented in subclass")

    def _show_favorite_context_menu(
        self, pos, button: Union[FavoriteButton, SequencerSquare]
    ):
        raise NotImplementedError("Should be implemented in subclass")

    def _save_favorite(self, button, idx):
        raise NotImplementedError("to be implemented in subclass")

    def _patch_load(self):
        raise NotImplementedError("to be implemented in subclass")

    def _patch_save(self):
        raise NotImplementedError("to be implemented in subclass")

    def _handle_program_change(self, bank_letter: str, program_number: int):
        raise NotImplementedError("to be implemented in subclass")
