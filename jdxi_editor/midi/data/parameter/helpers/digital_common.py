from jdxi_editor.midi.data.parameter.digital_common import DigitalCommonParameter


def parse_digital_common_parameters(data: list) -> dict:
    """
    Parses JD-Xi tone parameters from SysEx data, including Oscillator, Filter, and Amplifier parameters.

    Args:
        data (bytes): SysEx message containing tone parameters.

    Returns:
        dict: Parsed parameters.
    """

    # Function to safely retrieve values from `data`
    def safe_get(index, default=0):
        tone_name_length = 12
        index = index + tone_name_length # shift the index by 12 to account for the tone name
        return data[index] if index < len(data) else default

    parameters = {}

    # Mapping DigitalParameter Enum members to their respective positions in SysEx data
    for param in DigitalCommonParameter:
        # Use the parameter's address from the enum and fetch the value from the data
        parameters[param.name] = safe_get(param.address)

    return parameters
