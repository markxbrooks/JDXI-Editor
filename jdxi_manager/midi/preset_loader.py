import logging
import time
from typing import Optional
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.constants import (
    DT1_COMMAND_12,
    RQ1_COMMAND_11,
    DIGITAL_SYNTH_AREA,
    ANALOG_SYNTH_AREA,
    DRUM_KIT_AREA
)

class PresetLoader:
    """Utility class for loading presets via MIDI"""
    
    # Area codes for each synth type
    AREAS = {
        "Digital": 0x20,  # Changed from DIGITAL_SYNTH_AREA
        "Digital 1": 0x20,
        "Digital 2": 0x19,
        "Analog": 0x22,
        "Drums": 0x23
    }
    
    @staticmethod
    def calculate_checksum(data: list[int]) -> int:
        """Calculate Roland checksum for parameter messages"""
        checksum = sum(data) & 0x7F
        result = (128 - checksum) & 0x7F
        logging.debug(f"Calculated checksum for data {[hex(x)[2:].upper().zfill(2) for x in data]}: {hex(result)[2:].upper().zfill(2)}")
        return result

    @staticmethod
    def load_preset(midi_helper: Optional[MIDIHelper], preset_type: str, preset_num: int) -> None:
        """Load a preset using MIDI commands"""
        if not midi_helper:
            logging.error("No MIDI helper available")
            return

        try:
            logging.debug(f"Loading {preset_type} preset {preset_num}")

            # Get the appropriate area code for the synth type
            area = PresetLoader.AREAS.get(preset_type)
            if area is None:
                logging.error(f"Unknown preset type: {preset_type}")
                return

            # First message - Set bank and parameters
            data = [0x18, 0x00, area, 0x06, 0x5F]
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Second message - Set additional parameters
            data = [0x18, 0x00, area, 0x07, 0x40]
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Third message - Set preset number
            data = [0x18, 0x00, area, 0x08, preset_num - 1]  # Convert to 0-based index
            checksum = PresetLoader.calculate_checksum(data)
            midi_helper.send_message([
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, DT1_COMMAND_12,
                *data, checksum, 0xF7
            ])

            # Send parameter messages only for Digital presets
            if preset_type in ["Digital", "Digital 1", "Digital 2"]:
                parameter_addresses = [0x00, 0x20, 0x21, 0x22, 0x50]
                for addr in parameter_addresses:
                    data = [0x19, 0x01, addr, 0x00, 0x00, 0x00, 0x00, 0x40]
                    checksum = PresetLoader.calculate_checksum(data)
                    midi_helper.send_message([
                        0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, RQ1_COMMAND_11,
                        *data, checksum, 0xF7
                    ])
                    time.sleep(0.02)  # Small delay between messages

            logging.debug(f"Successfully loaded {preset_type} preset {preset_num}")

        except Exception as e:
            logging.error(f"Error loading {preset_type} preset: {str(e)}", exc_info=True) 