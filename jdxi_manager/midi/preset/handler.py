
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
        self.midi_out_device = midi_helper  # FIXME: Looks incorrect,
        self.midi_in_device = midi_helper  # but still works, so is this needed?
        self.device_number = device_number
        self.debug = 1
        self.midi_lock = 0
        self.midi_last = time.time()
        self.pdm_val = {}
        pub.subscribe(self.load_preset, "request_load_preset")

    def send_pa_ch_msg(self, addr, value, nr):
        if self.midi_out_device:
            while self.midi_lock != 0:
                time.sleep(0.001)  # wait until preceding parameter changes are done
            self.midi_lock = 1  # lock out other parameter change attempts

            if self.debug:
                logging.debug(f"par:[{addr}] val:[{value}] len:[{nr}]")

            # Prepare sysex string to send
            data = ""
            if nr > 1:
                data = f"{value:0{nr}X}"
                data = bytes.fromhex(data)
            else:
                data = bytes([value])

            addr_bytes = bytes.fromhex(addr)
            checksum = calculate_checksum(addr_bytes + data)
            sysex = (
                XI_HEADER
                + bytes([DT1_COMMAND_12])
                + addr_bytes
                + data
                + bytes([checksum, 0xF7])
            )

            # Enforce 2 ms gap since last parameter change message sent
            midi_now = time.time()
            gap = midi_now - self.midi_last
            if gap < 0.002:
                time.sleep(0.002 - gap)

            # Send the MIDI data to the synth
            self.midi_out_device.send_message(sysex)
            self.midi_last = time.time()  # store timestamp
            self.midi_lock = 0  # allow other parameter changes to proceed

    def load_preset(self, preset_data):
        """Load the preset based on the provided data"""
        print(f"Loading preset with data: {preset_data}")
        response = "Yes"
        program = preset_data["selpreset"]
        channel = preset_data["channel"]
        self.midi_helper.send_program_change(program=program, channel=channel)
        if response == "Yes" or preset_data["modified"] == 0:
            address = ""
            msb = 0
            lsb = 64
            self.preset_number = int(preset_data["selpreset"])
            if preset_data["preset_type"] == PresetType.DIGITAL_1:
                address = "18002006"
                msb = 95
                if self.preset_number > 128:
                    lsb = 65
                    self.preset_number -= 128
            elif preset_data["preset_type"] == PresetType.DIGITAL_2:
                address = "18002106"
                msb = 95
                if self.preset_number > 128:
                    lsb = 65
                    self.preset_number -= 128
            elif preset_data["preset_type"] == PresetType.ANALOG:
                address = "18002206"
                msb = 94
            elif preset_data["preset_type"] == PresetType.DRUMS:
                address = "18002306"
                msb = 86

            # Ensure addr is address string before using fromhex
            if not isinstance(address, str):
                raise ValueError("Address must be address string.")

            # Send the correct SysEx messages
            self.send_pa_ch_msg(address, msb, 1)
            self.send_pa_ch_msg(f"{int(address, 16) + 1:08X}", lsb, 1)
            self.send_pa_ch_msg(
                f"{int(address, 16) + 2:08X}", self.preset_number - 1, 1
            )

            # Additional SysEx messages for loading the preset
            self.send_sysex_message("19", "01", "00", "00", "00", "00", "00", "40")
            self.send_sysex_message("19", "01", "20", "00", "00", "00", "00", "3D")
            self.send_sysex_message("19", "01", "21", "00", "00", "00", "00", "3D")
            self.send_sysex_message("19", "01", "22", "00", "00", "00", "00", "3D")
            self.send_sysex_message("19", "01", "50", "00", "00", "00", "00", "25")
            self.update_display.emit(
                preset_data["preset_type"], preset_data["selpreset"] - 1, preset_data["channel"]
            )
            logging.info(f'Emitting update display preset_type: {preset_data["preset_type"]}, preset#: {preset_data["selpreset"]}, channel#: {preset_data["channel"]} ')

    def send_sysex_message(
        self, addr1, addr2, addr3, addr4, data1, data2, data3, data4
    ):
        # Construct the SysEx message
        sysex_msg = [
            0xF0,  # Start of SysEx
            0x41,  # Roland ID
            0x10,  # Device ID
            0x00,
            0x00,
            0x00,
            0x0E,  # Model ID
            0x11,  # Command ID (for additional messages)
            int(addr1, 16),  # Address 1
            int(addr2, 16),  # Address 2
            int(addr3, 16),  # Address 3
            int(addr4, 16),  # Address 4
            int(data1, 16),  # Data 1
            int(data2, 16),  # Data 2
            int(data3, 16),  # Data 3
            int(data4, 16),  # Data 4
            0xF7,  # End of SysEx
        ]

        # Calculate checksum
        checksum = (0x80 - (sum(sysex_msg[8:-1]) & 0x7F)) & 0x7F
        sysex_msg.insert(-1, checksum)

        # Send the SysEx message
        self.midi_helper.send_message(sysex_msg)
        logging.debug(f"Sent SysEx message: {sysex_msg}")

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index += 1
            self.preset_changed.emit(self.current_preset_index, self.channel)  # Emit signal
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index -= 1
            self.preset_changed.emit(self.current_preset_index, self.channel)  # Emit signal
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
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
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
