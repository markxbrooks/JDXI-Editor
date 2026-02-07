from dataclasses import dataclass
from typing import Callable

from jdxi_editor.midi.track.stats import TrackStats


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