def _build_coarse_tune() -> tuple:
    """Build 128 note names (C -1 … G 9) matching Perl @coarse_tune."""
    notes = ("C ", "C#", "D ", "Eb", "E ", "F ", "F#", "G ", "G#", "A ", "Bb", "B ")
    return tuple(notes[n] + str(o) for o in range(-1, 10) for n in range(12))[:128]


class EffectsData:
    """Collection of ui lists for Effects"""

    rate_note_states = ["RATE", "NOTE"]

    efx1_types = ["Thru", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"]
    efx1_type_values = [0, 1, 2, 3, 4]

    efx2_types = ["OFF", "FLANGER", "PHASER", "RING MOD", "SLICER"]
    efx2_type_values = [0, 5, 6, 7, 8]

    output_assignments = ["DIR", "EFX2"]

    effects_generic_types = ["0", "1", "2", "3", "4", "5"]

    switch_states = ["OFF", "ON"]

    flanger_notes = [
        "1/96",
        "1/64",
        "1/48",
        "1/32",
        "1/24",
        "3/64",
        "1/16",
        "1/12",
        "3/32",
        "1/8",
        "1/6",
        "3/16",
        "1/4",
        "1/3",
        "3/8",
        "1/2",
        "2/3",
        "3/4",
        "1",
        "4/3",
        "3/2",
        "2",
    ]
    # Alias for Delay/Flanger/Slicer note dropdown (matches Perl @dly_notes)
    delay_notes = flanger_notes

    # Reverb types (matches Perl @rev_type)
    rev_type = ["Room 1", "Room 2", "Stage 1", "Stage 2", "Hall 1", "Hall 2"]

    # HF Damp options for Delay/Reverb (matches Perl @hf_damp)
    hf_damp = [
        "200Hz",
        "250Hz",
        "315Hz",
        "400Hz",
        "500Hz",
        "630Hz",
        "800Hz",
        "1000Hz",
        "1250Hz",
        "1600Hz",
        "2000Hz",
        "2500Hz",
        "3150Hz",
        "4000Hz",
        "5000Hz",
        "6300Hz",
        "8000Hz",
        "BYPASS",
    ]

    # Delay type (SINGLE / PAN)
    delay_types = ["SINGLE", "PAN"]

    # Delay Time/Note mode
    delay_time_note_modes = ["Time", "Note"]

    # Note names for Side Note / coarse tune (C -1 … G 9, 128 entries; matches Perl @coarse_tune)
    coarse_tune = _build_coarse_tune()

    # Compression ratios
    compression_ratios = [
        "  1:1",
        "  2:1",
        "  3:1",
        "  4:1",
        "  5:1",
        "  6:1",
        "  7:1",
        "  8:1",
        "  9:1",
        " 10:1",
        " 20:1",
        " 30:1",
        " 40:1",
        " 50:1",
        " 60:1",
        " 70:1",
        " 80:1",
        " 90:1",
        "100:1",
        " inf:1",
    ]
    # Compression attack times
    compression_attack_times = [
        "0.05",
        "0.06",
        "0.07",
        "0.08",
        "0.09",
        "0.10",
        "0.20",
        "0.30",
        "0.40",
        "0.50",
        "0.60",
        "0.70",
        "0.80",
        "0.90",
        "1.0",
        "2.0",
        "3.0",
        "4.0",
        "5.0",
        "6.0",
        "7.0",
        "8.0",
        "9.0",
        "10.0",
        "15.0",
        "20.0",
        "25.0",
        "30.0",
        "35.0",
        "40.0",
        "45.0",
        "50.0",
    ]

    # Tooltips for effect controls (Phase 5 polish)
    effect_tooltips = {
        "EFX1_TYPE": "Effect 1 type: Thru, Distortion, Fuzz, Compressor, or Bit Crusher",
        "EFX1_LEVEL": "Effect 1 output level (0–127)",
        "EFX2_TYPE": "Effect 2 type: Off, Flanger, Phaser, Ring Mod, or Slicer",
        "EFX2_LEVEL": "Effect 2 output level (0–127)",
        "DELAY_ON_OFF": "Enable or bypass delay",
        "REVERB_ON_OFF": "Enable or bypass reverb",
        "EFX1_PARAM_3_DISTORTION_TYPE": "Distortion character type (0–5)",
        "EFX1_PARAM_3_FUZZ_TYPE": "Fuzz character type (0–5)",
        "EFX2_PARAM_5_PHASER_CENTER_FREQ": "Phaser resonance (0–127)",
    }

    # Compression release times
    compression_release_times = [
        "0.05",
        "0.07",
        "0.10",
        "0.50",
        "1",
        "5",
        "10",
        "17",
        "25",
        "50",
        "75",
        "100",
        "200",
        "300",
        "400",
        "500",
        "600",
        "700",
        "800",
        "900",
        "1000",
        "1200",
        "1500",
        "2000",
    ]
