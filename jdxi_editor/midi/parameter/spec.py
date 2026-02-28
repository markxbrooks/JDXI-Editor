"""
ParameterSpec class
"""

# Common ranges (min_val, max_val, min_display, max_display) for ParameterSpec
RANGE_BIPOLAR_63 = (1, 127, -63, 63)


class ParameterSpec(tuple):
    """
    Parameter specification that can be used in place of tuples for Enum definitions.

    Inherits from tuple so Enum can unpack it automatically. Provides named attributes
    for better code readability and IDE support.

    Usage:
        # In Enum class definition:
        PARAM = ParameterSpec(0x10, 0, 127)  # address, min_val, max_val
        PARAM = ParameterSpec(0x10, 0, 127, description="Description")  # with all params

        # Access attributes:
        param.address  # 0x10
        param.min_val  # 0
        param.max_val  # 127
    """

    def __new__(
        cls,
        address: int,
        min_val: int,
        max_val: int,
        min_display: int = 0,
        max_display: int = 127,
        description: str | None = None,
        display_name: str | None = None,
        options: list | None = None,
        values: list | None = None,
    ):
        # Tuple has only 7 elements so Enum unpacking passes 7 args to param __init__.
        # options/values are stored only as attributes in __init__, not in the tuple.
        return super().__new__(
            cls,
            (
                address,
                min_val,
                max_val,
                min_display,
                max_display,
                description,
                display_name,
            ),
        )

    def __init__(self, *args, **kwargs):
        """
        Initialize attributes. Handles both direct instantiation and tuple unpacking.

        When used in Enum: Enum unpacks the tuple and calls this with positional args.
        When instantiated directly: receives named parameters (e.g. description=..., display_name=...).
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
            self.description = args[5] if len(args) > 5 else kwargs.get("description")
            self.display_name = args[6] if len(args) > 6 else kwargs.get("display_name")
            self.options = args[7] if len(args) > 7 else kwargs.get("options")
            self.values = args[8] if len(args) > 8 else kwargs.get("values")
        else:
            # This shouldn't happen, but handle gracefully
            self.address = 0
            self.min_val = 0
            self.max_val = 127
            self.min_display = 0
            self.max_display = 127
            self.description = None
            self.display_name = None
            self.options = None
            self.values = None

        # Keyword args override when passed (e.g. ParameterSpec(0x01, 0, 127, description="..."))
        for k, v in kwargs.items():
            setattr(self, k, v)
