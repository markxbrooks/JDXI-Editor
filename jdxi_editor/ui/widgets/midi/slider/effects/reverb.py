"""filter slider to modify nrpn parameters"""

from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class ReverbSlider(ControlChangeSlider):
    """
    A class to represent a filter cutoff slider for JD-Xi using NRPN.
    """
    def __init__(
        self,
        midi_helper,
        label: str = "Reverb.",
    ):
        nrpn_map = {
            1: 12,  # NRPN LSB for Partial 1
            2: 12,  # Partial 2
            3: 12,  # Partial 3
        }
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map,
            channels=[15]
        )
