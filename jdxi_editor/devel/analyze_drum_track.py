#!/usr/bin/env python3
"""
Analyze a MIDI file to identify the drum track.

This script uses multiple heuristics to determine which track is the drum track:
1. MIDI Channel 9 (standard GM drum channel)
2. Track name containing drum-related keywords
3. Note patterns (drum range, note density, polyphony)
4. Lack of pitch bend/control changes
"""

import os
import sys
from collections import defaultdict
from typing import List, Optional, Tuple

try:
    import mido
    from mido import MidiFile
except ImportError:
    print("ERROR: mido library not found. Install with: pip install mido")
    sys.exit(1)


# Standard General MIDI drum note range (35-81)
DRUM_NOTE_MIN = 35
DRUM_NOTE_MAX = 81

# Keywords that suggest a drum track
DRUM_KEYWORDS = [
    "drum", "percussion", "perc", "kit", "beat", "rhythm",
    "snare", "kick", "hihat", "hi-hat", "cymbal", "crash"
]


def analyze_track_for_drums(track: mido.MidiTrack, track_index: int) -> dict:
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
                analysis["max_simultaneous"], 
                active_notes[absolute_time]
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


def find_drum_track(midi_file_path: str) -> Optional[Tuple[int, dict]]:
    """
    Analyze a MIDI file and return the most likely drum track.
    
    Returns: (track_index, analysis_dict) or None if file can't be analyzed
    """
    if not os.path.exists(midi_file_path):
        print(f"ERROR: File not found: {midi_file_path}")
        return None
    
    try:
        midi_file = MidiFile(midi_file_path)
    except Exception as e:
        print(f"ERROR: Could not load MIDI file: {e}")
        return None
    
    print(f"\n{'='*60}")
    print(f"Analyzing MIDI file: {midi_file_path}")
    print(f"{'='*60}")
    print(f"Ticks per beat: {midi_file.ticks_per_beat}")
    print(f"Number of tracks: {len(midi_file.tracks)}")
    print(f"Type: {midi_file.type}")
    print()
    
    # Analyze all tracks
    track_analyses = []
    for i, track in enumerate(midi_file.tracks):
        analysis = analyze_track_for_drums(track, i)
        track_analyses.append(analysis)
    
    # Print analysis for all tracks
    print("Track Analysis:")
    print("-" * 60)
    for analysis in track_analyses:
        track_name = analysis["track_name"] or f"Track {analysis['track_index'] + 1}"
        channels = sorted(analysis["channels"])
        channels_str = ", ".join(str(ch + 1) for ch in channels) if channels else "None"
        
        print(f"\nTrack {analysis['track_index'] + 1}: {track_name}")
        print(f"  Channels: {channels_str}")
        print(f"  Total notes: {analysis['note_count']}")
        print(f"  Drum notes ({DRUM_NOTE_MIN}-{DRUM_NOTE_MAX}): {analysis['drum_note_count']}")
        if analysis["note_count"] > 0:
            drum_pct = (analysis["drum_note_count"] / analysis["note_count"]) * 100
            print(f"  Drum note percentage: {drum_pct:.1f}%")
        print(f"  Max simultaneous notes: {analysis['max_simultaneous']}")
        if analysis["avg_note_duration"] > 0:
            print(f"  Avg note duration: {analysis['avg_note_duration']:.1f} ticks")
        print(f"  Has pitch bend: {analysis['has_pitch_bend']}")
        print(f"  Has control changes: {analysis['has_control_change']}")
        if analysis["program_changes"]:
            print(f"  Program changes: {analysis['program_changes']}")
        print(f"  DRUM SCORE: {analysis['score']:.1f}")
    
    # Find track with highest score
    if not track_analyses:
        return None
    
    # Sort by score (descending), then by tie-breaker criteria
    def tie_breaker(analysis):
        """Tie-breaker: prefer tracks with more notes, higher polyphony, shorter durations"""
        return (
            analysis["score"],
            analysis["note_count"],  # More notes = more likely main drum track
            analysis["max_simultaneous"],  # Higher polyphony
            -analysis["avg_note_duration"] if analysis["avg_note_duration"] > 0 else 0,  # Shorter durations
            not analysis["has_control_change"],  # No control changes preferred
        )
    
    best_track = max(track_analyses, key=tie_breaker)
    
    # Check for ties
    top_score = best_track["score"]
    tied_tracks = [t for t in track_analyses if t["score"] == top_score]
    
    print(f"\n{'='*60}")
    print("RESULT:")
    print(f"{'='*60}")
    if best_track["score"] > 0:
        track_name = best_track["track_name"] or f"Track {best_track['track_index'] + 1}"
        print(f"Most likely drum track: Track {best_track['track_index'] + 1} ({track_name})")
        print(f"Confidence score: {best_track['score']:.1f}/100")
        
        # Show tied tracks if any
        if len(tied_tracks) > 1:
            print(f"\n⚠ Note: {len(tied_tracks)} tracks tied with score {top_score:.1f}:")
            for tied in sorted(tied_tracks, key=lambda x: x["track_index"]):
                tied_name = tied["track_name"] or f"Track {tied['track_index'] + 1}"
                print(f"  - Track {tied['track_index'] + 1} ({tied_name}): "
                      f"{tied['note_count']} notes, "
                      f"max {tied['max_simultaneous']} simultaneous")
            print("  Selected based on: note count, polyphony, note duration, no control changes")
        
        if best_track["score"] >= 70:
            print("\n✓ High confidence - This is very likely the drum track")
        elif best_track["score"] >= 40:
            print("\n⚠ Medium confidence - This might be the drum track")
        else:
            print("\n⚠ Low confidence - Review manually")
        
        # Additional analysis for the selected track
        print(f"\nSelected track details:")
        print(f"  Channel: {sorted(best_track['channels'])[0] + 1 if best_track['channels'] else 'None'}")
        print(f"  Total notes: {best_track['note_count']}")
        print(f"  Drum notes: {best_track['drum_note_count']} ({best_track['drum_note_count']/best_track['note_count']*100:.1f}%)" if best_track['note_count'] > 0 else "  Drum notes: 0")
        print(f"  Max simultaneous: {best_track['max_simultaneous']}")
        
        return (best_track["track_index"], best_track)
    else:
        print("No track identified as drums (all scores were 0)")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_drum_track.py <midi_file>")
        print("\nExample:")
        print("  python analyze_drum_track.py theperfectkiss.mid")
        sys.exit(1)
    
    midi_file_path = sys.argv[1]
    result = find_drum_track(midi_file_path)
    
    if result:
        track_index, analysis = result
        print(f"\nTrack index (0-based): {track_index}")
        print(f"Track index (1-based): {track_index + 1}")
