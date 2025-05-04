"""
This module provides a utility function for retrieving the parameter address
corresponding to a given partial name within the drum section of the JD-Xi.

The function maps partial names to their respective addresses using
`DRUM_ADDRESS_MAP`, ensuring correct parameter access for drum sound editing.

Functions:
    get_address_for_partial_name(partial_name: str) -> int
        Returns the parameter address for the specified drum partial name.
"""


from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_ADDRESS_MAP


def get_address_for_partial_name(partial_name: str) -> int:
    """
    Get parameter area and address adjusted for partial number.
    :param partial_name: str The partial name
    :return: int The address
    """
    address = DRUM_ADDRESS_MAP.get(
        partial_name, 0x00
    )  # Default to 0x00 for common area
    return address
