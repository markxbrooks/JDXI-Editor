from pubsub import pub
from typing import List, Callable
from PySide6.QtCore import Signal

from jdxi_manager.midi.input_handler import MIDIInHandler
from jdxi_manager.data.digital import get_digital_parameter_by_address
from jdxi_manager.midi.output_handler import MIDIOutHandler


class MIDIHelper(MIDIInHandler, MIDIOutHandler):
    """Helper class for MIDI communication with the JD-Xi"""

    parameter_received = Signal(list, int)  # address, value
    json_sysex = Signal(str)  # json string only
    parameter_changed = Signal(object, int)  # Emit parameter and value
    preset_changed = Signal(int, str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.callbacks: List[Callable] = []
        self.channel = 1
        self.preset_number = 0
        self.cc_number = 0
        self.cc_msb_value = 0
        self.cc_lsb_value = 0
        pub.subscribe(self._handle_incoming_midi_message, "incoming_midi_message")

    def _get_parameter_from_address(self, address):
        """Map address to a DigitalParameter"""
        # Ensure the address is at least two elements
        if len(address) < 2:
            raise ValueError(
                f"Address must contain at least 2 elements, got {len(address)}"
            )

        # Extract the relevant part of the address (group, address pair)
        parameter_address = tuple(
            address[1:2]
        )  # Assuming address structure [group, address, ...]

        # Retrieve the corresponding DigitalParameter
        param = get_digital_parameter_by_address(parameter_address)

        if param:
            return param
        else:
            raise ValueError(
                f"Invalid address {parameter_address} - no corresponding DigitalParameter found."
            )


