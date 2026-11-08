"""
The parameter tables agree with the JD-Xi MIDI implementation's structure.

For every section a patch is made of (Program, Vocal FX, Effects, Zones,
Arpeggio, Digital, Analog, Drum):

- no two parameters partly overlap; the same offset twice is only allowed in
  the Effects tables, where one slot has a name per effect type
- raw ranges are MIDI values (0-127, 0-65535 for 4-nibble parameters), not
  the display units shown to the user
- the display range spans as many steps as the raw range (except the
  keyfollow parameters, which are shown in steps of 10, and name characters)

Plus round trips for parameters whose tables were wrong.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import pytest

from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.data.parameter.effects.effects import (
    DelayParam,
    Effect1Param,
    Effect2Param,
    ReverbParam,
)
from jdxi_editor.midi.data.parameter.vocal_fx import VocalFXParam
from jdxi_editor.midi.sysex.patch_values import param_class_for_address

SECTION_ADDRESSES = [
    "18000000",  # Program Common
    "18000100",  # Vocal FX
    "18000200",  # Effect 1
    "18000400",  # Effect 2
    "18000600",  # Delay
    "18000800",  # Reverb
    "18003000",  # Program Zone
    "18004000",  # Arpeggio
    "19010000",  # Digital Common
    "19012000",  # Digital Partial
    "19015000",  # Digital Modify
    "19420000",  # Analog
    "19700000",  # Drum Common
    "19702e00",  # Drum Partial
]
TABLES = {cls.__name__: cls for cls in map(param_class_for_address, SECTION_ADDRESSES)}
# One slot, a name per effect type (EFX1_PARAM_1 = ..._FUZZ_LEVEL = ...)
ALIASED_TABLES = {Effect1Param, Effect2Param, DelayParam, ReverbParam}
# Shown as -100..+100 in steps of 10 (raw 54-74)
SCALED_BY_10 = {"FILTER_CUTOFF_KEYFOLLOW", "AMP_LEVEL_KEYFOLLOW"}


def _size(param) -> int:
    return param.get_nibbled_size() if hasattr(param, "get_nibbled_size") else 1


@pytest.mark.parametrize("name", sorted(TABLES))
def test_no_partial_overlaps(name):
    cls = TABLES[name]
    spans = [(int(p.address), _size(p), p.name) for p in cls]
    problems = []
    for i, (start, size, first) in enumerate(spans):
        for other_start, other_size, second in spans[i + 1 :]:
            if not (start < other_start + other_size and other_start < start + size):
                continue
            if (start, size) == (other_start, other_size) and cls in ALIASED_TABLES:
                continue
            problems.append(f"{first} 0x{start:02X}+{size} / {second} 0x{other_start:02X}+{other_size}")
    assert problems == []


@pytest.mark.parametrize("name", sorted(TABLES))
def test_raw_ranges_are_midi_values(name):
    problems = []
    for p in TABLES[name]:
        limit = 127 if _size(p) == 1 else 0xFFFF
        if not 0 <= p.min_val <= p.max_val <= limit:
            problems.append(f"{p.name}: {p.min_val}..{p.max_val}")
    assert problems == []


@pytest.mark.parametrize("name", sorted(TABLES))
def test_display_range_matches_raw_range(name):
    problems = []
    for p in TABLES[name]:
        lo, hi = getattr(p, "display_min", None), getattr(p, "display_max", None)
        if lo is None and hi is None:
            continue
        if not (isinstance(lo, int) and isinstance(hi, int)):
            problems.append(f"{p.name}: display range {lo!r}..{hi!r}")
            continue
        if _size(p) != 1 or "NAME_" in p.name:
            continue
        step = 10 if p.name in SCALED_BY_10 else 1
        if hi - lo != (p.max_val - p.min_val) * step:
            problems.append(f"{p.name}: raw {p.min_val}..{p.max_val} display {lo}..{hi}")
    assert problems == []


@pytest.mark.parametrize(
    "param, display, raw",
    [
        (DigitalPartialParam.OSC_PITCH_COARSE, -24, 40),
        (DigitalPartialParam.OSC_PITCH_COARSE, 0, 64),
        (DigitalPartialParam.OSC_PITCH_FINE, -50, 14),
        (DigitalPartialParam.OSC_PITCH_FINE, 50, 114),
        (DigitalPartialParam.AMP_VELOCITY, -63, 1),
        (DigitalPartialParam.OSC_PITCH_ENV_DEPTH, 63, 127),
        (VocalFXParam.PAN, -64, 0),
        (VocalFXParam.AUTO_PITCH_GENDER, 10, 20),
        (VocalFXParam.AUTO_PITCH_OCTAVE, -1, 0),
    ],
)
def test_bipolar_round_trip(param, display, raw):
    assert param.convert_to_midi(display) == raw
    assert param.convert_from_midi(raw) == display


def test_moved_parameters_use_roland_offsets():
    assert int(DigitalPartialParam.AMP_LEVEL_KEYFOLLOW.address) == 0x3C
    assert int(DigitalPartialParam.LFO_SHAPE.address) == 0x1C
    assert int(DrumPartialParam.TVF_ENV_VELOCITY_SENS.address) == 0x12A
    assert int(DrumPartialParam.TVA_LEVEL_VELOCITY_SENS.address) == 0x137
