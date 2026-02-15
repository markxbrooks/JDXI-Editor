"""
Unit test for MIDI track name extraction (e.g. for piano.py staff labels).

Asserts that the first track name is "Bass Synthesizer" and the second is "Electric Guitar"
when reading a MIDI file with music21.midi.MidiFile (same logic as piano.py).
"""

import os
import sys
import tempfile
import unittest

from mido import MidiFile, MidiTrack, MetaMessage

from jdxi_editor.midi.music.track import get_track_names

# Project root on path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_midi_with_track_names(*track_names: str) -> str:
    """Create a type-1 MIDI file with the given track names. Returns path to temp file."""
    mid = MidiFile(type=1)
    for name in track_names:
        track = MidiTrack()
        track.append(MetaMessage("track_name", name=name))
        track.append(MetaMessage("end_of_track"))
        mid.tracks.append(track)
    fd, path = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    mid.save(path)
    return path


class TestMidiTrackNames(unittest.TestCase):
    """Test that MIDI track names are read correctly for staff annotation."""

    def test_first_track_name_is_bass_synthesizer(self):
        """First track name must be 'Bass Synthesizer'."""
        path = _make_midi_with_track_names("Bass Synthesizer", "Electric Guitar")
        try:
            names = get_track_names(path)
            self.assertGreaterEqual(len(names), 1, "Expected at least one track")
            self.assertEqual(names[0], "Bass Synthesizer")
        finally:
            os.unlink(path)

    def test_second_track_name_is_electric_guitar(self):
        """Second track name must be 'Electric Guitar'."""
        path = _make_midi_with_track_names("Bass Synthesizer", "Electric Guitar")
        try:
            names = get_track_names(path)
            self.assertGreaterEqual(len(names), 2, "Expected at least two tracks")
            self.assertEqual(names[1], "Electric Guitar")
        finally:
            os.unlink(path)

    def test_both_track_names_in_order(self):
        """First track 'Bass Synthesizer', second track 'Electric Guitar'."""
        path = _make_midi_with_track_names("Bass Synthesizer", "Electric Guitar")
        try:
            names = get_track_names(path)
            self.assertEqual(names[0], "Bass Synthesizer")
            self.assertEqual(names[1], "Electric Guitar")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
