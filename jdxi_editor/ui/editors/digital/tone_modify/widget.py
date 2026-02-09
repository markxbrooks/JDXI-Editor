from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass
class DigitalToneModifyWidgets:
    """Digital Tone Modify"""

    interval_sens: list[QWidget] = None
    envelope_loop_mode: list[QWidget] = None
    envelope_loop_sync_note: list[QWidget] = None
    chromatic_portamento: list[QWidget] = None
