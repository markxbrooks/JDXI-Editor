import logging
import os
import re
import json
from functools import partial
from typing import Optional, Dict, Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QComboBox,
    QPushButton,
    QSlider, QTabWidget,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QShortcut, QKeySequence
import qtawesome as qta

from jdxi_manager.data.parameter.digital_common import DigitalCommonParameter
from jdxi_manager.data.preset_data import ANALOG_PRESETS, DIGITAL_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.data.analog import AnalogCommonParameter
from jdxi_manager.data.parameter.analog import AnalogParameter
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.conversions import (
    midi_cc_to_ms,
    midi_cc_to_frac,
    frac_to_midi_cc,
    ms_to_midi_cc,
)
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.ui.image_utils import base64_to_pixmap
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.adsr_widget import ADSRWidget
from jdxi_manager.ui.widgets.analog_waveform import AnalogWaveformButton
from jdxi_manager.ui.widgets.preset_combo_box import PresetComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import (
    WaveformButton,
    upsaw_png,
    triangle_png,
    pwsqu_png,
    adsr_waveform_icon,
)
from jdxi_manager.ui.widgets.switch import Switch
from jdxi_manager.midi.constants.analog import (
    AnalogToneCC,
    Waveform,
    SubOscType,
    ANALOG_SYNTH_AREA,
    ANALOG_PART,
    ANALOG_OSC_GROUP,
)

import base64

instrument_icon_folder = "analog_synths"


def get_analog_parameter_by_address(address: int):
    """Retrieve the DigitalParameter by its address."""
    logging.info(f"address: {address}")
    from jdxi_manager.data.analog import AnalogParameter

    for param in AnalogParameter:
        if param.address == address:
            logging.info(f"get_analog_parameter_by_address found param: {param}")
            return param
    return None


def get_analog_parameter_name_by_address(address: int):
    """Retrieve the DigitalParameter by its address."""
    logging.info(f"address: {address}")
    from jdxi_manager.data.analog import AnalogParameter

    for param in AnalogParameter:
        if param.address == address:
            logging.info(f"get_analog_parameter_by_address found param: {param}")
            return param.name
    return None


class AnalogSynthEditor(BaseEditor):
    """Analog Synth"""

    preset_changed = Signal(int, str, int)

    def __init__(self, midi_helper: Optional[MIDIHelper], parent=None):
        super().__init__(midi_helper, parent)
        self.part = ANALOG_PART
        self.preset_loader = None
        self.setWindowTitle("Analog Synth")
        self.previous_json_data = None
        # Allow resizing
        self.setMinimumSize(800, 400)
        self.resize(1000, 600)
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        self.main_window = parent
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.presets = ANALOG_PRESETS
        self.preset_type = PresetType.ANALOG
        self.midi_requests = [
            "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"
        ]
        # Create scroll area for resizable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Store parameter controls for easy access
        self.controls: Dict[Union[AnalogParameter, AnalogCommonParameter], QWidget] = {}
        self.updating_from_spinbox = False
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # Additional styling specific to analog editor
        self.setStyleSheet(Style.JDXI_ANALOG_TABS_STYLE + Style.ANALOG_EDITOR_STYLE_V3)
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
            width: 300px;
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
        self.instrument_selection_combo = PresetComboBox(ANALOG_PRESETS)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.main_window.analog_preset_handler.preset_changed.connect(
            self.update_combo_box_index
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
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
        self.tab_widget.addTab(self._create_oscillator_section(), qta.icon("mdi.triangle-wave", color='#666666'), "Oscillator")
        self.tab_widget.addTab(self._create_filter_section(), qta.icon("ri.filter-3-fill", color='#666666'), "Filter")
        self.tab_widget.addTab(self._create_amp_section(), qta.icon("mdi.amplifier", color='#666666'), "Amp")
        self.tab_widget.addTab(self._create_lfo_section(), qta.icon("mdi.sine-wave", color='#666666'), "LFO")

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect filter controls
        self.filter_cutoff.valueChanged.connect(
            lambda v: self._send_cc(AnalogParameter.FILTER_CUTOFF.value[0], v)
        )
        self.filter_resonance.valueChanged.connect(
            lambda v: self._send_cc(AnalogParameter.FILTER_RESONANCE.value[0], v)
        )
        self.midi_helper.json_sysex.connect(self._update_sliders_from_sysex)
        for param, slider in self.controls.items():
            if isinstance(slider, QSlider):  # Ensure it's a slider
                slider.setTickPosition(
                    QSlider.TickPosition.TicksBothSides
                )  # Tick marks on both sides
                slider.setTickInterval(10)  # Adjust interval as needed
        self.data_request()
        self.midi_helper.parameter_received.connect(self._on_parameter_received)
        # Initialize previous JSON data storage
        self.previous_json_data = None
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        if self.midi_helper:
            self.midi_helper.program_changed.connect(self._handle_program_change)

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        area_code = address[0]
        if address[0] == ANALOG_SYNTH_AREA:
            # Extract the actual parameter address (80, 0) from [25, 1, 80, 0]
            parameter_address = tuple(address[2:])  # (80, 0)

            # Retrieve the corresponding DigitalParameter
            param = get_analog_parameter_by_address(parameter_address)
            partial_no = address[1]
            if param:
                logging.info(
                    f"param: \t{param} \taddress=\t{address}, Value=\t{value}"
                )

                # Update the corresponding slider
                if param in self.controls:
                    slider_value = param.convert_from_midi(value)
                    logging.info(f"midi value {value} converted to slider value {slider_value}")
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
            btn.setStyleSheet(Style.ANALOG_BUTTON_DEFAULT)

            # Set icons for each waveform
            if waveform == Waveform.SAW:
                saw_icon_base64 = upsaw_png("#FFFFFF", 1.0)
                saw_pixmap = base64_to_pixmap(saw_icon_base64)
                btn.setIcon(QIcon(saw_pixmap))
            elif waveform == Waveform.TRIANGLE:
                tri_icon_base64 = triangle_png("#FFFFFF", 1.0)
                tri_pixmap = base64_to_pixmap(tri_icon_base64)
                btn.setIcon(QIcon(tri_pixmap))
            elif waveform == Waveform.PULSE:
                pulse_icon_base64 = pwsqu_png("#FFFFFF", 1.0)
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

        self.sub_type = Switch(
            "Type",
            [
                SubOscType.OFF.display_name,
                SubOscType.OCT_DOWN_1.display_name,
                SubOscType.OCT_DOWN_2.display_name,
            ],
        )
        self.sub_type.valueChanged.connect(self._on_sub_type_changed)
        sub_layout.addWidget(self.sub_type)
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

    def update_instrument_preset(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        if synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_synth_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            preset_index = int(selected_synth_padded_number)
            logging.info(f"preset_index: {preset_index}")
            self.load_preset(preset_index)

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
                    "resources", instrument_icon_folder, "analog.png"
                )
            pixmap = QPixmap(file_to_load)
            scaled_pixmap = pixmap.scaledToHeight(
                250, Qt.TransformationMode.SmoothTransformation
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
            logging.info(f"selected instrument image type: {selected_instrument_type}")
            specific_image_path = os.path.join(
                "resources",
                instrument_icon_folder,
                f"{selected_instrument_name}.png",
            )
            generic_image_path = os.path.join(
                "resources",
                instrument_icon_folder,
                f"{selected_instrument_type}.png",
            )
            image_loaded = load_and_set_image(specific_image_path, generic_image_path)

        # Fallback to default image if no specific image is found
        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def load_preset(self, preset_index):
        preset_data = {
            "type": self.preset_type,  # Ensure this is a valid type
            "selpreset": preset_index,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        if not self.preset_loader:
            self.preset_loader = PresetLoader(self.midi_helper)
        if self.preset_loader:
            self.preset_loader.load_preset(preset_data)

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

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter group and address with partial offset
            # if isinstance(param, AnalogParameter):
            #    group, param_address = param.get_address_for_partial(self.partial_num)
            # else:
            group = ANALOG_OSC_GROUP  # Common parameters group
            param_address = param.address

            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=self.part,
                group=group,
                param=param_address,
                value=value,  # Make sure this value is being sent
            )
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def _on_parameter_changed(
        self, param: Union[AnalogParameter, AnalogCommonParameter], display_value: int
    ):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)

            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def _create_parameter_slider(
        self,
        param: Union[AnalogParameter, AnalogCommonParameter],
        label: str,
        vertical=False,
    ) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max, vertical)
               
        # Set up bipolar parameters
        if isinstance(param, AnalogParameter) and param in [
            AnalogParameter.FILTER_CUTOFF_KEYFOLLOW,
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
            AnalogParameter.FILTER_ENV_DEPTH
            # Add other bipolar parameters as needed
        ]:
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
        if not self.updating_from_spinbox:
            self.controls[AnalogParameter.AMP_ENV_ATTACK_TIME].setValue(
                ms_to_midi_cc(envelope["attackTime"], 10, 1000)
            )
            self.controls[AnalogParameter.AMP_ENV_DECAY_TIME].setValue(
                ms_to_midi_cc(envelope["decayTime"], 10, 1000)
            )
            self.controls[AnalogParameter.AMP_ENV_SUSTAIN_LEVEL].setValue(
                ms_to_midi_cc(envelope["sustainAmpl"], 0.1, 1)
            )
            self.controls[AnalogParameter.AMP_ENV_RELEASE_TIME].setValue(
                ms_to_midi_cc(envelope["releaseTime"], 10, 1000)
            )

    def ampEnvAdsrValueChanged(self):
        self.updating_from_spinbox = True
        self.amp_env_adsr_widget.envelope["attackTime"] = (
            self.amp_env_adsr_widget.attack_sb.value()
        )
        self.amp_env_adsr_widget.envelope["decayTime"] = (
            self.amp_env_adsr_widget.decay_sb.value()
        )
        self.amp_env_adsr_widget.envelope["releaseTime"] = (
            self.amp_env_adsr_widget.release_sb.value()
        )
        self.amp_env_adsr_widget.envelope["initialAmpl"] = (
            self.amp_env_adsr_widget.initial_sb.value()
        )
        self.amp_env_adsr_widget.envelope["peakAmpl"] = (
            self.amp_env_adsr_widget.peak_sb.value()
        )
        self.amp_env_adsr_widget.envelope["sustainAmpl"] = (
            self.amp_env_adsr_widget.sustain_sb.value()
        )
        self.amp_env_adsr_widget.plot.set_values(self.amp_env_adsr_widget.envelope)
        self.amp_env_adsr_widget.envelopeChanged.emit(self.amp_env_adsr_widget.envelope)
        self.updating_from_spinbox = False

    def _create_filter_section(self):
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
            icon = qta.icon(icon, color='#666666')  # Set icon color to grey
            pixmap = icon.pixmap(30, 30)  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Filter controls
        self.filter_switch = Switch("Filter", ["BYPASS", "LPF"])
        self.filter_switch.valueChanged.connect(self._on_filter_switch_changed)
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
        icon_base64 = adsr_waveform_icon("#FFFFFF", 2.0)
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
        env_group.setProperty("adsr", True)  # Mark as ADSR group
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)

        # Create ADSRWidget
        self.filter_adsr_widget = ADSRWidget()

        adsr_vlayout = QVBoxLayout()
        adsr_vlayout.addLayout(env_layout)
        env_layout.addWidget(self.filter_adsr_widget)
        env_layout.setStretchFactor(self.filter_adsr_widget, 5)

        # ADSR controls
        adsr_layout = QHBoxLayout()
        adsr_vlayout.addLayout(adsr_layout)

        self.filter_env_attack_time = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_ATTACK_TIME, "A", vertical=True
        )
        self.filter_env_decay_time = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_DECAY_TIME, "D", vertical=True
        )
        self.filter_env_sustain_level = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL, "S", vertical=True
        )
        self.filter_env_release_time = self._create_parameter_slider(
            AnalogParameter.FILTER_ENV_RELEASE_TIME, "R", vertical=True
        )
        adsr_layout.addWidget(self.filter_env_attack_time)
        adsr_layout.addWidget(self.filter_env_decay_time)
        adsr_layout.addWidget(self.filter_env_sustain_level)
        adsr_layout.addWidget(self.filter_env_release_time)
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

    def _on_filter_switch_changed(self, value):
        """Handle filter switch change"""
        from jdxi_manager.data.parameter.analog import AnalogParameter

        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.FILTER_SWITCH.value[0],
                value=value,
            )

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
        group = QWidget()
        #group = QGroupBox("Amplifier")
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
            icon = qta.icon(icon, color='#666666')  # Set icon color to grey
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
        env_group.setProperty("adsr", True)  # Mark as ADSR group
        amp_env_adsr_vlayout = QVBoxLayout()
        env_layout = QHBoxLayout()
        env_layout.setSpacing(5)
        env_layout.setContentsMargins(5, 15, 5, 5)
        env_group.setLayout(amp_env_adsr_vlayout)

        # Generate the ADSR waveform icon
        icon_base64 = adsr_waveform_icon("#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        # Vbox to vertically arrange icons and ADSR(D) Envelope controls
        sub_layout = QVBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        sub_layout.addLayout(icons_hlayout)

        env_layout.addWidget(
            self._create_parameter_slider(
                AnalogParameter.AMP_ENV_ATTACK_TIME, "A", vertical=True
            )
        )
        env_layout.addWidget(
            self._create_parameter_slider(
                AnalogParameter.AMP_ENV_DECAY_TIME, "D", vertical=True
            )
        )
        env_layout.addWidget(
            self._create_parameter_slider(
                AnalogParameter.AMP_ENV_SUSTAIN_LEVEL, "S", vertical=True
            )
        )
        env_layout.addWidget(
            self._create_parameter_slider(
                AnalogParameter.AMP_ENV_RELEASE_TIME, "R", vertical=True
            )
        )
        self.amp_env_adsr_widget = ADSRWidget()
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        amp_env_adsr_vlayout.addLayout(env_layout)
        sub_layout.addWidget(env_group)
        layout.addLayout(sub_layout)

        # Mapping ADSR parameters to their corresponding spinboxes
        self.adsr_control_map = {
            AnalogParameter.AMP_ENV_ATTACK_TIME: self.amp_env_adsr_widget.attack_sb,
            AnalogParameter.AMP_ENV_DECAY_TIME: self.amp_env_adsr_widget.decay_sb,
            AnalogParameter.AMP_ENV_SUSTAIN_LEVEL: self.amp_env_adsr_widget.sustain_sb,
            AnalogParameter.AMP_ENV_RELEASE_TIME: self.amp_env_adsr_widget.release_sb,
        }

        # 🔹 Connect ADSR spinboxes to external controls dynamically
        for param, spinbox in self.adsr_control_map.items():
            spinbox.valueChanged.connect(partial(self.update_slider_from_adsr, param))

        # 🔹 Connect external controls to ADSR spinboxes dynamically
        for param, spinbox in self.adsr_control_map.items():
            self.controls[param].valueChanged.connect(
                partial(
                    self.update_adsr_spinbox_from_param, self.adsr_control_map, param
                )
            )

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
        group = QWidget()
        #group = QGroupBox("LFO")
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
            ("RND", "mdi.wave", 5),      # Random
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
            btn.setStyleSheet(Style.ANALOG_BUTTON_DEFAULT)
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

        self.lfo_sync_switch = Switch("Tempo Sync", ["OFF", "ON"])
        self.lfo_sync_switch.valueChanged.connect(self._on_lfo_sync_changed)
        sync_row.addWidget(self.lfo_sync_switch)

        self.sync_note = QComboBox()
        self.sync_note.addItems(
            [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
        )
        self.sync_note.currentIndexChanged.connect(self._on_lfo_sync_note_changed)
        sync_row.addWidget(self.sync_note)

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
        self.key_trig = Switch("Key Trigger", ["OFF", "ON"])
        self.key_trig.valueChanged.connect(self._on_lfo_key_trig_changed)

        # Add all controls to layout
        layout.addWidget(self.lfo_rate)
        layout.addWidget(self.lfo_fade)
        layout.addLayout(sync_row)
        layout.addWidget(self.lfo_pitch)
        layout.addWidget(self.lfo_filter)
        layout.addWidget(self.lfo_amp)
        layout.addWidget(self.key_trig)

        return group

    def _on_waveform_selected(self, waveform: Waveform):
        """Handle waveform button selection KEEP!"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.OSC_WAVEFORM.value[0],
                value=waveform.midi_value,
            )
            for btn in self.wave_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(Style.ANALOG_BUTTON_DEFAULT)

            # Apply active style to the selected waveform button
            selected_btn = self.wave_buttons.get(waveform)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(Style.ANALOG_BUTTON_ACTIVE)
            self._update_pw_controls_state(waveform)

    def _send_cc(self, cc: AnalogToneCC, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
            # Convert enum to int if needed
            cc_number = cc.value if isinstance(cc, AnalogToneCC) else cc
            self.midi_helper.send_cc(cc_number, value, channel=ANALOG_PART)

    def _on_sub_type_changed(self, value: int):
        """Handle sub oscillator type change"""
        if self.midi_helper:
            # Convert switch position to SubOscType enum
            sub_type = SubOscType(value)
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.SUB_OSCILLATOR_TYPE.value[0],
                value=sub_type.midi_value,
            )

    def _on_coarse_changed(self, value: int):
        """Handle coarse tune change"""
        if self.midi_helper:
            # Convert -24 to +24 range to MIDI value (0x28 to 0x58)
            midi_value = value + 63  # Center at 63 (0x3F)
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.OSC_PITCH_COARSE.value[0],
                value=midi_value,
            )

    def _on_lfo_shape_changed(self, value: int):
        """Handle LFO shape change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.LFO_SHAPE.value[0],
                value=value,
            )
            # Reset all buttons to default style
            for btn in self.lfo_shape_buttons.values():
                btn.setChecked(False)
                btn.setStyleSheet(Style.ANALOG_BUTTON_DEFAULT)

            # Apply active style to the selected button
            selected_btn = self.lfo_shape_buttons.get(value)
            if selected_btn:
                selected_btn.setChecked(True)
                selected_btn.setStyleSheet(Style.ANALOG_BUTTON_ACTIVE)

    def _on_lfo_sync_changed(self, value: int):
        """
        Handle LFO sync change
        KEEP
        """
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.LFO_TEMPO_SYNC_SWITCH.value[0],
                value=value,
            )

    def _on_lfo_sync_note_changed(self, value: int):
        """
        Handle LFO sync note change
        KEEP
        """
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.LFO_TEMPO_SYNC_NOTE.value[0],
                value=value,
            )

    def _on_lfo_pitch_changed(self, value: int):
        """Handle LFO pitch depth change"""
        if self.midi_helper:
            # Convert -63 to +63 range to 1-127
            midi_value = value + 64 if value >= 0 else abs(value)
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.LFO_PITCH_DEPTH.value[0],
                value=midi_value,
            )

    def _on_lfo_filter_changed(self, value: int):
        """Handle LFO filter depth change"""
        if self.midi_helper:
            # Convert -63 to +63 range to 1-127
            midi_value = value + 64 if value >= 0 else abs(value)
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.LFO_FILTER_DEPTH.value[0],
                value=midi_value,
            )

    def _on_lfo_key_trig_changed(self, value: int):
        """Handle LFO key trigger change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=ANALOG_OSC_GROUP,
                param=AnalogParameter.LFO_KEY_TRIG.value[0],
                value=value,
            )

    def send_message(self, message):
        """Send a SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def _update_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")

        try:
            current_sysex_data = json.loads(json_sysex_data)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON format: {e}")
            return

        # Compare with previous data and log changes
        if self.previous_json_data:
            self._log_changes(self.previous_json_data, current_sysex_data)

        # Store the current data for future comparison
        self.previous_json_data = current_sysex_data

        if current_sysex_data.get("TEMPORARY_AREA") != "ANALOG_SYNTH_AREA":
            logging.warning("SysEx data does not belong to ANALOG_SYNTH_AREA. Skipping update.")
            return

        # Remove unnecessary keys
        ignored_keys = {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"}
        current_sysex_data = {k: v for k, v in current_sysex_data.items() if k not in ignored_keys}

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
            new_value = midi_cc_to_frac(value) if param in [
                AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
                AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
            ] else midi_cc_to_ms(value)

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

            if param:
                if param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons:
                    self._update_lfo_shape_buttons(param_value)
                elif param_name == "SUB_OSCILLATOR_TYPE" and param_value in sub_osc_type_map:
                    self.sub_type.blockSignals(True)
                    self.sub_type.setValue(sub_osc_type_map[param_value])
                    self.sub_type.blockSignals(False)
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

    def _update_sliders_from_sysex_old(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")

        try:
            current_sysex_data = json.loads(json_sysex_data)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON format: {e}")
            return

        # Compare with previous data and log changes
        if self.previous_json_data:
            self._log_changes(self.previous_json_data, current_sysex_data)

        # Store the current data as previous for next comparison
        self.previous_json_data = current_sysex_data

        area = current_sysex_data.get("TEMPORARY_AREA", None)
        logging.info(f"TEMPORARY_AREA: {area}")

        if area != "ANALOG_SYNTH_AREA":
            logging.warning(
                "SysEx data does not belong to ANALOG_SYNTH_AREA. Skipping update."
            )
            return

        # Remove unnecessary keys
        for key in {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"}:
            current_sysex_data.pop(key, None)

        # Define mapping dictionaries
        lfo_shape_map = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        sub_osc_type_map = {0: 0, 1: 1, 2: 2}
        osc_waveform_map = {0: Waveform.SAW, 1: Waveform.TRIANGLE, 2: Waveform.PULSE}
        filter_switch_map = {0: 0, 1: 1}

        failures, successes = [], []

        for param_name, param_value in current_sysex_data.items():
            param = AnalogParameter.get_by_name(param_name)

            if param and param in self.controls:
                slider = self.controls[param]
                slider.blockSignals(True)
                # logging.info(f"Updating: {param:50} {param_value}")
                slider.setValue(param_value)
                slider.blockSignals(False)
                successes.append(param_name)

                if param in [
                    AnalogParameter.AMP_ENV_SUSTAIN_LEVEL,
                    AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL,
                ]:
                    new_value = midi_cc_to_frac(param_value)
                else:
                    new_value = midi_cc_to_ms(param_value)
                # Update ADSR parameters in their respective spin boxes
                if param == AnalogParameter.AMP_ENV_ATTACK_TIME:
                    self.amp_env_adsr_widget.attack_sb.setValue(new_value)
                elif param == AnalogParameter.AMP_ENV_DECAY_TIME:
                    self.amp_env_adsr_widget.decay_sb.setValue(new_value)
                elif param == AnalogParameter.AMP_ENV_SUSTAIN_LEVEL:
                    self.amp_env_adsr_widget.sustain_sb.setValue(new_value)
                elif param == AnalogParameter.AMP_ENV_RELEASE_TIME:
                    self.amp_env_adsr_widget.release_sb.setValue(new_value)

                # Update ADSR parameters in their respective spinboxes
                if param == AnalogParameter.FILTER_ENV_ATTACK_TIME:
                    self.filter_adsr_widget.attack_sb.setValue(new_value)
                elif param == AnalogParameter.FILTER_ENV_DECAY_TIME:
                    self.filter_adsr_widget.decay_sb.setValue(new_value)
                elif param == AnalogParameter.FILTER_ENV_SUSTAIN_LEVEL:
                    self.filter_adsr_widget.sustain_sb.setValue(new_value)
                elif param == AnalogParameter.FILTER_ENV_RELEASE_TIME:
                    self.filter_adsr_widget.release_sb.setValue(new_value)
                # logging.info(f"Updating ADSR spinbox: {param_name:50} {new_value}")

            elif param_name == "LFO_SHAPE" and param_value in self.lfo_shape_buttons:
                self._update_lfo_shape_buttons(param_value)

            elif (
                param_name == "SUB_OSCILLATOR_TYPE" and param_value in sub_osc_type_map
            ):
                index = sub_osc_type_map[param_value]
                if isinstance(index, int):
                    self.sub_type.blockSignals(True)
                    self.sub_type.setValue(index)
                    self.sub_type.blockSignals(False)

            elif param_name == "OSC_WAVEFORM" and param_value in osc_waveform_map:
                self._update_waveform_buttons(param_value)

            elif param_name == "FILTER_SWITCH" and param_value in filter_switch_map:
                index = filter_switch_map[param_value]
                self.filter_switch.blockSignals(True)
                self.filter_switch.setValue(index)
                self.filter_switch.blockSignals(False)

            else:
                failures.append(param_name)

        # Logging success rate
        success_rate = (
            (len(successes) / len(current_sysex_data) * 100)
            if current_sysex_data
            else 0
        )
        # logging.info(f"Successes: {successes}")
        # logging.info(f"Failures: {failures}")
        # logging.info(f"Success Rate: {success_rate:.1f}%")
        # logging.info("--------------------------------")

    def _log_changes(self, previous_data, current_data):
        """Log changes between previous and current JSON data."""
        changes = []
        for key, current_value in current_data.items():
            previous_value = previous_data.get(key)
            if previous_value != current_value:
                changes.append((key, previous_value, current_value))

        if changes:
            logging.info("Changes detected:")
            for key, prev, curr in changes:
                logging.info(f"Parameter: {key}, Previous: {prev}, Current: {curr}")
        else:
            logging.info("No changes detected.")

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
            btn.setStyleSheet(Style.ANALOG_BUTTON_DEFAULT)

        # Apply active style to the selected waveform button
        selected_btn = wave_buttons.get(selected_waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.ANALOG_BUTTON_ACTIVE)

    def _update_lfo_shape_buttons(self, value):
        """Update the LFO shape buttons with visual feedback."""
        logging.debug(f"Updating LFO shape buttons with value {value}")

        # Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.ANALOG_BUTTON_DEFAULT)

        # Apply active style to the selected button
        selected_btn = self.lfo_shape_buttons.get(value)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.ANALOG_BUTTON_ACTIVE)
        else:
            logging.warning(f"Unknown LFO shape value: {value}")
