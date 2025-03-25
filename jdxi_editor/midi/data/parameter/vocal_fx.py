from typing import Optional, Tuple

from jdxi_editor.midi.data.parameter.synth import SynthParameter


class VocalFXParameter(SynthParameter):
    """Vocal FX parameters"""
    LEVEL = (0x00, 0, 127, 0, 127)  # Level (0-127)
    PAN = (0x01, -64, 63, -64, 63)  # Pan (-64 to +63, centered at 64)
    DELAY_SEND_LEVEL = (0x02, 0, 127, 0, 127)  # Delay send level (0-127)
    REVERB_SEND_LEVEL = (0x03, 0, 127, 0, 127)  # Reverb send level (0-127)
    OUTPUT_ASSIGN = (0x04, 0, 4, 0, 4)  # Output assignment (0-4)
    AUTO_PITCH_SWITCH = (0x05, 0, 1, 0, 1)  # Auto Note on/off (0-1)
    AUTO_PITCH_TYPE = (0x06, 0, 3, 0, 3)  # Auto Pitch preset_type (0-3)
    AUTO_PITCH_SCALE = (0x07, 0, 1, 0, 1) # Scale CHROMATIC, Maj(Min)
    AUTO_PITCH_KEY = (0x08, 0, 23, 0, 23)  # Auto Pitch key (0-23) C, Db, D, Eb, E, F, F#, G, Ab, A, Bb, B, Cm, C#m, Dm, D#m, Em, Fm, F#m, Gm, G#m, Am, Bbm, Bm
    AUTO_PITCH_NOTE = (0x09, 0, 11, 0, 11)  # Auto Pitch note (0-11)
    AUTO_PITCH_GENDER = (0x0A, -10, 10, -10, 10)  # Gender (-10 to +10, centered at 0)
    AUTO_PITCH_OCTAVE = (0x0B, -1, 1, -1, 1)  # Octave (-1 to +1: 0-2)
    AUTO_PITCH_BALANCE = (0x0C, 0, 100, 0, 100)  # Dry/Wet Balance (0-100)
    VOCODER_SWITCH = (0x0D, 0, 1)  # Vocoder on/off (0-1)
    VOCODER_ENVELOPE = (0x0E, 0, 2, 0, 2)  # Vocoder envelope preset_type (0-2)
    VOCODER_LEVEL = (0x0F, 0, 127, 0, 127)  # Vocoder level (0-127)
    VOCODER_MIC_SENS = (0x10, 0, 127, 0, 127)  # Vocoder mic sensitivity (0-127)
    VOCODER_SYNTH_LEVEL = (0x11, 0, 127, 0, 127)  # Vocoder synth level (0-127)
    VOCODER_MIC_MIX = (0x12, 0, 127, 0, 127)  # Vocoder mic mix level (0-127)
    VOCODER_MIC_HPF = (0x13, 0, 13, 0, 13)  # Vocoder mic HPF freq (0-13)

    def __init__(self, address: int, min_val: int, max_val: int,
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )
        return value

    #@staticmethod
    #def get_by_name(param_name):
    #    """Get the VocalFXParameter by name."""
    #    # Return the parameter member by name, or None if not found
    #    return VocalFXParameter.__members__.get(param_name, None)

    @staticmethod
    def get_name_by_address(address: int):
        """Return the parameter name for address given address."""
        for param in VocalFXParameter:
            if param.address == address:
                return param.name
        return None  # Return None if the address is not found

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in [
            self.AUTO_PITCH_SWITCH,
            self.VOCODER_SWITCH,
        ]

    @staticmethod
    def get_address(param_name):
        """Get the address of address parameter by name."""
        param = VocalFXParameter.get_by_name(param_name)
        if param:
            return param.value[0]
        return None

    @staticmethod
    def get_range(param_name):
        """Get the value range (min, max) of address parameter by name."""
        param = VocalFXParameter.get_by_name(param_name)
        if param:
            return param.value[1], param.value[2]
        return None, None

    @staticmethod
    def get_display_range(param_name):
        """Get the display value range (min, max) of address parameter by name."""
        param = VocalFXParameter.get_by_name(param_name)
        if param:
            return param.display_min, param.display_max
        return None, None

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display value range (min, max) for the parameter"""
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    def convert_from_display(self, display_value: int) -> int:
        """Convert from display value to MIDI value (0-127)"""
        # Handle bipolar parameters
        if self in [
            self.AUTO_PITCH_GENDER,
            self.PAN,
            self.AUTO_PITCH_BALANCE,
        ]:
            return display_value + 64  # -63 to +63 -> 0 to 127
        else:
            return display_value  # -63 to +63 -> 0 to 126

    @staticmethod
    def convert_to_display(value, min_val, max_val, display_min, display_max):
        """Convert address value to address display value within address range."""
        if min_val == max_val:
            return display_min
        return int((value - min_val) * (display_max - display_min) / (max_val - min_val) + display_min)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value"""
        # Handle special bipolar cases first
        if self == VocalFXParameter.PAN:
            return display_value + 64  # -63 to +63 -> 0 to 127
        elif self == VocalFXParameter.AUTO_PITCH_GENDER:
            return display_value + 10  # -63 to +63 -> 0 to 127

        # For parameters with simple linear scaling
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return int(self.min_val + (display_value - self.display_min) *
                       (self.max_val - self.min_val) / (self.display_max - self.display_min))
        return display_value

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to display value"""
        # Handle special bipolar cases first
        if self == VocalFXParameter.PAN:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == VocalFXParameter.AUTO_PITCH_GENDER:
            return midi_value - 10  # 0 to 127 -> -63 to +63

        # For parameters with simple linear scaling
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return int(self.display_min + (midi_value - self.min_val) *
                       (self.display_max - self.display_min) / (self.max_val - self.min_val))
        return midi_value

    @staticmethod
    def get_display_value_by_name(param_name: str, value: int) -> int:
        """Get the display value for address parameter by name and value."""
        param = VocalFXParameter.get_by_name(param_name)
        if param:
            return param.convert_from_midi(value)
        return value

    @staticmethod
    def get_midi_range(param_name):
        """Get the MIDI value range (min, max) of address parameter by name."""
        param = VocalFXParameter.get_by_name(param_name)
        if param:
            return param.min_val, param.max_val

    @staticmethod
    def get_midi_value(param_name, value):
        """Get the MIDI value for address parameter by name and value."""
        param = VocalFXParameter.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None
