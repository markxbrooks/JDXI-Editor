"""PDF export works from folders whose names contain spaces (LilyPond splits
the output path at spaces when music21 passes it)."""

from pathlib import Path

import mido
import pytest

from jdxi_editor.midi.music import pdf_export


def test_the_lilypond_work_folder_has_no_spaces():
    work = pdf_export._lily_workdir()
    try:
        assert " " not in str(work) and work.is_dir()
    finally:
        work.rmdir()


def _lilypond_available() -> bool:
    try:
        from music21 import environment

        path = environment.UserSettings()["lilypondPath"]
        return bool(path) and Path(str(path)).exists()
    except Exception:
        return False


@pytest.mark.skipif(not _lilypond_available(), reason="LilyPond not installed")
def test_export_beside_a_midi_file_in_folders_with_spaces(tmp_path):
    folder = tmp_path / "Oxygene JD-Xi" / "OxygeneV parts"
    folder.mkdir(parents=True)
    midi = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack([mido.MetaMessage("track_name", name="Bass")])
    for p in (55, 58, 60, 62) * 2:
        track += [mido.Message("note_on", note=p, velocity=90, time=0), mido.Message("note_off", note=p, time=480)]
    midi.tracks.append(track)
    source = folder / "Song - Someone.mid"
    midi.save(source)
    out = pdf_export.export_midi_to_pdf(source)
    assert out and Path(out) == folder / "Song - Someone.pdf" and Path(out).exists()
    assert sorted(p.name for p in folder.iterdir()) == ["Song - Someone.mid", "Song - Someone.pdf"]
