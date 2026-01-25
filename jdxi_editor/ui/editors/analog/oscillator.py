"""
Analog Oscillator Section
"""

from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QTabWidget, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.oscillator import AnalogWaveOsc
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.helpers import generate_analog_wave_button, generate_analog_waveform_icon_name
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget
from picomidi.sysex.parameter.address import AddressParameter


class AnalogOscillatorSection(SectionBaseWidget):
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
        self.analog = True

        super().__init__(icons_row_type=IconType.OSCILLATOR, analog=True)
        # Set controls after super().__init__() to avoid it being overwritten
        self.controls = controls or {}
        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """build widgets"""
        self.oscillator_tab_widget = QTabWidget()
        # --- Tuning and Pitch tab (standardized name matching Digital) ---
        self.tuning_widget = self._create_tuning_group()
        self.pitch_widget = self._create_tuning_pitch_widget()

    def setup_ui(self) -> None:
        """
        Setup the UI (standardized method name matching Digital Oscillator)
        :return: None
        """
        layout = self.get_layout(margins=(1, 1, 1, 1))

        # --- Waveform buttons ---
        layout.addLayout(self.create_waveform_buttons())

        # --- Tab widget to add pitch and PW controls to ---
        JDXi.UI.Theme.apply_tabs_style(self.oscillator_tab_widget, analog=True)
        layout.addWidget(self.oscillator_tab_widget)
        self._add_tab(key=Analog.Wave.Tab.PITCH, widget=self.pitch_widget)
        self._add_tab(key=Analog.Wave.Tab.TUNING, widget=self.tuning_widget)

        # --- Pulse Width tab ---
        pw_group = self._create_pw_group()
        self._add_tab(key=Analog.Wave.Tab.PULSE_WIDTH, widget=pw_group)

        layout.addStretch()

    def _create_tuning_pitch_widget(self) -> QWidget:
        """Create tuning and pitch widget combining Tuning and Pitch Envelope (standardized name matching Digital)"""
        pitch_layout = QHBoxLayout()
        pitch_layout.addStretch()
        pitch_layout.addWidget(self._create_pitch_env_group())
        pitch_layout.addStretch()
        pitch_widget = QWidget()
        pitch_widget.setLayout(pitch_layout)
        pitch_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return pitch_widget

    def create_waveform_buttons(self) -> QHBoxLayout:
        """
        Create the waveform buttons

        :return: QHBoxLayout
        """
        wave_layout_widgets = []
        for waveform in [
            Analog.Wave.Osc.SAW,
            Analog.Wave.Osc.TRIANGLE,
            Analog.Wave.Osc.PULSE,
        ]:
            icon_name = generate_analog_waveform_icon_name(waveform)
            btn = generate_analog_wave_button(icon_name, waveform)
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            self.controls[Analog.Param.OSC_WAVEFORM] = btn
            wave_layout_widgets.append(btn)

        self.sub_oscillator_type_switch = self._create_parameter_switch(
            Analog.Param.SUB_OSCILLATOR_TYPE,
            Analog.Display.Name.SUB_OSCILLATOR_TYPE,
            Analog.Display.Options.SUB_OSCILLATOR_TYPE,
        )
        wave_layout_widgets.append(self.sub_oscillator_type_switch)
        wave_layout = create_layout_with_widgets(wave_layout_widgets)
        return wave_layout

    def _create_tuning_group(self) -> QGroupBox:
        """
        Create the tuning group (standardized private method matching Digital)

        :return: QGroupBox
        """
        tuning_group = QGroupBox("Tuning")
        tuning_layout = create_layout_with_widgets(
            [
                self._create_parameter_slider(
                    Analog.Param.OSC_PITCH_COARSE,
                    Analog.Display.Name.OSC_PITCH_COARSE,
                    vertical=True,
                ),
                self._create_parameter_slider(
                    Analog.Param.OSC_PITCH_FINE,
                    Analog.Display.Name.OSC_PITCH_FINE,
                    vertical=True,
                ),
            ]
        )
        tuning_group.setLayout(tuning_layout)
        return tuning_group

    def _create_pw_group(self) -> QGroupBox:
        """
        Create the pulse width group (standardized private method matching Digital)

        :return: QGroupBox
        """
        pw_group = QGroupBox("Pulse Width")

        pw_layout = QVBoxLayout()
        pw_layout.addStretch()
        pw_group.setLayout(pw_layout)
        pw_layout.addStretch()
        self.pwm_widget = PWMWidget(
            pulse_width_param=Analog.Param.OSC_PULSE_WIDTH,
            mod_depth_param=Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            analog=self.analog,
        )
        self.pwm_widget.setMaximumHeight(JDXi.UI.Style.PWM_WIDGET_HEIGHT)
        pw_layout.addWidget(self.pwm_widget)
        pw_layout.addStretch()

        return pw_group

    def _create_pitch_env_group(self) -> QGroupBox:
        """
        Create the pitch envelope group (standardized private method matching Digital)

        :return: QGroupBox
        """
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_row_layout = QHBoxLayout()
        pitch_env_group.setLayout(pitch_env_row_layout)
        pitch_env_row_layout.addStretch()
        # --- Pitch Env Widget ---
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=Analog.Param.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=Analog.Param.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=Analog.Param.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        JDXi.UI.Theme.apply_adsr_style(self.pitch_env_widget, analog=True)

        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)
        pitch_env_row_layout.addWidget(self.pitch_env_widget)
        pitch_env_row_layout.addWidget(
            self._create_parameter_slider(
                Analog.Param.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                Analog.Display.Name.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                vertical=True,
            )
        )
        pitch_env_row_layout.addStretch()
        return pitch_env_group

    def _update_pw_controls_state(self, waveform: AnalogWaveOsc):
        """
        Update pulse width controls enabled state based on waveform

        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == Analog.Wave.Osc.PULSE
        self.pwm_widget.setEnabled(pw_enabled)
