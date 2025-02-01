import logging
import time
from typing import Dict, Optional, Union
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QTabWidget,
    QScrollArea,
    QSpinBox,
    QLabel,
    QComboBox,
    QFormLayout,
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QIcon, QPixmap
import base64
from io import BytesIO
import qtawesome as qta

from jdxi_manager.data.preset_data import DIGITAL_PRESETS, ANALOG_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.preset_loader import PresetLoader
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.adsr_widget import ADSRWidget
from jdxi_manager.ui.widgets.preset_combo_box import PresetComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import (
    WaveformButton,
    pwsqu_png,
    triangle_png,
    upsaw_png,
    square_png,
    sine_png,
    noise_png,
    spsaw_png,
    pcm_png,
    adsr_waveform_icon,
)
from jdxi_manager.data.digital import (
    DigitalParameter,
    DigitalCommonParameter,
    OscWave,
    DigitalPartial,
    set_partial_state,
    get_partial_state,
)
from jdxi_manager.midi.constants import DIGITAL_SYNTH_AREA, PART_1, PART_2
from jdxi_manager.ui.widgets.partial_switch import PartialsPanel
from jdxi_manager.ui.widgets.switch import Switch
import os
import re


instrument_icon_folder = "digital_synths"


class PartialEditor(QWidget):
    """Editor for a single partial"""

    def __init__(self, midi_helper=None, partial_num=1, part=PART_1, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_num = partial_num
        self.part = part

        # Store parameter controls for easy access
        self.controls: Dict[
            Union[DigitalParameter, DigitalCommonParameter], QWidget
        ] = {}

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        # Add sections in a vertical layout
        container_layout.addWidget(self._create_oscillator_section())
        container_layout.addWidget(self._create_filter_section())
        container_layout.addWidget(self._create_amp_section())
        container_layout.addWidget(self._create_lfo_section())
        container_layout.addWidget(self._create_mod_lfo_section())

        # Add container to scroll area
        main_layout.addWidget(container)

    def _create_parameter_slider(
        self, param: Union[DigitalParameter, DigitalCommonParameter], label: str
    ) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def _create_oscillator_section(self):
        group = QGroupBox("Oscillator")
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
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Top row: Waveform buttons and variation
        top_row = QHBoxLayout()

        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}
        for wave in [
            OscWave.SAW,
            OscWave.SQUARE,
            OscWave.PW_SQUARE,
            OscWave.TRIANGLE,
            OscWave.SINE,
            OscWave.NOISE,
            OscWave.SUPER_SAW,
            OscWave.PCM,
        ]:
            btn = WaveformButton(wave)
            if wave == OscWave.SAW:
                saw_wave_icon_base64 = upsaw_png("#FFFFFF", 1.0)
                saw_wave_pixmap = base64_to_pixmap(saw_wave_icon_base64)
                btn.setIcon(QIcon(saw_wave_pixmap))
            elif wave == OscWave.SQUARE:
                square_wave_icon_base64 = square_png("#FFFFFF", 1.0)
                square_wave_pixmap = base64_to_pixmap(square_wave_icon_base64)
                btn.setIcon(QIcon(square_wave_pixmap))
            elif wave == OscWave.SINE:
                sine_wave_icon_base64 = sine_png("#FFFFFF", 1.0)
                sine_wave_pixmap = base64_to_pixmap(sine_wave_icon_base64)
                btn.setIcon(QIcon(sine_wave_pixmap))
            elif wave == OscWave.NOISE:
                noise_wave_icon_base64 = noise_png("#FFFFFF", 1.0)
                noise_wave_pixmap = base64_to_pixmap(noise_wave_icon_base64)
                btn.setIcon(QIcon(noise_wave_pixmap))
            elif wave == OscWave.SUPER_SAW:
                super_saw_wave_icon_base64 = spsaw_png("#FFFFFF", 1.0)
                super_saw_wave_pixmap = base64_to_pixmap(super_saw_wave_icon_base64)
                btn.setIcon(QIcon(super_saw_wave_pixmap))
            elif wave == OscWave.PCM:
                pcm_wave_icon_base64 = pcm_png("#FFFFFF", 1.0)
                pcm_wave_pixmap = base64_to_pixmap(pcm_wave_icon_base64)
                btn.setIcon(QIcon(pcm_wave_pixmap))
            elif wave == OscWave.PW_SQUARE:
                pw_square_wave_icon_base64 = pwsqu_png("#FFFFFF", 1.0)
                pw_square_wave_pixmap = base64_to_pixmap(pw_square_wave_icon_base64)
                btn.setIcon(QIcon(pw_square_wave_pixmap))
            elif wave == OscWave.TRIANGLE:
                triangle_wave_icon_base64 = triangle_png("#FFFFFF", 1.0)
                triangle_wave_pixmap = base64_to_pixmap(triangle_wave_icon_base64)
                btn.setIcon(QIcon(triangle_wave_pixmap))
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))
            self.wave_buttons[wave] = btn
            wave_layout.addWidget(btn)
        top_row.addLayout(wave_layout)

        # Wave variation switch
        self.wave_var = Switch("Var", ["A", "B", "C"])
        self.wave_var.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.OSC_WAVE_VAR, v)
        )
        top_row.addWidget(self.wave_var)
        layout.addLayout(top_row)

        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        tuning_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.OSC_PITCH, "Pitch")
        )
        tuning_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.OSC_DETUNE, "Detune")
        )
        layout.addWidget(tuning_group)

        # Pulse Width controls (only enabled for PW-SQUARE wave)
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        self.pw_slider = self._create_parameter_slider(DigitalParameter.OSC_PW, "Width")
        self.pwm_slider = self._create_parameter_slider(
            DigitalParameter.OSC_PWM_DEPTH, "Mod"
        )
        pw_layout.addWidget(self.pw_slider)
        pw_layout.addWidget(self.pwm_slider)
        layout.addWidget(pw_group)

        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        pitch_env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.OSC_PITCH_ATTACK, "Attack")
        )
        pitch_env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.OSC_PITCH_DECAY, "Decay")
        )
        pitch_env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.OSC_PITCH_DEPTH, "Depth")
        )
        layout.addWidget(pitch_env_group)

        # Wave gain control
        self.wave_gain = Switch("Gain", ["-6dB", "0dB", "+6dB", "+12dB"])
        self.wave_gain.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.WAVE_GAIN, v)
        )
        layout.addWidget(self.wave_gain)

        # Super Saw detune (only for SUPER-SAW wave)
        self.super_saw_detune = self._create_parameter_slider(
            DigitalParameter.SUPER_SAW_DETUNE, "S-Saw Detune"
        )
        layout.addWidget(self.super_saw_detune)

        # Update PW controls enabled state when waveform changes
        self._update_pw_controls_state(OscWave.SAW)  # Initial state

        # PCM Wave number selector (only for PCM wave)
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QVBoxLayout()
        pcm_group.setLayout(pcm_layout)

        # Wave number spinner/selector
        wave_row = QHBoxLayout()
        self.wave_number = QSpinBox()
        self.wave_number.setRange(0, 16384)
        self.wave_number.setValue(0)
        self.wave_number.valueChanged.connect(self._on_wave_number_changed)
        wave_row.addWidget(QLabel("Number:"))
        wave_row.addWidget(self.wave_number)
        pcm_layout.addLayout(wave_row)

        layout.addWidget(pcm_group)
        pcm_group.setVisible(False)  # Hide initially
        self.pcm_group = pcm_group  # Store reference for visibility control

        return group

    def _update_pw_controls_state(self, waveform: OscWave):
        """Update pulse width controls enabled state based on waveform"""
        pw_enabled = waveform == OscWave.PW_SQUARE
        self.pw_slider.setEnabled(pw_enabled)
        self.pwm_slider.setEnabled(pw_enabled)

    def _update_pcm_controls_state(self, waveform: OscWave):
        """Update PCM wave controls visibility based on waveform"""
        self.pcm_group.setVisible(waveform == OscWave.PCM)

    def _on_wave_number_changed(self, value: int):
        """Handle wave number changes"""
        try:
            # Send wave number in 4-bit chunks
            b1 = (value >> 12) & 0x0F  # Most significant 4 bits
            b2 = (value >> 8) & 0x0F  # Next 4 bits
            b3 = (value >> 4) & 0x0F  # Next 4 bits
            b4 = value & 0x0F  # Least significant 4 bits

            # Send each byte
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_1, b1)
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_2, b2)
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_3, b3)
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_4, b4)

        except Exception as e:
            logging.error(f"Error setting wave number: {str(e)}")

    def _create_filter_section(self):
        group = QGroupBox("Filter")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # prettify with icons
        icon_hlayout = QHBoxLayout()
        for icon in ["mdi.sine-wave", "ri.filter-3-fill", "mdi.waveform"]:
            icon_label = QLabel()
            icon = qta.icon(icon)
            pixmap = icon.pixmap(30, 30)  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icon_hlayout.addWidget(icon_label)
        layout.addLayout(icon_hlayout)

        # Filter type controls
        type_row = QHBoxLayout()

        # Filter mode switch
        self.filter_mode = Switch(
            "Mode", ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"]
        )
        self.filter_mode.valueChanged.connect(lambda v: self._on_filter_mode_changed(v))
        type_row.addWidget(self.filter_mode)

        # Filter slope switch
        self.filter_slope = Switch("Slope", ["-12dB", "-24dB"])
        self.filter_slope.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.FILTER_SLOPE, v)
        )
        type_row.addWidget(self.filter_slope)
        layout.addLayout(type_row)

        # Main filter controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_CUTOFF, "Cutoff")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.FILTER_RESONANCE, "Resonance"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.FILTER_KEYFOLLOW, "KeyFollow"
            )
        )
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_VELOCITY, "Velocity")
        )
        layout.addWidget(controls_group)

        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR group
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)

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

        # Create ADSRWidget
        self.adsr_widget = ADSRWidget()
        # self.adsr_widget.envelopeChanged.connect(self.on_adsr_envelope_changed)
        # sub_layout.addWidget(self.adsr_widget)

        # ADSR controls
        adsr_layout = QHBoxLayout()
        adsr_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_ENV_ATTACK, "A")
        )
        adsr_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_ENV_DECAY, "D")
        )
        adsr_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_ENV_SUSTAIN, "S")
        )
        adsr_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_ENV_RELEASE, "R")
        )
        env_layout.addLayout(adsr_layout)

        # Envelope depth
        env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_ENV_DEPTH, "Depth")
        )
        sub_layout.addWidget(env_group)
        layout.addLayout(sub_layout)
        # HPF cutoff
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.HPF_CUTOFF, "HPF Cutoff")
        )

        # Aftertouch sensitivity
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.CUTOFF_AFTERTOUCH, "AT Sens")
        )

        return group

    def _on_filter_mode_changed(self, mode: int):
        """Handle filter mode changes"""
        # Send MIDI message
        self._on_parameter_changed(DigitalParameter.FILTER_MODE, mode)

        # Update control states
        self._update_filter_controls_state(mode)

    def _update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = mode != 0  # Enable if not BYPASS
        for param in [
            DigitalParameter.FILTER_CUTOFF,
            DigitalParameter.FILTER_RESONANCE,
            DigitalParameter.FILTER_KEYFOLLOW,
            DigitalParameter.FILTER_VELOCITY,
            DigitalParameter.FILTER_ENV_ATTACK,
            DigitalParameter.FILTER_ENV_DECAY,
            DigitalParameter.FILTER_ENV_SUSTAIN,
            DigitalParameter.FILTER_ENV_RELEASE,
            DigitalParameter.FILTER_ENV_DEPTH,
            DigitalParameter.FILTER_SLOPE,
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)

    def _create_amp_section(self):
        group = QGroupBox("Amplifier")
        layout = QVBoxLayout()
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
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Level and velocity controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)

        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_LEVEL, "Level")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_VELOCITY, "Velocity")
        )

        # Create and center the pan slider
        pan_slider = self._create_parameter_slider(DigitalParameter.AMP_PAN, "Pan")
        pan_slider.setValue(0)  # Center the pan slider
        controls_layout.addWidget(pan_slider)

        layout.addWidget(controls_group)

        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)  # Mark as ADSR group
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)

        # Generate the ADSR waveform icon
        icon_base64 = adsr_waveform_icon("#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_ENV_ATTACK, "A")
        )
        env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_ENV_DECAY, "D")
        )
        env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_ENV_SUSTAIN, "S")
        )
        env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_ENV_RELEASE, "R")
        )

        layout.addWidget(env_group)

        # Keyfollow and aftertouch
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_KEYFOLLOW, "KeyFollow")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LEVEL_AFTERTOUCH, "AT Sens")
        )

        return group

    def _create_lfo_section(self):
        group = QGroupBox("LFO")
        layout = QVBoxLayout()
        group.setLayout(layout)

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
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Shape and sync controls
        top_row = QHBoxLayout()

        # Shape switch
        self.lfo_shape = Switch("Shape", ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        self.lfo_shape.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.LFO_SHAPE, v)
        )
        top_row.addWidget(self.lfo_shape)

        # Sync switch
        self.lfo_sync = Switch("Sync", ["OFF", "ON"])
        self.lfo_sync.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.LFO_SYNC, v)
        )
        top_row.addWidget(self.lfo_sync)
        layout.addLayout(top_row)

        # Rate and fade controls
        layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LFO_RATE, "Rate")
        )
        layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LFO_FADE, "Fade")
        )

        # Key trigger switch
        self.lfo_trigger = Switch("Key Trigger", ["OFF", "ON"])
        self.lfo_trigger.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.LFO_TRIGGER, v)
        )
        layout.addWidget(self.lfo_trigger)

        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)

        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LFO_PITCH, "Pitch")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LFO_FILTER, "Filter")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LFO_AMP, "Amp")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LFO_PAN, "Pan")
        )
        layout.addWidget(depths_group)

        return group

    def _create_mod_lfo_section(self):
        """Create modulation LFO section"""
        group = QGroupBox("Mod LFO")
        layout = QVBoxLayout()
        group.setLayout(layout)

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
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Shape and sync controls
        top_row = QHBoxLayout()

        # Shape switch
        self.mod_lfo_shape = Switch("Shape", ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        self.mod_lfo_shape.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.MOD_LFO_SHAPE, v)
        )
        top_row.addWidget(self.mod_lfo_shape)

        # Sync switch
        self.mod_lfo_sync = Switch("Sync", ["OFF", "ON"])
        self.mod_lfo_sync.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.MOD_LFO_SYNC, v)
        )
        top_row.addWidget(self.mod_lfo_sync)
        layout.addLayout(top_row)

        # Rate and note controls
        rate_row = QHBoxLayout()
        rate_row.addWidget(
            self._create_parameter_slider(DigitalParameter.MOD_LFO_RATE, "Rate")
        )

        # Note selection (only visible when sync is ON)
        self.mod_lfo_note = Switch(
            "Note",
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
            ],
        )
        self.mod_lfo_note.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.MOD_LFO_NOTE, v)
        )
        rate_row.addWidget(self.mod_lfo_note)
        layout.addLayout(rate_row)

        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)

        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.MOD_LFO_PITCH, "Pitch")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.MOD_LFO_FILTER, "Filter")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.MOD_LFO_AMP, "Amp")
        )
        depths_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.MOD_LFO_PAN, "Pan")
        )
        layout.addWidget(depths_group)

        # Rate control
        layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.MOD_LFO_RATE_CTRL, "Rate Ctrl"
            )
        )

        return group

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter group and address with partial offset
            if isinstance(param, DigitalParameter):
                group, param_address = param.get_address_for_partial(self.partial_num)
            else:
                group = 0x00  # Common parameters group
                param_address = param.address

            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=group,
                param=param_address,
                value=value,  # Make sure this value is being sent
            )
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def _on_parameter_changed(
        self, param: Union[DigitalParameter, DigitalCommonParameter], display_value: int
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

    def _on_waveform_selected(self, waveform: OscWave):
        """Handle waveform button clicks"""
        # Update button states
        for wave, btn in self.wave_buttons.items():
            btn.setChecked(wave == waveform)

        # Send MIDI message
        if not self.send_midi_parameter(DigitalParameter.OSC_WAVE, waveform.value):
            logging.warning(f"Failed to set waveform to {waveform.name}")

        # Update control visibility
        self._update_pw_controls_state(waveform)
        self._update_pcm_controls_state(waveform)


class DigitalSynthEditor(BaseEditor):
    """class for Digital Synth Editor containing 3 partials"""

    preset_changed = Signal(int, str, int)

    def __init__(
        self,
        midi_helper: Optional[MIDIHelper] = None,
        synth_num=1,
        parent=None,
        preset_handler=None,
    ):
        super().__init__(parent)
        # Image display
        self.preset_type = (
            PresetType.DIGITAL_1 if synth_num == 1 else PresetType.DIGITAL_2
        )
        self.presets = DIGITAL_PRESETS
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image

        self.midi_helper = midi_helper
        self.preset_loader = PresetLoader(self.midi_helper)
        if preset_handler:
            self.preset_handler = preset_handler
        else:
            self.preset_handler = parent.digital_preset_handler
        self.synth_num = synth_num
        self.part = PART_1 if synth_num == 1 else PART_2
        self.setWindowTitle(f"Digital Synth {synth_num}")
        self.main_window = parent

        # Store parameter controls for easy access
        self.controls: Dict[
            Union[DigitalParameter, DigitalCommonParameter], QWidget
        ] = {}

        # Allow resizing
        self.setMinimumSize(800, 400)
        self.resize(1000, 600)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Title and instrument selection
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = QLabel(
            f"Digital Synth:\n {self.presets[0]}" if self.presets else "Digital Synth"
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

        self.instrument_selection_label = QLabel("Select a digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        upper_layout = QHBoxLayout()
        container_layout.addLayout(upper_layout)

        # Title and drum kit selection
        instrument_preset_group = QGroupBox("Digital Synth")
        self.instrument_title_label = QLabel(
            f"Digital Synth:\n {self.presets[0]}" if self.presets else "Digital Synth"
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

        self.instrument_selection_label = QLabel("Select a Digital synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        # Synth selection
        # Preset ComboBox
        self.instrument_selection_combo = PresetComboBox(DIGITAL_PRESETS)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_handler.current_preset_index
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.preset_handler.preset_changed.connect(self.update_combo_box_index)
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

        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        container_layout.addWidget(self.partials_panel)

        # Add performance section
        container_layout.addWidget(self._create_performance_section())

        # Create tab widget for partials
        self.partial_tab_widget = QTabWidget()
        self.partial_editors = {}

        # Create editor for each partial
        for i in range(1, 4):
            editor = PartialEditor(midi_helper, i, self.part)
            self.partial_editors[i] = editor
            self.partial_tab_widget.addTab(editor, f"Partial {i}")

        container_layout.addWidget(self.partial_tab_widget)

        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Connect partial switches to enable/disable tabs
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)

        # Initialize with default states
        self.initialize_partial_states()
        # Parameter request messages based on captured format
        messages = [
            # Common parameters (0x00)
            [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x11,
                0x19,
                0x01,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x40,
                0x26,
                0xF7,
            ],
            # OSC1 parameters (0x20)
            [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x11,
                0x19,
                0x01,
                0x20,
                0x00,
                0x00,
                0x00,
                0x00,
                0x3D,
                0x09,
                0xF7,
            ],
            # OSC2 parameters (0x21)
            [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x11,
                0x19,
                0x01,
                0x21,
                0x00,
                0x00,
                0x00,
                0x00,
                0x3D,
                0x08,
                0xF7,
            ],
            # OSC3 parameters (0x22)
            [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x11,
                0x19,
                0x01,
                0x22,
                0x00,
                0x00,
                0x00,
                0x00,
                0x3D,
                0x07,
                0xF7,
            ],
            # Effects parameters (0x50)
            [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x11,
                0x19,
                0x01,
                0x50,
                0x00,
                0x00,
                0x00,
                0x00,
                0x25,
                0x71,
                0xF7,
            ],
        ]

        # Send each message with a small delay
        for msg in messages:
            self.midi_helper.send_message(msg)
            time.sleep(0.02)  # Small delay between messages
            logging.debug(
                f"Sent parameter request: {' '.join([hex(x)[2:].upper().zfill(2) for x in msg])}"
            )

        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            self.midi_helper.set_callback(self.handle_midi_message)

        self.data_request()

        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            print("MIDI helper initialized")
            if hasattr(self.midi_helper, "set_callback"):
                self.midi_helper.set_callback(self.handle_midi_message)
                print("MIDI callback set")
            else:
                logging.error("MIDI set_callback method not found")
        else:
            logging.error("MIDI helper not initialized")

        self.midi_helper.parameter_received.connect(self._on_parameter_received)

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        print(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def _create_performance_section(self):
        """Create performance controls section"""
        group = QGroupBox("Performance")
        layout = QVBoxLayout()
        group.setLayout(layout)
        # prettify with icons

        icons_hlayout = QHBoxLayout()
        for icon in [
            "ph.bell-ringing-bold",
            "mdi.call-merge",
            "mdi.account-voice",
            "ri.voiceprint-fill",
            "mdi.piano",
        ]:
            icon_label = QLabel()
            icon = qta.icon(icon)
            pixmap = icon.pixmap(
                Style.ICON_SIZE, Style.ICON_SIZE
            )  # Set the desired size
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignHCenter)
            icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Create two rows of controls
        top_row = QHBoxLayout()
        bottom_row = QHBoxLayout()

        # Ring Modulator switch
        self.ring_switch = Switch("Ring", ["OFF", "---", "ON"])
        self.ring_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.RING_SWITCH, v)
        )
        top_row.addWidget(self.ring_switch)

        # Unison switch and size
        self.unison_switch = Switch("Unison", ["OFF", "ON"])
        self.unison_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.UNISON_SWITCH, v
            )
        )
        top_row.addWidget(self.unison_switch)

        self.unison_size = Switch("Size", ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"])
        self.unison_size.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.UNISON_SIZE, v)
        )
        top_row.addWidget(self.unison_size)

        # Portamento mode and legato
        self.porto_mode = Switch("Porto", ["NORMAL", "LEGATO"])
        self.porto_mode.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.PORTAMENTO_MODE, v
            )
        )
        bottom_row.addWidget(self.porto_mode)

        self.legato_switch = Switch("Legato", ["OFF", "ON"])
        self.legato_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(
                DigitalCommonParameter.LEGATO_SWITCH, v
            )
        )
        bottom_row.addWidget(self.legato_switch)

        # Analog Feel and Wave Shape
        analog_feel = self._create_parameter_slider(
            DigitalCommonParameter.ANALOG_FEEL, "Analog"
        )
        wave_shape = self._create_parameter_slider(
            DigitalCommonParameter.WAVE_SHAPE, "Shape"
        )

        # Add all controls to layout
        layout.addLayout(top_row)
        layout.addLayout(bottom_row)
        layout.addWidget(analog_feel)
        layout.addWidget(wave_shape)
        self.update_instrument_image()
        return group

    def _create_parameter_slider(
        self, param: Union[DigitalParameter, DigitalCommonParameter], label: str
    ) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        print(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(f"Digital Synth:\n {selected_synth_text}")

    def update_instrument_preset(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        if synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_synth_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            preset_index = int(selected_synth_padded_number)
            print(f"preset_index: {preset_index}")
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
                    "resources", instrument_icon_folder, "jdxi_vector.png"
                )
            pixmap = QPixmap(file_to_load)
            scaled_pixmap = pixmap.scaledToHeight(
                250, Qt.TransformationMode.SmoothTransformation
            )  # Resize to 250px height
            self.image_label.setPixmap(scaled_pixmap)
            return True

        default_image_path = os.path.join(
            "resources", instrument_icon_folder, "jdxi_vector.png"
        )
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
            print(f"selected_instrument_type: {selected_instrument_type}")
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
        # if self.preset_handler:
        #    self.preset_handler.set_preset(preset_index)
        if not self.preset_loader:
            self.preset_loader = PresetLoader(self.midi_helper)
        if self.preset_loader:
            self.preset_loader.load_preset(preset_data)

    def _on_parameter_changed(
        self, param: Union[DigitalParameter, DigitalCommonParameter], display_value: int
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

    def _on_partial_state_changed(
        self, partial: DigitalPartial, enabled: bool, selected: bool
    ):
        """Handle partial state changes"""
        if self.midi_helper:
            set_partial_state(self.midi_helper, partial, enabled, selected)

        # Enable/disable corresponding tab
        partial_num = partial.value
        self.partial_tab_widget.setTabEnabled(partial_num - 1, enabled)

        # Switch to selected partial's tab
        if selected:
            self.partial_tab_widget.setCurrentIndex(partial_num - 1)

    def initialize_partial_states(self):
        """Initialize partial states with defaults"""
        # Default: Partial 1 enabled and selected, others disabled
        for partial in DigitalPartial.get_partials():
            enabled = partial == DigitalPartial.PARTIAL_1
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.partial_tab_widget.setTabEnabled(partial.value - 1, enabled)

        # Show first tab
        self.partial_tab_widget.setCurrentIndex(0)

    def send_midi_parameter(
        self, param: Union[DigitalParameter, DigitalCommonParameter], value: int
    ) -> bool:
        """Send MIDI parameter to synth

        Args:
            param: Parameter to send
            value: Parameter value

        Returns:
            True if successful
        """
        try:
            # Validate and convert value
            midi_value = param.validate_value(value)

            # Common parameters use group 0x00
            if isinstance(param, DigitalCommonParameter):
                group = 0x00
                address = param.address
            else:
                # Get group/address for partial parameters
                group, address = param.get_address_for_partial(self.partial_num)

            # Send parameter via MIDI
            return self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=group,
                param=address,
                value=midi_value,
            )

        except Exception as e:
            logging.error(f"Error sending parameter {param.name}: {str(e)}")
            return False

    def _update_ui(self, parameters: Dict[str, int]):
        """Update UI with new parameter values"""
        try:
            # Emit the signal to update the UI
            self.ui_update_requested.emit(parameters)

        except Exception as e:
            logging.error(f"Error updating UI: {str(e)}", exc_info=True)

    def handle_midi_message(self, message):
        """Callback for handling incoming MIDI messages"""
        try:
            print(f"SysEx message: {message}")
            if message[7] == 0x12:  # DT1 command
                self._handle_dt1_message(message[8:])
        except Exception as e:
            logging.error(f"Error handling MIDI message: {str(e)}", exc_info=True)

    def _handle_dt1_message(self, data):
        """Handle Data Set 1 (DT1) messages

        Format: aa bb cc dd ... where:
        aa bb cc = Address
        dd ... = Data
        """
        if len(data) < 4:  # Need at least address and one data byte
            return

        address = data[0:3]
        print(f"DT1 message Address: {address}")
        value = data[3]
        print(f"DT1 message Value: {value}")
        # Emit signal with parameter data
        self.parameter_received.emit(address, value)

    def data_request(self):
        """Send data request SysEx messages to the JD-Xi"""
        # Define SysEx messages as byte arrays
        wave_type_request = bytes.fromhex(
            "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7"
        )
        oscillator_1_request = bytes.fromhex(
            "F0 41 10 00 00 00 0E 11 19 01 20 00 00 00 00 3D 09 F7"
        )
        oscillator_2_request = bytes.fromhex(
            "F0 41 10 00 00 00 0E 11 19 01 21 00 00 00 00 3D 08 F7"
        )
        oscillator_3_request = bytes.fromhex(
            "F0 41 10 00 00 00 0E 11 19 01 22 00 00 00 00 3D 07 F7"
        )
        effects_request = bytes.fromhex(
            "F0 41 10 00 00 00 0E 11 19 01 50 00 00 00 00 25 71 F7"
        )

        # Send each SysEx message
        self.send_message(wave_type_request)
        self.send_message(oscillator_1_request)
        self.send_message(oscillator_2_request)
        self.send_message(oscillator_3_request)
        self.send_message(effects_request)

    def send_message(self, message):
        """Send a SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def _on_parameter_received(self, address, value):
        """Handle parameter updates from MIDI messages."""
        # Check if the address corresponds to this editor's area
        if address[0] == DIGITAL_SYNTH_1_AREA:
            # Update the UI or internal state based on the address and value
            print(f"Received parameter update: Address={address}, Value={value}")


def base64_to_pixmap(base64_str):
    """Convert base64 string to QPixmap"""
    image_data = base64.b64decode(base64_str)
    image = QPixmap()
    image.loadFromData(image_data)
    return image
