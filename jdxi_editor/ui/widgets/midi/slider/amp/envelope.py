"""filter slider to modify nrpn parameters"""

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.midi.slider.nrpn import NRPNSlider


class AmpEnvelopeSlider(NRPNSlider):
    """
    The JD-Xi's ENV knob (NRPN 124-126): it acts on the tone's envelope *relative*
    to it, 64 (the middle) leaving the program as saved. The JD-Xi does not say
    where its knob is and loads every program as saved, the knob counting only
    once turned: the slider starts in the middle and goes back there with every
    program (it started at 0, the shortest envelope: moved there, no sound).
    """

    NEUTRAL = 64

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
        self.reset_to_neutral()

    def reset_to_neutral(self) -> None:
        """The program as saved: the middle, nothing sent."""
        self.setValueSilently(self.NEUTRAL)
        self.current_value = self.NEUTRAL
        self.update_style(self.NEUTRAL)
