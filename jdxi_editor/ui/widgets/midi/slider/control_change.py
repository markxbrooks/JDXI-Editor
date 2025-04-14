"""

def send_nrpn(self, channel, msb, lsb, value):
    self.send_control_change(99, msb, channel)  # NRPN MSB
    self.send_control_change(98, lsb, channel)  # NRPN LSB
    self.send_control_change(6, value, channel)  # Data Entry MSB
    # Optional: Reset NRPN selection
    self.send_control_change(99, 127, channel)
    self.send_control_change(98, 127, channel)

"""

import logging

from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.ui.widgets.slider import Slider


class ControlChangeSlider(Slider):
    """
    A base class for sliders with a common on_value_changed method to send Control Change (CC) messages.
    """

    def __init__(
        self,
        midi_helper,
        label: str,
        nrpn_map: dict,
        partial: int = 1,
        min_value: int = 0,
        max_value: int = 127,
        vertical: bool = True,
        channels: list = [0, 1, 2],
    ):
        super().__init__(
            label,
            min_val=min_value,
            max_val=max_value,
            vertical=vertical,
            show_value_label=False,
            draw_tick_marks=False,
        )
        self.channels = channels
        self.label = label
        self.midi_helper = midi_helper
        self.partial = partial  # 1, 2, or 3
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        self.vertical = vertical
        self.update_style(min_value)
        self.valueChanged.connect(self.on_value_changed)
        self.setTickPosition(self.TickPosition.NoTicks)
        self.nrpn_map = nrpn_map
        self.setStyleSheet(JDXIStyle.ADSR_DISABLED)

    def update_style(self, value: int):
        if value == 0:
            self.setStyleSheet(JDXIStyle.ADSR_DISABLED)
        else:
            self.setStyleSheet(JDXIStyle.ADSR)

    def on_value_changed(self, value: int):
        """
        Set the current value of the slider and send Control Change (CC) messages.
        """
        self.setStyleSheet(JDXIStyle.ADSR_DISABLED)
        logging.info(f"filter value: {value} for cutoff slider")

        if self.min_value <= value <= self.max_value:
            self.current_value = value
        else:
            raise ValueError("Value out of range.")

        self.update_style(value)

        for partial in [1, 2, 3]:
            logging.info(self.nrpn_map)
            cc_number = self.nrpn_map.get(partial)
            if cc_number is None:
                raise ValueError("Invalid partial number")
            for channel in self.channels:  # Or just the channel matching this partial
                self.midi_helper.send_control_change(cc_number, value, channel=channel)
        self.update_style(value)
