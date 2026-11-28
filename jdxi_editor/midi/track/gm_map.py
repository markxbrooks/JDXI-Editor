"""
The JD-Xi sound closest to a General MIDI instrument.

A file made for a General MIDI instrument chooses each channel's instrument
with a program change (0-127, no JD-Xi bank). On the JD-Xi those numbers
pick a sound of whatever bank the part is in: here each GM instrument has the
JD-Xi preset that comes closest — a Digital tone for Digital 1 and 2, an
Analog tone for the Analog part (it plays one note at a time: basses and
leads), a drum kit for the Drums. Close, not the same: a starting point the
user can change.

Preset numbers are the JD-Xi's, 1-based, as in its preset lists.
"""

from __future__ import annotations

from typing import Optional

import mido

from jdxi_editor.midi.track.instrument import GM_INSTRUMENTS

# Bank Select MSBs that choose JD-Xi sounds: programs, drum kits, analog and digital tones
JDXI_BANK_MSB = frozenset({85, 86, 94, 95})

# GM program (0-127) -> JD-Xi Digital preset (1-256), eight per GM family
GM_TO_DIGITAL: tuple[int, ...] = (
    # Piano: grand ×4, EP 1, EP 2 (FM), harpsichord, clavinet
    162, 162, 163, 162, 164, 165, 168, 169,
    # Chromatic percussion: celesta, glockenspiel, music box, vibraphone, marimba, xylophone, bells, dulcimer
    173, 174, 175, 176, 176, 176, 173, 178,
    # Organ: drawbar, percussive, rock, church, reed, accordion, harmonica, tango accordion
    170, 171, 170, 42, 42, 42, 190, 42,
    # Guitar: nylon, steel, jazz, clean, muted, overdriven, distortion, harmonics
    179, 179, 182, 180, 184, 183, 183, 180,
    # Bass: acoustic, finger, pick, fretless, slap ×2, synth 1, synth 2
    157, 158, 159, 160, 161, 161, 92, 90,
    # Strings: violin, viola, cello, contrabass, tremolo, pizzicato, harp, timpani
    46, 46, 46, 157, 46, 47, 178, 204,
    # Ensemble: strings 1, 2, synth strings 1, 2, choir, voice, synth voice, orchestra hit
    46, 6, 1, 4, 199, 197, 196, 200,
    # Brass: trumpet, trombone, tuba, muted trumpet, horn, section, synth brass 1, 2
    236, 236, 236, 235, 243, 245, 238, 239,
    # Reed: saxes, oboe, english horn, bassoon, clarinet
    190, 190, 190, 190, 190, 190, 190, 190,
    # Pipe: piccolo, flute, recorder, pan flute, bottle, shakuhachi, whistle, ocarina
    79, 79, 79, 190, 190, 190, 79, 80,
    # Synth lead: square, saw, calliope, chiff, charang, voice, fifths, bass + lead
    75, 66, 80, 79, 58, 74, 82, 87,
    # Synth pad: new age, warm, polysynth, choir, bowed, metallic, halo, sweep
    40, 2, 221, 198, 10, 43, 15, 20,
    # Synth FX: rain, soundtrack, crystal, atmosphere, brightness, goblins, echoes, sci-fi
    187, 44, 43, 7, 15, 188, 216, 189,
    # Ethnic: sitar, banjo, shamisen, koto, kalimba, bagpipe, fiddle, shanai
    185, 179, 185, 178, 173, 190, 46, 190,
    # Percussive: tinkle bell, agogo, steel drums, woodblock, taiko, melodic tom, synth drum, reverse cymbal
    174, 177, 177, 177, 204, 204, 204, 192,
    # Sound effects: fret noise, breath, seashore, bird, telephone, helicopter, applause, gunshot
    195, 195, 187, 188, 189, 188, 195, 204,
)
assert len(GM_TO_DIGITAL) == 128

# Synth leads played low are bass lines (a «square lead» in the bass register)
_DIGITAL_LOW_LEAD = {80: 124, 81: 114, 87: 114}  # Square Bs 1, ResoSawSynBs
_ANALOG_LOW_LEAD = {80: 13, 81: 6, 87: 5}  # Sqr Bass 1, Saw Bass 1, Saw+Sub Bs 1
LOW_REGISTER = 52  # average note below E3: a bass line

# GM program -> JD-Xi Analog preset (1-64) where there is one that fits
_GM_TO_ANALOG: dict[int, int] = {
    32: 16, 33: 16, 34: 7, 35: 14, 36: 25, 37: 25, 38: 6, 39: 13, 43: 2,  # basses
    80: 39, 81: 43, 82: 41, 83: 42, 84: 44, 85: 42, 86: 38, 87: 5,  # leads
}
_ANALOG_BRASS, _ANALOG_SOFT, _ANALOG_BASS = 40, 41, 16  # Analog Tp 1, Tri Lead 1, Soft Bass 1

# GM drum kits (program on channel 10) -> JD-Xi drum kit (1-33)
_GM_TO_KIT = {0: 29, 8: 30, 16: 31, 24: 7, 25: 2, 32: 32, 40: 32, 48: 29}  # Pop 1/2, Rock, EDM, TR-808, Jazz
DEFAULT_KIT = 29  # Pop Kit 1: the GM Standard kit


def digital_for_gm(program: int, average_note: Optional[float] = None) -> int:
    """The JD-Xi Digital preset (1-256) closest to GM *program*."""
    if average_note is not None and average_note < LOW_REGISTER and program in _DIGITAL_LOW_LEAD:
        return _DIGITAL_LOW_LEAD[program]
    return GM_TO_DIGITAL[program]


def analog_for_gm(program: int, average_note: Optional[float] = None) -> int:
    """The JD-Xi Analog preset (1-64) closest to GM *program* (a mono part: basses and leads)."""
    low = average_note is not None and average_note < LOW_REGISTER
    if low and program in _ANALOG_LOW_LEAD:
        return _ANALOG_LOW_LEAD[program]
    if program in _GM_TO_ANALOG:
        return _GM_TO_ANALOG[program]
    if 56 <= program <= 63:
        return _ANALOG_BRASS
    return _ANALOG_BASS if low else _ANALOG_SOFT


def kit_for_gm(program: Optional[int]) -> int:
    """The JD-Xi drum kit (1-33) closest to GM drum kit *program*."""
    if program is None:
        return DEFAULT_KIT
    if program in _GM_TO_KIT:
        return _GM_TO_KIT[program]
    return _GM_TO_KIT.get(program - program % 8, DEFAULT_KIT)  # a variation of a kit


def note_channel(track: mido.MidiTrack) -> Optional[int]:
    """The channel (0-based) of the track's first note."""
    for msg in track:
        if msg.type == "note_on":
            return msg.channel
    return None


def gm_program(track: mido.MidiTrack) -> Optional[int]:
    """
    The General MIDI program the track's notes start with: the first program
    change on their channel, unless a JD-Xi Bank Select comes with it (then
    it is a JD-Xi sound already).
    """
    channel = note_channel(track)
    msb: dict[int, int] = {}
    for msg in track:
        if msg.type == "control_change" and msg.control == 0:
            msb[msg.channel] = msg.value
        elif msg.type == "program_change" and (channel is None or msg.channel == channel):
            return None if msb.get(msg.channel) in JDXI_BANK_MSB else msg.program
    return None


def average_note(track: mido.MidiTrack) -> Optional[float]:
    notes = [msg.note for msg in track if msg.type == "note_on" and msg.velocity > 0]
    return sum(notes) / len(notes) if notes else None


def gm_name(program: int) -> str:
    return GM_INSTRUMENTS[program]


def preset_for_part(channel: int, track: mido.MidiTrack) -> Optional[int]:
    """
    The JD-Xi preset (1-based, of the part's own list) for *track* played by
    the part on *channel* (1, 2, 3, 10); None: the file chooses no GM sound.
    """
    program = gm_program(track)
    if program is None:
        return None
    drums = note_channel(track) == 9  # GM drums: the program is a kit
    if channel == 10:
        return kit_for_gm(program) if drums else None
    if drums:
        return None
    if channel == 3:
        return analog_for_gm(program, average_note(track))
    return digital_for_gm(program, average_note(track))


def strip_program_changes(track: mido.MidiTrack, channel: int) -> mido.MidiTrack:
    """*track* without its program changes and bank selects on *channel* (0-based), timing kept."""
    out = mido.MidiTrack()
    carry = 0
    for msg in track:
        drop = (getattr(msg, "channel", None) == channel and (
            msg.type == "program_change"
            or (msg.type == "control_change" and msg.control in (0, 32))))
        if drop:
            carry += msg.time
            continue
        out.append(msg.copy(time=msg.time + carry))
        carry = 0
    return out


def with_sound(track: mido.MidiTrack, channel: int, msb: int, lsb: int, program: int) -> mido.MidiTrack:
    """*track* starting with Bank Select + Program Change (0-based channel and program)."""
    head = [
        mido.Message("control_change", channel=channel, control=0, value=msb, time=0),
        mido.Message("control_change", channel=channel, control=32, value=lsb, time=0),
        mido.Message("program_change", channel=channel, program=program, time=0),
    ]
    # after the meta messages at tick 0 (name, tempo), before the first event
    out = mido.MidiTrack()
    inserted = False
    for msg in track:
        if not inserted and (not msg.is_meta or msg.time > 0):
            out.extend(head)
            inserted = True
        out.append(msg)
    if not inserted:
        out.extend(head)
    return out
