from pathlib import Path
from music21 import converter, environment, metadata

env = environment.UserSettings()
env['lilypondPath'] = '/opt/lilypond-2.24.4/bin/lilypond'

midi_file = Path.home() / "Desktop" / "music" / "Crocketts Theme - Jan Hammer - JDXi.mid"

score = converter.parse(midi_file)

# Add metadata (title, composer, etc.)
score.metadata = metadata.Metadata()
score.metadata.title = "Crocketts Theme"
score.metadata.composer = "Jan Hammer"

# minimal cleanup
score = score.quantize(quarterLengthDivisors=(4, 3))
score.makeMeasures(inPlace=True)
score.makeNotation(inPlace=True)

# Safe output file name (no spaces)
safe_output = midi_file.parent / "output_score"

# Write PDF via Lilypond
score.write(fp=safe_output, fmt='lily.pdf')

print("PDF created:", safe_output.with_suffix('.pdf'))
