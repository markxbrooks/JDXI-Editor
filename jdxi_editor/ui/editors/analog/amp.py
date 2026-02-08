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
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.adsr.spec import ADSRSpec, ADSRStage
from jdxi_editor.ui.editors.base.amp import BaseAmpSection
from jdxi_editor.ui.widgets.spec import SliderSpec


class AnalogAmpSection(BaseAmpSection):
    """Amp section of the JD-Xi editor"""

    # Slider parameter storage and generation (same pattern as Digital Amp / Analog Oscillator)
    SLIDER_GROUPS = {
        "controls": [
            SliderSpec(
                Analog.Param.AMP_LEVEL,
                Analog.Display.Name.AMP_LEVEL,
                vertical=True,
            ),
            SliderSpec(
                Analog.Param.AMP_LEVEL_KEYFOLLOW,
                Analog.Display.Name.AMP_LEVEL_KEYFOLLOW,
                vertical=True,
            ),
            SliderSpec(
                Analog.Param.AMP_LEVEL_VELOCITY_SENSITIVITY,
                Analog.Display.Name.AMP_LEVEL_VELOCITY_SENSITIVITY,
                vertical=True,
            ),
        ],
    }

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
        parent: Optional[QWidget] = None,
        send_midi_parameter=None,
        midi_helper: MidiIOHelper = None,
    ):
        super().__init__(
            analog=True,
            address=address,
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
        )
        # setup_ui not called for analog from SectionBaseWidget.__init__; build_widgets already ran in super().__init__
        self.setup_ui()
