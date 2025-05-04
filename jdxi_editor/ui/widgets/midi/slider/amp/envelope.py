"""filter slider to modify nrpn parameters"""

from jdxi_editor.ui.widgets.midi.slider.nrpn import NRPNSlider
from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.midi.io.helper import MidiIOHelper


class AmpEnvelopeSlider(NRPNSlider):
    """
    A class to represent a amp slider for JD-Xi using NRPN.
    """

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        label: str = "Envelope.",
    ):
        """Initialize the AmpEnvelopeSlider.

        :param midi_helper: MidiIOHelper
        :param label: str
        """
        nrpn_map = DigitalControlChange.get_nrpn_map("Envelope")
        super().__init__(midi_helper=midi_helper, label=label, nrpn_map=nrpn_map)
