"""Editor modules for JD-Xi parameters"""

# First import base editor since others depend on it
from jdxi_manager.ui.editors.base_editor import BaseEditor

# Then import specific editors
from jdxi_manager.ui.editors.analog import AnalogSynthEditor
from jdxi_manager.ui.editors.digital import DigitalSynthEditor
from jdxi_manager.ui.editors.drums import DrumKitEditor as DrumEditor
from jdxi_manager.ui.editors.effects import EffectsEditor
from jdxi_manager.ui.editors.arpeggio import ArpeggioEditor

__all__ = [
    'BaseEditor',
    'AnalogSynthEditor',
    'DigitalSynthEditor',
    'DrumEditor',
    'EffectsEditor',
    'ArpeggioEditor'
] 