"""
Instrument Display Config
"""

from dataclasses import dataclass


@dataclass
class InstrumentDisplayConfig:
    """
    Instrument Display Config
    """

    instrument_icon_folder: str
    instrument_default_image: str
    window_title: str
    display_prefix: str
