"""
Analog Oscillator Section
"""

from typing import Callable

from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.oscillator.widget import AnalogOscillatorWidgets
from jdxi_editor.ui.editors.analog.oscillator.widget_spec import (
    AnalogOscillatorLayoutSpec,
)
from jdxi_editor.ui.editors.base.oscillator.section import BaseOscillatorSection
from jdxi_editor.ui.editors.base.oscillator.widget import OscillatorWidgets
from jdxi_editor.ui.editors.digital.partial.oscillator.spec import (
    OscillatorFeature,
    OscillatorLayoutSpec,
)
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import (
    PitchEnvelopeSpec,
    PWMSpec,
    SliderSpec,
    SwitchSpec,
)


class AnalogOscillatorSection(BaseOscillatorSection):
    """Analog Oscillator Section"""

    """spec_pwm = PWMSpec(
        pulse_width_param=Analog.Param.OSC_PULSE_WIDTH,
        mod_depth_param=Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
    )"""

    """spec_pitch_env = PitchEnvelopeSpec(
        attack_param=Analog.Param.OSC_PITCH_ENV_ATTACK_TIME,
        decay_param=Analog.Param.OSC_PITCH_ENV_DECAY_TIME,
        depth_param=Analog.Param.OSC_PITCH_ENV_DEPTH,
    )"""

    SYNTH_SPEC = Analog

    def __init__(
        self,
        waveform_selected_callback: Callable,
        wave_buttons: dict,
        midi_helper: MidiIOHelper,
        address: JDXiSysExAddress,
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
        self.widgets: OscillatorWidgets | None = None
        self._on_waveform_selected = waveform_selected_callback
        self.waveform_buttons: dict = wave_buttons or {}
        self.midi_helper = midi_helper
        self.analog: bool = True
        self.wave_shapes = self.generate_wave_shapes()
        self._define_spec()
        super().__init__(
            icons_row_type=IconType.OSCILLATOR,
            analog=True,
            midi_helper=midi_helper,
            address=address,
            send_midi_parameter=send_midi_parameter,
        )
        log.info(
            scope=self.__class__.__name__,
            message=f"after super init self.controls: {self.controls}",
        )
        self.address = address
        self.finalize()

    def _define_spec(self):
        self.spec: AnalogOscillatorLayoutSpec = self._build_layout_spec()
        self.spec_pwm = self.spec.pwm
        self.spec_pitch_env = self.spec.pitch_env
        self.SWITCH_SPECS = self.spec.switches

    def _create_feature_widgets(self):
        env_sliders = self._build_sliders(self.spec.env)
        self.osc_pitch_env_velocity_sensitivity_slider = (
            env_sliders[0] if env_sliders else None
        )

        switches = self._build_switches(self.SWITCH_SPECS)
        self.sub_oscillator_type_switch = switches[0] if switches else None

        tuning = self._build_sliders(self.spec.tuning)
        self.tuning_sliders = tuning

    def build_widgets(self):
        """Build widgets: run base to create waveform buttons, pitch env, PWM, then analog-specific (sub-osc switch, tuning)."""
        super().build_widgets()
        # Base does not call _build_additional_analog_widgets; we must call it so env/tuning/switch sliders exist
        self._build_additional_analog_widgets()
        # All oscillator widgets in one container
        self.widgets = AnalogOscillatorWidgets(
            waveform_buttons=getattr(self, "waveform_buttons", None),
            pitch_env_widget=self.pitch_env_widget,
            pwm_widget=self.pwm_widget,
            switches=(
                [self.sub_oscillator_type_switch]
                if self.sub_oscillator_type_switch
                else []
            ),
            tuning=self.tuning_sliders or [],
            env=(
                [self.osc_pitch_env_velocity_sensitivity_slider]
                if self.osc_pitch_env_velocity_sensitivity_slider
                else []
            ),
            sub_oscillator_type_switch=self.sub_oscillator_type_switch,
            osc_pitch_env_velocity_sensitivity_slider=self.osc_pitch_env_velocity_sensitivity_slider,
            osc_pitch_coarse_slider=getattr(self, "osc_pitch_coarse_slider", None),
            osc_pitch_fine_slider=getattr(self, "osc_pitch_fine_slider", None),
            pitch_env_widgets=getattr(self, "pitch_env_widgets", []),
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
        env_sliders = self._build_sliders(self.spec.env)
        self.osc_pitch_env_velocity_sensitivity_slider = (
            env_sliders[0] if len(env_sliders) == 1 else None
        )
        # --- Sub Oscillator Type switch; optional when SWITCH_SPECS is empty
        switches = self._build_switches(self.SWITCH_SPECS)
        self.sub_oscillator_type_switch = switches[0] if len(switches) == 1 else None
        # --- Tuning Group sliders; optional for Digital
        tuning_slider_list = self._build_sliders(self.spec.tuning)
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
                S.Param.SUB_OSCILLATOR_TYPE.display_name,
                options=S.Display.Options.SUB_OSCILLATOR_TYPE,
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
        pwm = PWMSpec(
            pulse_width_param=Analog.Param.OSC_PULSE_WIDTH,
            mod_depth_param=Analog.Param.OSC_PULSE_WIDTH_MOD_DEPTH,
        )
        pitch_env = PitchEnvelopeSpec(
            attack_param=Analog.Param.OSC_PITCH_ENV_ATTACK_TIME,
            decay_param=Analog.Param.OSC_PITCH_ENV_DECAY_TIME,
            depth_param=Analog.Param.OSC_PITCH_ENV_DEPTH,
        )
        return AnalogOscillatorLayoutSpec(
            switches=switches,
            tuning=tuning,
            env=env,
            pwm=pwm,
            pitch_env=pitch_env,
            features={
                OscillatorFeature.PWM,
                OscillatorFeature.PITCH_ENV,
                OscillatorFeature.SUB_OSC,
            },
        )
