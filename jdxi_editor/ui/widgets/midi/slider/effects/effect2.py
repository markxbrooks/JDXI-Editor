"""filter slider to modify nrpn parameters"""

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class Effect2Slider(ControlChangeSlider):
    """
    A class to represent a filter cutoff slider for JD-Xi using NRPN.
    """

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        label: str = "Delay",
    ):
        nrpn_map = {
            1: 15,  # NRPN LSB for Partial 1
            2: 15,  # Partial 2
            3: 15,  # Partial 3
        }
        super().__init__(
            midi_helper=midi_helper, label=label, nrpn_map=nrpn_map, channels=[15]
        )
        """Initialize the Effect2Slider.

        :param midi_helper: MidiIOHelper
        :param label: str
        """
