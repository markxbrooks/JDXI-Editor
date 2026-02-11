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
from typing import TYPE_CHECKING, Optional

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
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
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.amp.section import AnalogAmpSection
from jdxi_editor.ui.editors.analog.filter.section import AnalogFilterSection
from jdxi_editor.ui.editors.analog.oscillator.section import AnalogOscillatorSection
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.editors.synth.helper import log_changes
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget


class BaseSynthEditor(SynthEditor):
    """Base Synth Editor UI."""

    SUB_OSC_TYPE_MAP = {}

    SYNTH_SPEC = Analog

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: Optional["JDXiPresetHelper"] = None,  # type: ignore[name-defined]
        parent: Optional["QWidget"] = None,  # type: ignore[name-defined]
    ):
        """
        Initialize the AnalogSynthEditor

        :param midi_helper: MidiIOHelper
        :param preset_helper: JDXIPresetHelper
        """
        super().__init__(midi_helper=midi_helper)
        self.osc_waveform_map = None
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
        self.updating_from_spinbox = False
        self.previous_json_data = None
        self.main_window = parent
        self.analog = True

        # --- Initialize mappings as empty dicts/lists early to prevent AttributeError
        # --- These will be populated after sections are created
        self.adsr_mapping = {}
        self.pitch_env_mapping = {}
        self.pwm_mapping = {}

        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            log.message(scope="BaseSynthEditor", message="MIDI signals connected")
        else:
            log.message(scope="BaseSynthEditor", message="MIDI signals not connected")

        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

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
        if not self.analog:
            JDXi.UI.Theme.apply_tabs_style(self.tab_widget)
            JDXi.UI.Theme.apply_editor_style(self.tab_widget)

    def set_dimensions(self):
        """set dimensions"""
        if self.analog:
            self.setMinimumSize(
                JDXi.UI.Dimensions.EDITOR_ANALOG.MIN_WIDTH,
                JDXi.UI.Dimensions.EDITOR_ANALOG.MIN_HEIGHT,
            )
            self.resize(
                JDXi.UI.Dimensions.EDITOR_ANALOG.WIDTH,
                JDXi.UI.Dimensions.EDITOR_ANALOG.HEIGHT,
            )
        else:
            self.setMinimumSize(
                JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_WIDTH,
                JDXi.UI.Dimensions.EDITOR_DIGITAL.MIN_HEIGHT,
            )
            self.resize(
                JDXi.UI.Dimensions.EDITOR_DIGITAL.INIT_WIDTH,
                JDXi.UI.Dimensions.EDITOR_DIGITAL.INIT_HEIGHT,
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

    def add_tabs(self):
        """Add tabs to tab widget. Only adds a tab when the section exists."""
        self._add_tab(key=self.SYNTH_SPEC.Tab.PRESETS, widget=self.instrument_preset)
        if getattr(self, "oscillator_section", None) is not None:
            self._add_tab(
                key=self.SYNTH_SPEC.Tab.OSCILLATOR, widget=self.oscillator_section
            )
        if getattr(self, "filter_section", None) is not None:
            self._add_tab(key=self.SYNTH_SPEC.Tab.FILTER, widget=self.filter_section)
        if getattr(self, "amp_section", None) is not None:
            self._add_tab(key=self.SYNTH_SPEC.Tab.AMP, widget=self.amp_section)
        if getattr(self, "lfo_section", None) is not None:
            self._add_tab(key=self.SYNTH_SPEC.Tab.LFO, widget=self.lfo_section)
        if getattr(self, "common_section", None) is not None:
            self._add_tab(key=self.SYNTH_SPEC.Tab.COMMON, widget=self.common_section)

    def _init_parameter_mappings(self):
        """Initialize MIDI parameter mappings."""
        self.cc_parameters = {
            "Cutoff": self.SYNTH_SPEC.ControlChange.CUTOFF,
            "Resonance": self.SYNTH_SPEC.ControlChange.RESONANCE,
            "Level": self.SYNTH_SPEC.ControlChange.LEVEL,
            "LFO Rate": self.SYNTH_SPEC.ControlChange.LFO_RATE,
        }

        self.nrpn_parameters = {
            "Envelope": self.SYNTH_SPEC.RPN.ENVELOPE.value.msb_lsb,  # --- (0, 124),
            "LFO Shape": self.SYNTH_SPEC.RPN.LFO_SHAPE.value.msb_lsb,  # --- (0, 3),
            "LFO Pitch Depth": self.SYNTH_SPEC.RPN.LFO_PITCH_DEPTH.value.msb_lsb,  # --- (0, 15),
            "LFO Filter Depth": self.SYNTH_SPEC.RPN.LFO_FILTER_DEPTH.value.msb_lsb,  # --- (0, 18),
            "LFO Amp Depth": self.SYNTH_SPEC.RPN.LFO_AMP_DEPTH.value.msb_lsb,  # --- (0, 21),
            "Pulse Width": self.SYNTH_SPEC.RPN.PULSE_WIDTH.value.msb_lsb,  # --- (0, 37),
        }

        # --- Reverse lookup map
        self.nrpn_map = {v: k for k, v in self.nrpn_parameters.items()}

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state (delegate to section, same mechanism as Digital)."""
        log.message(
            scope="BaseSynthEditor",
            message=f"update_filter_controls_state: mode={mode} "
            f"has filter_section={hasattr(self, 'filter_section')} "
            f"filter_section is not None={getattr(self, 'filter_section', None) is not None}",
        )
        if hasattr(self, "filter_section") and self.filter_section is not None:
            self.filter_section.update_controls_state(mode)
        else:
            log.warning(
                scope="BaseSynthEditor",
                message="update_filter_controls_state: no filter_section, skipping",
            )

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes (callback from filter section when mode button clicked)."""
        log.message(
            scope="BaseSynthEditor", message=f"_on_filter_mode_changed: mode={mode}"
        )
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
            0: self.SYNTH_SPEC.Filter.FilterType.BYPASS,
            1: self.SYNTH_SPEC.Filter.FilterType.LPF,
        }

        selected_filter_mode = filter_mode_map.get(value)

        if selected_filter_mode is None:
            log.warning("Unknown filter mode value: %s", value, scope="BaseSynthEditor")
            return

        # --- Reset all buttons to default style
        for btn in self.filter_section.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

        # --- Apply active style to the selected filter mode button
        selected_btn = self.filter_section.filter_mode_buttons.get(selected_filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)
        else:
            log.warning(
                "Filter mode button not found for: %s",
                selected_filter_mode,
                scope=self.__class__.__name__,
            )

    def _on_waveform_selected(self, waveform: AnalogWaveOsc):
        """
        Handle waveform button selection

        :param waveform: AnalogOscWave value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=self.SYNTH_SPEC.Param.OSC_WAVEFORM,
                value=waveform.value,
            )
            self.midi_helper.send_midi_message(sysex_message)

        # --- Use oscillator_section.waveform_buttons if available, fallback to wave_buttons
        buttons_dict = self.wave_buttons
        if self.oscillator_section and hasattr(
            self.oscillator_section, "waveform_buttons"
        ):
            buttons_dict = self.oscillator_section.waveform_buttons
            # --- Also sync to editor's wave_buttons for consistency
            self.wave_buttons.update(buttons_dict)

        # --- Reset all buttons to default style
        for btn in buttons_dict.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

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
        if self.SYNTH_SPEC.Param.OSC_WAVEFORM in self.controls:
            # --- Check which waveform button is currently checked
            for waveform, btn in self.wave_buttons.items():
                if btn.isChecked():
                    controls_data[self.SYNTH_SPEC.Param.OSC_WAVEFORM.name] = (
                        waveform.STATUS
                    )
                    break
            # --- If no button is checked, use default (SAW = 0)
            if self.SYNTH_SPEC.Param.OSC_WAVEFORM.name not in controls_data:
                controls_data[self.SYNTH_SPEC.Param.OSC_WAVEFORM.name] = (
                    self.SYNTH_SPEC.Wave.Osc.SAW.value
                )

        # --- Handle FILTER_MODE_SWITCH specially - find which filter mode button is checked
        if hasattr(self, "filter_section") and hasattr(
            self.filter_section, "filter_mode_buttons"
        ):
            # --- Check which filter mode button is currently checked
            for filter_mode, btn in self.filter_section.filter_mode_buttons.items():
                if btn.isChecked():
                    controls_data[self.SYNTH_SPEC.Param.FILTER_MODE_SWITCH.name] = (
                        filter_mode.value
                    )
                    break
            # --- If no button is checked, use default (BYPASS = 0)
            if self.SYNTH_SPEC.Param.FILTER_MODE_SWITCH.name not in controls_data:
                controls_data[self.SYNTH_SPEC.Param.FILTER_MODE_SWITCH.name] = (
                    self.SYNTH_SPEC.Filter.FilterType.BYPASS.value
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
                address=self.address, param=self.SYNTH_SPEC.Param.LFO_SHAPE, value=value
            )
            self.midi_helper.send_midi_message(sysex_message)
            # --- Reset all buttons to default style ---
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

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
                self.SYNTH_SPEC.Param.AMP_ENV_SUSTAIN_LEVEL,
                self.SYNTH_SPEC.Param.FILTER_ENV_SUSTAIN_LEVEL,
            ]
            else midi_value_to_ms(midi_value)
        )

        if param in self.adsr_mapping:
            control = self.adsr_mapping[param]
            control.blockSignals(True)
            control.setValue(slider_value)
            control.blockSignals(False)
            # ADSR plot is driven by envelope_changed; refresh after programmatic update
            amp_env = (
                self.SYNTH_SPEC.Param.AMP_ENV_ATTACK_TIME,
                self.SYNTH_SPEC.Param.AMP_ENV_DECAY_TIME,
                self.SYNTH_SPEC.Param.AMP_ENV_SUSTAIN_LEVEL,
                self.SYNTH_SPEC.Param.AMP_ENV_RELEASE_TIME,
            )
            if (
                param in amp_env
                and hasattr(self, "amp_section")
                and self.amp_section
                and getattr(self.amp_section, "adsr_widget", None)
            ):
                self.amp_section.adsr_widget.refresh_plot_from_controls()
            elif (
                param not in amp_env
                and hasattr(self, "filter_section")
                and self.filter_section
                and getattr(self.filter_section, "adsr_widget", None)
            ):
                self.filter_section.adsr_widget.refresh_plot_from_controls()
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
                self.SYNTH_SPEC.Param.OSC_PITCH_ENV_DEPTH,
            ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pitch_env_mapping:
            control = self.pitch_env_mapping[parameter]
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)
            if (
                hasattr(self, "oscillator_section")
                and self.oscillator_section
                and getattr(self.oscillator_section, "pitch_env_widget", None)
            ):
                self.oscillator_section.pitch_env_widget.refresh_plot_from_controls()
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
                self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
                self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH,
            ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pwm_mapping:
            control = self.pwm_mapping[parameter]
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)
            if (
                hasattr(self, "oscillator_section")
                and self.oscillator_section
                and getattr(self.oscillator_section, "pwm_widget", None)
            ):
                self.oscillator_section.pwm_widget.refresh_plot_from_controls()
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
        log.message(scope="BaseSynthEditor", message="[_update_controls]")
        # --- Compare with previous data and log changes
        if self.previous_json_data:
            log_changes(self.previous_json_data, sysex_data)

        # --- Store the current data for future comparison
        self.previous_json_data = sysex_data

        for param_name, param_value in sysex_data.items():
            param = self.SYNTH_SPEC.Param.get_by_name(param_name)

            if param:
                if (
                    param_name == "SUB_OSCILLATOR_TYPE"
                    and param_value in self.SUB_OSC_TYPE_MAP
                    and self.oscillator_section is not None
                    and hasattr(self.oscillator_section, "sub_oscillator_type_switch")
                ):
                    self.oscillator_section.sub_oscillator_type_switch.blockSignals(
                        True
                    )
                    self.oscillator_section.sub_oscillator_type_switch.setValue(
                        self.SUB_OSC_TYPE_MAP[param_value]
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
                    control = self.controls.get(
                        self.SYNTH_SPEC.Param.LFO_TEMPO_SYNC_SWITCH
                    )
                    if control:
                        control.setValue(param_value)
                        successes.append(param_name)
                    else:
                        failures.append(param_name)
                elif param_name == "LFO_TEMPO_SYNC_NOTE":
                    control = self.controls.get(
                        self.SYNTH_SPEC.Param.LFO_TEMPO_SYNC_NOTE
                    )
                    if control:
                        control.setValue(param_value)
                        successes.append(param_name)
                    else:
                        failures.append(param_name)
                elif param == self.SYNTH_SPEC.Param.FILTER_MODE_SWITCH:
                    mode_int = (
                        int(param_value)
                        if isinstance(param_value, (int, float))
                        else getattr(param_value, "value", 0)
                    )
                    if not isinstance(mode_int, int):
                        mode_int = 0
                    self._update_filter_mode_buttons(mode_int)
                    self.update_filter_controls_state(mode_int)
                elif param in [
                    self.SYNTH_SPEC.Param.AMP_ENV_ATTACK_TIME,
                    self.SYNTH_SPEC.Param.AMP_ENV_DECAY_TIME,
                    self.SYNTH_SPEC.Param.AMP_ENV_SUSTAIN_LEVEL,
                    self.SYNTH_SPEC.Param.AMP_ENV_RELEASE_TIME,
                    self.SYNTH_SPEC.Param.FILTER_ENV_ATTACK_TIME,
                    self.SYNTH_SPEC.Param.FILTER_ENV_DECAY_TIME,
                    self.SYNTH_SPEC.Param.FILTER_ENV_SUSTAIN_LEVEL,
                    self.SYNTH_SPEC.Param.FILTER_ENV_RELEASE_TIME,
                ]:
                    self.update_adsr_widget(param, param_value, successes, failures)
                elif param in self.pitch_env_mapping:
                    self.update_pitch_env_widget(
                        param, param_value, successes, failures
                    )
                elif param == self.SYNTH_SPEC.Param.OSC_WAVEFORM:
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
            0: self.SYNTH_SPEC.Wave.Osc.SAW,
            1: self.SYNTH_SPEC.Wave.Osc.TRI,
            2: self.SYNTH_SPEC.Wave.Osc.SQUARE,
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
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

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
            JDXi.UI.Theme.apply_button_rect(btn, analog=self.analog)

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
        pw_enabled = waveform == AnalogWaveOsc.SQUARE
        log.message(f"Waveform: {waveform} Pulse Width enabled: {pw_enabled}")
        # --- Access PWM controls from oscillator_section.pwm_widget.controls
        if self.oscillator_section and self.oscillator_section.pwm_widget:
            pwm_controls = self.oscillator_section.pwm_widget.controls
            if self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH in pwm_controls:
                pwm_controls[self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH].setEnabled(
                    pw_enabled
                )
            if self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH_MOD_DEPTH in pwm_controls:
                pwm_controls[
                    self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH_MOD_DEPTH
                ].setEnabled(pw_enabled)

            # --- Update the visual state (if controls are sliders)
            if self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH in pwm_controls:
                control = pwm_controls[self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH]
                if hasattr(control, "setStyleSheet"):
                    control.setStyleSheet(
                        ""
                        if pw_enabled
                        else "QSlider::groove:vertical { background: #000000; }"
                    )
            if self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH_MOD_DEPTH in pwm_controls:
                control = pwm_controls[self.SYNTH_SPEC.Param.OSC_PULSE_WIDTH_MOD_DEPTH]
                if hasattr(control, "setStyleSheet"):
                    control.setStyleSheet(
                        ""
                        if pw_enabled
                        else "QSlider::groove:vertical { background: #000000; }"
                    )
