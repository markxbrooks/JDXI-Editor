"""filter slider to modify nrpn parameters"""

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class FilterResonanceSlider(ControlChangeSlider):
    """
    A class to represent a filter resonance slider for JD-Xi using NRPN.
    """

    def __init__(
        self,
        midi_helper,
        label: str = "Reson.",
    ):
        nrpn_map = DigitalControlChange.get_cc_map("Resonance")
        super().__init__(midi_helper=midi_helper, label=label, nrpn_map=nrpn_map)
