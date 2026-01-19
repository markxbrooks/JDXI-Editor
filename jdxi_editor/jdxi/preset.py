from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST


class JDXiPresetList:
    """Preset Lists"""
    Analog: list = ANALOG_PRESET_LIST
    Digital: list = DIGITAL_PRESET_LIST
    Drum: list = DRUM_KIT_LIST
