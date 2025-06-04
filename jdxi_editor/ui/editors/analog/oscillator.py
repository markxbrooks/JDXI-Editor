"""
Analog Oscillator Section
"""

from typing import Callable
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.oscillator import AnalogSubOscType, AnalogOscWave
from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.pwm import PWMWidget
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton


class AnalogOscillatorSection(QWidget):
    """Analog Oscillator Section"""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        waveform_selected_callback: Callable,
        wave_buttons: dict,
        midi_helper: MidiIOHelper,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
    ):
        super().__init__()
        """
        Initialize the AnalogOscillatorSection
        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param waveform_selected_callback: Callable
        :param wave_buttons: dict
        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        """
        self.pitch_env_widget = None
        self.pwm_widget = None
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._on_waveform_selected = waveform_selected_callback
        self.wave_buttons = wave_buttons
        self.midi_helper = midi_helper
        self.address = address
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

    def create_waveform_buttons(self) -> QHBoxLayout:
        """
        Create the waveform buttons
        :return: QHBoxLayout
        """
        wave_layout = QHBoxLayout()

        for waveform in [
            AnalogOscWave.SAW,
            AnalogOscWave.TRIANGLE,
            AnalogOscWave.PULSE,
        ]:
            btn = AnalogWaveformButton(waveform)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ANALOG)

            # Set icons
            icon_name = (
                "upsaw"
                if waveform == AnalogOscWave.SAW
                else "triangle"
                if waveform == AnalogOscWave.TRIANGLE
                else "pwsqu"
            )
            icon_base64 = generate_waveform_icon(icon_name, "#FFFFFF", 0.7)
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
            btn.setFixedSize(60, 30)
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            self.controls[AddressParameterAnalog.OSC_WAVEFORM] = btn
            wave_layout.addWidget(btn)

        return wave_layout

    def create_tuning_group(self) -> QGroupBox:
        """
        Create the tuning group
        :return: QGroupBox
        """
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)

        tuning_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterAnalog.OSC_PITCH_COARSE, "Coarse (1/2 tones)"
            )
        )
        tuning_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterAnalog.OSC_PITCH_FINE, "Fine (cents)"
            )
        )

        return tuning_group

    def create_pw_group(self) -> QGroupBox:
        """
        Create the pulse width group
        :return: QGroupBox
        """
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)

        self.pwm_widget = PWMWidget(pulse_width_param=AddressParameterAnalog.OSC_PULSE_WIDTH,
                                    mod_depth_param=AddressParameterAnalog.OSC_PULSE_WIDTH_MOD_DEPTH,
                                    midi_helper=self.midi_helper,
                                    address=self.address,
                                    create_parameter_slider=self._create_parameter_slider,
                                    controls=self.controls)
        self.pwm_widget.setStyleSheet(JDXiStyle.ADSR_ANALOG)
        self.pwm_widget.setMaximumHeight(JDXiStyle.PWM_WIDGET_HEIGHT)
        pw_layout.addWidget(self.pwm_widget)

        return pw_group

    def create_pitch_env_group(self) -> QGroupBox:
        """
        Create the pitch envelope group
        :return: QGroupBox
        """
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        pitch_env_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterAnalog.OSC_PITCH_ENV_VELOCITY_SENSITIVITY, "Velocity Sensitivity"
            )
        )
        # Pitch Env Widget
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=AddressParameterAnalog.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=AddressParameterAnalog.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=AddressParameterAnalog.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        self.pitch_env_widget.setStyleSheet(JDXiStyle.ADSR_ANALOG)
        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        # env_layout.addWidget(self.pitch_env_widget)
        env_group.setLayout(env_layout)
        pitch_env_layout.addWidget(self.pitch_env_widget)
        return pitch_env_group

    def create_sub_osc_group(self) -> QGroupBox:
        """
        Create the sub oscillator group
        :return: QGroupBox
        """
        sub_group = QGroupBox("Sub Oscillator")
        sub_layout = QVBoxLayout()
        sub_group.setLayout(sub_layout)
        self.sub_oscillator_type_switch = self._create_parameter_switch(
            AddressParameterAnalog.SUB_OSCILLATOR_TYPE,
            "Type",
            [
                AnalogSubOscType.OFF.display_name,
                AnalogSubOscType.OCT_DOWN_1.display_name,
                AnalogSubOscType.OCT_DOWN_2.display_name,
            ],
        )
        sub_layout.addWidget(self.sub_oscillator_type_switch)

        return sub_group

    def _update_pw_controls_state(self, waveform: AnalogOscWave):
        """
        Update pulse width controls enabled state based on waveform
        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == AnalogOscWave.PW_SQUARE
        self.pw_slider.setEnabled(pw_enabled)
        self.pwm_slider.setEnabled(pw_enabled)
