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
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

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
from typing import Dict, Optional, Union

import qtawesome as qta
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.jdxi.preset.helper import create_scroll_container
from jdxi_editor.jdxi.preset.widget import InstrumentPresetWidget
from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.analog.oscillator import AnalogOscWave
from jdxi_editor.midi.data.control_change.analog import AnalogControlChange, AnalogRPN
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.amp import AnalogAmpSection
from jdxi_editor.ui.editors.analog.common import AnalogCommonSection
from jdxi_editor.ui.editors.analog.filter import AnalogFilterSection
from jdxi_editor.ui.editors.analog.lfo import AnalogLFOSection
from jdxi_editor.ui.editors.analog.oscillator import AnalogOscillatorSection
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.ui.editors.synth.editor import SynthEditor, log_changes
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions
from picomidi.utils.conversion import (
    midi_value_to_fraction,
    midi_value_to_ms,
)


class AnalogSynthEditor(SynthEditor):
    """Analog Synth Editor UI."""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: Optional["JDXiPresetHelper"] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the AnalogSynthEditor

        :param midi_helper: MidiIOHelper
        :param preset_helper: JDXIPresetHelper
        :param parent: QWidget
        """
        super().__init__(midi_helper, parent)
        self.instrument_image_group: QGroupBox | None = None
        self.scroll: QScrollArea | None = None
        self.instrument_preset_group: QGroupBox | None = None
        self.instrument_preset_layout: QVBoxLayout | None = None
        self.instrument_preset: QWidget | None = None
        self.instrument_preset_widget: QWidget | None = None
        self.instrument_preset_hlayout: QHBoxLayout | None = None
        self.amp_section: AnalogAmpSection | None = None
        self.oscillator_section: AnalogOscillatorSection | None = None
        self.filter_section: AnalogFilterSection | None = None
        self.read_request_button = None
        self.tab_widget = None
        self.lfo_section = None
        self.instrument_selection_label = None
        self.instrument_title_label = None
        self.preset_helper = preset_helper
        self.wave_buttons = {}
        self.lfo_shape_buttons = {}
        self.controls: Dict[Union[AnalogParam], QWidget] = {}
        self.updating_from_spinbox = False
        self.previous_json_data = None
        self.main_window = parent

        # Initialize mappings as empty dicts/lists early to prevent AttributeError
        # These will be populated after sections are created
        self.adsr_mapping = {}
        self.pitch_env_mapping = {}
        self.pwm_mapping = []

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

        # Define mapping dictionaries
        self.sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        self.filter_switch_map = {0: 0, 1: 1}
        self.osc_waveform_map = {
            0: AnalogOscWave.SAW,
            1: AnalogOscWave.TRIANGLE,
            2: AnalogOscWave.PULSE,
        }
        self._create_sections()
        self.adsr_mapping = {
            AnalogParam.AMP_ENV_ATTACK_TIME: self.amp_section.amp_env_adsr_widget.attack_control,
            AnalogParam.AMP_ENV_DECAY_TIME: self.amp_section.amp_env_adsr_widget.decay_control,
            AnalogParam.AMP_ENV_SUSTAIN_LEVEL: self.amp_section.amp_env_adsr_widget.sustain_control,
            AnalogParam.AMP_ENV_RELEASE_TIME: self.amp_section.amp_env_adsr_widget.release_control,
            AnalogParam.FILTER_ENV_ATTACK_TIME: self.filter_section.filter_adsr_widget.attack_control,
            AnalogParam.FILTER_ENV_DECAY_TIME: self.filter_section.filter_adsr_widget.decay_control,
            AnalogParam.FILTER_ENV_SUSTAIN_LEVEL: self.filter_section.filter_adsr_widget.sustain_control,
            AnalogParam.FILTER_ENV_RELEASE_TIME: self.filter_section.filter_adsr_widget.release_control,
        }
        self.pitch_env_mapping = {
            AnalogParam.OSC_PITCH_ENV_ATTACK_TIME: self.oscillator_section.pitch_env_widget.attack_control,
            AnalogParam.OSC_PITCH_ENV_DECAY_TIME: self.oscillator_section.pitch_env_widget.decay_control,
            AnalogParam.OSC_PITCH_ENV_DEPTH: self.oscillator_section.pitch_env_widget.depth_control,
        }
        self.pwm_mapping = [
            AnalogParam.OSC_PULSE_WIDTH,
            AnalogParam.OSC_PULSE_WIDTH_MOD_DEPTH,
        ]
        self.data_request()

    def setup_ui(self):
        """Set up the Analog Synth Editor UI."""
        self.setMinimumSize(
            JDXiDimensions.EDITOR_ANALOG_MIN_WIDTH,
            JDXiDimensions.EDITOR_ANALOG_MIN_HEIGHT,
        )
        self.resize(
            JDXiDimensions.EDITOR_ANALOG_WIDTH, JDXiDimensions.EDITOR_ANALOG_HEIGHT
        )
        JDXiThemeManager.apply_tabs_style(self, analog=True)
        JDXiThemeManager.apply_editor_style(self, analog=True)

        # Use EditorBaseWidget for consistent layout structure (harmonized with Digital)
        self.base_widget = EditorBaseWidget(parent=self, analog=True)
        self.base_widget.setup_scrollable_content(spacing=5, margins=(5, 5, 5, 5))

        # Add base widget to editor's layout (if editor has a layout)
        if not hasattr(self, "main_layout") or self.main_layout is None:
            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
        self.main_layout.addWidget(self.base_widget)

        # Store references for backward compatibility
        self.scroll = self.base_widget.get_scroll_area()

        # Set up instrument preset widget
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

        # Create tab widget and add preset as first tab
        self.tab_widget = self.base_widget.create_tab_widget()
        try:
            presets_icon = IconRegistry.get_icon(
                IconRegistry.MUSIC_NOTE_MULTIPLE, color=JDXiStyle.GREY
            )
            if presets_icon is None or presets_icon.isNull():
                raise ValueError("Icon is null")
        except:
            presets_icon = IconRegistry.get_icon(
                IconRegistry.MUSIC, color=JDXiStyle.GREY
            )
        self.tab_widget.addTab(self.instrument_preset, presets_icon, "Presets")

        # --- Configure sliders
        for slider in self.controls.values():
            if isinstance(slider, QSlider):
                slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
                slider.setTickInterval(10)

    def _create_sections(self):
        """Create the sections for the Analog Synth Editor."""
        self.oscillator_section = AnalogOscillatorSection(
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            waveform_selected_callback=self._on_waveform_selected,
            wave_buttons=self.wave_buttons,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.address,
        )
        self.tab_widget.addTab(
            self.oscillator_section,
            IconRegistry.get_icon(IconRegistry.TRIANGLE_WAVE, color=JDXiStyle.GREY),
            "Oscillator",
        )
        self.filter_section = AnalogFilterSection(
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            on_filter_mode_changed=self._on_filter_mode_changed,
            send_control_change=self.send_control_change,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.synth_data.address,
        )
        self.tab_widget.addTab(
            self.filter_section,
            IconRegistry.get_icon(IconRegistry.FILTER, color=JDXiStyle.GREY),
            "Filter",
        )
        self.amp_section = AnalogAmpSection(
            midi_helper=self.midi_helper,
            address=self.synth_data.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
        )
        self.tab_widget.addTab(
            self.amp_section,
            IconRegistry.get_icon(IconRegistry.AMPLIFIER, color=JDXiStyle.GREY),
            "Amp",
        )
        self.lfo_section = AnalogLFOSection(
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            create_parameter_combo_box=self._create_parameter_combo_box,
            on_lfo_shape_changed=self._on_lfo_shape_changed,
            lfo_shape_buttons=self.lfo_shape_buttons,
        )
        self.tab_widget.addTab(
            self.lfo_section,
            IconRegistry.get_icon(IconRegistry.SINE_WAVE, color=JDXiStyle.GREY),
            "LFO",
        )
        self.common_section = AnalogCommonSection(
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            create_parameter_combo_box=self._create_parameter_combo_box,
            controls=self.controls,
        )
        common_icon = IconRegistry.get_icon("mdi.cog-outline", color=JDXiStyle.GREY)
        self.tab_widget.addTab(self.common_section, common_icon, "Common")

    def _init_parameter_mappings(self):
        """Initialize MIDI parameter mappings."""
        self.cc_parameters = {
            "Cutoff": AnalogControlChange.CUTOFF,
            "Resonance": AnalogControlChange.RESONANCE,
            "Level": AnalogControlChange.LEVEL,
            "LFO Rate": AnalogControlChange.LFO_RATE,
        }

        self.nrpn_parameters = {
            "Envelope": AnalogRPN.ENVELOPE.value.msb_lsb,  # (0, 124),
            "LFO Shape": AnalogRPN.LFO_SHAPE.value.msb_lsb,  # (0, 3),
            "LFO Pitch Depth": AnalogRPN.LFO_PITCH_DEPTH.value.msb_lsb,  # (0, 15),
            "LFO Filter Depth": AnalogRPN.LFO_FILTER_DEPTH.value.msb_lsb,  # (0, 18),
            "LFO Amp Depth": AnalogRPN.LFO_AMP_DEPTH.value.msb_lsb,  # (0, 21),
            "Pulse Width": AnalogRPN.PULSE_WIDTH.value.msb_lsb,  # (0, 37),
        }

        # Reverse lookup map
        self.nrpn_map = {v: k for k, v in self.nrpn_parameters.items()}

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            AnalogParam.FILTER_CUTOFF,
            AnalogParam.FILTER_RESONANCE,
            AnalogParam.FILTER_CUTOFF_KEYFOLLOW,
            AnalogParam.FILTER_ENV_VELOCITY_SENSITIVITY,
            AnalogParam.FILTER_ENV_DEPTH,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
        self.filter_section.filter_adsr_widget.setEnabled(enabled)

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
        from jdxi_editor.midi.data.analog.filter import AnalogFilterType

        filter_mode_map = {
            0: AnalogFilterType.BYPASS,
            1: AnalogFilterType.LPF,
        }

        selected_filter_mode = filter_mode_map.get(value)

        if selected_filter_mode is None:
            log.warning("Unknown filter mode value: %s", value)
            return

        # Reset all buttons to default style
        for btn in self.filter_section.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXiThemeManager.apply_button_rect_analog(btn)

        # Apply active style to the selected filter mode button
        selected_btn = self.filter_section.filter_mode_buttons.get(selected_filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXiThemeManager.apply_button_analog_active(selected_btn)
        else:
            log.warning("Filter mode button not found for: %s", selected_filter_mode)

    def _on_waveform_selected(self, waveform: AnalogOscWave):
        """
        Handle waveform button selection

        :param waveform: AnalogOscWave value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=AnalogParam.OSC_WAVEFORM,
                value=waveform.value,
            )
            self.midi_helper.send_midi_message(sysex_message)

            for btn in self.wave_buttons.values():
                btn.setChecked(False)
                JDXiThemeManager.apply_button_rect_analog(btn)

            # --- Apply active style to the selected waveform button
            selected_btn = self.wave_buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                JDXiThemeManager.apply_button_analog_active(selected_btn)
            self._update_pw_controls_state(waveform)

    def get_controls_as_dict(self):
        """
        Get the current values of self.controls as a dictionary.
        Override to handle waveform buttons specially.

        :returns: dict A dictionary of control parameter names and their values.
        """
        # --- Get base controls
        controls_data = super().get_controls_as_dict()

        # --- Handle OSC_WAVEFORM specially - find which waveform button is checked
        if AnalogParam.OSC_WAVEFORM in self.controls:
            # --- Check which waveform button is currently checked
            for waveform, btn in self.wave_buttons.items():
                if btn.isChecked():
                    controls_data[AnalogParam.OSC_WAVEFORM.name] = waveform.STATUS
                    break
            # --- If no button is checked, use default (SAW = 0)
            if AnalogParam.OSC_WAVEFORM.name not in controls_data:
                controls_data[AnalogParam.OSC_WAVEFORM.name] = AnalogOscWave.SAW.value

        return controls_data

    def _on_lfo_shape_changed(self, value: int):
        """
        Handle LFO shape change

        :param value: int value
        :return: None
        """
        if self.midi_helper:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address, param=AnalogParam.LFO_SHAPE, value=value
            )
            self.midi_helper.send_midi_message(sysex_message)
            # --- Reset all buttons to default style ---
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                JDXiThemeManager.apply_button_rect_analog(btn)

            # --- Apply active style to the selected button ---
            selected_btn = self.lfo_shape_buttons.get(value)
            if selected_btn:
                selected_btn.setChecked(True)
                JDXiThemeManager.apply_button_analog_active(selected_btn)

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
                AnalogParam.AMP_ENV_SUSTAIN_LEVEL,
                AnalogParam.FILTER_ENV_SUSTAIN_LEVEL,
            ]
            else midi_value_to_ms(midi_value)
        )

        if param in self.adsr_mapping:
            control = self.adsr_mapping[param]
            control.setValue(slider_value)
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
                AnalogParam.OSC_PITCH_ENV_DEPTH,
            ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pitch_env_mapping:
            control = self.pitch_env_mapping[parameter]
            control.setValue(new_value)
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
                AnalogParam.OSC_PULSE_WIDTH_MOD_DEPTH,
                AnalogParam.OSC_PULSE_WIDTH,
            ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pwm_mapping:
            control = self.pwm_mapping[parameter]
            control.setValue(new_value)
            successes.append(parameter.name)
        else:
            failures.append(parameter.name)

    def _update_partial_controls(
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
            param = AnalogParam.get_by_name(param_name)

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
                    control = self.controls.get(AnalogParam.LFO_TEMPO_SYNC_SWITCH)
                    if control:
                        control.setValue(param_value)
                        successes.append(param_name)
                    else:
                        failures.append(param_name)
                elif param_name == "LFO_TEMPO_SYNC_NOTE":
                    control = self.controls.get(AnalogParam.LFO_TEMPO_SYNC_NOTE)
                    if control:
                        control.setValue(param_value)
                        successes.append(param_name)
                    else:
                        failures.append(param_name)
                elif param == AnalogParam.FILTER_MODE_SWITCH:
                    self._update_filter_mode_buttons(param_value)
                    self.update_filter_controls_state(bool(param_value))
                elif param in [
                    AnalogParam.AMP_ENV_ATTACK_TIME,
                    AnalogParam.AMP_ENV_DECAY_TIME,
                    AnalogParam.AMP_ENV_SUSTAIN_LEVEL,
                    AnalogParam.AMP_ENV_RELEASE_TIME,
                    AnalogParam.FILTER_ENV_ATTACK_TIME,
                    AnalogParam.FILTER_ENV_DECAY_TIME,
                    AnalogParam.FILTER_ENV_SUSTAIN_LEVEL,
                    AnalogParam.FILTER_ENV_RELEASE_TIME,
                ]:
                    self.update_adsr_widget(param, param_value, successes, failures)
                elif param in self.pitch_env_mapping:
                    self.update_pitch_env_widget(
                        param, param_value, successes, failures
                    )
                elif param == AnalogParam.OSC_WAVEFORM:
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
            0: AnalogOscWave.SAW,
            1: AnalogOscWave.TRIANGLE,
            2: AnalogOscWave.PULSE,
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
            JDXiThemeManager.apply_button_rect_analog(btn)

        # --- Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXiThemeManager.apply_button_analog_active(selected_btn)

    def _update_lfo_shape_buttons(self, value: int):
        """
        Update the LFO shape buttons with visual feedback.

        :param value: int value
        :return: None
        """
        # --- Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            JDXiThemeManager.apply_button_rect_analog(btn)

        # --- Apply active style to the selected button
        selected_btn = self.lfo_shape_buttons.get(value)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXiThemeManager.apply_button_analog_active(selected_btn)
        else:
            log.message(f"Unknown LFO shape value: {value}", level=logging.WARNING)

    def _update_pw_controls_state(self, waveform: AnalogOscWave):
        """
        Enable/disable PW controls based on waveform

        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == AnalogOscWave.PULSE
        log.message(f"Waveform: {waveform} Pulse Width enabled: {pw_enabled}")
        self.controls[AnalogParam.OSC_PULSE_WIDTH].setEnabled(pw_enabled)
        self.controls[AnalogParam.OSC_PULSE_WIDTH_MOD_DEPTH].setEnabled(pw_enabled)
        # --- Update the visual state
        self.controls[AnalogParam.OSC_PULSE_WIDTH].setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
        self.controls[AnalogParam.OSC_PULSE_WIDTH_MOD_DEPTH].setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )

    def create_instrument_preset_group(self, synth_type: str = "Analog") -> QGroupBox:
        """
        Create the instrument preset group box with tabs for normal and cheat presets.

        :param synth_type: str
        :return: QGroupBox
        """
        instrument_preset_group = QGroupBox(f"{synth_type} Synth")
        instrument_title_group_layout = QVBoxLayout(instrument_preset_group)

        # --- Create tabbed widget inside the group box
        preset_tabs = QTabWidget()
        JDXiThemeManager.apply_tabs_style(preset_tabs, analog=True)
        instrument_title_group_layout.addWidget(preset_tabs)

        # --- === Tab 1: Normal Analog Presets ===
        normal_preset_widget, normal_preset_layout = create_scroll_container()

        self.instrument_title_label = DigitalTitle()
        normal_preset_layout.addWidget(self.instrument_title_label)

        # --- update_tone_name
        self.edit_tone_name_button = QPushButton("Edit tone name")
        self.edit_tone_name_button.clicked.connect(self.edit_tone_name)
        normal_preset_layout.addWidget(self.edit_tone_name_button)

        # --- read request button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        normal_preset_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel(f"Select a {synth_type} synth:")
        normal_preset_layout.addWidget(self.instrument_selection_label)

        # --- Build preset options, values, and categories from preset_list
        preset_options = [
            f"{preset['id']} - {preset['name']}" for preset in self.preset_list
        ]
        # --- Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset["id"]) for preset in self.preset_list]
        preset_categories = sorted(
            set(preset["category"] for preset in self.preset_list)
        )

        # --- Category filter function for presets
        def preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # --- Extract preset ID from display string (format: "001 - Preset Name")
            preset_id_str = (
                preset_display.split(" - ")[0] if " - " in preset_display else None
            )
            if preset_id_str:
                # --- Find the preset in the list and check its category
                for preset in self.preset_list:
                    if preset["id"] == preset_id_str:
                        return preset["category"] == category
            return False

        # --- Create SearchableFilterableComboBox for preset selection
        self.instrument_selection_combo = SearchableFilterableComboBox(
            label="",
            options=preset_options,
            values=preset_values,
            categories=preset_categories,
            category_filter_func=preset_category_filter,
            show_label=False,
            show_search=True,
            show_category=True,
            search_placeholder="Search presets...",
        )

        # --- Apply Analog styling
        JDXiThemeManager.apply_combo_box(
            self.instrument_selection_combo.combo_box, analog=True
        )

        # --- Connect signals - use combo_box for currentIndexChanged
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )

        # --- Create a load button (SearchableFilterableComboBox doesn't have one built-in)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.update_instrument_preset)
        # --- Connect valueChanged signal to load preset
        self.instrument_selection_combo.valueChanged.connect(self.load_preset)

        # --- Add combo box and load button
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.instrument_selection_combo)
        button_layout.addWidget(load_button)
        normal_preset_layout.addLayout(button_layout)

        # --- Store reference to load button for compatibility
        self.instrument_selection_combo.load_button = load_button
        normal_preset_layout.addStretch()

        try:
            analog_presets_icon = qta.icon(
                "mdi.music-note-multiple", color=JDXiStyle.GREY
            )
            if analog_presets_icon.isNull():
                raise ValueError("Icon is null")
        except:
            analog_presets_icon = IconRegistry.get_icon(
                IconRegistry.MUSIC, color=JDXiStyle.GREY
            )
        preset_tabs.addTab(normal_preset_widget, analog_presets_icon, "Analog Presets")

        # --- === Tab 2: Cheat Presets (Digital Synth presets on Analog channel) ===
        cheat_preset_widget, cheat_preset_layout = create_scroll_container()

        # --- Build preset options, values, and categories from DIGITAL_PRESET_LIST
        preset_options = [
            f"{preset['id']} - {preset['name']}" for preset in DIGITAL_PRESET_LIST
        ]
        # --- Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset["id"]) for preset in DIGITAL_PRESET_LIST]
        preset_categories = sorted(
            set(preset["category"] for preset in DIGITAL_PRESET_LIST)
        )

        # --- Category filter function for presets
        def cheat_preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # --- Extract preset ID from display string (format: "001 - Preset Name")
            preset_id_str = (
                preset_display.split(" - ")[0] if " - " in preset_display else None
            )
            if preset_id_str:
                # --- Find the preset in the list and check its category
                for preset in DIGITAL_PRESET_LIST:
                    if preset["id"] == preset_id_str:
                        return preset["category"] == category
            return False

        # --- Create SearchableFilterableComboBox for cheat preset selection
        self.cheat_preset_combo_box = SearchableFilterableComboBox(
            label="Preset",
            options=preset_options,
            values=preset_values,
            categories=preset_categories,
            category_filter_func=cheat_preset_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
            search_placeholder="Search presets...",
        )
        cheat_preset_layout.addWidget(self.cheat_preset_combo_box)

        # --- Load Button
        self.cheat_load_button = QPushButton(
            IconRegistry.get_icon(
                IconRegistry.FOLDER_NOTCH_OPEN, color=JDXiStyle.FOREGROUND
            ),
            "Load Preset",
        )
        self.cheat_load_button.clicked.connect(self._load_cheat_preset)
        cheat_preset_layout.addWidget(self.cheat_load_button)

        cheat_preset_layout.addStretch()
        cheat_presets_icon = IconRegistry.get_icon(
            IconRegistry.CODE_BRACES, color=JDXiStyle.GREY
        )
        preset_tabs.addTab(cheat_preset_widget, cheat_presets_icon, "Cheat Presets")

        return instrument_preset_group

    def _load_cheat_preset(self):
        """
        Load a Digital Synth preset on the Analog Synth channel (Cheat Mode).
        """
        if not self.midi_helper:
            log.warning("⚠️ MIDI helper not available for cheat preset loading")
            return

        # --- Get the current value from SearchableFilterableComboBox
        # --- The value is the preset ID as integer (e.g., 1 for "001")
        preset_id_int = self.cheat_preset_combo_box.value()
        program_number = str(preset_id_int).zfill(
            3
        )  # --- Convert back to 3-digit format

        log.message("=======load_cheat_preset (Cheat Mode)=======")
        log.parameter("combo box program_number", program_number)

        # --- Get MSB, LSB, PC values from the Digital preset list
        msb = get_preset_parameter_value("msb", program_number, DIGITAL_PRESET_LIST)
        lsb = get_preset_parameter_value("lsb", program_number, DIGITAL_PRESET_LIST)
        pc = get_preset_parameter_value("pc", program_number, DIGITAL_PRESET_LIST)

        if None in [msb, lsb, pc]:
            log.warning(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return

        log.message("retrieved msb, lsb, pc for cheat preset:")
        log.parameter("combo box msb", msb)
        log.parameter("combo box lsb", lsb)
        log.parameter("combo box pc", pc)
        log_midi_info(msb, lsb, pc)

        # --- Send bank select and program change on ANALOG_SYNTH channel (Ch3)
        # --- Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            MidiChannel.ANALOG_SYNTH,  # --- Send to Analog Synth channel (Ch3)
            msb,  # --- MSB is already correct
            lsb,  # --- LSB is already correct
            pc - 1,  # --- Convert 1-based PC to 0-based
        )

        # --- Request data update
        if hasattr(self, "data_request"):
            self.data_request()
