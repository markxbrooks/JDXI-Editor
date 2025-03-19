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
    preset_handler = PresetHandler()
    editor = AnalogSynthEditor(midi_helper, preset_handler)
    editor.show()

"""

import os
import re
import json
import logging
from functools import partial
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
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QShortcut, QKeySequence
import qtawesome as qta

from jdxi_editor.midi.data.presets.analog import ANALOG_PRESETS_ENUMERATED
from jdxi_editor.midi.preset.type import PresetType
from jdxi_editor.midi.data.parameter.analog import AnalogParameter
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    midi_cc_to_frac,
    frac_to_midi_cc,
    ms_to_midi_cc,
)
from jdxi_editor.midi.data.constants.sysex import TEMPORARY_TONE_AREA, TEMPORARY_ANALOG_SYNTH_AREA
from jdxi_editor.midi.data.constants.analog import (
    AnalogControlChange,
    Waveform,
    SubOscType,
    ANALOG_PART,
    ANALOG_OSC_GROUP, LFO_TEMPO_SYNC_NOTES,
)
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_ANALOG
from jdxi_editor.ui.editors.synth import SynthEditor
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.adsr.adsr import ADSR
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox
from jdxi_editor.ui.widgets.slider import Slider


def get_analog_parameter_by_address(address: int):
    """Retrieve the DigitalParameter by its address."""
    logging.info(f"address: {address}")
    for param in AnalogParameter:
        if param.address == address:
            logging.info(f"get_analog_parameter_by_address found param: {param}")
            return param
    return None


class AnalogSynthEditor(SynthEditor):
    """Analog Synth"""

    # preset_changed = Signal(int, str, int)

    def __init__(
            self, midi_helper: Optional[MidiIOHelper], preset_handler=None, parent=None
    ):
        super().__init__(midi_helper, parent)
        self.bipolar_parameters = [
            AnalogParameter.FILTER_ENV_VELOCITY_SENS,
            AnalogParameter.AMP_LEVEL_KEYFOLLOW,
            AnalogParameter.OSC_PITCH_ENV_VELOCITY_SENS,
            AnalogParameter.OSC_PITCH_COARSE,
            AnalogParameter.OSC_PITCH_FINE,
            AnalogParameter.LFO_PITCH_MODULATION_CONTROL,
            AnalogParameter.LFO_AMP_MODULATION_CONTROL,
            AnalogParameter.LFO_FILTER_MODULATION_CONTROL,
            AnalogParameter.OSC_PITCH_ENV_DEPTH,
            AnalogParameter.LFO_RATE_MODULATION_CONTROL,
            AnalogParameter.FILTER_ENV_DEPTH,
            # Add other bipolar parameters as needed
        ]
        self.area = TEMPORARY_TONE_AREA
        self.group = ANALOG_OSC_GROUP
        self.part = ANALOG_PART
        self.preset_handler = preset_handler
        self.setWindowTitle("Analog Synth")
        self.previous_json_data = None
        # Allow resizing
        self.setMinimumSize(800, 600)
        self.resize(900, 600)
        self.image_label = QLabel()
        self.instrument_icon_folder = "analog_synths"
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        self.main_window = parent
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.presets = ANALOG_PRESETS_ENUMERATED
        self.preset_type = PresetType.ANALOG
        self.midi_requests = ["F0 41 10 00 00 00 0E 11 18 00 00 00 00 00 00 40 26 F7", # Program Common
                              "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"] # Analog
        self.midi_channel = MIDI_CHANNEL_ANALOG
        # Create scroll area for resizable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Store parameter controls for easy access
        self.controls: Dict[Union[AnalogParameter], QWidget] = {}
        self.updating_from_spinbox = False
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # Additional styling specific to analog editor
        self.setStyleSheet(Style.JDXI_TABS_ANALOG + Style.JDXI_EDITOR_ANALOG)
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        # Title and drum kit selection
        instrument_preset_group = QGroupBox("Analog Synth")
        self.instrument_title_label = QLabel(
            f"Analog Synth:\n {self.presets[0]}" if self.presets else "Analog Synth"
        )
        instrument_preset_group.setStyleSheet(
            """
            QGroupBox {
            width: 100px;
            }
        """
        )
        self.instrument_title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        instrument_title_group_layout = QVBoxLayout()
        instrument_preset_group.setLayout(instrument_title_group_layout)
        instrument_title_group_layout.addWidget(self.instrument_title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)

        self.instrument_selection_label = QLabel("Select an Analog synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        self.instrument_selection_combo = PresetComboBox(ANALOG_PRESETS_ENUMERATED)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        instrument_title_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(instrument_preset_group)
        upper_layout.addWidget(self.image_label)
        container_layout.addLayout(upper_layout)
        self.update_instrument_image()
        # Add sections side by side
        self.tab_widget = QTabWidget()
        container_layout.addWidget(self.tab_widget)
        self.tab_widget.addTab(
            self._create_oscillator_section(),
            qta.icon("mdi.triangle-wave", color="#666666"),
            "Oscillator",
        )
        self.tab_widget.addTab(
            self._create_filter_section(),
            qta.icon("ri.filter-3-fill", color="#666666"),
            "Filter",
        )
        self.tab_widget.addTab(
            self._create_amp_section(),
            qta.icon("mdi.amplifier", color="#666666"),
            "Amp",
        )
        self.tab_widget.addTab(
            self._create_lfo_section(),
            qta.icon("mdi.sine-wave", color="#666666"),
            "LFO",
        )

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect filter controls
        self.filter_resonance.valueChanged.connect(
            lambda v: self.send_control_change(
                AnalogParameter.FILTER_RESONANCE.value[0], v
            )
        )
        self.midi_helper.midi_sysex_json.connect(self._update_sliders_from_sysex)
        for param, slider in self.controls.items():
            if isinstance(slider, QSlider):  # Ensure it's address slider
                slider.setTickPosition(
                    QSlider.TickPosition.TicksBothSides
                )  # Tick marks on both sides
                slider.setTickInterval(10)  # Adjust interval as needed
        self.data_request()
        self.midi_helper.midi_parameter_received.connect(self._on_parameter_received)
        # Initialize previous JSON data storage
        self.previous_json_data = None
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            # Register the callback for incoming MIDI messages
            logging.info("MIDI helper initialized")
            if hasattr(self.midi_helper, "set_callback"):
                self.midi_helper.set_callback(self.midi_helper.midi_callback)
                logging.info("MIDI callback set")
            else:
                logging.error("MIDI set_callback method not found")
        else:
            logging.error("MIDI helper not initialized")
        self.midi_helper.update_analog_tone_name.connect(self.set_instrument_title_label)

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        area_code = address[0]
        if address[0] == TEMPORARY_ANALOG_SYNTH_AREA:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)

            # Retrieve the corresponding DigitalParameter
            param = get_analog_parameter_by_address(parameter_address)
            partial_no = address[1]
            if param:
                logging.info(f"param: \t{param} \taddress=\t{address}, Value=\t{value}")

                # Update the corresponding slider
                if param in self.controls:
                    slider_value = param.convert_from_midi(value)
                    logging.info(
                        f"midi value {value} converted to slider value {slider_value}"
                    )
                    slider = self.controls[param]
                    slider.blockSignals(True)  # Prevent feedback loop
                    slider.setValue(slider_value)
                    slider.blockSignals(False)

                # Handle OSC_WAVE parameter to update waveform buttons
                if param == AnalogParameter.OSC_WAVEFORM:
                    self._update_waveform_buttons(value)
                    logging.debug(
                        "updating waveform buttons for param {param} with {value}"
                    )

    def _on_midi_message_received(self, message):
        """Handle incoming MIDI messages"""
        if not message.type == "clock":
            logging.info(f"MIDI message: {message}")
            self.blockSignals(True)
            self.data_request()
            self.blockSignals(False)

    def _create_oscillator_section(self):
        group = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)  # Remove margins
        group.setLayout(layout)

        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}
        for waveform in [Waveform.SAW, Waveform.TRIANGLE, Waveform.PULSE]:
            btn = AnalogWaveformButton(waveform)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Set icons for each waveform
            if waveform == Waveform.SAW:
                saw_icon_base64 = generate_waveform_icon("upsaw", "#FFFFFF", 1.0)
                saw_pixmap = base64_to_pixmap(saw_icon_base64)
                btn.setIcon(QIcon(saw_pixmap))
            elif waveform == Waveform.TRIANGLE:
                tri_icon_base64 = generate_waveform_icon("triangle", "#FFFFFF", 1.0)
                tri_pixmap = base64_to_pixmap(tri_icon_base64)
                btn.setIcon(QIcon(tri_pixmap))
            elif waveform == Waveform.PULSE:
                pulse_icon_base64 = generate_waveform_icon("pwsqu", "#FFFFFF", 1.0)
                pulse_pixmap = base64_to_pixmap(pulse_icon_base64)
                btn.setIcon(QIcon(pulse_pixmap))

            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            wave_layout.addWidget(btn)
        layout.addLayout(wave_layout)

        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        self.osc_pitch_coarse = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_COARSE, "Coarse"
        )
        self.osc_pitch_fine = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_FINE, "Fine"
        )

        tuning_layout.addWidget(self.osc_pitch_coarse)
        tuning_layout.addWidget(self.osc_pitch_fine)
        layout.addWidget(tuning_group)

        # Pulse Width controls
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        self.osc_pulse_width = self._create_parameter_slider(
            AnalogParameter.OSC_PULSE_WIDTH,
            "Width",
        )
        self.osc_pulse_width_mod_depth = self._create_parameter_slider(
            AnalogParameter.OSC_PULSE_WIDTH_MOD_DEPTH,
            "Mod Depth",
        )

        pw_layout.addWidget(self.osc_pulse_width)
        pw_layout.addWidget(self.osc_pulse_width_mod_depth)
        layout.addWidget(pw_group)

        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        self.pitch_env_velo = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_VELOCITY_SENS, "Mod Depth"
        )
        self.pitch_env_attack = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_ATTACK_TIME, "Attack"
        )
        self.pitch_env_decay = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_DECAY, "Decay"
        )
        self.pitch_env_depth = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_ENV_DEPTH, "Depth"
        )

        pitch_env_layout.addWidget(self.pitch_env_velo)
        pitch_env_layout.addWidget(self.pitch_env_attack)
        pitch_env_layout.addWidget(self.pitch_env_decay)
        pitch_env_layout.addWidget(self.pitch_env_depth)
        layout.addWidget(pitch_env_group)

        # Sub Oscillator
        sub_group = QGroupBox("Sub Oscillator")
        sub_layout = QVBoxLayout()
        sub_group.setLayout(sub_layout)

        self.sub_oscillator_type_switch = self._create_parameter_switch(AnalogParameter.SUB_OSCILLATOR_TYPE,
            "Type",
            [
                SubOscType.OFF.display_name,
                SubOscType.OCT_DOWN_1.display_name,
                SubOscType.OCT_DOWN_2.display_name,
            ],
        )
        sub_layout.addWidget(self.sub_oscillator_type_switch)
        layout.addWidget(sub_group)

        # Update PW controls enabled state based on current waveform
        self._update_pw_controls_state(Waveform.SAW)  # Initial state

        return group

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        logging.info(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        logging.info(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(f"Analog Synth:\n {selected_synth_text}")

    def update_instrument_image(self):
        def load_and_set_image(image_path, secondary_image_path):
            """Helper function to load and set the image on the label."""
            file_to_load = ""

            if os.path.exists(image_path):
                file_to_load = image_path
            elif os.path.exists(secondary_image_path):
                file_to_load = secondary_image_path
            else:
                file_to_load = os.path.join(
                    "resources", self.instrument_icon_folder, "analog.png"
                )
            pixmap = QPixmap(file_to_load)
            scaled_pixmap = pixmap.scaledToHeight(
                150, Qt.TransformationMode.SmoothTransformation
            )  # Resize to 250px height
            self.image_label.setPixmap(scaled_pixmap)
            return True

        selected_instrument_text = (
            self.instrument_selection_combo.combo_box.currentText()
        )

        # Try to extract synth name from the selected text
        image_loaded = False
        if instrument_matches := re.search(
                r"(\d{3}): (\S+)\s(\S+)+", selected_instrument_text, re.IGNORECASE
        ):
            selected_instrument_name = (
                instrument_matches.group(2).lower().replace("&", "_").split("_")[0]
            )
            selected_instrument_type = (
                instrument_matches.group(3).lower().replace("&", "_").split("_")[0]
            )
            logging.info(
                f"selected instrument image preset_type: {selected_instrument_type}"
            )
            specific_image_path = os.path.join(
                "resources",
                self.instrument_icon_folder,
                f"{selected_instrument_name}.png",
            )
            generic_image_path = os.path.join(
                "resources",
                self.instrument_icon_folder,
                f"{selected_instrument_type}.png",
            )
            image_loaded = load_and_set_image(specific_image_path, generic_image_path)

        default_image_path = os.path.join("resources", "drum_kits", "drums.png")
        # Fallback to default image if no specific image is found
        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def _update_pw_controls_state(self, waveform: Waveform):
        """Enable/disable PW controls based on waveform"""
        pw_enabled = waveform == Waveform.PULSE
        self.osc_pulse_width.setEnabled(pw_enabled)
        self.osc_pulse_width_mod_depth.setEnabled(pw_enabled)
        # Update the visual state
        self.osc_pulse_width.setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )
        self.osc_pulse_width_mod_depth.setStyleSheet(
            "" if pw_enabled else "QSlider::groove:vertical { background: #000000; }"
        )

    def _on_parameter_changed(
            self, param: Union[AnalogParameter], display_value: int
    ):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            if hasattr(param, "validate_value"):
                midi_value = param.validate_value(display_value)
            else:
                midi_value = display_value

            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=param.address,
                                        value=midi_value)
            return_value = self.midi_helper.send_midi_message(sysex_message)

            # Send MIDI message
            if not return_value:  # self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")

    def _create_parameter_slider(
            self,
            param: Union[AnalogParameter],
            label: str,
            vertical=False,
            show_value_label=True,
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max, vertical, show_value_label)

        # Set up bipolar parameters
        if param in self.bipolar_parameters or param.is_bipolar:
            # Set format string to show + sign for positive values
            slider.setValueDisplayFormat(lambda v: f"{v:+d}" if v != 0 else "0")
            # Set center tick
            slider.setCenterMark(0)
            # Add more prominent tick at center
            slider.setTickPosition(Slider.TickPosition.TicksBothSides)
            slider.setTickInterval((display_max - display_min) // 4)
            

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def on_amp_env_adsr_envelope_changed(self, envelope):
        """ Updating ADSR envelope controls"""
        if not self.updating_from_spinbox:
            self.controls[AnalogParameter.AMP_ENV_ATTACK_TIME].setValue(
                ms_to_midi_cc(envelope["attack_time"], 10, 1000)
            )
            self.controls[AnalogParameter.AMP_ENV_DECAY_TIME].setValue(
                ms_to_midi_cc(envelope["decay_time"], 10, 1000)
            )
            self.controls[AnalogParameter.AMP_ENV_SUSTAIN_LEVEL].setValue(
                ms_to_midi_cc(envelope["sustain_level"], 0.1, 1)
            )
            self.controls[AnalogParameter.AMP_ENV_RELEASE_TIME].setValue(
                ms_to_midi_cc(envelope["release_time"], 10, 1000)
            )

    def amp_env_adsr_value_changed(self):
        self.updating_from_spinbox = True
        self.amp_env_adsr_widget.envelope["attack_time"] = (
            self.amp_env_adsr_widget.attack_sb.value()
        )
        self.amp_env_adsr_widget.envelope["decay_time"] = (
            self.amp_env_adsr_widget.decay_sb.value()
        )
        self.amp_env_adsr_widget.envelope["release_time"] = (
            self.amp_env_adsr_widget.release_sb.value()
        )
        self.amp_env_adsr_widget.envelope["sustain_level"] = (
            self.amp_env_adsr_widget.sustain_sb.value()
        )
        self.amp_env_adsr_widget.plot.set_values(self.amp_env_adsr_widget.envelope)
        self.amp_env_adsr_widget.envelopeChanged.emit(self.amp_env_adsr_widget.envelope)
        self.updating_from_spinbox = False

    def _create_filter_section(self):
        """Create the filter section"""
        group = QWidget()
        layout = QVBoxLayout()
        group.setLayout(layout)

        # prettify with icons
        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.triangle-wave",
            "mdi.sine-wave",
            "fa5s.wave-square",
            "mdi.cosine-wave",
            "mdi.triangle-wave",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")  # Set icon color to grey
            pixmap = icon.pixmap(30, 30)  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Filter controls
        self.filter_switch = self._create_parameter_switch(AnalogParameter.FILTER_SWITCH,
                                                           "Filter",
                                                           ["BYPASS", "LPF"])
        layout.addWidget(self.filter_switch)
        self.filter_cutoff = self._create_parameter_slider(
            AnalogParameter.FILTER_CUTOFF, "Cutoff"
        )
        self.filter_resonance = self._create_parameter_slider(
            AnalogParameter.FILTER_RESONANCE, "Resonance"
        )
        self.filter_cutoff_keyfollow = self._create_parameter_slider(
            AnalogParameter.FILTER_CUTOFF_KEYFOLLOW, "Keyfollow"
        )
        self.filter_env_depth = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_DEPTH, "Depth"
        )

        self.filter_env_velocity_sens = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_VELOCITY_SENS, "Env. Velocity Sens."
        )
        layout.addWidget(self.filter_cutoff)
        layout.addWidget(self.filter_resonance)
        layout.addWidget(self.filter_cutoff_keyfollow)
        layout.addWidget(self.filter_env_depth)
        layout.addWidget(self.filter_env_velocity_sens)

        # Add spacing
        layout.addSpacing(10)

        # Generate the ADSR waveform icon
        icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        # Vbox to vertically arrange icons and ADSR(D) Envelope controls
        sub_layout = QVBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        sub_layout.addLayout(icons_hlayout)

        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR area
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)

        # Create ADSRWidget
        # self.filter_adsr_widget = ADSRWidget()
        self.filter_adsr_widget = ADSR(
            AnalogParameter.FILTER_ENV_ATTACK_TIME,
            AnalogParameter.FILTER_ENV_DECAY_TIME,
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
            AnalogParameter.FILTER_ENV_RELEASE_TIME,
            self.midi_helper,
            area=self.area,
            part=self.part,
            group=self.group
        )
        adsr_vlayout = QVBoxLayout()
        adsr_vlayout.addLayout(env_layout)
        env_layout.addWidget(self.filter_adsr_widget)
        env_layout.setStretchFactor(self.filter_adsr_widget, 5)

        # ADSR controls
        adsr_layout = QHBoxLayout()
        adsr_vlayout.addLayout(adsr_layout)

        self.filter_env_attack_time = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_ATTACK_TIME,
            "A",
            vertical=True,
            show_value_label=False,
        )
        self.filter_env_decay_time = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_DECAY_TIME,
            "D",
            vertical=True,
            show_value_label=False,
        )
        self.filter_env_sustain_level = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
            "S",
            vertical=True,
            show_value_label=False,
        )
        self.filter_env_release_time = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_RELEASE_TIME,
            "R",
            vertical=True,
            show_value_label=False,
        )
        sub_layout.addWidget(env_group)
        env_group.setLayout(adsr_vlayout)
        layout.addLayout(sub_layout)

        # Mapping ADSR parameters to their corresponding spinboxes
        self.filter_adsr_control_map = {
            AnalogParameter.FILTER_ENV_ATTACK_TIME: self.filter_adsr_widget.attack_sb,
            AnalogParameter.FILTER_ENV_DECAY_TIME: self.filter_adsr_widget.decay_sb,
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL: self.filter_adsr_widget.sustain_sb,
            AnalogParameter.FILTER_ENV_RELEASE_TIME: self.filter_adsr_widget.release_sb,
        }

        # 🔹 Connect ADSR spinboxes to external controls dynamically
        for param, spinbox in self.filter_adsr_control_map.items():
            spinbox.valueChanged.connect(partial(self.update_slider_from_adsr, param))

        # 🔹 Connect external controls to ADSR spinboxes dynamically
        for param, spinbox in self.filter_adsr_control_map.items():
            self.controls[param].valueChanged.connect(
                partial(
                    self.update_filter_adsr_spinbox_from_param,
                    self.filter_adsr_control_map,
                    param,
                )
            )

        return group

    def update_filter_adsr_spinbox_from_param(self, control_map, param, value):
        """Updates an ADSR parameter from an external control, avoiding feedback loops."""
        spinbox = control_map[param]
        if param in [
            AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
        ]:
            new_value = midi_cc_to_frac(value)
        else:
            new_value = midi_cc_to_ms(value)
        if spinbox.value() != new_value:
            spinbox.blockSignals(True)
            spinbox.setValue(new_value)
            spinbox.blockSignals(False)
            self.filter_adsr_widget.valueChanged()

    def _create_amp_section(self):
        """Create the Amp section"""
        group = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 15, 5, 5)
        group.setLayout(layout)

        icons_hlayout = QHBoxLayout()
        for icon in [
            "mdi.volume-variant-off",
            "mdi6.volume-minus",
            "mdi.amplifier",
            "mdi6.volume-plus",
            "mdi.waveform",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon, color="#666666")  # Set icon color to grey
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Level control
        self.amp_level = self._create_parameter_slider(
            AnalogParameter.AMP_LEVEL, "Level"
        )
        self.amp_level_keyfollow = self._create_parameter_slider(
            AnalogParameter.AMP_LEVEL_KEYFOLLOW, "Keyfollow"
        )
        layout.addWidget(self.amp_level)
        layout.addWidget(self.amp_level_keyfollow)

        # Add spacing
        layout.addSpacing(10)

        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR area
        # env_group.setMaximumHeight(300)
        amp_env_adsr_vlayout = QVBoxLayout()
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)
        env_layout.setContentsMargins(5, 15, 5, 5)
        env_group.setLayout(amp_env_adsr_vlayout)

        # Generate the ADSR waveform icon
        icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        # Vbox to vertically arrange icons and ADSR(D) Envelope controls
        sub_layout = QVBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        sub_layout.addLayout(icons_hlayout)
        self.amp_env_adsr_widget = ADSR(
            AnalogParameter.AMP_ENV_ATTACK_TIME,
            AnalogParameter.AMP_ENV_DECAY_TIME,
            AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
            AnalogParameter.AMP_ENV_RELEASE_TIME,
            self.midi_helper,
            area=self.area,
            part=self.part,
            group=self.group
        )
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        sub_layout.addWidget(env_group)
        layout.addLayout(sub_layout)
        return group

    def update_adsr_spinbox_from_param(self, control_map, param, value):
        """Updates an ADSR parameter from an external control, avoiding feedback loops."""
        spinbox = control_map[param]
        if param in [
            AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
        ]:
            new_value = midi_cc_to_frac(value)
        else:
            new_value = midi_cc_to_ms(value)
        if spinbox.value() != new_value:
            spinbox.blockSignals(True)
            spinbox.setValue(new_value)
            spinbox.blockSignals(False)
            self.amp_env_adsr_widget.valueChanged()

    def update_slider_from_adsr(self, param, value):
        """Updates external control from ADSR widget, avoiding infinite loops."""
        control = self.controls[param]
        if param in [
            AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
        ]:
            new_value = frac_to_midi_cc(value)
        else:
            new_value = ms_to_midi_cc(value)
        if control.value() != new_value:
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)

    def _create_lfo_section(self):
        """Create the LFO section"""
        group = QWidget()
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Replace the LFO Shape selector combo box with buttons
        shape_row = QHBoxLayout()
        shape_row.addWidget(QLabel("Shape"))
        shape_row.addStretch(1)  # Add stretch before buttons
        self.lfo_shape_buttons = {}

        # Create buttons for each LFO shape
        lfo_shapes = [
            ("TRI", "mdi.triangle-wave", 0),
            ("SIN", "mdi.sine-wave", 1),
            ("SAW", "mdi.sawtooth-wave", 2),
            ("SQR", "mdi.square-wave", 3),
            ("S&H", "mdi.waveform", 4),  # Sample & Hold
            ("RND", "mdi.wave", 5),  # Random
        ]

        for name, icon_name, value in lfo_shapes:
            btn = QPushButton(name)  # Add text to button
            btn.setCheckable(True)
            btn.setProperty("value", value)
            icon = qta.icon(icon_name)
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
            btn.setFixedSize(80, 40)  # Make buttons wider to accommodate text
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, v=value: self._on_lfo_shape_changed(v))
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)
            self.lfo_shape_buttons[value] = btn
            shape_row.addWidget(btn)
            shape_row.addStretch(1)  # Add stretch after each button

        layout.addLayout(shape_row)

        # Rate and Fade Time
        self.lfo_rate = self._create_parameter_slider(AnalogParameter.LFO_RATE, "Rate")

        self.lfo_fade = self._create_parameter_slider(
            AnalogParameter.LFO_FADE_TIME, "Fade Time"
        )

        # Tempo Sync controls
        sync_row = QHBoxLayout()
        self.lfo_sync_switch = self._create_parameter_switch(AnalogParameter.LFO_TEMPO_SYNC_SWITCH,
                                                             "Tempo Sync",
                                                             ["OFF", "ON"])
        sync_row.addWidget(self.lfo_sync_switch)

        self.lfo_sync_note_label = QLabel("Sync note")
        self.lfo_sync_note = self._create_parameter_combo_box(
            AnalogParameter.LFO_TEMPO_SYNC_NOTE, "", options=LFO_TEMPO_SYNC_NOTES, show_label=False
        )
        sync_row.addWidget(self.lfo_sync_note_label)
        sync_row.addWidget(self.lfo_sync_note)

        # Depth controls
        self.lfo_pitch = self._create_parameter_slider(
            AnalogParameter.LFO_PITCH_DEPTH, "Pitch Depth"
        )

        self.lfo_filter = self._create_parameter_slider(
            AnalogParameter.LFO_FILTER_DEPTH,
            "Filter Depth",
        )

        self.lfo_amp = self._create_parameter_slider(
            AnalogParameter.LFO_AMP_DEPTH, "Amp Depth"
        )

        # Key Trigger switch
        self.key_trigger_switch = self._create_parameter_switch(AnalogParameter.LFO_KEY_TRIGGER,
                                                                "Key Trigger",
                                                                ["OFF", "ON"])

        # Add all controls to layout
        layout.addWidget(self.lfo_rate)
        layout.addWidget(self.lfo_fade)
        layout.addLayout(sync_row)
        layout.addWidget(self.lfo_pitch)
        layout.addWidget(self.lfo_filter)
        layout.addWidget(self.lfo_amp)
        layout.addWidget(self.key_trigger_switch)

        return group

    def _on_waveform_selected(self, waveform: Waveform):
        """Handle waveform button selection KEEP!"""
        if self.midi_helper:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.OSC_WAVEFORM.value[0],
                                        value=waveform.midi_value)
            self.midi_helper.send_midi_message(sysex_message)

            for btn in self.wave_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Apply active style to the selected waveform button
            selected_btn = self.wave_buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)
            self._update_pw_controls_state(waveform)

    def send_control_change(self, control_change: AnalogControlChange, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
            # Convert enum to int if needed
            control_change_number = (
                control_change.value
                if isinstance(control_change, AnalogControlChange)
                else control_change
            )
            self.midi_helper.send_control_change(control_change_number, value, MIDI_CHANNEL_ANALOG)

    def _on_lfo_shape_changed(self, value: int):
        """Handle LFO shape change"""
        if self.midi_helper:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.LFO_SHAPE.value[0],
                                        value=value)
            self.midi_helper.send_midi_message(sysex_message)
            # Reset all buttons to default style
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Apply active style to the selected button
            selected_btn = self.lfo_shape_buttons.get(value)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)

    def _on_lfo_sync_changed(self, value: int):
        """
        Handle LFO sync change
        """
        if self.midi_helper:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.LFO_TEMPO_SYNC_SWITCH.value[0],
                                        value=value)
            self.midi_helper.send_midi_message(sysex_message)

    def _on_lfo_sync_note_changed(self, value: int):
        """
        Handle LFO sync note change
        """
        if self.midi_helper:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.LFO_TEMPO_SYNC_NOTE.value[0],
                                        value=value)
            self.midi_helper.send_midi_message(sysex_message)

    def _on_lfo_pitch_changed(self, value: int):
        """Handle LFO pitch depth change"""
        if self.midi_helper:
            # Convert -63 to +63 range to 1-127
            midi_value = value + 64 if value >= 0 else abs(value)
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.LFO_PITCH_DEPTH.value[0],
                                        value=midi_value)
            self.midi_helper.send_midi_message(sysex_message)

    def _on_lfo_filter_changed(self, value: int):
        """Handle LFO filter depth change"""
        if self.midi_helper:
            # Convert -63 to +63 range to 1-127
            midi_value = value + 64 if value >= 0 else abs(value)
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=AnalogParameter.LFO_FILTER_DEPTH.value[0],
                                        value=midi_value)
            self.midi_helper.send_midi_message(sysex_message)

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
            self._log_changes(self.previous_json_data, current_sysex_data)

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
        osc_waveform_map = {0: Waveform.SAW, 1: Waveform.TRIANGLE, 2: Waveform.PULSE}

        failures, successes = [], []

        def update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
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
                       AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
                       AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
                   ]
                else midi_cc_to_ms(value)
            )

            adsr_mapping = {
                AnalogParameter.AMP_ENV_ATTACK_TIME: self.amp_env_adsr_widget.attack_sb,
                AnalogParameter.AMP_ENV_DECAY_TIME: self.amp_env_adsr_widget.decay_sb,
                AnalogParameter.AMP_ENV_SUSTAIN_LEVEL: self.amp_env_adsr_widget.sustain_sb,
                AnalogParameter.AMP_ENV_RELEASE_TIME: self.amp_env_adsr_widget.release_sb,
                AnalogParameter.FILTER_ENV_ATTACK_TIME: self.filter_adsr_widget.attack_sb,
                AnalogParameter.FILTER_ENV_DECAY_TIME: self.filter_adsr_widget.decay_sb,
                AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL: self.filter_adsr_widget.sustain_sb,
                AnalogParameter.FILTER_ENV_RELEASE_TIME: self.filter_adsr_widget.release_sb,
            }

            if param in adsr_mapping:
                spinbox = adsr_mapping[param]
                spinbox.setValue(new_value)

        for param_name, param_value in current_sysex_data.items():
            param = AnalogParameter.get_by_name(param_name)

            if param: # @@
                if param_name in ["LFO_SHAPE", "LFO_PITCH_DEPTH", "LFO_FILTER_DEPTH", "LFO_AMP_DEPTH", "PULSE_WIDTH"]:
                    nrpn_address = next(
                        (addr for addr, name in nrpn_map.items() if name == param_name), None
                    )
                    if nrpn_address:
                        self._handle_nrpn_message(nrpn_address, param_value, channel=1)
                elif param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons:
                    self._update_lfo_shape_buttons(param_value)
                elif (
                        param_name == "SUB_OSCILLATOR_TYPE"
                        and param_value in sub_osc_type_map
                ):
                    self.sub_oscillator_type_switch.blockSignals(True)
                    self.sub_oscillator_type_switch.setValue(sub_osc_type_map[param_value])
                    self.sub_oscillator_type_switch.blockSignals(False)
                elif param_name == "OSC_WAVEFORM" and param_value in osc_waveform_map:
                    self._update_waveform_buttons(param_value)
                elif param_name == "FILTER_SWITCH" and param_value in filter_switch_map:
                    self.filter_switch.blockSignals(True)
                    self.filter_switch.setValue(filter_switch_map[param_value])
                    self.filter_switch.blockSignals(False)
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
            0: Waveform.SAW,
            1: Waveform.TRIANGLE,
            2: Waveform.PULSE,
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
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)

    def _update_lfo_shape_buttons(self, value):
        """Update the LFO shape buttons with visual feedback."""
        logging.debug(f"Updating LFO shape buttons with value {value}")

        # Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

        # Apply active style to the selected button
        selected_btn = self.lfo_shape_buttons.get(value)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_ANALOG_ACTIVE)
        else:
            logging.warning(f"Unknown LFO shape value: {value}")

    def send_analog_synth_parameter(self, parameter: str, value: int, channel: int = 0) -> bool:
        """
        Send a MIDI Control Change or NRPN message for an Analog Synth parameter.
    
        Args:
            parameter: The name of the parameter to modify.
            value: The parameter value (0-127).
            channel: The MIDI channel (0-15).
    
        Returns:
            True if successful, False otherwise.
        """
        # Define parameter mappings
        cc_parameters = {
            "Cutoff": 102,
            "Resonance": 105,
            "Level": 117,
            "LFO Rate": 16,
        }
    
        nrpn_parameters = {
            "Envelope": (0, 124),
            "LFO Shape": (0, 3),
            "LFO Pitch Depth": (0, 15),
            "LFO Filter Depth": (0, 18),
            "LFO Amp Depth": (0, 21),
            "Pulse Width": (0, 37),
        }
    
        if parameter in cc_parameters:
            # Send as a Control Change (CC) message
            controller = cc_parameters[parameter]
            return self.midi_helper.send_control_change(controller, value, channel)
    
        elif parameter in nrpn_parameters:
            # Send as an NRPN message
            msb, lsb = nrpn_parameters[parameter]
            return self.midi_helper.send_nrpn((msb << 7) | lsb, value, channel)
    
        else:
            logging.error(f"Invalid Analog Synth parameter: {parameter}")
            return False

    def _handle_nrpn_message(self, nrpn_address: int, value: int, channel: int):
        """Process incoming NRPN messages and update UI controls."""
        logging.info(f"Received NRPN {nrpn_address} with value {value} on channel {channel}")
    
        # NRPN Address Mapping
        nrpn_map = {
            (0, 124): "Envelope",
            (0, 3): "LFO Shape",
            (0, 15): "LFO Pitch Depth",
            (0, 18): "LFO Filter Depth",
            (0, 21): "LFO Amp Depth",
            (0, 37): "Pulse Width",
        }
    
        # Find matching parameter
        msb = nrpn_address >> 7
        lsb = nrpn_address & 0x7F
        param_name = nrpn_map.get((msb, lsb))
    
        if param_name:
            # Update slider or control
            param = AnalogParameter.get_by_name(param_name)
            if param:
                self._update_slider(param, value)
        else:
            logging.warning(f"Unrecognized NRPN {nrpn_address}")

    def _update_slider(self, param, value):
        """Safely update sliders from NRPN messages."""
        slider = self.controls.get(param)
        if slider:
            slider_value = param.convert_from_midi(value)
            slider.blockSignals(True)
            slider.setValue(slider_value)
            slider.blockSignals(False)
            logging.info(f"Updated {param.name} slider to {slider_value}")



