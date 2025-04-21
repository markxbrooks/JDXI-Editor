"""Editor modules for JD-Xi parameters"""

# First import base editor since others depend on it
from jdxi_editor.ui.editors.synth.editor import SynthEditor

# Then import specific editors
from jdxi_editor.ui.editors.analog.editor import AnalogSynthEditor
from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
from jdxi_editor.ui.editors.drum.editor import DrumCommonEditor
from jdxi_editor.ui.editors.arpeggio.arpeggio import ArpeggioEditor
from jdxi_editor.ui.editors.effects.common import EffectsCommonEditor
from jdxi_editor.ui.editors.effects.vocal import VocalFXEditor
from jdxi_editor.ui.editors.io.program import ProgramEditor

__all__ = [
    "SynthEditor",
    "AnalogSynthEditor",
    "DigitalSynthEditor",
    "DrumCommonEditor",
    "ArpeggioEditor",
    "EffectsCommonEditor",
    "VocalFXEditor",
    "ProgramEditor",
]
