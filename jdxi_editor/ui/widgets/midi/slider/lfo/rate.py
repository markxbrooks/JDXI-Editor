"""LFO Rate slider: the JD-Xi's LFO Rate knob, CC 16-18 (one per Digital partial; the Analog: 16)."""

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange
from jdxi_editor.ui.widgets.midi.slider.control_change import ControlChangeSlider


class LFORateSlider(ControlChangeSlider):
    """
    The LFO rate, as the JD-Xi's knob sends it: Control Change 16, 17, 18
    (MIDI Implementation, Control Change Message List; doc/control-change-map.md).

    It sent NRPN 21-23 (an «LFO_Rate» NRPN entry copied from LFO Amp Depth):
    the Rate slider changed the LFO amp depth, which the Amp slider then showed,
    and the LFO rate never changed.
    """

    def __init__(
        self,
        midi_helper,
        label: str = "Rate",
    ):
        cc_map = DigitalControlChange.get_cc_map("LFO_Rate")
        super().__init__(midi_helper=midi_helper, label=label, nrpn_map=cc_map)
