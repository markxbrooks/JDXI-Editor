
import time
import logging
from PySide6.QtCore import Signal, QObject
from pubsub import pub

from jdxi_manager.midi.constants import DT1_COMMAND_12, RQ1_COMMAND_11
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.sysex.sysex import XI_HEADER


def calculate_checksum(data):
    """Calculate Roland checksum for parameter messages"""
    checksum = sum(data) & 0x7F
    result = (128 - checksum) & 0x7F
    return result


class PresetHandler(QObject):
    preset_changed = Signal(int, int)  # Signal emitted when preset changes
    update_display = Signal(int, int, int)

    def __init__(self, midi_helper, presets, device_number=0, channel=1, preset_type=PresetType.DIGITAL_1):
        super().__init__()
        self.presets = presets
        self.channel = channel
        self.type = preset_type
        self.current_preset_index = 0
        self.preset_number = 1  # Default preset
        self.midi_helper = midi_helper
        self.midi_out_device = midi_helper  # FIXME: Looks incorrect, but still works, so is this needed?
        self.midi_in_device = midi_helper  # Same as above
        self.device_number = device_number
        self.debug = 1
        self.midi_last = time.time()
        self.pdm_val = {}
        pub.subscribe(self.load_preset, "request_load_preset")

    def _send_sysex_message(self, addr1, addr2, addr3, addr4, data1, data2, data3, data4):
        """Helper function to send a SysEx message."""
        sysex_msg = [
            0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11,
            int(addr1, 16), int(addr2, 16), int(addr3, 16), int(addr4, 16),
            int(data1, 16), int(data2, 16), int(data3, 16), int(data4, 16),
            0xF7,
        ]

        # Calculate checksum
        checksum = (0x80 - (sum(sysex_msg[8:-1]) & 0x7F)) & 0x7F
        sysex_msg.insert(-1, checksum)

        # Send the SysEx message
        self.midi_helper.send_message(sysex_msg)
        logging.debug(f"Sent SysEx message: {sysex_msg}")

    def _send_parameter_change_message(self, addr, value, nr):
        """Send parameter change messages over MIDI."""
        if self.midi_out_device:

            if self.debug:
                logging.debug(f"par:[{addr}] val:[{value}] len:[{nr}]")

            # Prepare SysEx string to send
            data = f"{value:0{nr}X}" if nr > 1 else bytes([value])
            addr_bytes = bytes.fromhex(addr)
            checksum = calculate_checksum(addr_bytes + data)
            sysex = (
                XI_HEADER
                + bytes([DT1_COMMAND_12])
                + addr_bytes
                + data
                + bytes([checksum, 0xF7])
            )
            # Send the MIDI data
            self.midi_out_device.send_message(sysex)
            self.midi_last = time.time()

    def load_preset(self, preset_data):
        """Load the preset based on the provided data."""
        logging.info(f"Loading preset with data: {preset_data}")
        program = preset_data["selpreset"]
        channel = preset_data["channel"]
        self.midi_helper.send_program_change(program=program, channel=channel)

        if preset_data.get("modified", 0) == 0 or preset_data.get("response", "") == "Yes":
            address, msb, lsb = self._determine_address_and_values(preset_data)
            self.preset_number = int(preset_data["selpreset"])

            # Send the appropriate SysEx messages
            self._send_parameter_change_message(address, msb, 1)
            self._send_parameter_change_message(f"{int(address, 16) + 1:08X}", lsb, 1)
            self._send_parameter_change_message(f"{int(address, 16) + 2:08X}", self.preset_number - 1, 1)

            # Additional preset-related SysEx messages
            self._send_sysex_message("19", "01", "00", "00", "00", "00", "00", "40")
            self._send_sysex_message("19", "01", "20", "00", "00", "00", "00", "3D")
            self._send_sysex_message("19", "01", "21", "00", "00", "00", "00", "3D")
            self._send_sysex_message("19", "01", "22", "00", "00", "00", "00", "3D")
            self._send_sysex_message("19", "01", "50", "00", "00", "00", "00", "25")

            # Emit display update
            self.update_display.emit(preset_data["preset_type"], preset_data["selpreset"] - 1, preset_data["channel"])
            logging.info(f"Emitting update display preset_type: {preset_data['preset_type']}, preset#: {preset_data['selpreset']}, channel#: {preset_data['channel']}")

    def _determine_address_and_values(self, preset_data):
        """Determine the address and MSB/LSB values based on the preset type."""
        address, msb, lsb = "", 0, 64

        preset_type = preset_data.get("preset_type", PresetType.DIGITAL_1)
        if preset_type == PresetType.DIGITAL_1:
            address = "18002006"
            msb = 95
            if self.preset_number > 128:
                lsb = 65
                self.preset_number -= 128
        elif preset_type == PresetType.DIGITAL_2:
            address = "18002106"
            msb = 95
            if self.preset_number > 128:
                lsb = 65
                self.preset_number -= 128
        elif preset_type == PresetType.ANALOG:
            address = "18002206"
            msb = 94
        elif preset_type == PresetType.DRUMS:
            address = "18002306"
            msb = 86

        return address, msb, lsb

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index += 1
            self.preset_changed.emit(self.current_preset_index, self.channel)  # Emit signal
            self.update_display.emit(self.type, self.current_preset_index, self.channel)  # Emit signal
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_index > 0:
            self.current_preset_index -= 1
            self.preset_changed.emit(self.current_preset_index, self.channel)  # Emit signal
            self.update_display.emit(self.type, self.current_preset_index, self.channel)  # Emit signal
        return self.get_current_preset()

    def get_current_preset(self):
        """Get the current preset details."""
        return {
            "index": self.current_preset_index,
            "preset": self.presets[self.current_preset_index],
            "channel": self.channel,
        }

    def set_channel(self, channel):
        """Set the MIDI channel."""
        self.channel = channel

    def set_preset(self, index):
        """Set the preset manually and emit the signal."""
        if 0 <= index < len(self.presets):
            self.current_preset_index = index
            self.preset_changed.emit(self.current_preset_index, self.channel)
            self.update_display.emit(self.type, self.current_preset_index, self.channel)  # Emit signal
