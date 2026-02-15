from music21 import midi as m21_midi
from music21.midi import MetaEvents


def get_track_names(midi_path: str) -> list[str]:
    """Extract track names from a MIDI file (music21.midi.MidiFile, SEQUENCE_TRACK_NAME)."""
    mf = m21_midi.MidiFile()
    mf.open(midi_path)
    mf.read()
    mf.close()
    names = []
    for track in mf.tracks:
        track_name_events = [
            e for e in track.events if e.type == MetaEvents.SEQUENCE_TRACK_NAME
        ]
        if track_name_events:
            data = track_name_events[0].data
            names.append(data.decode("utf-8") if isinstance(data, bytes) else data)
        else:
            names.append(None)
    return names
