"""filter slider to modify nrpn parameters"""

from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class FilterCutoffSlider(ControlChangeSlider):
    """
    A class to represent a filter cutoff slider for JD-Xi using NRPN.
    """
    def __init__(
        self,
        midi_helper,
        label: str = "Reson.",
    ):
        nrpn_map = {
            1: 102,  # NRPN LSB for Partial 1
            2: 103,  # Partial 2
            3: 104,  # Partial 3
        }
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map
        )
