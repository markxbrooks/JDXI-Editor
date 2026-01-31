"""
Module: analog_synth_editor
===========================

This module defines the `AnalogSynthEditor` class, which provides a PySide6-based
user interface for editing analog synthesizer parameters in the Roland JD-Xi synthesizer.
It extends the `SynthEditor` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying analog synth parameters, including
  oscillator, filter, amp, LFO, and envelope settings.
- Supports MIDI communication to send and receive real-time parameter changes.
- Allows selection of different analog synth presets from a dropdown menu.
- Displays an instrument image that updates based on the selected preset.
- Includes a scrollable layout for managing a variety of parameter controls.
- Implements bipolar parameter handling for proper UI representation.
- Supports waveform selection with custom buttons and icons.
- Provides a "Send Read Request to Synth" button to retrieve current synth settings.
- Enables MIDI-triggered updates via incoming program changes and parameter adjustments.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (Analog.Parameter, AnalogCommonParameter, etc.)

Usage:
------
The `AnalogSynthEditor` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    preset_helper = PresetHandler()
    editor = AnalogSynthEditor(midi_helper, preset_helper)
    editor.show()

"""

import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.spec import AnalogTab
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.preset.widget import InstrumentPresetWidget

if TYPE_CHECKING:
    from jdxi_editor.ui.preset.helper import JDXiPresetHelper

from decologr import Decologr as log
from picomidi.utils.conversion import (
    midi_value_to_fraction,
    midi_value_to_ms,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.amp import AnalogAmpSection
from jdxi_editor.ui.editors.analog.common import AnalogCommonSection
from jdxi_editor.ui.editors.analog.filter import AnalogFilterSection
from jdxi_editor.ui.editors.analog.lfo import AnalogLFOSection
from jdxi_editor.ui.editors.analog.oscillator import AnalogOscillatorSection
from jdxi_editor.ui.editors.synth.editor import SynthEditor, log_changes
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget


class AnalogSynthEditor(SynthEditor):
    """Analog Synth Editor UI."""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: Optional["JDXiPresetHelper"] = None,  # type: ignore[name-defined]
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the AnalogSynthEditor

        :param midi_helper: MidiIOHelper
        :param preset_helper: JDXIPresetHelper
        :param parent: QWidget
        """
        super().__init__(midi_helper=midi_helper, parent=parent)
        self.instrument_image_group: QGroupBox | None = None
        self.scroll: QScrollArea | None = None
        self.instrument_preset_group: QGroupBox | None = None
        self.instrument_preset: QWidget | None = None
        self.instrument_preset_widget: QWidget | None = None
        self.amp_section: AnalogAmpSection | None = None
        self.oscillator_section: AnalogOscillatorSection | None = None
        self.filter_section: AnalogFilterSection | None = None
        self.tab_widget = None
        self.lfo_section = None
        self.preset_helper = preset_helper
        self.wave_buttons = {}
        self.lfo_shape_buttons = {}
        self.controls: Dict[Union[Analog.Param], QWidget] = {}
        self.updating_from_spinbox = False
        self.previous_json_data = None
        self.main_window = parent
        self.analog = True

        # --- Initialize mappings as empty dicts/lists early to prevent AttributeError
        # --- These will be populated after sections are created
        self.adsr_mapping = {}
        self.pitch_env_mapping = {}
        self.pwm_mapping = {}

        self._init_parameter_mappings()
        self._init_synth_data(JDXiSynth.ANALOG_SYNTH)
        self.setup_ui()

        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message("MIDI signals connected")
        else:
            log.message("MIDI signals not connected")

        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        # --- Define mapping dictionaries
        self.sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        self.filter_switch_map = {0: 0, 1: 1}
        self.osc_waveform_map = {
            0: Analog.Wave.Osc.SAW,
            1: Analog.Wave.Osc.TRIANGLE,
            2: Analog.Wave.Osc.PULSE,
        }
        self._create_sections()
        self.adsr_mapping = {
            Analog.Param.AMP_ENV_ATTACK_TIME: self.amp_section.adsr_widget.attack_control,
            Analog.Param.AMP_ENV_DECAY_TIME: self.amp_section.adsr_widget.decay_control,
            Analog.Param.AMP_ENV_SUSTAIN_LEVEL: self.amp_section.adsr_widget.sustain_control,
            Analog.Param.AMP_ENV_RELEASE_TIME: self.amp_section.adsr_widget.release_control,
            Analog.Param.FILTER_ENV_ATTACK_TIME: self.filter_section.adsr_widget.attack_control,
            Analog.Param.FILTER_ENV_DECAY_TIME: self.filter_section.adsr_widget.decay_control,
            Analog.Param.FILTER_ENV_SUSTAIN_LEVEL: self.filter_section.adsr_widget.sustain_control,
            Analog.Param.FILTER_ENV_RELEASE_TIME: self.filter_section.adsr_widget.release_control,
        }
        self.pitch_env_mapping = {
            Analog.Param.OSC_PITCH_ENV_ATTACK_TIME: self.oscillator_section.pitch_env_widget.attack_control,
            Analog.Param.OSC_PITCH_ENV_DECAY_TIME: self.oscillator_section.pitch_env_widget.decay_control,
            Analog.Param.OSC_PITCH_ENV_DEPTH: self.oscillator_section.pitch_env_widget.depth_control,
        }
        self.pwm_mapping = {
            Analog.Param.OSC_PULSE_WIDTH: self.oscillator_section.pwm_widget.controls[Analog.Param.OSC_PULSE_WIDTH],
            Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH: self.oscillator_section.pwm_widget.controls[Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH],
        }
        # Note: data_request() is called in showEvent() when editor is displayed

    def setup_ui(self):
        """Set up the Analog Synth Editor UI."""
        self.set_dimensions()
        self.set_style()

        # --- Use EditorBaseWidget for consistent layout structure (harmonized with Digital)
        self.base_widget = EditorBaseWidget(parent=self, analog=self.analog)
        self.base_widget.setup_scrollable_content(spacing=5, margins=(5, 5, 5, 5))

        # --- Add base widget to editor's layout (if editor has a layout)
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

        # --- Store references for backward compatibility
        self.scroll = self.base_widget.get_scroll_area()

        # --- Set up instrument preset widget
        self.instrument_preset = InstrumentPresetWidget(parent=self)
        self.instrument_preset.setup_header_layout()
        self.instrument_preset.setup()

        self.instrument_preset_group = (
            self.instrument_preset.create_instrument_preset_group()
        )
        self.instrument_preset.add_preset_group(self.instrument_preset_group)
        self.instrument_preset.add_stretch()

        (
            self.instrument_image_group,
            self.instrument_image_label,
            self.instrument_group_layout,
        ) = self.instrument_preset.create_instrument_image_group()
        self.instrument_preset.add_image_group(self.instrument_image_group)
        self.instrument_preset.add_stretch()
        self.update_instrument_image()
        self.build_widgets()

    def set_style(self):
        """Set style"""
        JDXi.UI.Theme.apply_tabs_style(self, analog=self.analog)
        JDXi.UI.Theme.apply_editor_style(self, analog=self.analog)

    def set_dimensions(self):
        """set dimensions"""
        self.setMinimumSize(
            JDXi.UI.Dimensions.EDITOR_ANALOG.MIN_WIDTH,
            JDXi.UI.Dimensions.EDITOR_ANALOG.MIN_HEIGHT,
        )
        self.resize(
            JDXi.UI.Dimensions.EDITOR_ANALOG.WIDTH,
            JDXi.UI.Dimensions.EDITOR_ANALOG.HEIGHT,
        )

    def build_widgets(self):
        """Create widgets"""
        self.tab_widget = self.base_widget.create_tab_widget()
        self._configure_sliders()

    def _configure_sliders(self):
        """Configure sliders"""
        for slider in self.controls.values():
            if isinstance(slider, QSlider):
                slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
                slider.setTickInterval(10)

    def _create_sections(self):
        """Create the sections for the Analog Synth Editor."""
        self.oscillator_section = AnalogOscillatorSection(
            waveform_selected_callback=self._on_waveform_selected,
            wave_buttons=self.wave_buttons,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.address,
        )
        self.filter_section = AnalogFilterSection(
            controls=self.controls,
            address=self.synth_data.address,
            send_midi_parameter=self.send_midi_parameter,
            midi_helper=self.midi_helper,
            on_filter_mode_changed=self._on_filter_mode_changed,
            parent=self,
        )
        self.amp_section = AnalogAmpSection(
            address=self.synth_data.address,
            controls=self.controls,
            parent=self,
        )
        self.lfo_section = AnalogLFOSection(
            on_lfo_shape_changed=self._on_lfo_shape_changed,
            lfo_shape_buttons=self.lfo_shape_buttons,
            send_midi_parameter=self.send_midi_parameter,
            controls=self.controls,
        )
        self.common_section = AnalogCommonSection(
            controls=self.controls,
        )
        self._add_tab(key=Analog.Tab.PRESETS, widget=self.instrument_preset)
        self._add_tab(key=Analog.Tab.OSCILLATOR, widget=self.oscillator_section)
        self._add_tab(key=Analog.Tab.FILTER, widget=self.filter_section)
        self._add_tab(key=Analog.Tab.AMP, widget=self.amp_section)
        self._add_tab(key=Analog.Tab.LFO, widget=self.lfo_section)
        self._add_tab(key=Analog.Tab.COMMON, widget=self.common_section)

    def _init_parameter_mappings(self):
        """Initialize MIDI parameter mappings."""
        self.cc_parameters = {
            "Cutoff": Analog.ControlChange.CUTOFF,
            "Resonance": Analog.ControlChange.RESONANCE,
            "Level": Analog.ControlChange.LEVEL,
            "LFO Rate": Analog.ControlChange.LFO_RATE,
        }

        self.nrpn_parameters = {
            "Envelope": Analog.RPN.ENVELOPE.value.msb_lsb,  # --- (0, 124),
            "LFO Shape": Analog.RPN.LFO_SHAPE.value.msb_lsb,  # --- (0, 3),
            "LFO Pitch Depth": Analog.RPN.LFO_PITCH_DEPTH.value.msb_lsb,  # --- (0, 15),
            "LFO Filter Depth": Analog.RPN.LFO_FILTER_DEPTH.value.msb_lsb,  # --- (0, 18),
            "LFO Amp Depth": Analog.RPN.LFO_AMP_DEPTH.value.msb_lsb,  # --- (0, 21),
            "Pulse Width": Analog.RPN.PULSE_WIDTH.value.msb_lsb,  # --- (0, 37),
        }

        # --- Reverse lookup map
        self.nrpn_map = {v: k for k, v in self.nrpn_parameters.items()}

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode (0=BYPASS, 1=LPF)."""
        enabled = mode != 0  # --- Enable if not BYPASS
        for param in [
            Analog.Param.FILTER_CUTOFF,
            Analog.Param.FILTER_RESONANCE,
            Analog.Param.FILTER_CUTOFF_KEYFOLLOW,
            Analog.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
            Analog.Param.FILTER_ENV_DEPTH,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
        # --- Enable/disable filter section groups (covers widgets not in self.controls)
        if hasattr(self, "filter_section") and self.filter_section is not None:
            if hasattr(self.filter_section, "filter_controls_group"):
                self.filter_section.controls_group.setEnabled(enabled)
            self.filter_section.adsr_widget.setEnabled(enabled)

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes"""
        self.update_filter_controls_state(mode)

    def update_filter_state(self, value: int):
        """
        Update the filter state

        :param value: int value
        :return: None
        """
        self._update_filter_mode_buttons(value)
        self.update_filter_controls_state(value)

    def _update_filter_mode_buttons(self, value: int):
        """
        Update the filter mode buttons based on the FILTER_MODE_SWITCH value with visual feedback

        :param value: int filter mode value (0 = BYPASS, 1 = LPF)
        :return: None
        """
        filter_mode_map = {
            0: Analog.Filter.FilterType.BYPASS,
            1: Analog.Filter.FilterType.LPF,
        }

        selected_filter_mode = filter_mode_map.get(value)

        if selected_filter_mode is None:
            log.warning("Unknown filter mode value: %s", value)
            return

        # --- Reset all buttons to default style
        for btn in self.filter_section.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect_analog(btn)

        # --- Apply active style to the selected filter mode button
        selected_btn = self.filter_section.filter_mode_buttons.get(selected_filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)
        else:
            log.warning("Filter mode button not found for: %s", selected_filter_mode)

    def _on_waveform_selected(self, waveform: AnalogWaveOsc):
        """
        Handle waveform button selection

        :param waveform: AnalogOscWave value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=Analog.Param.OSC_WAVEFORM,
                value=waveform.value,
            )
            self.midi_helper.send_midi_message(sysex_message)

        # --- Use oscillator_section.waveform_buttons if available, fallback to wave_buttons
        buttons_dict = self.wave_buttons
        if self.oscillator_section and hasattr(self.oscillator_section, 'waveform_buttons'):
            buttons_dict = self.oscillator_section.waveform_buttons
            # --- Also sync to editor's wave_buttons for consistency
            self.wave_buttons.update(buttons_dict)

        # --- Reset all buttons to default style
        for btn in buttons_dict.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect_analog(btn)

        # --- Apply active style to the selected waveform button
        selected_btn = buttons_dict.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)
        self._update_pw_controls_state(waveform)

    def get_controls_as_dict(self):
        """
        Get the current values of self.controls as a dictionary.
        Override to handle waveform buttons and filter mode buttons specially.

        :returns: dict A dictionary of control parameter names and their values.
        """
        # --- Get base controls
        controls_data = super().get_controls_as_dict()

        # --- Handle OSC_WAVEFORM specially - find which waveform button is checked
        if Analog.Param.OSC_WAVEFORM in self.controls:
            # --- Check which waveform button is currently checked
            for waveform, btn in self.wave_buttons.items():
                if btn.isChecked():
                    controls_data[Analog.Param.OSC_WAVEFORM.name] = waveform.STATUS
                    break
            # --- If no button is checked, use default (SAW = 0)
            if Analog.Param.OSC_WAVEFORM.name not in controls_data:
                controls_data[Analog.Param.OSC_WAVEFORM.name] = (
                    Analog.Wave.Osc.SAW.value
                )

        # --- Handle FILTER_MODE_SWITCH specially - find which filter mode button is checked
        if hasattr(self, "filter_section") and hasattr(
            self.filter_section, "filter_mode_buttons"
        ):
            # --- Check which filter mode button is currently checked
            for filter_mode, btn in self.filter_section.filter_mode_buttons.items():
                if btn.isChecked():
                    controls_data[Analog.Param.FILTER_MODE_SWITCH.name] = (
                        filter_mode.value
                    )
                    break
            # --- If no button is checked, use default (BYPASS = 0)
            if Analog.Param.FILTER_MODE_SWITCH.name not in controls_data:
                controls_data[Analog.Param.FILTER_MODE_SWITCH.name] = (
                    Analog.Filter.FilterType.BYPASS.value
                )

        return controls_data

    def _on_lfo_shape_changed(self, value: int):
        """
        Handle LFO shape change

        :param value: int value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address, param=Analog.Param.LFO_SHAPE, value=value
            )
            self.midi_helper.send_midi_message(sysex_message)
            # --- Reset all buttons to default style ---
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                JDXi.UI.Theme.apply_button_rect_analog(btn)

            # --- Apply active style to the selected button ---
            selected_btn = self.lfo_shape_buttons.get(value)
            if selected_btn:
                selected_btn.setChecked(True)
                JDXi.UI.Theme.apply_button_analog_active(selected_btn)

    def update_slider(
        self,
        param: AnalogParam,
        midi_value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Helper function to update sliders safely.

        :param param: AddressParameterAnalog value
        :param failures: list of failed parameters
        :param successes: list of successful parameters
        :param midi_value: int value
        :return: None
        """
        slider = self.controls.get(param)
        if slider:
            slider_value = param.convert_from_midi(midi_value)
            slider.blockSignals(True)
            slider.setValue(slider_value)
            slider.blockSignals(False)
            successes.append(param.name)
            log_slider_parameters(self.address, param, midi_value, slider_value)
        else:
            failures.append(param.name)

    def update_adsr_widget(
        self,
        param: AnalogParam,
        midi_value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Helper function to update ADSR widgets.

        :param param: AddressParameterAnalog value
        :param midi_value: int value
        :param failures: list of failed parameters
        :param successes: list of successful parameters
        :return: None
        """
        slider_value = (
            midi_value_to_fraction(midi_value)
            if param
            in [
                Analog.Param.AMP_ENV_SUSTAIN_LEVEL,
                Analog.Param.FILTER_ENV_SUSTAIN_LEVEL,
            ]
            else midi_value_to_ms(midi_value)
        )

        if param in self.adsr_mapping:
            control = self.adsr_mapping[param]
            control.blockSignals(True)
            control.setValue(slider_value)
            control.blockSignals(False)
            successes.append(param.name)
            log_slider_parameters(self.address, param, midi_value, slider_value)
        else:
            failures.append(param.name)

    def update_pitch_env_widget(
        self,
        parameter: AnalogParam,
        value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Helper function to update ADSR widgets.

        :param parameter: AddressParameterAnalog value
        :param value: int value
        :param failures: list of failed parameters
        :param successes: list of successful parameters
        :return: None
        """
        new_value = (
            midi_value_to_fraction(value)
            if parameter
            in [
                Analog.Param.OSC_PITCH_ENV_DEPTH,
            ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pitch_env_mapping:
            control = self.pitch_env_mapping[parameter]
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)
            successes.append(parameter.name)
        else:
            failures.append(parameter.name)

    def update_pwm_widget(
        self,
        parameter: AnalogParam,
        value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Helper function to update PWM widgets.

        :param parameter: AddressParameterAnalog value
        :param value: int value
        :param failures: list of failed parameters
        :param successes: list of successful parameters
        :return: None
        """
        new_value = (
            midi_value_to_fraction(value)
            if parameter
            in [
                Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
                Analog.Param.OSC_PULSE_WIDTH,
            ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pwm_mapping:
            control = self.pwm_mapping[parameter]
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)
            successes.append(parameter.name)
        else:
            failures.append(parameter.name)

    def _update_controls(
        self, partial_no: int, sysex_data: dict, successes: list, failures: list
    ) -> None:
        """
        Update sliders and combo boxes based on parsed SysEx data.

        :param sysex_data: dict SysEx data
        :param successes: list SysEx data
        :param failures: list SysEx data
        :return: None
        """

        # --- Compare with previous data and log changes
        if self.previous_json_data:
            log_changes(self.previous_json_data, sysex_data)

        # --- Store the current data for future comparison
        self.previous_json_data = sysex_data

        for param_name, param_value in sysex_data.items():
            param = Analog.Param.get_by_name(param_name)

            if param:
                if (
                    param_name == "SUB_OSCILLATOR_TYPE"
                    and param_value in self.sub_osc_type_map
                ):
                    self.oscillator_section.sub_oscillator_type_switch.blockSignals(
                        True
                    )
                    self.oscillator_section.sub_oscillator_type_switch.setValue(
                        self.sub_osc_type_map[param_value]
                    )
                    self.oscillator_section.sub_oscillator_type_switch.blockSignals(
                        False
                    )
                elif (
                    param_name == "OSC_WAVEFORM"
                    and param_value in self.osc_waveform_map
                ):
                    self._update_waveform_buttons(param_value)
                elif (
                    param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons
                ):
                    self._update_lfo_shape_buttons(param_value)
                elif param_name == "LFO_TEMPO_SYNC_SWITCH":
                    control = self.controls.get(Analog.Param.LFO_TEMPO_SYNC_SWITCH)
                    if control:
                        control.setValue(param_value)
                        successes.append(param_name)
                    else:
                        failures.append(param_name)
                elif param_name == "LFO_TEMPO_SYNC_NOTE":
                    control = self.controls.get(Analog.Param.LFO_TEMPO_SYNC_NOTE)
                    if control:
                        control.setValue(param_value)
                        successes.append(param_name)
                    else:
                        failures.append(param_name)
                elif param == Analog.Param.FILTER_MODE_SWITCH:
                    self._update_filter_mode_buttons(param_value)
                    self.update_filter_controls_state(bool(param_value))
                elif param in [
                    Analog.Param.AMP_ENV_ATTACK_TIME,
                    Analog.Param.AMP_ENV_DECAY_TIME,
                    Analog.Param.AMP_ENV_SUSTAIN_LEVEL,
                    Analog.Param.AMP_ENV_RELEASE_TIME,
                    Analog.Param.FILTER_ENV_ATTACK_TIME,
                    Analog.Param.FILTER_ENV_DECAY_TIME,
                    Analog.Param.FILTER_ENV_SUSTAIN_LEVEL,
                    Analog.Param.FILTER_ENV_RELEASE_TIME,
                ]:
                    self.update_adsr_widget(param, param_value, successes, failures)
                elif param in self.pitch_env_mapping:
                    self.update_pitch_env_widget(
                        param, param_value, successes, failures
                    )
                elif param == Analog.Param.OSC_WAVEFORM:
                    self._update_waveform_buttons(param_value)
                else:
                    self.update_slider(param, param_value, successes, failures)
                successes.append(param_name)
            else:
                failures.append(param_name)

    def _update_waveform_buttons(self, value: int):
        """
        Update the waveform buttons based on the OSC_WAVE value with visual feedback.

        :param value: int value
        :return: None
        """
        waveform_map = {
            0: Analog.Wave.Osc.SAW,
            1: Analog.Wave.Osc.TRIANGLE,
            2: Analog.Wave.Osc.PULSE,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            log.message(f"Unknown waveform value: {value}", level=logging.WARNING)
            return

        log.message(f"Waveform value {value} found, selecting {selected_waveform}")

        # --- Retrieve waveform buttons for the given partial
        wave_buttons = self.wave_buttons

        # --- Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect_analog(btn)

        # --- Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)

    def _update_lfo_shape_buttons(self, value: int):
        """
        Update the LFO shape buttons with visual feedback.

        :param value: int value
        :return: None
        """
        # --- Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect_analog(btn)

        # --- Apply active style to the selected button
        selected_btn = self.lfo_shape_buttons.get(value)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)
        else:
            log.message(f"Unknown LFO shape value: {value}", level=logging.WARNING)

    def _update_pw_controls_state(self, waveform: AnalogWaveOsc):
        """
        Enable/disable PW controls based on waveform

        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == AnalogWaveOsc.PULSE
        log.message(f"Waveform: {waveform} Pulse Width enabled: {pw_enabled}")
        # --- Access PWM controls from oscillator_section.pwm_widget.controls
        if self.oscillator_section and self.oscillator_section.pwm_widget:
            pwm_controls = self.oscillator_section.pwm_widget.controls
            if Analog.Param.OSC_PULSE_WIDTH in pwm_controls:
                pwm_controls[Analog.Param.OSC_PULSE_WIDTH].setEnabled(pw_enabled)
            if Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH in pwm_controls:
                pwm_controls[Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH].setEnabled(pw_enabled)
            
            # --- Update the visual state (if controls are sliders)
            if Analog.Param.OSC_PULSE_WIDTH in pwm_controls:
                control = pwm_controls[Analog.Param.OSC_PULSE_WIDTH]
                if hasattr(control, 'setStyleSheet'):
                    control.setStyleSheet(
                        "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
                    )
            if Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH in pwm_controls:
                control = pwm_controls[Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH]
                if hasattr(control, 'setStyleSheet'):
                    control.setStyleSheet(
                        "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
                    )
