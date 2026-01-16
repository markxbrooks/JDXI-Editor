"""
Analog Oscillator Section
"""

from typing import Callable

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QTabWidget, QVBoxLayout, QWidget

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.editor import IconType
import qtawesome as qta
from jdxi_editor.midi.data.analog.oscillator import AnalogOscWave, AnalogSubOscType
from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.partial.pwm import PWMWidget
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.widgets.button.waveform.analog import AnalogWaveformButton
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


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
        self.controls = controls
        self.analog = True
        
        super().__init__(icon_type=IconType.OSCILLATOR, analog=True)
        self.setup_ui()

    def setup_ui(self) -> None:
        """
        Setup the UI (standardized method name matching Digital Oscillator)
        :return: None
        """
        layout = self.get_layout(margins=(1, 1, 1, 1))

        # --- Waveform buttons ---
        layout.addLayout(self.create_waveform_buttons())

        # --- Tab widget to add pitch and PW controls to ---
        self.oscillator_tab_widget = QTabWidget()
        JDXiThemeManager.apply_tabs_style(self.oscillator_tab_widget, analog=True)
        layout.addWidget(self.oscillator_tab_widget)

        # --- Tuning and Pitch tab (standardized name matching Digital) ---
        tuning_pitch_widget = self._create_tuning_pitch_widget()
        tuning_icon = IconRegistry.get_icon(IconRegistry.MUSIC_NOTE, color=JDXiStyle.GREY)
        self.oscillator_tab_widget.addTab(tuning_pitch_widget, tuning_icon, "Tuning and Pitch")

        # --- Pulse Width tab ---
        pw_group = self._create_pw_group()
        pw_icon = QIcon(base64_to_pixmap(generate_waveform_icon("square", "#FFFFFF", 1.0)))
        self.oscillator_tab_widget.addTab(pw_group, pw_icon, "Pulse Width")
        
        layout.addStretch()

    def _create_tuning_pitch_widget(self) -> QWidget:
        """Create tuning and pitch widget combining Tuning and Pitch Envelope (standardized name matching Digital)"""
        pitch_layout = QHBoxLayout()
        pitch_layout.addStretch()
        pitch_layout.addWidget(self._create_tuning_group())
        pitch_layout.addWidget(self._create_pitch_env_group())
        pitch_layout.addStretch()
        pitch_widget = QWidget()
        pitch_widget.setLayout(pitch_layout)
        pitch_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)
        return pitch_widget

    def create_waveform_buttons(self) -> QHBoxLayout:
        """
        Create the waveform buttons

        :return: QHBoxLayout
        """
        wave_layout = QHBoxLayout()
        wave_layout.addStretch()

        for waveform in [
            AnalogOscWave.SAW,
            AnalogOscWave.TRIANGLE,
            AnalogOscWave.PULSE,
        ]:
            btn = AnalogWaveformButton(waveform)
            JDXiThemeManager.apply_button_rect_analog(btn)

            # Set icons
            icon_name = (
                "upsaw"
                if waveform == AnalogOscWave.SAW
                else "triangle" if waveform == AnalogOscWave.TRIANGLE else "pwsqu"
            )
            icon_base64 = generate_waveform_icon(icon_name, "#FFFFFF", 0.7)
            btn.setIcon(QIcon(base64_to_pixmap(icon_base64)))
            btn.setFixedSize(JDXiDimensions.WAVEFORM_ICON_WIDTH, JDXiDimensions.WAVEFORM_ICON_HEIGHT)
            btn.waveform_selected.connect(self._on_waveform_selected)
            self.wave_buttons[waveform] = btn
            self.controls[AnalogParam.OSC_WAVEFORM] = btn
            wave_layout.addWidget(btn)

        self.sub_oscillator_type_switch = self._create_parameter_switch(
            AnalogParam.SUB_OSCILLATOR_TYPE,
            "Type",
            [
                AnalogSubOscType.OFF.display_name,
                AnalogSubOscType.OCT_DOWN_1.display_name,
                AnalogSubOscType.OCT_DOWN_2.display_name,
            ],
        )
        wave_layout.addWidget(self.sub_oscillator_type_switch)
        wave_layout.addStretch()
        return wave_layout

    def _create_tuning_group(self) -> QGroupBox:
        """
        Create the tuning group (standardized private method matching Digital)

        :return: QGroupBox
        """
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QHBoxLayout()
        tuning_group.setLayout(tuning_layout)
        tuning_layout.addStretch()
        tuning_layout.addWidget(
            self._create_parameter_slider(
                AnalogParam.OSC_PITCH_COARSE, "Coarse (1/2 tones)", vertical=True
            )
        )
        tuning_layout.addWidget(
            self._create_parameter_slider(
                AnalogParam.OSC_PITCH_FINE, "Fine (cents)", vertical=True
            )
        )
        tuning_layout.addStretch()

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
            pulse_width_param=AnalogParam.OSC_PULSE_WIDTH,
            mod_depth_param=AnalogParam.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            analog=self.analog
        )
        JDXiThemeManager.apply_adsr_style(self.pwm_widget, analog=True)
        self.pwm_widget.setMaximumHeight(JDXiStyle.PWM_WIDGET_HEIGHT)
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
            attack_param=AnalogParam.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=AnalogParam.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=AnalogParam.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
        )
        JDXiThemeManager.apply_adsr_style(self.pitch_env_widget, analog=True)

        env_group = QGroupBox("Envelope")
        env_group.setProperty("adsr", True)
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)
        pitch_env_row_layout.addWidget(self.pitch_env_widget)
        pitch_env_row_layout.addWidget(
            self._create_parameter_slider(
                AnalogParam.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                "Velocity Sensitivity",
                vertical=True,
            )
        )
        pitch_env_row_layout.addStretch()
        return pitch_env_group

    def _update_pw_controls_state(self, waveform: AnalogOscWave):
        """
        Update pulse width controls enabled state based on waveform

        :param waveform: AnalogOscWave value
        :return: None
        """
        pw_enabled = waveform == AnalogOscWave.PULSE
        self.pwm_widget.setEnabled(pw_enabled)
