"""
UI Parameters
"""

from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions


class JDXiUIParameters:
    """UI options"""

    AnalogName: AnalogDisplayName = AnalogDisplayName
    AnalogOptions: AnalogDisplayOptions = AnalogDisplayOptions
    DigitalName: DigitalDisplayName = DigitalDisplayName
    DigitalOptions: DigitalDisplayOptions = DigitalDisplayOptions
    DrumName: DrumDisplayName = DrumDisplayName
    DrumOptions: DrumDisplayOptions = DrumDisplayOptions
