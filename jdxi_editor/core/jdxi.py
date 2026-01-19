"""
JDXi Composition God Object (!)
"""

from jdxi_editor.midi.constant import JDXiMidi
from jdxi_editor.synth.type import JDXiSynth
from jdxi_editor.ui.jdxiui import JDXiUI


class JDXi:
    """Composition of main JDXI components as a single container."""

    Synth: JDXiSynth = JDXiSynth
    UI: JDXiUI = JDXiUI
    Midi: JDXiMidi = JDXiMidi
