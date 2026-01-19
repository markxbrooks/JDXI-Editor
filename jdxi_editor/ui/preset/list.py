"""
JDXi Presets
"""
from jdxi_editor.ui.preset.manager import JDXiPresetManager
from jdxi_editor.ui.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.ui.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.ui.programs.drum import DRUM_KIT_LIST


class JDXiUIPresetList:
    """Preset Lists"""
    Analog: list = ANALOG_PRESET_LIST
    Digital: list = DIGITAL_PRESET_LIST
    Drum: list = DRUM_KIT_LIST
    Manager: JDXiPresetManager = JDXiPresetManager
