import logging
import re
from pubsub import pub

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QLabel,
    QPushButton,
    QFrame,
    QGroupBox,
    QButtonGroup,
    QGridLayout,
)
from PySide6.QtCore import Qt, QSettings, QObject, Signal
from PySide6.QtGui import (
    QAction,
    QFont,
    QFontDatabase,
)
from jdxi_manager.data.analog import AN_PRESETS
from jdxi_manager.data.presets.data import ANALOG_PRESETS_ENUMERATED, DIGITAL_PRESETS_ENUMERATED, DRUM_PRESETS_ENUMERATED
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.constants.arpeggio import ARP_PART, ARP_AREA, ARP_GROUP
from jdxi_manager.ui.editors import (
    AnalogSynthEditor,
    DigitalSynthEditor,
    DrumEditor,
    ArpeggioEditor,
    EffectsEditor,
    VocalFXEditor,
)
from jdxi_manager.ui.editors.pattern import PatternSequencer
from jdxi_manager.ui.editors.preset import PresetEditor
from jdxi_manager.ui.image.instrument import draw_instrument_pixmap
from jdxi_manager.ui.windows.midi.config import MIDIConfigDialog
from jdxi_manager.ui.windows.midi.debugger import MIDIDebugger
from jdxi_manager.ui.windows.midi.message_debug import MIDIMessageDebug
from jdxi_manager.ui.windows.patch.patch_name_editor import PatchNameEditor
from jdxi_manager.ui.windows.patch.patch_manager import PatchManager
from jdxi_manager.ui.style import Style, sequencer_button_style, toggle_button_style
from jdxi_manager.ui.widgets.piano.keyboard import PianoKeyboard
from jdxi_manager.ui.widgets.button.channel import ChannelButton
from jdxi_manager.ui.widgets.viewer.log import LogViewer
from jdxi_manager.ui.widgets.indicator import MIDIIndicator, LEDIndicator
from jdxi_manager.ui.widgets.button.favorite import FavoriteButton
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.midi.io.connection import MIDIConnection
from jdxi_manager.midi.constants import (
    START_OF_SYSEX,
    ROLAND_ID,
    DEVICE_ID,
    MODEL_ID_1,
    MODEL_ID_2,
    MODEL_ID_3,
    MODEL_ID,
    JD_XI_ID,
    DT1_COMMAND_12,
    RQ1_COMMAND_11,
    END_OF_SYSEX,
    ANALOG_SYNTH_AREA,
    MIDI_CHANNEL_DIGITAL1,
    MIDI_CHANNEL_DIGITAL2,
    MIDI_CHANNEL_ANALOG,
    MIDI_CHANNEL_DRUMS,
)
from jdxi_manager.midi.constants.sysex import TEMPORARY_PROGRAM_AREA
from jdxi_manager.midi.sysex.messages import IdentityRequest, ParameterMessage
from jdxi_manager.midi.preset.loader import PresetLoader


class PresetHandler(QObject):
    preset_changed = Signal(int)  # Signal emitted when preset changes
    update_display = Signal(int, int, int)

    def __init__(self, presets, channel=1, type=PresetType.DIGITAL_1):
        super().__init__()
        self.presets = presets
        self.channel = channel
        self.type = type
        self.current_preset_index = 0

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index += 1
            self.preset_changed.emit(self.current_preset_index)  # Emit signal
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index -= 1
            self.preset_changed.emit(self.current_preset_index)  # Emit signal
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
        return self.get_current_preset()

    def get_current_preset(self):
        """Get the current preset details."""
        return {
            "index": self.current_preset_index,
            "preset": self.presets[self.current_preset_index],
            "channel": self.channel,
        }

    def set_channel(self, channel):
        """Set the MIDI channel."""
        self.channel = channel

    def set_preset(self, index):
        """Set the preset manually and emit the signal."""
        if 0 <= index < len(self.presets):
            self.current_preset_index = index
            self.preset_changed.emit(self.current_preset_index)
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal


class MainWindow(QMainWindow):
    midi_program_changed = Signal(int, int)  # Add signal for program changes (channel, program)

    def __init__(self):
        super().__init__()
        self.slot_num = None
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)

        # Initialize attributes and SysEx settings
        self.attributes = {
            "ProgramBSMSB": [40, 4, 1],
            "ProgramBSLSB": [127, 5, 1],
            "ProgramPC": [15, 6, 1],
        }
        self.base_address = [0x01, 0x00, 0x00]
        self.offset = [0x00, 0x00]
        self.address = [
            self.base_address[0],
            self.base_address[1] + self.offset[0],
            self.base_address[2] + self.offset[1],
        ]
        self.data_length = [0x00, 0x00, 0x00, 0x3B]
        jd_xi_device = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]
        self.device_id = jd_xi_device  # Ensure JDXi_device is defined elsewhere
        self.sysex_setlist = self.device_id + [0x12] + self.address
        self.sysex_getlist = self.device_id + [0x11]
        self.device_status = "unknown"

        self.channel = 1
        self.analog_editor = None
        self.last_preset = None
        self.preset_loader = None
        self.log_file = None
        self.setWindowTitle("JD-Xi Manager")
        self.setMinimumSize(1000, 400)
        # Store window dimensions
        self.width = 1000
        self.height = 400
        self.margin = 15
        self.preset_type = PresetType.DIGITAL_1  # Default preset
        # Store display coordinates as class variables
        self.display_x = 35  # margin + 20
        self.display_y = 50  # margin + 20 + title height
        self.display_width = 180
        self.display_height = 70

        # Initialize state variables
        self.current_synth_type = PresetType.DIGITAL_1
        self.current_octave = 0  # Initialize octave tracking first
        self.current_preset_num = 1  # Initialize preset number
        self.current_preset_name = "JD Xi"  # Initialize preset name
        self.midi_in = None
        self.midi_out = None
        self.midi_in_port_name = ""  # Store input port name
        self.midi_out_port_name = ""  # Store output port name

        # Initialize MIDI helper
        self.midi_helper = MIDIHelper(parent=self)
        # self.preset_loader = PresetLoader(self.midi_helper)

        # Initialize windows to None
        self.log_viewer = None
        self.midi_debugger = None
        self.midi_message_debug = None

        # Try to auto-connect to JD-Xi
        self._auto_connect_jdxi()

        # Show MIDI config if auto-connect failed
        if (
            not self.midi_helper.current_in_port
            or not self.midi_helper.current_out_port
        ):
            self._show_midi_config()

        # Initialize MIDI indicators
        self.midi_in_indicator = MIDIIndicator()
        self.midi_out_indicator = MIDIIndicator()

        pub.subscribe(self._update_display_preset, "update_display_preset")

        # Set black background for entire application
        self.setStyleSheet(Style.JDXI_STYLE)

        # Load custom font
        self._load_digital_font()

        # Create UI
        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_layout()

        # Load settings
        self.settings = QSettings("jdxi_manager2", "settings")
        self._load_settings()

        # Show window
        self.show()

        # Add debug menu
        debug_menu = self.menuBar().addMenu("Debug")

        # Add MIDI debugger action (SysEx decoder)
        midi_debugger_action = QAction("MIDI SysEx Debugger", self)
        midi_debugger_action.triggered.connect(self._open_midi_debugger)
        debug_menu.addAction(midi_debugger_action)

        # Add MIDI message monitor action
        midi_monitor_action = QAction("MIDI Monitor", self)
        midi_monitor_action.triggered.connect(self._open_midi_message_debug)
        debug_menu.addAction(midi_monitor_action)

        # Add log viewer action
        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        debug_menu.addAction(log_viewer_action)

        # Add preset tracking
        self.current_preset_num = 1
        self.current_preset_name = "INIT PATCH"

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
        self.statusBar().addPermanentWidget(self.channel_button)
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # Load last used preset settings
        # self._load_last_preset()

        # Initialize synth type
        self.current_synth_type = PresetType.DIGITAL_1

        # Set default styles
        self._update_synth_button_styles()

        # Create favorite buttons container
        favorites_widget = QWidget()
        favorites_layout = QVBoxLayout(favorites_widget)
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
        self.statusBar().addPermanentWidget(favorites_widget)
        self.statusBar().addPermanentWidget(self.channel_button)
        self.statusBar().addPermanentWidget(self.piano_keyboard)

        # Load saved favorites
        self._load_saved_favorites()

        # Create editors menu
        editors_menu = self.menuBar().addMenu("Editors")

        # Add menu items for each editor
        digital1_action = editors_menu.addAction("Digital Synth 1")
        digital1_action.triggered.connect(lambda: self.show_editor("digital1"))

        digital2_action = editors_menu.addAction("Digital Synth 2")
        digital2_action.triggered.connect(lambda: self.show_editor("digital2"))

        analog_action = editors_menu.addAction("Analog Synth")
        analog_action.triggered.connect(lambda: self.show_editor("analog"))

        drums_action = editors_menu.addAction("Drums")
        drums_action.triggered.connect(lambda: self.show_editor("drums"))

        arp_action = editors_menu.addAction("Arpeggio")
        arp_action.triggered.connect(lambda: self.show_editor("arpeggio"))

        effects_action = editors_menu.addAction("Effects")
        effects_action.triggered.connect(lambda: self.show_editor("effects"))

        # Add Vocal FX menu item
        vocal_fx_action = editors_menu.addAction("Vocal FX")
        vocal_fx_action.triggered.connect(lambda: self.show_editor("vocal_fx"))

        # Initialize current preset index
        self.current_preset_index = 0

        # Initialize current preset index
        self.current_preset_index = 0

        # Initialize PresetHandler with the desired preset list
        self.digital_1_preset_handler = PresetHandler(DIGITAL_PRESETS_ENUMERATED)
        self.digital_2_preset_handler = PresetHandler(DIGITAL_PRESETS_ENUMERATED)
        self.analog_preset_handler = PresetHandler(ANALOG_PRESETS_ENUMERATED)
        self.drums_preset_handler = PresetHandler(DRUM_PRESETS_ENUMERATED)

        self.digital_1_preset_handler.update_display.connect(
            self.update_display_callback
        )
        self.digital_2_preset_handler.update_display.connect(
            self.update_display_callback
        )
        self.analog_preset_handler.update_display.connect(self.update_display_callback)
        self.drums_preset_handler.update_display.connect(self.update_display_callback)
        self.oldPos = None
        self.get_data()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos is not None:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = None

    def _select_synth(self, synth_type):
        """Select a synth and update button styles."""
        logging.info(f"Selected synth: {synth_type}")
        self.current_synth_type = synth_type
        self._update_synth_button_styles()

    def _update_synth_button_styles(self):
        """Update styles for synth buttons based on selection."""
        buttons = {
            PresetType.ANALOG: self.analog_button,
            PresetType.DIGITAL_1: self.digital1_button,
            PresetType.DIGITAL_2: self.digital2_button,
            PresetType.DRUMS: self.drums_button,
        }

        for synth_type, button in buttons.items():
            if synth_type == self.current_synth_type:
                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #333333;
                        border: 4px solid #d51e35;
                        border-radius: 15px;
                        padding: 0px;
                    }
                """
                )
            else:
                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #000000;
                        border: 4px solid #666666;
                        border-radius: 15px;
                        padding: 0px;
                    }
                """
                )

    def _get_presets_for_current_synth(self):
        """Return the appropriate preset list based on the current synth type."""
        preset_map = {
            PresetType.ANALOG: AN_PRESETS,
            PresetType.DIGITAL_1: DIGITAL_PRESETS_ENUMERATED,
            PresetType.DIGITAL_2: DIGITAL_PRESETS_ENUMERATED,
            PresetType.DRUMS: DRUM_PRESETS_ENUMERATED,
        }

        presets = preset_map.get(self.current_synth_type, None)
        if presets is None:
            logging.warning(
                f"Unknown synth type: {self.current_synth_type}, defaulting to DIGITAL_PRESETS"
            )
            return DIGITAL_PRESETS_ENUMERATED  # Safe fallback
        return presets

    def _get_preset_handler_for_current_synth(self):
        """Return the appropriate preset handler based on the current synth type."""
        handler_map = {
            PresetType.ANALOG: self.analog_preset_handler,
            PresetType.DIGITAL_1: self.digital_1_preset_handler,
            PresetType.DIGITAL_2: self.digital_2_preset_handler,
            PresetType.DRUMS: self.drums_preset_handler,
        }

        handler = handler_map.get(self.current_synth_type, None)
        if handler is None:
            logging.warning(
                f"Unknown synth type: {self.current_synth_type}, defaulting to digital_1_preset_handler"
            )
            return self.digital_1_preset_handler  # Safe fallback
        return handler

    def _previous_tone(self):
        """Decrement the tone index and update the display."""
        if self.current_preset_index <= 0:
            logging.info("Already at the first preset.")
            return

        self.current_preset_index -= 1
        presets = self._get_presets_for_current_synth()
        preset_handler = self._get_preset_handler_for_current_synth()

        self._update_display_preset(
            self.current_preset_index,
            presets[self.current_preset_index],
            self.channel,
        )

        preset_data = {
            "type": self.current_synth_type,
            "selpreset": self.current_preset_index + 1,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        self.load_preset(preset_data)

    def _next_tone(self):
        """Increment the tone index and update the display."""
        max_index = len(self._get_presets_for_current_synth()) - 1
        if self.current_preset_index >= max_index:
            logging.info("Already at the last preset.")
            return

        self.current_preset_index += 1
        presets = self._get_presets_for_current_synth()
        preset_handler = self._get_preset_handler_for_current_synth()

        self._update_display_preset(
            self.current_preset_index,
            presets[self.current_preset_index],
            self.channel,
        )

        preset_data = {
            "type": self.current_synth_type,
            "selpreset": self.current_preset_index + 1,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        self.load_preset(preset_data)

    def update_display_callback(self, synth_type, preset_index, channel):
        """Update the display for the given synth type and preset index."""
        logging.info(
            "update_display_callback: synth_type, preset_index, channel",
            synth_type,
            preset_index,
            channel,
        )
        preset_map = {
            PresetType.ANALOG: ANALOG_PRESETS_ENUMERATED,
            PresetType.DIGITAL_1: DIGITAL_PRESETS_ENUMERATED,
            PresetType.DIGITAL_2: DIGITAL_PRESETS_ENUMERATED,
            PresetType.DRUMS: DRUM_PRESETS_ENUMERATED,
        }

        # Default to DIGITAL_PRESETS_ENUMERATED if the synth_type is not found in the map
        presets = preset_map.get(synth_type, DIGITAL_PRESETS_ENUMERATED)

        self._update_display_preset(
            preset_index,
            presets[preset_index],
            channel,
        )

    def show_editor(self, editor_type: str):
        """Show the specified editor window"""
        editor_map = {
            "vocal_fx": self._show_vocal_fx,
            "digital1": self._show_digital_synth_editor,
            "digital2": self._show_digital_synth_editor,
            "analog": self._show_analog_synth_editor,
            "drums": self._show_drums_editor,
            "arpeggio": self._show_arpeggio_editor,
            "effects": self._open_effects,
            "pattern": self._open_pattern,
        }

        if editor_type in editor_map:
            editor_map[editor_type](editor_type)
        else:
            logging.info(f"Unknown editor type: {editor_type}")

    def _show_vocal_fx(self, editor_type: str):
        if not hasattr(self, "vocal_fx_editor"):
            self.vocal_fx_editor = VocalFXEditor(self.midi_helper, self)
            self.vocal_fx_editor.show()
            self.vocal_fx_editor.raise_()

    def _show_digital_synth_editor(self, editor_type: str):
        synth_num = 1 if editor_type == "digital1" else 2
        self._show_editor(
            f"Digital Synth {synth_num}", DigitalSynthEditor, synth_num=synth_num
        )
        self.preset_type = (
            PresetType.DIGITAL_1 if synth_num == 1 else PresetType.DIGITAL_2
        )
        if synth_num == 1:
            messages = [
                "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7",
                "F0 41 10 00 00 00 0E 11 19 01 20 00 00 00 00 3D 09 F7",
                "F0 41 10 00 00 00 0E 11 19 01 21 00 00 00 00 3D 08 F7",
                "F0 41 10 00 00 00 0E 11 19 01 22 00 00 00 00 3D 07 F7",
                "F0 41 10 00 00 00 0E 11 19 01 50 00 00 00 00 25 71 F7",
            ]
            for message in messages:
                self._send_midi_message(message)

    def _show_analog_synth_editor(self, editor_type: str):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        self.preset_type = PresetType.ANALOG

    def _show_drums_editor(self, editor_type: str):
        self._show_editor("Drums", DrumEditor)
        self.preset_type = PresetType.DRUMS

    def _show_arpeggio_editor(self, editor_type: str):
        self._show_editor("Arpeggio", ArpeggioEditor)

    def _open_effects(self, editor_type: str):
        self._show_editor("Effects", EffectsEditor)

    def _open_pattern(self, editor_type: str):
        self._show_editor("Pattern", PatternSequencer)

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

    def _create_tone_buttons_row(self):
        # Create Tone navigation buttons
        self.tone_label = QLabel("Tone")
        self.tone_down_button = QPushButton("-")
        self.spacer = QLabel(" ")
        self.tone_up_button = QPushButton("+")

        # Calculate size for tone buttons
        tone_button_diameter = 25

        # Create tone up button
        self.tone_up_button.setFixedSize(tone_button_diameter, tone_button_diameter)
        self.tone_up_button.setStyleSheet(Style.TONE_BUTTON_STYLE)

        # Create tone down button
        self.tone_down_button.setFixedSize(tone_button_diameter, tone_button_diameter)
        self.tone_down_button.setStyleSheet(Style.TONE_BUTTON_STYLE)

        # Connect buttons to functions
        self.tone_down_button.clicked.connect(self._previous_tone)
        self.tone_up_button.clicked.connect(self._next_tone)

        button_label_layout = QHBoxLayout()
        button_label_layout.addStretch()
        button_label_layout.addWidget(self.tone_label)
        button_label_layout.addStretch()
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.tone_down_button)
        button_layout.addWidget(self.spacer)
        button_layout.addWidget(self.tone_up_button)
        button_layout.addStretch()
        return button_layout

    def _create_favorite_buttons_row(self):
        """Create a row with label and circular button"""
        text = "Favorites"
        row = QHBoxLayout()
        row.setSpacing(10)

        # Add label with color based on text
        label = QLabel(text)
        if text == "Analog Synth":
            label.setStyleSheet(Style.ANALOG_SYNTH_PART_LABEL_STYLE)
        else:
            label.setStyleSheet(Style.SYNTH_PART_LABEL_STYLE)
        # row.addWidget(label)
        # Add spacer to push button to right
        row.addStretch()
        # Add button
        self.favourites_button = QPushButton()
        self.favourites_button.setFixedSize(30, 30)
        self.favourites_button.setCheckable(True)
        # button.clicked.connect(slot)
        # Style the button with brighter hover/pressed/selected  states
        self.favourites_button.setStyleSheet(Style.BUTTON_STYLE)
        row.addWidget(self.favourites_button)
        return row

    def _create_sequencer_buttons_row(self):
        """Create a row with label and circular button"""
        row = QHBoxLayout()
        self.sequencer_buttons = []

        grid = QGridLayout()
        for i in range(16):
            button = QPushButton()
            button.setFixedSize(25, 25)
            button.setCheckable(True)  # Ensure the button is checkable
            button.setStyleSheet(sequencer_button_style(button.isChecked()))
            button.toggled.connect(
                lambda checked, btn=button: toggle_button_style(btn, checked)
            )
            button.clicked.connect(lambda _, idx=i: self._save_favorite(idx))
            grid.addWidget(button, 0, i)  # Row 0, column i with spacing
            grid.setHorizontalSpacing(2)  # Add spacing between columns
            self.sequencer_buttons.append(button)
        row.addLayout(grid)

        return row

    def _save_favorite(self, index):
        """Save the current preset as a favorite"""
        settings = QSettings("YourCompany", "YourApp")
        preset_name = f"favorite_{index + 1:02d}"
        # Assuming you have a method to get the current preset
        current_preset = self._get_current_preset()
        settings.setValue(preset_name, current_preset)
        logging.info(f"Saved {current_preset} as {preset_name}")
        logging.debug(f"Saved {current_preset} as {preset_name}")

    def _get_current_preset(self):
        """Retrieve the current preset"""
        try:
            # Update the current preset index or details here
            preset_number = self.current_preset_index
            preset_name = self._get_current_preset_name()
            preset_type = self._get_current_preset_type()

            # Format the preset data
            current_preset = {
                "number": preset_number,
                "name": preset_name,
                "type": preset_type,
            }

            logging.debug(f"Current preset retrieved: {current_preset}")
            return current_preset

        except Exception as e:
            logging.error(f"Error retrieving current preset: {str(e)}")
            return None

    def _get_current_preset_name(self):
        """Get the name of the currently selected preset"""
        try:
            preset_type = self.current_synth_type
            preset_number = self.current_preset_index
            preset_map = {
                PresetType.ANALOG: ANALOG_PRESETS_ENUMERATED,
                PresetType.DIGITAL_1: DIGITAL_PRESETS_ENUMERATED,
                PresetType.DIGITAL_2: DIGITAL_PRESETS_ENUMERATED,
                PresetType.DRUMS: DRUM_PRESETS_ENUMERATED,
            }
            # Default to DIGITAL_PRESETS_ENUMERATED if the synth_type is not found in the map
            presets = preset_map.get(preset_type, DIGITAL_PRESETS_ENUMERATED)
            preset_name = presets[preset_number]
            logging.info(f"preset_name: {preset_name}")
            return preset_name
        except IndexError:
            return "Index Error for current preset"

    def _get_current_preset_name_from_settings(self):
        """Get the name of the currently selected preset"""
        try:
            synth_type = self.settings.value(
                "last_preset/synth_type", PresetType.ANALOG
            )
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)

            # Get preset name - adjust index to be 0-based
            if synth_type == PresetType.ANALOG:
                return AN_PRESETS[preset_num - 1]  # Convert 1-based to 0-based
            elif synth_type == PresetType.DIGITAL_1:
                return DIGITAL_PRESETS_ENUMERATED[preset_num - 1]
            elif synth_type == PresetType.DIGITAL_2:
                return DIGITAL_PRESETS_ENUMERATED[preset_num - 1]
            else:
                return DRUM_PRESETS_ENUMERATED[preset_num - 1]
        except IndexError:
            return "INIT PATCH"

    def _get_current_preset_type(self):
        """Get the type of the currently selected preset"""
        return self.settings.value("last_preset/synth_type", PresetType.ANALOG)

    def _create_section(self, title):
        """Create a section frame with title"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(150)

        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont(self.font().family(), 12, QFont.Bold))
        layout.addWidget(title_label)

        return frame

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

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

        # Synth menu - reordered to match buttons
        synth_menu = menubar.addMenu("Synth")

        digital1_action = QAction("Digital Synth 1", self)
        digital1_action.triggered.connect(self._open_digital_synth1)
        synth_menu.addAction(digital1_action)

        digital2_action = QAction("Digital Synth 2", self)
        digital2_action.triggered.connect(self._open_digital_synth2)
        synth_menu.addAction(digital2_action)

        drums_action = QAction("Drums", self)
        drums_action.triggered.connect(self._open_drums)
        synth_menu.addAction(drums_action)

        analog_action = QAction("Analog Synth", self)
        analog_action.triggered.connect(self._open_analog_synth)

        synth_menu.addAction(analog_action)

        pattern_action = QAction("Pattern Sequencer", self)
        pattern_action.triggered.connect(self._open_pattern)
        synth_menu.addAction(pattern_action)

        # Effects menu
        fx_menu = menubar.addMenu("Effects")

        arp_action = QAction("Arpeggiator", self)
        arp_action.triggered.connect(self._open_arpeggiator)
        fx_menu.addAction(arp_action)

        effects_action = QAction("Effects", self)
        effects_action.triggered.connect(self._open_effects)
        fx_menu.addAction(effects_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        log_viewer_action = QAction("Log Viewer", self)
        log_viewer_action.triggered.connect(self._show_log_viewer)
        help_menu.addAction(log_viewer_action)

        # Add Edit menu
        # edit_menu = menubar.addMenu("Edit")

        # Add Patch Name action
        edit_name_action = QAction("Edit Patch Name", self)
        edit_name_action.triggered.connect(self._edit_patch_name)
        edit_menu.addAction(edit_name_action)

        # Add Presets menu
        # presets_menu = self.menuBar().addMenu("&Presets")

        presets_action = edit_menu.addAction("&Presets")
        presets_action.triggered.connect(self._show_analog_presets)

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

    def _show_midi_config(self):
        """Show MIDI configuration dialog"""
        try:
            # Get available ports using instance method
            input_ports = self.midi_helper.get_input_ports()  # Use instance method
            output_ports = self.midi_helper.get_output_ports()  # Use instance method

            dialog = MIDIConfigDialog(
                input_ports,
                output_ports,
                self.midi_helper.current_in_port,
                self.midi_helper.current_out_port,
                parent=self,
            )

            if dialog.exec():
                in_port = dialog.get_input_port()
                out_port = dialog.get_output_port()

                # Open selected ports using instance methods
                if in_port:
                    self.midi_helper.open_input_port(in_port)
                if out_port:
                    self.midi_helper.open_output_port(out_port)

        except Exception as e:
            logging.error(f"Error showing MIDI configuration: {str(e)}")
            self.show_error("MIDI Configuration Error", str(e))

    def _update_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out

        # Save settings
        if midi_in and midi_out:
            self.settings.setValue("midi/input_port", midi_in.port_name)
            self.settings.setValue("midi/output_port", midi_out.port_name)

    def _load_settings(self):
        """Load application settings"""
        try:
            if hasattr(self, "settings"):
                # Load MIDI port settings
                input_port = self.settings.value("midi_in", "")
                output_port = self.settings.value("midi_out", "")

                # Load window geometry
                geometry = self.settings.value("geometry")
                if geometry:
                    self.restoreGeometry(geometry)

                # Load preset info
                self.current_preset_num = int(self.settings.value("preset_num", 1))
                self.current_preset_name = self.settings.value(
                    "preset_name", "INIT PATCH"
                )

                # Try to open MIDI ports if they were saved
                if input_port and output_port:
                    self._set_midi_ports(input_port, output_port)

                logging.debug("Settings loaded successfully")

        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")

    def _show_editor(self, title, editor_class, **kwargs):
        """Show editor window"""
        try:
            # Create editor with proper initialization
            if editor_class in [
                DigitalSynthEditor,
                DrumEditor,
                AnalogSynthEditor,
                PatternSequencer,
            ]:
                editor = editor_class(
                    midi_helper=self.midi_helper, parent=self, **kwargs
                )
            else:
                # For other editors, use existing initialization
                editor = editor_class(midi_out=self.midi_out, **kwargs)

            # Set window title
            editor.setWindowTitle(title)

            # Store reference and show
            if title == "Digital Synth 1":
                self.digital_synth1 = editor
            elif title == "Digital Synth 2":
                self.digital_synth2 = editor
            elif title == "Analog Synth":
                self.analog_synth = editor
            elif title == "Drum Kit":
                self.drum_kit = editor
            elif title == "Effects":
                self.effects = editor
            elif title == "Pattern":
                self.effects = editor

            # Show editor
            editor.show()
            editor.raise_()

        except Exception as e:
            logging.error(f"Error showing {title} editor: {str(e)}")

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages and flash indicator"""
        self.midi_in_indicator.flash()

    def _open_analog_synth(self):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        self.preset_type = PresetType.ANALOG
        self.current_synth_type = PresetType.ANALOG
        self.midi_helper.send_program_change(
            channel=MIDI_CHANNEL_ANALOG, program=1
        )  # Program 1 for now
        self.piano_keyboard.set_midi_channel(MIDI_CHANNEL_ANALOG)

    def _open_digital_synth1(self):
        """Open the Digital Synth 1 editor and send SysEx message."""
        self.current_synth_type = PresetType.DIGITAL_1
        try:
            if not hasattr(self, "digital_synth1_editor"):
                self.digital_synth1_editor = DigitalSynthEditor(
                    midi_helper=self.midi_helper, parent=self
                )
            self.digital_synth1_editor.show()
            self.digital_synth1_editor.raise_()
            self.piano_keyboard.set_midi_channel(0)
            self.midi_helper.send_program_change(
                channel=MIDI_CHANNEL_DIGITAL1, program=1
            )  # Program 1 for now
            self.midi_helper.send_bank_and_program_change(
                channel=MIDI_CHANNEL_DIGITAL1, bank_msb=87, bank_lsb=0, program=1
            )
            # Send the SysEx message
            sysex_msg = [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x11,
                0x19,
                0x01,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x40,
                0x26,
                0xF7,
            ]
            self.midi_helper.send_message(sysex_msg)
            logging.debug("Sent SysEx message for Digital Synth 1")

        except Exception as e:
            logging.error(f"Error opening Digital Synth 1 editor: {str(e)}")

    def _open_digital_synth2(self):
        self._show_editor("Digital Synth 2", DigitalSynthEditor, synth_num=2)
        self.preset_type = PresetType.DIGITAL_2
        self.current_synth_type = PresetType.DIGITAL_2
        self.midi_helper.send_program_change(
            channel=MIDI_CHANNEL_DIGITAL2, program=1
        )  # Program 1 for now
        self.piano_keyboard.set_midi_channel(MIDI_CHANNEL_DIGITAL2)

    def _open_drums(self):
        self._show_editor("Drums", DrumEditor)
        # self._show_drums_editor()
        self.preset_type = PresetType.DRUMS
        self.current_synth_type = PresetType.DRUMS
        self.midi_helper.send_program_change(
            channel=MIDI_CHANNEL_DRUMS, program=1
        )  # Program 1 for now
        self.piano_keyboard.set_midi_channel(MIDI_CHANNEL_DRUMS)

    def _open_arpeggiator(self):
        """Show the arpeggiator editor window"""
        try:
            if not hasattr(self, "arpeggiator"):
                self.arpeggiator = ArpeggioEditor(
                    midi_helper=self.midi_helper,  # Pass midi_helper instance
                    parent=self,
                )
            self.arpeggiator.show()
            self.arpeggiator.raise_()

        except Exception as e:
            logging.error(f"Error showing Arpeggiator editor: {str(e)}")

    def _open_effects(self):
        """Show the effects editor window"""
        try:
            if not hasattr(self, "effects_editor"):
                self.effects_editor = EffectsEditor(
                    midi_helper=self.midi_helper,  # Pass midi_helper instead of midi_out
                    parent=self,
                )
            self.effects_editor.show()
            self.effects_editor.raise_()

        except Exception as e:
            logging.error(f"Error showing Effects editor: {str(e)}")

    def _load_patch(self):
        """Show load patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper, parent=self, save_mode=False
            )
            patch_manager.show()
        except Exception as e:
            logging.error(f"Error loading patch: {str(e)}")

    def _save_patch(self):
        """Show save patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper, parent=self, save_mode=True
            )
            patch_manager.show()
        except Exception as e:
            logging.error(f"Error saving patch: {str(e)}")

    def _apply_patch(self, patch_data):
        """Apply loaded patch data"""
        # TODO: Implement patch loading
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Properly delete MIDI ports
            if self.midi_in:
                self.midi_in.delete()  # Use delete() instead of close()
            if self.midi_out:
                self.midi_out.delete()  # Use delete() instead of close()

            # Save settings
            self._save_settings()

            # Accept the event
            event.accept()

        except Exception as e:
            logging.error(f"Error during close event: {str(e)}")
            event.ignore()

    def set_log_file(self, log_file: str):
        """
        :param log_file: str
        """
        self.log_file = log_file

    def _show_log_viewer(self):
        """Show log viewer window"""
        if not self.log_viewer:
            self.log_viewer = LogViewer(midi_helper=self.midi_helper, parent=self)
        self.log_viewer.show()
        self.log_viewer.raise_()
        logging.debug("Showing LogViewer window")

    def _create_button_row(self, text, slot):
        """Create a row with label and circular button"""
        row = QHBoxLayout()
        row.setSpacing(10)

        # Add label with color based on text
        label = QLabel(text)
        if text == "Analog Synth":
            label.setStyleSheet(Style.ANALOG_SYNTH_PART_LABEL_STYLE)
        else:
            label.setStyleSheet(Style.SYNTH_PART_LABEL_STYLE)
        row.addWidget(label)

        # Add spacer to push button to right
        row.addStretch()

        # Add button
        button = QPushButton()
        button.setFixedSize(30, 30)
        button.setCheckable(True)
        button.clicked.connect(slot)

        # Style the button with brighter hover/pressed/selected  states
        button.setStyleSheet(Style.BUTTON_STYLE)

        row.addWidget(button)
        return row, button

    def add_arpeggiator_buttons(self, widget):
        """Add arpeggiator up/down buttons to the interface"""
        # Create container
        arpeggiator_buttons_container = QWidget(widget)

        # Position to align with sequencer but 25% higher (increased from 20%)
        seq_y = self.height - 50 - self.height * 0.1  # Base sequencer Y position
        offset_y = self.height * 0.25  # 25% of window height (increased from 0.2)
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
        arpeggiator_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """
        )
        arpeggiator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arpeggiator_layout.addWidget(arpeggiator_label)

        # Create horizontal layout for Down/Up labels
        labels_row = QHBoxLayout()
        labels_row.setSpacing(20)  # Space between labels

        # On label
        on_label = QLabel("On")
        on_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """
        )
        labels_row.addWidget(on_label)

        # Add labels row
        arpeggiator_layout.addLayout(labels_row)

        # Create horizontal layout for buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(20)  # Space between buttons

        # Down label
        key_hold_label = QLabel("Key Hold")
        key_hold_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """
        )
        labels_row.addWidget(key_hold_label)

        # Create and store arpeggiator  button
        self.arpeggiator_button = QPushButton()
        self.arpeggiator_button.setFixedSize(30, 30)
        self.arpeggiator_button.setCheckable(True)
        self.arpeggiator_button.clicked.connect(
            lambda checked: self._send_arp_on_off(checked)
        )
        self.arpeggiator_button.setStyleSheet(
            """
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """
        )
        buttons_row.addWidget(self.arpeggiator_button)

        # Create and store octave down button
        self.key_hold = QPushButton()
        self.key_hold.setFixedSize(30, 30)
        self.key_hold.setCheckable(True)
        self.key_hold.clicked.connect(lambda checked: self._send_arp_key_hold(checked))
        self.key_hold.setStyleSheet(
            """
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """
        )
        buttons_row.addWidget(self.key_hold)

        # Add buttons row
        arpeggiator_layout.addLayout(buttons_row)

        # Make container transparent
        arpeggiator_buttons_container.setStyleSheet("background: transparent;")

    def add_octave_buttons(self, widget):
        """Add octave up/down buttons to the interface"""
        # Create container
        octave_buttons_container = QWidget(widget)

        # Position to align with sequencer but 25% higher (increased from 20%)
        seq_y = self.height - 50 - self.height * 0.1  # Base sequencer Y position
        offset_y = self.height * 0.25  # 25% of window height (increased from 0.2)
        octave_x = self.width - self.width * 0.8 - 150  # Position left of sequencer

        # Apply the height offset to the Y position
        octave_buttons_container.setGeometry(
            octave_x,
            seq_y - 60 - offset_y,  # Move up by offset_y (now 25% instead of 20%)
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
        octave_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """
        )
        octave_label.setAlignment(Qt.AlignCenter)
        octave_layout.addWidget(octave_label)

        # Down label
        down_label = QLabel("Down")
        down_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """
        )
        labels_row.addWidget(down_label)

        # Up label
        up_label = QLabel("Up")
        up_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 13px;
            color: #d51e35;
            font-weight: bold;
        """
        )
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
        self.octave_down.setStyleSheet(
            """
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """
        )
        buttons_row.addWidget(self.octave_down)

        # Create and store octave up button
        self.octave_up = QPushButton()
        self.octave_up.setFixedSize(30, 30)
        self.octave_up.setCheckable(True)
        self.octave_up.clicked.connect(lambda: self._send_octave(1))
        self.octave_up.setStyleSheet(
            """
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
        """
        )
        buttons_row.addWidget(self.octave_up)

        # Add buttons row
        octave_layout.addLayout(buttons_row)

        # Make container transparent
        octave_buttons_container.setStyleSheet("background: transparent;")

    def _add_overlaid_controls(self, central_widget):
        """Add interactive controls overlaid on the JD-Xi image"""
        # Create absolute positioning layout
        central_widget.setLayout(QVBoxLayout())

        # Parts Select section with Arpeggiator
        parts_container = QWidget(central_widget)
        parts_x = self.display_x + self.display_width + 30
        parts_y = self.display_y - (
            self.height * 0.15
        )  # Move up by 20% of window height

        parts_container.setGeometry(parts_x, parts_y, 220, 250)
        parts_layout = QVBoxLayout(parts_container)
        parts_layout.setSpacing(15)  # Increased from 5 to 15 for more vertical spacing

        # Add Parts Select label
        parts_label = QLabel("Parts Select")
        parts_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
            padding-bottom: 10px;
        """
        )
        parts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parts_layout.addWidget(parts_label)

        # Parts buttons
        digital1_row, self.digital1_button = self._create_button_row(
            "Digital Synth 1", self._open_digital_synth1
        )
        digital2_row, self.digital2_button = self._create_button_row(
            "Digital Synth 2", self._open_digital_synth2
        )
        drums_row, self.drums_button = self._create_button_row(
            "Drums", self._open_drums
        )
        analog_row, self.analog_button = self._create_button_row(
            "Analog Synth", self._open_analog_synth
        )
        arp_row, self.arp_button = self._create_button_row(
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

        # Create a button group
        button_group = QButtonGroup()
        button_group.addButton(self.digital1_button)
        button_group.addButton(self.digital2_button)
        button_group.addButton(self.analog_button)
        button_group.addButton(self.drums_button)

        # Ensure only one button can be checked at a time
        button_group.setExclusive(True)

        parts_layout.addLayout(digital1_row)
        parts_layout.addLayout(digital2_row)
        parts_layout.addLayout(drums_row)
        parts_layout.addLayout(analog_row)
        parts_layout.addLayout(arp_row)

        self.add_octave_buttons(central_widget)
        self.add_arpeggiator_buttons(central_widget)

        # Effects button in top row
        fx_container = QWidget(central_widget)
        fx_container.setGeometry(self.width - 200, self.margin + 25, 150, 50)
        fx_layout = QHBoxLayout(fx_container)

        effects_row, self.effects_button = self._create_button_row(
            "Effects", self._open_effects
        )
        fx_layout.addLayout(effects_row)

        ###### For tone buttons ######
        # Effects button in top row
        tone_container = QWidget(central_widget)
        tone_container.setGeometry(self.width - 525, self.margin + 15, 150, 100)
        tone_container_layout = QVBoxLayout(tone_container)
        tone_label_layout = QHBoxLayout()
        tone_label = QLabel("Tone")
        tone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tone_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """
        )
        tone_label_layout.addWidget(tone_label)
        tone_container_layout.addLayout(tone_label_layout)
        tone_layout = QHBoxLayout()
        tone_row = self._create_tone_buttons_row()
        tone_layout.addLayout(tone_row)
        tone_container_layout.addLayout(tone_layout)

        # Beginning of sequencer section
        sequencer_container = QWidget(central_widget)
        sequencer_container.setGeometry(self.width - 540, self.margin + 150, 650, 100)
        sequencer_container_layout = QVBoxLayout(sequencer_container)
        sequencer_label_layout = QHBoxLayout()
        sequencer_label = QLabel("Sequencer")
        sequencer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sequencer_label.setStyleSheet(
            """
            font-family: "Myriad Pro", Arial;
            font-size: 14px;
            color: #d51e35;
            font-weight: bold;
            background: transparent;
        """
        )
        # sequencer_label_layout.addWidget(sequencer_label)
        # sequencer_container_layout.addLayout(sequencer_label_layout)
        sequencer_layout = QHBoxLayout()
        seq_width = 400  # Approximate width for sequencer
        favorites_button_row = self._create_favorite_buttons_row()
        sequencer = self._create_sequencer_buttons_row()
        sequencer_layout.addLayout(sequencer)
        # sequencer_container_layout.addLayout(favorites_button_row)
        sequencer_container_layout.addLayout(sequencer_layout)
        # End of sequencer section

        # Make containers transparent
        parts_container.setStyleSheet("background: transparent;")
        fx_container.setStyleSheet("background: transparent;")

        # Calculate keyboard dimensions
        key_width = self.width * 0.8 / 25  # keyboard_width/25
        key_height = 127  # white_key_height
        keyboard_y = self.height - key_height - (self.height * 0.1) + (key_height * 0.3)
        keyboard_start = self.width - (self.width * 0.8) - self.margin - 20

        # Add white keys C1 to F5
        white_notes = [
            36,
            38,
            40,
            41,
            43,
            45,
            47,  # C1 to B1
            48,
            50,
            52,
            53,
            55,
            57,
            59,  # C2 to B2
            60,
            62,
            64,
            65,
            67,
            69,
            71,  # C3 to B3
            72,
            74,
            76,
            77,
            79,
            81,
            83,  # C4 to B4
            84,
            86,
            88,
            89,  # C5 to F5
        ]

        # for i, note in enumerate(white_notes):
        #    x_pos = keyboard_start + i * key_width
        #    self._add_piano_key(widget, False, note, x_pos, keyboard_y, key_width, key_height)

        # Add black keys
        black_notes = [
            37,
            39,
            None,
            42,
            44,
            46,  # C#1 to B1
            49,
            51,
            None,
            54,
            56,
            58,  # C#2 to B2
            61,
            63,
            None,
            66,
            68,
            70,  # C#3 to B3
            73,
            75,
            None,
            78,
            80,
            82,  # C#4 to B4
            85,
            87,
            None,
            90,  # C#5 to F#5
        ]

        black_positions = [
            0,
            1,
            3,
            4,
            5,
            7,
            8,
            10,
            11,
            12,
            14,
            15,
            17,
            18,
            19,
            21,
            22,
            24,
            25,
            26,
            28,
            29,
            31,
            32,
        ]  # Extended positions

        # for pos, note in zip(black_positions, [n for n in black_notes if n is not None]):
        #    x_pos = keyboard_start + pos * key_width + key_width/2
        #    self._add_piano_key(widget, True, note, x_pos, keyboard_y, key_width, key_height)

    def _add_piano_key(
        self, widget, is_black, note_number, x_pos, keyboard_y, key_width, key_height
    ):
        """Helper to create a piano key button"""
        button = QPushButton(widget)

        if is_black:
            width = key_width * 0.6
            height = 80
            style = """
                QPushButton {
                    background-color: black;
                    border: 1px solid black;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                }
                QPushButton:pressed {
                    background-color: #333333;
                }
            """
        else:
            width = key_width - 1
            height = key_height
            style = """
                QPushButton {
                    background-color: white;
                    border: 1px solid black;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
            """

        button.setGeometry(int(x_pos), int(keyboard_y), int(width), int(height))
        button.setStyleSheet(style)

        def key_pressed():
            if self.midi_helper:
                handler = self._get_preset_handler_for_current_synth()
                self.midi_helper.send_note_on(
                    note=note_number, velocity=1, channel=handler.channel
                )
                logging.debug(f"Sent MIDI Note On {note_number} velocity 1")

        def key_released():
            if self.midi_helper:
                handler = self._get_preset_handler_for_current_synth()
                self.midi_helper.send_note_off(
                    note=note_number, velocity=5, channel=handler.channel
                )
                logging.debug(f"Sent MIDI Note Off {note_number} velocity 5")

        # Connect to mouse events instead of clicked
        button.pressed.connect(key_pressed)
        button.released.connect(key_released)

    def _send_octave(self, direction):
        """Send octave change MIDI message"""
        if self.midi_helper:
            # Update octave tracking
            self.current_octave = max(-3, min(3, self.current_octave + direction))

            # Update button states
            self.octave_down.setChecked(self.current_octave < 0)
            self.octave_up.setChecked(self.current_octave > 0)

            # Update display
            self._update_display()

            # Map octave value to correct SysEx value
            # -3 = 0x3D, -2 = 0x3E, -1 = 0x3F, 0 = 0x40, +1 = 0x41, +2 = 0x42, +3 = 0x43
            octave_value = 0x40 + self.current_octave  # 0x40 is center octave

            # Calculate checksum
            checksum = 0x19 + 0x01 + 0x00 + 0x15 + octave_value
            checksum = (0x80 - (checksum & 0x7F)) & 0x7F

            # Create SysEx message
            sysex_msg = [
                0xF0,  # Start of SysEx
                0x41,  # Roland ID
                0x10,  # Device ID
                0x00,
                0x00,
                0x00,
                0x0E,  # Model ID
                0x12,  # Command ID (DT1)
                0x19,  # Address 1
                0x01,  # Address 2
                0x00,  # Address 3
                0x15,  # Address 4
                octave_value,  # Parameter value
                checksum,  # Checksum
                0xF7,  # End of SysEx
            ]

            self.midi_helper.send_message(sysex_msg)
            logging.debug(
                f"Sent octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})"
            )

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
        pixmap = draw_instrument_pixmap(
            digital_font_family=(
                self.digital_font_family
                if hasattr(self, "digital_font_family")
                else None
            ),
            current_octave=self.current_octave,
            preset_num=self.current_preset_num,
            preset_name=self.current_preset_name,
        )
        if hasattr(self, "image_label"):
            self.image_label.setPixmap(pixmap)

    def _load_digital_font(self):
        """Load the digital LCD font for the display"""
        import os

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
            except Exception as e:
                logging.exception(
                    f"Error loading {font_name} font from {font_path}: {e}"
                )
        else:
            logging.debug(f"File not found: {font_path}")

    def _send_arp_key_hold(self, state):
        """Send arpeggiator key hold (latch) command"""
        try:
            if self.midi_helper:
                # Value: 0 = OFF, 1 = ON
                value = 0x01 if state else 0x00

                # Create SysEx message using constants
                sysex_msg = [
                    START_OF_SYSEX,
                    ROLAND_ID,
                    DEVICE_ID,
                    MODEL_ID_1,
                    MODEL_ID_2,
                    MODEL_ID_3,
                    JD_XI_ID,
                    DT1_COMMAND_12,
                    TEMPORARY_PROGRAM_AREA,  # Arpeggio area
                    0x00,  # Subgroup
                    0x00,  # Part
                    0x02,  # Key Hold parameter
                    value,  # Parameter value
                ]

                # Calculate checksum (sum all data bytes)
                checksum = sum(sysex_msg[8:-1]) & 0x7F  # From address to value
                checksum = (128 - checksum) & 0x7F

                # Add checksum and end of sysex
                sysex_msg.extend([checksum, END_OF_SYSEX])

                # Send message
                self.midi_helper.send_message(bytes(sysex_msg))
                logging.debug(f"Sent arpeggiator key hold: {'ON' if state else 'OFF'}")

        except Exception as e:
            logging.error(f"Error sending arp key hold: {str(e)}")

    def _send_arp_on_off(self, state):
        """Send arpeggiator on/off command"""
        try:
            if self.midi_helper:
                value = 0x01 if state else 0x00  # 1 = ON, 0 = OFF

                # Ensure all constants are integers
                sysex_msg = [
                    int(START_OF_SYSEX),
                    int(ROLAND_ID),
                    int(DEVICE_ID),
                    int(MODEL_ID_1),
                    int(MODEL_ID_2),
                    int(MODEL_ID_3),
                    int(JD_XI_ID),
                    int(DT1_COMMAND_12),
                    TEMPORARY_PROGRAM_AREA,  # Temporary area
                    ARP_PART,  # Part
                    ARP_GROUP,  # Part
                    0x03,  # On/Off parameter
                    int(value),  # Parameter value
                ]

                # Calculate checksum
                checksum = sum(sysex_msg[8:]) & 0x7F  # Sum from address to value
                checksum = (128 - checksum) & 0x7F  # Roland's checksum formula

                # Add checksum and end of sysex
                sysex_msg.append(checksum)
                sysex_msg.append(int(END_OF_SYSEX))

                # Validate all elements are integers
                assert all(
                    isinstance(x, int) for x in sysex_msg
                ), "Non-integer found in sysex_msg"

                # Send message
                self.midi_helper.send_message(sysex_msg)  # No need for bytearray()
                logging.debug(f"Sent arpeggiator on/off: {'ON' if state else 'OFF'}")

        except Exception as e:
            logging.error(f"Error sending arp on/off: {str(e)}")

    def _open_midi_debugger(self):
        """Open MIDI debugger window"""
        if not self.midi_helper:
            logging.error("MIDI helper not initialized")
            return
        """    
        if not self.midi_helper.midi_out:
            logging.warning("No MIDI output port set")
            # Show MIDI config dialog
            self._show_midi_config()
            return
        """
        if not self.midi_debugger:
            self.midi_debugger = MIDIDebugger(self.midi_helper)
            # Clean up reference when window is closed
            self.midi_debugger.setAttribute(Qt.WA_DeleteOnClose)
            self.midi_debugger.destroyed.connect(self._midi_debugger_closed)
            logging.debug("Created new MIDI debugger window")
        self.midi_debugger.show()
        self.midi_debugger.raise_()

    def _midi_debugger_closed(self):
        """Handle MIDI debugger window closure"""
        self.midi_debugger = None

    def _open_log_viewer(self):
        """Show log viewer window"""
        if not self.log_viewer:
            self.log_viewer = LogViewer(midi_helper=self.midi_helper, parent=self)
        self.log_viewer.show()
        self.log_viewer.raise_()
        logging.debug("Showing LogViewer window")

    def _log_viewer_closed(self):
        """Handle log viewer window closure"""
        self.log_viewer = None

    def _set_midi_ports(self, in_port, out_port):
        """Set MIDI input and output ports"""
        try:
            # Close existing ports
            if self.midi_in:
                self.midi_in.delete()  # Use delete() instead of close()
            if self.midi_out:
                self.midi_out.delete()  # Use delete() instead of close()

            # Open new ports
            self.midi_in = MIDIHelper.open_input(in_port, self)
            self.midi_out = MIDIHelper.open_output(out_port, self)

            # Store port names
            self.midi_in_port_name = in_port
            self.midi_out_port_name = out_port

            # Initialize singleton connection
            MIDIConnection().initialize(self.midi_in, self.midi_out, self)

            # Update MIDI helper
            self.midi_helper.midi_in = self.midi_in
            self.midi_helper.midi_out = self.midi_out

            # Set up MIDI input callback
            if self.midi_in:
                self.midi_in.set_callback(self._handle_midi_message)

            # Update indicators
            self.midi_in_indicator.set_active(self.midi_in is not None)
            self.midi_out_indicator.set_active(self.midi_out is not None)

            # Save settings
            if self.midi_in and self.midi_out:
                self.settings.setValue("midi_in", in_port)
                self.settings.setValue("midi_out", out_port)
                logging.info(f"MIDI ports configured - In: {in_port}, Out: {out_port}")
            else:
                logging.warning("Failed to configure MIDI ports")

        except Exception as e:
            logging.error(f"Error setting MIDI ports: {str(e)}")

    def _open_midi_message_debug(self):
        """Open MIDI message debug window"""
        if not self.midi_message_debug:
            self.midi_message_debug = MIDIMessageDebug()
            self.midi_message_debug.setAttribute(Qt.WA_DeleteOnClose)
            self.midi_message_debug.destroyed.connect(self._midi_message_debug_closed)
        self.midi_message_debug.show()
        self.midi_message_debug.raise_()

    def _midi_message_debug_closed(self):
        """Handle MIDI message debug window closure"""
        self.midi_message_debug = None

    def _handle_midi_message(self, message, timestamp):
        """Handle incoming MIDI message"""
        data = message[0]  # Get the raw MIDI data

        # Check if it's a SysEx message
        if data[0] == START_OF_SYSEX and len(data) > 8:
            # Verify it's a Roland message for JD-Xi
            if data[1] == DEVICE_ID and data[4:8] == bytes(  # Roland ID
                [MODEL_ID_1, MODEL_ID_2, MODEL_ID, JD_XI_ID]
            ):  # JD-Xi ID
                # Blink the input indicator
                if hasattr(self, "midi_in_indicator"):
                    self.midi_in_indicator.blink()

                # Forward to MIDI helper
                if hasattr(self, "midi_helper"):
                    self.midi_helper.handle_midi_message(message, timestamp)

    def _send_midi_message(self, message):
        """Send MIDI message and blink indicator"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
            # if self.midi_out:
            #    self.midi_out.send_message(message)
            # Blink the output indicator
            if hasattr(self, "midi_out_indicator"):
                self.midi_out_indicator.blink()

    """
    def _show_drums_editor(self):
        ""Show the drum editor window""
        try:
            if not hasattr(self, "drums_editor"):
                self.drums_editor = DrumEditor(
                    midi_helper=self.midi_helper, parent=self
                )  # Pass midi_helper instance
            self.drums_editor.show()
            self.drums_editor.raise_()
            
        except Exception as e:
            logging.error(f"Error showing Drums editor: {str(e)}") 
    """

    def update_preset_display(self, preset_num, preset_name):
        """Update the current preset display"""
        self.current_preset_num = preset_num
        self.current_preset_name = preset_name
        self._update_display()

    def _edit_patch_name(self):
        """Edit current patch name"""
        try:
            dialog = PatchNameEditor(self.current_preset_name, self)
            if dialog.exec_():
                new_name = dialog.get_name()

                # Update display
                self.update_preset_display(self.current_preset_num, new_name)

                # Send MIDI message to update patch name
                if self.midi_out:
                    msg = MIDIHelper.create_patch_name_message(
                        self.current_preset_num, new_name
                    )
                    self.midi_out.send_message(msg)
                    logging.debug(
                        f"Updated patch {self.current_preset_num} name to: {new_name}"
                    )

                    # Blink indicator
                    if hasattr(self, "midi_out_indicator"):
                        self.midi_out_indicator.blink()

        except Exception as e:
            logging.error(f"Error editing patch name: {str(e)}")

    def _save_settings(self):
        """Save application settings"""
        try:
            # Save MIDI port settings
            if hasattr(self, "settings"):
                self.settings.setValue("midi_in", self.midi_in_port_name)
                self.settings.setValue("midi_out", self.midi_out_port_name)

                # Save window geometry
                self.settings.setValue("geometry", self.saveGeometry())

                # Save current preset info
                self.settings.setValue("preset_num", self.current_preset_num)
                self.settings.setValue("preset_name", self.current_preset_name)

                logging.debug("Settings saved successfully")

        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")

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

    def _auto_connect_jdxi(self):
        """Attempt to automatically connect to JD-Xi MIDI ports"""
        try:
            # Get available ports
            input_ports = self.midi_helper.get_input_ports()
            output_ports = self.midi_helper.get_output_ports()

            # Look for JD-Xi in port names (case insensitive)
            jdxi_names = ["jd-xi", "jdxi", "roland jd-xi"]

            # Find input port
            for port in input_ports:
                if any(name in port.lower() for name in jdxi_names):
                    self.midi_helper.open_input_port(port)
                    logging.info(f"Auto-connected to JD-Xi input: {port}")
                    break

            # Find output port
            for port in output_ports:
                if any(name in port.lower() for name in jdxi_names):
                    self.midi_helper.open_output_port(port)
                    logging.info(f"Auto-connected to JD-Xi output: {port}")
                    break

            # Verify connection
            if self.midi_helper.current_in_port and self.midi_helper.current_out_port:
                # Send identity request to confirm it's a JD-Xi
                self._verify_jdxi_connection()
                return True

        except Exception as e:
            logging.error(f"Error auto-connecting to JD-Xi: {str(e)}")

        return False

    def _verify_jdxi_connection(self):
        """Verify connected device is a JD-Xi by sending identity request"""
        try:
            # Create identity request message using dataclass
            identity_request = IdentityRequest()

            # Send request
            if self.midi_helper:
                self.midi_helper.send_message(identity_request.to_list())
                logging.debug("Sent JD-Xi identity request")

        except Exception as e:
            logging.error(f"Error sending identity request: {str(e)}")

    def show_digital_synth_editor(self, synth_num=1):
        """Show digital synth editor window"""
        try:
            if not hasattr(self, f"digital_synth_{synth_num}_editor"):
                # Create new editor instance
                editor = DigitalSynthEditor(
                    synth_num=synth_num, midi_helper=self.midi_helper, parent=self
                )
                setattr(self, f"digital_synth_{synth_num}_editor", editor)

            # Get editor instance
            editor = getattr(self, f"digital_synth_{synth_num}_editor")

            # Show editor window
            editor.show()
            editor.raise_()
            editor.activateWindow()

            logging.debug(f"Showing Digital Synth {synth_num} editor")

        except Exception as e:
            logging.error(f"Error showing Digital Synth {synth_num} editor: {str(e)}")
            self.show_error("Editor Error", str(e))

    def handle_piano_note_on(self, note_num):
        """Handle piano key press"""
        if self.midi_helper:
            # Note on message: 0x90 (Note On, channel 1), note number, velocity 100
            msg = [0x90, note_num, 100]
            self.midi_helper.send_message(msg)
            logging.debug(f"Sent Note On: {note_num}")

    def handle_piano_note_off(self, note_num):
        """Handle piano key release"""
        if self.midi_helper:
            # Note off message: 0x80 (Note Off, channel 1), note number, velocity 0
            msg = [0x80, note_num, 0]
            self.midi_helper.send_message(msg)
            logging.debug(f"Sent Note Off: {note_num}")

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

    def _handle_octave_shift(self, direction: int):
        """Handle octave shift button press"""
        try:
            if self.midi_helper:
                # Get current octave from UI (-3 to +3)
                current = self.current_octave

                # Calculate new octave value
                new_octave = max(min(current + direction, 3), -3)

                # Convert to MIDI value (61-67 maps to -3 to +3)
                midi_value = new_octave + 64  # Center at 64

                # Send parameter change using new dataclass
                msg = ParameterMessage(
                    area=ANALOG_SYNTH_AREA,
                    part=0x00,
                    group=0x00,
                    param=0x34,  # Octave Shift parameter address
                    value=midi_value,
                ).to_list()

                self.midi_helper.send_message(msg)

                # Update UI state
                self.current_octave = new_octave
                self._update_octave_display()

                logging.debug(
                    f"Octave shifted to {new_octave} (MIDI value: {midi_value})"
                )

        except Exception as e:
            logging.error(f"Error shifting octave: {str(e)}")

    def _show_analog_presets(self):
        """Show the analog preset editor window"""
        self.preset_editor = PresetEditor(
            midi_helper=self.midi_helper, parent=self, preset_type=PresetType.ANALOG
        )
        self.preset_editor.preset_changed.connect(self._update_display_preset)
        # self.midi_helper.preset_changed.connect(self._update_display_preset)
        self.preset_editor.show()

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
            if hasattr(self, "channel_button"):
                self.channel_button.set_channel(channel)

            logging.debug(
                f"Updated display: {preset_number:03d}:{preset_name} (channel {channel})"
            )

        except Exception as e:
            logging.error(f"Error updating display: {str(e)}")

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

        except Exception as e:
            logging.error(f"Error updating display image: {str(e)}")

    def _load_last_preset(self):
        """Load the last used preset from settings"""
        try:
            # Get last preset info from settings
            synth_type = self.settings.value(
                "last_preset/synth_type", PresetType.DIGITAL_1
            )
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)
            channel = self.settings.value("last_preset/channel", 0, type=int)

            # Get preset list based on synth type
            if synth_type == PresetType.ANALOG:
                presets = AN_PRESETS
                bank_msb = 0
                bank_lsb = preset_num // 7
                program = preset_num % 7
            elif synth_type == PresetType.DIGITAL_1:
                presets = DIGITAL_PRESETS_ENUMERATED
                bank_msb = 1
                bank_lsb = preset_num // 16
                program = preset_num % 16
            elif synth_type == PresetType.DIGITAL_2:
                presets = DIGITAL_PRESETS_ENUMERATED
                bank_msb = 2
                bank_lsb = preset_num // 16
                program = preset_num % 16
            else:  # Drums
                presets = DRUM_PRESETS_ENUMERATED
                bank_msb = 3
                bank_lsb = preset_num // 16
                program = preset_num % 16

            # Send MIDI messages to load preset
            if hasattr(self, "midi_helper") and self.midi_helper:
                self.midi_helper.send_bank_select(bank_msb, bank_lsb, channel)
                self.midi_helper.send_program_change(program, channel)

                # Update display and channel
                preset_name = presets[preset_num - 1]  # Adjust index to be 0-based
                self._update_display_preset(preset_num, preset_name, channel)

                logging.debug(f"Loaded last preset: {preset_name} on channel {channel}")

        except Exception as e:
            logging.error(f"Error loading last preset: {str(e)}")

    def _save_last_preset(self, synth_type: str, preset_num: int, channel: int):
        """Save the last used preset to settings

        Args:
            synth_type: Type of synth ('Analog', 'Digital 1', 'Digital 2', 'Drums')
            preset_num: Preset number (0-based index)
            channel: MIDI channel
        """
        try:
            self.settings.setValue("last_preset/synth_type", synth_type)
            self.settings.setValue("last_preset/preset_num", preset_num)
            self.settings.setValue("last_preset/channel", channel)
            logging.debug(
                f"Saved last preset: {synth_type} #{preset_num} on channel {channel}"
            )

        except Exception as e:
            logging.error(f"Error saving last preset: {str(e)}")

    def _load_favorite(self, button: FavoriteButton):
        """Load preset from favorite button"""
        if button.preset:
            if self.midi_helper:
                # Get preset info from button
                self.preset_type = button.preset.synth_type
                self.current_preset_index = button.preset.preset_num
                self.channel = button.preset.channel
                # Update display - REMOVED the preset_num + 1
                self._update_display_preset(
                    self.current_preset_index + 1,  # Convert to 1-based index
                    button.preset.preset_name,
                    self.channel,
                )
                preset_data = {
                    "type": self.preset_type,  # Ensure this is a valid type
                    "selpreset": self.current_preset_index
                    + 1,  # Convert to 1-based index
                    "modified": 0,  # or 1, depending on your logic
                }
                # Send MIDI messages to load preset
                self.load_preset(preset_data)

    def _show_favorite_context_menu(self, pos, button: FavoriteButton):
        """Show context menu for favorite button"""
        menu = QMenu()

        # Add save action if we have a current preset
        if hasattr(self, "current_preset_num"):
            save_action = menu.addAction("Save Current Preset")
            save_action.triggered.connect(lambda: self._save_to_favorite(button))

        # Add clear action if slot has a preset
        if button.preset:
            clear_action = menu.addAction("Clear Slot")
            clear_action.triggered.connect(lambda: self._clear_favorite(button))

        menu.exec_(button.mapToGlobal(pos))

    def _save_to_favorite(self, button: FavoriteButton):
        """Save current preset to favorite slot"""
        if hasattr(self, "current_preset_num"):
            # Get current preset info from settings
            synth_type = self.settings.value(
                "last_preset/synth_type", PresetType.ANALOG
            )
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)
            channel = self.settings.value("last_preset/channel", 0, type=int)

            try:
                # Get the current preset name
                preset_name = self._get_current_preset_name()

                # Save to button (which will also save to settings)
                button.save_preset_as_favourite(
                    synth_type, preset_num, preset_name, channel
                )

                # Update display to show the saved preset
                self._update_display_preset(preset_num, preset_name, channel)

            except Exception as e:
                logging.error(f"Error saving to favorite: {str(e)}")
                QMessageBox.warning(self, "Error", f"Error saving preset: {str(e)}")

    def _clear_favorite(self, button: FavoriteButton):
        """Clear favorite slot"""
        button.clear_preset()

    def _load_saved_favorites(self):
        """Load saved favorites from settings"""
        for button in self.favorite_buttons:
            # Check if slot has saved preset
            synth_type = self.settings.value(
                f"favorites/slot{button.slot_num}/synth_type", ""
            )
            if synth_type:
                preset_num = self.settings.value(
                    f"favorites/slot{button.slot_num}/preset_num", 0, type=int
                )
                preset_name = self.settings.value(
                    f"favorites/slot{button.slot_num}/preset_name", ""
                )
                channel = self.settings.value(
                    f"favorites/slot{button.slot_num}/channel", 0, type=int
                )

                button.save_preset_as_favourite(
                    synth_type, preset_num, preset_name, channel
                )

    def load_preset(self, preset_data):
        """Load preset data into synth"""
        try:
            # self.preset_type = PresetType.DIGITAL_1
            if self.midi_helper:
                # Use PresetLoader for consistent preset loading
                self.preset_loader = PresetLoader(self.midi_helper)
                self.preset_loader.load_preset(
                    preset_data,
                )
                # Store as last loaded preset
                self.last_preset = preset_data
                # self.settings.setValue("last_preset", preset_data)

        except Exception as e:
            logging.error(f"Error loading preset: {str(e)}")

    def show_analog_editor(self):
        """Show analog synth editor"""
        try:
            if not hasattr(self, "analog_editor"):
                self.analog_editor = AnalogSynthEditor(midi_helper=self.midi_helper)
            self.analog_editor.show()
            self.analog_editor.raise_()

        except Exception as e:
            logging.error(f"Error showing Analog Synth editor: {str(e)}")

    def set_midi_ports(self, in_port: str, out_port: str) -> bool:
        """Set MIDI input and output ports

        Args:
            in_port: Input port name
            out_port: Output port name

        Returns:
            True if successful, False otherwise
        """
        try:
            # Open ports
            if not self.midi_helper.open_input_port(in_port):
                return False

            if not self.midi_helper.open_output_port(out_port):
                return False

            # Update indicators
            self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
            self.midi_out_indicator.set_state(self.midi_helper.is_output_open)

            return True

        except Exception as e:
            logging.error(f"Error setting MIDI ports: {str(e)}")
            return False

    def _connect_midi(self):
        """Connect to MIDI ports"""
        try:
            # Find JD-Xi ports
            in_port, out_port = self.midi_helper.find_jdxi_ports()

            if in_port and out_port:
                # Open ports
                if self.midi_helper.open_ports(in_port, out_port):
                    logging.info(f"Connected to JD-Xi ({in_port}, {out_port})")
                    self.statusBar().showMessage(f"Connected to JD-Xi")

                    # Remove or comment out any initialization messages
                    # self.midi_helper.send_identity_request()  # Remove this
                    return True

            logging.warning("JD-Xi not found")
            self.statusBar().showMessage("JD-Xi not found")
            return False

        except Exception as e:
            logging.error(f"Error connecting to MIDI: {str(e)}")
            self.statusBar().showMessage("MIDI connection error")
            return False

    def _open_vocal_fx(self):
        """Show the vocal FX editor window"""
        try:
            if not hasattr(self, "vocal_fx_editor"):
                self.vocal_fx_editor = VocalFXEditor(
                    midi_helper=self.midi_helper, parent=self
                )
            self.vocal_fx_editor.show()
            self.vocal_fx_editor.raise_()

        except Exception as e:
            logging.error(f"Error showing Vocal FX editor: {str(e)}")

    def _send_octave_bak(self, direction):
        """Send octave change MIDI message"""
        if self.midi_out:
            # Update octave tracking
            self.current_octave = max(-3, min(3, self.current_octave + direction))

            # Update button states
            self.octave_down.setChecked(self.current_octave < 0)
            self.octave_up.setChecked(self.current_octave > 0)

            # Update display
            self._update_display()

            # Map octave value to correct SysEx value
            # -3 = 0x3D, -2 = 0x3E, -1 = 0x3F, 0 = 0x40, +1 = 0x41, +2 = 0x42, +3 = 0x43
            octave_value = 0x40 + self.current_octave  # 0x40 is center octave

            # Calculate checksum
            checksum = 0x19 + 0x01 + 0x00 + 0x15 + octave_value
            checksum = (0x80 - (checksum & 0x7F)) & 0x7F

            # Create SysEx message
            sysex_msg = [
                0xF0,  # Start of SysEx
                0x41,  # Roland ID
                0x10,  # Device ID
                0x00,
                0x00,
                0x00,
                0x0E,  # Model ID
                0x12,  # Command ID (DT1)
                0x19,  # Address 1
                0x01,  # Address 2
                0x00,  # Address 3
                0x15,  # Address 4
                octave_value,  # Parameter value
                checksum,  # Checksum
                0xF7,  # End of SysEx
            ]

            self.midi_helper.send_message(sysex_msg)
            logging.debug(
                f"Sent octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})"
            )

    def _create_global_controls(self):
        """Create global controls section"""
        group = QGroupBox("Global Controls")
        layout = QHBoxLayout()
        group.setLayout(layout)

        # Octave controls
        octave_group = QGroupBox("Octave")
        octave_layout = QHBoxLayout()
        octave_group.setLayout(octave_layout)

        self.octave_down = QPushButton("Down")
        self.octave_up = QPushButton("Up")
        self.octave_display = QLabel("0")  # Display current octave
        self.octave_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.octave_down.clicked.connect(lambda: self._send_octave(-1))
        self.octave_up.clicked.connect(lambda: self._send_octave(1))
        octave_button_stylesheet = """
            QPushButton {
                background-color: black;
                border: 4px solid #d51e35;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
                border-color: #ff4d4d;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #333333;
                border-color: #ff6666;
            }
        """
        self.octave_up.setStyleSheet(octave_button_stylesheet)
        self.octave_down.setStyleSheet(octave_button_stylesheet)

        octave_layout.addWidget(self.octave_down)
        octave_layout.addWidget(self.octave_display)
        octave_layout.addWidget(self.octave_up)

        # Arpeggiator controls
        arp_group = QGroupBox("Arpeggiator")
        arp_layout = QHBoxLayout()
        arp_group.setLayout(arp_layout)

        self.arp_switch = QPushButton("On")
        self.arp_switch.setCheckable(True)
        self.arp_switch.clicked.connect(self._toggle_arpeggiator)

        arp_layout.addWidget(self.arp_switch)

        # Add groups to main layout
        layout.addWidget(octave_group)
        layout.addWidget(arp_group)

        return group

    def _change_octave(self, direction: int):
        """Change octave up/down

        Args:
            direction: +1 for up, -1 for down
        """
        if not self.midi_helper:
            return

        try:
            # Get current octave from display
            current = int(self.octave_display.text())

            # Calculate new octave (-3 to +3 range)
            new_octave = max(min(current + direction, 3), -3)

            # Convert to MIDI value (61-67 range)
            midi_value = new_octave + 64

            # Send parameter change
            self.midi_helper.send_parameter(
                area=0x00,  # Program zone area
                part=0x00,
                group=0x00,
                param=0x19,  # Zone Octave Shift parameter
                value=midi_value,
            )

            # Update display
            self.octave_display.setText(str(new_octave))

        except Exception as e:
            logging.error(f"Error changing octave: {str(e)}")

    def _toggle_arpeggiator(self, checked: bool):
        """Toggle arpeggiator on/off"""
        if not self.midi_helper:
            return

        try:
            # Send parameter change (0x00 = Program zone area, 0x03 = Arpeggio Switch)
            self.midi_helper.send_parameter(
                area=0x00,  # Program zone area
                part=0x00,  # Common part
                group=0x00,  # Common group
                param=0x03,  # Arpeggio Switch parameter
                value=1 if checked else 0,  # 0 = OFF, 1 = ON
            )

            # Update button text
            self.arp_switch.setText("Off" if not checked else "On")

        except Exception as e:
            logging.error(f"Error toggling arpeggiator: {str(e)}")

    def _show_arpeggio_editor(self):
        """Show the arpeggio editor window"""
        try:
            if not hasattr(self, "arpeggio_editor"):
                logging.debug("Creating new arpeggio editor")
                self.arpeggio_editor = ArpeggioEditor(midi_helper=self.midi_helper)
            logging.debug("Showing arpeggio editor")
            self.arpeggio_editor.show()
        except Exception as e:
            logging.error(f"Error showing Arpeggiator editor: {str(e)}")

    def get_data(self):
        """Retrieve data using SysEx request"""
        data = self.midi_helper.send_sysex_rq1(
            self.device_id, self.address + [0x00], self.data_length
        )

    def _handle_sysex_message(self, message, preset_data):
        """Handle SysEx MIDI messages."""
        try:
            sysex_bytes = list(message.data)
            parsed_data = parse_sysex(sysex_bytes)
            logging.debug(f"Parsed SysEx data: {parsed_data}")
        except ValueError as e:
            logging.error(
                f"Error handling SysEx message: {str(e)} for message: {message}"
            )

    def open_digital_synth_1_editor(self):
        """Open Digital Synth 1 editor window"""
        try:
            if not hasattr(self, 'digital_synth_1_editor'):
                self.digital_synth_1_editor = DigitalSynthEditor(
                    midi_helper=self.midi_helper,  # Pass the MIDI helper
                    synth_num=1,
                    parent=self,
                    preset_handler=self.digital_1_preset_handler
                )
            self.digital_synth_1_editor.show()
            logging.info("Selected synth: Digital 1")
        except Exception as e:
            logging.error(f"Error opening Digital Synth 1 editor: {str(e)}")


def parse_jdxi_tone(data):
    """
    Parses JD-Xi tone data from SysEx messages.
    Supports Digital1, Digital2, Analog, and Drums.

    Args:
        data (bytes): SysEx message containing tone data.

    Returns:
        dict: Parsed tone parameters.
    """
    if len(data) < 64:
        raise ValueError("Invalid data length. Must be at least 64 bytes.")

    parsed = {}
    try:
        parsed["header"] = data[:7].hex()
        parsed["address"] = data[7:11].hex()
        parsed["tone_name"] = data[11:24].decode(errors="ignore").strip()

        # Extracting shared parameters
        parsed["LFO Rate"] = data[24]
        parsed["LFO Depth"] = data[25]
        parsed["LFO Shape"] = data[26]

        parsed["OSC Type"] = data[33]
        parsed["OSC Pitch"] = data[34]
        parsed["Filter Cutoff"] = data[44]
        parsed["Filter Resonance"] = data[45]
        parsed["Amp Level"] = data[52]

        # Identify tone type
        tone_type = data[7]  # Address component identifies type
        if tone_type == 0x19:
            parsed["Tone Type"] = "Analog"
        elif tone_type == 0x1A:
            parsed["Tone Type"] = "Digital1"
        elif tone_type == 0x1B:
            parsed["Tone Type"] = "Digital2"
        elif tone_type == 0x1C:
            parsed["Tone Type"] = "Drums"
        else:
            parsed["Tone Type"] = "Unknown"

    except Exception as e:
        logging.error(f"Error parsing JD-Xi tone: {str(e)}")

    return parsed


def parse_sysex(sysex_bytes):
    if len(sysex_bytes) < 15:
        raise ValueError("Invalid SysEx message length")

    return {
        "start": sysex_bytes[0],
        "manufacturer_id": sysex_bytes[1],
        "device_id": sysex_bytes[2],
        "model_id": sysex_bytes[3:6],
        "jd_xi_id": sysex_bytes[6],
        "command_type": sysex_bytes[7],
        "area": sysex_bytes[8],
        "synth_number": sysex_bytes[9],
        "partial": sysex_bytes[10],
        "parameter": sysex_bytes[11],
        "value": sysex_bytes[12],
        "checksum": sysex_bytes[13],
        "end": sysex_bytes[14],
    }
