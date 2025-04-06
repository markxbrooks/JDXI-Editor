"""filter slider to modify nrpn parameters"""
import logging

from jdxi_editor.ui.widgets.slider import Slider


class FilterResonanceSlider(Slider):
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
        super().__init__(label, int(min_value), int(max_value),
                         show_value_label=False,
                         vertical=True,
                         draw_tick_marks=False)
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
            1: 105,  # NRPN LSB for Partial 1
            2: 106,  # Partial 2
            3: 107,  # Partial 3
        }

    def _on_value_changed(self, value: int):
        """
        Set the current value of the slider and send Control Change (CC) messages.
        """
        logging.info(f"filter value: {value} for cutoff slider")

        if self.min_value <= value <= self.max_value:
            self.current_value = value
        else:
            raise ValueError("Value out of range.")

        for partial in [1, 2, 3]:
            cc_number = self.nrpn_map.get(partial)
            if cc_number is None:
                raise ValueError("Invalid partial number")
            for channel in [0, 1, 2]:  # Or just the channel matching this partial
                self.midi_helper.send_control_change(cc_number, value, channel=channel)
