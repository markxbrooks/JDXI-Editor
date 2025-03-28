"""Editor modules for JD-Xi parameters"""

# First import base editor since others depend on it
from jdxi_editor.ui.editors.synth.editor import SynthEditor

# Then import specific editors
from jdxi_editor.ui.editors.analog.analog import AnalogSynthEditor
from jdxi_editor.ui.editors.digital.common import DigitalCommonEditor
from jdxi_editor.ui.editors.drum.common import DrumCommonEditor
from jdxi_editor.ui.editors.arpeggio.arpeggio import ArpeggioEditor
from jdxi_editor.ui.editors.effects.effects import EffectsEditor
from jdxi_editor.ui.editors.effects.vocal import VocalFXEditor
from jdxi_editor.ui.editors.io.program import ProgramEditor
from jdxi_editor.ui.editors.io.midi_file import MidiFileEditor

__all__ = [
    "SynthEditor",
    "AnalogSynthEditor",
    "DigitalCommonEditor",
    "DrumCommonEditor",
    "ArpeggioEditor",
    "EffectsEditor",
    "VocalFXEditor",
    "ProgramEditor",
    "MidiFileEditor",
]
