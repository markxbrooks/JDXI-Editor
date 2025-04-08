"""
Digital Synth Editor for the Roland JD-Xi.

This module provides the UI components for editing digital synth parameters on the Roland JD-Xi.
The editor supports three partials (voices) with individual parameter control and common parameters
that affect all partials.

Classes:
    DigitalSynthEditor: Main editor class for digital synth parameters
        - Handles MIDI communication for parameter changes
        - Manages UI state for all digital synth controls
        - Provides preset loading and management
        - Supports real-time parameter updates via SysEx

Features:
    - Three independent partial editors
    - Common parameter controls (portamento, unison, legato, etc.)
    - Preset management and loading
    - Real-time MIDI parameter updates
    - ADSR envelope controls for both amplitude and filter
    - Oscillator waveform selection
    - Partial enabling/disabling and selection

Dependencies:
    - PySide6 for UI components
    - qtawesome for icons
    - Custom MIDI handling classes
    - Digital synth parameter definitions

"""

import logging
from typing import Dict, Optional, Union, List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShortcut, QKeySequence

from jdxi_editor.midi.data.editor.data import DigitalSynthData
from jdxi_editor.midi.data.parsers.util import COMMON_IGNORED_KEYS
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.data.digital import (
    DigitalOscWave,
    DigitalPartial,
    get_digital_parameter_by_address,
)
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParameter
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.midi.utils.conversions import midi_cc_to_ms, midi_cc_to_frac
from jdxi_editor.ui.editors.digital.common import DigitalCommonSection
from jdxi_editor.ui.editors.digital.tone_modify import DigitalToneModifySection
from jdxi_editor.ui.editors.digital.utils import _log_debug_info, _filter_sysex_keys, _get_partial_number, \
    _is_valid_sysex_area, _log_synth_area_info, _is_digital_synth_area, _sysex_area_matches
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.editors.digital.partial import DigitalPartialEditor
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox
from jdxi_editor.ui.widgets.switch.partial import PartialsPanel


def get_area(data: tuple[int, int]) -> str:
    """Map address bytes to corresponding temporary area."""
    logging.info(f"data for temporary area: {data}")
    area_mapping = {
        (0x18, 0x00): "TEMPORARY_PROGRAM_AREA",
        (0x19, 0x42): "TEMPORARY_ANALOG_SYNTH_AREA",
        (0x19, 0x01): "TEMPORARY_DIGITAL_SYNTH_1_AREA",
        (0x19, 0x21): "TEMPORARY_DIGITAL_SYNTH_2_AREA",
        (0x19, 0x70): "TEMPORARY_DRUM_KIT_AREA",
    }
    return area_mapping.get(tuple(data), "Unknown")


class DigitalSynthEditor(SynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        synth_number=1,
        parent=None,
        preset_helper=None,
    ):
        super().__init__(parent)
        self.instrument_image_group = None
        self.partial_number = None
        self.current_data = None
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper or (
            parent.digital_1_preset_helper
            if self.preset_type == SynthType.DIGITAL_1
            else parent.digital_2_preset_helper
        )
        self.main_window = parent
        self.synth_number = synth_number
        self.controls: Dict[
            Union[DigitalPartialParameter, DigitalCommonParameter], QWidget
        ] = {}
        self._init_synth_data(synth_number)
        self.setup_ui(synth_number)
        self.update_instrument_image()
        self._initialize_partial_states()

        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            if synth_number == 2:
                self.midi_helper.update_digital2_tone_name.connect(
                    self.set_instrument_title_label
                )

            else:
                self.midi_helper.update_digital1_tone_name.connect(
                    self.set_instrument_title_label
                )
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        self.data_request()
        self.show()

    def _init_synth_data(self, synth_number):
        """Initialize synth-specific data."""
        self.synth_data = DigitalSynthData(synth_number)
        print(self.synth_data)
        data = self.synth_data

        self.area = data.area
        self.part = data.part
        self.group = data.group
        self.setWindowTitle(data.window_title)

        self.preset_type = data.preset_type
        self.instrument_default_image = data.instrument_default_image
        self.instrument_icon_folder = data.instrument_icon_folder
        self.presets = data.presets
        self.preset_list = data.preset_list
        self.midi_requests = data.midi_requests
        self.midi_channel = data.midi_channel

    def setup_ui(self, synth_num):
        self.setMinimumSize(800, 300)
        self.resize(930, 600)
        # Image display
        self.instrument_image_group = QGroupBox()
        instrument_group_layout = QVBoxLayout()
        self.instrument_image_group.setLayout(instrument_group_layout)
        self.instrument_image_label = QLabel()
        instrument_group_layout.addWidget(self.instrument_image_label)
        self.instrument_image_group.setStyleSheet(Style.JDXI_INSTRUMENT_IMAGE_LABEL)
        self.instrument_image_group.setMinimumWidth(450)
        self.instrument_image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setStyleSheet(Style.JDXI_TABS + Style.JDXI_EDITOR)
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Title and instrument selection
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = DigitalTitle()
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        self.instrument_selection_label = QLabel("Select address digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        # Title and instrument selection selection
        self._create_instrument_group(container_layout, upper_layout)

        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        container_layout.addWidget(self.partials_panel)
        self.partials_panel.setStyleSheet(Style.JDXI_TABS)

        self._create_partial_tab_widget(container_layout, self.midi_helper)

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect partial switches to enable/disable tabs
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)
        self.midi_helper.midi_parameter_received.connect(self._on_parameter_received)
        self.show()

    def _create_instrument_group(self, container_layout, upper_layout):
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = QLabel(self.presets[0] if self.presets else "")
        self.instrument_title_label = DigitalTitle()
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)
        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)
        self.instrument_selection_label = QLabel("Select preset for Digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        self.instrument_selection_combo = PresetComboBox(self.synth_data.preset_list)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_helper.current_preset_zero_indexed
        )
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.preset_helper.preset_changed.connect(self.update_combo_box_index)
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        instrument_title_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(instrument_preset_group)
        upper_layout.addStretch(1)
        upper_layout.addWidget(self.instrument_image_group)
        container_layout.addLayout(upper_layout)
        self.update_instrument_image()

    def _create_partial_tab_widget(self, container_layout, midi_helper):
        # Create tab widget for partials
        self.partial_tab_widget = QTabWidget()
        self.partial_tab_widget.setStyleSheet(Style.JDXI_TABS + Style.JDXI_EDITOR)
        self.partial_editors = {}
        # Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(midi_helper, self.synth_number, i, parent=self)
            self.partial_editors[i] = editor
            self.partial_tab_widget.addTab(editor, f"Partial {i}")
        self.common_section = DigitalCommonSection(
            self._create_parameter_slider, self._create_parameter_switch, self.controls
        )
        self.partial_tab_widget.addTab(self.common_section, "Common")
        self.tone_modify_section = DigitalToneModifySection(
            self._create_parameter_slider,
            self._create_parameter_combo_box,
            self._create_parameter_switch,
            self.controls,
        )
        self.partial_tab_widget.addTab(self.tone_modify_section, "Tone Modify")
        container_layout.addWidget(self.partial_tab_widget)

    def _on_partial_state_changed(
        self, partial: DigitalPartial, enabled: bool, selected: bool
    ):
        """Handle partial state changes"""
        self.set_partial_state(partial, enabled, selected)

        # Enable/disable corresponding tab
        partial_num = partial.value
        self.partial_tab_widget.setTabEnabled(partial_num - 1, enabled)

        # Switch to selected partial's tab
        if selected:
            self.partial_tab_widget.setCurrentIndex(partial_num - 1)

    def set_partial_state(self,
                          partial: DigitalPartial,
                          enabled: bool = True,
                          selected: bool = True) -> bool:
        """Set the state of address partial

        Args:
            partial: The partial to modify
            enabled: Whether the partial is enabled (ON/OFF)
            selected: Whether the partial is selected

        Returns:
            True if successful
        """
        try:
            logging.info(f"Setting partial {partial.switch_param} state: enabled={enabled}, selected={selected}")
            self.send_midi_parameter(param=partial.switch_param, value=1 if enabled else 0)
            logging.info(f"Setting partial {partial.select_param} state: enabled={enabled}, selected={selected}")
            self.send_midi_parameter(param=partial.select_param, value=1 if selected else 0)
        except Exception as ex:
            logging.error(f"Error setting partial {partial.name} state: {str(ex)}")
            return False

    def _initialize_partial_states(self):
        """Initialize partial states with defaults"""
        # Default: Partial 1 enabled and selected, others disabled
        for partial in DigitalPartial.get_partials():
            enabled = partial == DigitalPartial.PARTIAL_1
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.partial_tab_widget.setTabEnabled(partial.value - 1, enabled)

        # Show first tab
        self.partial_tab_widget.setCurrentIndex(0)

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        if not _is_digital_synth_area(address[0]):
            return

        parameter_address = tuple(address[2:])
        partial_no = address[1]
        param = get_digital_parameter_by_address(parameter_address)

        if not param:
            logging.debug(f"No parameter found for address: {parameter_address}")
            return

        logging.info(f"Received param: {param} | address: {address} | value: {value}")
        self._update_partial_slider(partial_no, param, value)
        self._handle_special_params(partial_no, param, value)

    def _handle_special_params(self, partial_no, param, value):
        if param == DigitalPartialParameter.OSC_WAVE:
            self._update_waveform_buttons(partial_no, value)
            logging.debug(f"Updated waveform buttons for OSC_WAVE: value={value}")

        elif param == DigitalPartialParameter.FILTER_MODE_SWITCH:
            self.partial_editors[partial_no].filter_mode_switch.setValue(value)
            self._update_filter_state(partial_no, value)
            logging.debug(f"Updated filter state for FILTER_MODE_SWITCH: value={value}")

    def _apply_partial_ui_updates(self, partial_no: int, sysex_data: dict):
        """Apply updates to the UI components based on SysEx data."""
        debug_stats = True
        successes, failures = [], []

        for param_name, param_value in sysex_data.items():
            param = DigitalPartialParameter.get_by_name(param_name)
            if not param:
                failures.append(param_name)
                continue

            if param == DigitalPartialParameter.OSC_WAVE:
                self._update_waveform_buttons(partial_no, param_value)
            elif param == DigitalPartialParameter.FILTER_MODE_SWITCH:
                self._update_filter_state(partial_no, value=param_value)
            else:
                self._update_partial_slider(partial_no, param, param_value, successes)
                self._update_partial_adsr_widget(partial_no, param, param_value)

        if debug_stats:
            success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
            logging.info(f"Successes: {successes}")
            logging.info(f"Failures: {failures}")
            logging.info(f"Success Rate: {success_rate:.1f}%")
            logging.info("--------------------------------")

    def _dispatch_sysex_to_area(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        failures, successes = [], []

        # Parse SysEx data
        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        synth_tone = sysex_data.get("SYNTH_TONE")

        if synth_tone in ["TONE_COMMON", "TONE_MODIFY"]:
            logging.info("\nTone common")
            self._update_tone_common_modify_sliders_from_sysex(json_sysex_data)
        elif synth_tone in ["PRC3"]:  # This is for drums but comes through
            pass
        else:
            self._update_partial_sliders_from_sysex(json_sysex_data)

    def _update_filter_state(self, partial_no, value):
        """update_filter_state"""
        self.partial_editors[partial_no].update_filter_controls_state(value)

    def _update_partial_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes for a partial based on parsed SysEx data."""
        logging.info("Updating Partial UI components from SysEx data")

        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        current_synth = get_area([self.area, self.part])
        logging.info(f"current_synth: {current_synth}")
        temp_area = sysex_data.get("TEMPORARY_AREA")
        if not current_synth == temp_area:
            return

        partial_no = _get_partial_number(sysex_data.get("SYNTH_TONE"))
        if partial_no is None:
            return

        filtered_data = _filter_sysex_keys(sysex_data)
        self._apply_partial_ui_updates(partial_no, filtered_data)

    def _update_partial_sliders_from_sysex_new(self, json_sysex_data: str):
        """Update sliders and combo boxes for a partial based on parsed SysEx data."""
        logging.info("Updating Partial UI components from SysEx data")

        sysex_data = self._parse_sysex_json(json_sysex_data)
        print(sysex_data)
        if not sysex_data:
            return

        if not _sysex_area_matches(sysex_data, self.area):
            logging.info("SysEx area mismatch. Skipping update.")
            return

        partial_no = _get_partial_number(sysex_data.get("SYNTH_TONE"))
        if partial_no is None:
            return

        filtered_data = _filter_sysex_keys(sysex_data)
        self._apply_partial_ui_updates(partial_no, filtered_data)

    def _update_tone_common_modify_ui(self, sysex_data: Dict, successes: list, failures: list, debug: bool):
        """
        :param sysex_data: Dictionary containing SysEx data
        :param successes: List of successful parameters
        :param failures: List of failed parameters
        :param debug: bool
        :return: None

        _update_tone_common_modify_ui
        """
        logging.info("\nTone common and modify")
        for param_name, param_value in sysex_data.items():
            param = DigitalCommonParameter.get_by_name(param_name)
            logging.info(f"Tone common/modify : param_name: {param} {param_value}")
            if not param:
                failures.append(param_name)
                continue

            try:
                if param.name in ["PARTIAL1_SWITCH", "PARTIAL2_SWITCH", "PARTIAL3_SWITCH"]:
                    self._update_partial_selection_switch(param, param_value, successes, failures, debug)
                if param.name in ["PARTIAL1_SELECT", "PARTIAL2_SELECT", "PARTIAL3_SELECT"]:
                    self._update_partial_selected_state(param, param_value, successes, failures, debug)
                elif "SWITCH" or "SHIFT" in param_name:
                    self._update_switch(param, param_value, successes, failures, debug)
                else:
                    self._update_slider(param, param_value, successes, failures, debug)
            except Exception as ex:
                logging.info(f"Error {ex} occurred")

    def _update_tone_common_modify_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and switches based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        successes, failures = [], []

        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data or not _is_valid_sysex_area(sysex_data):
            return

        _log_synth_area_info(sysex_data)

        synth_tone = sysex_data.get("SYNTH_TONE")

        filtered_data = {
            k: v for k, v in sysex_data.items() if k not in COMMON_IGNORED_KEYS
        }

        if synth_tone in ["TONE_COMMON", "TONE_MODIFY"]:
            self._update_tone_common_modify_ui(filtered_data, successes, failures, debug_param_updates)

        _log_debug_info(filtered_data, successes, failures, debug_stats)

    def _update_partial_slider(self, partial_no: int, param, value, successes: list):
        slider = self.partial_editors[partial_no].controls.get(param)
        if not slider:
            return

        slider_value = param.convert_from_midi(value)
        logging.info(f"Updating {param.name}: MIDI {value} -> Slider {slider_value}")
        slider.blockSignals(True)
        slider.setValue(slider_value)
        slider.blockSignals(False)
        successes.append(param.name)

    def _update_partial_adsr_widget(self, partial_no: int, param, value):
        use_frac = param in {
            DigitalPartialParameter.AMP_ENV_SUSTAIN_LEVEL,
            DigitalPartialParameter.FILTER_ENV_SUSTAIN_LEVEL,
        }
        new_value = midi_cc_to_frac(value) if use_frac else midi_cc_to_ms(value)

        adsr_map = {
            DigitalPartialParameter.AMP_ENV_ATTACK_TIME:
                self.partial_editors[partial_no].amp_tab.amp_env_adsr_widget.attack_sb,
            DigitalPartialParameter.AMP_ENV_DECAY_TIME:
                self.partial_editors[partial_no].amp_tab.amp_env_adsr_widget.decay_sb,
            DigitalPartialParameter.AMP_ENV_SUSTAIN_LEVEL:
                self.partial_editors[partial_no].amp_tab.amp_env_adsr_widget.sustain_sb,
            DigitalPartialParameter.AMP_ENV_RELEASE_TIME:
                self.partial_editors[partial_no].amp_tab.amp_env_adsr_widget.release_sb,
            DigitalPartialParameter.FILTER_ENV_ATTACK_TIME:
                self.partial_editors[partial_no].filter_tab.filter_adsr_widget.attack_sb,
            DigitalPartialParameter.FILTER_ENV_DECAY_TIME:
                self.partial_editors[partial_no].filter_tab.filter_adsr_widget.decay_sb,
            DigitalPartialParameter.FILTER_ENV_SUSTAIN_LEVEL:
                self.partial_editors[partial_no].filter_tab.filter_adsr_widget.sustain_sb,
            DigitalPartialParameter.FILTER_ENV_RELEASE_TIME:
                self.partial_editors[partial_no].filter_tab.filter_adsr_widget.release_sb,
        }

        spinbox = adsr_map.get(param)
        if spinbox:
            spinbox.setValue(new_value)

    def _update_slider(self, param, value, successes, failures, debug):
        """ Update slider based on parameter and value. """
        slider = self.controls.get(param)
        logging.info(f"Updating slider for: {param}")
        if slider:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            successes.append(param.name)
            if debug:
                logging.info(f"Updated: {param.name:50} {value}")
        else:
            failures.append(param.name)

    def _update_switch(self, param, value, successes, failures, debug):
        """ Update switch based on parameter and value. """
        switch = self.controls.get(param)
        logging.info(f"Updating switch for: {param}")
        try:
            value = int(value)
            if switch:
                switch.blockSignals(True)
                switch.setValue(value)
                switch.blockSignals(False)
                successes.append(param.name)
                if debug:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)
        except Exception as ex:
            logging.info(f"Error {ex} occurred setting switch {param.name} to {value}")
            failures.append(param.name)

    def _update_partial_selection_switch(self, param, value, successes, failures, debug):
        """Update the partial selection switches based on parameter and value."""
        param_name = param.name
        partial_switch_map = {
            "PARTIAL1_SWITCH": 1,
            "PARTIAL2_SWITCH": 2,
            "PARTIAL3_SWITCH": 3,
        }
        partial_number = partial_switch_map.get(param_name)
        check_box = self.partials_panel.switches.get(partial_number)
        logging.info(f"Updating switch for: {param_name}, checkbox: {check_box}")
        if check_box:
            check_box.blockSignals(True)
            check_box.setState(bool(value), False)
            check_box.blockSignals(False)
            successes.append(param.name)
            if debug:
                logging.info(f"Updated: {param.name:50} {value}")
        else:
            failures.append(param.name)

    def _update_partial_selected_state(self, param, value, successes, failures, debug):
        """Update the partial selection switches based on parameter and value."""
        param_name = param.name
        partial_switch_map = {
            "PARTIAL1_SELECT": 1,
            "PARTIAL2_SELECT": 2,
            "PARTIAL3_SELECT": 3,
        }
        partial_number = partial_switch_map.get(param_name)
        check_box = self.partials_panel.switches.get(partial_number)
        logging.info(f"Updating switch for: {param_name}, checkbox: {check_box}")
        if check_box:
            check_box.blockSignals(True)
            check_box.setSelected(bool(value))
            check_box.blockSignals(False)
            successes.append(param.name)
            if debug:
                logging.info(f"Updated: {param.name:50} {value}")
        else:
            failures.append(param.name)

    def _update_waveform_buttons(self, partial_number, value):
        """Update the waveform buttons based on the OSC_WAVE value with visual feedback."""
        logging.debug(
            f"Updating waveform buttons for partial {partial_number} with value {value}"
        )

        if partial_number is None:
            logging.warning("Cannot update waveform buttons: partial_number is None")
            return

        waveform_map = {
            0: DigitalOscWave.SAW,
            1: DigitalOscWave.SQUARE,
            2: DigitalOscWave.PW_SQUARE,
            3: DigitalOscWave.TRIANGLE,
            4: DigitalOscWave.SINE,
            5: DigitalOscWave.NOISE,
            6: DigitalOscWave.SUPER_SAW,
            7: DigitalOscWave.PCM,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            logging.warning(f"Unknown waveform value: {value}")
            return

        logging.debug(f"Waveform value {value} found, selecting {selected_waveform}")

        # Retrieve waveform buttons for the given partial
        if partial_number not in self.partial_editors:
            logging.warning(f"Partial editor {partial_number} not found")
            return

        wave_buttons = self.partial_editors[partial_number].oscillator_tab.wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_RECT)
        else:
            logging.warning(f"Waveform button not found for {selected_waveform}")
