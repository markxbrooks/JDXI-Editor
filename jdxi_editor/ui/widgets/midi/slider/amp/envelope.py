"""filter slider to modify nrpn parameters"""
import logging

from jdxi_editor.ui.widgets.slider import Slider


class AmpEnvelopeSlider(Slider):
    """
    A class to represent a filter slider for JD-Xi using NRPN.
    """

    def __init__(
        self,
        midi_helper,
        partial: int,
        min_value: int,
        max_value: int,
        label: str,
        vertical: bool = True,
    ):
        super().__init__(label, int(min_value), int(max_value), vertical=True)
        self.midi_helper = midi_helper
        self.partial = partial  # 1, 2, or 3
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        self.vertical = vertical
        self.valueChanged.connect(self._on_value_changed)
        self.setTickPosition(self.TickPosition.NoTicks)

        # Map partial number to NRPN controller number for Cutoff
        self.nrpn_map = {
            1: 124,  # NRPN LSB for Partial 1
            2: 125,  # Partial 2
            3: 126,  # Partial 3
        }

    def _on_value_changed(self, value: float):
        """
        Set the current value of the slider and send NRPN messages.
        """
        logging.info(f"filter value: {value} for nrpn slider")
        if self.min_value <= value <= self.max_value:
            self.current_value = value
        else:
            raise ValueError("Value out of range.")

        cc_value = int(
            (value - self.min_value) / (self.max_value - self.min_value) * 127
        )
        logging.info(f"cc_value: {cc_value}")
        nrpn_lsb = self.nrpn_map.get(self.partial)
        if nrpn_lsb is None:
            raise ValueError("Invalid partial number")

        for channel in [0, 1, 2]:  # Optionally send to all partials
            self.midi_helper.send_control_change(99, 0x00, channel)  # NRPN MSB
            self.midi_helper.send_control_change(98, nrpn_lsb, channel)  # NRPN LSB
            self.midi_helper.send_control_change(6, cc_value, channel)  # Data Entry MSB
