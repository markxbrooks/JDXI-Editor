import logging
from jdxi_editor.ui.widgets.slider import Slider

class ControlChangeSlider(Slider):
    """
    A base class for sliders with a common on_value_changed method to send Control Change (CC) messages.
    """

    def __init__(
        self,
        midi_helper,
        partial: int,
        min_value: int,
        max_value: int,
        label: str,
        nrpn_map: dict,
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
        self.valueChanged.connect(self.on_value_changed)
        self.setTickPosition(self.TickPosition.NoTicks)
        self.nrpn_map = nrpn_map

    def on_value_changed(self, value: int):
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