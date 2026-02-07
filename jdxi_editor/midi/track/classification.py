"""
Track classification utilities for MIDI files.

This module provides functions to classify MIDI tracks into categories:
- Bass: Low-pitched, monophonic or low polyphony tracks
- Keys/Guitars: Wide range, polyphonic tracks (piano, guitar, etc.)
- Strings: Sustained, legato tracks with ensemble-like patterns
"""

from typing import List, Optional

from mido import MidiFile, MidiTrack

from jdxi_editor.midi.track.analyzer import TrackAnalyzer
from jdxi_editor.midi.track.data import BASS_NOTE_MAX, BASS_KEYWORDS, KEYS_KEYWORDS, GUITAR_KEYWORDS, STRINGS_KEYWORDS
from jdxi_editor.midi.track.rule import STRINGS_RULES, KEYS_RULES, BASS_RULES


from dataclasses import dataclass
from typing import Callable

from jdxi_editor.midi.track.stats import TrackStats


def name_contains(keywords):
    def _check(s: TrackStats):
        if not s.track_name:
            return False
        name = s.track_name.lower()
        return any(k in name for k in keywords)
    return _check


def percentage(part, whole):
    return (part / whole * 100) if whole else 0


def bass_percentage_gt(p):
    return lambda s: percentage(s.bass_note_count, s.note_count) > p


def max_polyphony_le(n):
    return lambda s: s.max_simultaneous <= n


def avg_duration_gt(ticks):
    return lambda s: s.avg_note_duration > ticks


def note_range_ge(n):
    return lambda s: s.note_range >= n


def has_pitch_bend(s: TrackStats):
    return s.has_pitch_bend


def max_polyphony_ge(n):
    return lambda s: s.max_simultaneous >= n


def note_count_gt(n):
    return lambda s: s.note_count > n


def note_count_between(lo, hi):
    return lambda s: lo <= s.note_count <= hi


def legato_score_gt(x):
    return lambda s: s.legato_score > x


def velocity_range_gt(r):
    return lambda s: (max(s.velocities) - min(s.velocities)) > r if s.velocities else False


def mid_percentage_between(lo, hi):
    return lambda s: (
        s.note_count > 0
        and lo <= (s.mid_range_note_count / s.note_count * 100) <= hi
    )


def velocity_std_lt(threshold):
    def _check(s: TrackStats):
        if not s.velocities:
            return False
        return _calculate_std_dev(s.velocities) < threshold
    return _check


def analyze_track_for_classification(track: MidiTrack, track_index: int) -> "TrackStats":
    return TrackAnalyzer(track, track_index).run()


def score_rules(stats: TrackStats, rules: list[ScoreRule]) -> float:
    total = 0.0
    for rule in rules:
        total += rule.evaluate(stats)
    return total


def calculate_scores(stats: TrackStats) -> None:
    stats.scores["bass"] = score_rules(stats, BASS_RULES)
    stats.scores["keys_guitars"] = score_rules(stats, KEYS_RULES)
    stats.scores["strings"] = score_rules(stats, STRINGS_RULES)


def explain_score(stats: TrackStats, rules: list[ScoreRule]):
    return [
        (rule.name, rule.weight)
        for rule in rules
        if rule.condition(stats)
    ]


def _calculate_std_dev(values: List[float]) -> float:
    """Calculate standard deviation of a list of values."""
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance**0.5


def classify_tracks(
    midi_file: MidiFile,
    exclude_drum_tracks: Optional[List[int]] = None,
    min_score: float = 30.0,
) -> dict:
    """
    Classify tracks in a MIDI file into Bass, Keys/Guitars, and Strings.

    Args:
        midi_file: The MIDI file to analyze
        exclude_drum_tracks: List of track indices to exclude from classification
        min_score: Minimum score threshold for a track to be classified

    Returns:
        Dictionary with keys:
        - "bass": List of (track_index, "TrackStats") tuples
        - "keys_guitars": List of (track_index, TrackStats) tuples
        - "strings": List of (track_index, TrackStats) tuples
        - "unclassified": List of (track_index, TrackStats) tuples
    """
    exclude_drum_tracks = exclude_drum_tracks or []

    # --- Analyze all tracks
    track_analyses = []
    for i, track in enumerate(midi_file.tracks):
        if i in exclude_drum_tracks:
            continue
        analysis = analyze_track_for_classification(track, i)
        track_analyses.append(analysis)

    # --- Classify each track
    classifications = {
        "bass": [],
        "keys_guitars": [],
        "strings": [],
        "unclassified": [],
    }

    for analysis in track_analyses:
        scores = analysis.scores
        max_score = max(scores.values())
        max_category = max(scores.items(), key=lambda x: x[1])[0]

        if max_score >= min_score:
            classifications[max_category].append((analysis.track_index, analysis))
        else:
            classifications["unclassified"].append((analysis.track_index, analysis))

    # --- Sort each category by score (descending)
    for category in classifications:
        if category == "unclassified":
            # --- Sort unclassified by their best score
            classifications[category].sort(
                key=lambda x: max(x[1].scores.values()), reverse=True
            )
        else:
            classifications[category].sort(
                key=lambda x: x[1].scores[category], reverse=True
            )

    return classifications
