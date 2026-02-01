"""
Digital Tone Modify Text classes
"""


class DigitalModifyNames:
    """Digital Modify names"""

    ATTACK_TIME_INTERVAL_SENS: str = "Attack Time Interval Sens"
    RELEASE_TIME_INTERVAL_SENS: str = "Release Time Interval Sens"
    PORTAMENTO_TIME_INTERVAL_SENS: str = "Portamento Time Interval Sens"
    ENVELOPE_LOOP_MODE: str = "Envelope Loop Mode"
    ENVELOPE_LOOP_SYNC_NOTE: str = "Envelope Loop Sync Note"
    CHROMATIC_PORTAMENTO: str = "Chromatic Portamento"


class DigitalModifyOptions:
    """Digital Modify Options"""

    ENVELOPE_LOOP_MODE: list = ["OFF", "FREE-RUN", "TEMPO-SYNC"]
    CHROMATIC_PORTAMENTO: list = ["OFF", "ON"]
