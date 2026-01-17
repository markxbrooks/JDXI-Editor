"""Helper function for the AnalogParameterEditor."""

from decologr import Decologr as log
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam


def get_analog_parameter_by_address(address: tuple[int]):
    """Retrieve the DigitalParameter by its address."""
    log.parameter("address", address)
    for param in AnalogParam:
        if param.address == address:
            log.message(f"get_analog_parameter_by_address found param: {param}")
            return param
    return None
