"""filter slider to modify nrpn parameters"""

import logging

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class AmpLevelSlider(ControlChangeSlider):
    """
    A class to represent a amp slider for JD-Xi using NRPN.
    """
    def __init__(
        self,
        midi_helper,
        label: str = "Levl.",
    ):
        nrpn_map = {
            1: 117,  # NRPN LSB for Partial 1
            2: 118,  # Partial 2
            3: 119,  # Partial 3
        }
        print(nrpn_map)
        nrpn_map = DigitalControlChange.get_cc_map("Level")
        print(nrpn_map)
        super().__init__(
            midi_helper=midi_helper,
            label=label,
            nrpn_map=nrpn_map
        )
