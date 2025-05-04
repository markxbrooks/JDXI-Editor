"""Digital"""

from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)


def parse_digital_parameters(data: list) -> dict:
    """
    Parses JD-Xi tone parameters from SysEx data, including Oscillator, Filter, and Amplitude parameters.

    :param data: bytes SysEx message containing tone parameters.
    :return: dict Parsed parameters.
    """

    def safe_get(index: int, default: int = 0) -> int:
        """
        Safely retrieve values from `data`
        :param index: int The index
        :param default: int The default value
        :return: int The value
        """
        tone_name_length = 12
        index = (
            index + tone_name_length
        )  # shift the index by 12 to account for the tone name
        return data[index] if index < len(data) else default

    parameters = {}

    # Mapping DigitalParameter Enum members to their respective positions in SysEx data
    for param in AddressParameterDigitalPartial:
        # Use the parameter's address from the enum and fetch the value from the data
        parameters[param.name] = safe_get(param.address)

    return parameters
