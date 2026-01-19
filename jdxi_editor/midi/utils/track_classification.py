"""
Track classification utilities for MIDI files.

This module provides functions to classify MIDI tracks into categories:
- Bass: Low-pitched, monophonic or low polyphony tracks
- Keys/Guitars: Wide range, polyphonic tracks (piano, guitar, etc.)
- Strings: Sustained, legato tracks with ensemble-like patterns
"""

from collections import defaultdict
from typing import List, Optional

import mido
from mido import MidiFile, MidiTrack

# Note range definitions (MIDI note numbers)
BASS_NOTE_MAX = 60  # C4 - typical upper limit for bass
BASS_NOTE_MIN = 24  # C1 - typical lower limit for bass

KEYS_GUITARS_NOTE_MIN = 36  # C2
KEYS_GUITARS_NOTE_MAX = 96  # C7

# Keywords that suggest instrument types
BASS_KEYWORDS = ["bass", "bassist", "bassline", "low", "sub"]
KEYS_KEYWORDS = ["piano", "keyboard", "keys", "pianist", "organ", "synth"]
GUITAR_KEYWORDS = ["guitar", "guitarist", "acoustic", "electric", "strum"]
STRINGS_KEYWORDS = [
    "string",
    "violin",
    "viola",
    "cello",
    "viola",
    "orchestra",
    "ensemble",
    "symphony",
]


def analyze_track_for_classification(track: MidiTrack, track_index: int) -> dict:
    """
    Analyze a MIDI track to determine its classification.

    Returns a dictionary with analysis results and scores for each category.
    """
    analysis = {
        "track_index": track_index,
        "track_name": None,
        "channels": set(),
        "note_count": 0,
        "note_ons": [],
        "note_offs": [],
        "notes": [],  # All note numbers
        "velocities": [],
        "avg_note_duration": 0.0,
        "max_simultaneous": 0,
        "note_range": 0,  # Highest note - lowest note
        "lowest_note": 127,
        "highest_note": 0,
        "bass_note_count": 0,
        "mid_range_note_count": 0,
        "high_note_count": 0,
        "has_pitch_bend": False,
        "has_control_change": False,
        "program_changes": [],
        "legato_score": 0.0,  # Measure of note overlap (strings indicator)
        "scores": {
            "bass": 0.0,
            "keys_guitars": 0.0,
            "strings": 0.0,
        },
    }

    # Extract track name from meta messages
    for msg in track:
        if msg.is_meta and msg.type == "track_name":
            analysis["track_name"] = msg.name
            break

    # Analyze messages
    active_notes = defaultdict(int)  # Track active notes at each tick
    absolute_time = 0
    note_on_times = {}  # Track when notes start for legato calculation
    durations = []

    for msg in track:
        absolute_time += msg.time

        if msg.is_meta:
            continue

        if hasattr(msg, "channel"):
            analysis["channels"].add(msg.channel)

        if msg.type == "note_on" and msg.velocity > 0:
            analysis["note_count"] += 1
            note = msg.note
            analysis["notes"].append(note)
            analysis["velocities"].append(msg.velocity)
            analysis["note_ons"].append((absolute_time, note, msg.channel))

            # Track note range
            analysis["lowest_note"] = min(analysis["lowest_note"], note)
            analysis["highest_note"] = max(analysis["highest_note"], note)

            # Categorize notes by range
            if note <= BASS_NOTE_MAX:
                analysis["bass_note_count"] += 1
            elif note <= 72:  # C5
                analysis["mid_range_note_count"] += 1
            else:
                analysis["high_note_count"] += 1

            # Track simultaneous notes
            active_notes[absolute_time] += 1
            analysis["max_simultaneous"] = max(
                analysis["max_simultaneous"], active_notes[absolute_time]
            )

            # Track note start times for legato calculation
            note_on_times[note] = absolute_time

        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            note = msg.note if msg.type == "note_off" else msg.note
            analysis["note_offs"].append((absolute_time, note))

            # Calculate note duration for legato (overlap detection)
            if note in note_on_times:
                duration = absolute_time - note_on_times[note]
                durations.append(duration)

                # Check for legato (overlapping notes)
                # If another note starts before this one ends, it's legato
                for other_note, other_start in note_on_times.items():
                    if (
                        other_note != note
                        and other_start > note_on_times[note]
                        and other_start < absolute_time
                    ):
                        analysis["legato_score"] += 1.0

                del note_on_times[note]

        elif msg.type == "pitchwheel":
            analysis["has_pitch_bend"] = True

        elif msg.type == "control_change":
            analysis["has_control_change"] = True

        elif msg.type == "program_change":
            analysis["program_changes"].append(msg.program)

    # Calculate average note duration
    if durations:
        analysis["avg_note_duration"] = sum(durations) / len(durations)

    # Calculate note range
    if analysis["lowest_note"] < 127 and analysis["highest_note"] > 0:
        analysis["note_range"] = analysis["highest_note"] - analysis["lowest_note"]

    # Normalize legato score
    if analysis["note_count"] > 0:
        analysis["legato_score"] = analysis["legato_score"] / analysis["note_count"]

    # Calculate scores for each category
    _calculate_bass_score(analysis)
    _calculate_keys_guitars_score(analysis)
    _calculate_strings_score(analysis)

    return analysis


def _calculate_bass_score(analysis: dict) -> None:
    """Calculate score for Bass classification."""
    score = 0.0

    # Track name contains bass keywords = +30 points
    if analysis["track_name"]:
        name_lower = analysis["track_name"].lower()
        if any(keyword in name_lower for keyword in BASS_KEYWORDS):
            score += 30.0

    # High percentage of bass notes = +40 points
    if analysis["note_count"] > 0:
        bass_percentage = (analysis["bass_note_count"] / analysis["note_count"]) * 100
        if bass_percentage > 70:
            score += 40.0
        elif bass_percentage > 50:
            score += 25.0
        elif bass_percentage > 30:
            score += 15.0

    # Low note range (most notes below C4) = +20 points
    if analysis["highest_note"] <= BASS_NOTE_MAX:
        score += 20.0
    elif analysis["highest_note"] <= 72:  # C5
        score += 10.0

    # Low polyphony (bass is often monophonic or 2-3 notes) = +15 points
    if analysis["max_simultaneous"] <= 2:
        score += 15.0
    elif analysis["max_simultaneous"] <= 4:
        score += 8.0

    # Longer note durations (bass sustains) = +10 points
    if analysis["avg_note_duration"] > 500:
        score += 10.0
    elif analysis["avg_note_duration"] > 300:
        score += 5.0

    # Has pitch bend (bass slides) = +5 points
    if analysis["has_pitch_bend"]:
        score += 5.0

    analysis["scores"]["bass"] = score


def _calculate_keys_guitars_score(analysis: dict) -> None:
    """Calculate score for Keys/Guitars classification."""
    score = 0.0

    # Track name contains keys/guitar keywords = +30 points
    if analysis["track_name"]:
        name_lower = analysis["track_name"].lower()
        if any(keyword in name_lower for keyword in KEYS_KEYWORDS + GUITAR_KEYWORDS):
            score += 30.0

    # Wide note range (spans multiple octaves) = +25 points
    if analysis["note_range"] >= 24:  # 2 octaves
        score += 25.0
    elif analysis["note_range"] >= 12:  # 1 octave
        score += 15.0

    # High polyphony (chords) = +20 points
    if analysis["max_simultaneous"] >= 5:
        score += 20.0
    elif analysis["max_simultaneous"] >= 3:
        score += 12.0

    # Medium to high note density = +15 points
    if analysis["note_count"] > 200:
        score += 15.0
    elif analysis["note_count"] > 100:
        score += 10.0

    # Velocity variations (dynamic playing) = +10 points
    if analysis["velocities"]:
        velocity_range = max(analysis["velocities"]) - min(analysis["velocities"])
        if velocity_range > 60:
            score += 10.0
        elif velocity_range > 40:
            score += 5.0

    # Balanced note distribution (not just low or high) = +10 points
    if analysis["note_count"] > 0:
        mid_percentage = (
            analysis["mid_range_note_count"] / analysis["note_count"]
        ) * 100
        if 30 <= mid_percentage <= 70:
            score += 10.0

    analysis["scores"]["keys_guitars"] = score


def _calculate_strings_score(analysis: dict) -> None:
    """Calculate score for Strings classification."""
    score = 0.0

    # Track name contains strings keywords = +30 points
    if analysis["track_name"]:
        name_lower = analysis["track_name"].lower()
        if any(keyword in name_lower for keyword in STRINGS_KEYWORDS):
            score += 30.0

    # High legato score (overlapping notes) = +25 points
    if analysis["legato_score"] > 0.5:
        score += 25.0
    elif analysis["legato_score"] > 0.3:
        score += 15.0

    # Long note durations (sustained notes) = +20 points
    if analysis["avg_note_duration"] > 800:
        score += 20.0
    elif analysis["avg_note_duration"] > 500:
        score += 12.0

    # Wide note range (ensemble spans wide range) = +15 points
    if analysis["note_range"] >= 24:
        score += 15.0
    elif analysis["note_range"] >= 12:
        score += 8.0

    # High polyphony (ensemble playing) = +15 points
    if analysis["max_simultaneous"] >= 4:
        score += 15.0
    elif analysis["max_simultaneous"] >= 2:
        score += 8.0

    # Smooth velocity (ensemble dynamics) = +10 points
    if analysis["velocities"]:
        velocity_std = _calculate_std_dev(analysis["velocities"])
        if velocity_std < 20:  # Low variation suggests ensemble
            score += 10.0

    # Moderate note density (not too sparse, not too dense) = +5 points
    if 50 <= analysis["note_count"] <= 500:
        score += 5.0

    analysis["scores"]["strings"] = score


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
        - "bass": List of (track_index, analysis_dict) tuples
        - "keys_guitars": List of (track_index, analysis_dict) tuples
        - "strings": List of (track_index, analysis_dict) tuples
        - "unclassified": List of (track_index, analysis_dict) tuples
    """
    exclude_drum_tracks = exclude_drum_tracks or []

    # Analyze all tracks
    track_analyses = []
    for i, track in enumerate(midi_file.tracks):
        if i in exclude_drum_tracks:
            continue
        analysis = analyze_track_for_classification(track, i)
        track_analyses.append(analysis)

    # Classify each track
    classifications = {
        "bass": [],
        "keys_guitars": [],
        "strings": [],
        "unclassified": [],
    }

    for analysis in track_analyses:
        scores = analysis["scores"]
        max_score = max(scores.values())
        max_category = max(scores.items(), key=lambda x: x[1])[0]

        if max_score >= min_score:
            classifications[max_category].append((analysis["track_index"], analysis))
        else:
            classifications["unclassified"].append((analysis["track_index"], analysis))

    # Sort each category by score (descending)
    for category in classifications:
        if category == "unclassified":
            # Sort unclassified by their best score
            classifications[category].sort(
                key=lambda x: max(x[1]["scores"].values()), reverse=True
            )
        else:
            classifications[category].sort(
                key=lambda x: x[1]["scores"][category], reverse=True
            )

    return classifications
