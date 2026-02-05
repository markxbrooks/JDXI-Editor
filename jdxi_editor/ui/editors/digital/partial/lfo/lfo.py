"""
LFO section of the digital partial editor.
"""

from typing import Callable, Literal

from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.editor import IconType


class DigitalLFOSection(BaseLFOSection):
    """LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Fade"

    SYNTH_SPEC = Digital

    def __init__(
        self,
        controls: dict,
        send_midi_parameter: Callable = None,
        icons_row_type=IconType.ADSR,
        analog=False,
    ):
        """
        Initialize the DigitalLFOSection

        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self.controls = controls

        super().__init__(
            icons_row_type=icons_row_type,
            analog=analog,
            send_midi_parameter=send_midi_parameter,
        )
        self.send_midi_parameter = send_midi_parameter
        self.wave_shape_param: Literal[Digital.Param.LFO_SHAPE] = (
            Digital.Param.LFO_SHAPE
        )
        self.build_widgets()
        self.setup_ui()
