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

import json
import logging
from typing import Optional, Dict, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QPushButton,
    QSlider,
    QTabWidget,
    QComboBox,
    QSpinBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QShortcut, QKeySequence
import qtawesome as qta

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB
from jdxi_editor.midi.data.editor.data import AnalogSynthData, create_synth_data
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.preset.type import JDXISynth
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    midi_cc_to_frac,
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
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox


def set_widget_value_safely(widget, value):
    """
    Block signals for the widget, set its value, then unblock signals.

    Args:
        widget: The widget whose value is to be set.
        value: The value to set on the widget.
    """
    widget.blockSignals(True)
    if isinstance(widget, QSlider):
        widget.setValue(value)
    elif isinstance(widget, QComboBox):
        widget.setCurrentIndex(value)
    elif isinstance(widget, QSpinBox):
        widget.setValue(value)
    # Add other widget types as needed
    widget.blockSignals(False)


class AnalogSynthEditor(SynthEditor):
    """Analog Synth Editor UI."""

    def __init__(
        self, midi_helper: Optional[MidiIOHelper], preset_helper=None, parent=None
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
        self._init_synth_data()
        self.setup_ui()

        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._update_sliders_from_sysex)
            self.midi_helper.midi_parameter_received.connect(
                self._on_parameter_received
            )
            logging.info("MIDI helper initialized")
        else:
            logging.error("MIDI helper not initialized")

        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        self.data_request()

    def setup_ui(self):
        """Set up the Analog Synth Editor UI."""
        self.setMinimumSize(600, 600)
        self.resize(900, 600)
        self.setStyleSheet(JDXIStyle.TABS_ANALOG + JDXIStyle.EDITOR_ANALOG)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Top layout with title and image
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        instrument_preset_group = QGroupBox("Analog Synth")
        instrument_title_group_layout = QVBoxLayout(instrument_preset_group)

        self.instrument_title_label = DigitalTitle()
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel("Select an Analog synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)

        self.instrument_selection_combo = PresetComboBox(ANALOG_PRESET_LIST)
        self.instrument_selection_combo.setStyleSheet(JDXIStyle.COMBO_BOX_ANALOG)
        self.instrument_selection_combo.combo_box.setEditable(True)

        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)

        instrument_title_group_layout.addWidget(self.instrument_selection_combo)

        upper_layout.addWidget(instrument_preset_group)
        upper_layout.addWidget(self.instrument_image_label)

        self.update_instrument_image()

        # Tab sections
        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)

        self.oscillator_section = AnalogOscillatorSection(
            self._create_parameter_slider,
            self._create_parameter_switch,
            self._on_waveform_selected,
            self.wave_buttons,
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
            self.synth_data.address
        )
        self.tab_widget.addTab(
            self.filter_section, qta.icon("ri.filter-3-fill", color="#666666"), "Filter"
        )

        self.amp_section = AmpSection(
            self.midi_helper,
            self.synth_data.address,
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

        # Configure sliders
        for param, slider in self.controls.items():
            if isinstance(slider, QSlider):
                slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
                slider.setTickInterval(10)

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
        
    def _init_synth_data(self, synth_number):
        """Initialize synth-specific data."""
        self.synth_data = create_synth_data(JDXISynth.ANALOG)
        self.sysex_address = self.synth_data.address
    
        # Dynamically assign attributes
        for attr in [
            "address",
            "preset_type",
            "instrument_default_image",
            "instrument_icon_folder",
            "presets",
            "preset_list",
            "midi_requests",
            "midi_channel",
        ]:
            setattr(self, attr, getattr(self.synth_data, attr))
    
        logging.info(self.synth_data)

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
        # Update control states
        self.update_filter_controls_state(mode)

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        area_code = address[0]
        if address[0] == AddressMemoryAreaMSB.ANALOG:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)

            # Retrieve the corresponding DigitalParameter
            param = get_analog_parameter_by_address(parameter_address)
            partial_no = address[1]
            if param:
                logging.info(f"param: \t{param} \taddress=\t{address}, Value=\t{value}")
            elif param == AddressParameterAnalog.FILTER_MODE_SWITCH:
                self.update_filter_state(value=AddressParameterAnalog.FILTER_MODE_SWITCH.value)

                # Update the corresponding slider
                if param in self.controls:
                    self._update_slider(param, param_value, successes)
                    """
                    slider_value = param.convert_from_midi(value)
                    logging.info(
                        f"midi value {value} converted to slider value {slider_value}"
                    )
                    slider = self.controls[param]
                    slider.blockSignals(True)  # Prevent feedback loop
                    slider.setValue(slider_value)
                    slider.blockSignals(False)
                    """

                # Handle OSC_WAVE parameter to update waveform buttons
                if param == AddressParameterAnalog.OSC_WAVEFORM:
                    self._update_waveform_buttons(value)
                    logging.debug(
                        "updating waveform buttons for param {param} with {value}"
                    )

    def update_filter_state(self, value):
        """update_filter_state"""
        self.update_filter_controls_state(value)

    def _on_waveform_selected(self, waveform: AnalogOscWave):
        """Handle waveform button selection"""
        if self.midi_helper:
            sysex_message = RolandSysEx(
                msb=self.address_msb,
                umb=self.address_umb,
                lmb=self.address_lmb,
                lsb=AddressParameterAnalog.OSC_WAVEFORM.value[0],
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
        """Handle LFO shape change"""
        if self.midi_helper:
            sysex_message = RolandSysEx(
                msb=self.address_msb,
                umb=self.address_umb,
                lmb=self.address_lmb,
                lsb=AddressParameterAnalog.LFO_SHAPE.value[0],
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

    def _update_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")

        try:
            current_sysex_data = json.loads(json_sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        # Compare with previous data and log changes
        if self.previous_json_data:
            log_changes(self.previous_json_data, current_sysex_data)

        # Store the current data for future comparison
        self.previous_json_data = current_sysex_data

        if current_sysex_data.get("TEMPORARY_AREA") != "TEMPORARY_ANALOG_SYNTH_AREA":
            logging.warning(
                "SysEx data does not belong to TEMPORARY_ANALOG_SYNTH_AREA. Skipping update."
            )
            return

        # Remove unnecessary keys
        ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "TONE_NAME",
            "SYNTH_TONE",
        }
        current_sysex_data = {
            k: v for k, v in current_sysex_data.items() if k not in ignored_keys
        }

        # Define mapping dictionaries
        sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        filter_switch_map = {0: 0, 1: 1}
        osc_waveform_map = {
            0: AnalogOscWave.SAW,
            1: AnalogOscWave.TRIANGLE,
            2: AnalogOscWave.PULSE,
        }

        failures, successes = [], []

        def update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                # set_widget_value_safely(slider, slider_value)
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)

        def update_adsr_widget(param, value):
            """Helper function to update ADSR widgets."""
            new_value = (
                midi_cc_to_frac(value)
                if param
                in [
                    AddressParameterAnalog.AMP_ENV_SUSTAIN_LEVEL,
                    AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL,
                ]
                else midi_cc_to_ms(value)
            )

            adsr_mapping = {
                AddressParameterAnalog.AMP_ENV_ATTACK_TIME: self.amp_section.amp_env_adsr_widget.attack_sb,
                AddressParameterAnalog.AMP_ENV_DECAY_TIME: self.amp_section.amp_env_adsr_widget.decay_sb,
                AddressParameterAnalog.AMP_ENV_SUSTAIN_LEVEL: self.amp_section.amp_env_adsr_widget.sustain_sb,
                AddressParameterAnalog.AMP_ENV_RELEASE_TIME: self.amp_section.amp_env_adsr_widget.release_sb,
                AddressParameterAnalog.FILTER_ENV_ATTACK_TIME: self.filter_section.filter_adsr_widget.attack_sb,
                AddressParameterAnalog.FILTER_ENV_DECAY_TIME: self.filter_section.filter_adsr_widget.decay_sb,
                AddressParameterAnalog.FILTER_ENV_SUSTAIN_LEVEL: self.filter_section.filter_adsr_widget.sustain_sb,
                AddressParameterAnalog.FILTER_ENV_RELEASE_TIME: self.filter_section.filter_adsr_widget.release_sb,
            }

            if param in adsr_mapping:
                spinbox = adsr_mapping[param]
                spinbox.setValue(new_value)

        for param_name, param_value in current_sysex_data.items():
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
                if param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons:
                    self._update_lfo_shape_buttons(param_value)
                if (
                    param_name == "SUB_OSCILLATOR_TYPE"
                    and param_value in sub_osc_type_map
                ):
                    self.oscillator_section.sub_oscillator_type_switch.blockSignals(
                        True
                    )
                    self.oscillator_section.sub_oscillator_type_switch.setValue(
                        sub_osc_type_map[param_value]
                    )
                    self.oscillator_section.sub_oscillator_type_switch.blockSignals(
                        False
                    )
                elif param_name == "OSC_WAVEFORM" and param_value in osc_waveform_map:
                    self._update_waveform_buttons(param_value)
                elif (
                        param == AddressParameterAnalog.FILTER_MODE_SWITCH
                        and param_value in filter_switch_map
                ):
                    self.filter_section.filter_mode_switch.blockSignals(True)
                    self.filter_section.filter_mode_switch.setValue(
                        filter_switch_map[param_value]
                    )
                    self.filter_section.filter_mode_switch.blockSignals(False)
                    self.update_filter_controls_state(bool(param_value))
                else:
                    update_slider(param, param_value)
                    update_adsr_widget(param, param_value)
            else:
                failures.append(param_name)

        logging.info(f"Updated {len(successes)} parameters successfully.")
        if failures:
            logging.warning(f"Failed to update {len(failures)} parameters: {failures}")

    def _update_waveform_buttons(self, value):
        """Update the waveform buttons based on the OSC_WAVE value with visual feedback."""
        logging.debug(f"Updating waveform buttons with value {value}")

        waveform_map = {
            0: AnalogOscWave.SAW,
            1: AnalogOscWave.TRIANGLE,
            2: AnalogOscWave.PULSE,
        }

        selected_waveform = waveform_map.get(value)

        if selected_waveform is None:
            logging.warning(f"Unknown waveform value: {value}")
            return

        logging.debug(f"Waveform value {value} found, selecting {selected_waveform}")

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

    def _update_lfo_shape_buttons(self, value):
        """Update the LFO shape buttons with visual feedback."""
        logging.debug(f"Updating LFO shape buttons with value {value}")

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
            logging.warning(f"Unknown LFO shape value: {value}")

    def _update_pw_controls_state(self, waveform: AnalogOscWave):
        """Enable/disable PW controls based on waveform"""
        pw_enabled = waveform == AnalogOscWave.PULSE
        logging.info(self.controls)
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH].setEnabled(pw_enabled)
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH_MOD_DEPTH].setEnabled(pw_enabled)
        # Update the visual state
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH].setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
        self.controls[AddressParameterAnalog.OSC_PULSE_WIDTH_MOD_DEPTH].setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
