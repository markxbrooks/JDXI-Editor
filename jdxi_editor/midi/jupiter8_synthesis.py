"""
Jupiter 8 String Synthesis Module

This module provides functions to create Jupiter 8-like string sounds using pure Python synthesis
without requiring SoundFonts or external audio libraries.
"""

import numpy as np
import scipy.io.wavfile as wav


def create_jupiter8_string(frequency=440, duration=2.0, sample_rate=44100):
    """Create a Jupiter 8-like string sound using additive synthesis"""
    
    # Time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Fundamental frequency
    fundamental = np.sin(2 * np.pi * frequency * t)
    
    # Harmonics (Jupiter 8 strings have rich harmonics)
    harmonics = [
        0.5 * np.sin(2 * np.pi * frequency * 2 * t),    # 2nd harmonic
        0.3 * np.sin(2 * np.pi * frequency * 3 * t),    # 3rd harmonic
        0.2 * np.sin(2 * np.pi * frequency * 4 * t),    # 4th harmonic
        0.1 * np.sin(2 * np.pi * frequency * 5 * t),    # 5th harmonic
    ]
    
    # Combine all harmonics
    string_sound = fundamental + sum(harmonics)
    
    # Calculate envelope segments
    total_samples = len(string_sound)
    attack_samples = int(0.1 * total_samples)
    decay_samples = int(0.2 * total_samples)
    sustain_samples = int(0.5 * total_samples)
    release_samples = total_samples - attack_samples - decay_samples - sustain_samples
    
    # Ensure we don't have negative release samples
    if release_samples < 0:
        # Adjust sustain to fit
        sustain_samples += release_samples
        release_samples = 0
    
    # Create ADSR envelope
    envelope = np.ones(total_samples)
    
    # Attack (0 to 1)
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay (1 to 0.7)
    if decay_samples > 0:
        envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, 0.7, decay_samples)
    
    # Sustain (0.7)
    if sustain_samples > 0:
        envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = 0.7
    
    # Release (0.7 to 0)
    if release_samples > 0:
        envelope[attack_samples+decay_samples+sustain_samples:] = np.linspace(0.7, 0, release_samples)
    
    # Apply envelope and normalize
    string_sound = string_sound * envelope
    string_sound = string_sound / np.max(np.abs(string_sound)) * 0.8
    
    return string_sound, sample_rate


def create_string_chord(frequencies, duration=3.0, sample_rate=44100):
    """Create a chord of Jupiter 8-like strings"""
    
    # Create individual string sounds
    string_sounds = []
    for freq in frequencies:
        sound, _ = create_jupiter8_string(freq, duration, sample_rate)
        string_sounds.append(sound)
    
    # Mix them together
    chord = np.sum(string_sounds, axis=0)
    
    # Normalize to prevent clipping
    chord = chord / np.max(np.abs(chord)) * 0.8
    
    return chord, sample_rate


def demo_jupiter8_strings():
    """Demo function to create and save Jupiter 8-like string sounds"""
    
    print("[INFO] Creating Jupiter 8-like string sounds...")
    
    # Create a single string note (A4)
    single_string, sr = create_jupiter8_string(frequency=440, duration=3.0)
    wav.write('jupiter8_single_string.wav', sr, (single_string * 32767).astype(np.int16))
    print("[INFO] Created single string: jupiter8_single_string.wav")
    
    # Create a string chord (C major: C, E, G)
    chord_frequencies = [261.63, 329.63, 392.00]  # C4, E4, G4
    string_chord, sr = create_string_chord(chord_frequencies, duration=4.0)
    wav.write('jupiter8_string_chord.wav', sr, (string_chord * 32767).astype(np.int16))
    print("[INFO] Created string chord: jupiter8_string_chord.wav")
    
    # Create a lower string note (C3)
    low_string, sr = create_jupiter8_string(frequency=130.81, duration=3.0)
    wav.write('jupiter8_low_string.wav', sr, (low_string * 32767).astype(np.int16))
    print("[INFO] Created low string: jupiter8_low_string.wav")
    
    print("[INFO] All Jupiter 8-like string sounds created successfully!")


if __name__ == "__main__":
    demo_jupiter8_strings()
