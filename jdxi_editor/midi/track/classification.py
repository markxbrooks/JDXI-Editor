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
# from jdxi_editor.midi.track.stats import TrackStats


def analyze_track_for_classification(track: MidiTrack, track_index: int) -> "TrackStats":
    return TrackAnalyzer(track, track_index).run()


def _calculate_bass_score(analysis: "TrackStats") -> None:
    """Calculate score for Bass classification."""
    score = 0.0

    score = _uprate_is_present_in_name(keywords=BASS_KEYWORDS, additional_score=30, analysis=analysis, score=score)

    score = _uprate_high_percentage_bass_notes(analysis, score)

    score = _uprate_low_note_range(analysis, score)

    score = _uprate_low_polyphony(analysis, score)

    score = _uprate_long_note_duration(analysis, score)

    score = _uprate_pitch_bends(analysis, score)

    analysis.scores["bass"] = score


def _uprate_pitch_bends(analysis: "TrackStats", score: float) -> float:
    # --- Has pitch bend (bass slides) = +5 points
    if analysis.has_pitch_bend:
        score += 5.0
    return score


def _uprate_long_note_duration(analysis: "TrackStats", score: float) -> float:
    # --- Longer note durations (bass sustains) = +10 points
    if analysis.avg_note_duration > 500:
        score += 10.0
    elif analysis.avg_note_duration > 300:
        score += 5.0
    return score


def _uprate_low_polyphony(analysis: "TrackStats", score: float) -> float:
    # --- Low polyphony (bass is often monophonic or 2-3 notes) = +15 points
    if analysis.max_simultaneous <= 2:
        score += 15.0
    elif analysis.max_simultaneous <= 4:
        score += 8.0
    return score


def _uprate_high_percentage_bass_notes(analysis: "TrackStats", score: float) -> float:
    # ---  High percentage of bass notes = +40 points
    if analysis.note_count > 0:
        bass_percentage = (analysis.bass_note_count / analysis.note_count) * 100
        if bass_percentage > 70:
            score += 40.0
        elif bass_percentage > 50:
            score += 25.0
        elif bass_percentage > 30:
            score += 15.0
    return score


def _uprate_low_note_range(analysis: "TrackStats", score: float) -> float:
    # --- Low note range (most notes below C4) = +20 points
    if analysis.highest_note <= BASS_NOTE_MAX:
        score += 20.0
    elif analysis.highest_note <= 72:  # C5
        score += 10.0
    return score


def _calculate_keys_guitars_score(analysis: "TrackStats") -> None:
    """Calculate score for Keys/Guitars classification."""
    score = 0.0

    score = _uprate_is_present_in_name(keywords=KEYS_KEYWORDS + GUITAR_KEYWORDS,
                                       additional_score=30.0,
                                       analysis=analysis,
                                       score=score)

    score = _uprate_wide_note_range(analysis, score)

    score = _uprate_high_polyphony(analysis, score)

    score = _uptate_medium_to_high_note_density(analysis, score)

    score = _uprate_velocity_variations(analysis, score)

    score = _uprate_balanced_note_distribution(analysis, score)

    analysis.scores["keys_guitars"] = score


def _uprate_balanced_note_distribution(analysis, score: float) -> float:
    # --- Balanced note distribution (not just low or high) = +10 points
    if analysis.note_count > 0:
        mid_percentage = (
                                 analysis.mid_range_note_count / analysis.note_count
                         ) * 100
        if 30 <= mid_percentage <= 70:
            score += 10.0
    return score


def _uprate_velocity_variations(analysis, score: float) -> float:
    # --- Velocity variations (dynamic playing) = +10 points
    if analysis.velocities:
        velocity_range = max(analysis.velocities) - min(analysis.velocities)
        if velocity_range > 60:
            score += 10.0
        elif velocity_range > 40:
            score += 5.0
    return score


def _uptate_medium_to_high_note_density(analysis, score: float) -> float:
    # --- Medium to high note density = +15 points
    if analysis.note_count > 200:
        score += 15.0
    elif analysis.note_count > 100:
        score += 10.0
    return score


def _uprate_high_polyphony(analysis, score: float) -> float:
    # --- High polyphony (chords) = +20 points
    if analysis.max_simultaneous >= 5:
        score += 20.0
    elif analysis.max_simultaneous >= 3:
        score += 12.0
    return score


def _uprate_wide_note_range(analysis: "TrackStats", score: float) -> float:
    # --- Wide note range (spans multiple octaves) = +25 points
    if analysis.note_range >= 24:  # 2 octaves
        score += 25.0
    elif analysis.note_range >= 12:  # 1 octave
        score += 15.0
    return score


def _uprate_is_present_in_name(keywords: list,
                               analysis: "TrackStats",
                               score: float,
                               additional_score: float = 30.0) -> float:
    # --- Track name contains keys/guitar keywords = +30 points
    if analysis.track_name:
        name_lower = analysis.track_name.lower()
        if any(keyword in name_lower for keyword in keywords):
            score += additional_score
    return score


def _calculate_strings_score(analysis: "TrackStats") -> None:
    """Calculate score for Strings classification."""
    score = 0.0

    score = _uprate_is_present_in_name(keywords=STRINGS_KEYWORDS,
                                       additional_score=30.0,
                                       analysis=analysis,
                                       score=score)

    score = _uprate_high_legato_score(analysis, score)

    score = _uprate_long_notes(analysis, score)

    score = _uprate_strings_wide_note_range(analysis, score)

    score = _uprate_strings_high_polyphony(analysis, score)

    score = _uprate_smooth_velocities(analysis, score)

    score = _uprate_moderate_note_density(analysis, score)

    analysis.scores["strings"] = score


def _uprate_moderate_note_density(analysis, score: float) -> float:
    # --- Moderate note density (not too sparse, not too dense) = +5 points
    if 50 <= analysis.note_count <= 500:
        score += 5.0
    return score


def _uprate_smooth_velocities(analysis, score: float) -> float:
    # --- Smooth velocity (ensemble dynamics) = +10 points
    if analysis.velocities:
        velocity_std = _calculate_std_dev(analysis.velocities)
        if velocity_std < 20:  # Low variation suggests ensemble
            score += 10.0
    return score


def _uprate_strings_high_polyphony(analysis, score: float) -> float:
    # --- High polyphony (ensemble playing) = +15 points
    if analysis.max_simultaneous >= 4:
        score += 15.0
    elif analysis.max_simultaneous >= 2:
        score += 8.0
    return score


def _uprate_strings_wide_note_range(analysis, score: float) -> float:
    # --- Wide note range (ensemble spans wide range) = +15 points
    if analysis.note_range >= 24:
        score += 15.0
    elif analysis.note_range >= 12:
        score += 8.0
    return score


def _uprate_long_notes(analysis, score: float) -> float:
    # --- Long note durations (sustained notes) = +20 points
    if analysis.avg_note_duration > 800:
        score += 20.0
    elif analysis.avg_note_duration > 500:
        score += 12.0
    return score


def _uprate_high_legato_score(analysis, score: float) -> float:
    # --- High legato score (overlapping notes) = +25 points
    if analysis.legato_score > 0.5:
        score += 25.0
    elif analysis.legato_score > 0.3:
        score += 15.0
    return score


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
