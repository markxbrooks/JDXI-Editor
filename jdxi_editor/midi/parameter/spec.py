"""
ParameterSpec class
"""


class ParameterSpec(tuple):
    """
    Parameter specification that can be used in place of tuples for Enum definitions.

    Inherits from tuple so Enum can unpack it automatically. Provides named attributes
    for better code readability and IDE support.

    Usage:
        # In Enum class definition:
        PARAM = ParameterSpec(0x10, 0, 127)  # address, min_val, max_val
        PARAM = ParameterSpec(0x10, 0, 127, 0, 127, "Description")  # with all params

        # Access attributes:
        param.address  # 0x10
        param.min_val  # 0
        param.max_val  # 127
    """
    def __new__(cls, address: int, min_val: int, max_val: int,
                min_display: int = 0, max_display: int = 127,
                description: str | None = None,
                display_name: str | None = None):
        # Create tuple with all values - Enum will unpack this
        return super().__new__(cls, (address, min_val, max_val, min_display, max_display, description, display_name))

    def __init__(self, *args):
        """
        Initialize attributes. Handles both direct instantiation and tuple unpacking.

        When used in Enum: Enum unpacks the tuple and calls this with positional args.
        When instantiated directly: receives named parameters.
        """
        # If we got a single tuple (from Enum unpacking), extract values
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]

        # Handle both direct call and unpacked tuple
        if len(args) >= 3:
            self.address = args[0]
            self.min_val = args[1]
            self.max_val = args[2]
            self.min_display = args[3] if len(args) > 3 else 0
            self.max_display = args[4] if len(args) > 4 else 127
            self.description = args[5] if len(args) > 5 else None
        else:
            # This shouldn't happen, but handle gracefully
            self.address = 0
            self.min_val = 0
            self.max_val = 127
            self.min_display = 0
            self.max_display = 127
            self.description = None
