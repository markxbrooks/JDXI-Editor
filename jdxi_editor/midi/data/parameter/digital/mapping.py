from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter

ENVELOPE_MAPPING = {
    # Filter ADSR
    "FILTER_ENV_ATTACK_TIME": EnvelopeParameter.ATTACK_TIME,
    "FILTER_ENV_DECAY_TIME": EnvelopeParameter.DECAY_TIME,
    "FILTER_ENV_SUSTAIN_LEVEL": EnvelopeParameter.SUSTAIN_LEVEL,
    "FILTER_ENV_RELEASE_TIME": EnvelopeParameter.RELEASE_TIME,
    "FILTER_ENV_DEPTH": EnvelopeParameter.PEAK_LEVEL,
    "FILTER_CUTOFF": EnvelopeParameter.FILTER_CUTOFF,
    # AMP ADSR
    "AMP_ENV_ATTACK_TIME": EnvelopeParameter.ATTACK_TIME,
    "AMP_ENV_DECAY_TIME": EnvelopeParameter.DECAY_TIME,
    "AMP_ENV_SUSTAIN_LEVEL": EnvelopeParameter.SUSTAIN_LEVEL,
    "AMP_ENV_RELEASE_TIME": EnvelopeParameter.RELEASE_TIME,
    # Oscillator
    "OSC_PITCH_ENV_ATTACK_TIME": EnvelopeParameter.ATTACK_TIME,
    "OSC_PITCH_ENV_DECAY_TIME": EnvelopeParameter.DECAY_TIME,
    "OSC_PITCH_ENV_DEPTH": EnvelopeParameter.PEAK_LEVEL,
    "OSC_PULSE_WIDTH": EnvelopeParameter.PULSE_WIDTH,
    "OSC_PULSE_WIDTH_MOD_DEPTH": EnvelopeParameter.MOD_DEPTH,
    # WMT 1
    "WMT1_VELOCITY_FADE_WIDTH_LOWER": EnvelopeParameter.FADE_LOWER,
    "WMT1_VELOCITY_RANGE_LOWER": EnvelopeParameter.RANGE_LOWER,
    "WMT1_VELOCITY_RANGE_UPPER": EnvelopeParameter.RANGE_UPPER,
    "WMT1_VELOCITY_FADE_WIDTH_UPPER": EnvelopeParameter.FADE_UPPER,
    "WMT1_WAVE_LEVEL": EnvelopeParameter.DEPTH,
    # WMT 2
    "WMT2_VELOCITY_FADE_WIDTH_LOWER": EnvelopeParameter.FADE_LOWER,
    "WMT2_VELOCITY_RANGE_LOWER": EnvelopeParameter.RANGE_LOWER,
    "WMT2_VELOCITY_RANGE_UPPER": EnvelopeParameter.RANGE_UPPER,
    "WMT2_VELOCITY_FADE_WIDTH_UPPER": EnvelopeParameter.FADE_UPPER,
    "WMT2_WAVE_LEVEL": EnvelopeParameter.DEPTH,
    # WMT 3
    "WMT3_VELOCITY_FADE_WIDTH_LOWER": EnvelopeParameter.FADE_LOWER,
    "WMT3_VELOCITY_RANGE_LOWER": EnvelopeParameter.RANGE_LOWER,
    "WMT3_VELOCITY_RANGE_UPPER": EnvelopeParameter.RANGE_UPPER,
    "WMT3_VELOCITY_FADE_WIDTH_UPPER": EnvelopeParameter.FADE_UPPER,
    "WMT3_WAVE_LEVEL": EnvelopeParameter.DEPTH,
    # WMT 4
    "WMT4_VELOCITY_FADE_WIDTH_LOWER": EnvelopeParameter.FADE_LOWER,
    "WMT4_VELOCITY_RANGE_LOWER": EnvelopeParameter.RANGE_LOWER,
    "WMT4_VELOCITY_RANGE_UPPER": EnvelopeParameter.RANGE_UPPER,
    "WMT4_VELOCITY_FADE_WIDTH_UPPER": EnvelopeParameter.FADE_UPPER,
    "WMT4_WAVE_LEVEL": EnvelopeParameter.DEPTH,
}
