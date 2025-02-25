import logging
import re

from jdxi_manager.midi.preset.handler import PresetHandler
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
from PySide6.QtCore import Qt, QSettings, Signal
from PySide6.QtGui import (
    QAction,
    QFont,
    QFontDatabase,
)
from jdxi_manager.data.analog import AN_PRESETS
from jdxi_manager.data.presets.data import ANALOG_PRESETS_ENUMERATED, DIGITAL_PRESETS_ENUMERATED, DRUM_PRESETS_ENUMERATED
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.constants.arpeggio import ARP_PART, ARP_GROUP
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
from jdxi_manager.ui.windows.jdxi.jdxi import JdxiWindow
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


class MainWindow(JdxiWindow):
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

        self.channel = MIDI_CHANNEL_DIGITAL1
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
        self.current_preset_num = 1  # Initialize preset number
        self.current_preset_name = "JD Xi"  # Initialize preset name
        self.midi_in = None
        self.midi_out = None
        self.midi_in_port_name = ""  # Store input port name
        self.midi_out_port_name = ""  # Store output port name

        # Initialize MIDI helper
        if self.midi_in:
            self.midi_in.delete()  # Use delete() instead of close()
        if self.midi_out:
            self.midi_out.delete()  # Use delete() instead of close()
        if self.midi_helper:
            self.midi_helper.close_ports()
        self.midi_helper = MIDIHelper(parent=self)
        self.preset_loader = PresetLoader(self.midi_helper)

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
        self.midi_in_indicator.set_state(bool(self.midi_in))
        self.midi_out_indicator.set_state(bool(self.midi_out))

        pub.subscribe(self._update_display_preset, "update_display_preset")

        # Set black background for entire application
        self.setStyleSheet(Style.JDXI_STYLE)

        # Load custom font
        self._load_digital_font()

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

        # Load last used preset settings
        self._load_last_preset()

        # Initialize synth type
        self.current_synth_type = PresetType.DIGITAL_1

        # Load saved favorites
        self._load_saved_favorites()

        # Create editors menu
        # editors_menu = self.menuBar().addMenu("Editors")

        # Add menu items for each editor
        # digital1_action = editors_menu.addAction("Digital Synth 1")
        # digital1_action.triggered.connect(lambda: self.show_editor("digital1"))

        # digital2_action = editors_menu.addAction("Digital Synth 2")
        # digital2_action.triggered.connect(lambda: self.show_editor("digital2"))

        # analog_action = editors_menu.addAction("Analog Synth")
        # analog_action.triggered.connect(lambda: self.show_editor("analog"))

        # drums_action = editors_menu.addAction("Drums")
        # drums_action.triggered.connect(lambda: self.show_editor("drums"))

        # arp_action = editors_menu.addAction("Arpeggio")
        # arp_action.triggered.connect(lambda: self.show_editor("arpeggio"))

        # effects_action = editors_menu.addAction("Effects")
        # effects_action.triggered.connect(lambda: self.show_editor("effects"))

        # Add Vocal FX menu item
        # vocal_fx_action = editors_menu.addAction("Vocal FX")
        # vocal_fx_action.triggered.connect(lambda: self.show_editor("vocal_fx"))

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

        # Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)

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
        self.channel = MIDI_CHANNEL_ANALOG
        self.preset_type = PresetType.ANALOG

    def _show_drums_editor(self, editor_type: str):
        self._show_editor("Drums", DrumEditor)
        self.channel = MIDI_CHANNEL_DRUMS
        self.preset_type = PresetType.DRUMS

    def _show_arpeggio_editor(self, editor_type: str):
        self._show_editor("Arpeggio", ArpeggioEditor)

    def _open_effects(self, editor_type: str):
        self._show_editor("Effects", EffectsEditor)

    def _open_pattern(self, editor_type: str):
        self._show_editor("Pattern", PatternSequencer)

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
            logging.info(f"Showing {title} editor")
            # Store reference and show
            if title == "Digital Synth 1":
                self.digital_synth1 = editor
                self.channel = MIDI_CHANNEL_DIGITAL1
            elif title == "Digital Synth 2":
                self.digital_synth2 = editor
                self.channel = MIDI_CHANNEL_DIGITAL2
            elif title == "Analog Synth":
                self.analog_synth = editor
                self.channel = MIDI_CHANNEL_ANALOG
            elif title == "Drums":
                self.drum_kit = editor
                self.channel = MIDI_CHANNEL_DRUMS
            elif title == "Effects":
                self.effects = editor
            elif title == "Pattern":
                self.effects = editor
            logging.info(f"midi channel: {self.channel}")
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
        self.channel = MIDI_CHANNEL_ANALOG

    def _open_digital_synth1(self):
        """Open the Digital Synth 1 editor and send SysEx message."""
        self.current_synth_type = PresetType.DIGITAL_1
        self.channel = MIDI_CHANNEL_DIGITAL1
        try:
            if not hasattr(self, "digital_synth1_editor"):
                self.digital_synth1_editor = DigitalSynthEditor(
                    midi_helper=self.midi_helper, parent=self
                )
            self.digital_synth1_editor.show()
            self.digital_synth1_editor.raise_()
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
        self.channel = MIDI_CHANNEL_DIGITAL2
        self.preset_type = PresetType.DIGITAL_2
        self.current_synth_type = PresetType.DIGITAL_2

    def _open_drums(self):
        self.channel = MIDI_CHANNEL_DRUMS
        self._show_editor("Drums", DrumEditor)
        self.preset_type = PresetType.DRUMS
        self.current_synth_type = PresetType.DRUMS

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

    def _midi_message_debug_closed(self):
        """Handle MIDI message debug window closure"""
        self.midi_message_debug = None

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
                    self.midi_helper.handle_incoming_midi_message(message, timestamp)

    def _send_midi_message(self, message):
        """Send MIDI message and blink indicator"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
            # Blink the output indicator
            if hasattr(self, "midi_out_indicator"):
                self.midi_out_indicator.blink()

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
                if synth_num == 1:
                    self.channel = 1
                elif synth_num == 2:
                    self.channel = 2
                else:
                    self.channel = 1
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
            # self.channel is 0-indexed, so add 1 to match MIDI channel in log file
            msg = [0x90 + (self.channel), note_num, 100]
            self.midi_helper.send_message(msg)
            logging.info(f"Sent Note On: {note_num} on channel {self.channel + 1}")

    def handle_piano_note_off(self, note_num):
        """Handle piano key release"""
        if self.midi_helper:
            # Calculate the correct status byte for note_off:
            # 0x80 is the base for note_off messages. Subtract 1 if self.channel is 1-indexed.
            status = 0x80 + (self.channel)
            msg = [status, note_num, 0]
            self.midi_helper.send_message(msg)
            logging.info(f"Sent Note Off: {note_num} on channel {self.channel + 1}")

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
