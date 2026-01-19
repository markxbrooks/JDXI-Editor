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
from typing import Optional, Union

import qtawesome as qta
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QMouseEvent, QShortcut
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QProgressDialog

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import (
    AddressOffsetProgramLMB,
    AddressOffsetSystemUMB,
    AddressOffsetTemporaryToneUMB,
    AddressStartMSB,
    RolandSysExAddress,
)
from jdxi_editor.midi.data.control_change.sustain import ControlChangeSustain
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.program.zone import ProgramZoneParam
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.io.input_handler import add_or_replace_program_and_save
from jdxi_editor.midi.message.roland import JDXiSysEx
from jdxi_editor.midi.program.helper import JDXiProgramHelper
from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.project import __package_name__
from jdxi_editor.synth.type import JDXiSynth
from jdxi_editor.ui.dialogs.about import UiAboutDialog
from jdxi_editor.ui.dialogs.settings import UiPreferencesDialog
from jdxi_editor.ui.editors import (
    AnalogSynthEditor,
    ArpeggioEditor,
    DigitalSynthEditor,
    DrumCommonEditor,
    EffectsCommonEditor,
    ProgramEditor,
    SynthEditor,
    VocalFXEditor,
)
from jdxi_editor.ui.editors.config import EditorConfig
from jdxi_editor.ui.editors.digital.editor import (
    DigitalSynth2Editor,
    DigitalSynth3Editor,
)
from jdxi_editor.ui.editors.helpers.program import (
    calculate_midi_values,
    get_program_id_by_name,
)
from jdxi_editor.ui.editors.io.player import MidiFileEditor
from jdxi_editor.ui.editors.io.preset import PresetEditor
from jdxi_editor.ui.editors.main import MainEditor
from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor
from jdxi_editor.ui.preset.button import JDXiPresetButtonData
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.preset.tone.lists import JDXiPresetToneList
from jdxi_editor.ui.style.factory import generate_sequencer_button_style
from jdxi_editor.ui.widgets.button import SequencerSquare
from jdxi_editor.ui.widgets.button.favorite import FavoriteButton
from jdxi_editor.ui.widgets.viewer.log import LogViewer
from jdxi_editor.ui.windows.jdxi.recent_files import RecentFilesManager
from jdxi_editor.ui.windows.jdxi.ui import JDXiWindow
from jdxi_editor.ui.windows.jdxi.utils import show_message_box
from jdxi_editor.ui.windows.midi.config_dialog import MIDIConfigDialog
from jdxi_editor.ui.windows.midi.debugger import MIDIDebugger
from jdxi_editor.ui.windows.midi.monitor import MIDIMessageMonitor
from jdxi_editor.ui.windows.patch.manager import PatchManager
from jdxi_editor.utils.file import documentation_file_path, os_file_open
from picomidi.constant import Midi


class JDXiInstrument(JDXiWindow):
    """
    class JDXiInstrument
    """

    def __init__(self, splash=None, progress_bar=None, status_label=None):
        super().__init__()
        self.splash = splash
        self.splash_progress_bar = progress_bar
        self.splash_status_label = status_label
        if platform.system() == "Windows":
            JDXi.UI.ThemeManager.apply_transparent(self)
            JDXi.UI.ThemeManager.apply_adsr_disabled(self)
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
        self.settings = QSettings("mabsoft", __package_name__)
        self.recent_files_manager = RecentFilesManager()
        self.recent_files_menu = None
        # Add Recent Files menu now that recent_files_manager is initialized
        self._add_recent_files_menu()
        self._load_settings()
        self._toggle_illuminate_sequencer_lightshow(True)
        self._load_saved_favorites()
        self._update_synth_button_styles()
        self._set_callbacks()
        self._init_preset_helpers()
        self.editor_registry = {
            "vocal_fx": EditorConfig(
                title="Vocal Effects",
                editor_class=VocalFXEditor,
                synth_type=JDXiSynth.VOCAL_FX,
                midi_channel=MidiChannel.VOCAL_FX,
                icon="mdi.microphone",
            ),
            "digital1": EditorConfig(
                title="Digital Synth 1",
                editor_class=DigitalSynthEditor,
                synth_type=JDXiSynth.DIGITAL_SYNTH_1,
                midi_channel=MidiChannel.DIGITAL_SYNTH_1,
                kwargs={"synth_number": 1},
                icon="mdi.piano",
            ),
            "digital2": EditorConfig(
                title="Digital Synth 2",
                editor_class=DigitalSynth2Editor,
                synth_type=JDXiSynth.DIGITAL_SYNTH_2,
                midi_channel=MidiChannel.DIGITAL_SYNTH_2,
                kwargs={"synth_number": 2},
                icon="mdi.piano",
            ),
            "analog": EditorConfig(
                title="Analog Synth",
                editor_class=AnalogSynthEditor,
                synth_type=JDXiSynth.ANALOG_SYNTH,
                midi_channel=MidiChannel.ANALOG_SYNTH,
                icon="mdi.piano",
            ),
            "drums": EditorConfig(
                title="Drums",
                editor_class=DrumCommonEditor,
                synth_type=JDXiSynth.DRUM_KIT,
                midi_channel=MidiChannel.DRUM_KIT,
                icon="fa5s.drum",
            ),
            "arpeggio": EditorConfig(
                title="Arpeggiator",
                editor_class=ArpeggioEditor,
                icon="ph.music-notes-simple-bold",
            ),
            "effects": EditorConfig(
                title="Effects",
                editor_class=EffectsCommonEditor,
                icon="ri.sound-module-fill",
            ),
            "pattern": EditorConfig(
                title="Pattern",
                editor_class=PatternSequenceEditor,
                icon="mdi.view-sequential-outline",
            ),
            "preset": EditorConfig(
                title="Preset", editor_class=PresetEditor, icon="mdi6.soundbar"
            ),
            "program": EditorConfig(
                title="Program", editor_class=ProgramEditor, icon="ri.speaker-line"
            ),
            "midi_file": EditorConfig(
                title="MIDI File", editor_class=MidiFileEditor, icon="mdi.midi-port"
            ),
        }

        self.show()
        self.main_editor = None
        self.data_request()
        self._show_main_editor()
        self.init_main_editor()
        # Initialize the current preset and synth type
        self.current_synth_type = JDXiSynth.DIGITAL_SYNTH_1
        self.channel = MidiChannel.DIGITAL_SYNTH_1

    def _init_preset_helpers(self):
        """Initialize preset helpers dynamically"""
        preset_configs = [
            (
                JDXiSynth.DIGITAL_SYNTH_1,
                JDXiPresetToneList.Digital.ENUMERATED,
                MidiChannel.DIGITAL_SYNTH_1,
            ),
            (
                JDXiSynth.DIGITAL_SYNTH_2,
                JDXiPresetToneList.Digital.ENUMERATED,
                MidiChannel.DIGITAL_SYNTH_2,
            ),
            (
                JDXiSynth.ANALOG_SYNTH,
                JDXiPresetToneList.Analog.ENUMERATED,
                MidiChannel.ANALOG_SYNTH,
            ),
            (
                JDXiSynth.DRUM_KIT,
                JDXiPresetToneList.Drum.ENUMERATED,
                MidiChannel.DRUM_KIT,
            ),
        ]

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
            lambda tone_name, synth_type: self.set_tone_name_by_type(
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

    def mouseMoveEvent(self, event: QMouseEvent):
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

    def register_editor(self, editor: SynthEditor) -> None:
        """
        register editor

        :param editor: SynthEditor
        :return: None
        """
        self.editors.append(editor)
        log.message(f"Editor {str(editor)} registered")
        for i, registered_editor in enumerate(self.editors):
            log.message(f"Registered Editor {i} {str(registered_editor)}")

    def set_tone_name_by_type(self, tone_name: str, synth_type: str) -> None:
        """
        set tone name by type

        :param tone_name: str Tone name
        :param synth_type: str Synth type
        :return: None
        """
        if synth_type == JDXiSynth.PROGRAM:
            pass
        self.preset_manager.set_preset_name_by_type(synth_type, tone_name)
        self._update_display()

    def get_preset_helper_for_current_synth(self) -> JDXiPresetHelper:
        """
        Return the appropriate preset helper based on the current synth preset_type

        :return: JDXiPresetHelper
        """
        helper = self.preset_helpers.get(self.current_synth_type)
        if helper is None:
            log.warning(
                f"Unknown synth preset_type: {self.current_synth_type}, defaulting to digital_1"
            )
            return self.preset_helpers[JDXiSynth.DIGITAL_SYNTH_1]  # Safe fallback
        return helper

    def set_current_program_name(self, program_name: str) -> None:
        """
        program name

        :param program_name: str
        :return: None
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

        :param channel: int midi channel (discarded)
        :param program_number: int Program number
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
        self.channel = JDXiSynth.midi_channel_number(synth_type)
        self._update_synth_button_styles()
        self.preset_helper = self.get_preset_helper_for_current_synth()
        self.preset_helper.preset_changed.connect(self.midi_helper.send_program_change)

    def _update_synth_button_styles(self):
        """Update styles for synth buttons based on selection."""
        for synth_type, button in self.synth_buttons.items():
            is_selected = synth_type == self.current_synth_type
            button.setStyleSheet(
                JDXi.UI.Style.BUTTON_ROUND_SELECTED
                if not is_selected
                else JDXi.UI.Style.BUTTON_ROUND
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

        if not presets:
            show_message_box("No presets", "No presets available for this synth type.")
            return
        log.parameter(f"Presets for current synth: {self.current_synth_type}", presets)
        max_index = len(presets) - 1
        new_preset_index = self.current_preset_index + index_change

        if new_preset_index < 0:
            show_message_box("First preset", "Already at the first preset.")
            return
        if new_preset_index > max_index:
            show_message_box("Last preset", "Already at the last preset.")
            return

        self.current_preset_index = new_preset_index
        preset_helper = self.get_preset_helper_for_current_synth()
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
        # Convert channel integer to MidiChannel enum if needed
        if isinstance(channel, int):
            try:
                channel_enum = MidiChannel(channel)
            except (ValueError, TypeError):
                log.warning(
                    f"Invalid channel value: {channel}, using synth_type instead"
                )
                channel_enum = None
        else:
            channel_enum = channel

        # Try to get presets by channel first, then fall back to synth_type
        presets = None
        if channel_enum is not None:
            presets = self.preset_manager.get_presets_for_channel(channel_enum)

        # Ensure presets is a list (it should be, but handle edge cases)
        if not isinstance(presets, list):
            # Try to get presets by synth_type instead
            presets = self.preset_manager.get_presets_for_synth(synth_type)
            if not isinstance(presets, list):
                log.error(
                    f"Both get_presets_for_channel and get_presets_for_synth returned non-list. "
                    f"channel_enum: {channel_enum}, synth_type: {synth_type}, presets type: {type(presets)}"
                )
                return
        # Ensure preset_index is within bounds
        if preset_index < 0 or preset_index >= len(presets):
            log.error(
                f"Preset index {preset_index} out of range for presets list (length: {len(presets)})"
            )
            return
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

    def init_main_editor(self) -> None:
        """
        Initialize the UI for the MainEditor

        :return:
        """
        self.main_editor.hide()
        self.main_editor.setUpdatesEnabled(False)
        self.main_editor.blockSignals(True)
        self.show_editor("program")
        self.show_editor("digital1")
        self.show_editor("digital2")
        self.show_editor("analog")
        self.show_editor("drums")
        self.show_editor("arpeggio")
        self.show_editor("effects")
        self.show_editor("vocal_fx")
        self.show_editor("pattern")
        self.show_editor("midi_file")
        self.main_editor.editor_tab_widget.setCurrentIndex(0)
        self.main_editor.blockSignals(False)
        self.main_editor.setUpdatesEnabled(True)
        self.main_editor.show()

    def show_editor(self, editor_type: str, **kwargs) -> None:
        """
        Show editor of given type

        :param editor_type: str Editor type
        """
        config = self.editor_registry.get(editor_type)
        if not config:
            logging.warning(f"Unknown editor type: {editor_type}")
            return

        if config.synth_type:
            self.current_synth_type = config.synth_type
        if config.midi_channel:
            self.channel = config.midi_channel

        # Merge registry kwargs with call-site kwargs
        merged_kwargs = {**config.kwargs, **kwargs}

        self._show_editor_tab(
            config.title, config.editor_class, config.icon, **merged_kwargs
        )

    def on_documentation(self):
        """
        on_documentation

        :return: None
        """
        html_file = documentation_file_path("index.html")
        try:
            os_file_open(html_file)
        except Exception as ex:
            log.exception(f"Error {ex} occurred opening documentation")

    def on_preferences(self):
        """
        on_preferences
        :return:
        """
        preferences_dialog = UiPreferencesDialog(self)
        preferences_dialog.ui_setup(preferences_dialog)
        preferences_dialog.setAttribute(Qt.WA_DeleteOnClose)
        preferences_dialog.exec()

    def get_existing_editor(self, editor_class) -> Optional[SynthEditor]:
        """
        Get existing editor instance of the specified class

        :param editor_class: class
        :return: Optional[SynthEditor]
        """
        instance_attr = f"{editor_class.__name__.lower()}_instance"
        existing_editor = getattr(self, instance_attr, None)
        log.parameter("existing_editor", existing_editor)
        return existing_editor

    def _show_editor_tab(self, title: str, editor_class, icon, **kwargs) -> None:
        """
        _show_editor_tab

        :param title: str Title of the tab
        :param editor_class: cls Class of the Editor
        :param kwargs:
        :return: None
        """
        try:
            instance_attr = f"{editor_class.__name__.lower()}_instance"
            existing_editor = getattr(self, instance_attr, None)

            if existing_editor:
                index = self.main_editor.editor_tab_widget.indexOf(existing_editor)
                if index != -1:
                    self.main_editor.editor_tab_widget.setCurrentIndex(index)
                    # Update tab bar property for styling
                    self._update_tab_bar_property(index)
                    return

            preset_helper = (
                self.get_preset_helper_for_current_synth()
                if editor_class
                in {
                    ArpeggioEditor,
                    DigitalSynthEditor,
                    DigitalSynth2Editor,
                    DigitalSynth3Editor,
                    AnalogSynthEditor,
                    DrumCommonEditor,
                    PatternSequenceEditor,
                    ProgramEditor,
                    PresetEditor,
                    MidiFileEditor,
                    VocalFXEditor,
                    EffectsCommonEditor,
                }
                else None
            )

            # Connect Pattern Sequencer to MidiFileEditor if both exist
            if editor_class == PatternSequenceEditor:
                midi_file_editor = self.get_existing_editor(MidiFileEditor)
                if midi_file_editor:
                    kwargs["midi_file_editor"] = midi_file_editor
            elif editor_class == MidiFileEditor:
                # After creating MidiFileEditor, connect it to Pattern Sequencer
                def connect_pattern_sequencer():
                    pattern_editor = self.get_existing_editor(PatternSequenceEditor)
                    if pattern_editor and hasattr(
                        pattern_editor, "set_midi_file_editor"
                    ):
                        pattern_editor.set_midi_file_editor(existing_editor)

                # Use QTimer to connect after editor is fully created
                from PySide6.QtCore import QTimer

                QTimer.singleShot(100, connect_pattern_sequencer)

            # Update splash screen when creating editors
            if self.splash_status_label and self.splash_progress_bar:
                if title == "Analog Synth":
                    self.splash_status_label.setText("Loading Analog Synth editor...")
                    self.splash_progress_bar.setValue(30)
                elif title == "Digital Synth 1":
                    self.splash_status_label.setText(
                        "Loading Digital Synth 1 editor..."
                    )
                    self.splash_progress_bar.setValue(40)
                elif title == "Digital Synth 2":
                    self.splash_status_label.setText(
                        "Loading Digital Synth 2 editor..."
                    )
                    self.splash_progress_bar.setValue(50)
                elif title == "Drums":
                    self.splash_status_label.setText("Preparing Drum Kit editor...")
                    self.splash_progress_bar.setValue(55)
                QApplication.processEvents()

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

            tab_index = self.main_editor.editor_tab_widget.addTab(
                editor, qta.icon(icon, color=JDXi.UI.Style.GREY), title
            )

            # Store the tab index for Analog Synth to enable styling
            if title == "Analog Synth":
                tab_bar = self.main_editor.editor_tab_widget.tabBar()
                tab_bar.setTabData(tab_index, "analog")

            self.main_editor.editor_tab_widget.setCurrentWidget(editor)

            # Connect to tab change signal to update QTabBar property for styling
            if not hasattr(self, "_tab_change_connected"):
                self.main_editor.editor_tab_widget.currentChanged.connect(
                    self._update_tab_bar_property
                )
                self._tab_change_connected = True
            self._update_tab_bar_property(
                self.main_editor.editor_tab_widget.currentIndex()
            )

            setattr(self, instance_attr, editor)
            self.register_editor(editor)

            # Connect Pattern Sequencer to MidiFileEditor after creation
            if editor_class == MidiFileEditor:
                # Connect to Pattern Sequencer if it exists
                pattern_editor = self.get_existing_editor(PatternSequenceEditor)
                if pattern_editor and hasattr(pattern_editor, "set_midi_file_editor"):
                    pattern_editor.set_midi_file_editor(editor)
            elif editor_class == PatternSequenceEditor:
                # Connect to MidiFileEditor if it exists
                midi_file_editor = self.get_existing_editor(MidiFileEditor)
                if midi_file_editor:
                    editor.set_midi_file_editor(midi_file_editor)

            if hasattr(editor, "preset_helper"):
                editor.preset_helper.update_display.connect(
                    self.update_display_callback
                )

            if hasattr(editor, "partial_editors"):
                for partial in editor.partial_editors.values():
                    self.register_editor(partial)

        except Exception as ex:
            import traceback

            log.error(f"Error showing {title} editor: {ex}", exception=ex)
            log.error(f"Traceback: {traceback.format_exc()}")

    def _update_tab_bar_property(self, index: int) -> None:
        """
        Update QTabBar property based on current tab selection for styling.

        :param index: int Current tab index
        """
        if index < 0:
            return
        tab_bar = self.main_editor.editor_tab_widget.tabBar()
        tab_data = tab_bar.tabData(index)
        # Set property on QTabBar to enable property-based styling
        if tab_data == "analog":
            tab_bar.setProperty("analogTabSelected", True)
        else:
            tab_bar.setProperty("analogTabSelected", False)
        # Force style update
        tab_bar.style().unpolish(tab_bar)
        tab_bar.style().polish(tab_bar)

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
                self.get_preset_helper_for_current_synth()
                if editor_class
                in [
                    ArpeggioEditor,
                    DigitalSynthEditor,
                    DigitalSynth2Editor,
                    AnalogSynthEditor,
                    DrumCommonEditor,
                    PatternSequenceEditor,
                    ProgramEditor,
                    PresetEditor,
                    MidiFileEditor,
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
            self.register_editor(editor)
            if hasattr(editor, "preset_helper"):
                editor.preset_helper.update_display.connect(
                    self.update_display_callback
                )
            if hasattr(editor, "partial_editors"):
                for i, partial_item in enumerate(editor.partial_editors.values()):
                    self.register_editor(partial_item)

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

    def _show_main_editor(self) -> None:
        """
        _show_about_help

        :return:
        """
        if not self.main_editor:
            self.main_editor = MainEditor(self)
        self.main_editor.show()
        self.main_editor.raise_()

    def _create_menu_bar(self) -> None:
        """Override to add Recent Files submenu."""
        super()._create_menu_bar()
        # Note: Recent Files menu is added later in _add_recent_files_menu()
        # because recent_files_manager is initialized after super().__init__()

    def _add_recent_files_menu(self) -> None:
        """Add Recent Files submenu to File menu."""
        if (
            not hasattr(self, "recent_files_manager")
            or self.recent_files_manager is None
        ):
            return

        # Get the File menu by finding the action
        file_menu = None
        for action in self.menuBar().actions():
            if action.text() == "File":
                file_menu = action.menu()
                break

        if file_menu:
            # Find the position after "Load MIDI file" and "Save MIDI file"
            actions = file_menu.actions()
            insert_pos = 2  # After "Load MIDI file" and "Save MIDI file"

            # Add separator before Recent Files
            file_menu.insertSeparator(
                actions[insert_pos] if insert_pos < len(actions) else None
            )

            # Create Recent Files submenu
            self.recent_files_menu = file_menu.addMenu("Recent MIDI Files")
            self._update_recent_files_menu()

    def _update_recent_files_menu(self) -> None:
        """Update the Recent Files menu with current recent files."""
        if not self.recent_files_menu:
            return

        if (
            not hasattr(self, "recent_files_manager")
            or self.recent_files_manager is None
        ):
            return

        # Check if the menu object is still valid (not deleted)
        try:
            # Try to access a property to verify the C++ object still exists
            _ = self.recent_files_menu.title()
        except RuntimeError:
            # Menu was deleted, reset reference and return
            self.recent_files_menu = None
            return

        # Clear existing actions
        try:
            self.recent_files_menu.clear()
        except RuntimeError:
            # Menu was deleted during operation, reset reference and return
            self.recent_files_menu = None
            return

        recent_files = self.recent_files_manager.get_recent_files()

        if not recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_files_menu.addAction(action)
        else:
            for file_path in recent_files:
                # Create display name (just filename)
                from pathlib import Path

                display_name = Path(file_path).name
                action = QAction(display_name, self)
                action.setData(file_path)  # Store full path
                action.triggered.connect(
                    lambda checked, path=file_path: self._load_recent_file(path)
                )
                self.recent_files_menu.addAction(action)

            # Add separator and clear action
            self.recent_files_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_files_menu.addAction(clear_action)

    def _load_recent_file(self, file_path: str) -> None:
        """
        Load a recent MIDI file.

        :param file_path: Path to the MIDI file
        """
        from pathlib import Path

        if not Path(file_path).exists():
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "File Not Found", f"The file '{file_path}' no longer exists."
            )
            self._update_recent_files_menu()
            return

        # Get or create MIDI file editor
        self.midi_file_editor = self.get_existing_editor(MidiFileEditor)
        if not self.midi_file_editor:
            self.show_editor("midi_file")

        # Load the file directly
        self.midi_file_editor.midi_load_file_from_path(file_path)
        self.show_editor("midi_file")

    def _clear_recent_files(self) -> None:
        """Clear all recent files."""
        self.recent_files_manager.clear_recent_files()
        self._update_recent_files_menu()

    def _midi_file_load(self):
        """
        _midi_file_load

        :return: None
        Load a MIDI file and process it
        1. Load the current MIDI file using the MidiFileEditor.
        2. If the editor does not exist, create and show it.
        3. After saving, show the editor again.
        """
        self.midi_file_editor = self.get_existing_editor(MidiFileEditor)
        if not self.midi_file_editor:
            self.show_editor("midi_file")
        # Set parent so midi_load_file can access recent_files_manager
        if self.midi_file_editor:
            self.midi_file_editor.parent = self
        self.midi_file_editor.midi_load_file()
        self.show_editor("midi_file")

    def _midi_file_save(self):
        """
        _midi_file_save
        :return:
        1. Save the current MIDI file using the MidiFileEditor.
        2. If the editor does not exist, create and show it.
        3. After saving, show the editor again.
        """
        self.midi_file_editor = self.get_existing_editor(MidiFileEditor)
        if not self.midi_file_editor:
            self.show_editor("midi_file")
        self.midi_file_editor.midi_save_file()
        self.show_editor("midi_file")

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

    def _dump_settings_to_synth(self) -> None:
        """
        Dump all current settings from all editors to the synthesizer.
        This sends all parameters from all active editors to the JD-Xi.
        """
        try:
            if not self.midi_helper:
                log.warning("MIDI helper not initialized. Cannot dump settings.")
                return

            if (
                not self.midi_helper.midi_out
                or not self.midi_helper.midi_out.is_port_open()
            ):
                log.warning("MIDI output port is not open. Cannot dump settings.")
                return

            log.message("Starting to dump all settings to synthesizer...")

            from jdxi_editor.midi.sysex.json_composer import JDXiJSONComposer

            json_composer = JDXiJSONComposer()

            total_sent = 0
            total_skipped = 0

            # Iterate through all registered editors
            for editor in self.editors:
                # Skip editors that don't have the required attributes
                if not hasattr(editor, "address") or not hasattr(
                    editor, "get_controls_as_dict"
                ):
                    continue

                # Skip certain editor types
                from jdxi_editor.ui.editors import ProgramEditor
                from jdxi_editor.ui.editors.io.player import MidiFileEditor
                from jdxi_editor.ui.editors.pattern.pattern import PatternSequenceEditor

                if isinstance(
                    editor, (PatternSequenceEditor, ProgramEditor, MidiFileEditor)
                ):
                    continue

                try:
                    # Compose JSON from current editor state
                    editor_json = json_composer.compose_message(editor)
                    if editor_json:
                        # Convert to JSON string and send to instrument
                        import json

                        json_string = json.dumps(editor_json)
                        self.midi_helper.send_json_patch_to_instrument(json_string)

                        # Count parameters sent
                        metadata_fields = {
                            "JD_XI_HEADER",
                            "ADDRESS",
                            "TEMPORARY_AREA",
                            "SYNTH_TONE",
                        }
                        param_count = len(
                            [k for k in editor_json.keys() if k not in metadata_fields]
                        )
                        total_sent += param_count
                        log.message(
                            f"Sent {param_count} parameters from {editor.__class__.__name__}"
                        )
                except Exception as ex:
                    log.error(
                        f"Error dumping settings from {editor.__class__.__name__}: {ex}"
                    )
                    total_skipped += 1

            log.message(
                f"Settings dump complete: {total_sent} parameters sent to synthesizer"
            )

        except Exception as ex:
            log.error(f"Error dumping settings to synth: {ex}")

    def _update_user_program_database(self) -> None:
        """
        Update the User Program database by scanning through all user banks (E, F, G, H)
        and reading program names from the synthesizer.

        This method:
        1. Iterates through each user bank (E, F, G, H)
        2. For each bank, iterates through programs 1-64
        3. Selects each program on the synthesizer
        4. Waits for program name and tone data to be received
        5. Saves the program to the database
        6. Shows progress to the user
        """
        if not self.midi_helper or not self.midi_helper.is_output_open:
            QMessageBox.warning(
                self,
                "MIDI Not Connected",
                "Please connect to the JD-Xi synthesizer before updating the database.",
            )
            return

        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Update User Program Database",
            "This will scan through all user banks (E, F, G, H) and update the program database.\n"
            "This may take several minutes. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # User banks to scan
        user_banks = ["E", "F", "G", "H"]
        programs_per_bank = 64
        total_programs = len(user_banks) * programs_per_bank

        # Create progress dialog
        progress = QProgressDialog(
            "Updating User Program Database...", "Cancel", 0, total_programs, self
        )
        progress.setWindowTitle("Updating Database")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # Initialize state
        self._db_update_banks = user_banks.copy()
        self._db_update_current_bank_index = 0
        self._db_update_current_program = 1
        self._db_update_progress = progress
        self._db_update_programs_saved = 0
        self._db_update_waiting_for_data = False
        self._db_update_timeout_count = 0
        self._db_update_program_name_received = False
        self._db_update_tone_names_received = set()

        # Disable auto-add during database update to prevent premature saves
        self._db_update_auto_add_enabled = True
        if hasattr(self.midi_helper, "_auto_add_enabled"):
            self._db_update_auto_add_enabled = getattr(
                self.midi_helper, "_auto_add_enabled", True
            )
        # Temporarily disable auto-add
        self.midi_helper._auto_add_enabled = False

        # Connect to MIDI input handler to detect when program data is received
        # MidiIOHelper inherits from MidiInHandler, so we can connect directly
        try:
            self.midi_helper.update_program_name.disconnect()
        except:
            pass
        # Connect to program name updates
        self.midi_helper.update_program_name.connect(self._on_program_name_received)

        # Also connect to tone name updates to track when all data is received
        try:
            self.midi_helper.update_tone_name.disconnect()
        except:
            pass
        self.midi_helper.update_tone_name.connect(self._on_tone_name_received)

        # Start the update process
        self._process_next_program()

    def _process_next_program(self) -> None:
        """Process the next program in the update sequence."""
        if self._db_update_progress.wasCanceled():
            self._cleanup_db_update()
            return

        # Check if we've completed all banks
        if self._db_update_current_bank_index >= len(self._db_update_banks):
            self._cleanup_db_update()

            # Reload programs from database to refresh the UI
            from jdxi_editor.ui.programs.programs import JDXiUIProgramList

            JDXiUIProgramList.USER_PROGRAMS = JDXiUIProgramList._load_user_programs()

            # Refresh program editor if it's open
            if hasattr(self, "editors"):
                for editor in self.editors:
                    if hasattr(editor, "populate_programs"):
                        editor.populate_programs()
                    # Also refresh User Programs table if it exists
                    if hasattr(editor, "_populate_user_programs_table"):
                        editor._populate_user_programs_table()

            QMessageBox.information(
                self,
                "Update Complete",
                f"Successfully updated {self._db_update_programs_saved} programs in the database.\n\n"
                f"The program list has been refreshed with the updated names.",
            )
            return

        current_bank = self._db_update_banks[self._db_update_current_bank_index]

        # Check if we've completed all programs in current bank
        if self._db_update_current_program > 64:
            self._db_update_current_bank_index += 1
            self._db_update_current_program = 1
            self._process_next_program()
            return

        # Update progress
        current_progress = (
            self._db_update_current_bank_index * 64
            + self._db_update_current_program
            - 1
        )
        self._db_update_progress.setValue(current_progress)
        self._db_update_progress.setLabelText(
            f"Reading {current_bank}{self._db_update_current_program:02d}..."
        )

        # Calculate MIDI values for this program
        try:
            result = calculate_midi_values(
                current_bank, self._db_update_current_program
            )
            if result is None:
                log.error(
                    f"Failed to calculate MIDI values for {current_bank}{self._db_update_current_program:02d}"
                )
                self._move_to_next_program()
                return
            msb, lsb, pc = result
        except (ValueError, TypeError) as e:
            log.error(
                f"Error calculating MIDI values for {current_bank}{self._db_update_current_program:02d}: {e}"
            )
            self._move_to_next_program()
            return

        # Clear incoming preset data before selecting program
        self.midi_helper._incoming_preset_data.clear()
        self.midi_helper._incoming_preset_data.msb = msb
        self.midi_helper._incoming_preset_data.lsb = lsb
        # Store the program number (1-based) that we're requesting
        # For user banks: E=1-64, F=65-128, G=1-64, H=65-128 (1-based PC values)
        if current_bank == "E":
            program_num_1based = self._db_update_current_program  # 1-64
        elif current_bank == "F":
            program_num_1based = self._db_update_current_program + 64  # 65-128
        elif current_bank == "G":
            program_num_1based = self._db_update_current_program  # 1-64
        elif current_bank == "H":
            program_num_1based = self._db_update_current_program + 64  # 65-128
        else:
            program_num_1based = self._db_update_current_program
        self.midi_helper._incoming_preset_data.program_number = program_num_1based
        log.message(
            f"🔍 Requesting program {current_bank}{self._db_update_current_program:02d} (PC={program_num_1based})"
        )

        # Reset tracking flags
        self._db_update_program_name_received = False
        self._db_update_tone_names_received = set()

        # Select the program on the synthesizer
        log.message(
            f"🎹 Selecting program {current_bank}{self._db_update_current_program:02d} (MSB={msb}, LSB={lsb}, PC={pc})"
        )
        self.midi_helper.send_bank_select_and_program_change(
            MidiChannel.PROGRAM, msb, lsb, pc
        )

        # Wait longer for program to load on synthesizer before requesting data
        # Set flag to wait for data
        self._db_update_waiting_for_data = True
        self._db_update_timeout_count = 0

        # Request data from synthesizer after a delay to allow program to load
        QTimer.singleShot(1000, self._request_program_data)

        # Set timeout timer (8 seconds max wait per program - increased for reliability)
        QTimer.singleShot(8000, self._handle_program_data_timeout)

    def _request_program_data(self) -> None:
        """Request program data from the synthesizer."""
        if hasattr(self, "program_helper"):
            self.program_helper.data_request()

    def _on_program_name_received(self, program_name: str) -> None:
        """Handle when program name is received from the synthesizer."""
        if not self._db_update_waiting_for_data:
            return

        self._db_update_program_name_received = True
        log.message(f"📝 Program name received: {program_name}")

        # Check if we have all required data, then save
        self._check_and_save_program()

    def _on_tone_name_received(self, area: str, tone_name: str) -> None:
        """Handle when tone name is received from the synthesizer."""
        if not self._db_update_waiting_for_data:
            return

        # Track which tone names we've received
        if area in ["digital_1", "digital_2", "analog", "drum"]:
            self._db_update_tone_names_received.add(area)
            log.message(f"🎵 Tone name received: {area} = {tone_name}")

        # Check if we have all required data, then save
        self._check_and_save_program()

    def _check_and_save_program(self) -> None:
        """Check if we have all required data and save if ready."""
        if not self._db_update_waiting_for_data:
            return

        # We need program name - that's the most important
        if not self._db_update_program_name_received:
            return

        # Check if we already started a save timer
        if hasattr(self, "_db_update_save_timer_started"):
            return

        # Wait a bit to collect tone names, but don't wait forever
        required_tones = {"digital_1", "digital_2", "analog", "drum"}
        has_all_tones = required_tones.issubset(self._db_update_tone_names_received)

        if has_all_tones:
            # We have everything, save immediately after a short delay
            self._db_update_save_timer_started = True
            QTimer.singleShot(500, self._save_current_program)
        else:
            # Wait a bit more for remaining tone names (max 2.5 seconds after program name)
            self._db_update_save_timer_started = True
            QTimer.singleShot(2500, self._save_current_program)

    def _save_current_program(self) -> None:
        """Save the current program data to the database."""
        if not self._db_update_waiting_for_data:
            return

        try:
            current_bank = self._db_update_banks[self._db_update_current_bank_index]
            data = self.midi_helper._incoming_preset_data

            # Create program ID
            program_id = f"{current_bank}{self._db_update_current_program:02d}"

            # Use placeholder name if no program name received
            if not data.program_name:
                log.warning(
                    f"No program name received for {program_id}, using placeholder name"
                )
                data.program_name = f"User bank {current_bank} program {self._db_update_current_program:02d}"

            # Use the program number from data if available, otherwise calculate it
            # The program_number in data should be 1-based (1-128)
            if data.program_number is not None:
                program_number = data.program_number
            else:
                # Calculate based on bank and program index
                if current_bank == "E":
                    program_number = self._db_update_current_program  # 1-64
                elif current_bank == "F":
                    program_number = self._db_update_current_program + 64  # 65-128
                elif current_bank == "G":
                    program_number = self._db_update_current_program  # 1-64
                elif current_bank == "H":
                    program_number = self._db_update_current_program + 64  # 65-128
                else:
                    program_number = self._db_update_current_program

            log.message(
                f"💾 Saving program {program_id}: name='{data.program_name}', PC={program_number}"
            )

            # Check if program already exists in database
            from jdxi_editor.ui.editors.helpers.program import get_program_by_id

            existing_program = get_program_by_id(program_id)

            # Determine genre: preserve existing genre if program data is unchanged
            genre = "Unknown"
            if existing_program:
                # Compare all fields except genre to see if program data has changed
                new_msb = data.msb if data.msb is not None else 85
                new_lsb = (
                    data.lsb
                    if data.lsb is not None
                    else (0 if current_bank in ["E", "F"] else 1)
                )
                new_digital_1 = data.tone_names.get("digital_1")
                new_digital_2 = data.tone_names.get("digital_2")
                new_analog = data.tone_names.get("analog")
                new_drums = data.tone_names.get("drum")

                # Check if all program data matches (excluding genre)
                data_matches = (
                    existing_program.name == data.program_name
                    and existing_program.pc == program_number
                    and existing_program.msb == new_msb
                    and existing_program.lsb == new_lsb
                    and existing_program.digital_1 == new_digital_1
                    and existing_program.digital_2 == new_digital_2
                    and existing_program.analog == new_analog
                    and existing_program.drums == new_drums
                )

                if data_matches:
                    # Program data is unchanged, preserve existing genre
                    genre = (
                        existing_program.genre if existing_program.genre else "Unknown"
                    )
                    log.message(
                        f"📋 Program {program_id} data unchanged, preserving genre: '{genre}'"
                    )
                else:
                    # Program data has changed, use "Unknown" (user can edit genre manually)
                    log.message(
                        f"🔄 Program {program_id} data changed, resetting genre to 'Unknown'"
                    )

            # Create JDXiProgram object
            program = JDXiProgram(
                id=program_id,
                name=data.program_name,
                genre=genre,
                pc=program_number,
                msb=data.msb if data.msb is not None else JDXi.Midi.CC.BANK_SELECT.MSB,
                lsb=(
                    data.lsb
                    if data.lsb is not None
                    else (0 if current_bank in ["E", "F"] else 1)
                ),
                digital_1=data.tone_names.get("digital_1"),
                digital_2=data.tone_names.get("digital_2"),
                analog=data.tone_names.get("analog"),
                drums=data.tone_names.get("drum"),
            )

            # Save the program
            if add_or_replace_program_and_save(program):
                self._db_update_programs_saved += 1
                log.message(
                    f"✅ Saved program {program_id}: {program.name} (genre: '{genre}')"
                )
            else:
                log.warning(f"⚠️ Failed to save program {program_id}")

        except Exception as ex:
            log.error(f"Error saving program: {ex}")

        # Move to next program
        self._move_to_next_program()

    def _handle_program_data_timeout(self) -> None:
        """Handle timeout when waiting for program data."""
        if self._db_update_waiting_for_data:
            log.warning(
                f"Timeout waiting for program data: "
                f"{self._db_update_banks[self._db_update_current_bank_index]}"
                f"{self._db_update_current_program:02d}"
            )
            self._move_to_next_program()

    def _move_to_next_program(self) -> None:
        """Move to the next program in the sequence."""
        self._db_update_waiting_for_data = False
        self._db_update_program_name_received = False
        self._db_update_tone_names_received = set()
        if hasattr(self, "_db_update_save_timer_started"):
            delattr(self, "_db_update_save_timer_started")
        self._db_update_current_program += 1

        # Process next program after a short delay
        QTimer.singleShot(500, self._process_next_program)

    def _cleanup_db_update(self) -> None:
        """Clean up after database update is complete."""
        self._db_update_waiting_for_data = False
        self._db_update_program_name_received = False
        self._db_update_tone_names_received = set()

        # Re-enable auto-add if it was enabled before
        if hasattr(self, "_db_update_auto_add_enabled"):
            self.midi_helper._auto_add_enabled = self._db_update_auto_add_enabled

        # Disconnect signals
        try:
            self.midi_helper.update_program_name.disconnect(
                self._on_program_name_received
            )
        except:
            pass
        try:
            self.midi_helper.update_tone_name.disconnect(self._on_tone_name_received)
        except:
            pass

        if hasattr(self, "_db_update_progress"):
            self._db_update_progress.close()

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
        preset_helper = self.get_preset_helper_for_current_synth()
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
                return JDXiPresetToneList.Analog.ENUMERATED[
                    preset_number - 1
                ]  # Convert 1-based to 0-based
            if synth_type == JDXiSynth.DIGITAL_SYNTH_1:
                return JDXiPresetToneList.Digital.ENUMERATED[preset_number - 1]
            if synth_type == JDXiSynth.DIGITAL_SYNTH_2:
                return JDXiPresetToneList.Digital.ENUMERATED[preset_number - 1]
            else:
                return JDXiPresetToneList.Drum.ENUMERATED[preset_number - 1]
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
            f"Updated octave to: {self.current_octave} (value: {hex(JDXi.Midi.SYSEX.OCTAVE.CENTER_VALUE + self.current_octave)})"
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
            from jdxi_editor.midi.io.helper import MidiIOHelper

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
                lsb=DigitalCommonParam.OCTAVE_SHIFT.lsb,
            )
            sysex_message = JDXiSysEx(
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
                    sysex_message = JDXiSysEx(
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
                        cc, cc_value, MidiChannel.DIGITAL_SYNTH_1
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
                value = Midi.VALUE.ON if state else Midi.VALUE.OFF  # 1 = ON, 0 = OFF
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
                        lsb=Midi.VALUE.ZERO,
                    )
                    sysex_message = self.sysex_composer.compose_message(
                        address=address,
                        param=ProgramZoneParam.ARPEGGIO_SWITCH,
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
            msg = [Midi.NOTE.ON + self.channel, note_num, 100]
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
                status = Midi.NOTE.OFF + self.channel
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
                JDXiSynth.ANALOG_SYNTH: (JDXiPresetToneList.Analog.ENUMERATED, 0, 7),
                JDXiSynth.DIGITAL_SYNTH_1: (
                    JDXiPresetToneList.Digital.ENUMERATED,
                    1,
                    16,
                ),
                JDXiSynth.DIGITAL_SYNTH_2: (
                    JDXiPresetToneList.Digital.ENUMERATED,
                    2,
                    16,
                ),
                JDXiSynth.DRUM_KIT: (JDXiPresetToneList.Drum.ENUMERATED, 3, 16),
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
        self.settings = QSettings("mabsoft", __package_name__)
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
