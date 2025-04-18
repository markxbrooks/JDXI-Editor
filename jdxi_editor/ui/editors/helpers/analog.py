import logging

from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog


def get_analog_parameter_by_address(address: int):
    """Retrieve the DigitalParameter by its address."""
    logging.info(f"address: {address}")
    for param in AddressParameterAnalog:
        if param.address == address:
            logging.info(f"get_analog_parameter_by_address found param: {param}")
            return param
    return None
