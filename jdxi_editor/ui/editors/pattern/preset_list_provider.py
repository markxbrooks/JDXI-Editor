"""
Preset list provider for Digital, Analog, and Drums rows.

When "Use SoundFont List" is enabled in MIDI configuration, preset names
are loaded from the configured SoundFont (.sf2) file. Otherwise, built-in
JD-Xi options are used.
"""

import os
from typing import Any, Dict, List, Optional, Union

from PySide6.QtCore import QSettings

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.project import __organization_name__, __program__
from jdxi_editor.ui.editors.pattern.options import DIGITAL_OPTIONS, DRUM_OPTIONS

# QSettings keys for MIDI config preferences
USE_SOUNDFONT_LIST_KEY = "midi_config/use_soundfont_list"
SF2_PATH_KEY = "midi_config/sf2_path"
HARDWARE_INTERFACE_KEY = "midi_config/hardware_interface"

# GM percussion key map (key 36–59): MIDI note -> display name
GM_DRUM_NAMES: List[str] = [
    "Bass Drum 1",      # 36
    "Side Stick",       # 37
    "Acoustic Snare",   # 38
    "Hand Clap",        # 39
    "Electric Snare",   # 40
    "Low Floor Tom",    # 41
    "Closed Hi-Hat",    # 42
    "High Floor Tom",   # 43
    "Pedal Hi-Hat",     # 44
    "Low Tom",          # 45
    "Open Hi-Hat",      # 46
    "Low-Mid Tom",      # 47
    "Hi-Mid Tom",       # 48
    "Crash Cymbal 1",   # 49
    "High Tom",         # 50
    "Ride Cymbal 1",    # 51
    "Chinese Cymbal",   # 52
    "Ride Bell",        # 53
    "Tambourine",       # 54
    "Splash Cymbal",    # 55
    "Cowbell",          # 56
    "Crash Cymbal 2",   # 57
    "Vibraslap",        # 58
    "Ride Cymbal 2",    # 59
]


def get_digital_options() -> List[str]:
    """Options for Digital Synth 1/2 rows. Always use built-in note names (C4, etc.)."""
    return list(DIGITAL_OPTIONS)


def get_analog_options() -> List[str]:
    """Options for Analog Synth row. Always use built-in note names."""
    return list(DIGITAL_OPTIONS)


def get_drum_options() -> List[str]:
    """Options for Drums row. Uses GM percussion names when SoundFont list is on."""
    if not _use_soundfont_list():
        return list(DRUM_OPTIONS)
    path = _sf2_path()
    if not path or not os.path.isfile(path):
        return list(DRUM_OPTIONS)
    return list(GM_DRUM_NAMES)


def _use_soundfont_list() -> bool:
    settings = QSettings(__organization_name__, __program__)
    val = settings.value(USE_SOUNDFONT_LIST_KEY, False)
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes")


def _sf2_path() -> str:
    settings = QSettings(__organization_name__, __program__)
    return str(settings.value(SF2_PATH_KEY, ""))


def get_sf2_path() -> str:
    """Read the saved SoundFont path from settings."""
    return _sf2_path()


def get_use_soundfont_list() -> bool:
    """Read the Use SoundFont List preference."""
    return _use_soundfont_list()


def set_use_soundfont_list(enabled: bool) -> None:
    """Set the Use SoundFont List preference."""
    settings = QSettings(__organization_name__, __program__)
    settings.setValue(USE_SOUNDFONT_LIST_KEY, enabled)
    settings.sync()


def set_sf2_path(path: str) -> None:
    """Set the SoundFont path for preset list source."""
    settings = QSettings(__organization_name__, __program__)
    settings.setValue(SF2_PATH_KEY, path)
    settings.sync()


def get_hardware_interface() -> str:
    """Read the saved hardware audio interface name from settings."""
    settings = QSettings(__organization_name__, __program__)
    return str(settings.value(HARDWARE_INTERFACE_KEY, ""))


def set_hardware_interface(name: str) -> None:
    """Set the hardware audio interface preference for FluidSynth."""
    settings = QSettings(__organization_name__, __program__)
    settings.setValue(HARDWARE_INTERFACE_KEY, name)
    settings.sync()


def _load_sf2_presets(sf2_path: str) -> List[tuple]:
    """Load (bank, preset, name) from .sf2 using sf2utils. Skips EOP."""
    try:
        from sf2utils.sf2parse import Sf2File

        with open(sf2_path, "rb") as f:
            sf2 = Sf2File(f)
            return [
                (p.bank, p.preset, p.name)
                for p in sf2.presets
                if p.name != "EOP"
            ]
    except Exception:
        return []


def get_preset_list_for_synth_type(
    synth_type: str,
) -> Union[Dict[int, Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Get the preset list for the instrument preset widget.

    When "Use SoundFont List" is enabled and SF2 path is valid, returns presets
    from the SoundFont. Otherwise returns built-in JD-Xi presets.

    :param synth_type: "Analog", "Digital", or "Drums"
    :return: Preset list in dict format (Digital) or list format (Analog/Drums)
    """
    if not _use_soundfont_list():
        return _get_jdxi_preset_list(synth_type)

    path = _sf2_path()
    if not path or not os.path.isfile(path):
        return _get_jdxi_preset_list(synth_type)

    presets = _load_sf2_presets(path)
    if not presets:
        return _get_jdxi_preset_list(synth_type)

    if synth_type == "Drums":
        # Bank 128 = GM drum kits
        drum_presets = [
            (b, p, n) for b, p, n in presets
            if b == 128
        ]
        if not drum_presets:
            # Fallback: use bank 0 if no bank 128 (some SF2s put drums elsewhere)
            drum_presets = [(b, p, n) for b, p, n in presets if b != 0][:16]
        # GM bank 128 = drum kits; MSB 128, LSB 0
        return [
            {
                "id": f"{i + 1:03d}",
                "name": name,
                "category": "SoundFont",
                "msb": "128",
                "lsb": "0",
                "pc": str(prog + 1),  # 1-based for MIDI send
            }
            for i, (_bank, prog, name) in enumerate(drum_presets)
        ]

    # Digital and Analog: use bank 0 melodic presets
    melodic = [(b, p, n) for b, p, n in presets if b == 0]
    if not melodic:
        return _get_jdxi_preset_list(synth_type)

    # Return list format (works with get_preset_parameter_value and widget)
    result = [
        {
            "id": f"{i + 1:03d}",
            "name": name,
            "category": "SoundFont",
            "msb": "0",
            "lsb": "0",
            "pc": str(prog + 1),  # 1-based
        }
        for i, (_bank, prog, name) in enumerate(melodic)
    ]

    # Digital widget expects dict; Analog/Drum use list. Return list for both.
    return result


def _get_jdxi_preset_list(synth_type: str) -> Union[Dict, List]:
    """Return built-in JD-Xi preset list for the given synth type."""
    if synth_type == "Analog":
        return JDXi.UI.Preset.Analog.PROGRAM_CHANGE
    if synth_type == "Digital":
        return JDXi.UI.Preset.Digital.PROGRAM_CHANGE
    if synth_type == "Drums":
        return JDXi.UI.Preset.Drum.PROGRAM_CHANGE
    return JDXi.UI.Preset.Digital.PROGRAM_CHANGE
