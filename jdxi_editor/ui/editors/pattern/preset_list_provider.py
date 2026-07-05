"""
Preset list provider for Digital, Analog, and Drums rows.

When "Use SoundFont List" is enabled in MIDI configuration and a valid
SoundFont path is configured, preset names for Digital, Analog, and Drums
instrument editors are loaded from the SoundFont (.sf2) file. Otherwise
built-in JD-Xi presets are used.
"""

import os
from typing import Any, Dict, List, Optional, Union

from PySide6.QtCore import QObject, QSettings, Signal

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.project import __organization_name__, __program__
from jdxi_editor.ui.editors.pattern.options import DIGITAL_OPTIONS, DRUM_OPTIONS


class PresetListSignals(QObject):
    """Singleton signal emitter for preset list changes."""
    
    soundfont_list_changed = Signal()
    
    _instance = None
    
    @classmethod
    def instance(cls) -> "PresetListSignals":
        if cls._instance is None:
            cls._instance = PresetListSignals()
        return cls._instance


def get_preset_signals() -> PresetListSignals:
    """Get the singleton signal emitter for preset list changes."""
    return PresetListSignals.instance()

# QSettings keys for MIDI config preferences
USE_SOUNDFONT_LIST_KEY = "midi_config/use_soundfont_list"
SF2_PATH_KEY = "midi_config/sf2_path"
HARDWARE_INTERFACE_KEY = "midi_config/hardware_interface"

# GM percussion key map (key 36–59): MIDI note -> display name
GM_DRUM_NAMES: List[str] = [
    "Bass Drum 1",  # 36
    "Side Stick",  # 37
    "Acoustic Snare",  # 38
    "Hand Clap",  # 39
    "Electric Snare",  # 40
    "Low Floor Tom",  # 41
    "Closed Hi-Hat",  # 42
    "High Floor Tom",  # 43
    "Pedal Hi-Hat",  # 44
    "Low Tom",  # 45
    "Open Hi-Hat",  # 46
    "Low-Mid Tom",  # 47
    "Hi-Mid Tom",  # 48
    "Crash Cymbal 1",  # 49
    "High Tom",  # 50
    "Ride Cymbal 1",  # 51
    "Chinese Cymbal",  # 52
    "Ride Bell",  # 53
    "Tambourine",  # 54
    "Splash Cymbal",  # 55
    "Cowbell",  # 56
    "Crash Cymbal 2",  # 57
    "Vibraslap",  # 58
    "Ride Cymbal 2",  # 59
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
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return bool(val)


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
    """Set the Use SoundFont List preference and notify listeners."""
    from decologr import Decologr as log
    settings = QSettings(__organization_name__, __program__)
    settings.setValue(USE_SOUNDFONT_LIST_KEY, enabled)
    settings.sync()
    # Notify any connected widgets to refresh their preset lists
    log.info(scope="preset_list_provider", message=f"Emitting soundfont_list_changed signal (enabled={enabled})")
    get_preset_signals().soundfont_list_changed.emit()


def set_sf2_path(path: str) -> None:
    """Set the SoundFont path for preset list source and notify listeners."""
    settings = QSettings(__organization_name__, __program__)
    settings.setValue(SF2_PATH_KEY, path)
    settings.sync()
    get_preset_signals().soundfont_list_changed.emit()


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
    from decologr import Decologr as log
    try:
        from sf2utils.sf2parse import Sf2File

        with open(sf2_path, "rb") as f:
            sf2 = Sf2File(f)
            presets = [(p.bank, p.preset, p.name) for p in sf2.presets if p.name != "EOP"]
            log.debug(f"Loaded {len(presets)} presets from {sf2_path}")
            return presets
    except ImportError as e:
        log.warning(f"sf2utils not installed: {e}. Install with: pip install sf2utils")
        return []
    except Exception as e:
        log.error(f"Failed to load SF2 file {sf2_path}: {e}")
        return []


def get_preset_list_for_synth_type(
    synth_type: str,
) -> Union[Dict[int, Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Get the preset list for the instrument preset widget.

    When "Use SoundFont List" is enabled and a valid SF2 path is configured,
    returns presets from the SoundFont for Digital, Analog, and Drums.
    Otherwise returns built-in JD-Xi presets.

    :param synth_type: "Analog", "Digital", or "Drums"
    :return: Preset list in dict format (JD-Xi Digital/Analog) or list format
    """
    from decologr import Decologr as log

    if not _use_soundfont_list():
        log.debug(f"Using JD-Xi preset list for {synth_type}")
        return _get_jdxi_preset_list(synth_type)

    path = _sf2_path()
    if not path or not os.path.isfile(path):
        log.debug(f"SF2 path invalid for {synth_type}, using JD-Xi presets")
        return _get_jdxi_preset_list(synth_type)

    presets = _load_sf2_presets(path)
    if not presets:
        return _get_jdxi_preset_list(synth_type)

    if synth_type == "Drums":
        drum_presets = [(b, p, n) for b, p, n in presets if b == 128]
        if not drum_presets:
            drum_presets = [(b, p, n) for b, p, n in presets if b != 0][:16]
        return [
            {
                "id": f"{i + 1:03d}",
                "name": name,
                "category": "SoundFont",
                "msb": "128",
                "lsb": "0",
                "pc": str(prog + 1),
            }
            for i, (_bank, prog, name) in enumerate(drum_presets)
        ]

    if synth_type in ("Digital", "Analog"):
        melodic = [(b, p, n) for b, p, n in presets if b == 0]
        if not melodic:
            return _get_jdxi_preset_list(synth_type)
        return [
            {
                "id": f"{i + 1:03d}",
                "name": name,
                "category": "SoundFont",
                "msb": "0",
                "lsb": "0",
                "pc": str(prog + 1),
            }
            for i, (_bank, prog, name) in enumerate(melodic)
        ]

    return _get_jdxi_preset_list(synth_type)


def _get_jdxi_preset_list(synth_type: str) -> Union[Dict, List]:
    """Return built-in JD-Xi preset list for the given synth type."""
    if synth_type == "Analog":
        return JDXi.UI.Preset.Analog.PROGRAM_CHANGE
    if synth_type == "Digital":
        return JDXi.UI.Preset.Digital.PROGRAM_CHANGE
    if synth_type == "Drums":
        return JDXi.UI.Preset.Drum.PROGRAM_CHANGE
    return JDXi.UI.Preset.Digital.PROGRAM_CHANGE
