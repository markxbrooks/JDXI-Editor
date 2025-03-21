"""
Module: preset_data

This module defines the `PresetData` dataclass, which represents the structure of a JD-Xi preset.
It includes attributes for preset type, current selection, modification status, and MIDI channel.

Classes:
    - PresetData: Stores preset metadata for MIDI program selection and management.

Constants:
    - MIDI_CHANNEL_DIGITAL1: Default MIDI channel for Digital 1 presets.
    - PresetType.DIGITAL_1: Default preset type for Digital 1.
"""

from dataclasses import dataclass
from typing import Optional

from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DIGITAL1
from jdxi_editor.midi.preset.type import ToneType


@dataclass
class Preset:
    number: int = None
    name: str = None,
    preset_type: str = ToneType.DIGITAL_1
    channel: Optional[int] = MIDI_CHANNEL_DIGITAL1
