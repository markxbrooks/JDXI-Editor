"""
Analog Filter Section
"""

from typing import Callable, Dict, Optional

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import (
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.filter import BaseFilterSection
from jdxi_editor.ui.widgets.spec import FilterSpec, SliderSpec


class AnalogFilterSection(BaseFilterSection):
    """Analog Filter Section"""

    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Analog.Param.FILTER_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Analog.Param.FILTER_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(ADSRStage.SUSTAIN, Analog.Param.FILTER_ENV_SUSTAIN_LEVEL),
        ADSRStage.RELEASE: ADSRSpec(ADSRStage.RELEASE, Analog.Param.FILTER_ENV_RELEASE_TIME),
        ADSRStage.PEAK: ADSRSpec(ADSRStage.PEAK, Analog.Param.FILTER_ENV_DEPTH),
    }

    SLIDER_GROUPS = {
        "filter": [
            SliderSpec(AnalogParam.FILTER_RESONANCE, "Resonance", vertical=True),
            SliderSpec(AnalogParam.FILTER_CUTOFF_KEYFOLLOW, "KeyFollow", vertical=True),
            SliderSpec(AnalogParam.FILTER_ENV_VELOCITY_SENSITIVITY, "Velocity", vertical=True),
        ],
    }
    
    FILTER_SPECS: Dict[AnalogFilterType, FilterSpec] = {
        AnalogFilterType.BYPASS: FilterSpec(
            param=None,  # No parameter adjustments for bypass
            icon=JDXi.UI.Icon.POWER,  # Power/off icon
            name="BPF",
            description=AnalogFilterType.BYPASS.tooltip
    ),
        AnalogFilterType.LPF: FilterSpec(
            param=Analog.Param.FILTER_MODE_SWITCH,  # Key parameter for low-pass filter
            icon=JDXi.UI.Icon.FILTER,  # Filter icon
            name="LPF",
            description=AnalogFilterType.LPF.tooltip
    ),
    }

    def __init__(
        self,
        controls: dict[AddressParameter, QWidget],
        address: RolandSysExAddress,
        on_filter_mode_changed: Callable = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the AnalogFilterSection

        :param controls: dict[AddressParameter, QWidget] controls to add to
        :param address: RolandSysExAddress
        :param on_filter_mode_changed: Optional callback for filter mode changes
        """
        super().__init__(controls=controls,
                         address=address,
                         on_filter_mode_changed=on_filter_mode_changed,
                         parent=parent)

        self.build_widgets()
        self.setup_ui()
