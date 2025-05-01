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
from typing import Dict, Optional, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QLabel,
    QPushButton, QSplitter,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShortcut, QKeySequence

from jdxi_editor.jdxi.preset.helper import JDXIPresetHelper
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.data.parsers.util import COMMON_IGNORED_KEYS
from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.data.digital import (
    DigitalOscWave,
    DigitalPartial,
    get_digital_parameter_by_address,
)
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.digital.partial import AddressParameterDigitalPartial
from jdxi_editor.midi.utils.conversions import midi_cc_to_ms, midi_cc_to_frac
from jdxi_editor.ui.editors.digital.common import DigitalCommonSection
from jdxi_editor.ui.editors.digital.tone_modify import DigitalToneModifySection
from jdxi_editor.ui.editors.digital.utils import (
    _log_debug_info,
    _filter_sysex_keys,
    _get_partial_number,
    _is_valid_sysex_area,
    _log_synth_area_info,
    _is_digital_synth_area,
    get_area,
)
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.editors.digital.partial import DigitalPartialEditor
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox
from jdxi_editor.ui.widgets.panel.partial import PartialsPanel


class DigitalSynthEditor(SynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXIPresetHelper = None,
        synth_number: int = 1,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.instrument_image_group = None
        self.partial_number = None
        self.current_data = None
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper or (
            parent.digital_1_preset_helper
            if self.preset_type == JDXISynth.DIGITAL_1
            else parent.digital_2_preset_helper
        )
        self.main_window = parent
        self.controls: Dict[
            Union[AddressParameterDigitalPartial, AddressParameterDigitalCommon], QWidget
        ] = {}
        synth_map = {
            1: JDXISynth.DIGITAL_1,
            2: JDXISynth.DIGITAL_2
        }
        if synth_number not in synth_map:
            raise ValueError(f"Invalid synth_number: {synth_number}. Must be 1 or 2.")
        self.synth_number = synth_number
        self._init_synth_data(synth_map[synth_number])
        self.setup_ui()
        self.update_instrument_image()
        self._initialize_partial_states()
        # Connect signals
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        # Request data from the synth for initialization of state and show the editor
        self.data_request()
        self.show()

    def setup_ui(self):
        """ set up user interface """
        self.setMinimumSize(800, 300)
        self.resize(930, 600)
        self.setStyleSheet(JDXIStyle.TABS + JDXIStyle.EDITOR)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        # === Top half ===
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_widget.setLayout(top_layout)

        # Partials panel only
        self.partials_panel = PartialsPanel()
        self.partials_panel.setStyleSheet(JDXIStyle.TABS)

        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)

        # === Bottom half (scroll area) ===
        # inside setup_ui()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        self.instrument_image_group = QGroupBox()
        instrument_group_layout = QVBoxLayout()
        self.instrument_image_group.setLayout(instrument_group_layout)
        self.instrument_image_label = QLabel()
        instrument_group_layout.addWidget(self.instrument_image_label)
        self.instrument_image_group.setStyleSheet(JDXIStyle.INSTRUMENT_IMAGE_LABEL)
        self.instrument_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instrument_image_group.setMinimumWidth(450)

        container_layout.addWidget(self.instrument_image_group)

        upper_layout = QHBoxLayout()
        top_layout.addLayout(upper_layout)
        top_layout.addWidget(self.partials_panel)

        self._create_instrument_group(container_layout, upper_layout)

        self._create_partial_tab_widget(container_layout, self.midi_helper)

        scroll.setWidget(container)

        splitter.addWidget(top_widget)
        splitter.addWidget(scroll)

        splitter.setSizes([100, 600])  # give more room to bottom

        # Splitter handle style
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #444;
                border: 1px solid #666;
            }
            QSplitter::handle:vertical {
                height: 6px;
            }
            QSplitter::handle:horizontal {
                width: 6px;
            }
        """)

        self.midi_helper.midi_parameter_received.connect(self._on_parameter_received)

        self.show()

    def _create_instrument_group(self,
                                 container_layout: QVBoxLayout,
                                 upper_layout:  QHBoxLayout) -> None:
        """
        Create the instrument group for the digital synth editor.
        :param container_layout: Layout for the main container
        :param upper_layout: Upper layout for the instrument group
        :return: None
        """
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

    def _create_partial_tab_widget(self,
                                   container_layout: QVBoxLayout,
                                   midi_helper: MidiIOHelper) -> None:
        """
        Create the partial tab widget for the digital synth editor.
        :param container_layout: QVBoxLayout for the main container
        :param midi_helper: MiodiIOHelper instance for MIDI communication
        :return: None
        """
        self.partial_tab_widget = QTabWidget()
        self.partial_tab_widget.setStyleSheet(JDXIStyle.TABS + JDXIStyle.EDITOR)
        self.partial_editors = {}
        # Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(
                midi_helper, self.synth_number, i, parent=self
            )
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

    def _on_partial_state_changed(self,
                                  partial: DigitalPartial,
                                  enabled: bool,
                                  selected: bool) -> None:
        """
        Handle the state change of a partial (enabled/disabled and selected/unselected).
        :param partial: The partial to modify
        :param enabled: Whether the partial is enabled (ON/OFF)
        :param selected: Whether the partial is selected
        :return: None
        """
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
                          selected: bool = True) -> Optional[bool]:
        """
        Set the state of a partial (enabled/disabled and selected/unselected).
        :param partial: The partial to modify
        :param enabled: Whether the partial is enabled (ON/OFF)
        :param selected: Whether the partial is selected
        :return: True if successful, False otherwise
        """
        try:
            log_parameter("Setting partial:", partial.switch_param)
            log_parameter("Partial state enabled (Yes/No):", enabled)
            log_parameter("Partial selected (Yes/No):", selected)
            self.send_midi_parameter(
                param=partial.switch_param, value=1 if enabled else 0
            )
            self.send_midi_parameter(
                param=partial.select_param, value=1 if selected else 0
            )
            return True
        except Exception as ex:
            log_message(f"Error setting partial {partial.name} state: {str(ex)}")
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

    def _on_parameter_received(self,
                               address: list,
                               value: int) -> None:
        """
        Handle received MIDI parameter and update UI components accordingly.
        :param address: list
        :param value: int
        :return: None
        """
        if not _is_digital_synth_area(address[0]):
            return

        parameter_address = tuple(address[2:])
        partial_no = address[1]
        param = get_digital_parameter_by_address(parameter_address)

        if not param:
            log_parameter("No parameter found for address", parameter_address)
            return

        log_message(f"Received param: {param} | address: {address} | value: {value}")
        self._update_partial_slider(partial_no, param, value)
        self._handle_special_params(partial_no, param, value)

    def _handle_special_params(self,
                               partial_no: int,
                               param: AddressParameter,
                               value: int) -> None:
        """
        Handle special parameters that require additional UI updates.
        :param partial_no: int
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        if param == AddressParameterDigitalPartial.OSC_WAVE:
            self._update_waveform_buttons(partial_no, value)
            log_parameter("Updated waveform buttons for OSC_WAVE", value)

        elif param == AddressParameterDigitalPartial.FILTER_MODE_SWITCH:
            self.partial_editors[partial_no].filter_mode_switch.setValue(value)
            self._update_filter_state(partial_no, value)
            log_parameter("Updated filter state for FILTER_MODE_SWITCH", value)

    def _apply_partial_ui_updates(self,
                                  partial_no: int,
                                  sysex_data: dict) -> None:
        """
        Apply updates to the UI components based on the received SysEx data.
        :param partial_no: int
        :param sysex_data: dict
        :return: None
        """
        debug_stats = True
        successes, failures = [], []

        for param_name, param_value in sysex_data.items():
            param = AddressParameterDigitalPartial.get_by_name(param_name)
            if not param:
                failures.append(param_name)
                continue

            if param == AddressParameterDigitalPartial.OSC_WAVE:
                self._update_waveform_buttons(partial_no, param_value)
            elif param == AddressParameterDigitalPartial.FILTER_MODE_SWITCH:
                self._update_filter_state(partial_no, value=param_value)
            else:
                self._update_partial_slider(partial_no, param, param_value, successes, failures)
                self._update_partial_adsr_widget(partial_no, param, param_value)

        if debug_stats:
            success_rate = (len(successes) / len(sysex_data) * 100) if sysex_data else 0
            log_message(f"Successes: \t{successes}")
            log_message(f"Failures: \t{failures}")
            log_message(f"Success Rate: \t{success_rate:.1f}%")
            log_message("============================================================================================")

    def _dispatch_sysex_to_area(self,
                                json_sysex_data: str) -> None:
        """
        Dispatch SysEx data to the appropriate area for processing.
        :param json_sysex_data:
        :return: None
        """
        failures, successes = [], []

        # Parse SysEx data
        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return
        temp_area = sysex_data.get("TEMPORARY_AREA")
        synth_tone = sysex_data.get("SYNTH_TONE")

        log_message("\n========================================================================================================================================================================================")
        log_message(f"Updating UI components from SysEx data for \t{temp_area} \t{synth_tone}")
        log_message("========================================================================================================================================================================================")

        if synth_tone in ["TONE_COMMON", "TONE_MODIFY"]:
            log_message("\nTone common")
            self._update_tone_common_modify_sliders_from_sysex(json_sysex_data)
        elif synth_tone in ["PRC3"]:  # This is for drums but comes through
            pass
        else:
            self._update_partial_sliders_from_sysex(json_sysex_data)

    def _update_filter_state(self,
                             partial_no: int,
                             value: int) -> None:
        """
        Update the filter state of a partial based on the given value.
        :param partial_no: int
        :param value: int
        :return: None
        """
        self.partial_editors[partial_no].update_filter_controls_state(value)

    def _update_partial_sliders_from_sysex(self,
                                           json_sysex_data: str) -> None:
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        :return: None
        """
        log_message("\nUpdating Partial UI components from SysEx data")

        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return
        current_synth = get_area([self.sysex_address.msb, self.sysex_address.umb])
        log_parameter("current_synth", current_synth)
        temp_area = sysex_data.get("TEMPORARY_AREA")
        log_parameter("temp_area", temp_area)
        if not current_synth == temp_area:
            log_message(f"temp_area: {temp_area} is not current_synth: {current_synth}, Skipping update")
            return
        log_message(f"temp_area: {temp_area} is current_synth: {current_synth}, updating...")
        incoming_data_partial_no = _get_partial_number(sysex_data.get("SYNTH_TONE"))
        log_parameter("incoming_data_partial_no", incoming_data_partial_no)
        if incoming_data_partial_no is None:
            return
        filtered_data = _filter_sysex_keys(sysex_data)
        self._apply_partial_ui_updates(incoming_data_partial_no, filtered_data)

    def _update_tone_common_modify_ui(self,
                                      sysex_data: Dict,
                                      successes: list = None,
                                      failures: list = None,
                                      debug: bool = False):
        """
        Update the UI components for tone common and modify parameters.
        :param sysex_data: Dictionary containing SysEx data
        :param successes: List of successful parameters
        :param failures: List of failed parameters
        :param debug: bool
        :return: None
        """
        log_message("\nTone common and modify")
        for param_name, param_value in sysex_data.items():
            param = AddressParameterDigitalCommon.get_by_name(param_name)
            log_parameter("Tone common/modify param", param)
            log_parameter("Tone common/modify : param_value", param_value)
            if not param:
                failures.append(param_name)
                continue

            try:
                if param.name in [
                    "PARTIAL1_SWITCH",
                    "PARTIAL2_SWITCH",
                    "PARTIAL3_SWITCH",
                ]:
                    self._update_partial_selection_switch(
                        param, param_value, successes, failures, debug
                    )
                if param.name in [
                    "PARTIAL1_SELECT",
                    "PARTIAL2_SELECT",
                    "PARTIAL3_SELECT",
                ]:
                    self._update_partial_selected_state(
                        param, param_value, successes, failures, debug
                    )
                elif "SWITCH" or "SHIFT" in param_name:
                    self._update_switch(param, param_value, successes, failures, debug)
                else:
                    self._update_slider(param, param_value, successes, failures, debug)
            except Exception as ex:
                log_message(f"Error {ex} occurred")

    def _update_tone_common_modify_sliders_from_sysex(self,
                                                      json_sysex_data: str) -> None:
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        :return: None
        """
        log_message("\n============================================================================================")
        log_message("Updating UI components from SysEx data")
        log_message("\n============================================================================================")
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
            self._update_tone_common_modify_ui(
                filtered_data, successes, failures, debug_param_updates
            )

        _log_debug_info(filtered_data, successes, failures, debug_stats)

    def _update_partial_slider(self,
                               partial_no: int,
                               param: AddressParameter,
                               value: int,
                               successes: list = None,
                               failures: list = None) -> None:
        """
        Update the slider for a specific partial based on the parameter and value.
        :param partial_no: int
        :param param: AddressParameter
        :param value: int
        :param successes: list
        :return: None
        """
        slider = self.partial_editors[partial_no].controls.get(param)
        if not slider:
            failures.append(param.name)
            return

        slider_value = param.convert_from_midi(value)
        log_slider_parameters(self.sysex_address.umb, self.sysex_address.lmb, param, value, slider_value)
        slider.blockSignals(True)
        slider.setValue(slider_value)
        slider.blockSignals(False)
        successes.append(param.name)

    def _update_partial_adsr_widget(self,
                                    partial_no: int,
                                    param: AddressParameter,
                                    value: int):
        """
        Update the ADSR widget for a specific partial based on the parameter and value.
        :param partial_no: int Partial number
        :param param: AddressParameter address
        :param value: int value
        :return: None
        """
        use_frac = param in {
            AddressParameterDigitalPartial.AMP_ENV_SUSTAIN_LEVEL,
            AddressParameterDigitalPartial.FILTER_ENV_SUSTAIN_LEVEL,
        }
        new_value = midi_cc_to_frac(value) if use_frac else midi_cc_to_ms(value)
        adsr_map = {
            AddressParameterDigitalPartial.AMP_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.attack_control,
            AddressParameterDigitalPartial.AMP_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.decay_control,
            AddressParameterDigitalPartial.AMP_ENV_SUSTAIN_LEVEL: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.depth_control,
            AddressParameterDigitalPartial.AMP_ENV_RELEASE_TIME: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.release_control,
            AddressParameterDigitalPartial.FILTER_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.attack_control,
            AddressParameterDigitalPartial.FILTER_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.decay_control,
            AddressParameterDigitalPartial.FILTER_ENV_SUSTAIN_LEVEL: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.depth_control,
            AddressParameterDigitalPartial.FILTER_ENV_RELEASE_TIME: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.release_control,
        }
        spinbox = adsr_map.get(param)
        if spinbox:
            spinbox.setValue(new_value)

    def _update_slider(self,
                       param: AddressParameter,
                       value: int,
                       successes: list = None,
                       failures: list = None,
                       debug: bool = False) -> None:
        """
        Update slider based on parameter and value.
        :param param: AddressParameter
        :param value: int value
        :param successes: list
        :param failures: list
        :param debug: bool
        :return: None
        """
        slider = self.controls.get(param)
        if debug:
            log_parameter("Updating slider for", param)
        if slider:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
            successes.append(param.name)
            if debug:
                log_parameter(f"Updated {value} for", param)
        else:
            failures.append(param.name)

    def _update_switch(self,
                       param: AddressParameter,
                       value: int,
                       successes: list = None,
                       failures: list = None,
                       debug: bool = False) -> None:
        """
        Update switch based on parameter and value.
        :param param: AddressParameter
        :param value: int value
        :param successes: list
        :param failures: list
        :param debug: bool
        :return: None
        """
        switch = self.controls.get(param)
        if debug:
            log_parameter("Updating switch for", param)
        try:
            value = int(value)
            if switch:
                switch.blockSignals(True)
                switch.setValue(value)
                switch.blockSignals(False)
                successes.append(param.name)
                if debug:
                    log_parameter(f"Updated {value} for", param)
            else:
                failures.append(param.name)
        except Exception as ex:
            log_message(f"Error {ex} occurred setting switch {param.name} to {value}")
            failures.append(param.name)

    def _update_partial_selection_switch(self,
                                         param: AddressParameter,
                                         value: int,
                                         successes: list,
                                         failures: list,
                                         debug: bool = False) -> None:
        """
        Update the partial selection switches based on parameter and value.
        :param param: AddressParameter
        :param value: int
        :param successes: list
        :param failures: list
        :param debug: bool
        :return: None
        """
        param_name = param.name
        partial_switch_map = {
            "PARTIAL1_SWITCH": 1,
            "PARTIAL2_SWITCH": 2,
            "PARTIAL3_SWITCH": 3,
        }
        partial_number = partial_switch_map.get(param_name)
        check_box = self.partials_panel.switches.get(partial_number)
        log_parameter(f"Updating switch for: {param_name}, checkbox:", check_box)
        if check_box:
            check_box.blockSignals(True)
            check_box.setState(bool(value), False)
            check_box.blockSignals(False)
            successes.append(param.name)
            if debug:
                log_message(f"Updated: {param.name:50} {value}")
        else:
            failures.append(param.name)

    def _update_partial_selected_state(self,
                                       param: AddressParameter,
                                       value: int,
                                       successes: list,
                                       failures: list,
                                       debug: bool = False) -> None:
        """
        Update the partial selected state based on parameter and value.
        :param param: AddressParameter
        :param value: int
        :param successes: list
        :param failures: list
        :param debug: bool
        :return: None
        """
        param_name = param.name
        partial_switch_map = {
            "PARTIAL1_SELECT": 1,
            "PARTIAL2_SELECT": 2,
            "PARTIAL3_SELECT": 3,
        }
        partial_number = partial_switch_map.get(param_name)
        check_box = self.partials_panel.switches.get(partial_number)
        log_message("Updating switch")
        log_parameter("param_name", param_name)
        log_parameter("checkbox", check_box)
        if check_box:
            check_box.blockSignals(True)
            check_box.setSelected(bool(value))
            check_box.blockSignals(False)
            successes.append(param.name)
            if debug:
                log_message(f"Updated: {param.name:50} {value}")
        else:
            failures.append(param.name)

    def _update_waveform_buttons(self,
                                 partial_number: int,
                                 value: int):
        """
         Update the waveform buttons based on the OSC_WAVE value with visual feedback
        :param partial_number: int
        :param value: int
        :return:
        """
        log_parameter(
            f"Updating waveform buttons for partial {partial_number}", value)
        if partial_number is None:
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
            logging.warning("Unknown waveform value: %s", value)
            return

        log_parameter(f"Waveform value {value} found, selecting", selected_waveform)

        # Retrieve waveform buttons for the given partial
        if partial_number not in self.partial_editors:
            logging.warning(f"Partial editor {partial_number} not found")
            return

        wave_buttons = self.partial_editors[partial_number].oscillator_tab.wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXIStyle.BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXIStyle.BUTTON_RECT)
        else:
            logging.warning("Waveform button not found for: %s",selected_waveform)


class DigitalSynth2Editor(DigitalSynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXIPresetHelper = None,
        synth_number: int = 2,
        parent: QWidget = None,
    ):
        super().__init__(midi_helper=midi_helper,
                         synth_number=synth_number,
                         preset_helper=preset_helper,
                         parent=parent)
