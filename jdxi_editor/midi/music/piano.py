from pathlib import Path
from music21 import converter, environment
import sys
import os
import shutil
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))
from jdxi_editor.midi.music.pdf_export import cleanup_score, annotate_staffs, export_score, set_metadata, \
    remove_empty_parts
from jdxi_editor.midi.music.track import get_track_names
from decologr import setup_logging, Decologr as log

env = environment.UserSettings()
env['lilypondPath'] = '/opt/lilypond-2.24.4/bin/lilypond'


def main(midi_file: str):
    midi_file = Path(midi_file)
    setup_logging(project_name="scorely")

    midi_file_stem = midi_file.stem

    # try to match the format "Title - Composer - JDXi"
    if " - " in midi_file_stem:
        filename_parts = midi_file_stem.split(" - ")
        title = filename_parts[0]
        composer = filename_parts[1]
    # Gary_Numan_Cars.mid
    elif "_" in midi_file_stem:
        filename_parts = midi_file_stem.split("_")
        title = filename_parts[0]
        composer = filename_parts[1]
    elif "-" in midi_file_stem:
        filename_parts = midi_file_stem.split("-")
        title = filename_parts[0]
        composer = filename_parts[1]
    else:
        title = midi_file_stem
        composer = "Unknown"

    # Parse the MIDI file
    score = converter.parse(midi_file)

    set_metadata(composer, score, title)

    # --- Get MIDI track names for staff labels ---
    track_names = get_track_names(str(midi_file))

    annotate_staffs(score, track_names)

    score = remove_empty_parts(score)

    score = cleanup_score(score)

    try:
        final_file, safe_output = export_score(midi_file, midi_file_stem, score)
    except ValueError as e:
        log.error(f"Export failed: {e}")
        raise
    shutil.move(safe_output.with_suffix('.pdf'), final_file)

    log.message(f"Moved file to {final_file}")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--midi-file", type=str, required=True)
    args = args.parse_args()
    main(args.midi_file)