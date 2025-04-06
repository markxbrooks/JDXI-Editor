"""filter slider to modify nrpn parameters"""

from jdxi_editor.ui.widgets.slider import Slider


class FilterSlider(Slider):
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

        # Map partial number to NRPN controller number for Cutoff
        self.nrpn_map = {
            1: 102,  # NRPN LSB for Partial 1
            2: 103,  # Partial 2
            3: 104,  # Partial 3
        }

    def set_value(self, value: float):
        """
        Set the current value of the slider and send NRPN messages.
        """
        if self.min_value <= value <= self.max_value:
            self.current_value = value
        else:
            raise ValueError("Value out of range.")

        cc_value = int(
            (value - self.min_value) / (self.max_value - self.min_value) * 127
        )
        nrpn_lsb = self.nrpn_map.get(self.partial)
        if nrpn_lsb is None:
            raise ValueError("Invalid partial number")

        for channel in [0, 1, 2]:  # Optionally send to all partials
            self.midi_helper.send_control_change(99, 0x01, channel)  # NRPN MSB
            self.midi_helper.send_control_change(98, nrpn_lsb, channel)  # NRPN LSB
            self.midi_helper.send_control_change(6, cc_value, channel)  # Data Entry MSB


class FilterSliderOld(Slider):
    """
    A class to represent a filter slider.
    """

    def __init__(
        self,
        midi_helper,
        min_value: float,
        max_value: float,
        label: str,
        min_val: int,
        max_val: int,
        vertical: bool = True,
    ):
        """
        Initialize the FilterSlider with minimum and maximum values.

        :param min_value: Minimum value of the slider.
        :param max_value: Maximum value of the slider.
        """
        super().__init__(label, min_val, max_val, vertical=True)
        self.midi_helper = midi_helper
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        self.vertical = vertical

    def set_value(self, value: float):
        """
        Set the current value of the slider.

        :param value: The value to set.
        """
        if self.min_value <= value <= self.max_value:
            self.current_value = value
        else:
            raise ValueError("Value out of range.")

        cc_value = int(value * 127)

        status = 0xB0 | (channel & 0x0F)
        cc_number = 1  # Filter

        if self.midi_helper.midi_out:
            self.midi_helper.midi_out.send_message([status, cc_number, cc_value])
            for channel in [0, 1, 2]:
                self.midi_helper.send_control_change(
                    cc_number, cc_value, channel=channel
                )
