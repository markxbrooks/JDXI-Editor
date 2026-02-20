"""
Analog Oscillator Section
"""

from types import SimpleNamespace
from typing import Callable

from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.analog.oscillator import AnalogOscillatorWidgetTypes
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.analog.oscillator.widget import AnalogOscillatorWidgets
from jdxi_editor.ui.editors.analog.oscillator.widget_spec import (
    AnalogOscillatorLayoutSpec,
)
from jdxi_editor.ui.editors.base.layout.spec import OscillatorFeature
from jdxi_editor.ui.editors.base.oscillator.section import BaseOscillatorSection
from jdxi_editor.ui.editors.base.oscillator.widget import OscillatorWidgets
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import (
    PitchEnvelopeSpec,
    PWMSpec,
    SliderSpec,
    SwitchSpec,
)


class AnalogOscillatorSection(BaseOscillatorSection):
    """Analog Oscillator Section"""

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
        log.info(
            scope=self.__class__.__name__,
            message="AnalogOscillatorSection __init__ start (address=%s)"
            % (getattr(address, "__repr__", lambda: address)(),),
        )
        self.widgets: OscillatorWidgets | None = None
        self._on_waveform_selected = waveform_selected_callback
        self.widgets_waveform_buttons: dict = wave_buttons or {}
        self.analog: bool = True
        self.wave_shapes = self.generate_wave_shapes()
        log.info(scope=self.__class__.__name__, message="_define_spec ...")
        self._define_spec()
        log.info(scope=self.__class__.__name__, message="calling super().__init__ ...")
        super().__init__(
            icons_row_type=IconType.OSCILLATOR,
            analog=True,
            midi_helper=midi_helper,
            address=address,
            send_midi_parameter=send_midi_parameter,
        )
        log.info(
            scope=self.__class__.__name__,
            message="after super().__init__ (controls keys: %s)"
            % (list(self.controls.keys()) if getattr(self, "controls", None) else [],),
        )
        self.address = address
        log.info(scope=self.__class__.__name__, message="calling finalize() ...")
        self.finalize()
        log.info(scope=self.__class__.__name__, message="AnalogOscillatorSection __init__ done.")

    def _define_spec(self):
        self.spec: AnalogOscillatorLayoutSpec = self._build_layout_spec()

    def _create_feature_widgets_old(self):
        log.info(scope=self.__class__.__name__, message="_create_feature_widgets ...")
        env_sliders = self._build_sliders(self.spec.env)
        self.osc_pitch_env_velocity_sensitivity_slider = (
            env_sliders[0] if env_sliders else None
        )
        if not hasattr(self, "spec") or not hasattr(self.spec, "switches"):
            switches = []
        else:
            switches = self._build_switches(self.spec.switches)
        self.sub_oscillator_type_switch = switches[0] if switches else None

        tuning = self._build_sliders(self.spec.tuning)
        self.tuning_sliders = tuning
        log.info(
            scope=self.__class__.__name__,
            message="_create_feature_widgets done (tuning_sliders=%s)"
            % (len(self.tuning_sliders) if self.tuning_sliders else 0,),
        )

    def build_widgets(self):
        """Build widgets: run base to create waveform buttons, pitch env, PWM, then analog-specific (sub-osc switch, tuning)."""
        log.info(scope=self.__class__.__name__, message="build_widgets start")
        super().build_widgets()
        log.info(scope=self.__class__.__name__, message="build_widgets after super()")
        # Base does not call _build_additional_analog_widgets; we must call it so env/tuning/switch sliders exist
        # Reuse pitch_env_widget and pwm_widget if already created by _build_additional_analog_widgets
        pitch_env = getattr(self, "pitch_env_widget", None) or self._create_pitch_env_widget()
        pwm = getattr(self, "pwm_widget", None) or self._create_pwm_widget()
        self.pitch_env_widget = pitch_env
        self.pwm_widget = pwm
        # All oscillator widgets in one container
        self.widgets = AnalogOscillatorWidgets(
            waveform_buttons=self._create_waveform_buttons(),
            pitch_env_widget=pitch_env,
            pwm_widget=pwm,
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
            osc_pitch_coarse_slider=getattr(
                self, AnalogOscillatorWidgetTypes.OSC_PITCH_COARSE, None
            ),
            osc_pitch_fine_slider=getattr(
                self, AnalogOscillatorWidgetTypes.OSC_PITCH_FINE, None
            ),
            pitch_env_widgets=getattr(
                self, AnalogOscillatorWidgetTypes.PITCH_ENV_WIDGETS, []
            ),
        )
        # Aliases to old widgets for back compatibility
        self.widgets_waveform_buttons = self.widgets.waveform_buttons
        self.widgets.pitch_env_widget = self.widgets.pitch_env_widget
        self.pitch_env_widgets = [self.widgets.pitch_env_widget]
        log.info(scope=self.__class__.__name__, message="build_widgets calling _build_additional_widgets()")
        self._build_additional_widgets()
        log.info(scope=self.__class__.__name__, message="build_widgets done")

    def generate_wave_shapes(self) -> list:
        """Generate waveform button specs (same pattern as Analog LFO / Analog Filter)."""
        return self.generate_wave_shapes_analog()

    def _build_additional_widgets(self):
        self._build_additional_analog_widgets()

    def _build_additional_analog_widgets(self):
        """build additional analog widgets"""
        # log.info(scope=self.__class__.__name__, message="_build_additional_analog_widgets start")
        self._create_env_slider()
        self._create_suboscillator_switches()
        self._ensure_widgets()  # needed for now

    def _create_suboscillator_switches(self):
        """Sub Oscillator Type switch; optional when SWITCH_SPECS is empty"""
        if not hasattr(self, "spec") or not hasattr(self.spec, "switches"):
            switches = []
        else:
            switches = self._build_switches(self.spec.switches)
        self.sub_oscillator_type_switch = switches[0] if len(switches) == 1 else None

    def _ensure_widgets(self):
        # --- Ensure pitch_env_widget and pwm_widget exist before _create_tab_widget (base uses
        # self.pitch_env_widgets and self.widgets.pwm_widget; at this point we're still inside
        # super().build_widgets() so self.widgets is not yet the AnalogOscillatorWidgets instance)
        if getattr(self, "pitch_env_widget", None) is None:
            self.pitch_env_widget = self._create_pitch_env_widget()
        if getattr(self, "pwm_widget", None) is None:
            self.pwm_widget = self._create_pwm_widget()
        self.pitch_env_widgets = [w for w in [self.pitch_env_widget] + (
            [self.osc_pitch_env_velocity_sensitivity_slider]
            if self.osc_pitch_env_velocity_sensitivity_slider is not None
            else []
        ) if w is not None]
        # --- Base _create_pw_group and _create_pitch_env_group need self.widgets.pwm_widget and
        # self.pitch_env_widgets; provide a minimal namespace so _create_tab_widget() can run
        if not isinstance(getattr(self, "widgets", None), AnalogOscillatorWidgets):
            self.widgets = SimpleNamespace(
                pitch_env_widget=self.pitch_env_widget,
                pwm_widget=self.pwm_widget,
            )

    def _create_env_slider(self):
        """Create env sliders"""
        # Only one slider BTW, despite the plural name
        env_sliders = self._build_sliders(self.spec.env)
        self.osc_pitch_env_velocity_sensitivity_slider = (
            env_sliders[0] if len(env_sliders) == 1 else None
        )

    def _build_layout_spec(self) -> AnalogOscillatorLayoutSpec:
        """Build Analog Oscillator Layout Spec"""
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
                OscillatorFeature.WAVEFORM,
                OscillatorFeature.TUNING,
                OscillatorFeature.PWM,
                OscillatorFeature.PITCH_ENV,
                OscillatorFeature.PW_SHIFT,
            },
            feature_tabs={
                OscillatorFeature.TUNING: self._add_tuning_tab,
                OscillatorFeature.PWM: self._add_pwm_tab,
                OscillatorFeature.PITCH_ENV: self._add_pitch_env_tab,
            },
        )
