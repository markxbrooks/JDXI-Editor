"""
LFO Filter Depth Slider
"""

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.widgets.midi.slider.nrpn import NRPNSlider


class LFOFilterDepthSlider(NRPNSlider):
    """
    A slider for controlling LFO Pitch Depth for JD-Xi partials via NRPN.
    """

    def __init__(self, midi_helper, label: str = "LFO Pitch Depth", is_bipolar=True):
        nrpn_map = DigitalControlChange.get_nrpn_map("LFO_Filter")
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map,
            nrpn_msb=0,  # JD-Xi NRPN MSB
            is_bipolar=is_bipolar,
        )
