import logging
from functools import partial
from typing import Dict, Union

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
)

from jdxi_manager.data import DigitalParameter
from jdxi_manager.data.digital import DigitalCommonParameter, OscWave
from jdxi_manager.midi.constants import PART_1, DIGITAL_SYNTH_AREA
from jdxi_manager.midi.conversions import (
    midi_cc_to_frac,
    midi_cc_to_ms,
    ms_to_midi_cc,
    frac_to_midi_cc,
)
from jdxi_manager.ui.image_utils import base64_to_pixmap
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider, WaveformButton
from jdxi_manager.ui.widgets.adsr_widget import ADSRWidget
from jdxi_manager.ui.widgets.switch import Switch
from jdxi_manager.ui.widgets.waveform import (
    upsaw_png,
    square_png,
    pwsqu_png,
    triangle_png,
    sine_png,
    noise_png,
    spsaw_png,
    pcm_png,
    adsr_waveform_icon,
)


class DigitalPartialEditor(QWidget):
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
        self.updating_from_spinbox = False

    def _create_parameter_slider(
        self,
        param: Union[DigitalParameter, DigitalCommonParameter],
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

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def _create_oscillator_section(self):
        group = QGroupBox("Oscillator")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Prettify with icons
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

        wave_icons = {
            OscWave.SAW: upsaw_png("#FFFFFF", 1.0),
            OscWave.SQUARE: square_png("#FFFFFF", 1.0),
            OscWave.PW_SQUARE: pwsqu_png("#FFFFFF", 1.0),
            OscWave.TRIANGLE: triangle_png("#FFFFFF", 1.0),
            OscWave.SINE: sine_png("#FFFFFF", 1.0),
            OscWave.NOISE: noise_png("#FFFFFF", 1.0),
            OscWave.SUPER_SAW: spsaw_png("#FFFFFF", 1.0),
            OscWave.PCM: pcm_png("#FFFFFF", 1.0),
        }

        for wave, icon_base64 in wave_icons.items():
            btn = WaveformButton(wave)
            btn.setStyleSheet(Style.BUTTON_DEFAULT)  # Apply default styles

            # Set waveform icons
            wave_pixmap = base64_to_pixmap(icon_base64)
            btn.setIcon(QIcon(wave_pixmap))

            # Connect click signal
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
            icon_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
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
        env_layout = QVBoxLayout()
        env_group.setLayout(env_layout)

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

        # Create ADSRWidget
        self.filter_adsr_widget = ADSRWidget()
        adsr_vlayout = QVBoxLayout()
        env_layout.addWidget(self.filter_adsr_widget)
        # adsr_vlayout.addWidget(self.filter_adsr_widget)
        env_layout.setStretchFactor(self.filter_adsr_widget, 5)

        # ADSR controls
        adsr_layout = QHBoxLayout()
        adsr_vlayout.addLayout(adsr_layout)

        adsr_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.FILTER_ENV_ATTACK, "A", vertical=True
            )
        )
        adsr_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.FILTER_ENV_DECAY, "D", vertical=True
            )
        )
        adsr_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.FILTER_ENV_SUSTAIN, "S", vertical=True
            )
        )
        adsr_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.FILTER_ENV_RELEASE, "R", vertical=True
            )
        )
        env_layout.addLayout(adsr_vlayout)

        # Envelope depth
        env_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.FILTER_ENV_DEPTH, "Depth")
        )
        sub_layout.addWidget(env_group)
        layout.addLayout(sub_layout)
        env_group.setStyleSheet("QGroupBox { margin-top: 10px; }")
        self.filter_adsr_widget.updateGeometry()
        env_group.updateGeometry()

        # HPF cutoff
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.HPF_CUTOFF, "HPF Cutoff")
        )

        # Aftertouch sensitivity
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.CUTOFF_AFTERTOUCH, "AT Sens")
        )
        # Mapping ADSR parameters to their corresponding spinboxes
        self.filter_adsr_control_map = {
            DigitalParameter.FILTER_ENV_ATTACK: self.filter_adsr_widget.attack_sb,
            DigitalParameter.FILTER_ENV_DECAY: self.filter_adsr_widget.decay_sb,
            DigitalParameter.FILTER_ENV_SUSTAIN: self.filter_adsr_widget.sustain_sb,
            DigitalParameter.FILTER_ENV_RELEASE: self.filter_adsr_widget.release_sb,
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
            DigitalParameter.AMP_ENV_SUSTAIN,
            DigitalParameter.FILTER_ENV_SUSTAIN,
        ]:
            new_value = midi_cc_to_frac(value)
        else:
            new_value = midi_cc_to_ms(value)
        if spinbox.value() != new_value:
            spinbox.blockSignals(True)
            spinbox.setValue(new_value)
            spinbox.blockSignals(False)
            self.filter_adsr_widget.valueChanged()

    def on_adsr_envelope_changed(self, envelope):
        if not self.updating_from_spinbox:
            self.controls[DigitalParameter.FILTER_ENV_ATTACK].setValue(
                ms_to_midi_cc(envelope["attackTime"], 10, 1000)
            )
            self.controls[DigitalParameter.FILTER_ENV_DECAY].setValue(
                ms_to_midi_cc(envelope["decayTime"], 10, 1000)
            )
            self.controls[DigitalParameter.FILTER_ENV_SUSTAIN].setValue(
                ms_to_midi_cc(envelope["sustainAmpl"], 0.1, 1)
            )
            self.controls[DigitalParameter.FILTER_ENV_RELEASE].setValue(
                ms_to_midi_cc(envelope["releaseTime"], 10, 1000)
            )

    def filterAdsrValueChanged(self):
        self.updating_from_spinbox = True
        self.filter_adsr_widget.envelope["attackTime"] = (
            self.filter_adsr_widget.attack_sb.value()
        )
        self.filter_adsr_widget.envelope["decayTime"] = (
            self.filter_adsr_widget.decay_sb.value()
        )
        self.filter_adsr_widget.envelope["releaseTime"] = (
            self.filter_adsr_widget.release_sb.value()
        )
        self.filter_adsr_widget.envelope["initialAmpl"] = (
            self.filter_adsr_widget.initialSB.value()
        )
        self.filter_adsr_widget.envelope["peakAmpl"] = (
            self.filter_adsr_widget.peakSB.value()
        )
        self.filter_adsr_widget.envelope["sustainAmpl"] = (
            self.filter_adsr_widget.sustain_sb.value()
        )
        self.filter_adsr_widget.plot.set_values(self.filter_adsr_widget.envelope)
        self.filter_adsr_widget.envelopeChanged.emit(self.filter_adsr_widget.envelope)
        self.updating_from_spinbox = False

    def on_amp_env_adsr_envelope_changed(self, envelope):
        if not self.updating_from_spinbox:
            self.controls[DigitalParameter.AMP_ENV_ATTACK].setValue(
                ms_to_midi_cc(envelope["attackTime"], 10, 1000)
            )
            self.controls[DigitalParameter.AMP_ENV_DECAY].setValue(
                ms_to_midi_cc(envelope["decayTime"], 10, 1000)
            )
            self.controls[DigitalParameter.AMP_ENV_SUSTAIN].setValue(
                ms_to_midi_cc(envelope["sustainAmpl"], 0.1, 1)
            )
            self.controls[DigitalParameter.AMP_ENV_RELEASE].setValue(
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
            self.amp_env_adsr_widget.initialSB.value()
        )
        self.amp_env_adsr_widget.envelope["peakAmpl"] = (
            self.amp_env_adsr_widget.peakSB.value()
        )
        self.amp_env_adsr_widget.envelope["sustainAmpl"] = (
            self.amp_env_adsr_widget.sustain_sb.value()
        )
        self.amp_env_adsr_widget.plot.set_values(self.amp_env_adsr_widget.envelope)
        self.amp_env_adsr_widget.envelopeChanged.emit(self.amp_env_adsr_widget.envelope)
        self.updating_from_spinbox = False

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
        amp_env_adsr_vlayout = QVBoxLayout()
        env_group.setLayout(amp_env_adsr_vlayout)

        # Generate the ADSR waveform icon
        icon_base64 = adsr_waveform_icon("#FFFFFF", 2.0)
        pixmap = base64_to_pixmap(icon_base64)  # Convert to QPixmap

        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignHCenter)
        icons_hlayout = QHBoxLayout()
        icons_hlayout.addWidget(icon_label)
        layout.addLayout(icons_hlayout)

        # Create ADSRWidget
        self.amp_env_adsr_widget = ADSRWidget()

        env_layout.addLayout(amp_env_adsr_vlayout)
        amp_env_adsr_vlayout.addWidget(self.amp_env_adsr_widget)
        amp_env_adsr_vlayout.setStretchFactor(self.amp_env_adsr_widget, 5)
        amp_env_adsr_vlayout.addLayout(env_layout)
        env_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.AMP_ENV_ATTACK, "A", vertical=True
            )
        )
        env_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.AMP_ENV_DECAY, "D", vertical=True
            )
        )
        env_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.AMP_ENV_SUSTAIN, "S", vertical=True
            )
        )
        env_layout.addWidget(
            self._create_parameter_slider(
                DigitalParameter.AMP_ENV_RELEASE, "R", vertical=True
            )
        )

        layout.addWidget(env_group)

        # Keyfollow and aftertouch
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.AMP_KEYFOLLOW, "KeyFollow")
        )
        controls_layout.addWidget(
            self._create_parameter_slider(DigitalParameter.LEVEL_AFTERTOUCH, "AT Sens")
        )
        # Mapping ADSR parameters to their corresponding spinboxes
        self.adsr_control_map = {
            DigitalParameter.AMP_ENV_ATTACK: self.amp_env_adsr_widget.attack_sb,
            DigitalParameter.AMP_ENV_DECAY: self.amp_env_adsr_widget.decay_sb,
            DigitalParameter.AMP_ENV_SUSTAIN: self.amp_env_adsr_widget.sustain_sb,
            DigitalParameter.AMP_ENV_RELEASE: self.amp_env_adsr_widget.release_sb,
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
            DigitalParameter.AMP_ENV_SUSTAIN,
            DigitalParameter.AMP_ENV_SUSTAIN,
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
            DigitalParameter.AMP_ENV_SUSTAIN,
            DigitalParameter.AMP_ENV_SUSTAIN,
        ]:
            new_value = frac_to_midi_cc(value)
        else:
            new_value = ms_to_midi_cc(value)
        if control.value() != new_value:
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)

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

        # Ensure `depths_group` layout is only set once
        if (
            not depths_group.layout()
        ):  # Check if the group already has a layout assigned
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

    def update_slider_from_adsr(self, param, value):
        """Updates external control from ADSR widget, avoiding infinite loops."""
        control = self.controls[param]
        if param in [
            DigitalParameter.AMP_ENV_SUSTAIN,
            DigitalParameter.FILTER_ENV_SUSTAIN,
        ]:
            new_value = frac_to_midi_cc(value)
        else:
            new_value = ms_to_midi_cc(value)
        if control.value() != new_value:
            control.blockSignals(True)
            control.setValue(new_value)
            control.blockSignals(False)

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

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")

    def _on_waveform_selected(self, waveform: OscWave):
        """Handle waveform button clicks"""
        # Reset all buttons to default style
        for btn in self.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.BUTTON_DEFAULT)

        # Update button states
        # for wave, btn in self.wave_buttons.items():
        #    btn.setChecked(wave == waveform)

        # Apply active style to the selected waveform button
        selected_btn = self.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.BUTTON_ACTIVE)

        # Send MIDI message
        if not self.send_midi_parameter(DigitalParameter.OSC_WAVE, waveform.value):
            logging.warning(f"Failed to set waveform to {waveform.name}")

        # Update control visibility
        self._update_pw_controls_state(waveform)
        self._update_pcm_controls_state(waveform)
