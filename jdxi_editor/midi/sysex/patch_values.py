"""
jdxi_editor.midi.sysex.patch_values
Patch sections in raw MIDI values, the form the JD-Xi itself sends.

Saved sections carry ``VALUE_FORMAT: "midi"``. A section taken from the
synth's memory also carries ``SYSEX``, the section as one DT1 message, so it
can be restored byte for byte.

Bundles saved before this were written from the editor controls, in their
display units (ms, 0.0-1.0 fractions, signed ±63, ...), but read back as raw
values, so every load and save moved them. ``display_to_midi`` converts one of
those values the way the control showed it, and ``upgrade_legacy_section``
converts a whole old section.

Example:
    >>> from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam as P
    >>> display_to_midi(P.AMP_PAN, -35)          # signed display value
    29
    >>> display_to_midi(P.AMP_ENV_ATTACK_TIME, 290.0)   # ms (10-1000)
    36
    >>> display_to_midi(P.AMP_ENV_SUSTAIN_LEVEL, 0.39)  # fraction
    50
"""

from __future__ import annotations

from typing import Any, Optional

from picomidi.utils.conversion import fraction_to_midi_value, ms_to_midi_value

from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParam
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.modify import DigitalModifyParam
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.data.parameter.program.zone import ProgramZoneParam
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParam
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter

VALUE_FORMAT = "VALUE_FORMAT"
VALUE_FORMAT_MIDI = "midi"
SYSEX = "SYSEX"

# Section keys that are not parameters
METADATA_KEYS = frozenset(
    {
        SysExSection.JD_XI_HEADER,
        SysExSection.ADDRESS,
        SysExSection.TEMPORARY_AREA,
        SysExSection.SYNTH_TONE,
        SysExSection.TONE_NAME,
        VALUE_FORMAT,
        SYSEX,
        "parameter_block",
        "block_name",
    }
)

_TIMES = (
    EnvelopeParameter.ATTACK_TIME,
    EnvelopeParameter.DECAY_TIME,
    EnvelopeParameter.RELEASE_TIME,
)
_LEVELS = (EnvelopeParameter.SUSTAIN_LEVEL,)


def param_class_for_address(address: str):
    """Parameter class of the section at a 4-byte address ("19012000"), or None."""
    address = address.lower()
    area, umb, lmb = address[:2], address[2:4], address[4:6]
    if area == "18" and umb == "00":
        return {
            "00": ProgramCommonParam,
            "01": VocalFXParam,
            "02": Effect1Param,
            "04": Effect2Param,
            "06": DelayParam,
            "08": ReverbParam,
            "30": ProgramZoneParam,
            "31": ProgramZoneParam,
            "32": ProgramZoneParam,
            "33": ProgramZoneParam,
            "40": ArpeggioParam,
        }.get(lmb)
    if area == "19":
        if umb in ("01", "21"):
            if lmb == "00":
                return DigitalCommonParam
            if lmb in ("20", "21", "22"):
                return DigitalPartialParam
            if lmb == "50":
                return DigitalModifyParam
        if umb == "42" and lmb == "00":
            return AnalogParam
        if umb == "70":
            return DrumCommonParam if lmb == "00" else DrumPartialParam
    return None


def _envelope_type(param) -> Optional[str]:
    getter = getattr(param, "get_envelope_param_type", None)
    if not callable(getter):
        return None
    try:
        return getter()
    except NotImplementedError:
        return None


def display_to_midi(param, value: Any) -> int:
    """
    Raw MIDI value of *param* from the value its editor control shows.

    Envelope times are in ms (10-5000 for the pitch envelope, 10-1000
    otherwise), sustain levels are 0.0-1.0, everything else is in the
    parameter's display range, which the parameter converts itself.
    """
    if isinstance(value, bool):
        value = int(value)
    env_type = _envelope_type(param)
    if env_type in _TIMES:
        max_time = 5000 if param.name.startswith("OSC_PITCH_ENV") else 1000
        return ms_to_midi_value(float(value), 10, max_time)
    if env_type in _LEVELS and isinstance(value, float) and value <= 1.0:
        return fraction_to_midi_value(value)
    number = int(round(float(value)))
    min_val = getattr(param, "min_val", 0) or 0
    if (
        0 < min_val
        and getattr(param, "display_min", None) == min_val  # no display offset
        and number < min_val
        and number + min_val <= param.max_val
    ):
        # A combo box reports its index; the range starts above 0 (Octave
        # Shift is 61-67, shown as -3..+3 at index 0..6)
        number += min_val
    convert = getattr(param, "convert_to_midi", None)
    return int(convert(number)) if callable(convert) else number


def section_values_to_midi(section: dict, param_class=None) -> dict:
    """Copy of *section* with its parameter values converted by display_to_midi."""
    if param_class is None:
        param_class = param_class_for_address(str(section.get(SysExSection.ADDRESS, "")))
    converted = dict(section)
    for name, value in section.items():
        if name in METADATA_KEYS or name.startswith("TONE_NAME_"):
            continue
        if not isinstance(value, (int, float)):
            continue
        param = param_class.get_by_name(name) if param_class is not None else None
        if param is None:
            continue
        try:
            converted[name] = display_to_midi(param, value)
        except (TypeError, ValueError):
            continue
    converted[VALUE_FORMAT] = VALUE_FORMAT_MIDI
    return converted


def is_midi_section(section: dict) -> bool:
    return section.get(VALUE_FORMAT) == VALUE_FORMAT_MIDI or SYSEX in section


def upgrade_legacy_section(section: dict) -> dict:
    """A section from an old bundle (display values) in raw MIDI values."""
    if is_midi_section(section):
        return section
    return section_values_to_midi(section)
