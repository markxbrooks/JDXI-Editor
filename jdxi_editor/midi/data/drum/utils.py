from typing import Tuple

from jdxi_editor.midi.data.drum.data import DRUM_ADDRESSES


def get_address_for_partial(partial_num: int) -> Tuple[int, int]:
    """Get parameter area and address adjusted for partial number"""
    LO = DRUM_ADDRESSES[partial_num][
        2
    ]  # Skip the first row (common area), then extract the 3rd byte (zero-based index)
    HI = LO + 1
    return int(f"{LO:02X}", 16), int(f"{HI:02X}", 16)

def get_address_for_partial_new(partial_num: int) -> int:
    """Get parameter area and address adjusted for partial number"""
    address = DRUM_ADDRESSES[partial_num][2]
    return int(f"{address:02X}", 16)


def _on_tva_level_velocity_sens_slider_changed(self, value: int):
    """Handle TVA Level Velocity Sens change"""
    if self.midi_helper:
        # Convert -63 to +63 range to MIDI value (0 to 127)
        midi_value = value + 63  # Center at 63
        self.midi_helper.send_parameter(
            area=DRUM_KIT_AREA,
            part=DRUM_PART,
            group=DRUM_LEVEL,
            param=0x137,  # Address for TVA Level Velocity Sens
            value=midi_value,
        )
        logging.info(f"TVA Level Velocity Sens changed to {midi_value}")


