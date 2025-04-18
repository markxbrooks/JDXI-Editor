"""

# Create editor instances
analog_editor = AnalogSynthEditor(midi_helper, preset_helper)
digital_editor = DigitalSynthEditor(midi_helper, preset_helper)
drum_editor = DrumSynthEditor(midi_helper, preset_helper)

# Save all controls to a single JSON file
save_all_controls_to_single_file(
    editors=[self.analog_editor, self.digital_synth2_editor self.digital_synth1_editor, analog_editor],
    file_path="all_controls.json"
)
JD-Xi Instrument class for managing presets and MIDI settings.

This module defines the `JdxiInstrument` class, which extends from the `JdxiUi` class to manage JD-Xi instrument presets, MIDI communication, and UI interactions. It allows for controlling and modifying different preset types (Digital 1, Digital 2, Analog, Drums) and provides MIDI connectivity for program changes and preset management.

Key Features:
- Handles MIDI connectivity and communication, including program change signals.
- Manages different preset types (Digital, Analog, Drums) with the ability to select and load presets.
- Provides MIDI indicators to display the status of MIDI input/output ports.
- Includes functionality for dragging the window and selecting different synth types.
- Integrates with external MIDI devices for seamless performance control.
- Includes a custom UI to manage and visualize the instrument's preset settings.
- Supports the auto-connection of JD-Xi and provides MIDI configuration if auto-connection fails.

Methods:
    - __init__: Initializes the instrument's MIDI settings, UI components, and preset handlers.
    - mousePressEvent, mouseMoveEvent, mouseReleaseEvent: Handles window drag events for custom window movement.
    - _select_synth: Selects the current synth type and updates UI button styles.
    - _update_synth_button_styles: Updates button styles based on the selected synth type.
    - _get_presets_for_current_synth: Returns the list of presets based on the selected synth type.
    - _get_for_current_synth: Returns the appropriate preset handler based on the selected synth type.
    - _previous_tone: Navigates to the previous tone in the preset list and updates the display.
    - ...

"""
import logging
import platform
from typing import Union

from PySide6.QtGui import QShortcut, QKeySequence

from PySide6.QtWidgets import QMenu, QMessageBox, QLabel
from PySide6.QtCore import Qt, QSettings, QTimer

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB, AddressOffsetProgramLMB, \
    AddressOffsetTemporaryToneUMB, AddressOffsetSystemUMB
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParameter
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter
from jdxi_editor.midi.preset.type import JDXISynth
from jdxi_editor.midi.data.presets.jdxi import JDXIPresets
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.io.connection import MIDIConnection
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.preset.data import Preset
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.midi.program.helper import ProgramHelper
from jdxi_editor.midi.sysex.requests import MidiRequests
from jdxi_editor.ui.editors import (
    AnalogSynthEditor,
    DigitalSynthEditor,
    DrumCommonEditor,
    ArpeggioEditor,
    EffectsCommonEditor,
    VocalFXEditor,
    ProgramEditor, SynthEditor,
)
from jdxi_editor.ui.editors.helpers.program import (
    get_program_id_by_name,
    get_program_name_by_id,
)
from jdxi_editor.ui.editors.io.player import MidiPlayer
from jdxi_editor.ui.editors.pattern.pattern import PatternSequencer
from jdxi_editor.ui.editors.io.preset import PresetEditor
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.ui.style.helpers import generate_sequencer_button_style
from jdxi_editor.ui.widgets.button import SequencerSquare
from jdxi_editor.ui.windows.jdxi.helpers.port import _find_jdxi_port
from jdxi_editor.ui.windows.midi.config_dialog import MIDIConfigDialog
from jdxi_editor.ui.windows.midi.debugger import MIDIDebugger
from jdxi_editor.ui.windows.midi.message_debug import MIDIMessageDebug
from jdxi_editor.ui.windows.patch.manager import PatchManager
from jdxi_editor.ui.windows.jdxi.ui import JdxiUi
from jdxi_editor.ui.widgets.viewer.log import LogViewer
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton

CENTER_OCTAVE_VALUE = 0x40  # for octave up/down buttons


class JdxiInstrument(JdxiUi):
    def __init__(self):
        super().__init__()
        self.digital_1_preset_helper = None
        self.current_program_id = "A01"
        self.current_program_number = int(self.current_program_id[1:])
        self.current_program_name = get_program_name_by_id(self.current_program_id)
        self.slot_num = None
        self.channel = MidiChannel.DIGITAL1
        self.analog_editor = None
        self.last_preset = None
        self.log_file = None
        self.preset_type = JDXISynth.DIGITAL_1  # Default preset
        # Initialize state variables
        self.current_synth_type = JDXISynth.DIGITAL_1
        self.current_preset_num = 1  # Initialize preset number
        self.current_preset_name = "JD Xi"  # Initialize preset name
        self.midi_in = None
        self.midi_out = None
        self.midi_in_port_name = ""  # Store input port name
        self.midi_out_port_name = ""  # Store output port name
        self.key_hold_latched = False
        # Initialize MIDI helper
        if self.midi_in:
            self.midi_in.delete()  # Use delete() instead of close()
        if self.midi_out:
            self.midi_out.delete()  # Use delete() instead of close()
        if self.midi_helper:
            self.midi_helper.close_ports()
        self.midi_helper = MidiIOHelper()
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        # Initialize windows to None
        self.log_viewer = None
        self.midi_debugger = None
        self.midi_message_debug = None

        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL

        # Try to auto-connect to JD-Xi
        self._auto_connect_jdxi()
        self.midi_helper.send_identity_request()
        self.program_helper = ProgramHelper(self.midi_helper, MidiChannel.PROGRAM)
        # Load custom font
        self._load_digital_font()

        # Load settings
        self.settings = QSettings("jdxi_manager2", "settings")
        self._load_settings()

        # Show window
        self.show()

        # Add preset tracking
        self.current_preset_num = 1
        self.current_preset_name = "INIT PATCH"

        # Create display label
        self.display_label = QLabel()
        # self.display_label.setMinimumSize(220, 100)  # Adjust size as needed
        self._toggle_illuminate_sequencer_lightshow(True)
        if platform.system() == "Windows":
            self.setStyleSheet(JDXIStyle.TRANSPARENT + JDXIStyle.ADSR_DISABLED)
        # Show MIDI config if auto-connect failed
        if (
            not self.midi_helper.current_in_port
            or not self.midi_helper.current_out_port
        ):
            self._show_midi_config()
        # Initialize MIDI indicators
        self.midi_in_indicator.set_state(bool(self.midi_in))
        self.midi_out_indicator.set_state(bool(self.midi_out))
        self.key_hold_button.clicked.connect(self._send_arp_key_hold)
        self.arpeggiator_button.clicked.connect(self._send_arp_on_off)

        # Add display to layout
        if hasattr(self, "main_layout"):
            self.main_layout.addWidget(self.display_label)

        # Load last used preset settings
        # FIXME: self._load_last_preset()

        # Initialize synth preset_type
        self.current_synth_type = JDXISynth.DIGITAL_1

        # Load saved favorites
        self._load_saved_favorites()

        # Set default styles
        self._update_synth_button_styles()

        # Initialize current preset index
        self.current_preset_index = 0

        # Initialize current preset index
        self.current_preset_index = 0

        # Initialize PresetHandler with the desired preset list
        self.digital_1_preset_helper = PresetHelper(
            self.midi_helper,
            JDXIPresets.DIGITAL_ENUMERATED,
            channel=MidiChannel.DIGITAL1,
            preset_type=JDXISynth.DIGITAL_1,
        )
        self.digital_2_preset_helper = PresetHelper(
            self.midi_helper,
            JDXIPresets.DIGITAL_ENUMERATED,
            channel=MidiChannel.DIGITAL2,
            preset_type=JDXISynth.DIGITAL_2,
        )
        self.analog_preset_helper = PresetHelper(
            self.midi_helper,
            JDXIPresets.ANALOG_ENUMERATED,
            channel=MidiChannel.ANALOG,
            preset_type=JDXISynth.ANALOG,
        )
        self.drums_preset_helper = PresetHelper(
            self.midi_helper,
            JDXIPresets.DRUM_ENUMERATED,
            channel=MidiChannel.DRUM,
            preset_type=JDXISynth.DRUMS,
        )

        self.digital_1_preset_helper.update_display.connect(
            self.update_display_callback
        )
        self.digital_2_preset_helper.update_display.connect(
            self.update_display_callback
        )
        self.analog_preset_helper.update_display.connect(self.update_display_callback)
        self.drums_preset_helper.update_display.connect(self.update_display_callback)
        self.old_pos = None

        # Set initial indicator states
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
        self.digital_display.mousePressEvent = self._open_program_editor
        # Connect buttons to functions
        self.program_down_button.clicked.connect(self._previous_program)
        self.program_up_button.clicked.connect(self._next_program)
        self.midi_helper.update_program_name.connect(self.set_current_program_name)
        self.midi_helper.update_digital1_tone_name.connect(
            self.set_current_digital1_tone_name
        )
        self.midi_helper.update_digital2_tone_name.connect(
            self.set_current_digital2_tone_name
        )
        self.midi_helper.update_analog_tone_name.connect(
            self.set_current_analog_tone_name
        )
        self.midi_helper.update_drums_tone_name.connect(
            self.set_current_drums_tone_name
        )
        self.midi_helper.midi_program_changed.connect(self.set_current_program_number)
        # sur ctrl-R for data request
        # Add keyboard shortcuts
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        # Initialize preset handlers dynamically
        preset_configs = [
            (JDXISynth.DIGITAL_1, JDXIPresets.DIGITAL_ENUMERATED, MidiChannel.DIGITAL1),
            (JDXISynth.DIGITAL_2, JDXIPresets.DIGITAL_ENUMERATED, MidiChannel.DIGITAL2),
            (JDXISynth.ANALOG, JDXIPresets.ANALOG_ENUMERATED, MidiChannel.ANALOG),
            (JDXISynth.DRUMS, JDXIPresets.DRUM_ENUMERATED, MidiChannel.DRUM),
        ]

        self.preset_helpers = {
            synth_type: PresetHelper(
                self.midi_helper, presets, channel=channel, preset_type=synth_type
            )
            for synth_type, presets, channel in preset_configs
        }
        
        self.editors = []

    def add_editor(self, editor: SynthEditor):
        self.editors.append(editor)

    def _handle_program_change(self):
        """perform data request"""
        self.data_request()

    def _get_preset_helper_for_current_synth(self):
        """Return the appropriate preset handler based on the current synth preset_type."""
        handler = self.preset_helpers.get(self.current_synth_type)
        if handler is None:
            logging.warning(
                f"Unknown synth preset_type: {self.current_synth_type}, defaulting to digital_1"
            )
            return self.preset_helpers[JDXISynth.DIGITAL_1]  # Safe fallback
        return handler

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def set_current_program_name(self, program_name: str):
        """program name"""
        self.current_program_name = program_name
        self.current_program_id = get_program_id_by_name(program_name)
        if not self.current_program_id:
            self.current_program_number = 0
        else:
            self.current_program_number = int(self.current_program_id[1:])
        self._update_display()

    def set_current_program_number(self, channel: int, program_number: int):
        """program name"""
        self.current_program_number = program_number + 1
        self.data_request()
        self._update_display()

    def set_current_digital1_tone_name(self, tone_name: str):
        """program name"""
        self.current_digital1_tone_name = tone_name
        self._update_display()

    def data_request(self):
        """Send data request SysEx messages to the JD-Xi"""
        # Define SysEx messages as byte arrays
        for request in self.midi_requests:
            request = bytes.fromhex(request)
            # Send each SysEx message
            self.midi_helper.send_raw_message(request)

    def set_current_digital2_tone_name(self, tone_name: str):
        """program name"""
        self.current_digital2_tone_name = tone_name
        self._update_display()

    def set_current_analog_tone_name(self, tone_name: str):
        """program name"""
        self.current_analog_tone_name = tone_name
        self._update_display()

    def set_current_drums_tone_name(self, tone_name: str):
        """program name"""
        self.current_drums_tone_name = tone_name
        self._update_display()

    def _select_synth(self, synth_type):
        """Select address synth and update button styles."""
        logging.info(f"Selected synth: {synth_type}")
        self.current_synth_type = synth_type
        self._update_synth_button_styles()
        self.preset_helper = self._get_preset_helper_for_current_synth()
        self.preset_helper.preset_changed.connect(self.midi_helper.send_program_change)

    def _update_synth_button_styles(self):
        """Update styles for synth buttons based on selection."""
        buttons = {
            JDXISynth.ANALOG: self.analog_button,
            JDXISynth.DIGITAL_1: self.digital1_button,
            JDXISynth.DIGITAL_2: self.digital2_button,
            JDXISynth.DRUMS: self.drums_button,
        }

        for synth_type, button in buttons.items():
            if synth_type == self.current_synth_type:
                button.setStyleSheet(JDXIStyle.BUTTON_ROUND)
            else:
                button.setStyleSheet(JDXIStyle.BUTTON_ROUND_SELECTED)
                button.setChecked(False)

    def _get_presets_for_current_synth(self):
        """Return the appropriate preset list based on the current synth preset_type."""
        preset_map = {
            JDXISynth.ANALOG: JDXIPresets.ANALOG,
            JDXISynth.DIGITAL_1: JDXIPresets.DIGITAL_ENUMERATED,
            JDXISynth.DIGITAL_2: JDXIPresets.DIGITAL_ENUMERATED,
            JDXISynth.DRUMS: JDXIPresets.DRUM_ENUMERATED,
        }

        presets = preset_map.get(self.current_synth_type, None)
        if presets is None:
            logging.warning(
                f"Unknown synth preset_type: {self.current_synth_type}, defaulting to DIGITAL_PRESETS"
            )
            return JDXIPresets.DIGITAL_ENUMERATED  # Safe fallback
        return presets

    def _previous_program(self):
        """Decrement the program index and update the display."""
        """Decrement the tone index and update the display."""
        if self.current_program_number == 1:
            logging.info("Already at the first program.")
            msg_box = QMessageBox()
            msg_box.setIcon(
                QMessageBox.Critical
            )  # Use QMessageBox.Warning, Information, or Question as needed
            msg_box.setWindowTitle("First program")
            msg_box.setText("Already at the first program")
            msg_box.exec()
            return
        self.current_program_number -= 1
        self.program_helper.previous_program()
        self._update_display()

    def _next_program(self):
        """Increment the program index and update the display."""
        self.current_program_number += 1
        self.program_helper.next_program()
        self._update_display()

    def _previous_tone(self):
        """Decrement the tone index and update the display."""
        if self.current_preset_index <= 0:
            logging.info("Already at the first preset.")
            msg_box = QMessageBox()
            msg_box.setIcon(
                QMessageBox.Critical
            )  # Use QMessageBox.Warning, Information, or Question as needed
            msg_box.setWindowTitle("First preset")
            msg_box.setText("Already at the first preset")
            msg_box.exec()
            return

        self.current_preset_index -= 1
        presets = self._get_presets_for_current_synth()
        preset_helper = self._get_preset_helper_for_current_synth()

        self._update_display_preset(
            self.current_preset_index,
            presets[self.current_preset_index],
            self.channel,
        )
        preset_helper.load_preset_by_program_change(
            self.current_preset_index, self.current_synth_type
        )

    def _next_tone(self):
        """Increment the tone index and update the display."""
        max_index = len(self._get_presets_for_current_synth()) - 1
        if self.current_preset_index >= max_index:
            logging.info("Already at the last preset.")
            msg_box = QMessageBox()
            msg_box.setIcon(
                QMessageBox.Critical
            )  # Use QMessageBox.Warning, Information, or Question as needed
            msg_box.setWindowTitle("Last preset")
            msg_box.setText("already at the last preset")
            msg_box.exec()
            return

        self.current_preset_index += 1
        presets = self._get_presets_for_current_synth()
        preset_helper = self._get_preset_helper_for_current_synth()
        self._update_display_preset(
            self.current_preset_index,
            presets[self.current_preset_index],
            self.channel,
        )
        preset_helper.load_preset_by_program_change(
            self.current_preset_index, self.current_synth_type
        )

    def update_display_callback(self, synth_type, preset_index, channel):
        """Update the display for the given synth preset_type and preset index."""
        logging.info(
            f"update_display_callback: synth_type: {synth_type} preset_index: {preset_index}, channel: {channel}",
        )

        preset_channel_map = {
            MidiChannel.ANALOG: JDXIPresets.ANALOG_ENUMERATED,
            MidiChannel.DIGITAL1: JDXIPresets.DIGITAL_ENUMERATED,
            MidiChannel.DIGITAL2: JDXIPresets.DIGITAL_ENUMERATED,
            MidiChannel.DRUM: JDXIPresets.DRUM_ENUMERATED,
        }

        # Default to DIGITAL_PRESETS_ENUMERATED if the synth_type is not found in the map
        presets = preset_channel_map.get(channel, JDXIPresets.DIGITAL_ENUMERATED)

        self._update_display_preset(
            preset_index,
            presets[preset_index],
            channel,
        )

    def _toggle_illuminate_sequencer_lightshow(self, enabled: bool) -> None:
        """Toggle the sequencer lightshow on or off."""
        if not enabled:
            if hasattr(self, "lightshow_timer") and self.lightshow_timer.isActive():
                self.lightshow_timer.stop()
            # Turn off any active lights
            for btn in self.sequencer_buttons:
                btn.setStyleSheet(generate_sequencer_button_style(False))
                btn.setChecked(True)
            return

        self._lightshow_index = 0

        def step():
            # Turn off previous
            for i, btn in enumerate(self.sequencer_buttons):
                btn.setChecked(False)
                btn.setStyleSheet(
                    generate_sequencer_button_style(i == self._lightshow_index)
                )

            self._lightshow_index += 1
            if self._lightshow_index >= len(self.sequencer_buttons):
                self._lightshow_index = 0  # Loop back to start

        # Create and start the timer
        if not hasattr(self, "lightshow_timer"):
            self.lightshow_timer = QTimer(self)
            self.lightshow_timer.timeout.connect(step)

        self.lightshow_timer.start(500)  # Every 500 ms

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
            "preset": self._open_preset,
            "program": self._open_program,
            "midi_file": self._open_midi_file,
        }
        self._select_synth(self.preset_type)
        if editor_type in editor_map:
            editor_map[editor_type](editor_type)
        else:
            logging.info(f"Unknown editor preset_type: {editor_type}")

    def _show_vocal_fx(self, editor_type: str):
        if not hasattr(self, "vocal_fx_editor"):
            self.vocal_fx_editor = VocalFXEditor(self.midi_helper, self)
            self.vocal_fx_editor.show()
            self.vocal_fx_editor.raise_()

    def _show_digital_synth_editor(self, editor_type: str):
        synth_number = 1 if editor_type == "digital1" else 2
        self._show_editor(
            f"Digital Synth {synth_number}", DigitalSynthEditor, synth_num=synth_number
        )
        self.preset_type = (
            JDXISynth.DIGITAL_1 if synth_number == 1 else JDXISynth.DIGITAL_2
        )

    def _show_analog_synth_editor(self, editor_type: str):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        self.channel = MidiChannel.ANALOG
        self.preset_type = JDXISynth.ANALOG

    def _show_drums_editor(self, editor_type: str):
        self._show_editor("Drums", DrumCommonEditor)
        self.channel = MidiChannel.DRUM
        self.preset_type = JDXISynth.DRUMS

    def _open_vocal_effects(self, title, editor_type: str):
        self._show_editor("Vocal Effects", VocalFXEditor)

    def _open_pattern(self, editor_type: str):
        self._show_editor("Pattern", PatternSequencer)

    def _open_preset(self, editor_type: str):
        try:
            self._show_editor("Preset", PresetEditor)
        except Exception as ex:
            logging.error(f"Error showing Preset editor: {str(ex)}")

    def _open_program(self, editor_type: str):
        try:
            self._show_editor("Program", ProgramEditor)
        except Exception as ex:
            logging.error(f"Error showing Program editor: {str(ex)}")

    def _open_midi_file(self, editor_type: str):
        self._show_editor("MIDI File", MidiPlayer)

    def _save_favorite(self, button, index):
        """Save the current preset as an address favorite and prevent toggling off."""
        self.settings = QSettings("mabsoft", "jdxi_editor")
        preset_name = f"favorite_{index + 1:02d}"

        if button.isChecked():
            current_preset = self._get_current_tone()
            if current_preset:
                button.preset = current_preset  # Store preset in button
                button.setToolTip(
                    f"Tone {current_preset.number} {current_preset.name}, {current_preset.type}"
                )
                button.setChecked(True)  # Keep it checked
                button.setCheckable(False)  # Prevent unchecking directly
                self.settings.setValue(preset_name, current_preset)  # Save preset
                logging.info(f"Saved {current_preset} as {preset_name}")
        else:
            self.load_button_preset(button)  # Load stored preset if checked

    def load_button_preset(self, button):
        """load preset dat stored on the button"""
        preset = button.preset
        preset_data = Preset(
            type=preset.type,  # Ensure this is address valid preset_type
            number=preset.number,  # Convert to 1-based index
        )
        self.current_synth_type = preset.type
        preset_helper = self._get_preset_helper_for_current_synth()
        preset_helper.load_preset(preset_data)

    def _get_current_tone(self):
        """Retrieve the current preset"""
        try:
            # Update the current preset index or details here
            tone_number = self.current_tone_number
            tone_name = self.current_tone_name
            synth_type = self.current_synth_type
            current_tone = Preset(number=tone_number, name=tone_name, type=synth_type)
            logging.debug(f"Current preset retrieved: {current_tone}")
            return current_tone

        except Exception as ex:
            logging.error(f"Error retrieving current preset: {str(ex)}")
            return None

    def _get_current_preset_name(self):
        """Get the name of the currently selected preset"""
        try:
            preset_type = self.current_synth_type
            preset_number = self.current_preset_index
            preset_map = {
                JDXISynth.ANALOG: JDXIPresets.ANALOG_ENUMERATED,
                JDXISynth.DIGITAL_1: JDXIPresets.DIGITAL_ENUMERATED,
                JDXISynth.DIGITAL_2: JDXIPresets.DIGITAL_ENUMERATED,
                JDXISynth.DRUMS: JDXIPresets.DRUM_ENUMERATED,
            }
            # Default to DIGITAL_PRESETS_ENUMERATED if the synth_type is not found in the map
            presets = preset_map.get(preset_type, JDXIPresets.DIGITAL_ENUMERATED)
            preset_name = presets[preset_number]
            logging.info(f"preset_name: {preset_name}")
            return preset_name
        except IndexError:
            return "Index Error for current preset"

    def _get_current_preset_name_from_settings(self):
        """Get the name of the currently selected preset"""
        try:
            synth_type = self.settings.value("last_preset/synth_type", JDXISynth.ANALOG)
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)

            # Get preset name - adjust index to be 0-based
            if synth_type == JDXISynth.ANALOG:
                return JDXIPresets.ANALOG[preset_num - 1]  # Convert 1-based to 0-based
            if synth_type == JDXISynth.DIGITAL_1:
                return JDXIPresets.DIGITAL_ENUMERATED[preset_num - 1]
            if synth_type == JDXISynth.DIGITAL_2:
                return JDXIPresets.DIGITAL_ENUMERATED[preset_num - 1]
            else:
                return JDXIPresets.DRUM_ENUMERATED[preset_num - 1]
        except IndexError:
            return "INIT PATCH"

    def _get_current_preset_type(self):
        """Get the preset_type of the currently selected preset"""
        return self.preset_type
        # return self.settings.value("last_preset/synth_type", PresetType.ANALOG)

    def _show_midi_config(self):
        """Show MIDI configuration dialog"""
        try:
            dialog = MIDIConfigDialog(
                self.midi_helper,
                parent=self)
            dialog.exec()

        except Exception as e:
            logging.error(f"Error showing MIDI configuration: {str(e)}")
            self.show_error("MIDI Configuration Error", str(e))

    def _update_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out

        # Save settings
        #if midi_in and midi_out:
        #    self.settings.setValue("midi/input_port", midi_in.port_name)
        #    self.settings.setValue("midi/output_port", midi_out.port_name)

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

        except Exception as ex:
            logging.error(f"Error loading settings: {str(ex)}")

    def _show_editor(self, title, editor_class, **kwargs):
        """Show editor window"""
        try:
            # Create editor with proper initialization
            if editor_class in [
                DigitalSynthEditor,
                DrumCommonEditor,
                AnalogSynthEditor,
                PatternSequencer,
                ProgramEditor,
                PresetEditor,
                MidiPlayer,
            ]:
                preset_helper = self._get_preset_helper_for_current_synth()
                editor = editor_class(
                    midi_helper=self.midi_helper,
                    parent=self,
                    preset_helper=preset_helper,
                    **kwargs,
                )
            else:
                # For other editors, use existing initialization
                editor = editor_class(midi_out=self.midi_out, **kwargs)

            # Set window title
            editor.setWindowTitle(title)
            logging.info(f"Showing {title} editor")
            self.add_editor(editor)
            # Store reference and show
            if title == "Digital Synth 1":
                self.digital_synth1_editor = editor
                self.channel = MidiChannel.DIGITAL1
            elif title == "Digital Synth 2":
                self.digital_synth2_editor = editor
                self.channel = MidiChannel.DIGITAL2
            elif title == "Analog Synth":
                self.analog_synth_editor = editor
                self.channel = MidiChannel.ANALOG
            elif title == "Drums":
                self.drum_kit_editor = editor
                self.channel = MidiChannel.DRUM
            elif title == "Effects":
                self.effects_editor = editor
            elif title == "Pattern":
                self.pattern_editor = editor
            elif title == "Preset":
                self.preset_editor = editor
            elif title == "Program":
                self.program_editor = editor
            elif title == "MIDI File":
                self.midi_file_editor = editor
            logging.info(f"midi channel: {self.channel}")
            # Show editor
            editor.show()
            editor.raise_()
            editor.preset_helper.update_display.connect(self.update_display_callback)

        except Exception as ex:
            logging.error(f"Error showing {title} editor: {str(ex)}")

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages and flash indicator"""
        self.midi_in_indicator.flash()

    def _open_analog_synth(self):
        self._show_editor("Analog Synth", AnalogSynthEditor)
        self.preset_type = JDXISynth.ANALOG
        self.current_synth_type = JDXISynth.ANALOG
        self.channel = MidiChannel.ANALOG

    def _open_digital_synth1(self):
        """Open the Digital Synth 1 editor and send SysEx message."""
        self.current_synth_type = JDXISynth.DIGITAL_1
        self.channel = MidiChannel.DIGITAL1
        try:
            if not hasattr(self, "digital_synth1_editor"):
                self.digital_synth1_editor = DigitalSynthEditor(
                    midi_helper=self.midi_helper, parent=self
                )
                self.add_editor(self.digital_synth1_editor)
            self.digital_synth1_editor.show()
            self.digital_synth1_editor.raise_()
        except Exception as ex:
            logging.error(f"Error opening Digital Synth 1 editor: {str(ex)}")

    def _open_digital_synth2(self):
        self._show_editor("Digital Synth 2", DigitalSynthEditor, synth_number=2)
        self.channel = MidiChannel.DIGITAL2
        self.preset_type = JDXISynth.DIGITAL_2
        self.current_synth_type = JDXISynth.DIGITAL_2

    def _open_drums(self):
        self.channel = MidiChannel.DRUM
        self._show_editor("Drums", DrumCommonEditor)
        self.preset_type = JDXISynth.DRUMS
        self.current_synth_type = JDXISynth.DRUMS

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

        except Exception as ex:
            logging.error(f"Error showing Arpeggiator editor: {str(ex)}")

    def _open_effects(self):
        """Show the effects editor window"""
        try:
            if not hasattr(self, "effects_editor"):
                self.effects_editor = EffectsCommonEditor(
                    midi_helper=self.midi_helper,  # Pass midi_helper instead of midi_out
                    parent=self,
                )
            self.effects_editor.show()
            self.effects_editor.raise_()

        except Exception as ex:
            logging.error(f"Error showing Effects editor: {str(ex)}")

    def _open_midi_debugger(self):
        """Open MIDI debugger window"""
        if not self.midi_helper:
            logging.error("MIDI helper not initialized")
            return
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
                midi_helper=self.midi_helper, parent=self, save_mode=False, editors=self.editors,
            )
            patch_manager.show()
        except Exception as ex:
            logging.error(f"Error loading patch: {str(ex)}")

    def _save_patch(self):
        """Show save patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper,
                parent=self,
                save_mode=True,
                editors=self.editors
            )
            patch_manager.show()
        except Exception as ex:
            logging.error(f"Error saving patch: {str(ex)}")

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

        except Exception as ex:
            logging.error(f"Error during close event: {str(ex)}")
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

    def _update_octave_ui(self):
        """Update octave-related UI elements"""
        self.octave_down.setChecked(self.current_octave < 0)
        self.octave_up.setChecked(self.current_octave > 0)
        self._update_display()
        logging.debug(
            f"Updated octave to: {self.current_octave} (value: {hex(CENTER_OCTAVE_VALUE + self.current_octave)})"
        )

    def _send_octave(self, direction):
        """Send octave change MIDI message"""
        if self.midi_helper:
            # Update octave tracking
            self.current_octave = max(-3, min(3, self.current_octave + direction))

            # Update UI via centralized method
            self._update_octave_ui()

            # Update display
            self._update_display()
            # Map octave value to correct SysEx value
            # -3 = 0x3D, -2 = 0x3E, -1 = 0x3F, 0 = 0x40, +1 = 0x41, +2 = 0x42, +3 = 0x43
            octave_value = 0x40 + self.current_octave  # 0x40 is center octave
            logging.debug(
                f"Sending octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})"
            )
            sysex_message = RolandSysEx(
                address_msb=AddressMemoryAreaMSB.TEMPORARY_TONE,
                address_umb=AddressOffsetTemporaryToneUMB.DIGITAL_PART_1,
                address_lmb=AddressOffsetProgramLMB.COMMON,
                address_lsb=DigitalCommonParameter.OCTAVE_SHIFT.value[0],
                value=octave_value,
            )
            return self.midi_helper.send_midi_message(sysex_message)

    def send_midi_parameter(
        self,
            address_lmb,
            address_lsb,
            value,
            address_msb=AddressMemoryAreaMSB.PROGRAM,
            address_umb=AddressOffsetSystemUMB.COMMON,
    ) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False
        try:
            # Ensure value is included in the MIDI message
            sysex_message = RolandSysEx(
                address_msb=address_msb,
                address_umb=address_umb,
                address_lmb=address_lmb,
                address_lsb=address_lsb,
                value=value,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as ex:
            logging.error(f"MIDI error setting {address_lsb}: {str(ex)}")
            return False

    def _send_arp_key_hold(self, state):
        """Send arpeggiator key hold (latch) command"""
        try:
            if self.midi_helper:
                self.key_hold_latched = not self.key_hold_latched
                # Value: 0 = OFF, 1 = ON
                value = 0x01 if state else 0x00
                            # Ensure value is included in the MIDI message
                sysex_message = RolandSysEx(
                    address_msb=AddressMemoryAreaMSB.PROGRAM,
                    address_umb=AddressOffsetSystemUMB.COMMON,
                    address_lmb=AddressOffsetProgramLMB.CONTROLLER,
                    address_lsb=0x02,
                    value=value,
                )
                self.midi_helper.send_midi_message(sysex_message)
                logging.debug(f"Sent arpeggiator key hold: {'ON' if state else 'OFF'}")

        except Exception as ex:
            logging.error(f"Error sending arp key hold: {str(ex)}")

    def _send_arp_on_off(self, state):
        """Send arpeggiator on/off command"""
        try:
            if self.midi_helper:
                value = 0x01 if state else 0x00  # 1 = ON, 0 = OFF
                logging.info(f"Sent arpeggiator on/off: {'ON' if state else 'OFF'}")
                # send arp on to all 4 program zones
                for zone in [AddressOffsetProgramLMB.CONTROLLER,
                             AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_1,
                             AddressOffsetProgramLMB.ZONE_DIGITAL_SYNTH_2,
                             AddressOffsetProgramLMB.ZONE_ANALOG_SYNTH,
                             AddressOffsetProgramLMB.ZONE_DRUM]:
                    sysex_message = RolandSysEx(
                        address_msb=AddressMemoryAreaMSB.PROGRAM,
                        address_umb=AddressOffsetSystemUMB.COMMON,
                        address_lmb=zone,
                        address_lsb=ArpeggioParameter.ARPEGGIO_SWITCH.value[0],
                        value=value,
                    )
                    self.midi_helper.send_midi_message(sysex_message)
        except Exception as ex:
            logging.error(f"Error sending arp on/off: {str(ex)}")

    def _set_midi_ports(self, in_port, out_port):
        """Set MIDI input and output ports."""
        try:
            # Close existing ports safely
            if self.midi_in:
                self.midi_in.close_port()
                self.midi_in = None
            if self.midi_out:
                self.midi_out.close_port()
                self.midi_out = None

            # Check available ports before opening new ones
            available_in_ports = MidiIOHelper.get_input_ports()
            available_out_ports = MidiIOHelper.get_output_ports()

            if in_port not in available_in_ports:
                logging.warning(
                    f"Input port '{in_port}' not found. Available: {available_in_ports}"
                )
                return

            if out_port not in available_out_ports:
                logging.warning(
                    f"Output port '{out_port}' not found. Available: {available_out_ports}"
                )
                return

            # Open new ports
            self.midi_in = MidiIOHelper.open_input(in_port, self)
            self.midi_out = MidiIOHelper.open_output(out_port, self)

            # Store port names
            self.midi_in_port_name = in_port
            self.midi_out_port_name = out_port

            # Initialize singleton connection
            MIDIConnection().initialize(self.midi_in, self.midi_out, self)
            MIDIConnection().identify_device()

            # Update MIDI helper references
            self.midi_helper.midi_in = self.midi_in
            self.midi_helper.midi_out = self.midi_out

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

        except Exception as ex:
            logging.error(f"Error setting MIDI ports: {str(ex)}")

    def _open_midi_message_debug(self):
        """Open MIDI message debug window"""
        if not self.midi_message_debug:
            self.midi_message_debug = MIDIMessageDebug()
            self.midi_message_debug.setAttribute(Qt.WA_DeleteOnClose)
            self.midi_message_debug.destroyed.connect(self._midi_message_debug_closed)
        self.midi_message_debug.show()
        self.midi_message_debug.raise_()

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

        except Exception as ex:
            logging.error(f"Error saving settings: {str(ex)}")

    def _auto_connect_jdxi(self):
        """Attempt to automatically connect to JD-Xi MIDI ports."""
        try:
            # Get available ports
            input_ports = self.midi_helper.get_input_ports()
            output_ports = self.midi_helper.get_output_ports()

            # Find JD-Xi ports
            selected_in_port = _find_jdxi_port(input_ports, "input")
            selected_out_port = _find_jdxi_port(output_ports, "output")

            # Ensure both ports are found
            if not selected_in_port or not selected_out_port:
                logging.warning(
                    f"JD-Xi MIDI auto-connect failed. Found input: {selected_in_port}, output: {selected_out_port}"
                )
                return False

            # Open the found ports
            self.midi_helper.open_input_port(selected_in_port)
            self.midi_helper.open_output_port(selected_out_port)

            # Explicitly store the selected ports # FIXME: this looks incorrect
            self.midi_helper.current_in_port = selected_in_port
            self.midi_helper.current_out_port = selected_out_port

            # Verify connection
            if self._verify_jdxi_connection():
                logging.info(
                    f"Successfully connected to JD-Xi MIDI: {selected_in_port} / {selected_out_port}"
                )
                return True
            else:
                logging.warning("JD-Xi identity verification failed.")
                return False

        except Exception as ex:
            logging.error(f"Error auto-connecting to JD-Xi: {str(ex)}")
            return False

    def _verify_jdxi_connection(self):
        """Verify connected device is address JD-Xi by sending identity request"""
        try:
            # Create identity request message using dataclass
            identity_request = IdentityRequestMessage()

            # Send request
            if self.midi_helper:
                self.midi_helper.send_raw_message(identity_request.to_message_list())
                logging.debug("Sent JD-Xi identity request")

        except Exception as ex:
            logging.error(f"Error sending identity request: {str(ex)}")

    def handle_piano_note_on(self, note_num):
        """Handle piano key press"""
        if self.midi_helper:
            # self.channel is 0-indexed, so add 1 to match MIDI channel in log file
            msg = [0x90 + self.channel, note_num, 100]
            self.midi_helper.send_raw_message(msg)
            logging.info(f"Sent Note On: {note_num} on channel {self.channel + 1}")

    def handle_piano_note_off(self, note_num):
        """Handle piano key release"""
        if self.midi_helper:
            # Calculate the correct status byte for note_off:
            # 0x80 is the base for note_off messages. Subtract 1 if self.channel is 1-indexed.
            if not self.key_hold_latched:
                status = 0x80 + self.channel
                msg = [status, note_num, 0]
                self.midi_helper.send_raw_message(msg)
                logging.info(f"Sent Note Off: {note_num} on channel {self.channel + 1}")
    
    def _load_last_preset(self):
        """Load the last used preset from settings."""
        try:
            # Get last preset info from settings
            synth_type = self.settings.value("last_preset/synth_type", JDXISynth.DIGITAL_1)
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)
            channel = self.settings.value("last_preset/channel", 0, type=int)
    
            # Define mappings for synth types
            synth_mappings = {
                JDXISynth.ANALOG: (JDXIPresets.ANALOG, 0, 7),
                JDXISynth.DIGITAL_1: (JDXIPresets.DIGITAL_ENUMERATED, 1, 16),
                JDXISynth.DIGITAL_2: (JDXIPresets.DIGITAL_ENUMERATED, 2, 16),
                JDXISynth.DRUMS: (JDXIPresets.DRUM_ENUMERATED, 3, 16),
            }
    
            # Get preset list and MIDI parameters based on synth type
            presets, bank_msb, lsb_divisor = synth_mappings.get(synth_type, ([], 0, 1))
            bank_lsb = preset_num // lsb_divisor
            program = preset_num % lsb_divisor
    
            # Send MIDI messages to load preset
            if hasattr(self, "midi_helper") and self.midi_helper:
                self.midi_helper.send_bank_select(bank_msb, bank_lsb, channel)
                self.midi_helper.send_program_change(program, channel)
    
                # Update display and channel
                preset_name = presets[preset_num - 1]  # Adjust index to be 0-based
                self._update_display_preset(preset_num, preset_name, channel)
    
                logging.debug(f"Loaded last preset: {preset_name} on channel {channel}")
    
        except Exception as ex:
            logging.error(f"Error loading last preset: {str(ex)}")
    
    def _load_last_presetold(self):
        """Load the last used preset from settings"""
        try:
            # Get last preset info from settings
            synth_type = self.settings.value(
                "last_preset/synth_type", JDXISynth.DIGITAL_1
            )
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)
            channel = self.settings.value("last_preset/channel", 0, type=int)

            # Get preset list based on synth preset_type
            if synth_type == JDXISynth.ANALOG:
                presets = JDXIPresets.ANALOG
                bank_msb = 0
                bank_lsb = preset_num // 7
                program = preset_num % 7
            elif synth_type == JDXISynth.DIGITAL_1:
                presets = JDXIPresets.DIGITAL_ENUMERATED
                bank_msb = 1
                bank_lsb = preset_num // 16
                program = preset_num % 16
            elif synth_type == JDXISynth.DIGITAL_2:
                presets = JDXIPresets.DIGITAL_ENUMERATED
                bank_msb = 2
                bank_lsb = preset_num // 16
                program = preset_num % 16
            else:  # Drums
                presets = JDXIPresets.DRUM_ENUMERATED
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

        except Exception as ex:
            logging.error(f"Error loading last preset: {str(ex)}")

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

        except Exception as ex:
            logging.error(f"Error saving last preset: {str(ex)}")

    def _load_favorite(self, button):
        """Load preset from favorite button"""
        if button.preset:
            if self.midi_helper:
                # Get preset info from button
                self.preset_type = button.preset.type
                self.current_preset_index = button.preset.tone_number
                self.channel = button.preset.channel
                # Update display - REMOVED the preset_num + 1
                self._update_display_preset(
                    self.current_preset_index + 1,  # Convert to 1-based index
                    button.preset.tone_name,
                    self.channel,
                )
                preset_data = Preset(
                    type=self.preset_type,  # Ensure this is address valid preset_type
                    number=self.current_preset_index,
                    channel=self.channel,
                )
                # Send MIDI messages to load preset
                self.load_preset(preset_data)

    def _show_favorite_context_menu(
        self, pos, button: Union[FavoriteButton, SequencerSquare]
    ):
        """Show context menu for favorite button"""
        menu = QMenu()

        # Add save action if we have address current preset
        if hasattr(self, "current_preset_num"):
            save_action = menu.addAction("Save Current Preset")
            save_action.triggered.connect(lambda: self._save_to_favorite(button))

        # Add clear action if slot has address preset
        if button.preset:
            clear_action = menu.addAction("Clear Slot")
            clear_action.triggered.connect(lambda: self._clear_favorite(button))

        menu.exec_(button.mapToGlobal(pos))

    def _save_to_favorite(self, button: Union[FavoriteButton, SequencerSquare]):
        """Save current preset to favorite slot"""
        if hasattr(self, "current_preset_num"):
            # Get current preset info from settings
            synth_type = self.settings.value("last_preset/synth_type", JDXISynth.ANALOG)
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

            except Exception as ex:
                logging.error(f"Error saving to favorite: {str(ex)}")
                QMessageBox.warning(self, "Error", f"Error saving preset: {str(ex)}")

    def _clear_favorite(self, button: FavoriteButton):
        """Clear favorite slot"""
        button.clear_preset()

    def _load_saved_favorites(self):
        """Load saved favorites from settings"""
        for button in self.sequencer_buttons:
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
                self.digital_1_preset_helper = PresetHelper(self.midi_helper)
                self.digital_1_preset_helper.load_preset(
                    preset_data,
                )
                # Store as last loaded preset
                self.last_preset = preset_data
                # self.settings.setValue("last_preset", preset_data)

        except Exception as ex:
            logging.error(f"Error loading preset: {str(ex)}")

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

        except Exception as ex:
            logging.error(f"Error setting MIDI ports: {str(ex)}")
            return False

    def connect_jdxi_midi_ports(self):
        """Connect to MIDI ports"""
        try:
            # Find JD-Xi ports
            in_port, out_port = self.midi_helper.find_jdxi_ports()

            if in_port and out_port:
                # Open ports
                if self.midi_helper.open_ports(in_port, out_port):
                    logging.info(f"Connected to JD-Xi ({in_port}, {out_port})")
                    self.statusBar().showMessage("Connected to JD-Xi")
                    return True

            logging.warning("JD-Xi not found")
            self.statusBar().showMessage("JD-Xi not found")
            return False

        except Exception as ex:
            logging.error(f"Error connecting to MIDI: {str(ex)}")
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

        except Exception as ex:
            logging.error(f"Error showing Vocal FX editor: {str(ex)}")

    def _show_arpeggio_editor(self, event):
        """Show the arpeggio editor window"""
        try:
            if not hasattr(self, "arpeggio_editor"):
                logging.debug("Creating new arpeggio editor")
                self.arpeggio_editor = ArpeggioEditor(midi_helper=self.midi_helper)
            logging.debug("Showing arpeggio editor")
            self.arpeggio_editor.show()
        except Exception as ex:
            logging.error(f"Error showing Arpeggiator editor: {str(ex)}")

    def _open_program_editor(self, event):
        """Open the ProgramEditor when the digital display is clicked."""
        if event.button() == Qt.MouseButton.LeftButton:
            try:
                self._show_editor("Program", ProgramEditor)
            except Exception as ex:
                logging.error(f"Error opening Program editor: {str(ex)}")
