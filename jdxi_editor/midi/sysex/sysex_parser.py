"""

Sysex parser
# Example usage:
sysex_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x7E, 0x7F, 0x06, 0x01, 0x19, 0x01, 0x00,
              0xF7]  # Example SysEx data

parser = SysExParser(sysex_data)
parsed_data = parser.parse()
logging.info(f"Parsed Data: {parsed_data}")


"""

import logging
from typing import Optional, List, Type, Dict

from jdxi_editor.midi.data.address.address import ProgramAddressOffset, DrumKitParameter, UnknownToneAddress, \
    TemporaryToneAddressOffset, Address, END_OF_SYSEX, START_OF_SYSEX, JD_XI_HEADER_LIST, MemoryAreaAddress
from jdxi_editor.midi.data.parameter.analog import AnalogParameter


import logging
from typing import Optional, List, Type, Dict

from jdxi_editor.midi.data.address.address import ProgramAddressOffset, DrumKitParameter, UnknownToneAddress, \
    TemporaryToneAddressOffset, Address, END_OF_SYSEX, START_OF_SYSEX, JD_XI_HEADER_LIST
from jdxi_editor.midi.data.parameter.analog import AnalogParameter


class SysExParser:
    def __init__(self, sysex_data: List[int]):
        self.sysex_data = sysex_data

    def parse(self):
        if not self._is_valid_sysex():
            raise ValueError("Invalid SysEx message")

        # Remove the SysEx start (F0) and end (F7) bytes
        data = self.sysex_data[1:-1]

        # Verify the JD-Xi header
        if not self._verify_header(data[:len(JD_XI_HEADER_LIST)]):
            raise ValueError("Invalid JD-Xi header")
        else:
            print("correct JDXI header found")

        # Extract the address and the corresponding data
        address = data[len(JD_XI_HEADER_LIST)]
        print(f"Extracted address: {address}")  # Log address for debugging
        try:
            parameter = MemoryAreaAddress.get_parameter_by_address(int(address))
            print(parameter)
        except Exception as ex:
            print(f"Exception {ex} occurred")

        if parameter:
            # Extract the parameter-specific data (following the address byte)
            parameter_data = data[len(JD_XI_HEADER_LIST) + 1:]
            return self._parse_parameter(parameter, parameter_data)
        else:
            logging.warning(f"Unrecognized address: {address}. Skipping.")
            return {}  # Handle unknown address gracefully

    def _is_valid_sysex(self) -> bool:
        """Checks if the SysEx message starts and ends with the correct bytes."""
        return self.sysex_data[0] == START_OF_SYSEX and self.sysex_data[-1] == END_OF_SYSEX

    def _verify_header(self, header_data: List[int]) -> bool:
        """Checks if the SysEx header matches the JD-Xi model ID."""
        return header_data == JD_XI_HEADER_LIST

    def _parse_parameter(self, parameter: Address, data: List[int]):
        """Parses the parameter data according to the parameter type."""
        if isinstance(parameter, ProgramAddressOffset):
            return self._parse_program_parameter(parameter, data)
        elif isinstance(parameter, DrumKitParameter):
            return self._parse_drum_kit_parameter(parameter, data)
        elif isinstance(parameter, UnknownToneAddress):
            return self._parse_tone_parameter(parameter, data)
        elif isinstance(parameter, TemporaryToneAddressOffset):
            return self._parse_temporary_parameter(parameter, data)
        # Add other parameter types parsing as needed
        return {}

    def _parse_program_parameter(self, parameter: ProgramAddressOffset, data: List[int]):
        """Parse data for Program parameters."""
        # Example: Extract and process data for PART_DIGITAL_SYNTH_1
        if parameter == ProgramAddressOffset.PART_DIGITAL_SYNTH_1:
            return {"synth_1_data": data}
        # Add other program parameter parsing logic here
        return {}

    def _parse_drum_kit_parameter(self, parameter: DrumKitParameter, data: List[int]):
        """Parse data for Drum Kit parameters."""
        # Example: Extract drum kit data
        if parameter == DrumKitParameter.PARTIAL_1:
            return {"drum_part_1": data}
        # Add other drum kit parameter parsing logic here
        return {}

    def _parse_tone_parameter(self, parameter: UnknownToneAddress, data: List[int]):
        """Parse data for Tone parameters."""
        # Example: Extract and process data for Tone parameters
        if parameter == UnknownToneAddress.TONE_1_LEVEL:
            return {"tone_1_level": data[0]}  # Assuming data[0] holds the tone level for TONE_1_LEVEL
        elif parameter == UnknownToneAddress.TONE_2_LEVEL:
            return {"tone_2_level": data[0]}  # Assuming data[0] holds the tone level for TONE_2_LEVEL
        # Add other tone parameter parsing logic here
        return {}

    def _parse_temporary_parameter(self, parameter: TemporaryToneAddressOffset, data: List[int]):
        """Parse data for Temporary parameters."""
        # Example: Extract and process data for Temporary parameters
        if parameter == TemporaryToneAddressOffset.DIGITAL_PART_1:
            return {"digital_part_1_data": data}
        elif parameter == TemporaryToneAddressOffset.DIGITAL_PART_2:
            return {"digital_part_2_data": data}
        elif parameter == TemporaryToneAddressOffset.ANALOG_PART:
            return {"analog_part_data": data}
        elif parameter == TemporaryToneAddressOffset.DRUM_KIT_PART:
            return {"drum_kit_part_data": data}
        # Add other temporary parameter parsing logic here
        return {}

    def parse_parameters(self, data: List[int], parameter_type: Type) -> Dict[str, int]:
        """Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types."""
        return {param.name: self.safe_get(data, param.address) for param in parameter_type}

    def parse_sysex(self, data: List[int]):
        """An example method to parse a full SysEx message."""
        # Example of extracting parameters
        analog_params = self.parse_parameters(data, AnalogParameter)  # Use your own parameter class
        print(analog_params)  # Example output
        # Further parsing logic here...

    def safe_get(self, data: List[int], address: int) -> int:
        """Safely retrieves the value from SysEx data based on the address."""
        if 0 <= address < len(data):
            return data[address]
        return 0  # Default value if address is out of bounds


if __name__ == "__main__":
    sysex_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x19, 0x01, 0x20, 0x01, 0x19, 0x01, 0x00,
                  0xF7]  # Example SysEx data

    parser = SysExParser(sysex_data)
    parsed_data = parser.parse()
    logging.info(f"Parsed Data: {parsed_data}")


