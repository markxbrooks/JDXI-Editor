"""filter slider to modify nrpn parameters"""
from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider
from jdxi_editor.ui.widgets.midi.slider.nrpn import NRPNSlider


class LFORateSlider(NRPNSlider):
    """
    A class to represent a amp slider for JD-Xi using NRPN.
    """
    def __init__(
        self,
        midi_helper,
        label: str = "Reson.",
    ):
        nrpn_map = DigitalControlChange.get_nrpn_map("LFO_Rate")
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map
        )
