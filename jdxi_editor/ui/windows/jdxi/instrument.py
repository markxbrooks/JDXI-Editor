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
import threading
from functools import partial
from typing import Union, Optional

from PySide6.QtGui import QShortcut, QKeySequence, QMouseEvent, QCloseEvent

from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtCore import Qt, QSettings, QTimer

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import (
    AddressStartMSB,
    AddressOffsetTemporaryToneUMB,
    AddressOffsetSystemUMB,
    RolandSysExAddress,
    AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.control_change.sustain import ControlChangeSustain
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.parameter.program.zone import AddressParameterProgramZone
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.jdxi.preset.button import JDXiPresetButtonData
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.midi.program.helper import JDXiProgramHelper
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.dialogs.about import UiAboutDialog
from jdxi_editor.ui.editors import (
    AnalogSynthEditor,
    DigitalSynthEditor,
    DrumCommonEditor,
    ArpeggioEditor,
    EffectsCommonEditor,
    VocalFXEditor,
    ProgramEditor,
    SynthEditor,
)
from jdxi_editor.ui.editors.digital.editor import DigitalSynth2Editor
from jdxi_editor.ui.editors.helpers.program import (
    get_program_id_by_name,
)
from jdxi_editor.ui.editors.io.player import MidiPlayer
from jdxi_editor.ui.editors.pattern.pattern import PatternSequencer
from jdxi_editor.ui.editors.io.preset import PresetEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.jdxi.style.factory import generate_sequencer_button_style
from jdxi_editor.ui.widgets.button import SequencerSquare
from jdxi_editor.ui.windows.jdxi.utils import show_message_box
from jdxi_editor.ui.windows.midi.config_dialog import MIDIConfigDialog
from jdxi_editor.ui.windows.midi.debugger import MIDIDebugger
from jdxi_editor.ui.windows.midi.monitor import MIDIMessageMonitor
from jdxi_editor.ui.windows.patch.manager import PatchManager
from jdxi_editor.ui.windows.jdxi.ui import JDXiUi
from jdxi_editor.ui.widgets.viewer.log import LogViewer
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper

# Homeless value
CENTER_OCTAVE_VALUE = 0x40  # for octave up/down buttons


class JDXiInstrument(JDXiUi):
    """
    class JDXiInstrument
    """
    def __init__(self):
        super().__init__()
        if platform.system() == "Windows":
            self.setStyleSheet(JDXiStyle.TRANSPARENT + JDXiStyle.ADSR_DISABLED)
        # Try to auto-connect to JD-Xi
        self.midi_helper.auto_connect_jdxi()
        if (
            not self.midi_helper.current_in_port
            or not self.midi_helper.current_out_port
        ):
            self._show_midi_config()
        self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
        self.midi_out_indicator.set_state(self.midi_helper.is_output_open)
        self.sysex_composer = JDXiSysExComposer()
        self.program_helper = JDXiProgramHelper(self.midi_helper, MidiChannel.PROGRAM)
        self.settings = QSettings("jdxi_manager2", "settings")
        self._load_settings()
        self._toggle_illuminate_sequencer_lightshow(True)
        self._load_saved_favorites()
        self._update_synth_button_styles()
        self._set_callbacks()
        self._init_preset_helpers()
        self.show()
        self.data_request()

    def _init_preset_helpers(self):
        """Initialize preset helpers dynamically"""
        preset_configs = [
            (
                JDXiSynth.DIGITAL_SYNTH_1,
                JDXiPresetToneList.DIGITAL_ENUMERATED,
                MidiChannel.DIGITAL1,
            ),
            (
                JDXiSynth.DIGITAL_SYNTH_2,
                JDXiPresetToneList.DIGITAL_ENUMERATED,
                MidiChannel.DIGITAL2,
            ),
            (
                JDXiSynth.ANALOG_SYNTH,
                JDXiPresetToneList.ANALOG_ENUMERATED,
                MidiChannel.ANALOG,
            ),
            (JDXiSynth.DRUM_KIT, JDXiPresetToneList.DRUM_ENUMERATED, MidiChannel.DRUM),
        ]
        from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper

        self.preset_helpers = {
            synth_type: JDXiPresetHelper(
                self.midi_helper, presets, channel=channel, preset_type=synth_type
            )
            for synth_type, presets, channel in preset_configs
        }
        for helper in self.preset_helpers.values():
            helper.update_display.connect(self.update_display_callback)

    def _set_callbacks(self):
        """Set up signal-slot connections for various UI elements."""
        self.key_hold_button.clicked.connect(self._midi_send_arp_key_hold)
        self.arpeggiator_button.clicked.connect(self._midi_send_arp_on_off)
        self.digital_display.mousePressEvent = self._show_program_editor
        self.program_down_button.clicked.connect(self._program_previous)
        self.program_up_button.clicked.connect(self._program_next)
        self.midi_helper.update_program_name.connect(self.set_current_program_name)
        self.midi_helper.midi_message_incoming.connect(self._midi_blink_input)
        self.midi_helper.midi_message_outgoing.connect(self._midi_blink_output)
        self.midi_helper.update_tone_name.connect(
            lambda tone_name, synth_type: self.set_preset_name_by_type(
                tone_name, synth_type
            ),
        )
        self.midi_helper.midi_program_changed.connect(self.set_current_program_number)
        # ctrl-R for data request
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event
        :param event: QCloseEvent
        :return: None
        """
        try:
            self.midi_helper.close_ports()
            self._save_settings()
            event.accept()
        except Exception as ex:
            log.error(f"Error during close event: {str(ex)}")
            event.ignore()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        mousePressEvent
        :param event: mousePressEvent
        :return: None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent) :
        """
        mouseMoveEvent
        :param event: QMouseEvent
        :return: None
        """
        if self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        mouseReleaseEvent
        :param event: QMouseEvent
        :return: None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def data_request(self) -> None:
        """
        Request the current value of the NRPN parameter from the device.
        """
        threading.Thread(
            target=send_with_delay,
            args=(
                self.midi_helper,
                self.midi_requests,
            ),
        ).start()

    def _handle_program_change(self, bank_letter: str, program_number: int) -> None:
        """
        perform data request
        :param bank_letter: str
        :param program_number: int
        :return: None
        """
        self.data_request()

    def add_editor(self, editor: SynthEditor) -> None:
        """
        add editor
        :param editor: SynthEditor
        :return: None
        """
        self.editors.append(editor)
        log.message(f"Editor added. Now {self.editors} available")

    def set_preset_name_by_type(self, tone_name: str, synth_type: str) -> None:
        """
        set preset name by type
        :param tone_name: str
        :param synth_type: str
        :return: None
        """
        if synth_type == JDXiSynth.PROGRAM:
            pass
        self.preset_manager.set_preset_name_by_type(synth_type, tone_name)
        self._update_display()

    def _get_preset_helper_for_current_synth(self) -> JDXiPresetHelper:
        """
        Return the appropriate preset helper based on the current synth preset_type
        :return: JDXiPresetHelper
        """
        helper = self.preset_helpers.get(self.current_synth_type)
        if helper is None:
            logging.warning(
                f"Unknown synth preset_type: {self.current_synth_type}, defaulting to digital_1"
            )
            return self.preset_helpers[JDXiSynth.DIGITAL_SYNTH_1]  # Safe fallback
        return helper

    def set_current_program_name(self, program_name: str):
        """
        program name
        :param program_name: str
        :return:
        """
        self.current_program_name = program_name
        self.current_program_id = get_program_id_by_name(program_name)
        if not self.current_program_id:
            self.current_program_number = 0
        else:
            self.current_program_number = int(self.current_program_id[1:])
        self._update_display()

    def set_current_program_number(self, channel: int, program_number: int) -> None:
        """
        program number
        :param channel: int
        :param program_number: int
        :return: None
        """
        self.current_program_number = program_number + 1
        self.data_request()
        self._update_display()

    def _select_synth(self, synth_type: JDXiSynth) -> None:
        """
        Select address synth and update button styles
        :param synth_type: JDXiSynth
        :return: None
        """
        log.parameter("Selected synth:", synth_type)
        self.current_synth_type = synth_type
        self._update_synth_button_styles()
        self.preset_helper = self._get_preset_helper_for_current_synth()
        self.preset_helper.preset_changed.connect(self.midi_helper.send_program_change)

    def _update_synth_button_styles(self):
        """Update styles for synth buttons based on selection."""
        for synth_type, button in self.synth_buttons.items():
            is_selected = synth_type == self.current_synth_type
            button.setStyleSheet(
                JDXiStyle.BUTTON_ROUND_SELECTED
                if not is_selected
                else JDXiStyle.BUTTON_ROUND
            )
            button.setChecked(is_selected)

    def _program_update(self, index_change: int) -> None:
        """
        Update the program by incrementing or decrementing its index
        :param index_change: int
        :return: None
        """
        new_program_number = self.current_program_number + index_change
        if new_program_number < 1:
            show_message_box("First program", "Already at the first program.")
            return
        self.current_program_number = new_program_number
        if index_change > 0:
            self.program_helper.next_program()
        else:
            self.program_helper.previous_program()
        self._update_display()

    def _program_previous(self) -> None:
        """Decrement the program index and update the display."""
        self._program_update(-1)

    def _program_next(self) -> None:
        """Increment the program index and update the display."""
        self._program_update(1)

    def _preset_update(self, index_change: int) -> None:
        """
        Update the preset by incrementing or decrementing its index
        :param index_change: int
        :return: None
        """
        presets = self.preset_manager.get_presets_for_synth(
            synth=self.current_synth_type
        )
        max_index = len(presets) - 1
        new_preset_index = self.current_preset_index + index_change

        if new_preset_index < 0:
            show_message_box("First preset", "Already at the first preset.")
            return
        if new_preset_index > max_index:
            show_message_box("Last preset", "Already at the last preset.")
            return

        self.current_preset_index = new_preset_index
        preset_helper = self._get_preset_helper_for_current_synth()
        self._update_display_preset(
            self.current_preset_index,
            presets[self.current_preset_index],
            self.channel,
        )
        preset_helper.load_preset_by_program_change(
            self.current_preset_index, self.current_synth_type
        )

    def _preset_previous(self) -> None:
        """
        Decrement the tone index and update the display
        :return: None
        """
        self._preset_update(-1)

    def _preset_next(self) -> None:
        """Increment the tone index and update the display."""
        self._preset_update(1)

    def update_display_callback(
        self, synth_type: JDXiSynth, preset_index: int, channel: int
    ) -> None:
        """
        Update the display for the given synth preset_type and preset index
        :param synth_type: JDXiSynth
        :param preset_index: int
        :param channel: int
        :return: None
        """
        log.message(
            f"update_display_callback: synth_type: {synth_type} preset_index: {preset_index}, channel: {channel}",
        )
        presets = self.preset_manager.get_presets_for_channel(channel)
        self._update_display_preset(
            preset_index,
            presets[preset_index],
            channel,
        )

    def _toggle_illuminate_sequencer_lightshow(self, enabled: bool) -> None:
        """
        Toggle the sequencer lightshow on or off
        :param enabled: bool
        :return: None
        """
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
            for i, button in enumerate(self.sequencer_buttons):
                button.setChecked(False)
                button.setStyleSheet(
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

    def show_editor(self, editor_type: str) -> None:
        """
        Show editor of given type
        :param editor_type: str
        :return: None
        """
        self.editor_registry = {
            "vocal_fx": (
                "Vocal Effects",
                VocalFXEditor,
                JDXiSynth.VOCAL_FX,
                MidiChannel.VOCAL,
            ),
            "digital1": (
                "Digital Synth 1",
                DigitalSynthEditor,
                JDXiSynth.DIGITAL_SYNTH_1,
                MidiChannel.DIGITAL1,
                {"synth_number": 1},
            ),
            "digital2": (
                "Digital Synth 2",
                DigitalSynth2Editor,
                JDXiSynth.DIGITAL_SYNTH_2,
                MidiChannel.DIGITAL2,
                {"synth_number": 2},
            ),
            "analog": (
                "Analog Synth",
                AnalogSynthEditor,
                JDXiSynth.ANALOG_SYNTH,
                MidiChannel.ANALOG,
            ),
            "drums": ("Drums", DrumCommonEditor, JDXiSynth.DRUM_KIT, MidiChannel.DRUM),
            "arpeggio": ("Arpeggiator", ArpeggioEditor, None, None),
            "effects": ("Effects", EffectsCommonEditor, None, None),
            "pattern": ("Pattern", PatternSequencer, None, None),
            "preset": ("Preset", PresetEditor, None, None),
            "program": ("Program", ProgramEditor, None, None),
            "midi_file": ("MIDI File", MidiPlayer, None, None),
        }

        config = self.editor_registry.get(editor_type)
        if not config:
            logging.warning(f"Unknown editor type: {editor_type}")
            return

        title, editor_class, synth_type, midi_channel, kwargs = (
            (*config, {}) if len(config) == 4 else config
        )

        if synth_type:
            self.current_synth_type = synth_type
        if midi_channel:
            self.channel = midi_channel

        self._show_editor(title, editor_class, **kwargs)

    def _show_editor(self, title: str, editor_class, **kwargs) -> None:
        """
        _show editor
        :param title: str
        :param editor_class: class
        :param kwargs: Any
        :return: None
        """
        try:
            instance_attr = f"{editor_class.__name__.lower()}_instance"
            existing_editor = getattr(self, instance_attr, None)
            if existing_editor:
                existing_editor.show()
                existing_editor.raise_()
                return

            preset_helper = (
                self._get_preset_helper_for_current_synth()
                if editor_class
                in [
                    ArpeggioEditor,
                    DigitalSynthEditor,
                    DigitalSynth2Editor,
                    AnalogSynthEditor,
                    DrumCommonEditor,
                    PatternSequencer,
                    ProgramEditor,
                    PresetEditor,
                    MidiPlayer,
                    VocalFXEditor,
                    EffectsCommonEditor,
                ]
                else None
            )

            editor = (
                editor_class(
                    midi_helper=self.midi_helper,
                    preset_helper=preset_helper,
                    parent=self,
                    **kwargs,
                )
                if preset_helper
                else editor_class(
                    midi_out=self.midi_helper.midi_out,
                    parent=self,
                    **kwargs,
                )
            )
            editor.setWindowTitle(title)
            editor.show()
            editor.raise_()

            setattr(self, instance_attr, editor)
            self.add_editor(editor)
            if hasattr(editor, "preset_helper"):
                editor.preset_helper.update_display.connect(
                    self.update_display_callback
                )
            if hasattr(editor, "partial_editors"):
                for i, partial_item in enumerate(editor.partial_editors.values()):
                    self.add_editor(partial_item)

        except Exception as ex:
            log.error(f"Error showing {title} editor", exception=ex)

    def _show_log_viewer(self) -> None:
        """Show log viewer window"""
        if not self.log_viewer:
            self.log_viewer = LogViewer(midi_helper=self.midi_helper, parent=self)
        self.log_viewer.show()
        self.log_viewer.raise_()
        log.message("Showing LogViewer window")

    def _show_midi_config(self) -> None:
        """Show MIDI configuration dialog"""
        try:
            dialog = MIDIConfigDialog(self.midi_helper, parent=self)
            dialog.exec()

        except Exception as ex:
            log.error("Error showing MIDI configuration", exception=ex)
            self.show_error("MIDI Configuration Error", str(ex))

    def _show_midi_debugger(self) -> None:
        """Open MIDI debugger window"""
        if not self.midi_helper:
            log.message("MIDI helper not initialized")
            return
        if not self.midi_debugger:
            self.midi_debugger = MIDIDebugger(self.midi_helper)
            # Clean up reference when window is closed
            self.midi_debugger.setAttribute(Qt.WA_DeleteOnClose)
            log.message("Created new MIDI debugger window")
        self.midi_debugger.show()
        self.midi_debugger.raise_()

    def _show_midi_message_monitor(self) -> None:
        """Open MIDI message monitor window"""
        if not self.midi_message_monitor:
            self.midi_message_monitor = MIDIMessageMonitor(
                midi_helper=self.midi_helper, parent=self
            )
            self.midi_message_monitor.setAttribute(Qt.WA_DeleteOnClose)
        self.midi_message_monitor.show()
        self.midi_message_monitor.raise_()

    def _show_program_editor(self, _) -> None:
        """Open the ProgramEditor when the digital display is clicked."""
        self.show_editor("program")

    def _show_about_help(self) -> None:
        """
        _show_about_help
        :return:
        """
        about_dialog = UiAboutDialog(self)
        about_dialog.setup_ui(about_dialog)
        about_dialog.setAttribute(Qt.WA_DeleteOnClose)
        about_dialog.exec()

    def _patch_load(self) -> None:
        """Show load patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper,
                parent=self,
                save_mode=False,
                editors=self.editors,
            )
            patch_manager.show()
        except Exception as ex:
            log.error("Error loading patch", exception=ex)

    def _patch_save(self) -> None:
        """Show save patch dialog"""
        try:
            patch_manager = PatchManager(
                midi_helper=self.midi_helper,
                parent=self,
                save_mode=True,
                editors=self.editors,
            )
            patch_manager.show()
        except Exception as ex:
            log.error("Error saving patch", exception=ex)

    def load_button_preset(self, button: SequencerSquare) -> None:
        """
        load preset data stored on the button
        :param button: SequencerSquare
        :return: None
        """
        preset = button.preset
        preset_data = JDXiPresetButtonData(
            type=preset.type,  # Ensure this is address valid preset_type
            number=preset.number,  # Convert to 1-based index
        )
        self.current_synth_type = preset.type
        preset_helper = self._get_preset_helper_for_current_synth()
        preset_helper.load_preset(preset_data)

    def _generate_button_preset(self) -> Optional[JDXiPresetButtonData]:
        """
        Generate a ButtonPreset object based on the current preset.

        :return: Optional[JDXiPresetButtonData]
        """

        try:
            # Update the current preset index or details here
            button_preset = JDXiPresetButtonData(
                number=self.preset_manager.current_preset_number,
                name=self.preset_manager.current_preset_name,
                type=self.current_synth_type,
            )
            log.message(f"Current preset retrieved: {button_preset}")
            return button_preset
        except Exception as ex:
            log.error("Error generating button preset", ex)
            return None

    def _get_current_preset_name_from_settings(self) -> str:
        """
        :return: str

        Get the name of the currently selected preset
        based on the last used preset type and number.
        """
        try:
            synth_type = self.settings.value(
                "last_preset/synth_type", JDXiSynth.DIGITAL_SYNTH_1
            )
            preset_number = self.settings.value("last_preset/preset_num", 0, type=int)

            # Get preset name - adjust index to be 0-based
            if synth_type == JDXiSynth.ANALOG_SYNTH:
                return JDXiPresetToneList.ANALOG[
                    preset_number - 1
                ]  # Convert 1-based to 0-based
            if synth_type == JDXiSynth.DIGITAL_SYNTH_1:
                return JDXiPresetToneList.DIGITAL_ENUMERATED[preset_number - 1]
            if synth_type == JDXiSynth.DIGITAL_SYNTH_2:
                return JDXiPresetToneList.DIGITAL_ENUMERATED[preset_number - 1]
            else:
                return JDXiPresetToneList.DRUM_ENUMERATED[preset_number - 1]
        except IndexError:
            return "INIT PATCH"

    def _get_current_preset_type(self) -> JDXiSynth:
        """
        Get the preset_type of the currently selected preset
        :return: JDXiSynth
        """
        return self.current_synth_type
        # return self.settings.value("last_preset/synth_type", PresetType.ANALOG)

    def _ui_update_octave(self) -> None:
        """Update octave-related UI elements"""
        self.octave_down.setChecked(self.current_octave < 0)
        self.octave_up.setChecked(self.current_octave > 0)
        self._update_display()
        log.message(
            f"Updated octave to: {self.current_octave} (value: {hex(CENTER_OCTAVE_VALUE + self.current_octave)})"
        )

    def _midi_init_ports(
        self, in_port: MidiIOController, out_port: MidiIOController
    ) -> None:
        """
        Set MIDI input and output ports
        :param in_port:
        :param out_port:
        :return: None
        """
        try:
            self.midi_helper.midi_in = MidiIOHelper.open_input(in_port, self)
            self.midi_helper.midi_out = MidiIOHelper.open_output(out_port, self)
            self.midi_helper.in_port_name = in_port
            self.midi_helper.out_port_name = out_port
            self.midi_helper.identify_device()
            self.midi_in_indicator.set_active(self.midi_helper.midi_in is not None)
            self.midi_out_indicator.set_active(self.midi_helper.midi_out is not None)
            self._save_settings()
        except Exception as ex:
            log.error("Error setting MIDI ports", exception=ex)

    def _midi_blink_input(self, _):
        """Handle incoming MIDI messages and flash indicator"""
        self.midi_in_indicator.blink()

    def _midi_blink_output(self, _):
        """handle outgoing message blink"""
        self.midi_out_indicator.blink()

    def _midi_send_octave(self, direction: int) -> Union[None, bool]:
        """
        Send octave change MIDI message
        :param direction: int
        :return: Union[None, bool]
        """
        if self.midi_helper:
            # Update octave tracking
            self.current_octave = max(-3, min(3, self.current_octave + direction))
            self._ui_update_octave()
            self._update_display()
            # Map octave value to correct SysEx value
            # -3 = 0x3D, -2 = 0x3E, -1 = 0x3F, 0 = 0x40, +1 = 0x41, +2 = 0x42, +3 = 0x43
            octave_value = 0x40 + self.current_octave  # 0x40 is center octave
            log.message(
                f"Sending octave change SysEx, new octave: {self.current_octave} (value: {hex(octave_value)})"
            )
            address = RolandSysExAddress(
                msb=AddressStartMSB.TEMPORARY_TONE,
                umb=AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,
                lmb=AddressOffsetProgramLMB.COMMON,
                lsb=AddressParameterDigitalCommon.OCTAVE_SHIFT.lsb,
            )
            sysex_message = RolandSysEx(
                sysex_address=address,
                value=octave_value,
            )
            return self.midi_helper.send_midi_message(sysex_message)

    def _midi_send_arp_key_hold(self, state: bool) -> None:
        """
        Send arpeggiator key hold (latch) command
        :param state: bool
        :return: None
        """
        try:
            if self.midi_helper:
                self.midi_key_hold_latched = not self.midi_key_hold_latched
                # Value: 0 = OFF, 1 = ON
                value = 0x01 if state else 0x00
                address1 = RolandSysExAddress(
                    msb=AddressStartMSB.TEMPORARY_TONE,
                    umb=AddressOffsetTemporaryToneUMB.DIGITAL_SYNTH_1,
                    lmb=AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_1,
                    lsb=0x46,
                )
                address2 = RolandSysExAddress(
                    msb=AddressStartMSB.TEMPORARY_TONE,
                    umb=0x01,
                    lmb=0x00,
                    lsb=0x14,
                )
                # Assuming RolandSysEx accepts an address in bytes
                for address in [address1, address2]:
                    # Send the SysEx message
                    sysex_message = RolandSysEx(
                        sysex_address=address,
                        value=value,
                    )
                    self.midi_helper.send_midi_message(sysex_message)
                cc_value = 127 if state else 0
                cc_list = [
                    ControlChangeSustain.HOLD1,  # Hold-1 Damper (Sustain) – CC64
                    ControlChangeSustain.PORTAMENTO,  # Portamento (on/off)
                    ControlChangeSustain.SOSTENUTO,  # Sostenuto – CC66
                    ControlChangeSustain.SOFT_PEDAL,  # Soft Pedal (Una Corda) – CC67
                    ControlChangeSustain.LEGATO,  # Legato foot switch
                    ControlChangeSustain.HOLD2,
                ]  # Hold-2
                # cc_list = [68]
                for cc in cc_list:
                    self.midi_helper.send_control_change(
                        cc, cc_value, MidiChannel.DIGITAL1
                    )
                log.message(f"Sent arpeggiator key hold: {'ON' if state else 'OFF'}")
        except Exception as ex:
            log.error("Error sending arp key hold", exception=ex)

    def _midi_send_arp_on_off(self, state: bool) -> None:
        """
        Send arpeggiator on/off command
        :param state: bool ON/OFF
        :return: None
        """
        try:
            if self.midi_helper:
                value = (
                    MidiConstant.VALUE_ON if state else MidiConstant.VALUE_OFF
                )  # 1 = ON, 0 = OFF
                log.message(f"Sent arpeggiator on/off: {'ON' if state else 'OFF'}")
                # send arp on to all zones
                for zone in [
                    AddressOffsetProgramLMB.CONTROLLER,
                    AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_1,
                    AddressOffsetProgramLMB.PART_DIGITAL_SYNTH_2,
                    AddressOffsetProgramLMB.PART_ANALOG,
                    AddressOffsetProgramLMB.ZONE_DRUM,
                ]:
                    address = RolandSysExAddress(
                        msb=AddressStartMSB.TEMPORARY_PROGRAM,
                        umb=AddressOffsetSystemUMB.COMMON,
                        lmb=zone,
                        lsb=MidiConstant.ZERO_BYTE,
                    )
                    sysex_message = self.sysex_composer.compose_message(
                        address=address,
                        param=AddressParameterProgramZone.ARPEGGIO_SWITCH,
                        value=value,
                    )
                    self.midi_helper.send_midi_message(sysex_message)
        except Exception as ex:
            log.error("Error sending arp on/off", exception=ex)

    def handle_piano_note_on(self, note_num: int) -> None:
        """
        Handle piano key press
        :param note_num: int note midi number
        :return: None
        """
        if self.midi_helper:
            # self.channel is 0-indexed, so add 1 to match MIDI channel in log file
            msg = [MidiConstant.NOTE_ON + self.channel, note_num, 100]
            self.midi_helper.send_raw_message(msg)
            log.message(f"Sent Note On: {note_num} on channel {self.channel + 1}")

    def handle_piano_note_off(self, note_num: int) -> None:
        """
        Handle piano key release
        :param note_num: int midi note number
        :return: None
        """
        if self.midi_helper:
            # Calculate the correct status byte for note_off:
            # 0x80 is the base for note_off messages. Subtract 1 if self.channel is 1-indexed.
            if not self.midi_key_hold_latched:
                status = MidiConstant.NOTE_OFF + self.channel
                msg = [status, note_num, 0]
                self.midi_helper.send_raw_message(msg)
                log.message(f"Sent Note Off: {note_num} on channel {self.channel + 1}")

    def _load_last_preset(self):
        """Load the last used preset from settings."""
        try:
            # Get last preset info from settings
            synth_type = self.settings.value(
                "last_preset/synth_type", JDXiSynth.DIGITAL_SYNTH_1
            )
            preset_number = int(
                self.settings.value("last_preset/preset_num", 0, type=int)
            )
            channel = int(self.settings.value("last_preset/channel", 0, type=int))

            # Define mappings for synth types
            synth_mappings = {
                JDXiSynth.ANALOG_SYNTH: (JDXiPresetToneList.ANALOG, 0, 7),
                JDXiSynth.DIGITAL_SYNTH_1: (
                    JDXiPresetToneList.DIGITAL_ENUMERATED,
                    1,
                    16,
                ),
                JDXiSynth.DIGITAL_SYNTH_2: (
                    JDXiPresetToneList.DIGITAL_ENUMERATED,
                    2,
                    16,
                ),
                JDXiSynth.DRUM_KIT: (JDXiPresetToneList.DRUM_ENUMERATED, 3, 16),
            }

            # Get preset list and MIDI parameters based on synth type
            presets, bank_msb, lsb_divisor = synth_mappings.get(synth_type, ([], 0, 1))
            bank_lsb = preset_number // lsb_divisor
            program = preset_number % lsb_divisor

            # Send MIDI messages to load preset
            if hasattr(self, "midi_helper") and self.midi_helper:
                self.midi_helper.send_bank_select(bank_msb, bank_lsb, channel)
                self.midi_helper.send_program_change(program, channel)

                # Update display and channel
                preset_name = presets[preset_number - 1]  # Adjust index to be 0-based
                self._update_display_preset(preset_number, preset_name, channel)

                log.message(f"Loaded last preset: {preset_name} on channel {channel}")

        except Exception as ex:
            log.error("Error loading last preset", exception=ex)

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
            log.message(
                f"Saved last preset: {synth_type} #{preset_num} on channel {channel}"
            )

        except Exception as ex:
            log.error("Error saving last preset", exception=ex)

    def _show_favorite_context_menu(
        self, pos, button: Union[FavoriteButton, SequencerSquare]
    ):
        """Show context menu for favorite button"""
        menu = QMenu()

        # Add save action if we have address current preset
        if hasattr(self, "current_preset_number"):
            save_action = menu.addAction("Save Current Preset")
            save_action.triggered.connect(lambda: self._save_to_favorite(button))

        # Add clear action if slot has address preset
        if button.preset:
            clear_action = menu.addAction("Clear Slot")
            clear_action.triggered.connect(lambda: self._clear_favorite(button))

        menu.exec_(button.mapToGlobal(pos))

    def _save_to_favorite(self, button: Union[FavoriteButton, SequencerSquare]) -> None:
        """
        Save current preset to favorite slot
        :param button: Union[FavoriteButton, SequencerSquare]
        :return: None
        """
        if hasattr(self, "current_preset_number"):
            # Get current preset info from settings
            synth_type = self.settings.value(
                "last_preset/synth_type", JDXiSynth.ANALOG_SYNTH
            )
            preset_num = self.settings.value("last_preset/preset_num", 0, type=int)
            channel = self.settings.value("last_preset/channel", 0, type=int)
            try:
                # Get the current preset name
                preset_name = self.preset_manager.get_preset_name_by_type_and_index(
                    self.current_synth_type, self.current_preset_index
                )

                # Save to button (which will also save to settings)
                button.save_preset_as_favourite(
                    synth_type, preset_num, preset_name, channel
                )

                # Update display to show the saved preset
                self._update_display_preset(
                    int(preset_num), str(preset_name), int(channel)
                )

            except Exception as ex:
                log.error("Error saving to favorite", ex)
                QMessageBox.warning(self, "Error", f"Error saving preset: {str(ex)}")

    def _clear_favorite(self, button: Union[FavoriteButton, SequencerSquare]) -> None:
        """
        Clear favorite slot
        :param button: FavoriteButton
        :return: None
        """
        button.clear_preset()

    def _load_saved_favorites(self):
        """Load saved favorites from settings"""
        for button in self.sequencer_buttons:
            synth_type = self.settings.value(
                f"favorites/slot{button.slot_number}/synth_type", ""
            )
            if synth_type:
                preset_num = self.settings.value(
                    f"favorites/slot{button.slot_number}/preset_num", 0, type=int
                )
                preset_name = self.settings.value(
                    f"favorites/slot{button.slot_number}/preset_name", ""
                )
                channel = self.settings.value(
                    f"favorites/slot{button.slot_number}/channel", 0, type=int
                )

                button.save_preset_as_favourite(
                    synth_type, preset_num, preset_name, channel
                )

    def _save_favorite(
        self, button: Union[FavoriteButton, SequencerSquare], index: int
    ) -> None:
        """
        Save the current preset as an address favorite and prevent toggling off
        :param button: button: Union[FavoriteButton, SequencerSquare]
        :param index: int
        :return: None
        """
        self.settings = QSettings("mabsoft", "jdxi_editor")
        preset_name = f"favorite_{index + 1:02d}"

        if button.isChecked():
            button_preset = self._generate_button_preset()
            if button_preset:
                button.preset = button_preset  # Store preset in button
                button.setToolTip(
                    f"Tone {button_preset.number} {button_preset.name}, {button_preset.type}"
                )
                button.setChecked(True)  # Keep it checked
                button.setCheckable(False)  # Prevent unchecking directly
                self.settings.setValue(preset_name, button_preset)  # Save preset
                log.message(f"Saved {button_preset} as {preset_name}")
        else:
            self.load_button_preset(button)  # Load stored preset if checked

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
                self.current_preset_number = int(
                    self.settings.value("preset_number", 1)
                )
                self.current_preset_name = self.settings.value(
                    "preset_name", "INIT PATCH"
                )

                # Try to open MIDI ports if they were saved
                if input_port and output_port:
                    self._midi_init_ports(input_port, output_port)

                log.message("JD-Xi Settings loaded successfully")

        except Exception as ex:
            log.error("Error loading settings", ex)

    def _save_settings(self):
        """Save application settings"""
        try:
            # Save MIDI port settings
            if hasattr(self, "settings"):
                self.settings.setValue("midi_in", self.midi_helper.in_port_name)
                self.settings.setValue("midi_out", self.midi_helper.out_port_name)

                # Save window geometry
                self.settings.setValue("geometry", self.saveGeometry())

                # Save current preset info
                self.settings.setValue("preset_number", self.current_preset_number)
                self.settings.setValue("preset_name", self.current_preset_name)

                log.message("Settings saved successfully")

        except Exception as ex:
            log.error("Error saving settings", exception=ex)
