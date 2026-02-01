"""
Analog Oscillator Section
"""

from typing import Callable, Dict, Union

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QTabWidget, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.helpers import (
    generate_analog_wave_button,
    generate_analog_waveform_icon_name,
)
from jdxi_editor.ui.editors.base.oscillator import BaseOscillatorSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec


class AnalogOscillatorSection(BaseOscillatorSection):
    """Analog Oscillator Section"""

    SLIDER_GROUPS = {
        "tuning": [
            SliderSpec(
                Analog.Param.OSC_PITCH_COARSE,
                Analog.Display.Name.OSC_PITCH_COARSE,
                vertical=True,
            ),
            SliderSpec(
                Analog.Param.OSC_PITCH_FINE,
                Analog.Display.Name.OSC_PITCH_FINE,
                vertical=True,
            ),
        ],
        # --- Analog has this extra parameter, so here is the slider
        "env": [
            SliderSpec(
                Analog.Param.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                Analog.Display.Name.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                vertical=True,
            )
        ],
    }
    # --- Waveform buttons
    BUTTON_SPECS = [
        SliderSpec(
            param=Analog.Wave.Osc.SAW,
            label=Analog.Wave.WaveType.UPSAW,
            icon_name=Analog.Wave.WaveType.UPSAW,
        ),
        SliderSpec(
            param=Analog.Wave.Osc.TRI,
            label=Analog.Wave.WaveType.SQUARE,
            icon_name=Analog.Wave.WaveType.SQUARE,
        ),
        SliderSpec(
            param=Analog.Wave.Osc.PW_SQUARE,
            label=Analog.Wave.WaveType.PWSQU,
            icon_name=Analog.Wave.WaveType.PWSQU,
        ),
    ]

    SWITCH_SPECS = [
        SwitchSpec(
            Analog.Param.SUB_OSCILLATOR_TYPE,
            Analog.Display.Name.SUB_OSCILLATOR_TYPE,
            Analog.Display.Options.SUB_OSCILLATOR_TYPE,
        ),
    ]

    SYNTH_SPEC = Analog

    def __init__(
        self,
        waveform_selected_callback: Callable,
        wave_buttons: dict,
        midi_helper: MidiIOHelper,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
    ):
        """
        Initialize the AnalogOscillatorSection

        :param waveform_selected_callback: Callable
        :param wave_buttons: dict to store waveform buttons (waveform -> button mapping)
        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        """
        self.pitch_env_widget: PitchEnvelopeWidget | None = None
        self.pwm_widget: PWMWidget | None = None
        self._on_waveform_selected = waveform_selected_callback
        self.waveform_buttons: dict = wave_buttons or {}
        self.midi_helper = midi_helper
        self.analog: bool = True

        super().__init__(
            icons_row_type=IconType.OSCILLATOR, analog=True, midi_helper=midi_helper
        )
        # --- Set attributes after super().__init__() to avoid them being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        self.address = address
        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """build widgets"""
        self._create_waveform_buttons()
        (self.osc_pitch_env_velocity_sensitivity_slider,) = self._build_sliders(
            self.SLIDER_GROUPS["env"]
        )
        # --- Only one switch, for Sub Oscillator Type
        (self.sub_oscillator_type_switch,) = self._build_switches(self.SWITCH_SPECS)
        # --- Tuning Group sliders
        (
            self.osc_pitch_coarse_slider,
            self.osc_pitch_fine_slider,
        ) = self._build_sliders(self.SLIDER_GROUPS["tuning"])
        self.tuning_sliders = [self.osc_pitch_coarse_slider, self.osc_pitch_fine_slider]

        # --- PWM Widget ---
        self.pwm_widget = PWMWidget(
            pulse_width_param=Analog.Param.OSC_PULSE_WIDTH,
            mod_depth_param=Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
            midi_helper=self.midi_helper,
            address=self.address,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            analog=self.analog,
        )

        # --- Pitch Env Widget ---
        self.pitch_env_widget = PitchEnvelopeWidget(
            attack_param=self.SYNTH_SPEC.Param.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=self.SYNTH_SPEC.Param.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=self.SYNTH_SPEC.Param.OSC_PITCH_ENV_DEPTH,
            midi_helper=self.midi_helper,
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            address=self.address,
            analog=self.analog,
        )
        # --- Create pitch_env_widgets list after pitch_env_widget is created
        self.pitch_env_widgets = [
            self.pitch_env_widget,
            self.osc_pitch_env_velocity_sensitivity_slider,
        ]
        # --- Finally create Tab widget with all of the above widgets
        self._create_tab_widget()

    def _create_tab_widget(self):
        """Tab widget with tuning group and pitch widget. Use self.tab_widget so base _add_tab() adds tabs to it."""
        self.tab_widget = QTabWidget()
        # --- Tuning tab (standardized name matching Digital) ---
        self.tuning_group = self._create_tuning_group()
        # --- Pitch tab (standardized name matching Digital) ---
        self.pitch_widget = self._create_tuning_pitch_widget()
        # --- Pulse Width tab ---
        self.pw_group = self._create_pw_group()

    def setup_ui(self) -> None:
        """
        Setup the UI (standardized method name matching Digital Oscillator)
        :return: None
        """
        layout = self.get_layout(margins=JDXi.UI.Dimensions.EDITOR_ANALOG.MARGINS)
        # --- Waveform buttons ---
        self.waveform_button_layout = self._create_wave_layout()
        layout.addLayout(self.waveform_button_layout)
        # --- Tab widget (same as self.tab_widget so _add_tab adds tabs to the widget in the layout) ---
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=True)
        layout.addWidget(self.tab_widget)
        self._add_tab(key=Analog.Wave.Tab.PITCH, widget=self.pitch_widget)
        self._add_tab(key=Analog.Wave.Tab.TUNING, widget=self.tuning_group)
        self._add_tab(key=Analog.Wave.Tab.PULSE_WIDTH, widget=self.pw_group)

        layout.addStretch()
