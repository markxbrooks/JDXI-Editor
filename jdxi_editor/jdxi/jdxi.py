"""
JDXi Composition God Object (!)
"""

from jdxi_editor.jdxi.jdxiui import JDXiUI
from jdxi_editor.jdxi.midi.constant import JDXiMidi


class JDXi:
    """Composition of main JDXI UI components as a single, immutable container."""

    UI: JDXiUI = JDXiUI
    Midi: JDXiMidi = JDXiMidi
