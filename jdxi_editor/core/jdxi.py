"""
JDXi Composition God Object (!)
"""

from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.constant import JDXiMidi
from jdxi_editor.ui.jdxiui import JDXiUI


class JDXi:
    """
    Composition of main JDXI components as a single container.

    Model of the data for all UI & Midi parameters as a single tree, importable at whichever branch needed.

    Example:
    >>> from jdxi_editor.midi.data.parameter.digital.EDITOR_PARAM import JDXiMidiDigital as Digital
    """

    Synth: JDXiSynth = JDXiSynth
    UI: JDXiUI = JDXiUI
    Midi: JDXiMidi = JDXiMidi
