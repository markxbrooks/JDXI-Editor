"""
Control Change Slider

sends CC, (N)RPN messages to the synth

def send_nrpn(self, channel, msb, lsb, value):
    self.send_control_change(99, msb, channel)  # NRPN MSB
    self.send_control_change(98, lsb, channel)  # NRPN LSB
    self.send_control_change(6, value, channel)  # Data Entry MSB
    # Optional: Reset NRPN selection
    self.send_control_change(99, 127, channel)
    self.send_control_change(98, 127, channel)

"""

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.slider import Slider


class ControlChangeSlider(Slider):
    """
    A base class for sliders with a common on_valueChanged method to send Control Change (CC) messages.
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
        is_bipolar=False,
    ):
        super().__init__(
            label,
            min_value=min_value,
            max_value=max_value,
            midi_helper=midi_helper,
            vertical=vertical,
            show_value_label=False,
            draw_tick_marks=False,
            is_bipolar=is_bipolar,
        )
        """Initialize the ControlChangeSlider.

        :param midi_helper: MidiIOHelper
        :param label: str
        :param nrpn_map: dict
        :param partial: int
        :param min_value: int
        :param max_value: int
        :param vertical: bool
        :param channels: list
        """
        self.channels = channels
        self.label = label
        self.current_value = min_value
        self.vertical = vertical
        self.update_style(min_value)
        self.valueChanged.connect(self.on_valueChanged)
        self.setTickPosition(self.TickPosition.NoTicks)
        self.nrpn_map = nrpn_map
        self.setStyleSheet(JDXi.UI.Style.ADSR_DISABLED)

    def update_style(self, value: int) -> None:
        """Update the style of the slider.

        :param value: int
        """
        if value == 0:
            self.setStyleSheet(JDXi.UI.Style.ADSR_DISABLED)
        else:
            JDXi.UI.ThemeManager.apply_adsr_style(self, analog=False)

    def on_valueChanged(self, value: int):
        """
        Set the current value of the slider and send Control Change (CC) messages.

        :param value: int
        """
        self.setStyleSheet(JDXi.UI.Style.ADSR_DISABLED)
        log.message(f"filter value: {value} for cutoff slider")

        if self.min_value <= value <= self.max_value:
            self.current_value = value
        else:
            raise ValueError("Value out of range.")

        self.update_style(value)

        for partial in [1, 2, 3]:
            log.message(self.nrpn_map)
            cc_number = self.nrpn_map.get(partial)
            if cc_number is None:
                raise ValueError("Invalid partial number")
            for channel in self.channels:  # Or just the channel matching this partial
                self.midi_helper.send_control_change(cc_number, value, channel=channel)
        self.update_style(value)
