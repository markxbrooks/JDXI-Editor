"""
Drum track detection utilities for MIDI files.

This module provides functions to analyze MIDI tracks and identify which tracks
are likely drum tracks based on various heuristics.
"""

from collections import defaultdict
from typing import List, Tuple

import mido
from mido import MidiFile, MidiTrack

# Standard General MIDI drum note range (35-81)
DRUM_NOTE_MIN = 35
DRUM_NOTE_MAX = 81

# Keywords that suggest a drum track
DRUM_KEYWORDS = [
    "drum",
    "percussion",
    "perc",
    "kit",
    "beat",
    "rhythm",
    "snare",
    "kick",
    "hihat",
    "hi-hat",
    "cymbal",
    "crash",
]


def analyze_track_for_drums(track: MidiTrack, track_index: int) -> dict:
    """
    Analyze a MIDI track to determine if it's likely a drum track.

    Returns a dictionary with analysis results and a score.
    """
    analysis = {
        "track_index": track_index,
        "track_name": None,
        "channels": set(),
        "note_count": 0,
        "drum_note_count": 0,
        "note_ons": [],
        "note_offs": [],
        "avg_note_duration": 0.0,
        "simultaneous_notes": 0,
        "max_simultaneous": 0,
        "has_pitch_bend": False,
        "has_control_change": False,
        "program_changes": [],
        "score": 0.0,
    }

    # Extract track name from meta messages
    for msg in track:
        if msg.is_meta and msg.type == "track_name":
            analysis["track_name"] = msg.name
            break

    # Analyze messages
    active_notes = defaultdict(int)  # Track active notes at each tick
    absolute_time = 0
    note_durations = []

    for msg in track:
        absolute_time += msg.time

        if msg.is_meta:
            continue

        if hasattr(msg, "channel"):
            analysis["channels"].add(msg.channel)

        if msg.type == "note_on" and msg.velocity > 0:
            analysis["note_count"] += 1
            analysis["note_ons"].append((absolute_time, msg.note, msg.channel))

            # Check if note is in drum range
            if DRUM_NOTE_MIN <= msg.note <= DRUM_NOTE_MAX:
                analysis["drum_note_count"] += 1

            # Track simultaneous notes
            active_notes[absolute_time] += 1
            analysis["max_simultaneous"] = max(
                analysis["max_simultaneous"], active_notes[absolute_time]
            )

        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            analysis["note_offs"].append((absolute_time, msg.note))

        elif msg.type == "pitchwheel":
            analysis["has_pitch_bend"] = True

        elif msg.type == "control_change":
            analysis["has_control_change"] = True

        elif msg.type == "program_change":
            analysis["program_changes"].append(msg.program)

    # Calculate average note duration (simplified)
    if analysis["note_ons"] and analysis["note_offs"]:
        # Match note ons with note offs (simplified approach)
        durations = []
        for on_time, note, _ in analysis["note_ons"]:
            # Find corresponding note off
            for off_time, off_note in analysis["note_offs"]:
                if off_note == note and off_time > on_time:
                    durations.append(off_time - on_time)
                    break
        if durations:
            analysis["avg_note_duration"] = sum(durations) / len(durations)

    # Calculate score
    score = 0.0

    # Channel 9 (drum channel) = +50 points
    if 9 in analysis["channels"]:
        score += 50.0

    # Track name contains drum keywords = +30 points
    if analysis["track_name"]:
        name_lower = analysis["track_name"].lower()
        if any(keyword in name_lower for keyword in DRUM_KEYWORDS):
            score += 30.0

    # High percentage of drum notes = +20 points
    if analysis["note_count"] > 0:
        drum_percentage = (analysis["drum_note_count"] / analysis["note_count"]) * 100
        if drum_percentage > 80:
            score += 20.0
        elif drum_percentage > 50:
            score += 10.0

    # High note density = +10 points
    if analysis["note_count"] > 100:
        score += 10.0

    # High polyphony (many simultaneous notes) = +10 points
    if analysis["max_simultaneous"] > 5:
        score += 10.0

    # Short average note duration (typical for drums) = +5 points
    if analysis["avg_note_duration"] > 0 and analysis["avg_note_duration"] < 500:
        score += 5.0

    # No pitch bend (drums don't use it) = +5 points
    if not analysis["has_pitch_bend"]:
        score += 5.0

    analysis["score"] = score
    return analysis


def detect_drum_tracks(
    midi_file: MidiFile, min_score: float = 70.0
) -> List[Tuple[int, dict]]:
    """
    Detect drum tracks in a MIDI file.

    Args:
        midi_file: The MIDI file to analyze
        min_score: Minimum score threshold for a track to be considered a drum track

    Returns:
        List of tuples (track_index, analysis_dict) for tracks that meet the threshold,
        sorted by score (descending)
    """
    # Analyze all tracks
    track_analyses = []
    for i, track in enumerate(midi_file.tracks):
        analysis = analyze_track_for_drums(track, i)
        track_analyses.append(analysis)

    # Sort by score (descending), then by tie-breaker criteria
    def tie_breaker(analysis):
        """Tie-breaker: prefer tracks with more notes, higher polyphony, shorter durations"""
        return (
            analysis["score"],
            analysis["note_count"],  # More notes = more likely main drum track
            analysis["max_simultaneous"],  # Higher polyphony
            (
                -analysis["avg_note_duration"]
                if analysis["avg_note_duration"] > 0
                else 0
            ),  # Shorter durations
            not analysis["has_control_change"],  # No control changes preferred
        )

    track_analyses.sort(key=tie_breaker, reverse=True)

    # Filter by minimum score
    drum_tracks = [
        (analysis["track_index"], analysis)
        for analysis in track_analyses
        if analysis["score"] >= min_score
    ]

    return drum_tracks
