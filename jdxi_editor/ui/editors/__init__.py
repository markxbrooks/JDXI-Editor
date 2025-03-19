"""Editor modules for JD-Xi parameters"""

# First import base editor since others depend on it
from jdxi_editor.ui.editors.synth import SynthEditor

# Then import specific editors
from jdxi_editor.ui.editors.analog import AnalogSynthEditor
from jdxi_editor.ui.editors.digital import DigitalSynthEditor
from jdxi_editor.ui.editors.drum import DrumEditor
from jdxi_editor.ui.editors.arpeggio import ArpeggioEditor
from jdxi_editor.ui.editors.effects import EffectsEditor
from jdxi_editor.ui.editors.vocal_fx import VocalFXEditor
from jdxi_editor.ui.editors.program import ProgramEditor
from jdxi_editor.ui.editors.midi_file import MidiFileEditor

__all__ = [
    "SynthEditor",
    "AnalogSynthEditor",
    "DigitalSynthEditor",
    "DrumEditor",
    "ArpeggioEditor",
    "EffectsEditor",
    "VocalFXEditor",
    "ProgramEditor",
    "MidiFileEditor",
]
