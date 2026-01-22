"""
AMP section for the digital partial editor.
"""

from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.editors.widget_specs import SliderSpec


class DigitalAmpSection(ParameterSectionBase):
    """Digital Amp Section for JD-Xi Editor"""

    PARAM_SPECS = [
        SliderSpec(DigitalPartialParam.AMP_LEVEL, DigitalDisplayName.AMP_LEVEL),
        SliderSpec(DigitalPartialParam.AMP_LEVEL_KEYFOLLOW, DigitalDisplayName.AMP_LEVEL_KEYFOLLOW),
        SliderSpec(DigitalPartialParam.AMP_VELOCITY, DigitalDisplayName.AMP_VELOCITY),
        SliderSpec(DigitalPartialParam.LEVEL_AFTERTOUCH, DigitalDisplayName.LEVEL_AFTERTOUCH),
        SliderSpec(DigitalPartialParam.CUTOFF_AFTERTOUCH, DigitalDisplayName.CUTOFF_AFTERTOUCH),
        SliderSpec(DigitalPartialParam.AMP_PAN, DigitalDisplayName.AMP_PAN),  # Horizontal pan
    ]

    ADSR_SPEC = {
        "attack": DigitalPartialParam.AMP_ENV_ATTACK_TIME,
        "decay": DigitalPartialParam.AMP_ENV_DECAY_TIME,
        "sustain": DigitalPartialParam.AMP_ENV_SUSTAIN_LEVEL,
        "release": DigitalPartialParam.AMP_ENV_RELEASE_TIME,
    }

    BUTTON_SPECS = []  # Digital Amp does not have waveform buttons
