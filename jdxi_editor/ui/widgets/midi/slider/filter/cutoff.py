"""filter slider to modify nrpn parameters"""

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class FilterCutoffSlider(ControlChangeSlider):
    """
    A class to represent a filter cutoff slider for JD-Xi using NRPN.
    """

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        label: str = "Cutoff.",
    ):
        """Initialize the FilterCutoffSlider.

        :param midi_helper: MidiIOHelper
        :param label: str
        """
        nrpn_map = DigitalControlChange.get_cc_map("Cutoff")
        super().__init__(midi_helper=midi_helper, label=label, nrpn_map=nrpn_map)
