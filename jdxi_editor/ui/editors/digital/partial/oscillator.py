"""
Digital Oscillator Section for the JDXI Editor
"""

import logging
from typing import Callable
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QComboBox,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.digital.oscillator import DigitalOscWave
from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.digital.partial import AddressParameterDigitalPartial
from jdxi_editor.midi.data.pcm.waves import PCM_WAVES_CATEGORIZED
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.pwm import PWMWidget
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.button.waveform.waveform import WaveformButton
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from jdxi_editor.ui.widgets.slider import Slider


class PulseWidthModWidget(QWidget):
    def __init__(self,
                 width_param: AddressParameter,
                 mod_depth_param: AddressParameter,
                 shift_param: AddressParameter,
                 midi_helper: MidiIOHelper,
                 controls,
                 address: RolandSysExAddress,
                 create_parameter_slider: Callable,
                 parent: QWidget = None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.controls = controls
        self.address = address

        layout = QVBoxLayout(self)

        self._create_parameter_slider = create_parameter_slider

        # Pulse Width (% of cycle)
        self.width_slider = self._create_parameter_slider(
            width_param, "Width (% of cycle)"
        )
        layout.addWidget(self.width_slider)

        # Mod Depth (LFO applied)
        self.mod_depth_slider = self._create_parameter_slider(
            mod_depth_param, "Mod Depth (of LFO applied)"
        )
        layout.addWidget(self.mod_depth_slider)

        # Pulse Width Shift
        self.shift_slider = self._create_parameter_slider(
            shift_param, "PW Shift"
        )
        layout.addWidget(self.shift_slider)

        self.setLayout(layout)

    def _create_parameter_slider(
            self,
            param: AddressParameter,
            label: str,
            value: int = None) -> Slider:
        """
        Create address slider for address parameter with proper display conversion
        :param param: AddressParameter
        :param label: str
        :param value: int
        :return: Slider
        """
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        # Create vertical slider
        slider = Slider(
            label,
            min_value=display_min,
            max_value=display_max,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=False,
            is_bipolar=param.is_bipolar,
        )
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(
            lambda v, s=slider: self.update_envelope_from_slider(s)
        )
        slider.valueChanged.connect(lambda v: self.send_parameter_message(param, v))
        self.controls[param] = slider
        return slider


class DigitalOscillatorSection(QWidget):
    """Digital Oscillator Section for the JDXI Editor"""

    def __init__(
            self,
            create_parameter_slider: Callable,
            create_parameter_switch: Callable,
            create_parameter_combo_box: Callable,
            send_midi_parameter: Callable,
            partial_number: int,
            midi_helper: MidiIOHelper,
            controls: dict[AddressParameter, QWidget],
            address: RolandSysExAddress,
    ):
        super().__init__()
        self.pwm_widget = None
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.send_midi_parameter = send_midi_parameter
        self.address = address
        self.setup_ui()
        log.parameter(f"initialization complete for", self)

    def setup_ui(self):
        """Setup the oscillator section UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Top row: Waveform buttons and variation switch
        top_row = QHBoxLayout()
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}

        wave_icons = {
            DigitalOscWave.SAW: generate_waveform_icon("upsaw", "#FFFFFF", 1.0),
            DigitalOscWave.SQUARE: generate_waveform_icon("square", "#FFFFFF", 1.0),
            DigitalOscWave.PW_SQUARE: generate_waveform_icon("pwsqu", "#FFFFFF", 1.0),
            DigitalOscWave.TRIANGLE: generate_waveform_icon("triangle", "#FFFFFF", 1.0),
            DigitalOscWave.SINE: generate_waveform_icon("sine", "#FFFFFF", 1.0),
            DigitalOscWave.NOISE: generate_waveform_icon("noise", "#FFFFFF", 1.0),
            DigitalOscWave.SUPER_SAW: generate_waveform_icon("spsaw", "#FFFFFF", 1.0),
            DigitalOscWave.PCM: generate_waveform_icon("pcm", "#FFFFFF", 1.0),
        }

        for wave, icon_base64 in wave_icons.items():
            btn = WaveformButton(wave)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)
            btn.setFixedSize(60, 30)
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))
            self.wave_buttons[wave] = btn
            self.controls[AddressParameterDigitalPartial.OSC_WAVE] = btn
            wave_layout.addWidget(btn)

        top_row.addLayout(wave_layout)
        self.wave_variation_switch = self._create_parameter_switch(
            AddressParameterDigitalPartial.OSC_WAVE_VARIATION,
            "Variation",
            ["A", "B", "C"],
        )
        top_row.addWidget(self.wave_variation_switch)
        layout.addLayout(top_row)

        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)
        tuning_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.OSC_PITCH, "Pitch (1/2 tones)"
            )
        )
        tuning_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.OSC_DETUNE, "Detune (cents)"
            )
        )
        layout.addWidget(tuning_group)

        # Pulse Width controls
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        #self.pw_slider = self._create_parameter_slider(
        #    AddressParameterDigitalPartial.OSC_PULSE_WIDTH, "Width (% of cycle)"
        #)
        #self.pw_mod_slider = self._create_parameter_slider(
        #    AddressParameterDigitalPartial.OSC_PULSE_WIDTH_MOD_DEPTH,
        #    "Mod Depth (of LFO applied)",
        #)
        self.pw_shift_slider = self._create_parameter_slider(
            AddressParameterDigitalPartial.OSC_PULSE_WIDTH_SHIFT,
            "Shift (range of change)",
        )
        # pw_layout.addWidget(self.pw_slider)
        # pw_layout.addWidget(self.pw_mod_slider)

        self.pwm_widget = PWMWidget(pulse_width_param=AddressParameterDigitalPartial.OSC_PULSE_WIDTH,
                                    mod_depth_param=AddressParameterDigitalPartial.OSC_PULSE_WIDTH_MOD_DEPTH,
                                    midi_helper=self.midi_helper,
                                    address=self.address,
                                    controls=self.controls)
        self.pwm_widget.setStyleSheet(JDXiStyle.ADSR)
        self.pwm_widget.setMaximumHeight(JDXiStyle.PWM_WIDGET_HEIGHT)
        pw_layout.addWidget(self.pwm_widget)

        pw_layout.addWidget(self.pw_shift_slider)

        layout.addWidget(pw_group)

        # PCM Wave controls
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QGridLayout()
        pcm_group.setLayout(pcm_layout)
        self.pcm_wave_gain = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.PCM_WAVE_GAIN,
            "Gain [dB]",
            ["-6", "0", "+6", "+12"],
        )
        self.pcm_wave_number = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.PCM_WAVE_NUMBER,
            "Number",
            [f"{w['Wave Number']}: {w['Wave Name']}" for w in PCM_WAVES_CATEGORIZED],
        )
        self.pcm_category_combo = QComboBox()
        self.pcm_categories = ["No selection"] + sorted(
            set(w["Category"] for w in PCM_WAVES_CATEGORIZED)
        )
        self.pcm_category_combo.addItems(self.pcm_categories)
        self.pcm_category_combo.currentIndexChanged.connect(self.update_waves)
        pcm_layout.addWidget(self.pcm_wave_gain, 0, 0)
        pcm_layout.addWidget(QLabel("Category"), 0, 1)
        pcm_layout.addWidget(self.pcm_category_combo, 0, 2)
        pcm_layout.addWidget(self.pcm_wave_number, 0, 3)
        layout.addWidget(pcm_group)

        # Super Saw controls
        super_saw_group = QGroupBox("Super Saw")
        super_saw_layout = QVBoxLayout()
        super_saw_group.setLayout(super_saw_layout)
        self.super_saw_detune = self._create_parameter_slider(
            AddressParameterDigitalPartial.SUPER_SAW_DETUNE, "S-Saw Detune"
        )
        super_saw_layout.addWidget(self.super_saw_detune)
        layout.addWidget(super_saw_group)

        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)
        # Pitch Env Widget
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=AddressParameterDigitalPartial.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=AddressParameterDigitalPartial.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=AddressParameterDigitalPartial.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            controls=self.controls,
            address=self.address,
        )
        self.pitch_env_widget.setStyleSheet(JDXiStyle.ADSR)
        pitch_env_layout.addWidget(self.pitch_env_widget)
        layout.addWidget(pitch_env_group)

        # Initialize states
        self._update_pw_controls_enabled_state(DigitalOscWave.SAW)
        self._update_pcm_controls_enabled_state(DigitalOscWave.PCM)
        self._update_supersaw_controls_enabled_state(DigitalOscWave.PCM)

    def _on_waveform_selected(self, waveform: DigitalOscWave):
        """Handle waveform button clicks"""
        # Reset all buttons to default style
        for btn in self.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = self.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if not self.send_midi_parameter(
                AddressParameterDigitalPartial.OSC_WAVE, waveform.value
        ):
            logging.warning(f"Failed to set waveform to {waveform.name}")

        self._update_waveform_controls_enabled_states(waveform)

    def _update_waveform_controls_enabled_states(self, waveform: DigitalOscWave):
        """
        _update_waveform_controls_states
        :param waveform: DigitalOscWave
        :return: None

        Update control visibility and enabled state based on the selected waveform.
        """
        self._update_pw_controls_enabled_state(waveform)
        self._update_pcm_controls_enabled_state(waveform)
        self._update_supersaw_controls_enabled_state(waveform)

    def update_waves(self):
        """Update PCM waves based on selected category"""
        selected_category = self.pcm_category_combo.currentText()

        # Filter waves or show all if "No selection"
        if selected_category == "No selection":
            filtered_waves = PCM_WAVES_CATEGORIZED  # Show all waves
        else:
            filtered_waves = [
                w for w in PCM_WAVES_CATEGORIZED if w["Category"] == selected_category
            ]

        # Update wave combo box
        self.pcm_wave_number.combo_box.clear()
        self.pcm_wave_number.combo_box.addItems(
            [f"{w['Wave Number']}: {w['Wave Name']}" for w in filtered_waves]
        )
        self.pcm_wave_number.values = [w["Wave Number"] for w in filtered_waves]

    def _update_pw_controls_enabled_state(self, waveform: DigitalOscWave):
        """Update pulse width controls enabled state based on waveform"""
        pass
        pw_enabled = waveform == DigitalOscWave.PW_SQUARE
        """self.pw_slider.setEnabled(pw_enabled)
        self.pw_mod_slider.setEnabled(pw_enabled)"""
        self.pw_shift_slider.setEnabled(pw_enabled)

    def _update_pcm_controls_enabled_state(self, waveform: DigitalOscWave):
        """Update PCM wave controls visibility based on waveform"""
        pcm_enabled = waveform == DigitalOscWave.PCM
        self.pcm_wave_gain.setEnabled(pcm_enabled)
        self.pcm_category_combo.setEnabled(pcm_enabled)
        self.pcm_wave_number.setEnabled(pcm_enabled)

    def _update_supersaw_controls_enabled_state(self, waveform: DigitalOscWave):
        """Update supersaw controls visibility based on waveform"""
        supersaw_enabled = waveform == DigitalOscWave.SUPER_SAW
        self.super_saw_detune.setEnabled(supersaw_enabled)
