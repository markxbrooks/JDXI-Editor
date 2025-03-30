from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.style import Style
from jdxi_editor.midi.data.parameter.analog import AnalogParameter, Waveform

class OscillatorSection(QWidget):
    def __init__(self, controls):
        super().__init__()
        self.controls = controls
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
        self.wave_buttons = {}
        for waveform in [Waveform.SAW, Waveform.TRIANGLE, Waveform.PULSE]:
            btn = AnalogWaveformButton(waveform)
            btn.setStyleSheet(Style.JDXI_BUTTON_RECT_ANALOG)
            icon_base64 = generate_waveform_icon(waveform.name.lower(), "#FFFFFF", 1.0)
            pixmap = base64_to_pixmap(icon_base64)
            btn.setIcon(QIcon(pixmap))
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            wave_layout.addWidget(btn)
        return wave_layout

    def create_tuning_group(self):
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        self.controls['osc_pitch_coarse'] = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_COARSE, "Coarse"
        )
        self.controls['osc_pitch_fine'] = self._create_parameter_slider(
            AnalogParameter.OSC_PITCH_FINE, "Fine"
        )

        tuning_layout.addWidget(self.controls['osc_pitch_coarse'])
        tuning_layout.addWidget(self.controls['osc_pitch_fine'])
        return tuning_group

    # ... Repeat for create_pw_group, create_pitch_env_group, create_sub_osc_group