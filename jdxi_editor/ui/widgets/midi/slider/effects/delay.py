"""filter slider to modify nrpn parameters"""

from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class DelaySlider(ControlChangeSlider):
    """
    A class to represent a filter cutoff slider for JD-Xi using NRPN.
    """
    def __init__(
        self,
        midi_helper,
        label: str = "Delay",
    ):
        nrpn_map = {
            1: 13,  # NRPN LSB for Partial 1
            2: 13,  # Partial 2
            3: 13,  # Partial 3
        }
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map,
            channels=[15]
        )
