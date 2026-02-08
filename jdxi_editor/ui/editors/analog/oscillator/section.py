"""
Analog Oscillator Section
"""

from typing import Callable

from decologr import Decologr as log
from jdxi_editor.ui.editors.analog.oscillator.widget import OscillatorWidgets
from jdxi_editor.ui.editors.analog.oscillator.widget_spec import AnalogOscillatorLayoutSpec
from jdxi_editor.ui.widgets.layout import WidgetLayoutSpec
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.oscillator import BaseOscillatorSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.pitch.envelope import PitchEnvelopeWidget
from jdxi_editor.ui.widgets.pulse_width.pwm import PWMWidget
from jdxi_editor.ui.widgets.spec import (
    PitchEnvelopeSpec,
    PWMSpec,
    SliderSpec,
    SwitchSpec,
)


class AnalogOscillatorSection(BaseOscillatorSection):
    """Analog Oscillator Section"""

    PWM_SPEC = PWMSpec(
        pulse_width_param=Analog.Param.OSC_PULSE_WIDTH,
        mod_depth_param=Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
    )

    PITCH_ENV_SPEC = PitchEnvelopeSpec(
        attack_param=Analog.Param.OSC_PITCH_ENV_ATTACK_TIME,
        decay_param=Analog.Param.OSC_PITCH_ENV_DECAY_TIME,
        depth_param=Analog.Param.OSC_PITCH_ENV_DEPTH,
    )

    SYNTH_SPEC = Analog

    def __init__(
            self,
            waveform_selected_callback: Callable,
            wave_buttons: dict,
            midi_helper: MidiIOHelper,
            address: RolandSysExAddress,
            send_midi_parameter: Callable = None,
    ):
        """
        Initialize the AnalogOscillatorSection

        :param waveform_selected_callback: Callable
        :param wave_buttons: dict to store waveform buttons (waveform -> button mapping)
        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self.osc: OscillatorWidgets | None = None
        self.pitch_env_widget: PitchEnvelopeWidget | None = None
        self.pwm_widget: PWMWidget | None = None
        self._on_waveform_selected = waveform_selected_callback
        self.waveform_buttons: dict = wave_buttons or {}
        self.midi_helper = midi_helper
        self.analog: bool = True
        self.wave_shapes = self.generate_wave_shapes()
        super().__init__(
            icons_row_type=IconType.OSCILLATOR,
            analog=True,
            midi_helper=midi_helper,
            address=address,
            send_midi_parameter=send_midi_parameter,
        )
        log.info(scope=self.__class__.__name__, message=f"after super init self.controls: {self.controls}")
        self.address = address
        self._build_widgets()
        self.build_widgets()
        log.info(scope=self.__class__.__name__, message=f"after build_widgets self.controls: {self.controls}")
        self.setup_ui()

    def _build_widgets(self) -> OscillatorWidgets:
        """Build Widgets"""
        self.SLIDER_GROUPS: AnalogOscillatorLayoutSpec = self._build_layout_spec()
        self.SWITCH_SPECS = self.SLIDER_GROUPS.switches

        return OscillatorWidgets(
            switches=self._build_switches(self.SLIDER_GROUPS.switches),
            tuning=self._build_sliders(self.SLIDER_GROUPS.tuning),
            env=self._build_sliders(self.SLIDER_GROUPS.env),
        )

    def build_widgets(self):
        """Build widgets: run base to create waveform buttons, pitch env, PWM, then analog-specific (sub-osc switch, tuning)."""
        super().build_widgets()
        # Keep self.osc for any code that expects OscillatorWidgets (switches/tuning/env)
        self.osc = OscillatorWidgets(
            switches=[self.sub_oscillator_type_switch] if self.sub_oscillator_type_switch else [],
            tuning=self.tuning_sliders or [],
            env=[self.osc_pitch_env_velocity_sensitivity_slider]
            if self.osc_pitch_env_velocity_sensitivity_slider
            else [],
        )

    def generate_wave_shapes(self) -> list:
        """Generate waveform button specs (same pattern as Analog LFO / Analog Filter)."""
        W = self.SYNTH_SPEC.Wave
        return [
            SliderSpec(
                param=W.Osc.SAW,
                label=W.WaveType.UPSAW,
                icon_name=W.WaveType.UPSAW,
            ),
            SliderSpec(
                param=W.Osc.TRI,
                label=W.WaveType.SQUARE,
                icon_name=W.WaveType.SQUARE,
            ),
            SliderSpec(
                param=W.Osc.SQUARE,
                label=W.WaveType.PWSQU,
                icon_name=W.WaveType.PWSQU,
            ),
        ]

    def _build_additional_analog_widgets(self):
        # --- Env sliders (e.g. pitch env velocity sensitivity); optional for Digital
        env_sliders = self._build_sliders(self.SLIDER_GROUPS.get("env", []))
        self.osc_pitch_env_velocity_sensitivity_slider = (
            env_sliders[0] if len(env_sliders) == 1 else None
        )
        # --- Sub Oscillator Type switch; optional when SWITCH_SPECS is empty
        switches = self._build_switches(self.SWITCH_SPECS)
        self.sub_oscillator_type_switch = switches[0] if len(switches) == 1 else None
        # --- Tuning Group sliders; optional for Digital
        tuning_slider_list = self._build_sliders(self.SLIDER_GROUPS.get("tuning", []))
        if len(tuning_slider_list) == 2:
            self.osc_pitch_coarse_slider, self.osc_pitch_fine_slider = (
                tuning_slider_list
            )
            self.tuning_sliders = [
                self.osc_pitch_coarse_slider,
                self.osc_pitch_fine_slider,
            ]
        else:
            self.osc_pitch_coarse_slider = None
            self.osc_pitch_fine_slider = None
            self.tuning_sliders = []
        # --- Create pitch_env_widgets list after pitch_env_widget is created
        self.pitch_env_widgets = [self.pitch_env_widget]
        if self.osc_pitch_env_velocity_sensitivity_slider is not None:
            self.pitch_env_widgets.append(
                self.osc_pitch_env_velocity_sensitivity_slider
            )
        # --- Finally create Tab widget with all of the above widgets
        self._create_tab_widget()

    def _build_layout_spec(self) -> AnalogOscillatorLayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        switches = [
            SwitchSpec(
                S.Param.SUB_OSCILLATOR_TYPE,
                S.Display.Name.SUB_OSCILLATOR_TYPE,
                S.Display.Options.SUB_OSCILLATOR_TYPE,
            ),
        ]

        tuning = [
            SliderSpec(
                S.Param.OSC_PITCH_COARSE,
                S.Display.Name.OSC_PITCH_COARSE,
                vertical=True,
            ),
            SliderSpec(
                S.Param.OSC_PITCH_FINE,
                S.Display.Name.OSC_PITCH_FINE,
                vertical=True,
            ),
        ]
        # --- Analog has this extra parameter, so here is the slider
        env = [
            SliderSpec(
                S.Param.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                S.Display.Name.OSC_PITCH_ENV_VELOCITY_SENSITIVITY,
                vertical=True,
            )
        ]

        return AnalogOscillatorLayoutSpec(switches=switches, tuning=tuning, env=env)
