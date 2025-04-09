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


class NRPNSlider(Slider):
    """
    A base class for sliders that send NRPN messages to a specified partial.
    """

    def __init__(
        self,
        midi_helper,
        label: str,
        nrpn_map: dict,
        partial: int = 1,
        nrpn_msb: int = 0,
        min_value: int = 0,
        max_value: int = 127,
        vertical: bool = True,
        param_type: str = "nrpn"
    ):
        super().__init__(
            label,
            min_val=min_value,
            max_val=max_value,
            vertical=vertical,
            show_value_label=False,
            draw_tick_marks=False,
        )

        self.label = label
        self.midi_helper = midi_helper
        self.partial = partial
        self.nrpn_map = nrpn_map
        self.nrpn_msb = nrpn_msb
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = min_value
        self.vertical = vertical
        self.setTickPosition(self.TickPosition.NoTicks)
        self.valueChanged.connect(self.on_value_changed)
        self.param_type = param_type  # "nrpn" or "rpn"
        self.update_style(self.current_value)

    def update_style(self, value: int):
        if value == 0:
            self.setStyleSheet(JDXIStyle.ADSR_DISABLED)
        else:
            self.setStyleSheet(JDXIStyle.ADSR)

    def on_value_changed(self, value: int):
        """
        Set the current value of the slider and send NRPN or RPN messages.
        """
        logging.info(f"{self.label} value changed to {value}")

        if not self.min_value <= value <= self.max_value:
            raise ValueError("Value out of range.")

        self.current_value = value
        self.update_style(value)

        for partial in [1, 2, 3]:
            param_lsb = self.nrpn_map.get(partial)
            if param_lsb is None:
                raise ValueError(f"Invalid partial number: {partial}")

            parameter = (self.nrpn_msb << 7) | param_lsb

            for channel in [0, 1, 2]:
                if self.param_type == "nrpn":
                    self.midi_helper.send_nrpn(parameter=parameter, value=value, channel=channel)
                elif self.param_type == "rpn":
                    self.midi_helper.send_rpn(parameter=parameter, value=value, channel=channel)
                else:
                    raise ValueError(f"Unsupported parameter type: {self.param_type}")

