from mido import MidiTrack

from jdxi_editor.midi.track.data import BASS_NOTE_MAX
from jdxi_editor.midi.track.stats import TrackStats


class TrackAnalyzer:
    """Track analyser to add tracks"""

    def __init__(self, track: MidiTrack, index: int):
        self.track = track
        self.stats = TrackStats(index)

        self.time = 0
        self.active_notes: dict[int, int] = {}
        self.note_start: dict[int, int] = {}
        self.durations: list[int] = []

    def run(self) -> TrackStats:
        """run the analysis and send to dispatcher"""
        self._read_track_name()

        for msg in self.track:
            self.time += msg.time
            if msg.is_meta:
                continue
            self._dispatch(msg)

        self._finalize()
        return self.stats

    def _dispatch(self, msg):
        """dispatch to handler"""
        if hasattr(msg, "channel"):
            self.stats.channels.add(msg.channel)

        handler = getattr(self, f"_on_{msg.type}", None)
        if handler:
            handler(msg)

    def _on_note_on(self, msg):
        """on note on"""
        if msg.velocity == 0:
            return self._on_note_off(msg)

        s = self.stats
        note = msg.note

        s.note_count += 1
        s.notes.append(note)
        s.velocities.append(msg.velocity)
        s.note_ons.append((self.time, note, msg.channel))

        s.lowest_note = min(s.lowest_note, note)
        s.highest_note = max(s.highest_note, note)

        if note <= BASS_NOTE_MAX:
            s.bass_note_count += 1
        elif note <= 72:
            s.mid_range_note_count += 1
        else:
            s.high_note_count += 1

        self.active_notes[note] = self.time
        s.max_simultaneous = max(s.max_simultaneous, len(self.active_notes))

        self.note_start[note] = self.time

    def _on_note_off(self, msg):
        """check for legato"""
        note = msg.note
        self.stats.note_offs.append((self.time, note))

        start = self.note_start.pop(note, None)
        if start is None:
            return

        duration = self.time - start
        self.durations.append(duration)

        # legato detection
        for other_start in self.note_start.values():
            if start < other_start < self.time:
                self.stats.legato_score += 1

        self.active_notes.pop(note, None)

    def _on_pitchwheel(self, msg):
        """check for bent notes"""
        self.stats.has_pitch_bend = True

    def _on_control_change(self, msg):
        """add cc"""
        self.stats.has_control_change = True

    def _on_program_change(self, msg):
        """add pc"""
        self.stats.program_changes.append(msg.program)

    def _finalize(self):
        """finalize analysis"""
        s = self.stats

        if self.durations:
            s.avg_note_duration = sum(self.durations) / len(self.durations)

        if s.lowest_note < 127:
            s.note_range = s.highest_note - s.lowest_note

        if s.note_count:
            s.legato_score /= s.note_count
        # To avoid circular import error
        from jdxi_editor.midi.track.classification import calculate_scores
        calculate_scores(s)

    def _read_track_name(self):
        """Extract track name from meta messages"""
        for msg in self.track:
            if msg.is_meta and msg.type == "track_name":
                self.stats.track_name = msg.name
                break
