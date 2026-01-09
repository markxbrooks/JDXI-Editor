"""
AddressParameterDigitalModify: JD-Xi Digital Synthesizer Parameter Mapping
====================================================================
Defines the AddressParameterDigitalModify class for modifying parameters of
Digital/SuperNATURAL synth tones in the JD-Xi.

This class provides attributes and methods to manage various modulation
parameters shared across all partials of a digital synth tone. It also
includes methods for retrieving display text representations of switch
values, parameter lookup by name, and value validation.

Example usage:

# Create a AddressParameterDigitalModify instance for Attack Time Interval Sensitivity
attack_time_param = AddressParameterDigitalModify(*AddressParameterDigitalModify.ATTACK_TIME_INTERVAL_SENS)

# Validate a value
validated_value = attack_time_param.validate_value(100)

# Get display text for a switch value
text = attack_time_param.get_switch_text(1)  # For ENVELOPE_LOOP_MODE, returns "FREE-RUN"

# Retrieve parameter by name
param = AddressParameterDigitalModify.get_by_name("ENVELOPE_LOOP_MODE")
if param:
    print(param.name, param.min_val, param.max_val)

"""

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB


class DigitalModifyParam(AddressParameter):
    """Modify parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    def __init__(self, address: int, min_val: int, max_val: int, tooltip: str = ""):
        super().__init__(address, min_val, max_val)
        self.address = address
        self.min_val = min_val
        self.max_val = max_val
        self.tooltip = tooltip

    ATTACK_TIME_INTERVAL_SENS = (
        0x01,
        0,
        127,
        "Shortens the FILTER and AMP Attack Time according to the spacing between note-on events.\nHigher values produce a greater effect. With a setting of 0, there will be no effect.\nThis is effective when you want to play rapid notes using a sound that has a slow attack\n(Attack Time).",
    )
    RELEASE_TIME_INTERVAL_SENS = (
        0x02,
        0,
        127,
        "Shortens the FILTER and AMP Release Time if the interval between one note-on and the next\nnote-off is brief. Higher values produce a greater effect. With a setting of 0, there will be no effect.\nThis is effective when you want to play staccato notes using a sound that has a slow release",
    )
    PORTAMENTO_TIME_INTERVAL_SENS = (
        0x03,
        0,
        127,
        "Shortens the Portamento Time according to the spacing between note-on events. Higher values\nproduce a greater effect. With a setting of 0, there will be no effect.",
    )
    ENVELOPE_LOOP_MODE = (
        0x04,
        0,
        2,
        "Use this to loop the envelope between certain regions during a note-on.\nOFF The envelope will operate normally.\nFREE-RUN When the Decay segment has ended, the envelope will return to the Attack. The Attack through\nDecay segments will repeat until note-off occurs.\nTEMPO-SYNC Specifies the loop rate as a note value (Sync Note parameter).",
    )
    ENVELOPE_LOOP_SYNC_NOTE = (
        0x05,
        0,
        19,
        "Returns to the Attack at the specified rate. If the Attack+Decay time is shorter than the specified\nloop, the sound is maintained at the Sustain Level. If the Attack+Decay time is longer than the\nspecified loop, the sound returns to the Attack even if the Decay has not completed. This will\n\ncontinue repeating until note-off occurs.",
    )
    CHROMATIC_PORTAMENTO = (
        0x06,
        0,
        1,
        "If this is turned ON, portamento will operate in semitone steps. If this is turned OFF, the pitch will\nchange smoothly from one note to the next.\n This is effective when you want to play chromatic portamento\n using a sound that has a\nslow portamento time.",
    )

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.ENVELOPE_LOOP_MODE:
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif self == self.CHROMATIC_PORTAMENTO:
            return ["OFF", "ON"][value]
        elif self == self.ENVELOPE_LOOP_SYNC_NOTE:
            return [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ][value]
        return str(value)

    @staticmethod
    def get_by_name(param_name):
        """Get the Parameter by name."""
        # Return the parameter member by name, or None if not found
        return DigitalModifyParam.__members__.get(param_name, None)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value)}")

        # Validate range for specific parameters
        if self == self.ENVELOPE_LOOP_SYNC_NOTE and not (0 <= value <= 19):
            raise ValueError(
                f"Value {value} out of range for {self.name} (valid range: 0-19)"
            )

        return value

    def get_address_for_partial(self, partial_number: int = 0):
        return AddressOffsetSuperNATURALLMB.MODIFY, 0x00
