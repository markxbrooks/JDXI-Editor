"""
Digital Filter Section for the JDXI Editor
"""

from typing import Dict

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.filter import DigitalFilterType, DigitalFilterTypeEnum
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.filter import BaseFilterSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import SliderSpec, FilterSpec, FilterWidgetSpec


class DigitalFilterSection(BaseFilterSection):
    """Digital Filter Section for JD-Xi Digital Partial"""

    SLIDER_GROUPS = {
        "filter": [
            SliderSpec(Digital.Param.FILTER_RESONANCE, "Resonance", vertical=True),
            SliderSpec(Digital.Param.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow", vertical=True),
            SliderSpec(Digital.Param.FILTER_ENV_VELOCITY_SENSITIVITY, "Velocity", vertical=True),
            SliderSpec(
                Digital.Param.FILTER_ENV_DEPTH, Digital.Display.Name.FILTER_ENV_DEPTH
            ),
        ],
    }

    # --- Filter mode buttons
    BUTTON_SPECS = [
        SliderSpec(
            Digital.Filter.Mode.BYPASS,
            Digital.Filter.FilterType.BYPASS,
            icon_name=JDXi.UI.Icon.Wave.BYPASS_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF,
            Digital.Filter.FilterType.LPF,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.HPF,
            Digital.Filter.FilterType.HPF,
            icon_name=JDXi.UI.Icon.Wave.HPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.BPF,
            Digital.Filter.FilterType.BPF,
            icon_name=JDXi.UI.Icon.Wave.BPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.PKG,
            Digital.Filter.FilterType.PKG,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF2,
            Digital.Filter.FilterType.LPF2,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF3,
            Digital.Filter.FilterType.LPF3,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
        SliderSpec(
            Digital.Filter.Mode.LPF4,
            Digital.Filter.FilterType.LPF4,
            icon_name=JDXi.UI.Icon.Wave.LPF_FILTER,
        ),
    ]

    BUTTON_ENABLE_RULES = {
        Digital.Filter.Mode.BYPASS: [],  # disables everything
        # --- Other modes: all sliders are enabled (default)
    }

    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Digital.Param.FILTER_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Digital.Param.FILTER_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Digital.Param.FILTER_ENV_SUSTAIN_LEVEL),
        ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Digital.Param.FILTER_ENV_RELEASE_TIME),
        ADSRStage.PEAK: ADSRSpec(ADSRStage.PEAK, Digital.Param.FILTER_ENV_DEPTH),
    }

    FILTER_SPECS: Dict[DigitalFilterType, FilterSpec] = {
        DigitalFilterType.BYPASS: FilterSpec(
            param=None,
            icon=JDXi.UI.Icon.POWER,
            name=DigitalFilterTypeEnum.BYPASS.name,
            description=DigitalFilterTypeEnum.BYPASS.tooltip,
        ),
        DigitalFilterType.LPF: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF.name,
            description=DigitalFilterTypeEnum.LPF.tooltip,
        ),
        DigitalFilterType.HPF: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.HPF.name,
            description=DigitalFilterTypeEnum.HPF.tooltip,
        ),
        DigitalFilterType.BPF: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.BPF.name,
            description=DigitalFilterTypeEnum.BPF.tooltip,
        ),
        DigitalFilterType.PKG: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.PKG.name,
            description=DigitalFilterTypeEnum.PKG.tooltip,
        ),
        DigitalFilterType.LPF2: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF2.name,
            description=DigitalFilterTypeEnum.LPF2.tooltip,
        ),
        DigitalFilterType.LPF3: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF3.name,
            description=DigitalFilterTypeEnum.LPF3.tooltip,
        ),
        DigitalFilterType.LPF4: FilterSpec(
            param=Digital.Param.FILTER_MODE_SWITCH,
            icon=JDXi.UI.Icon.FILTER,
            name=DigitalFilterTypeEnum.LPF4.name,
            description=DigitalFilterTypeEnum.LPF4.tooltip,
        ),
    }

    FILTER_WIDGET_SPEC = FilterWidgetSpec(cutoff_param=Digital.Param.FILTER_CUTOFF,
                                          slope_param=Digital.Param.FILTER_SLOPE, )

    SYNTH_SPEC = Digital

    FILTER_MODE_ENABLED_MAP = {
        0: Digital.Filter.Mode.BYPASS,
        1: Digital.Filter.Mode.LPF,
        2: Digital.Filter.Mode.HPF,
        3: Digital.Filter.Mode.BPF,
        4: Digital.Filter.Mode.PKG,
        5: Digital.Filter.Mode.LPF2,
        6: Digital.Filter.Mode.LPF3,
        7: Digital.Filter.Mode.LPF4,
    }

    # Map Digital.Filter.Mode to filter mode string
    FILTER_MODE_MIDI_MAP = {
        Digital.Filter.Mode.BYPASS: Digital.Filter.ModeType.BYPASS,
        Digital.Filter.Mode.LPF: Digital.Filter.ModeType.LPF,
        Digital.Filter.Mode.HPF: Digital.Filter.ModeType.HPF,
        Digital.Filter.Mode.BPF: Digital.Filter.ModeType.BPF,
        Digital.Filter.Mode.PKG: Digital.Filter.ModeType.LPF,  # PKG uses LPF-style plot
        Digital.Filter.Mode.LPF2: Digital.Filter.ModeType.LPF,
        Digital.Filter.Mode.LPF3: Digital.Filter.ModeType.LPF,
        Digital.Filter.Mode.LPF4: Digital.Filter.ModeType.LPF,
    }

    FILTER_PARAMS_LIST = [
        Digital.Param.FILTER_CUTOFF,
        Digital.Param.FILTER_SLOPE,
        Digital.Param.FILTER_RESONANCE,
        Digital.Param.FILTER_CUTOFF_KEYFOLLOW,
        Digital.Param.FILTER_ENV_VELOCITY_SENSITIVITY,
        Digital.Param.FILTER_ENV_DEPTH,
    ]

    def __init__(self, *, icons_row_type: str = IconType.ADSR, **kwargs):
        """Initialize DigitalFilterSection with ADSR icon type"""
        super().__init__(icons_row_type=icons_row_type, **kwargs)
