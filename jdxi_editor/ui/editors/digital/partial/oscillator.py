"""
Digital Oscillator Section for the JDXI Editor
"""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QGridLayout, QComboBox

from jdxi_editor.midi.data.digital import DigitalOscWave
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.midi.data.presets.pcm_waves import PCM_WAVES_CATEGORIZED
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.button.waveform import WaveformButton


class DigitalOscillatorSection(QWidget):
    """ Digital Oscillator Section for the JDXI Editor """
    def __init__(self,
                 create_parameter_slider,
                 create_parameter_switch,
                 create_parameter_combo_box,
                 send_midi_parameter,
                 partial_number,
                 midi_helper,
                 controls,
                 part,
                 parent=None):
        super().__init__()
        self.partial_number = partial_number
        self.midi_helper = midi_helper
        self.controls = controls
        self.part = part
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.send_midi_parameter = send_midi_parameter
        self.setup_ui()

    def setup_ui(self):
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
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT)
            btn.setFixedSize(60, 30)
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))
            self.wave_buttons[wave] = btn
            wave_layout.addWidget(btn)

        top_row.addLayout(wave_layout)
        self.wave_variation_switch = self._create_parameter_switch(DigitalPartialParameter.OSC_WAVE_VARIATION, "Variation", ["A", "B", "C"])
        top_row.addWidget(self.wave_variation_switch)
        layout.addLayout(top_row)

        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)
        tuning_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.OSC_PITCH, "Pitch"))
        tuning_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.OSC_DETUNE, "Detune"))
        layout.addWidget(tuning_group)

        # Pulse Width controls
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)
        self.pw_slider = self._create_parameter_slider(DigitalPartialParameter.OSC_PULSE_WIDTH, "Width")
        self.pwm_slider = self._create_parameter_slider(DigitalPartialParameter.OSC_PULSE_WIDTH_MOD_DEPTH, "Mod")
        pw_layout.addWidget(self.pw_slider)
        pw_layout.addWidget(self.pwm_slider)
        layout.addWidget(pw_group)

        # PCM Wave controls
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QGridLayout()
        pcm_group.setLayout(pcm_layout)
        self.pcm_wave_gain = self._create_parameter_combo_box(DigitalPartialParameter.PCM_WAVE_GAIN, "Gain [dB]", ["-6", "0", "+6", "+12"])
        self.pcm_wave_number = self._create_parameter_combo_box(DigitalPartialParameter.PCM_WAVE_NUMBER, "Number", set(w["Wave Number"] for w in PCM_WAVES_CATEGORIZED))
        self.pcm_category_combo = QComboBox()
        self.pcm_categories = ["No selection"] + sorted(set(w["Category"] for w in PCM_WAVES_CATEGORIZED))
        self.pcm_category_combo.addItems(self.pcm_categories)
        self.pcm_category_combo.currentIndexChanged.connect(self.update_waves)
        pcm_layout.addWidget(self.pcm_wave_gain, 0, 0)
        pcm_layout.addWidget(QLabel("Category"), 0, 1)
        pcm_layout.addWidget(self.pcm_category_combo, 0, 2)
        pcm_layout.addWidget(self.pcm_wave_number, 0, 3)
        layout.addWidget(pcm_group)

        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)
        pitch_env_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.OSC_PITCH_ENV_ATTACK_TIME, "Attack"))
        pitch_env_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.OSC_PITCH_ENV_DECAY_TIME, "Decay"))
        pitch_env_layout.addWidget(self._create_parameter_slider(DigitalPartialParameter.OSC_PITCH_ENV_DEPTH, "Depth"))
        layout.addWidget(pitch_env_group)

        # Super Saw detune
        self.super_saw_detune = self._create_parameter_slider(DigitalPartialParameter.SUPER_SAW_DETUNE, "S-Saw Detune")
        layout.addWidget(self.super_saw_detune)

        # Initialize states
        self._update_pw_controls_state(DigitalOscWave.SAW)
        self._update_pcm_controls_state(DigitalOscWave.PCM)

    def _on_waveform_selected(self, waveform: DigitalOscWave):
        """Handle waveform button clicks"""
        # Reset all buttons to default style
        for btn in self.wave_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT)

        # Apply active style to the selected waveform button
        selected_btn = self.wave_buttons.get(waveform)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if not self.send_midi_parameter(DigitalPartialParameter.OSC_WAVE, waveform.value):
            logging.warning(f"Failed to set waveform to {waveform.name}")

        # Update control visibility
        self._update_pw_controls_state(waveform)
        self._update_pcm_controls_state(waveform)

    def update_waves(self):
        selected_category = self.pcm_category_combo.currentText()

        # Filter waves or show all if "No selection"
        if selected_category == "No selection":
            filtered_waves = PCM_WAVES_CATEGORIZED  # Show all waves
        else:
            filtered_waves = [w for w in PCM_WAVES_CATEGORIZED if w["Category"] == selected_category]

        # Update wave combo box
        self.pcm_wave_number.combo_box.clear()
        self.pcm_wave_number.combo_box.addItems([f"{w['Wave Number']}: {w['Wave Name']}" for w in filtered_waves])
        self.pcm_wave_number.values = [w["Wave Number"] for w in filtered_waves]

    def _update_pw_controls_state(self, waveform: DigitalOscWave):
        """Update pulse width controls enabled state based on waveform"""
        pw_enabled = waveform == DigitalOscWave.PW_SQUARE
        self.pw_slider.setEnabled(pw_enabled)
        self.pwm_slider.setEnabled(pw_enabled)

    def _update_pcm_controls_state(self, waveform: DigitalOscWave):
        """Update PCM wave controls visibility based on waveform"""
        pcm_enabled = waveform == DigitalOscWave.PCM
        self.pcm_wave_gain.setEnabled(pcm_enabled)
        self.pcm_category_combo.setEnabled(pcm_enabled)
        self.pcm_wave_number.setEnabled(pcm_enabled)
