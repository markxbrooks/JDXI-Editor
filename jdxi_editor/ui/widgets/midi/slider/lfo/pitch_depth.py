"""filter slider to modify nrpn parameters

CC#99 – NRPN MSB

CC#98 – NRPN LSB

CC#6 – Data Entry MSB (value: 0–127)

(Optional) CC#38 – Data Entry LSB (if 14-bit needed, but not in your case)

CC#101 & 100 – Reset to NULL (optional, to avoid data confusion)

"""

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.widgets.midi.slider.nrpn import NRPNSlider


class LFOPitchSlider(NRPNSlider):
    """
    A slider for controlling LFO Pitch Depth for JD-Xi partials via NRPN.
    """

    def __init__(self, midi_helper, label: str = "LFO Pitch Depth"):
        nrpn_map = DigitalControlChange.get_nrpn_map("LFO_Pitch")
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map,
            nrpn_msb=0,  # JD-Xi NRPN MSB
        )
