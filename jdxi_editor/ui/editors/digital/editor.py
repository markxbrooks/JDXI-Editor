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

from typing import Dict, Optional, Union

from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.jdxi.preset.widget import InstrumentPresetWidget
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
from jdxi_editor.ui.editors.digital import (
    DigitalCommonSection,
    DigitalPartialEditor,
    DigitalToneModifySection,
)
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.panel.partial import PartialsPanel
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_fraction, midi_value_to_ms


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

        JDXi.UI.ThemeManager.apply_tabs_style(self)
        JDXi.UI.ThemeManager.apply_editor_style(self)

        # Use EditorBaseWidget for consistent layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content(spacing=5, margins=(5, 5, 5, 5))

        # Get container layout for adding content
        container_layout = self.base_widget.get_container_layout()

        # Add base widget to editor's layout
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

        # === Top half ===
        instrument_widget = QWidget()
        instrument_layout = QVBoxLayout()
        instrument_widget.setLayout(instrument_layout)

        # Partials panel only
        self.partials_panel = PartialsPanel()
        JDXi.UI.ThemeManager.apply_tabs_style(self.partials_panel)

        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)

        # --- Use InstrumentPresetWidget for consistent layout
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

        # --- Add partials panel directly to container
        container_layout.addWidget(self.partials_panel)
        container_layout.setSpacing(5)  # Minimal spacing instead of stretch

        # --- Create partial tab widget
        self.partial_tab_widget = QTabWidget()
        self.partial_tab_widget.setStyleSheet(JDXi.UI.Style.TAB_TITLE)
        instrument_widget.setLayout(instrument_layout)
        try:
            presets_icon = JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.MUSIC_NOTE_MULTIPLE, color=JDXi.UI.Style.GREY
            )
            if presets_icon is None or presets_icon.isNull():
                raise ValueError("Icon is null")
        except:
            presets_icon = JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.MUSIC, color=JDXi.UI.Style.GREY
            )
        self.partial_tab_widget.addTab(instrument_widget, presets_icon, "Presets")
        self._create_partial_tab_widget(container_layout, self.midi_helper)

    def _create_partial_tab_widget(
        self, container_layout: QVBoxLayout, midi_helper: MidiIOHelper
    ) -> None:
        """
        Create the partial tab widget for the digital synth editor.

        :param container_layout: QVBoxLayout for the main container
        :param midi_helper: MiodiIOHelper instance for MIDI communication
        :return: None
        """

        JDXi.UI.ThemeManager.apply_tabs_style(self.partial_tab_widget)
        JDXi.UI.ThemeManager.apply_editor_style(self.partial_tab_widget)
        self.partial_editors = {}
        # --- Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialEditor(
                midi_helper,
                self.synth_number,
                i,
                preset_type=self.preset_type,
                parent=self,
            )
            self.partial_editors[i] = editor
            partial_icon = JDXi.UI.IconRegistry.get_icon(
                f"mdi.numeric-{i}-circle-outline", color=JDXi.UI.Style.GREY
            )
            self.partial_tab_widget.addTab(editor, partial_icon, f"Partial {i}")
        self.common_section = DigitalCommonSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._create_parameter_combo_box,
            self.controls,
        )
        common_icon = JDXi.UI.IconRegistry.get_icon(
            "mdi.cog-outline", color=JDXi.UI.Style.GREY
        )
        self.partial_tab_widget.addTab(self.common_section, common_icon, "Common")
        self.tone_modify_section = DigitalToneModifySection(
            self._create_parameter_slider,
            self._create_parameter_combo_box,
            self._create_parameter_switch,
            self.controls,
        )
        misc_icon = JDXi.UI.IconRegistry.get_icon(
            "mdi.dots-horizontal", color=JDXi.UI.Style.GREY
        )
        self.partial_tab_widget.addTab(self.tone_modify_section, misc_icon, "Misc")
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
            self._update_filter_mode_buttons(partial_no, value)
            self._update_filter_state(partial_no, value)
            log.parameter("Updated filter state for FILTER_MODE_SWITCH", value)

        elif param == DigitalPartialParam.LFO_SHAPE:
            self._update_lfo_shape_buttons(partial_no, value)
            log.parameter("Updated LFO shape buttons for LFO_SHAPE", value)

        elif param == DigitalPartialParam.MOD_LFO_SHAPE:
            self._update_mod_lfo_shape_buttons(partial_no, value)
            log.parameter("Updated Mod LFO shape buttons for MOD_LFO_SHAPE", value)

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
                self._update_filter_mode_buttons(partial_no, param_value)
                self._update_filter_state(partial_no, value=param_value)
            elif param == DigitalPartialParam.LFO_SHAPE:
                self._update_lfo_shape_buttons(partial_no, param_value)
            elif param == DigitalPartialParam.MOD_LFO_SHAPE:
                self._update_mod_lfo_shape_buttons(partial_no, param_value)
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
            log.warning("Unknown waveform value: %s", value)
            return

        log.parameter(f"Waveform value {value} found, selecting", selected_waveform)

        # Retrieve waveform buttons for the given partial
        if partial_number not in self.partial_editors:
            log.warning(f"Partial editor {partial_number} not found")
            return

        wave_buttons = self.partial_editors[partial_number].oscillator_tab.wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        else:
            log.warning("Waveform button not found for: %s", selected_waveform)

    def _update_filter_mode_buttons(self, partial_number: int, value: int):
        """
        Update the filter mode buttons based on the FILTER_MODE_SWITCH value with visual feedback

        :param partial_number: int
        :param value: int
        :return:
        """
        log.parameter(
            f"Updating filter mode buttons for partial {partial_number}", value
        )
        if partial_number is None:
            return

        from jdxi_editor.midi.data.digital.filter import DigitalFilterMode

        filter_mode_map = {
            0: DigitalFilterMode.BYPASS,
            1: DigitalFilterMode.LPF,
            2: DigitalFilterMode.HPF,
            3: DigitalFilterMode.BPF,
            4: DigitalFilterMode.PKG,
            5: DigitalFilterMode.LPF2,
            6: DigitalFilterMode.LPF3,
            7: DigitalFilterMode.LPF4,
        }

        selected_filter_mode = filter_mode_map.get(value)

        if selected_filter_mode is None:
            log.warning("Unknown filter mode value: %s", value)
            return

        log.parameter(
            f"Filter mode value {value} found, selecting", selected_filter_mode
        )

        # Retrieve filter mode buttons for the given partial
        if partial_number not in self.partial_editors:
            log.warning(f"Partial editor {partial_number} not found")
            return

        filter_mode_buttons = self.partial_editors[
            partial_number
        ].filter_tab.filter_mode_buttons

        # Reset all buttons to default style
        for btn in filter_mode_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # Apply active style to the selected filter mode button
        selected_btn = filter_mode_buttons.get(selected_filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        else:
            log.warning("Filter mode button not found for: %s", selected_filter_mode)

    def _update_lfo_shape_buttons(self, partial_number: int, value: int):
        """
        Update the LFO shape buttons based on the LFO_SHAPE value with visual feedback

        :param partial_number: int
        :param value: int
        :return:
        """
        log.parameter(f"Updating LFO shape buttons for partial {partial_number}", value)
        if partial_number is None:
            return

        from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape

        lfo_shape_map = {
            0: DigitalLFOShape.TRIANGLE,
            1: DigitalLFOShape.SINE,
            2: DigitalLFOShape.SAW,
            3: DigitalLFOShape.SQUARE,
            4: DigitalLFOShape.SAMPLE_HOLD,
            5: DigitalLFOShape.RANDOM,
        }

        selected_lfo_shape = lfo_shape_map.get(value)

        if selected_lfo_shape is None:
            log.warning("Unknown LFO shape value: %s", value)
            return

        log.parameter(f"LFO shape value {value} found, selecting", selected_lfo_shape)

        # Retrieve LFO shape buttons for the given partial
        if partial_number not in self.partial_editors:
            log.warning(f"Partial editor {partial_number} not found")
            return

        lfo_shape_buttons = self.partial_editors[
            partial_number
        ].lfo_tab.lfo_shape_buttons

        # Reset all buttons to default style
        for btn in lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # Apply active style to the selected LFO shape button
        selected_btn = lfo_shape_buttons.get(selected_lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        else:
            log.warning("LFO shape button not found for: %s", selected_lfo_shape)

    def _update_mod_lfo_shape_buttons(self, partial_number: int, value: int):
        """
        Update the Mod LFO shape buttons based on the MOD_LFO_SHAPE value with visual feedback

        :param partial_number: int
        :param value: int
        :return:
        """
        log.parameter(
            f"Updating Mod LFO shape buttons for partial {partial_number}", value
        )
        if partial_number is None:
            return

        from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape

        mod_lfo_shape_map = {
            0: DigitalLFOShape.TRIANGLE,
            1: DigitalLFOShape.SINE,
            2: DigitalLFOShape.SAW,
            3: DigitalLFOShape.SQUARE,
            4: DigitalLFOShape.SAMPLE_HOLD,
            5: DigitalLFOShape.RANDOM,
        }

        selected_mod_lfo_shape = mod_lfo_shape_map.get(value)

        if selected_mod_lfo_shape is None:
            log.warning("Unknown Mod LFO shape value: %s", value)
            return

        log.parameter(
            f"Mod LFO shape value {value} found, selecting", selected_mod_lfo_shape
        )

        # Retrieve Mod LFO shape buttons for the given partial
        if partial_number not in self.partial_editors:
            log.warning(f"Partial editor {partial_number} not found")
            return

        mod_lfo_shape_buttons = self.partial_editors[
            partial_number
        ].mod_lfo_tab.mod_lfo_shape_buttons

        # Reset all buttons to default style
        for btn in mod_lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # Apply active style to the selected Mod LFO shape button
        selected_btn = mod_lfo_shape_buttons.get(selected_mod_lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        else:
            log.warning(
                "Mod LFO shape button not found for: %s", selected_mod_lfo_shape
            )


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

class MyHandler:
    def __init__(self, partial_no):
        self.partial_no = partial_no
        self._build_registry()

    def _build_registry(self):
        self._registry = {
            DigitalPartialParam.OSC_WAVE: self._wave_handler,
            DigitalPartialParam.FILTER_MODE_SWITCH: self._filter_mode_handler,
            DigitalPartialParam.LFO_SHAPE: self._lfo_shape_handler,
            DigitalPartialParam.MOD_LFO_SHAPE: self._mod_lfo_shape_handler,
        }

    def _wave_handler(self, param_value, successes, failures):
        self._update_waveform_buttons(self.partial_no, param_value)

    def _filter_mode_handler(self, param_value, successes, failures):
        self._update_filter_mode_buttons(self.partial_no, param_value)
        self._update_filter_state(self.partial_no, value=param_value)

    def _lfo_shape_handler(self, param_value, successes, failures):
        self._update_lfo_shape_buttons(self.partial_no, param_value)

    def _mod_lfo_shape_handler(self, param_value, successes, failures):
        self._update_mod_lfo_shape_buttons(self.partial_no, param_value)

    def handle(self, param, param_value, successes, failures):
        func = self._registry.get(param)
        if func:
            func(param_value, successes, failures)
            return True
        return False

    def process_sysex_data(self, sysex_data):
        failures = []
        successes = []
        handler = MyHandler(self.partial_no)
    
        for param_name, param_value in sysex_data.items():
            param = DigitalPartialParam.get_by_name(param_name)
            if not param:
                failures.append(param_name)
                continue
            if not handler.handle(param, param_value, successes, failures):
                if param in self.adsr_parameters:
                    self._update_partial_adsr_widgets(
                        self.partial_no, param, param_value, successes, failures
                    )
                elif param in self.pitch_env_parameters:
                    self._update_partial_pitch_env_widgets(
                        self.partial_no, param, param_value, successes, failures
                    )
                elif param in self.pwm_parameters:
                    self._update_pulse_width_widgets(
                        self.partial_no, param, param_value, successes, failures
                    )
                else:
                    self._update_partial_slider(
                        self.partial_no, param, param_value, successes, failures
                    )
    
        return successes, failures


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
