"""
Digital Filter Section for the JDXI Editor
"""

from typing import Dict

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.filter import (
    DigitalFilterType,
    DigitalFilterTypeEnum,
)
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.filter.definition import FilterDefinition
from jdxi_editor.ui.editors.base.filter.filter import BaseFilterSection
from jdxi_editor.ui.editors.base.filter.spec import FilterLayoutSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import FilterSpec, FilterWidgetSpec, SliderSpec


class DigitalFilterSection(BaseFilterSection):
    """Digital Filter Section for JD-Xi Digital Partial"""

    BUTTON_ENABLE_RULES = {
        Digital.Filter.Mode.BYPASS: [],  # disables everything
        # --- Other modes: all sliders are enabled (default)
    }

    FILTER_WIDGET_SPEC = FilterWidgetSpec(
        cutoff_param=Digital.Param.FILTER_CUTOFF,
        slope_param=Digital.Param.FILTER_SLOPE,
    )

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

    def generate_wave_shapes(self):
        """Generate filter mode button specs (same pattern as Analog Filter / Digital Oscillator)."""
        F = self.SYNTH_SPEC.Filter
        I = JDXi.UI.Icon.WaveForm
        return [
            SliderSpec(F.Mode.BYPASS, F.FilterType.BYPASS, icon_name=I.BYPASS_FILTER),
            SliderSpec(F.Mode.LPF, F.FilterType.LPF, icon_name=I.LPF_FILTER),
            SliderSpec(F.Mode.HPF, F.FilterType.HPF, icon_name=I.HPF_FILTER),
            SliderSpec(F.Mode.BPF, F.FilterType.BPF, icon_name=I.BPF_FILTER),
            SliderSpec(F.Mode.PKG, F.FilterType.PKG, icon_name=I.LPF_FILTER),
            SliderSpec(F.Mode.LPF2, F.FilterType.LPF2, icon_name=I.LPF_FILTER),
            SliderSpec(F.Mode.LPF3, F.FilterType.LPF3, icon_name=I.LPF_FILTER),
            SliderSpec(F.Mode.LPF4, F.FilterType.LPF4, icon_name=I.LPF_FILTER),
        ]

    def _build_filter_spec(self) -> dict[str, FilterSpec]:
        """build filter spec"""
        filter = {
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
        return filter

    def __init__(self, *, icons_row_type: str = IconType.ADSR, **kwargs):
        """Initialize DigitalFilterSection with ADSR icon type"""
        self.wave_shapes = self.generate_wave_shapes()
        self.spec: FilterLayoutSpec = self._build_layout_spec()
        self.spec_adsr = self.spec.adsr
        self.spec_filter: dict[str, FilterSpec] = self._build_filter_spec()
        self.DEFINITION = FilterDefinition(
            modes=DigitalFilterTypeEnum,
            param_mode=Digital.Param.FILTER_MODE_SWITCH,
            midi_to_mode={
                0: DigitalFilterTypeEnum.BYPASS,
                1: DigitalFilterTypeEnum.LPF,
            },
            mode_to_midi={
                DigitalFilterTypeEnum.BYPASS: 0,
                DigitalFilterTypeEnum.LPF: 1,
            },
            specs=self.spec_filter,
            widget_spec=self.FILTER_WIDGET_SPEC,
            sliders=self.spec,
            adsr=self.spec.adsr,
            bypass_mode=DigitalFilterTypeEnum.BYPASS,
        )
        super().__init__(definition=self.DEFINITION, **kwargs)
