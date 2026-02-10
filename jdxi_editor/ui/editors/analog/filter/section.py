"""
Analog Filter Section
"""

from typing import Callable, Dict

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.filter.definition import FilterDefinition
from jdxi_editor.ui.editors.base.filter.filter import BaseFilterSection
from jdxi_editor.ui.editors.base.filter.spec import FilterLayoutSpec
from jdxi_editor.ui.widgets.spec import FilterSpec, FilterWidgetSpec, SliderSpec


class AnalogFilterSection(BaseFilterSection):
    """Analog Filter Section"""

    FILTER_SPECS: Dict[AnalogFilterType, FilterSpec] = {
        AnalogFilterType.BYPASS: FilterSpec(
            param=None,  # No parameter adjustments for bypass
            icon=JDXi.UI.Icon.POWER,  # Power/off icon
            name="BYPASS",
            description=AnalogFilterType.BYPASS.tooltip,
        ),
        AnalogFilterType.LPF: FilterSpec(
            param=Analog.Param.FILTER_MODE_SWITCH,  # Key parameter for low-pass filter
            icon=JDXi.UI.Icon.FILTER,  # Filter icon
            name="LPF",
            description=AnalogFilterType.LPF.tooltip,
        ),
    }

    FILTER_WIDGET_SPEC = FilterWidgetSpec(cutoff_param=Analog.Param.FILTER_CUTOFF)

    SYNTH_SPEC = Analog

    MIDI_TO_FILTER: Dict[int, AnalogFilterType]
    FILTER_TO_MIDI: Dict[AnalogFilterType, int]

    UI_TO_FILTER: Dict[Analog.Filter.Mode, AnalogFilterType]

    # Same mechanism as Digital: used by update_controls_state() in base
    FILTER_MODE_ENABLED_MAP = {
        0: Analog.Filter.FilterType.BYPASS,
        1: Analog.Filter.FilterType.LPF,
    }
    FILTER_MODE_MIDI_MAP = {
        Analog.Filter.Mode.BYPASS: Analog.Filter.ModeType.BYPASS,
        Analog.Filter.Mode.LPF: Analog.Filter.ModeType.LPF,
    }
    FILTER_PARAMS_LIST = [
        Analog.Param.FILTER_CUTOFF,
        Analog.Param.FILTER_RESONANCE,
        Analog.Param.FILTER_CUTOFF_KEYFOLLOW,
        Analog.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
        Analog.Param.FILTER_ENV_DEPTH,
    ]

    def __init__(
        self,
        address: JDXiSysExAddress,
        on_filter_mode_changed: Callable = None,
        midi_helper: MidiIOHelper = None,
        send_midi_parameter: Callable = None,
        analog: bool = True,
    ):
        """
        Initialize the AnalogFilterSection

        :param address: RolandSysExAddress
        :param on_filter_mode_changed: Optional callback for filter mode changes
        """
        self.wave_shapes = self.generate_wave_shapes()
        self.spec: FilterLayoutSpec = self._build_layout_spec()
        self.spec_adsr = self.spec.adsr
        self.DEFINITION = FilterDefinition(
            modes=AnalogFilterType,
            param_mode=Analog.Param.FILTER_MODE_SWITCH,
            midi_to_mode={0: AnalogFilterType.BYPASS, 1: AnalogFilterType.LPF},
            mode_to_midi={AnalogFilterType.BYPASS: 0, AnalogFilterType.LPF: 1},
            specs=self.FILTER_SPECS,
            widget_spec=self.FILTER_WIDGET_SPEC,
            sliders=self.spec,
            adsr=self.spec_adsr,
            bypass_mode=AnalogFilterType.BYPASS,
        )
        super().__init__(
            definition=self.DEFINITION,
            address=address,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
            on_filter_mode_changed=on_filter_mode_changed,
            analog=analog,
        )

        self.build_widgets()
        self.setup_ui()

    def generate_wave_shapes(self):
        """Generate filter mode button specs (same pattern as Analog LFO generate_wave_shapes)."""
        return [
            SliderSpec(
                Analog.Filter.Mode.BYPASS,
                Analog.Filter.FilterTypeString.BYPASS,
                icon_name=JDXi.UI.Icon.WaveForm.BYPASS_FILTER,
            ),
            SliderSpec(
                Analog.Filter.Mode.LPF,
                Analog.Filter.FilterTypeString.LPF,
                icon_name=JDXi.UI.Icon.WaveForm.LPF_FILTER,
            ),
        ]

    def _build_layout_spec(self) -> FilterLayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        controls = [
            SliderSpec(
                S.Param.FILTER_RESONANCE,
                S.Param.FILTER_RESONANCE.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.FILTER_CUTOFF_KEYFOLLOW,
                S.Param.FILTER_CUTOFF_KEYFOLLOW.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
                S.Param.FILTER_ENV_VELOCITY_SENSITIVITY.display_name,
                vertical=True,
            ),
        ]
        adsr: Dict[ADSRStage, ADSRSpec] = {
            ADSRStage.ATTACK: ADSRSpec(
                ADSRStage.ATTACK, Analog.Param.FILTER_ENV_ATTACK_TIME
            ),
            ADSRStage.DECAY: ADSRSpec(
                ADSRStage.DECAY, Analog.Param.FILTER_ENV_DECAY_TIME
            ),
            ADSRStage.SUSTAIN: ADSRSpec(
                ADSRStage.SUSTAIN, Analog.Param.FILTER_ENV_SUSTAIN_LEVEL
            ),
            ADSRStage.RELEASE: ADSRSpec(
                ADSRStage.RELEASE, Analog.Param.FILTER_ENV_RELEASE_TIME
            ),
            ADSRStage.DEPTH: ADSRSpec(ADSRStage.DEPTH, Analog.Param.FILTER_ENV_DEPTH),
        }
        return FilterLayoutSpec(controls=controls, adsr=adsr)
