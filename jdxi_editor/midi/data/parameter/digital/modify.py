"""
DigitalModifyParameter: JD-Xi Digital Synthesizer Parameter Mapping
====================================================================
Defines the DigitalModifyParameter class for modifying parameters of
Digital/SuperNATURAL synth tones in the JD-Xi.

This class provides attributes and methods to manage various modulation
parameters shared across all partials of a digital synth tone. It also
includes methods for retrieving display text representations of switch
values, parameter lookup by name, and value validation.

Example usage:

# Create a DigitalModifyParameter instance for Attack Time Interval Sensitivity
attack_time_param = DigitalModifyParameter(*DigitalModifyParameter.ATTACK_TIME_INTERVAL_SENS)

# Validate a value
validated_value = attack_time_param.validate_value(100)

# Get display text for a switch value
text = attack_time_param.get_switch_text(1)  # For ENVELOPE_LOOP_MODE, returns "FREE-RUN"

# Retrieve parameter by name
param = DigitalModifyParameter.get_by_name("ENVELOPE_LOOP_MODE")
if param:
    print(param.name, param.min_val, param.max_val)

"""
from jdxi_editor.midi.data.address.address import SuperNATURALAddressOffset
from jdxi_editor.midi.data.parameter.synth import SynthParameter


class DigitalModifyParameter(SynthParameter):
    """Modify parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    def __init__(self, address: int, min_val: int, max_val: int):
        super().__init__(address, min_val, max_val) 
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    ATTACK_TIME_INTERVAL_SENS = (0x00, 0, 127)
    RELEASE_TIME_INTERVAL_SENS = (0x01, 0, 127)
    PORTAMENTO_TIME_INTERVAL_SENS = (0x02, 0, 127)
    ENVELOPE_LOOP_MODE = (0x03, 0, 2)
    ENVELOPE_LOOP_SYNC_NOTE = (0x05, 0, 19)
    CHROMATIC_PORTAMENTO = (0x06, 0, 1)

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.ENVELOPE_LOOP_MODE:
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif self == self.CHROMATIC_PORTAMENTO:
            return ["OFF", "ON"][value]
        elif self == self.ENVELOPE_LOOP_SYNC_NOTE:
            return ["16", "12", "8", "4", "2", "1", "3/4", "2/3", "1/2", "3/8", "1/3", "1/4", "3/16", "1/6", "1/8", "3/32", "1/12", "1/16", "1/24", "1/32"][value]
        return str(value)
    
    @staticmethod
    def get_by_name(param_name):
        """Get the Parameter by name."""
        # Return the parameter member by name, or None if not found
        return DigitalModifyParameter.__members__.get(param_name, None)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value)}")

        # Validate range for specific parameters
        if self == self.ENVELOPE_LOOP_SYNC_NOTE and not (0 <= value <= 19):
            raise ValueError(f"Value {value} out of range for {self.name} (valid range: 0-19)")

        return value

    def get_address_for_partial(self, partial_number: int = 0):
        return SuperNATURALAddressOffset.TONE_MODIFY, 0x00
