from pathlib import Path
from music21 import converter
from music21 import environment
env = environment.UserSettings()
env['lilypondPath'] = '/opt/lilypond-2.24.4/bin/lilypond'

midi_file = Path.home() / "Desktop" / "music" / "Crocketts Theme - Jan Hammer - JDXi.mid"

score = converter.parse(midi_file)

# minimal cleanup (keep it simple first)
score = score.quantize(quarterLengthDivisors=(4, 3))
score.makeMeasures(inPlace=True)
score.makeNotation(inPlace=True)

# --- SAFE OUTPUT NAME (NO SPACES) ---
safe_output = midi_file.parent / "output_score"

score.write(fp=safe_output, fmt='lily.pdf')

print("PDF created:", safe_output.with_suffix('.pdf'))
