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
from typing import Optional, Dict, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSlider,
    QTabWidget,
    QSplitter,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
import qtawesome as qta

from jdxi_editor.jdxi.preset.helper import JDXIPresetHelper
from jdxi_editor.log.header import log_header_message
from jdxi_editor.log.message import log_message
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.utils.conversions import (
    midi_value_to_ms,
    midi_value_to_fraction,
)
from jdxi_editor.midi.data.analog.oscillator import AnalogOscWave
from jdxi_editor.ui.editors.analog.amp import AmpSection
from jdxi_editor.ui.editors.analog.filter import AnalogFilterSection
from jdxi_editor.ui.editors.analog.lfo import AnalogLFOSection
from jdxi_editor.ui.editors.analog.oscillator import AnalogOscillatorSection
from jdxi_editor.ui.editors.helpers.analog import get_analog_parameter_by_address
from jdxi_editor.ui.editors.synth.editor import SynthEditor, log_changes
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.widgets.switch.switch import Switch


class AnalogSynthEditor(SynthEditor):
    """Analog Synth Editor UI."""

    def __init__(
            self,
            midi_helper: Optional[MidiIOHelper] = None,
            preset_helper: Optional[JDXIPresetHelper] = None,
            parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper, parent)

        self.amp_section = None
        self.oscillator_section = None
        self.read_request_button = None
        self.tab_widget = None
        self.lfo_section = None
        self.instrument_selection_label = None
        self.preset_helper = preset_helper
        self.wave_buttons = {}
        self.lfo_shape_buttons = {}
        self.controls: Dict[Union[AddressParameterAnalog], QWidget] = {}
        self.updating_from_spinbox = False
        self.previous_json_data = None
        self.main_window = parent

        self._init_parameter_mappings()
        self._init_synth_data(JDXISynth.ANALOG)
        self.setup_ui()

        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            self.midi_helper.midi_parameter_received.connect(
                self._on_parameter_received
            )
            log_message("MIDI helper initialized")
        else:
            log_message("MIDI helper not initialized")

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
            AddressParameterAnalog.AMP_ENV_ATTACK_TIME: self.amp_section.amp_env_adsr_widget.attack_control,
            AddressParameterAnalog.AMP_ENV_DECAY_TIME: self.amp_section.amp_env_adsr_widget.decay_control,
            AddressParameterAnalog.AMP_ENV_SUSTAIN_LEVEL: self.amp_section.amp_env_adsr_widget.sustain_control,
            AddressParameterAnalog.AMP_ENV_RELEASE_TIME: self.amp_section.amp_env_adsr_widget.release_control,
            AddressParameterAnalog.FILTER_ENV_ATTACK_TIME: self.filter_section.filter_adsr_widget.attack_control,
            AddressParameterAnalog.FILTER_ENV_DECAY_TIME: self.filter_section.filter_adsr_widget.decay_control,
            AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL: self.filter_section.filter_adsr_widget.sustain_control,
            AddressParameterAnalog.FILTER_ENV_RELEASE_TIME: self.filter_section.filter_adsr_widget.release_control,
        }
        self.pitch_env_mapping = {
            AddressParameterAnalog.OSC_PITCH_ENV_ATTACK_TIME: self.oscillator_section.pitch_env_widget.attack_control,
            AddressParameterAnalog.OSC_PITCH_ENV_DECAY_TIME: self.oscillator_section.pitch_env_widget.decay_control,
            AddressParameterAnalog.OSC_PITCH_ENV_DEPTH: self.oscillator_section.pitch_env_widget.depth_control,
        }
        self.data_request()

    def setup_ui(self):
        """Set up the Analog Synth Editor UI."""
        self.setMinimumSize(650, 600)
        self.resize(950, 600)
        self.setStyleSheet(JDXIStyle.TABS_ANALOG + JDXIStyle.EDITOR_ANALOG)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        # === Top half ===
        upper_widget = QWidget()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        scroll.setWidget(container)
        main_layout.addWidget(splitter)

        # Top layout with title and image
        upper_layout = QHBoxLayout()
        upper_widget.setLayout(upper_layout)

        instrument_preset_group = self._create_instrument_preset_group()
        upper_layout.addWidget(instrument_preset_group)

        self._create_instrument_image_group()
        upper_layout.addWidget(self.instrument_image_group)
        self.update_instrument_image()

        # Tab sections
        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)

        # Configure sliders
        for param, slider in self.controls.items():
            if isinstance(slider, QSlider):
                slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
                slider.setTickInterval(10)

        scroll.setWidget(container)

        splitter.addWidget(upper_widget)
        splitter.addWidget(scroll)
        splitter.setSizes([300, 300])  # give more room to bottom
        # Splitter handle style
        splitter.setStyleSheet(JDXIStyle.SPLITTER)
        self.show()

    def _create_sections(self):
        """Create the sections for the Analog Synth Editor."""
        self.oscillator_section = AnalogOscillatorSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._on_waveform_selected,
            self.wave_buttons,
            self.midi_helper,
            self.sysex_address
        )
        self.tab_widget.addTab(
            self.oscillator_section,
            qta.icon("mdi.triangle-wave", color="#666666"),
            "Oscillator",
        )
        self.filter_section = AnalogFilterSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._on_filter_mode_changed,
            self.send_control_change,
            self.midi_helper,
            self.synth_data.sysex_address
        )
        self.tab_widget.addTab(
            self.filter_section, qta.icon("ri.filter-3-fill", color="#666666"), "Filter"
        )
        self.amp_section = AmpSection(
            self.midi_helper,
            self.synth_data.sysex_address,
            self._create_parameter_slider,
            generate_waveform_icon,
            base64_to_pixmap,
        )
        self.tab_widget.addTab(
            self.amp_section, qta.icon("mdi.amplifier", color="#666666"), "Amp"
        )
        self.lfo_section = AnalogLFOSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._create_parameter_combo_box,
            self._on_lfo_shape_changed,
            self.lfo_shape_buttons,
        )
        self.tab_widget.addTab(
            self.lfo_section, qta.icon("mdi.sine-wave", color="#666666"), "LFO"
        )

    def _init_parameter_mappings(self):
        """Initialize MIDI parameter mappings."""
        self.cc_parameters = {
            "Cutoff": 102,
            "Resonance": 105,
            "Level": 117,
            "LFO Rate": 16,
        }

        self.nrpn_parameters = {
            "Envelope": (0, 124),
            "LFO Shape": (0, 3),
            "LFO Pitch Depth": (0, 15),
            "LFO Filter Depth": (0, 18),
            "LFO Amp Depth": (0, 21),
            "Pulse Width": (0, 37),
        }

        # Reverse lookup map
        self.nrpn_map = {v: k for k, v in self.nrpn_parameters.items()}

    def update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            AddressParameterAnalog.FILTER_CUTOFF,
            AddressParameterAnalog.FILTER_RESONANCE,
            AddressParameterAnalog.FILTER_CUTOFF_KEYFOLLOW,
            AddressParameterAnalog.FILTER_ENV_VELOCITY_SENSITIVITY,
            AddressParameterAnalog.FILTER_ENV_DEPTH,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)
        self.filter_section.filter_adsr_widget.setEnabled(enabled)

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes"""
        self.update_filter_controls_state(mode)

    def _on_parameter_received(self, address: list[int], value: int):
        """
        Handle incoming MIDI parameter messages.
        :param address: list of address bytes
        :param value: int value
        :return: None
        """
        if address[0] == AddressMemoryAreaMSB.ANALOG:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)
            # Retrieve the corresponding DigitalParameter
            param = get_analog_parameter_by_address(parameter_address)
            if param:
                log_message(f"param: \t{param} \taddress=\t{address}, Value=\t{value}")
            elif param == AddressParameterAnalog.FILTER_MODE_SWITCH:
                self.update_filter_state(value=AddressParameterAnalog.FILTER_MODE_SWITCH.value)
                if param in self.controls:
                    self._update_slider(param, param.value)
                # Handle OSC_WAVE parameter to update waveform buttons
                if param == AddressParameterAnalog.OSC_WAVEFORM:
                    self._update_waveform_buttons(value)
                    log_message(
                        f"updating waveform buttons for param {param} with {value}"
                    )

    def update_filter_state(self, value: int):
        """
        Update the filter state
        :param value: int value
        :return: None
        """
        self.update_filter_controls_state(value)

    def _on_waveform_selected(self, waveform: AnalogOscWave):
        """
        Handle waveform button selection
        :param waveform: AnalogOscWave value
        :return: None
        """
        if self.midi_helper:
            sysex_message = RolandSysEx(
                msb=self.sysex_address.msb,
                umb=self.sysex_address.umb,
                lmb=self.sysex_address.lmb,
                lsb=AddressParameterAnalog.OSC_WAVEFORM.lsb,
                value=waveform.midi_value,
            )
            self.midi_helper.send_midi_message(sysex_message)

            for btn in self.wave_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(JDXIStyle.BUTTON_RECT_ANALOG)

            # Apply active style to the selected waveform button
            selected_btn = self.wave_buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(JDXIStyle.BUTTON_ANALOG_ACTIVE)
            self._update_pw_controls_state(waveform)

    def _on_lfo_shape_changed(self, value: int):
        """
        Handle LFO shape change
        :param value: int value
        :return: None
        """
        if self.midi_helper:
            sysex_message = RolandSysEx(
                msb=self.sysex_address.msb,
                umb=self.sysex_address.umb,
                lmb=self.sysex_address.lmb,
                lsb=AddressParameterAnalog.LFO_SHAPE.lsb,
                value=value,
            )
            self.midi_helper.send_midi_message(sysex_message)
            # Reset all buttons to default style
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(JDXIStyle.BUTTON_RECT_ANALOG)

            # Apply active style to the selected button
            selected_btn = self.lfo_shape_buttons.get(value)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(JDXIStyle.BUTTON_ANALOG_ACTIVE)

    def update_slider(self, param: AddressParameterAnalog,
                      value: int,
                      successes: list = None,
                      failures: list = None) -> None:
        """
        Helper function to update sliders safely.
        :param param: AddressParameterAnalog value
        :param failures: list of failed parameters
        :param successes: list of successful parameters
        :param value: int value
        :return: None
        """
        slider = self.controls.get(param)
        if slider:
            slider_value = param.convert_from_midi(value)
            slider.blockSignals(True)
            slider.setValue(slider_value)
            slider.blockSignals(False)
            successes.append(param.name)
            log_slider_parameters(self.sysex_address.umb, self.sysex_address.lmb, param, value, slider_value)
        else:
            failures.append(param.name)

    def update_adsr_widget(self,
                           parameter: AddressParameterAnalog,
                           value: int,
                           successes: list = None,
                           failures: list = None) -> None:
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
                   AddressParameterAnalog.AMP_ENV_SUSTAIN_LEVEL,
                   AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL,
               ]
            else midi_value_to_ms(value)
        )

        if parameter in self.adsr_mapping:
            control = self.adsr_mapping[parameter]
            control.setValue(new_value)
            successes.append(parameter.name)
        else:
            failures.append(parameter.name)

    def update_pitch_env_widget(self,
                                parameter: AddressParameterAnalog,
                                value: int, successes: list = None,
                                failures: list = None) -> None:
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
                   AddressParameterAnalog.OSC_PITCH_ENV_DEPTH,
               ]
            else midi_value_to_ms(value, 10, 1000)
        )

        if parameter in self.pitch_env_mapping:
            control = self.pitch_env_mapping[parameter]
            control.setValue(new_value)
            successes.append(parameter.name)
        else:
            failures.append(parameter.name)

    def _dispatch_sysex_to_area(self,
                                json_sysex_data: str):
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str JSON SysEx data
        :return: None
        """
        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return
        temp_area = sysex_data.get("TEMPORARY_AREA")
        synth_tone = sysex_data.get("SYNTH_TONE")

        if temp_area != "TEMPORARY_ANALOG_SYNTH_AREA" or synth_tone != "TONE_COMMON":
            return
        log_header_message(f"Updating {temp_area} {synth_tone} UI components from SysEx data")

        # Compare with previous data and log changes
        if self.previous_json_data:
            log_changes(self.previous_json_data, sysex_data)

        # Store the current data for future comparison
        self.previous_json_data = sysex_data

        # Remove unnecessary keys
        ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "TONE_NAME", "TONE_NAME_1", "TONE_NAME_2", "TONE_NAME_3", "TONE_NAME_4", "TONE_NAME_5", "TONE_NAME_6",
            "TONE_NAME_7", "TONE_NAME_8", "TONE_NAME_9", "TONE_NAME_10", "TONE_NAME_11", "TONE_NAME_12",
            "SYNTH_TONE",
        }
        sysex_data = {
            k: v for k, v in sysex_data.items() if k not in ignored_keys
        }

        failures, successes = [], []

        for param_name, param_value in sysex_data.items():
            param = AddressParameterAnalog.get_by_name(param_name)

            if param:
                # FIXME: Deal with NRPN later
                # if param_name in ["LFO_SHAPE", "LFO_PITCH_DEPTH", "LFO_FILTER_DEPTH", "LFO_AMP_DEPTH", "PULSE_WIDTH"]:
                #    nrpn_map = {
                #        (0, 124): "Envelope",
                #        (0, 3): "LFO Shape",
                #        (0, 15): "LFO Pitch Depth",
                #        (0, 18): "LFO Filter Depth",
                #        (0, 21): "LFO Amp Depth",
                #        (0, 37): "Pulse Width",
                #    }
                #    nrpn_address = next(
                #        (addr for addr, name in nrpn_map.items() if name == param_name), None
                #    )
                #    if nrpn_address:
                #        self._handle_nrpn_message(nrpn_address, param_value, channel=1)
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
                elif param_name == "OSC_WAVEFORM" and param_value in self.osc_waveform_map:
                    self._update_waveform_buttons(param_value)
                elif param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons:
                    self._update_lfo_shape_buttons(param_value)
                elif param_name == "LFO_TEMPO_SYNC_SWITCH":
                    self.controls[AddressParameterAnalog.LFO_TEMPO_SYNC_SWITCH].setValue(param_value)
                elif param_name == "LFO_TEMPO_SYNC_NOTE":
                    self.controls[AddressParameterAnalog.LFO_TEMPO_SYNC_NOTE].setValue(param_value)
                elif (
                        param == AddressParameterAnalog.FILTER_MODE_SWITCH
                        and param_value in self.filter_switch_map
                ):
                    self.filter_section.filter_mode_switch.blockSignals(True)
                    self.filter_section.filter_mode_switch.setValue(
                        self.filter_switch_map[param_value]
                    )
                    self.filter_section.filter_mode_switch.blockSignals(False)
                    self.update_filter_controls_state(bool(param_value))
                elif param in [
                    AddressParameterAnalog.AMP_ENV_ATTACK_TIME,
                    AddressParameterAnalog.AMP_ENV_DECAY_TIME,
                    AddressParameterAnalog.AMP_ENV_SUSTAIN_LEVEL,
                    AddressParameterAnalog.AMP_ENV_RELEASE_TIME,
                    AddressParameterAnalog.FILTER_ENV_ATTACK_TIME,
                    AddressParameterAnalog.FILTER_ENV_DECAY_TIME,
                    AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL,
                    AddressParameterAnalog.FILTER_ENV_RELEASE_TIME,
                ]:
                    self.update_adsr_widget(param,
                                            param_value,
                                            successes,
                                            failures)
                elif param in self.pitch_env_mapping:
                    self.update_pitch_env_widget(param,
                                                 param_value,
                                                 successes,
                                                 failures)
                else:
                    self.update_slider(param,
                                       param_value,
                                       successes,
                                       failures)

            else:
                failures.append(param_name)

        log_message(f"Updated {len(successes)} parameters successfully.")
        if failures:
            log_message(f"Failed to update {len(failures)} parameters: {failures}", level=logging.WARNING)

    def update_switch(self, switch: Switch,
                      value: int,
                      successes: list = None,
                      failures: list = None) -> None:
        """
        Update switch state and log success/failure.
        :param switch: QWidget representing the switch
        :param value: int value to set
        :param successes: list of successful parameters
        :param failures: list of failed parameters
        :return: None
        """
        if isinstance(switch, Switch):
            switch.setValue(value)
            successes.append(switch.objectName())
        else:
            failures.append(switch.objectName())

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
            log_message(f"Unknown waveform value: {value}", level=logging.WARNING)
            return

        log_message(f"Waveform value {value} found, selecting {selected_waveform}")

        # Retrieve waveform buttons for the given partial
        wave_buttons = self.wave_buttons

        # Reset all buttons to default style
        for btn in wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXIStyle.BUTTON_RECT_ANALOG)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXIStyle.BUTTON_ANALOG_ACTIVE)

    def _update_lfo_shape_buttons(self, value: int):
        """
        Update the LFO shape buttons with visual feedback.
        :param value: int value
        :return: None
        """
        # Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXIStyle.BUTTON_RECT_ANALOG)

        # Apply active style to the selected button
        selected_btn = self.lfo_shape_buttons.get(value)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXIStyle.BUTTON_ANALOG_ACTIVE)
        else:
            log_message(f"Unknown LFO shape value: {value}", level=logging.WARNING)

    def _update_pw_controls_state(self, waveform: AnalogOscWave):
        """
        Enable/disable PW controls based on waveform
        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == AnalogOscWave.PULSE
        log_message(f"Waveform: {waveform} Pulse Width enabled: {pw_enabled}")
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH].setEnabled(pw_enabled)
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH_MOD_DEPTH].setEnabled(pw_enabled)
        # Update the visual state
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH].setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH_MOD_DEPTH].setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
