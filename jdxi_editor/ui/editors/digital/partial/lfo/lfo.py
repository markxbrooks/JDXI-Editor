"""
LFO section of the digital partial editor.
"""

from typing import Callable, Literal

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.editor import IconType


class DigitalLFOSection(BaseLFOSection):
    """LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Fade"

    SYNTH_SPEC = Digital

    def __init__(
        self,
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        address: JDXiSysExAddress = None,
        icons_row_type=IconType.ADSR,
        analog=False,
    ):
        """
        Initialize the DigitalLFOSection

        :param send_midi_parameter: Callable to send MIDI parameter updates
        :param midi_helper: MidiIOHelper for MIDI communication
        :param address: RolandSysExAddress for this partial (required for sending MIDI)
        """
        self.wave_shape_buttons = {}

        super().__init__(
            icons_row_type=icons_row_type,
            analog=analog,
            send_midi_parameter=send_midi_parameter,
            address=address,
            midi_helper=midi_helper,
        )
        self.send_midi_parameter = send_midi_parameter
        self.midi_helper = midi_helper
        self.wave_shape_param: Literal[Digital.Param.LFO_SHAPE] = (
            Digital.Param.LFO_SHAPE
        )
        self.build_widgets()
        self.setup_ui()
