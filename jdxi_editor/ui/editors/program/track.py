"""Mixer Track"""

from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QLabel


class MixerTrackEntity:
    """Actual Mixer Tracks"""
    MASTER: str = "MASTER"
    DIGITAL1: str = "DIGITAL1"
    DIGITAL2: str = "DIGITAL2"
    DRUMS: str = "DRUMS"
    ANALOG: str = "ANALOG"


@dataclass
class MixerTrack:
    """Mixer Track"""
    name: str
    slider: QWidget
    value_label: QLabel
    icon: QLabel
