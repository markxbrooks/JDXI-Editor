""" Helper function for the AnalogParameterEditor."""

from jdxi_editor.log.message import log_message
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog


def get_analog_parameter_by_address(address: tuple[int]):
    """Retrieve the DigitalParameter by its address."""
    log_parameter("address", address)
    for param in AddressParameterAnalog:
        if param.address == address:
            log_message(f"get_analog_parameter_by_address found param: {param}")
            return param
    return None
