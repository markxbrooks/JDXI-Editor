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

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.jdxi.preset.widget import InstrumentPresetWidget
from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.synth.factory import create_synth_data
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.digital import DigitalOscWave, DigitalPartial
from jdxi_editor.midi.data.parameter.digital import (
    DigitalCommonParam,
    DigitalModifyParam,
    DigitalPartialParam,
)
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.utils.conversions import midi_value_to_fraction, midi_value_to_ms
from jdxi_editor.ui.editors.digital import (
    DigitalCommonSection,
    DigitalPartialEditor,
    DigitalToneModifySection,
)
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.widgets.panel.partial import PartialsPanel
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions, DigitalDimensions


class DigitalSynthEditor(SynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXiPresetHelper = None,
        synth_number: int = 1,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.instrument_image_group: QGroupBox | None = None
        self.instrument_title_label: QLabel | None = None
        self.partial_number = None
        self.current_data = None
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper or (
            parent.digital_1_preset_helper
            if self.preset_type == JDXiSynth.DIGITAL_SYNTH_1
            else parent.digital_2_preset_helper
        )
        self.main_window = parent
        self.controls: Dict[
            Union[DigitalPartialParam, DigitalCommonParam],
            QWidget,
        ] = {}
        synth_map = {1: JDXiSynth.DIGITAL_SYNTH_1, 2: JDXiSynth.DIGITAL_SYNTH_2}
        if synth_number not in synth_map:
            raise ValueError(
                f"Invalid synth_number: {synth_number}. Must be 1, 2 or 3."
            )
        self.synth_number = synth_number
        self._init_synth_data(synth_map[synth_number])
        self.setup_ui()
        self.update_instrument_image()
        self._initialize_partial_states()
        # Connect signals
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_control_changed.connect(self._handle_control_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        # Request data from the synth for initialization of state and show the editor
        self.data_request()
        # self.show()
        self.adsr_parameters = [
            DigitalPartialParam.AMP_ENV_ATTACK_TIME,
            DigitalPartialParam.AMP_ENV_DECAY_TIME,
            DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL,
            DigitalPartialParam.AMP_ENV_RELEASE_TIME,
            DigitalPartialParam.FILTER_ENV_ATTACK_TIME,
            DigitalPartialParam.FILTER_ENV_DECAY_TIME,
            DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
            DigitalPartialParam.FILTER_ENV_RELEASE_TIME,
        ]
        self.pitch_env_parameters = [
            DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
            DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME,
            DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
        ]
        self.pwm_parameters = [
            DigitalPartialParam.OSC_PULSE_WIDTH,
            DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH,
        ]

        def __str__(self):
            return f"{self.__class__.__name__} {self.preset_type}"

        def __repr__(self):
            return f"{self.__class__.__name__} {self.preset_type}"

    def setup_ui(self):
        """set up user interface"""
        self.setMinimumSize(850, 300)
        self.resize(1030, 600)
        from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager

        JDXiThemeManager.apply_tabs_style(self)
        JDXiThemeManager.apply_editor_style(self)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # === Top half ===
        instrument_widget = QWidget()
        instrument_layout = QVBoxLayout()
        instrument_widget.setLayout(instrument_layout)

        # Partials panel only
        self.partials_panel = PartialsPanel()
        JDXiThemeManager.apply_tabs_style(self.partials_panel)

        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(DigitalDimensions.SPACING)  # Reduced spacing
        container_layout.setContentsMargins(DigitalDimensions.MARGIN, DigitalDimensions.MARGIN, DigitalDimensions.MARGIN, DigitalDimensions.MARGIN)  # Reduced margins
        container.setLayout(container_layout)

        # Use InstrumentPresetWidget for consistent layout
        self.instrument_preset = InstrumentPresetWidget(parent=self)
        self.instrument_preset.setup_header_layout()
        self.instrument_preset.setup()

        instrument_preset_group = self.instrument_preset.create_instrument_preset_group(
            synth_type="Digital"
        )
        self.instrument_preset.add_preset_group(instrument_preset_group)
        self.instrument_preset.add_stretch()

        (
            self.instrument_image_group,
            self.instrument_image_label,
            self.instrument_group_layout,
        ) = self.instrument_preset.create_instrument_image_group()
        self.instrument_preset.add_image_group(self.instrument_image_group)
        self.instrument_preset.add_stretch()
        self.update_instrument_image()

        instrument_layout.addWidget(self.instrument_preset)
        instrument_layout.setSpacing(5)  # Minimal spacing
        container_layout.addWidget(self.partials_panel)
        container_layout.setSpacing(5)  # Minimal spacing instead of stretch
        self.partial_tab_widget = QTabWidget()
        instrument_widget.setLayout(instrument_layout)
        self.partial_tab_widget.addTab(instrument_widget, "Presets")
        self._create_partial_tab_widget(container_layout, self.midi_helper)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_partial_tab_widget(
        self, container_layout: QVBoxLayout, midi_helper: MidiIOHelper
    ) -> None:
        """
        Create the partial tab widget for the digital synth editor.

        :param container_layout: QVBoxLayout for the main container
        :param midi_helper: MiodiIOHelper instance for MIDI communication
        :return: None
        """

        JDXiThemeManager.apply_tabs_style(self.partial_tab_widget)
        JDXiThemeManager.apply_editor_style(self.partial_tab_widget)
        self.partial_editors = {}
        # Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(
                midi_helper,
                self.synth_number,
                i,
                preset_type=self.preset_type,
                parent=self,
            )
            self.partial_editors[i] = editor
            self.partial_tab_widget.addTab(editor, f"Partial {i}")
        self.common_section = DigitalCommonSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._create_parameter_combo_box,
            self.controls,
        )
        self.partial_tab_widget.addTab(self.common_section, "Common")
        self.tone_modify_section = DigitalToneModifySection(
            self._create_parameter_slider,
            self._create_parameter_combo_box,
            self._create_parameter_switch,
            self.controls,
        )
        self.partial_tab_widget.addTab(self.tone_modify_section, "Misc")
        container_layout.addWidget(self.partial_tab_widget)

    def _on_partial_state_changed(
        self, partial: DigitalPartialParam, enabled: bool, selected: bool
    ) -> None:
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
        self.partial_tab_widget.setTabEnabled(partial_num, enabled)

        # Switch to selected partial's tab
        if selected:
            self.partial_tab_widget.setCurrentIndex(partial_num)

    def set_partial_state(
        self, partial: DigitalPartialParam, enabled: bool = True, selected: bool = True
    ) -> Optional[bool]:
        """
        Set the state of a partial (enabled/disabled and selected/unselected).

        :param partial: The partial to modify
        :param enabled: Whether the partial is enabled (ON/OFF)
        :param selected: Whether the partial is selected
        :return: True if successful, False otherwise
        """
        try:
            log.parameter("Setting partial:", partial.switch_param)
            log.parameter("Partial state enabled (Yes/No):", enabled)
            log.parameter("Partial selected (Yes/No):", selected)
            self.send_midi_parameter(
                param=partial.switch_param, value=1 if enabled else 0
            )
            self.send_midi_parameter(
                param=partial.select_param, value=1 if selected else 0
            )
            return True
        except Exception as ex:
            log.error(f"Error setting partial {partial.name} state: {str(ex)}")
            return False

    def _initialize_partial_states(self):
        """
        Initialize partial states with defaults
        Default: Partial 1 enabled and selected, others disabled
        """
        for partial in DigitalPartial.get_partials():
            enabled = partial == DigitalPartial.PARTIAL_1
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.partial_tab_widget.setTabEnabled(partial.value, enabled)
        self.partial_tab_widget.setCurrentIndex(0)

    def _handle_special_params(
        self, partial_no: int, param: AddressParameter, value: int
    ) -> None:
        """
        Handle special parameters that require additional UI updates.

        :param partial_no: int
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        if param == DigitalPartialParam.OSC_WAVE:
            self._update_waveform_buttons(partial_no, value)
            log.parameter("Updated waveform buttons for OSC_WAVE", value)

        elif param == DigitalPartialParam.FILTER_MODE_SWITCH:
            self.partial_editors[partial_no].filter_tab.filter_mode_switch.setValue(
                value
            )
            self._update_filter_state(partial_no, value)
            log.parameter("Updated filter state for FILTER_MODE_SWITCH", value)

    def _update_partial_controls(
        self, partial_no: int, sysex_data: dict, successes: list, failures: list
    ) -> None:
        """
        Apply updates to the UI components based on the received SysEx data.

        :param partial_no: int
        :param sysex_data: dict
        :param successes: list
        :param failures: list
        :return: None
        """
        for param_name, param_value in sysex_data.items():
            param = DigitalPartialParam.get_by_name(param_name)
            if not param:
                failures.append(param_name)
                continue

            if param == DigitalPartialParam.OSC_WAVE:
                self._update_waveform_buttons(partial_no, param_value)
            elif param == DigitalPartialParam.FILTER_MODE_SWITCH:
                self._update_filter_state(partial_no, value=param_value)
            elif param in self.adsr_parameters:
                self._update_partial_adsr_widgets(
                    partial_no, param, param_value, successes, failures
                )
            elif param in self.pitch_env_parameters:
                self._update_partial_pitch_env_widgets(
                    partial_no, param, param_value, successes, failures
                )
            elif param in self.pwm_parameters:
                self._update_pulse_width_widgets(
                    partial_no, param, param_value, successes, failures
                )
            else:
                self._update_partial_slider(
                    partial_no, param, param_value, successes, failures
                )

        log.debug_info(successes, failures)

    def _update_filter_state(self, partial_no: int, value: int) -> None:
        """
        Update the filter state of a partial based on the given value.

        :param partial_no: int
        :param value: int
        :return: None
        """
        self.partial_editors[partial_no].update_filter_controls_state(value)

    def _update_common_controls(
        self,
        partial_number: int,
        sysex_data: Dict,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Update the UI components for tone common and modify parameters.

        :param partial_number: int partial number
        :param sysex_data: Dictionary containing SysEx data
        :param successes: List of successful parameters
        :param failures: List of failed parameters
        :return: None
        """
        for control in self.controls:
            log.parameter("control", control, silent=True)
        sysex_data.pop("SYNTH_TONE", None)
        sysex_data.pop("TONE_CATEGORY", None)
        for param_name, param_value in sysex_data.items():
            log.parameter(f"{param_name} {param_value}", param_value, silent=True)
            param = DigitalCommonParam.get_by_name(param_name)
            if not param:
                log.parameter(
                    f"param not found: {param_name} ", param_value, silent=True
                )
                failures.append(param_name)
                continue
            log.parameter(f"found {param_name}", param_name, silent=True)
            try:
                if param.name in [
                    "PARTIAL1_SWITCH",
                    "PARTIAL2_SWITCH",
                    "PARTIAL3_SWITCH",
                ]:
                    self._update_partial_selection_switch(
                        param, param_value, successes, failures
                    )
                if param.name in [
                    "PARTIAL1_SELECT",
                    "PARTIAL2_SELECT",
                    "PARTIAL3_SELECT",
                ]:
                    self._update_partial_selected_state(
                        param, param_value, successes, failures
                    )
                elif "SWITCH" in param_name:
                    self._update_switch(param, param_value, successes, failures)
                else:
                    self._update_slider(param, param_value, successes, failures)
            except Exception as ex:
                log.error(f"Error {ex} occurred")

    def _update_modify_controls(
        self,
        partial_number: int,
        sysex_data: dict,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Update the UI components for tone common and modify parameters.

        :param partial_number: int partial number
        :param sysex_data: dict Dictionary containing SysEx data
        :param successes: list List of successful parameters
        :param failures: list List of failed parameters
        :return: None
        """
        for control in self.controls:
            log.parameter("control", control, silent=True)
        sysex_data.pop("SYNTH_TONE", None)
        for param_name, param_value in sysex_data.items():
            log.parameter(f"{param_name} {param_value}", param_value, silent=True)
            param = DigitalModifyParam.get_by_name(param_name)
            if not param:
                log.parameter(
                    f"param not found: {param_name} ", param_value, silent=True
                )
                failures.append(param_name)
                continue
            elif "SWITCH" in param_name:
                self._update_switch(param, param_value, successes, failures)
            else:
                log.parameter(f"found {param_name}", param_name, silent=True)
                self.address.lmb = AddressOffsetSuperNATURALLMB.MODIFY
                self._update_slider(param, param_value, successes, failures)

    def _update_partial_adsr_widgets(
        self,
        partial_no: int,
        param: DigitalPartialParam,
        midi_value: int,
        successes: list = None,
        failures: list = None,
    ):
        """
        Update the ADSR widget for a specific partial based on the parameter and value.

        :param partial_no: int Partial number
        :param param: AddressParameter address
        :param midi_value: int value
        :return: None
        """
        use_fraction = param in {
            DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL,
            DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL,
        }
        control_value = (
            midi_value_to_fraction(midi_value)
            if use_fraction
            else midi_value_to_ms(midi_value)
        )
        self.adsr_map = {
            DigitalPartialParam.AMP_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.attack_control,
            DigitalPartialParam.AMP_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.decay_control,
            DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.sustain_control,
            DigitalPartialParam.AMP_ENV_RELEASE_TIME: self.partial_editors[
                partial_no
            ].amp_tab.amp_env_adsr_widget.release_control,
            DigitalPartialParam.FILTER_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.attack_control,
            DigitalPartialParam.FILTER_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.decay_control,
            DigitalPartialParam.FILTER_ENV_SUSTAIN_LEVEL: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.sustain_control,
            DigitalPartialParam.FILTER_ENV_RELEASE_TIME: self.partial_editors[
                partial_no
            ].filter_tab.filter_adsr_widget.release_control,
        }
        spinbox = self.adsr_map.get(param)
        if not spinbox:
            failures.append(param.name)
            return
        if spinbox:
            spinbox.setValue(control_value)
            synth_data = create_synth_data(JDXiSynth.DIGITAL_SYNTH_1, partial_no)
            self.address.lmb = synth_data.lmb
            log_slider_parameters(self.address, param, midi_value, control_value)
            successes.append(param.name)

    def _update_partial_pitch_env_widgets(
        self,
        partial_no: int,
        param: DigitalPartialParam,
        midi_value: int,
        successes: list = None,
        failures: list = None,
    ):
        """
        Update the Pitch Env widget for a specific partial based on the parameter and value.

        :param partial_no: int Partial number
        :param param: AddressParameter address
        :param midi_value: int value
        :param successes: list = None,
        :param failures: list = None,
        :return: None
        """
        use_fraction = param in {
            DigitalPartialParam.OSC_PITCH_ENV_DEPTH,
        }
        new_value = (
            midi_value_to_fraction(midi_value)
            if use_fraction
            else midi_value_to_ms(midi_value, 10, 5000)
        )
        self.pitch_env_map = {
            DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].oscillator_tab.pitch_env_widget.attack_control,
            DigitalPartialParam.OSC_PITCH_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].oscillator_tab.pitch_env_widget.decay_control,
            DigitalPartialParam.OSC_PITCH_ENV_DEPTH: self.partial_editors[
                partial_no
            ].oscillator_tab.pitch_env_widget.depth_control,
        }
        control = self.pitch_env_map.get(param)
        if control:
            control.setValue(new_value)
            successes.append(param.name)
        else:
            failures.append(param.name)

    def _update_pulse_width_widgets(
        self,
        partial_no: int,
        param: DigitalPartialParam,
        midi_value: int,
        successes: list = None,
        failures: list = None,
    ):
        """
        Update the Pitch Env widget for a specific partial based on the parameter and value.

        :param partial_no: int Partial number
        :param param: AddressParameter address
        :param midi_value: int value
        :param successes: list = None,
        :param failures: list = None,
        :return: None
        """
        use_fraction = param in {
            DigitalPartialParam.OSC_PULSE_WIDTH,
            DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH,
        }
        new_value = (
            midi_value_to_fraction(midi_value)
            if use_fraction
            else midi_value_to_ms(midi_value, 10, 5000)
        )
        self.pitch_env_map = {
            DigitalPartialParam.OSC_PULSE_WIDTH: self.partial_editors[
                partial_no
            ].oscillator_tab.pwm_widget.pulse_width_control,
            DigitalPartialParam.OSC_PULSE_WIDTH_MOD_DEPTH: self.partial_editors[
                partial_no
            ].oscillator_tab.pwm_widget.mod_depth_control,
        }
        control = self.pitch_env_map.get(param)
        if control:
            control.setValue(new_value)
            successes.append(param.name)
        else:
            failures.append(param.name)

    def _update_partial_selection_switch(
        self,
        param: AddressParameter,
        value: int,
        successes: list,
        failures: list,
    ) -> None:
        """
        Update the partial selection switches based on parameter and value.

        :param param: AddressParameter
        :param value: int
        :param successes: list
        :param failures: list
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
        log.parameter(
            f"Updating switch for: {param_name}, checkbox:", check_box, silent=True
        )
        if check_box:
            check_box.blockSignals(True)
            check_box.setState(bool(value), False)
            check_box.blockSignals(False)
            successes.append(param.name)
        else:
            failures.append(param.name)

    def _update_partial_selected_state(
        self,
        param: AddressParameter,
        value: int,
        successes: list,
        failures: list,
    ) -> None:
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
        if check_box:
            check_box.blockSignals(True)
            check_box.setSelected(bool(value))
            check_box.blockSignals(False)
            successes.append(param.name)
            # log.message(f"Updated: {param.name:50} {value}")
        else:
            failures.append(param.name)

    def _update_waveform_buttons(self, partial_number: int, value: int):
        """
         Update the waveform buttons based on the OSC_WAVE value with visual feedback

        :param partial_number: int
        :param value: int
        :return:
        """
        log.parameter(f"Updating waveform buttons for partial {partial_number}", value)
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

        log.parameter(f"Waveform value {value} found, selecting", selected_waveform)

        # Retrieve waveform buttons for the given partial
        if partial_number not in self.partial_editors:
            logging.warning(f"Partial editor {partial_number} not found")
            return

        wave_buttons = self.partial_editors[partial_number].oscillator_tab.wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXiStyle.BUTTON_RECT)
        else:
            logging.warning("Waveform button not found for: %s", selected_waveform)


class DigitalSynth2Editor(DigitalSynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXiPresetHelper = None,
        synth_number: int = 2,
        parent: QWidget = None,
    ):
        super().__init__(
            midi_helper=midi_helper,
            synth_number=synth_number,
            preset_helper=preset_helper,
            parent=parent,
        )


class DigitalSynth3Editor(DigitalSynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXiPresetHelper = None,
        synth_number: int = 3,
        parent: QWidget = None,
    ):
        super().__init__(
            midi_helper=midi_helper,
            synth_number=synth_number,
            preset_helper=preset_helper,
            parent=parent,
        )
