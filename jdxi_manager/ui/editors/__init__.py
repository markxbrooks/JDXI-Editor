"""Editor modules for JD-Xi parameters"""

# First import base editor since others depend on it
from jdxi_manager.ui.editors.synth import SynthEditor

# Then import specific editors
from jdxi_manager.ui.editors.analog import AnalogSynthEditor
from jdxi_manager.ui.editors.digital import DigitalSynthEditor
from jdxi_manager.ui.editors.drum import DrumEditor
from jdxi_manager.ui.editors.arpeggio import ArpeggioEditor
from jdxi_manager.ui.editors.effects import EffectsEditor
from jdxi_manager.ui.editors.vocal_fx import VocalFXEditor
from jdxi_manager.ui.editors.program import ProgramEditor

__all__ = [
    "AnalogSynthEditor",
    "DigitalSynthEditor",
    "DrumEditor",
    "ArpeggioEditor",
    "EffectsEditor",
    "VocalFXEditor",
    "ProgramEditor",
]
