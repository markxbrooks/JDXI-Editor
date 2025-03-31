from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox

from jdxi_editor.midi.data.constants.analog import SubOscType, Waveform
from jdxi_editor.midi.data.parameter.analog import AnalogParameter
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton


class OscillatorSection(QWidget):
    def __init__(self, create_parameter_slider, create_parameter_switch, waveform_selected_callback, wave_buttons):
        super().__init__()
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._on_waveform_selected = waveform_selected_callback
        self.wave_buttons = wave_buttons
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

        # Waveform buttons
        layout.addLayout(self.create_waveform_buttons())

        # Tuning controls
        layout.addWidget(self.create_tuning_group())

        # Pulse Width controls
        layout.addWidget(self.create_pw_group())

        # Pitch Envelope
        layout.addWidget(self.create_pitch_env_group())

        # Sub Oscillator
        layout.addWidget(self.create_sub_osc_group())

    def create_waveform_buttons(self):
        wave_layout = QHBoxLayout()

        for waveform in [Waveform.SAW, Waveform.TRIANGLE, Waveform.PULSE]:
            btn = AnalogWaveformButton(waveform)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)

            # Set icons
            icon_name = "upsaw" if waveform == Waveform.SAW else "triangle" if waveform == Waveform.TRIANGLE else "pwsqu"
            icon_base64 = generate_waveform_icon(icon_name, "#FFFFFF", 1.0)
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))

            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            wave_layout.addWidget(btn)

        return wave_layout

    def create_tuning_group(self):
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        tuning_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PITCH_COARSE, "Coarse"))
        tuning_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PITCH_FINE, "Fine"))

        return tuning_group

    def create_pw_group(self):
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        pw_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PULSE_WIDTH, "Width"))
        pw_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PULSE_WIDTH_MOD_DEPTH, "Mod Depth"))

        return pw_group

    def create_pitch_env_group(self):
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        pitch_env_layout.addWidget(
            self._create_parameter_slider(AnalogParameter.OSC_PITCH_ENV_VELOCITY_SENSITIVITY, "Mod Depth"))
        pitch_env_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PITCH_ENV_ATTACK_TIME, "Attack"))
        pitch_env_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PITCH_ENV_DECAY, "Decay"))
        pitch_env_layout.addWidget(self._create_parameter_slider(AnalogParameter.OSC_PITCH_ENV_DEPTH, "Depth"))

        return pitch_env_group

    def create_sub_osc_group(self):
        sub_group = QGroupBox("Sub Oscillator")
        sub_layout = QVBoxLayout()
        sub_group.setLayout(sub_layout)
        self.sub_oscillator_type_switch = self._create_parameter_switch(
            AnalogParameter.SUB_OSCILLATOR_TYPE, "Type",
            [SubOscType.OFF.display_name, SubOscType.OCT_DOWN_1.display_name, SubOscType.OCT_DOWN_2.display_name]
        )
        sub_layout.addWidget(self.sub_oscillator_type_switch)

        return sub_group
