from pathlib import Path
from music21 import converter, environment, metadata, instrument as m21_instrument

from jdxi_editor.midi.music.track import get_track_names

env = environment.UserSettings()
env['lilypondPath'] = '/opt/lilypond-2.24.4/bin/lilypond'

midi_file = Path.home() / "Desktop" / "music" / "Crocketts Theme - Jan Hammer - JDXi.mid"

# Parse the MIDI file
score = converter.parse(midi_file)

# --- Set metadata ---
score.metadata = metadata.Metadata()
score.metadata.title = "Crocketts Theme"
score.metadata.composer = "Jan Hammer"

# --- Get MIDI track names for staff labels ---
track_names = get_track_names(str(midi_file))


def short_name(name: str, max_len: int = 12) -> str:
    """Abbreviation for staff label (e.g. 'Piano' -> 'Pno.', long names truncated)."""
    if not name or len(name) <= max_len:
        return name or ""
    return name[: max_len - 1].rstrip() + "."


# Annotate each staff with its MIDI track name (for PDF labels)
for idx, part in enumerate(score.parts):
    track_name = None
    if idx < len(track_names):
        track_name = track_names[idx]
    if not track_name:
        inst = part.getInstrument()
        track_name = inst.instrumentName if inst else f"Part {idx + 1}"
    part.partName = track_name
    # So LilyPond prints the label on the staff, set the Instrument name too
    inst = part.getInstrument()
    if inst is not None:
        inst.instrumentName = track_name
        inst.instrumentAbbreviation = short_name(track_name)
    else:
        part.insert(0, m21_instrument.Instrument(instrumentName=track_name))

# Minimal cleanup
score = score.quantize(quarterLengthDivisors=(4, 3))
score.makeMeasures(inPlace=True)
score.makeNotation(inPlace=True)

# Safe output file name
safe_output = midi_file.parent / "output_score"

# Write PDF via Lilypond
score.write(fp=safe_output, fmt='lily.pdf')

print("PDF created:", safe_output.with_suffix('.pdf'))
