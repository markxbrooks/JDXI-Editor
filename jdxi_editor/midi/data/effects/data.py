from jdxi_editor.midi.data.effects.effects import EffectParam

DISTORTION_PARAMS = [
    EffectParam("Drive", 0, 127, 64),
    EffectParam("Level", 0, 127, 100),
    EffectParam("Tone", -20000, 20000, 0, "Hz"),
]
FUZZ_PARAMS = [
    EffectParam("Drive", 0, 127, 64),
    EffectParam("Level", 0, 127, 100),
    EffectParam("Tone", -20000, 20000, 0, "Hz"),
]
COMPRESSOR_PARAMS = [
    EffectParam("Attack", 0, 127, 64, "ms"),
    EffectParam("Release", 0, 127, 64, "ms"),
    EffectParam("Threshold", -60, 0, -20, "dB"),
    EffectParam("Ratio", 1, 100, 4),
    EffectParam("Gain", -12, 12, 0, "dB"),
]
BITCRUSHER_PARAMS = [
    EffectParam("Bit Depth", 1, 16, 16, "bits"),
    EffectParam("Sample Rate", 1000, 48000, 48000, "Hz"),
    EffectParam("Drive", 0, 127, 64),
]
PHASER_PARAMS = [
    EffectParam("Rate", 0, 127, 64),
    EffectParam("Depth", 0, 127, 64),
    EffectParam("Manual", -20000, 20000, 0),
    EffectParam("Resonance", 0, 127, 64),
    EffectParam("Mix", 0, 100, 50, "%"),
]
FLANGER_PARAMS = [
    EffectParam("Rate", 0, 127, 64),
    EffectParam("Depth", 0, 127, 64),
    EffectParam("Manual", -20000, 20000, 0),
    EffectParam("Resonance", 0, 127, 64),
    EffectParam("Mix", 0, 100, 50, "%"),
]
DELAY_PARAMS = [
    EffectParam("Time", 1, 2000, 500, "ms"),
    EffectParam("Feedback", 0, 127, 64),
    EffectParam("High Damp", 0, 127, 64),
    EffectParam("Mix", 0, 100, 50, "%"),
]
CHORUS_PARAMS = [
    EffectParam("Rate", 0, 127, 64),
    EffectParam("Depth", 0, 127, 64),
    EffectParam("Pre-Delay", 0, 100, 0, "ms"),
    EffectParam("Mix", 0, 100, 50, "%"),
]
MAIN_DELAY_PARAMS = [
    EffectParam("Time", 1, 2000, 500, "ms"),
    EffectParam("Feedback", 0, 127, 64),
    EffectParam("High Damp", 0, 127, 64),
    EffectParam("Low Damp", 0, 127, 64),
]
MAIN_REVERB_PARAMS = [
    EffectParam("Time", 0, 127, 64),
    EffectParam("Pre-Delay", 0, 100, 0, "ms"),
    EffectParam("High Damp", 0, 127, 64),
    EffectParam("Low Damp", 0, 127, 64),
    EffectParam("Density", 0, 127, 64),
]
EFX1_PARAMS = {
    0: [],  # OFF
    1: DISTORTION_PARAMS,
    2: FUZZ_PARAMS,
    3: COMPRESSOR_PARAMS,
    4: BITCRUSHER_PARAMS,
}
EFX2_PARAMS = {
    0: [],  # OFF
    5: PHASER_PARAMS,
    6: FLANGER_PARAMS,
    7: DELAY_PARAMS,
    8: CHORUS_PARAMS,
}
