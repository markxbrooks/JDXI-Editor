from dataclasses import dataclass


@dataclass
class InstrumentDisplayConfig:
    instrument_icon_folder: str
    instrument_default_image: str
    window_title: str
    display_prefix: str
