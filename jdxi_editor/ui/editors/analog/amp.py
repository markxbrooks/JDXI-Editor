"""
Amp section of the JD-Xi editor

This section contains the controls for the amp section of the JD-Xi editor.
"""

from typing import Dict, Optional, Union

from PySide6.QtWidgets import (
    QWidget,
)

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.amp import BaseAmpSection
from jdxi_editor.ui.widgets.spec import SliderSpec


class AnalogAmpSection(BaseAmpSection):
    """Amp section of the JD-Xi editor"""

    PARAM_SPECS = [
        SliderSpec(Analog.Param.AMP_LEVEL, Analog.Display.Name.AMP_LEVEL),
        SliderSpec(
            Analog.Param.AMP_LEVEL_KEYFOLLOW, Analog.Display.Name.AMP_LEVEL_KEYFOLLOW
        ),
        SliderSpec(
            Analog.Param.AMP_LEVEL_VELOCITY_SENSITIVITY,
            Analog.Display.Name.AMP_LEVEL_VELOCITY_SENSITIVITY,
        ),
    ]
    ADSR_SPEC: Dict[ADSRStage, ADSRSpec] = {
        ADSRStage.ATTACK: ADSRSpec(ADSRStage.ATTACK, Analog.Param.AMP_ENV_ATTACK_TIME),
        ADSRStage.DECAY: ADSRSpec(ADSRStage.DECAY, Analog.Param.AMP_ENV_DECAY_TIME),
        ADSRStage.SUSTAIN: ADSRSpec(
            ADSRStage.SUSTAIN, Analog.Param.AMP_ENV_SUSTAIN_LEVEL
        ),
        ADSRStage.RELEASE: ADSRSpec(
            ADSRStage.RELEASE, Analog.Param.AMP_ENV_RELEASE_TIME
        ),
    }

    SYNTH_SPEC = Analog

    def __init__(
        self,
        address,
        controls: dict,
        parent: Optional[QWidget] = None,
    ):

        # --- Dynamic widgets storage
        self.amp_sliders = {}
        self.tab_widget = None
        self.layout = None

        super().__init__(
            analog=True,
            parent=parent,
            controls=controls,
            address=address,
        )
        self.build_widgets()
        self.setup_ui()
