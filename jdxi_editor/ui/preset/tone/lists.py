"""
JDXi presets
"""

from jdxi_editor.ui.preset.tone.analog.list import JDXiPresetToneListAnalog
from jdxi_editor.ui.preset.tone.digital.list import JDXiPresetToneListDigital
from jdxi_editor.ui.preset.tone.drum.list import JDXiPresetToneListDrum


class JDXiPresetToneList:
    """JDXi Preset 'Tone' lists for each of the 3 parts; Analog, Digital and Drums"""

    Analog: JDXiPresetToneListAnalog = JDXiPresetToneListAnalog
    Digital: JDXiPresetToneListDigital = JDXiPresetToneListDigital
    Drum: JDXiPresetToneListDrum = JDXiPresetToneListDrum
