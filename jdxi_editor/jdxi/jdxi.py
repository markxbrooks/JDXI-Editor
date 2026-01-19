"""
JDXi Composition God Object (!)
"""

from jdxi_editor.jdxi.jdxiui import JDXiUI
from jdxi_editor.jdxi.midi.constant import JDXiMidi
from jdxi_editor.jdxi.synth.type import JDXiSynth


class JDXi:
    """Composition of main JDXI components as a single container."""
    Synth: JDXiSynth = JDXiSynth
    UI: JDXiUI = JDXiUI
    Midi: JDXiMidi = JDXiMidi
