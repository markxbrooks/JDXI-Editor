
import numpy as np
import pretty_midi
import sys

def detect_onsets_wav_to_midi(wav_path, midi_path,
                              sr=22050, hop_length=512,
                              fps=100, tempo_guess=120.0,
                              min_note_len=0.05):
    # Load audio
    y, sr = librosa.load(wav_path, sr=sr, mono=True)

    # Compute onset strength envelope (global, not drum-specific)
    # You can also try a multi-band onset detection by filtering bands
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

    # Onset times (in seconds)
    onset_times = librosa.onset.onset_detect(onset_envelope=onset_env,
                                             sr=sr, hop_length=hop_length,
                                             backoff=0.5)

    # Convert to seconds (onset_times is already in frames -> seconds via hop_length/sr)
    onset_seconds = librosa.frames_to_time(onset_times, sr=sr, hop_length=hop_length)

    # Optional tempo estimation (not strictly needed for MIDI, but helps with quantization)
    # tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)

    # Create a PrettyMIDI object and a drum instrument (drums channel)
    pm = pretty_midi.PrettyMIDI()
    drum_program = pretty_midi.instrument_name_to_program('Acoustic Drum Kit')
    drum = pretty_midi.Instrument(program=drum_program, is_drum=True, name='Drum')
    pm.instruments.append(drum)

    # Simple mapping: all detected onsets become kicks (note number 36)
    # For a more varied drum kit, you can assign different MIDI note numbers
    # 36: Kick, 38: Snare, 42/46: Closed/Open Hat etc.
    # Here, as a starting point, we’ll alternate kick and snare for demonstration.

    note_sequence = []
    grid = 60.0 / 4.0  # 16th-note grid at 60 BPM (will be recalculated below if tempo is known)

    # Quantize to a grid based on a fixed tempo; compute MIDI ticks timing
    # We'll simply map seconds to MIDI ticks assuming 480 PPQ
    PPQ = 480
    # Build events with simple rule: even indices -> kick (36), odd -> snare (38)
    for i, t in enumerate(onset_seconds):
        # Quantize to 16th-note grid (adjust as needed)
        # First, estimate beat length in seconds from a reasonable tempo
        # We'll use 120 BPM as default if not estimating tempo
        beat_len = 60.0 / 120.0  # default beat length
        grid_len = beat_len / 4.0  # 16th note
        # Quantize time to nearest grid
        q = round(t / grid_len) * grid_len
        # Alternate between kick and snare for demonstration
        midi_note = 36 if i % 2 == 0 else 38
        velocity = 100
        start = q
        duration = min(min_note_len, 0.25)  # a short hit
        end = start + duration

        note = pretty_midi.Note(velocity=velocity, pitch=midi_note,
                                start=start, end=end)
        drum.notes.append(note)

    # Write MIDI
    pm.write(midi_path)
    print(f"Wrote MIDI to {midi_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python drum_to_midi.py input.wav output.mid")
        sys.exit(1)
    detect_onsets_wav_to_midi(sys.argv[1], sys.argv[2])
