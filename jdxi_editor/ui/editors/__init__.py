"""Editor modules for JD-Xi parameters"""

# IMPORTANT: Import SynthEditor FIRST since it's the base class that others depend on
# This prevents circular import issues when other modules import from this __init__.py
# Then import specific editors that depend on SynthEditor
from jdxi_editor.ui.editors.analog.editor import AnalogSynthEditor
from jdxi_editor.ui.editors.arpeggio.arpeggio import ArpeggioEditor
from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor
from jdxi_editor.ui.editors.drum.editor import DrumCommonEditor
from jdxi_editor.ui.editors.effects.common import EffectsCommonEditor
from jdxi_editor.ui.editors.effects.vocal import VocalFXEditor
from jdxi_editor.ui.editors.io.program import ProgramEditor
from jdxi_editor.ui.editors.synth.editor import SynthEditor

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
