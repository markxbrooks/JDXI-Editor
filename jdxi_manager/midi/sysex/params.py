from typing import List

from jdxi_manager.data.digital import get_digital_parameter_by_address


def get_parameter_from_address(address: List[int]):
    """
    Map a given address to a DigitalParameter.

    Args:
        address: A list representing the address bytes.
    Raises:
        ValueError: If the address is too short or no corresponding DigitalParameter is found.
    Returns:
        The DigitalParameter corresponding to the address.
    """
    if len(address) < 2:
        raise ValueError(f"Address must contain at least 2 elements, got {len(address)}")

    # Assuming address structure [group, address, ...]
    parameter_address = tuple(address[1:2])
    param = get_digital_parameter_by_address(parameter_address)

    if param:
        return param
    else:
        raise ValueError(f"Invalid address {parameter_address} - no corresponding DigitalParameter found.")

