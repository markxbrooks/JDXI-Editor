from enum import Enum


class AddressParameterEffectCommon(Enum):
    """Common parameters for Effects."""

    PROGRAM_EFFECT_1 = 0x02
    PROGRAM_EFFECT_2 = 0x04
    PROGRAM_DELAY = 0x06
    PROGRAM_REVERB = 0x08

    @property
    def address(self):
        return self.value  # Access Enum value correctly
