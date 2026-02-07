"""
Track classification utilities for MIDI files.

This module provides functions to classify MIDI tracks into categories:
- Bass: Low-pitched, monophonic or low polyphony tracks
- Keys/Guitars: Wide range, polyphonic tracks (piano, guitar, etc.)
- Strings: Sustained, legato tracks with ensemble-like patterns
"""

from dataclasses import dataclass, field


@dataclass
class TrackStats:
    """Track Stats"""
    track_index: int
    track_name: str | None = None

    channels: set[int] = field(default_factory=set)

    note_count: int = 0
    notes: list[int] = field(default_factory=list)
    velocities: list[int] = field(default_factory=list)

    lowest_note: int = 127
    highest_note: int = 0

    bass_note_count: int = 0
    mid_range_note_count: int = 0
    high_note_count: int = 0

    note_ons: list[tuple[int,int,int]] = field(default_factory=list)
    note_offs: list[tuple[int,int]] = field(default_factory=list)

    has_pitch_bend: bool = False
    has_control_change: bool = False
    program_changes: list[int] = field(default_factory=list)

    avg_note_duration: float = 0.0
    max_simultaneous: int = 0
    note_range: int = 0
    legato_score: float = 0.0

    scores: dict[str, float] = field(default_factory=lambda: {
        "bass":0.0,
        "keys_guitars":0.0,
        "strings":0.0
    })
