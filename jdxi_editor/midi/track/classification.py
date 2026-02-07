"""
Track classification utilities for MIDI files.

This module provides functions to classify MIDI tracks into categories:
- Bass: Low-pitched, monophonic or low polyphony tracks
- Keys/Guitars: Wide range, polyphonic tracks (piano, guitar, etc.)
- Strings: Sustained, legato tracks with ensemble-like patterns
"""

from dataclasses import dataclass
from typing import Callable, List, Optional

from mido import MidiFile, MidiTrack

from jdxi_editor.midi.track.analyzer import TrackAnalyzer
from jdxi_editor.midi.track.data import (
    BASS_NOTE_MAX,
    BASS_KEYWORDS,
    KEYS_KEYWORDS,
    GUITAR_KEYWORDS,
    STRINGS_KEYWORDS,
)
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


@dataclass(frozen=True)
class ScoreRule:
    name: str
    weight: float
    condition: Callable[["TrackStats"], bool]

    def evaluate(self, stats: "TrackStats") -> float:
        return self.weight if self.condition(stats) else 0.0


# --- Bass: from _calculate_bass_score / _uprate_*
BASS_RULES = [
    ScoreRule("name", 30, name_contains(BASS_KEYWORDS)),
    ScoreRule("mostly_low_notes", 40, bass_percentage_gt(70)),
    ScoreRule("medium_low_notes", 25, bass_percentage_gt(50)),
    ScoreRule("some_low_notes", 15, bass_percentage_gt(30)),
    ScoreRule("very_low_range", 20, lambda s: s.highest_note <= BASS_NOTE_MAX),
    ScoreRule("medium_low_range", 10, lambda s: BASS_NOTE_MAX < s.highest_note <= 72),
    ScoreRule("low_polyphony", 15, max_polyphony_le(2)),
    ScoreRule("medium_polyphony", 8, max_polyphony_le(4)),
    ScoreRule("long_notes", 10, avg_duration_gt(500)),
    ScoreRule("medium_notes", 5, lambda s: 300 < s.avg_note_duration <= 500),
    ScoreRule("slides", 5, has_pitch_bend),
]

# --- Keys/Guitars: from _calculate_keys_guitars_score / _uprate_*
KEYS_RULES = [
    ScoreRule("name", 30, name_contains(KEYS_KEYWORDS + GUITAR_KEYWORDS)),
    ScoreRule("wide_range_2oct", 25, note_range_ge(24)),
    ScoreRule("wide_range_1oct", 15, lambda s: 12 <= s.note_range < 24),
    ScoreRule("high_polyphony", 20, max_polyphony_ge(5)),
    ScoreRule("medium_polyphony", 12, lambda s: 3 <= s.max_simultaneous < 5),
    ScoreRule("high_note_density", 15, note_count_gt(200)),
    ScoreRule("medium_note_density", 10, lambda s: 100 < s.note_count <= 200),
    ScoreRule("velocity_range_high", 10, velocity_range_gt(60)),
    ScoreRule("velocity_range_medium", 5, lambda s: s.velocities and 40 < (max(s.velocities) - min(s.velocities)) <= 60),
    ScoreRule("balanced_mid_notes", 10, mid_percentage_between(30, 70)),
]

# --- Strings: from _calculate_strings_score / _uprate_*
STRINGS_RULES = [
    ScoreRule("name", 30, name_contains(STRINGS_KEYWORDS)),
    ScoreRule("high_legato", 25, legato_score_gt(0.5)),
    ScoreRule("medium_legato", 15, lambda s: 0.3 < s.legato_score <= 0.5),
    ScoreRule("long_notes", 20, avg_duration_gt(800)),
    ScoreRule("medium_long_notes", 12, lambda s: 500 < s.avg_note_duration <= 800),
    ScoreRule("wide_range_2oct", 15, note_range_ge(24)),
    ScoreRule("wide_range_1oct", 8, lambda s: 12 <= s.note_range < 24),
    ScoreRule("high_polyphony", 15, max_polyphony_ge(4)),
    ScoreRule("medium_polyphony", 8, lambda s: 2 <= s.max_simultaneous < 4),
    ScoreRule("smooth_velocities", 10, velocity_std_lt(20)),
    ScoreRule("moderate_density", 5, note_count_between(50, 500)),
]


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
