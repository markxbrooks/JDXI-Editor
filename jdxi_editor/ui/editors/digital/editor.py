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

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_fraction, midi_value_to_ms
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.factory import create_synth_data
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.digital import DigitalPartial
from jdxi_editor.midi.data.parameter.digital import (
    DigitalCommonParam,
    DigitalModifyParam,
    DigitalPartialParam,
)
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.partial.switch import PartialSelectState, PartialSwitchState
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.editors.base.editor import BaseSynthEditor
from jdxi_editor.ui.editors.digital import (
    DigitalCommonSection,
    DigitalPartialPanel,
    DigitalToneModifySection,
)
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.preset.widget import InstrumentPresetWidget
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.widgets.panel.partial import PartialsPanel


class DigitalSynthEditor(BaseSynthEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    FILTER_MODE_MAP = {
        0: Digital.Filter.Mode.BYPASS,
        1: Digital.Filter.Mode.LPF,
        2: Digital.Filter.Mode.HPF,
        3: Digital.Filter.Mode.BPF,
        4: Digital.Filter.Mode.PKG,
        5: Digital.Filter.Mode.LPF2,
        6: Digital.Filter.Mode.LPF3,
        7: Digital.Filter.Mode.LPF4,
    }

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: JDXiPresetHelper = None,
        synth_number: int = 1,
        parent: "JDXiInstrument" = None,
    ):
        super().__init__(parent)
        self.main_layout = None
        self.instrument_image_group: QGroupBox | None = None
        self.instrument_title_label: QLabel | None = None
        self.partial_number = None
        self.current_data = None
        self.midi_helper = midi_helper
        self.preset_helper = preset_helper
        self.main_window = parent
        self.controls: Dict[
            Union[DigitalPartialParam, DigitalCommonParam],
            QWidget,
        ] = {}
        synth_map = {1: JDXi.Synth.DIGITAL_SYNTH_1, 2: JDXi.Synth.DIGITAL_SYNTH_2}
        if synth_number not in synth_map:
            raise ValueError(
                f"Invalid synth_number: {synth_number}. Must be 1, 2 or 3."
            )
        self.synth_number = synth_number
        self._init_synth_data(synth_map[synth_number])
        # Set parameter lists before connecting signals (Sysex can arrive immediately)
        self.adsr_parameters = [
            Digital.Param.AMP_ENV_ATTACK_TIME,
            Digital.Param.AMP_ENV_DECAY_TIME,
            Digital.Param.AMP_ENV_SUSTAIN_LEVEL,
            Digital.Param.AMP_ENV_RELEASE_TIME,
            Digital.Param.FILTER_ENV_ATTACK_TIME,
            Digital.Param.FILTER_ENV_DECAY_TIME,
            Digital.Param.FILTER_ENV_SUSTAIN_LEVEL,
            Digital.Param.FILTER_ENV_RELEASE_TIME,
        ]
        self.pitch_env_parameters = [
            Digital.Param.OSC_PITCH_ENV_ATTACK_TIME,
            Digital.Param.OSC_PITCH_ENV_DECAY_TIME,
            Digital.Param.OSC_PITCH_ENV_DEPTH,
        ]
        self.pwm_parameters = [
            Digital.Param.OSC_PULSE_WIDTH,
            Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
        ]
        self.build_widgets()
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
        # Note: data_request() is called in showEvent() when editor is displayed

        def __str__(self):
            return f"{self.__class__.__name__} {self.preset_type}"

        def __repr__(self):
            return f"{self.__class__.__name__} {self.preset_type}"

    def setup_ui(self):
        """set up user interface"""
        self.set_dimensions()
        self.set_style()

        self.base_widget.setup_scrollable_content(
            spacing=JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING,
            margins=JDXi.UI.Dimensions.EDITOR_DIGITAL.MARGINS,
        )

        # --- Add base widget to editor's layout
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
        JDXi.UI.Theme.apply_tabs_style(self.partials_panel)

        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)

        # --- Use InstrumentPresetWidget for consistent layout
        self.instrument_preset: InstrumentPresetWidget = InstrumentPresetWidget(
            parent=self
        )
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
        instrument_layout.setSpacing(
            JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING
        )  # Minimal spacing
        instrument_widget.setLayout(instrument_layout)
        try:
            presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC_NOTE_MULTIPLE, color=JDXi.UI.Style.GREY
            )
            if presets_icon is None or presets_icon.isNull():
                raise ValueError("Icon is null")
        except:
            presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.MUSIC, color=JDXi.UI.Style.GREY
            )
        # Get container layout for adding content
        container_layout = self.base_widget.get_container_layout()
        # --- Add partials panel directly to container
        container_layout.addWidget(self.partials_panel)
        container_layout.setSpacing(
            JDXi.UI.Dimensions.EDITOR_DIGITAL.SPACING
        )  # Minimal spacing instead of stretch
        self.tab_widget.setStyleSheet(JDXi.UI.Style.TAB_TITLE)
        self._add_tab(key=Digital.Tab.PRESETS, widget=instrument_widget)
        self._setup_tabs(container_layout, self.midi_helper)

    def set_style(self):
        """Set style"""
        JDXi.UI.Theme.apply_tabs_style(self)
        JDXi.UI.Theme.apply_editor_style(self)

    def set_dimensions(self):
        """Set dimensions"""
        self.setMinimumSize(
            JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_WIDTH,
            JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_HEIGHT,
        )
        self.resize(
            JDXi.UI.Dimensions.EDITOR_DIGITAL.INIT_WIDTH,
            JDXi.UI.Dimensions.EDITOR_DIGITAL.INIT_HEIGHT,
        )

    def build_widgets(self):
        """Build Widgets before running setup ui"""
        # --- Create partial tab widget
        self.tab_widget = QTabWidget()
        # Use EditorBaseWidget for consistent layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=self.analog)

    def _setup_tabs(
        self, container_layout: QVBoxLayout, midi_helper: MidiIOHelper
    ) -> None:
        """
        Create the partial tab widget for the digital synth editor.

        :param container_layout: QVBoxLayout for the main container
        :param midi_helper: MidiIOHelper instance for MIDI communication
        :return: None
        """
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget)
        JDXi.UI.Theme.apply_editor_style(self.tab_widget)
        self.partial_editors = {}
        # --- Create editor for each partial
        for i in range(1, 4):
            editor = DigitalPartialPanel(
                midi_helper,
                self.synth_number,
                i,
                preset_type=self.preset_type,
                parent=self,
            )
            self.partial_editors[i] = editor
            # Use tab definitions for partials
            if i == 1:
                self._add_tab(key=Digital.Tab.PARTIAL_1, widget=editor)
            elif i == 2:
                self._add_tab(key=Digital.Tab.PARTIAL_2, widget=editor)
            elif i == 3:
                self._add_tab(key=Digital.Tab.PARTIAL_3, widget=editor)

        self.common_section = DigitalCommonSection(
            controls=self.controls,
            address=self.address,
            send_midi_parameter=self.send_midi_parameter,
            midi_helper=midi_helper,
        )
        self._add_tab(key=Digital.Tab.COMMON, widget=self.common_section)

        self.tone_modify_section = DigitalToneModifySection(
            controls=self.controls,
            send_midi_parameter=self.send_midi_parameter,
            midi_helper=midi_helper,
        )
        self._add_tab(key=Digital.Tab.MISC, widget=self.tone_modify_section)
        container_layout.addWidget(self.tab_widget)

    def _on_partial_state_changed(
        self, partial: DigitalPartial, enabled: bool, selected: bool
    ) -> None:
        """
        Handle the state change of a partial (enabled/disabled and selected/unselected).

        :param partial: DigitalPartial The partial to modify
        :param enabled: bool Whether the partial is enabled (ON/OFF)
        :param selected: Whether the partial is selected
        :return: None
        """
        self.set_partial_state(partial, enabled, selected)

        # --- Enable/disable corresponding tab
        partial_num = partial.value
        self.tab_widget.setTabEnabled(partial_num, enabled)

        # --- Switch to selected partial's tab
        if selected:
            self.tab_widget.setCurrentIndex(partial_num)

    def set_partial_state(
        self, partial: DigitalPartial, enabled: bool = True, selected: bool = True
    ) -> Optional[bool]:
        """
        Set the state of a partial (enabled/disabled and selected/unselected).

        :param partial: The partial to modify (DigitalPartial enum)
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
            self.tab_widget.setTabEnabled(partial.value, enabled)
        self.tab_widget.setCurrentIndex(0)

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
        if param == Digital.Param.OSC_WAVEFORM:
            self._update_waveform_buttons(partial_no, value)
            log.parameter("Updated waveform buttons for OSC_WAVE", value)

        elif param == Digital.Param.FILTER_MODE_SWITCH:
            self._update_filter_mode_buttons(partial_no, value)
            self._update_filter_state(partial_no, value)
            log.parameter("Updated filter state for FILTER_MODE_SWITCH", value)

        elif param == Digital.Param.LFO_SHAPE:
            self._update_lfo_shape_buttons(partial_no, value)
            log.parameter("Updated LFO shape buttons for LFO_SHAPE", value)

        elif param == Digital.Param.MOD_LFO_SHAPE:
            self._update_mod_lfo_shape_buttons(partial_no, value)
            log.parameter("Updated Mod LFO shape buttons for MOD_LFO_SHAPE", value)

    def _update_controls(
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
            param = Digital.Param.get_by_name(param_name)
            if not param:
                failures.append(param_name)
                continue

            if param == Digital.Param.OSC_WAVEFORM:
                self._update_waveform_buttons(partial_no, param_value)
            elif param == Digital.Param.FILTER_MODE_SWITCH:
                self._update_filter_mode_buttons(partial_no, param_value)
                self._update_filter_state(partial_no, value=param_value)
            elif param == Digital.Param.LFO_SHAPE:
                self._update_lfo_shape_buttons(partial_no, param_value)
            elif param == Digital.Param.MOD_LFO_SHAPE:
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
        self.partial_editors[partial_no].filter_tab.update_controls_state(value)

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
        sysex_data.pop(SysExSection.SYNTH_TONE, None)
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
                    PartialSwitchState.PARTIAL1_SWITCH,
                    PartialSwitchState.PARTIAL2_SWITCH,
                    PartialSwitchState.PARTIAL3_SWITCH,
                ]:
                    self._update_partial_selection_switch(
                        param, param_value, successes, failures
                    )
                if param.name in [
                    PartialSelectState.PARTIAL1_SELECT,
                    PartialSelectState.PARTIAL2_SELECT,
                    PartialSelectState.PARTIAL3_SELECT,
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
        sysex_data.pop(SysExSection.SYNTH_TONE, None)
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
            Digital.Param.AMP_ENV_SUSTAIN_LEVEL,
            Digital.Param.FILTER_ENV_SUSTAIN_LEVEL,
        }
        control_value = (
            midi_value_to_fraction(midi_value)
            if use_fraction
            else midi_value_to_ms(midi_value)
        )
        self.adsr_map = {
            Digital.Param.AMP_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].amp_tab.adsr_widget.attack_control,
            Digital.Param.AMP_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].amp_tab.adsr_widget.decay_control,
            Digital.Param.AMP_ENV_SUSTAIN_LEVEL: self.partial_editors[
                partial_no
            ].amp_tab.adsr_widget.sustain_control,
            Digital.Param.AMP_ENV_RELEASE_TIME: self.partial_editors[
                partial_no
            ].amp_tab.adsr_widget.release_control,
            Digital.Param.FILTER_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].filter_tab.adsr_widget.attack_control,
            Digital.Param.FILTER_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].filter_tab.adsr_widget.decay_control,
            Digital.Param.FILTER_ENV_SUSTAIN_LEVEL: self.partial_editors[
                partial_no
            ].filter_tab.adsr_widget.sustain_control,
            Digital.Param.FILTER_ENV_RELEASE_TIME: self.partial_editors[
                partial_no
            ].filter_tab.adsr_widget.release_control,
        }
        spinbox = self.adsr_map.get(param)
        if not spinbox:
            failures.append(param.name)
            return
        if spinbox:
            spinbox.blockSignals(True)
            spinbox.setValue(control_value)
            spinbox.blockSignals(False)
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
            Digital.Param.OSC_PITCH_ENV_DEPTH,
        }
        new_value = (
            midi_value_to_fraction(midi_value)
            if use_fraction
            else midi_value_to_ms(midi_value, 10, 5000)
        )
        self.pitch_env_map = {
            Digital.Param.OSC_PITCH_ENV_ATTACK_TIME: self.partial_editors[
                partial_no
            ].oscillator_tab.pitch_env_widget.attack_control,
            Digital.Param.OSC_PITCH_ENV_DECAY_TIME: self.partial_editors[
                partial_no
            ].oscillator_tab.pitch_env_widget.decay_control,
            Digital.Param.OSC_PITCH_ENV_DEPTH: self.partial_editors[
                partial_no
            ].oscillator_tab.pitch_env_widget.depth_control,
        }
        control = self.pitch_env_map.get(param)
        if control:
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)
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
            Digital.Param.OSC_PULSE_WIDTH,
            Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
        }
        new_value = (
            midi_value_to_fraction(midi_value)
            if use_fraction
            else midi_value_to_ms(midi_value, 10, 5000)
        )
        # Try to get controls from the oscillator section's controls dictionary
        oscillator_section = self.partial_editors[partial_no].oscillator_tab
        control = None

        # First, try to get from controls dictionary (new parameter-based system)
        if (
            hasattr(oscillator_section, "controls")
            and param in oscillator_section.controls
        ):
            control = oscillator_section.controls[param]
        # Fallback: try to access pwm_widget (old system, for backward compatibility)
        elif (
            hasattr(oscillator_section, "pwm_widget") and oscillator_section.pwm_widget
        ):
            if param == Digital.Param.OSC_PULSE_WIDTH:
                control = oscillator_section.pwm_widget.pulse_width_control
            elif param == Digital.Param.OSC_PULSE_WIDTH_MOD_DEPTH:
                control = oscillator_section.pwm_widget.mod_depth_control

        if control:
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)
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
            PartialSwitchState.PARTIAL1_SWITCH: 1,
            PartialSwitchState.PARTIAL2_SWITCH: 2,
            PartialSwitchState.PARTIAL3_SWITCH: 3,
        }
        partial_number = partial_switch_map.get(param_name)
        if partial_number is None:
            failures.append(param.name)
            return

        # --- Convert integer to DigitalPartial enum for dictionary lookup
        partial_enum = DigitalPartial(partial_number)
        check_box = self.partials_panel.switches.get(partial_enum)
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
            PartialSelectState.PARTIAL1_SELECT: 1,
            PartialSelectState.PARTIAL2_SELECT: 2,
            PartialSelectState.PARTIAL3_SELECT: 3,
        }
        partial_number = partial_switch_map.get(param_name)
        if partial_number is None:
            failures.append(param.name)
            return

        # --- Convert integer to DigitalPartial enum for dictionary lookup
        partial_enum = DigitalPartial(partial_number)
        check_box = self.partials_panel.switches.get(partial_enum)
        if check_box:
            check_box.blockSignals(True)
            check_box.setSelected(bool(value))
            check_box.blockSignals(False)
            successes.append(param.name)
            # --- log.message(f"Updated: {param.name:50} {value}")
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
            0: Digital.Wave.Osc.SAW,
            1: Digital.Wave.Osc.SQUARE,
            2: Digital.Wave.Osc.PW_SQUARE,
            3: Digital.Wave.Osc.TRI,
            4: Digital.Wave.Osc.SINE,
            5: Digital.Wave.Osc.NOISE,
            6: Digital.Wave.Osc.SUPER_SAW,
            7: Digital.Wave.Osc.PCM,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            log.warning("Unknown waveform value: %s", value)
            return

        log.parameter(f"Waveform value {value} found, selecting", selected_waveform)

        # --- Retrieve waveform buttons for the given partial
        if partial_number not in self.partial_editors:
            log.warning(f"Partial editor {partial_number} not found")
            return

        wave_buttons = self.partial_editors[
            partial_number
        ].oscillator_tab.waveform_buttons

        # --- Reset all buttons to default style
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

        # Update enabled states of dependent widgets (e.g., SuperSaw Detune)
        oscillator_section = self.partial_editors[partial_number].oscillator_tab
        if hasattr(oscillator_section, "_update_button_enabled_states"):
            oscillator_section._update_button_enabled_states(selected_waveform)

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

        selected_filter_mode = self.FILTER_MODE_MAP.get(value)

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
            0: Digital.LFO.Shape.TRI,
            1: Digital.LFO.Shape.SINE,
            2: Digital.LFO.Shape.SAW,
            3: Digital.LFO.Shape.SQUARE,
            4: Digital.LFO.Shape.SAMPLE_HOLD,
            5: Digital.LFO.Shape.RANDOM,
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
        ].lfo_tab.wave_shape_buttons

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
            0: Digital.LFO.Shape.TRI,
            1: Digital.LFO.Shape.SINE,
            2: Digital.LFO.Shape.SAW,
            3: Digital.LFO.Shape.SQUARE,
            4: Digital.LFO.Shape.SAMPLE_HOLD,
            5: Digital.LFO.Shape.RANDOM,
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
        ].mod_lfo_tab.wave_shape_buttons

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
