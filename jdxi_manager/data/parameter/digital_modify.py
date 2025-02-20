from enum import Enum
from typing import Optional, Tuple

from jdxi_manager.data.parameter.synth import SynthParameter

"""
For reference:
**SuperNATURAL Synth Tone Modify
+------------------------------------------------------------------------------+
| Offset | |
| Address | Description |
|-------------+----------------------------------------------------------------|
| 00 00 | 0aaa aaaa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
| 00 01 | 0aaa aaaa | Attack Time Interval Sens (0 - 127) |
| 00 02 | 0aaa aaaa | Release Time Interval Sens (0 - 127) |
| 00 03 | 0aaa aaaa | Portamento Time Interval Sens (0 - 127) |
| 00 04 | 0000 00aa | Envelope Loop Mode (0 - 2) |
| | | OFF, FREE-RUN, TEMPO-SYNC |
| 00 05 | 000a aaaa | Envelope Loop Sync Note (0 - 19) |
| | | 16, 12, 8, 4, 2, 1, 3/4, 2/3, 1/2, |
| | | 3/8, 1/3, 1/4, 3/16, 1/6, 1/8, 3/32, |
| | | 1/12, 1/16, 1/24, 1/32 |
| 00 06 | 0000 000a | Chromatic Portamento (0 - 1) |
| | | OFF, ON |
| 00 07 | 0aaa aaaa | (reserve) <*> |
| 00 08 | 0aaa aaaa | (reserve) <*> |
| : | | |
| 00 24 | 0aaa aaaa | (reserve) <*> |
|-------------+----------------------------------------------------------------|
| 00 00 00 25 | Total Size |
"""


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
            raise ValueError(f"Value must be integer, got {type(value)}")
        
        if self == self.ENVELOPE_LOOP_SYNC_NOTE:
            if value < 0 or value > 19:
                raise ValueError(f"Value {value} out of range for {self.name} (valid range: 0-19)")
        return value        

