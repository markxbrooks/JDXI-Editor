"""
Module for defining drum kit parameters in the Roland JD-Xi editor.

This module provides the `DrumPartialParameter` class, which extends `SynthParameter`
to define the addresses, value ranges, and characteristics of drum partial parameters.
It includes various attributes representing different drum-related parameters, such as
tuning, level, panning, and effects settings.

Classes:
    DrumPartialParameter -- Represents a drum partial parameter with its address,
                            value range, and optional digital range.

Attributes:
    DRUM_GROUP_MAP -- Mapping of drum groups.
    DRUM_ADDRESS_MAP -- Mapping of parameter names to MIDI addresses.

Example usage:
    drum_param = DrumPartialParameter(0x0F, 0, 127)
    print(drum_param.address)  # Output: 0x0F
    print(drum_param.min_val)  # Output: 0
    print(drum_param.max_val)  # Output: 127
"""

from typing import Optional, Tuple

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.data.parameter.digital.mapping import ENVELOPE_MAPPING
from jdxi_editor.midi.data.parameter.drum.addresses import (
    DRUM_ADDRESS_MAP,
    DRUM_GROUP_MAP,
)
from jdxi_editor.midi.parameter.spec import ParameterSpec


class DrumPartialParam(AddressParameter):
    """Drum kit parameters with their addresses and value ranges"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = "",
        display_name: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip if tooltip else ""
        self._display_name = display_name
        self.bipolar_parameters = [
            "PARTIAL_FINE_TUNE",
            "PITCH_ENV_DEPTH",
            "PARTIAL_PAN",
            "PARTIAL_ALTERNATE_PAN_DEPTH",
            "TVA_ENV_TIME_1_VELOCITY_SENS",
            "TVA_ENV_TIME_4_VELOCITY_SENS",
            "TVF_CUTOFF_VELOCITY_SENS",
            "TVF_ENV_DEPTH",
            "TVF_ENV_VELOCITY_SENS",
            "TVF_ENV_TIME_1_VELOCITY_SENS",
            "TVF_ENV_TIME_4_VELOCITY_SENS",
            "WMT1_WAVE_COARSE_TUNE",
            "WMT1_WAVE_FINE_TUNE",
            "WMT1_WAVE_PAN",
            "WMT2_WAVE_COARSE_TUNE",
            "WMT2_WAVE_FINE_TUNE",
            "WMT2_WAVE_PAN",
            "WMT3_WAVE_COARSE_TUNE",
            "WMT3_WAVE_FINE_TUNE",
            "WMT3_WAVE_PAN",
            "WMT4_WAVE_COARSE_TUNE",
            "WMT4_WAVE_FINE_TUNE",
            "WMT4_WAVE_PAN",
        ]
        self.CONVERSION_OFFSETS = {
            # Partials
            "PARTIAL_FINE_TUNE": 64,
            "PARTIAL_PAN": 64,
            "PARTIAL_ALTERNATE_PAN_DEPTH": 64,
            # WMT1
            "WMT1_WAVE_COARSE_TUNE": 64,
            "WMT1_WAVE_FINE_TUNE": 64,
            "WMT1_WAVE_PAN": 64,
            # WMT2
            "WMT2_WAVE_COARSE_TUNE": 64,
            "WMT2_WAVE_FINE_TUNE": 64,
            "WMT2_WAVE_PAN": 64,
            # WMT3
            "WMT3_WAVE_COARSE_TUNE": 64,
            "WMT3_WAVE_FINE_TUNE": 64,
            "WMT3_WAVE_PAN": 64,
            # WMT4
            "WMT4_WAVE_COARSE_TUNE": 64,
            "WMT4_WAVE_FINE_TUNE": 64,
            "WMT4_WAVE_PAN": 64,
            # Pitch ENV
            "PITCH_ENV_DEPTH": 64,
            "PITCH_ENV_VELOCITY_SENS": 64,
            "PITCH_ENV_TIME_1_VELOCITY_SENS": 64,
            "PITCH_ENV_TIME_4_VELOCITY_SENS": 64,
            "PITCH_ENV_LEVEL_0": 64,
            "PITCH_ENV_LEVEL_1": 64,
            "PITCH_ENV_LEVEL_2": 64,
            "PITCH_ENV_LEVEL_3": 64,
            "PITCH_ENV_LEVEL_4": 64,
            # TVF
            "TVF_CUTOFF_VELOCITY_SENS": 64,
            "TVF_RESONANCE_VELOCITY_SENS": 64,
            "TVF_ENV_DEPTH": 64,
            "TVF_ENV_VELOCITY_SENS": 64,
            "TVF_ENV_TIME_1_VELOCITY_SENS": 64,
            "TVF_ENV_TIME_4_VELOCITY_SENS": 64,
            # TVA
            "TVA_LEVEL_VELOCITY_SENS": 64,
            "TVA_ENV_TIME_1_VELOCITY_SENS": 64,
            "TVA_ENV_TIME_4_VELOCITY_SENS": 64,
            "RELATIVE_LEVEL": 64,
        }

    # Partial Name parameters
    PARTIAL_NAME_1 = ParameterSpec(0x00, 32, 127)
    PARTIAL_NAME_2 = ParameterSpec(0x01, 32, 127)
    PARTIAL_NAME_3 = ParameterSpec(0x02, 32, 127)
    PARTIAL_NAME_4 = ParameterSpec(0x03, 32, 127)
    PARTIAL_NAME_5 = ParameterSpec(0x04, 32, 127)
    PARTIAL_NAME_6 = ParameterSpec(0x05, 32, 127)
    PARTIAL_NAME_7 = ParameterSpec(0x06, 32, 127)
    PARTIAL_NAME_8 = ParameterSpec(0x07, 32, 127)
    PARTIAL_NAME_9 = ParameterSpec(0x08, 32, 127)
    PARTIAL_NAME_10 = ParameterSpec(0x09, 32, 127)
    PARTIAL_NAME_11 = ParameterSpec(0x0A, 32, 127)
    PARTIAL_NAME_12 = ParameterSpec(0x0B, 32, 127)

    # Assign Type
    ASSIGN_TYPE = ParameterSpec(
        0x0C,
        0,
        1,
        0,
        1,
        "Assign Type sets the way sounds are played when the same key is pressed a number of times.\nMULTI: Layer the sound of the same keys. Even with continuous sounds where the sound plays\nfor an extended time, such as with crash cymbals, the sounds are layered, without previously\nplayed sounds being eliminated.\nSINGLE: Only one sound can be played at a time when the same key is pressed. With continuous\nsounds where the sound plays for an extended time, the previous sound is stopped when the\nfollowing sound is played.",
    )  # MULTI, SINGLE

    # Mute Group
    MUTE_GROUP = ParameterSpec(
        0x0D,
        0,
        31,
        0,
        31,
        "On an actual acoustic drum set, an open hi-hat and a closed hi-hat sound can never occur\nsimultaneously.\n\nTo reproduce the reality of this situation, you can set up a Mute Group.\nThe Mute Group function allows you to designate two or more drum partials that are not allowed\nto sound simultaneously. Up to 31 Mute Groups can be used.\nDrum partials that does not belong to any such group should be set to “OFF.”",
    )  # OFF, 1 - 31

    # Partial Level
    PARTIAL_LEVEL = ParameterSpec(
        0x0E,
        0,
        127,
        0,
        127,
        "Sets the volume of the waveform.\nMEMO\nThe volume of each drum partial is specified by TVA Level (p. 24), and the overall volume of\nthe entire drum kit is specified by COMMON Kit Level (p. 20).",
    )

    # Partial Coarse Tune
    PARTIAL_COARSE_TUNE = ParameterSpec(
        0x0F,
        0,
        127,
        0,
        127,
        "Adjusts the pitch of the waveform’s sound up or down in semitone steps (+/- 4 octaves).\nMEMO\nThe overall coarse tuning for all of the drum partials is specified by PITCH Coarse Tune (p. 22).",
    )  # C-1 - G9

    # Partial Fine Tune
    PARTIAL_FINE_TUNE = ParameterSpec(
        0x10,
        14,
        114,
        -50,
        50,
        "Adjusts the pitch of the waveform’s sound up or down in 1-cent steps (+/-50 cents).\n* One cent is 1/100th of a semitone.\nMEMO\nThe overall fine tuning for all of the drum partials is specified by PITCH Fine Tune (p. 22 of maanual).",
    )  # -50 - +50

    # Partial Random Pitch Depth
    PARTIAL_RANDOM_PITCH_DEPTH = ParameterSpec(
        0x11,
        0,
        30,
        0,
        30,
        "Specifies the width of random pitch deviation that will occur each time a key is pressed. If you do\nnot want the pitch to change randomly, set this to “0.” These values are in units of cents (1/100th\n of a semitone).",
    )

    # Partial Pan
    PARTIAL_PAN = ParameterSpec(
        0x12,
        0,
        127,
        -64,
        63,
        "Sets the pan for the drum partial. “L64” is far left, “0” is center, and “63R” is far right.\nMEMO\nUse the Wave Pan parameter (p. 21 f the Manual) to specify the panning of the waveforms that make up\nthe drum partial.",
    )  # L64 - 63R

    # Partial Random Pan Depth
    PARTIAL_RANDOM_PAN_DEPTH = ParameterSpec(
        0x13,
        0,
        63,
        0,
        63,
        "When a loop waveform is selected, the sound will normally continue as long as the key is\npressed. If you want the sound to decay naturally even if the key remains pressed, set this to\nNO-SUS.\n* If a one-shot type Wave is selected, it will not sustain even if this parameter is set to\nSUSTAIN.",
    )

    # Partial Alternate Pan Depth
    PARTIAL_ALTERNATE_PAN_DEPTH = ParameterSpec(
        0x14,
        1,
        127,
        -63,
        63,
        "Use this parameter when you want the stereo location to change randomly each time you press\na key.\nHigher settings will produce a greater amount of change.\nNOTE\nThis applies only to waves whose Wave Random Pan Sw parameter (p. 21) is ON.",
    )  # L63 - 63R

    # Partial Env Mode
    PARTIAL_ENV_MODE = ParameterSpec(
        0x15,
        0,
        1,
        "Partial Env Mode: When a loop waveform is selected, the sound will normally continue as long as the key is pressed. If you want the sound to decay naturally even if the key remains pressed, set this to\nNO-SUS.\nMEMO\n* If a one-shot type Wave is selected, it will not sustain even if this parameter is set to“SUSTAIN.” NO-SUS, SUSTAIN",
    )  # NO-SUS, SUSTAIN

    # Partial Output Level
    PARTIAL_OUTPUT_LEVEL = ParameterSpec(
        0x16,
        0,
        127,
        0,
        127,
        "Specifies the signal level of each partial.\nMEMO\nThe overall output level of the entire drum kit is specified by COMMON Kit Level (p. 20 of the manual).",
    )

    # Partial Chorus Send Level
    PARTIAL_CHORUS_SEND_LEVEL = ParameterSpec(
        0x19,
        0,
        127,
        0,
        127,
        "Specifies the level of the signal sent to the chorus for each partial.",
    )

    # Partial Reverb Send Level
    PARTIAL_REVERB_SEND_LEVEL = ParameterSpec(
        0x1A,
        0,
        127,
        0,
        127,
        "Specifies the level of the signal sent to the reverb for each partial.",
    )

    # Partial Output Assign
    PARTIAL_OUTPUT_ASSIGN = ParameterSpec(
        0x1B,
        0,
        4,
        0,
        4,
        "Specifies how the sound of each partial will be output. (EFX1, EFX2, DLY, REV, DIR)",
    )  # EFX1, EFX2, DLY, REV, DIR

    # Partial Pitch Bend Range
    PARTIAL_PITCH_BEND_RANGE = ParameterSpec(
        0x1C,
        0,
        48,
        0,
        48,
        "Specifies the amount of pitch change in semitones (4 octaves) that will occur when the Pitch\nBend Lever is moved. The amount of change when the lever is tilted is set to the same value for\n both left and right sides",
    )

    # Partial Receive Expression
    PARTIAL_RECEIVE_EXPRESSION = ParameterSpec(
        0x1D,
        0,
        1,
        0,
        1,
        "For each drum partial, specify whether MIDI Expression messages will be received (ON), or not\n(OFF).",
    )  # OFF, ON

    # Partial Receive Hold-1
    PARTIAL_RECEIVE_HOLD_1 = ParameterSpec(
        0x1E,
        0,
        1,
        0,
        1,
        "For each drum partial, specify whether MIDI Hold-1 messages will be received (ON), or not (OFF).\nNOTE\nThis has no effect if the Env Mode parameter is set to “NO-SUS.”",
    )  # OFF, ON

    # WMT Velocity Control
    WMT_VELOCITY_CONTROL = ParameterSpec(
        0x20,
        0,
        2,
        0,
        2,
        "WMT Velocity Control determines whether a different drum partial is played (ON) or not (OFF)\ndepending on the force with which the key is played (velocity).\nWhen set to “RANDOM,” the drum kit’s constituent drum partials will sound randomly,\n\nregardless of any Velocity messages.",
    )  # OFF, ON, RANDOM

    # WMT1 Wave Switch
    WMT1_WAVE_SWITCH = ParameterSpec(
        0x21,
        0,
        1,
        0,
        1,
        "When a loop waveform is selected, the sound will normally continue as long as the key is pressed. If you want the sound to decay naturally even if the key remains pressed, set this to\nNO-SUS.\nMEMO\n* If a one-shot type Wave is selected, it will not sustain even if this parameter is set to“SUSTAIN.” NO-SUS, SUSTAIN",
    )  # OFF, ON

    # WMT1 Wave Group Type
    WMT1_WAVE_GROUP_TYPE = ParameterSpec(
        0x22,
        0,
        0,
        0,
        0,
        "Only one preset_type",
    )  # Only one preset_type

    # WMT1 Wave Group ID
    WMT1_WAVE_GROUP_ID = ParameterSpec(
        0x23, 0, 16384, 0, 16384, "OFF, 1 - 16384"
    )  # OFF, 1 - 16384

    # WMT1 Wave Number L (Mono)
    WMT1_WAVE_NUMBER_L = ParameterSpec(
        0x27,
        0,
        16384,
        0,
        16384,
        "Selects the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT1 Wave Number R
    WMT1_WAVE_NUMBER_R = ParameterSpec(
        0x2B,
        0,
        16384,
        0,
        16384,
        "Selects the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT1 Wave Gain
    WMT1_WAVE_GAIN = ParameterSpec(
        0x2F,
        0,
        3,
        0,
        3,
        "Sets the gain (amplitude) of the waveform. The value will change in 6 dB (decibel) steps.\nEach 6 dB increase doubles the gain. The gain is specified in decibels (dB).",
    )  # -6, 0, +6, +12 [dB]

    # WMT1 Wave FXM Switch
    WMT1_WAVE_FXM_SWITCH = ParameterSpec(0x30, 0, 1, 0, 1, "OFF, ON")  # OFF, ON

    # WMT1 Wave FXM Color
    WMT1_WAVE_FXM_COLOR = ParameterSpec(
        0x31,
        0,
        3,
        1,
        4,
        "Specifies how FXM will perform frequency modulation.\nHigher settings result in a grainier sound, while lower settings result in a more metallic sound.\nValues: 1 - 4",
    )  # 1 - 4

    # WMT1 Wave FXM Depth
    WMT1_WAVE_FXM_DEPTH = ParameterSpec(
        0x32,
        0,
        16,
        0,
        16,
        "Specifies the depth of the modulation produced by FXM.\nNOTE\nIf Wave Tempo Sync is “ON,” pitch-related settings (p. 22) and FMX-related settings have no\neffect.\nValues: 0 - 16",
    )  # 0 - 16

    # WMT1 Wave Tempo Sync
    WMT1_WAVE_TEMPO_SYNC = ParameterSpec(
        0x33,
        0,
        1,
        0,
        1,
        "This setting causes the pitch of the waveform to be adjusted in response to the tempo of the song.\nWhen this is set to “ON,” the pitch of the waveform will be adjusted in response to the tempo of the song.\nWhen this is set to “OFF,” the pitch of the waveform will not be adjusted in response to the tempo of the song.",
    )  # OFF, ON

    # WMT1 Wave Coarse Tune
    WMT1_WAVE_COARSE_TUNE = ParameterSpec(
        0x34,
        16,
        112,
        -48,
        48,
        "Adjusts the pitch of the waveform’s sound up or down in semitone steps (+/- 4 octaves).\nMEMO\nThe overall coarse tuning for all of the drum partials is specified by PITCH Coarse Tune (p. 22).",
    )  # -48 - +48

    # WMT1 Wave Fine Tune
    WMT1_WAVE_FINE_TUNE = ParameterSpec(
        0x35,
        14,
        114,
        -50,
        50,
        "Adjusts the pitch of the waveform’s sound up or down in 1/100th of a semitone steps (+/- 50 cents).\nMEMO\nThe overall fine tuning for all of the drum partials is specified by PITCH Fine Tune (p. 22).",
    )  # -50 - +50

    # WMT1 Wave Pan
    WMT1_WAVE_PAN = ParameterSpec(
        0x36,
        0,
        127,
        -64,
        63,
        "Sets the pan for the drum partial. “L64” is far left, “0” is center, and “63R” is far right.\nMEMO\nUse the Wave Pan parameter (p. 21 f the Manual) to specify the panning of the waveforms that make up\nthe drum partial.",
    )  # L64 - 63R

    # WMT1 Wave Random Pan Switch
    WMT1_WAVE_RANDOM_PAN_SWITCH = ParameterSpec(
        0x37,
        0,
        1,
        0,
        1,
        "Use this setting to cause the waveform’s panning to change randomly each time a key is pressed\n(ON) or not (OFF).\n* To specify the range in which pan is changed, edit Random Pan Depth (p. 24).",
    )  # OFF, ON

    # WMT1 Wave Alternate Pan Switch
    WMT1_WAVE_ALTERNATE_PAN_SWITCH = ParameterSpec(
        0x38,
        0,
        2,
        0,
        2,
        "This setting causes panning of the waveform to be alternated between left and right each time a\nkey is pressed.\nSet Alter Pan Sw to “ON” to pan the Wave according to the Alter Pan Depth settings, or to\n“REVS” when you want the panning reversed.\nIf you do not want the panning to change each time a key is pressed, set this to “OFF.”",
    )  # OFF, ON, REVERSE

    # WMT1 Wave Level
    WMT1_WAVE_LEVEL = ParameterSpec(
        0x39,
        0,
        127,
        0,
        127,
        "Sets the volume of the waveform.\nMEMO\nThe volume of each drum partial is specified by TVA Level (p. 24), and the overall volume of\nthe entire drum kit is specified by COMMON Kit Level (p. 20).\nValues: 0 - 127",
    )  # 0 - 127

    # WMT1 Velocity Range Lower
    WMT1_VELOCITY_RANGE_LOWER = ParameterSpec(
        0x3A,
        1,
        127,
        1,
        127,
        "Sets the lowest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.\nNOTE\nIf you attempt to set the lower key velocity above the higher, or the higher key velocity\nbelow the lower, the other setting changes in tandem.",
    )  # 1 - UPPER

    # WMT1 Velocity Range Upper
    WMT1_VELOCITY_RANGE_UPPER = ParameterSpec(
        0x3B,
        1,
        127,
        1,
        127,
        "Sets the highest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.",
    )  # LOWER - 127

    # WMT1 Velocity Fade Width Lower
    WMT1_VELOCITY_FADE_WIDTH_LOWER = ParameterSpec(
        0x3C,
        0,
        127,
        0,
        127,
        "Determines what will happen to the tone’s level when the tone is played at a velocity lower than\nits specified velocity range. Higher settings produce a more gradual change in volume. If you\nwant notes played outside the specified key velocity range to not be sounded at all, set this to 0",
    )
    # WMT1 Velocity Fade Width Upper
    WMT1_VELOCITY_FADE_WIDTH_UPPER = ParameterSpec(
        0x3D,
        0,
        127,
        0,
        127,
        "This determines what will happen to the tone’s level when the tone is played at a velocity greater\nthan its specified velocity range.\nHigher settings produce a more gradual change in volume.\nIf you want notes played outside the specified key velocity range to not be sounded at all, set\nthis to 0",
    )

    # WMT2 Wave Switch
    WMT2_WAVE_SWITCH = ParameterSpec(
        0x3E,
        0,
        1,
        0,
        1,
        "When a loop waveform is selected, the sound will normally continue as long as the key is pressed. If you want the sound to decay naturally even if the key remains pressed, set this to\nNO-SUS.\nMEMO\n* If a one-shot type Wave is selected, it will not sustain even if this parameter is set to“SUSTAIN.” NO-SUS, SUSTAIN",
    )  # OFF, ON

    # WMT2 Wave Group Type
    WMT2_WAVE_GROUP_TYPE = ParameterSpec(
        0x3F,
        0,
        0,
        0,
        0,
        "Selects the Wave Group that contains the Wave to be used for the drum partial. The Wave Group ID is displayed at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # Only one preset_type

    # WMT2 Wave Group ID
    WMT2_WAVE_GROUP_ID = ParameterSpec(
        0x40,
        0,
        16384,
        0,
        16384,
        "Selects the Wave Group that contains the Wave to be used for the drum partial. The Wave Group ID is displayed at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT2 Wave Number L (Mono)
    WMT2_WAVE_NUMBER_L = ParameterSpec(
        0x44,
        0,
        16384,
        0,
        16384,
        "Selects the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT2 Wave Number R
    WMT2_WAVE_NUMBER_R = ParameterSpec(
        0x48,
        0,
        16384,
        0,
        16384,
        "Selects the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT2 Wave Gain
    WMT2_WAVE_GAIN = ParameterSpec(
        0x4C,
        0,
        3,
        0,
        3,
        "Sets the gain (amplitude) of the waveform. The value will change in 6 dB (decibel) steps.\nEach 6 dB increase doubles the gain. The gain is specified in decibels (dB).",
    )  # -6, 0, +6, +12 [dB]

    # WMT2 Wave FXM Switch
    WMT2_WAVE_FXM_SWITCH = ParameterSpec(
        0x4D,
        0,
        1,
        0,
        1,
        "Frequency Cross-Modulation (FXM),OFF, ON",
    )  # OFF, ON

    # WMT2 Wave FXM Color
    WMT2_WAVE_FXM_COLOR = ParameterSpec(
        0x4E,
        0,
        3,
        1,
        4,
        "Specifies how FXM will perform frequency modulation.\nHigher settings result in a grainier sound, while lower settings result in a more metallic sound.",
    )  # 1 - 4

    # WMT2 Wave FXM Depth
    WMT2_WAVE_FXM_DEPTH = ParameterSpec(
        0x4F,
        0,
        16,
        0,
        16,
        "Specifies the depth of the modulation produced by FXM.\nNOTE\nIf Wave Tempo Sync is “ON,” pitch-related settings (p. 22) and FMX-related settings have no\neffect.",
    )  # 0 - 16

    # WMT2 Wave Tempo Sync
    WMT2_WAVE_TEMPO_SYNC = ParameterSpec(
        0x50,
        0,
        1,
        0,
        1,
        "This setting causes the pitch of the waveform to be adjusted in response to the tempo of the song.\nWhen this is set to “ON,” the pitch of the waveform will be adjusted in response to the tempo of the song.\nWhen this is set to “OFF,” the pitch of the waveform will not be adjusted in response to the tempo of the song.",
    )  # OFF, ON

    # WMT2 Wave Coarse Tune
    WMT2_WAVE_COARSE_TUNE = ParameterSpec(
        0x51,
        16,
        112,
        -48,
        48,
        "Adjusts the pitch of the waveform’s sound up or down in semitone steps (+/- 4 octaves).\nMEMO\nThe overall coarse tuning for all of the drum partials is specified by PITCH Coarse Tune (p. 22).",
    )  # -48 - +48

    # WMT2 Wave Fine Tune
    WMT2_WAVE_FINE_TUNE = ParameterSpec(
        0x52,
        14,
        114,
        -50,
        50,
        "Adjusts the pitch of the waveform’s sound up or down in 1/100th of a semitone steps (+/- 50 cents).\nMEMO\nThe overall fine tuning for all of the drum partials is specified by PITCH Fine Tune (p. 22).",
    )  # -50 - +50

    # WMT2 Wave Pan
    WMT2_WAVE_PAN = ParameterSpec(
        0x53,
        0,
        127,
        -64,
        63,
        "Sets the pan for the drum partial. “L64” is far left, “0” is center, and “63R” is far right.\nMEMO\nUse the Wave Pan parameter (p. 21 f the Manual) to specify the panning of the waveforms that make up\nthe drum partial.",
    )  # L64 - 63R

    # WMT2 Wave Random Pan Switch
    WMT2_WAVE_RANDOM_PAN_SWITCH = ParameterSpec(
        0x54,
        0,
        1,
        0,
        1,
        "Use this setting to cause the waveform’s panning to change randomly each time a key is pressed\n(ON) or not (OFF).\n* To specify the range in which pan is changed, edit Random Pan Depth (p. 24).",
    )  # OFF, ON

    # WMT2 Wave Alternate Pan Switch
    WMT2_WAVE_ALTERNATE_PAN_SWITCH = ParameterSpec(
        0x55,
        0,
        2,
        0,
        2,
        "This setting causes panning of the waveform to be alternated between left and right each time a\nkey is pressed.\nSet Alter Pan Sw to “ON” to pan the Wave according to the Alter Pan Depth settings, or to\n“REVS” when you want the panning reversed.\nIf you do not want the panning to change each time a key is pressed, set this to “OFF.”",
    )  # OFF, ON, REVERSE

    # WMT2 Wave Level
    WMT2_WAVE_LEVEL = ParameterSpec(
        0x56,
        0,
        127,
        0,
        127,
        "Sets the level of the waveform. The value will change in 6 dB (decibel) steps.\nEach 6 dB increase doubles the gain. The gain is specified in decibels (dB).",
    )  # 0 - 127

    # WMT2 Velocity Range Lower
    WMT2_VELOCITY_RANGE_LOWER = ParameterSpec(
        0x57,
        1,
        127,
        1,
        127,
        "Sets the lowest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.\nNOTE\nIf you attempt to set the lower key velocity above the higher, or the higher key velocity\nbelow the lower, the other setting changes in tandem.",
    )  # 1 - UPPER

    # WMT2 Velocity Range Upper
    WMT2_VELOCITY_RANGE_UPPER = ParameterSpec(
        0x58,
        1,
        127,
        1,
        127,
        "Sets the highest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.",
    )  # LOWER - 127

    # WMT2 Velocity Fade Width Lower
    WMT2_VELOCITY_FADE_WIDTH_LOWER = ParameterSpec(
        0x59,
        0,
        127,
        0,
        127,
        "Determines what will happen to the tone’s level when the tone is played at a velocity lower than\nits specified velocity range. Higher settings produce a more gradual change in volume. If you\nwant notes played outside the specified key velocity range to not be sounded at all, set this to 0",
    )

    # WMT2 Velocity Fade Width Upper
    WMT2_VELOCITY_FADE_WIDTH_UPPER = ParameterSpec(
        0x5A,
        0,
        127,
        0,
        127,
        "This determines what will happen to the tone’s level when the tone is played at a velocity greater\nthan its specified velocity range.\nHigher settings produce a more gradual change in volume.\nIf you want notes played outside the specified key velocity range to not be sounded at all, set\nthis to 0",
    )

    # WMT3 Wave Switch
    WMT3_WAVE_SWITCH = ParameterSpec(
        0x5B,
        0,
        1,
        0,
        1,
        "When a loop waveform is selected, the sound will normally continue as long as the key is pressed. If you want the sound to decay naturally even if the key remains pressed, set this to\nNO-SUS.\nMEMO\n* If a one-shot type Wave is selected, it will not sustain even if this parameter is set to“SUSTAIN.” NO-SUS, SUSTAIN",
    )  # OFF, ON

    # WMT3 Wave Group Type
    WMT3_WAVE_GROUP_TYPE = ParameterSpec(
        0x5C,
        0,
        0,
        0,
        0,
        "Selects the Wave Group that contains the Wave to be used for the drum partial. The Wave Group ID is displayed at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # Only one preset_type

    # WMT3 Wave Group ID
    WMT3_WAVE_GROUP_ID = ParameterSpec(
        0x5D,
        0,
        16384,
        0,
        16384,
        "Selects the Wave Group that contains the Wave to be used for the drum partial. The Wave Group ID is displayed at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT3 Wave Number L (Mono)
    WMT3_WAVE_NUMBER_L = ParameterSpec(
        0x61,
        0,
        16384,
        0,
        16384,
        "Specifies the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT3 Wave Number R
    WMT3_WAVE_NUMBER_R = ParameterSpec(
        0x65,
        0,
        16384,
        0,
        16384,
        "Specifies the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT3 Wave Gain
    WMT3_WAVE_GAIN = ParameterSpec(
        0x69,
        0,
        3,
        0,
        3,
        "Sets the gain (amplitude) of the waveform. The value will change in 6 dB (decibel) steps.\nEach 6 dB increase doubles the gain. The gain is specified in decibels (dB).",
    )  # -6, 0, +6, +12 [dB]

    # WMT3 Wave FXM Switch
    WMT3_WAVE_FXM_SWITCH = ParameterSpec(
        0x6A,
        0,
        1,
        0,
        1,
        "Frequency Cross-Modulation (FXM),OFF, ON",
    )  # OFF, ON

    # WMT3 Wave FXM Color
    WMT3_WAVE_FXM_COLOR = ParameterSpec(
        0x6B,
        0,
        3,
        0,
        3,
        "Specifies how FXM will perform frequency modulation.\nHigher settings result in a grainier sound, while lower settings result in a more metallic sound.",
    )  # 1 - 4

    # WMT3 Wave FXM Depth
    WMT3_WAVE_FXM_DEPTH = ParameterSpec(
        0x6C,
        0,
        16,
        0,
        16,
        "Specifies the depth of the modulation produced by FXM.\nNOTE\nIf Wave Tempo Sync is “ON,” pitch-related settings (p. 22) and FMX-related settings have no\neffect.",
    )  # 0 - 16

    # WMT3 Wave Tempo Sync
    WMT3_WAVE_TEMPO_SYNC = ParameterSpec(
        0x6D,
        0,
        1,
        0,
        1,
        "This setting causes the pitch of the waveform to be adjusted in response to the tempo of the song.\nWhen this is set to “ON,” the pitch of the waveform will be adjusted in response to the tempo of the song.\nWhen this is set to “OFF,” the pitch of the waveform will not be adjusted in response to the tempo of the song.",
    )  # OFF, ON

    # WMT3 Wave Coarse Tune
    WMT3_WAVE_COARSE_TUNE = ParameterSpec(
        0x6E,
        16,
        112,
        -48,
        48,
        "Adjusts the pitch of the waveform’s sound up or down in semitone steps (+/- 4 octaves).\nMEMO\nThe overall coarse tuning for all of the drum partials is specified by PITCH Coarse Tune (p. 22).",
    )  # -48 - +48

    # WMT3 Wave Fine Tune
    WMT3_WAVE_FINE_TUNE = ParameterSpec(
        0x6F,
        14,
        114,
        -50,
        50,
        "Adjusts the pitch of the waveform’s sound up or down in 1/100th of a semitone steps (+/- 50 cents).\nMEMO\nThe overall fine tuning for all of the drum partials is specified by PITCH Fine Tune (p. 22).",
    )  # -50 - +50

    # WMT3 Wave Pan
    WMT3_WAVE_PAN = ParameterSpec(
        0x70,
        0,
        127,
        -64,
        64,
        "Sets the pan for the drum partial. “L64” is far left, “0” is center, and “63R” is far right.\nMEMO\nUse the Wave Pan parameter (p. 21 f the Manual) to specify the panning of the waveforms that make up\nthe drum partial.",
    )  # L64 - 63R

    # WMT3 Wave Random Pan Switch
    WMT3_WAVE_RANDOM_PAN_SWITCH = ParameterSpec(
        0x71,
        0,
        1,
        0,
        1,
        "Use this setting to cause the waveform’s panning to change randomly each time a key is pressed\n(ON) or not (OFF).\n* To specify the range in which pan is changed, edit Random Pan Depth (p. 24).",
    )  # OFF, ON

    # WMT3 Wave Alternate Pan Switch
    WMT3_WAVE_ALTERNATE_PAN_SWITCH = ParameterSpec(
        0x72,
        0,
        2,
        0,
        2,
        "This setting causes panning of the waveform to be alternated between left and right each time a\nkey is pressed.\nSet Alter Pan Sw to “ON” to pan the Wave according to the Alter Pan Depth settings, or to\n“REVS” when you want the panning reversed.\nIf you do not want the panning to change each time a key is pressed, set this to “OFF.”",
    )  # OFF, ON, REVERSE

    # WMT3 Wave Level
    WMT3_WAVE_LEVEL = ParameterSpec(
        0x73,
        0,
        127,
        0,
        127,
        "Sets the level of the waveform. The value will change in 6 dB (decibel) steps.\nEach 6 dB increase doubles the gain. The gain is specified in decibels (dB).",
    )  # 0 - 127

    # WMT3 Velocity Range Lower
    WMT3_VELOCITY_RANGE_LOWER = ParameterSpec(
        0x74,
        1,
        127,
        1,
        127,
        "Sets the lowest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.\nNOTE\nIf you attempt to set the lower key velocity above the higher, or the higher key velocity\nbelow the lower, the other setting changes in tandem.",
    )  # 1 - UPPER

    # WMT3 Velocity Range Upper
    WMT3_VELOCITY_RANGE_UPPER = ParameterSpec(
        0x75,
        1,
        127,
        1,
        127,
        "Sets the highest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.",
    )  # LOWER - 127

    # WMT3 Velocity Fade Width Lower
    WMT3_VELOCITY_FADE_WIDTH_LOWER = ParameterSpec(
        0x76,
        0,
        127,
        0,
        127,
        "Determines what will happen to the tone’s level when the tone is played at a velocity lower than\nits specified velocity range. Higher settings produce a more gradual change in volume. If you\nwant notes played outside the specified key velocity range to not be sounded at all, set this to 0",
    )

    # WMT3 Velocity Fade Width Upper
    WMT3_VELOCITY_FADE_WIDTH_UPPER = ParameterSpec(
        0x77,
        0,
        127,
        0,
        127,
        "This determines what will happen to the tone’s level when the tone is played at a velocity greater\nthan its specified velocity range.\nHigher settings produce a more gradual change in volume.\nIf you want notes played outside the specified key velocity range to not be sounded at all, set\nthis to 0",
    )

    # WMT4 Wave Switch
    WMT4_WAVE_SWITCH = ParameterSpec(
        0x78,
        0,
        1,
        0,
        1,
        "When a loop waveform is selected, the sound will normally continue as long as the key is pressed. If you want the sound to decay naturally even if the key remains pressed, set this to\nNO-SUS.\nMEMO\n* If a one-shot type Wave is selected, it will not sustain even if this parameter is set to“SUSTAIN.” NO-SUS, SUSTAIN",
    )  # OFF, ON

    # WMT4 Wave Group Type
    WMT4_WAVE_GROUP_TYPE = ParameterSpec(
        0x79,
        0,
        0,
        0,
        0,
        "Selects the Wave Group that contains the Wave to be used for the drum partial. The Wave Group ID is displayed at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # Only one preset_type

    # WMT4 Wave Group ID
    WMT4_WAVE_GROUP_ID = ParameterSpec(
        0x7A,
        0,
        16384,
        0,
        16384,
        "Selects the Wave Group that contains the Wave to be used for the drum partial. The Wave Group ID is displayed at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT4 Wave Number L (Mono)
    WMT4_WAVE_NUMBER_L = ParameterSpec(
        0x7E,
        0,
        16384,
        0,
        16384,
        "Specifies the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT4 Wave Number R
    WMT4_WAVE_NUMBER_R = ParameterSpec(
        0x102,
        0,
        16384,
        0,
        16384,
        "Specifies the Waves comprising the drum partial. Along with the Wave number, the Wave name\nappears at the lower part of the digital.\nWhen in monaural mode, only the left side (L) is specified. When in stereo, the right side (R) is also\nNo.R specified.",
    )  # OFF, 1 - 16384

    # WMT4 Wave Gain
    WMT4_WAVE_GAIN = ParameterSpec(
        0x106,
        0,
        3,
        0,
        3,
        "Sets the gain (amplitude) of the waveform. The value will change in 6 dB (decibel) steps.\nEach 6 dB increase doubles the gain. The gain is specified in decibels (dB).",
    )  # -6, 0, +6, +12 [dB]

    # WMT4 Wave FXM Switch
    WMT4_WAVE_FXM_SWITCH = ParameterSpec(
        0x107,
        0,
        1,
        0,
        1,
        "Sets whether FXM will be used (ON) or not (OFF).\nFXM\nFXM (Frequency Cross Modulation) uses a specified waveform to apply frequency\nmodulation to the currently selected waveform, creating complex overtones. This is useful for\ncreating dramatic sounds or sound effects.",
    )  # OFF, ON

    # WMT4 Wave FXM Color
    WMT4_WAVE_FXM_COLOR = ParameterSpec(
        0x108,
        0,
        3,
        0,
        3,
        "Specifies how FXM will perform frequency modulation.\nHigher settings result in a grainier sound, while lower settings result in a more metallic sound.",
    )  # 1 - 4

    # WMT4 Wave FXM Depth
    WMT4_WAVE_FXM_DEPTH = ParameterSpec(
        0x109,
        0,
        16,
        0,
        16,
        "Specifies the depth of the frequency modulation. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.\nNOTE\nIf Wave Tempo Sync is ON, pitch-related settings (p. 22) and FMX-related settings have no effect.",
    )  # 1 - 16

    # WMT4 Wave Tempo Sync
    WMT4_WAVE_TEMPO_SYNC = ParameterSpec(
        0x10A,
        0,
        1,
        0,
        1,
        "This setting causes the pitch of the waveform to be adjusted in response to the tempo of the song.\nWhen this is set to “ON,” the pitch of the waveform will be adjusted in response to the tempo of the song.\nWhen this is set to “OFF,” the pitch of the waveform will not be adjusted in response to the tempo of the song.",
    )  # OFF, ON

    # WMT4 Wave Coarse Tune
    WMT4_WAVE_COARSE_TUNE = ParameterSpec(
        0x10B,
        16,
        112,
        -48,
        48,
        "Selects the pitch at which a drum partial sounds.\nNOTE\nThe coarse tune of the waveforms that make up the drum partial is specified by the Wave Coarse Tune parameter (p. 21). C-1–G9",
    )  # -48 - +48

    # WMT4 Wave Fine Tune
    WMT4_WAVE_FINE_TUNE = ParameterSpec(
        0x10C,
        14,
        114,
        -50,
        50,
        "Fine Tune\nAdjusts the pitch of the drum partial’s sound up or down in 1-cent steps (+/-50 cents).\n* One cent is 1/100th of a semitone.\nMEMO\nThe fine tune of the waveforms that make up the drum partial is specified by the Wave Fine Tune parameter (p. 21).",
    )  # -50 - +50

    # WMT4 Wave Pan
    WMT4_WAVE_PAN = ParameterSpec(
        0x10D,
        0,
        127,
        -64,
        64,
        "Pan\nLeft: -64, Center: 0, Right: +64",
    )  # L64 - 63R

    # WMT4 Wave Random Pan Switch
    WMT4_WAVE_RANDOM_PAN_SWITCH = ParameterSpec(
        0x10E,
        0,
        1,
        0,
        1,
        "Use this setting to cause the waveform’s panning to change randomly each time a key is pressed\n(ON) or not (OFF).\n* To specify the range in which pan is changed, edit Random Pan Depth (p. 24).",
    )  # OFF, ON

    # WMT4 Wave Alternate Pan Switch
    WMT4_WAVE_ALTERNATE_PAN_SWITCH = ParameterSpec(
        0x10F,
        0,
        2,
        0,
        2,
        "This setting causes panning of the waveform to be alternated between left and right each time a\nkey is pressed.\nSet Alter Pan Sw to “ON” to pan the Wave according to the Alter Pan Depth settings, or to\n“REVS” when you want the panning reversed.\nIf you do not want the panning to change each time a key is pressed, set this to “OFF.”",
    )  # OFF, ON, REVERSE

    # WMT4 Wave Level
    WMT4_WAVE_LEVEL = ParameterSpec(
        0x110,
        0,
        127,
        0,
        127,
        "Sets the volume of the waveform.\nMEMO\nThe volume of each drum partial is specified by TVA Level (p. 24), and the overall volume of\nthe entire drum kit is specified by COMMON Kit Level (p. 20).",
    )

    # WMT4 Velocity Range Lower
    WMT4_VELOCITY_RANGE_LOWER = ParameterSpec(
        0x111,
        1,
        127,
        1,
        127,
        "Sets the lowest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.\nNOTE\nIf you attempt to set the lower key velocity above the higher, or the higher key velocity\nbelow the lower, the other setting changes in tandem.",
    )  # 1 - UPPER

    # WMT4 Velocity Range Upper
    WMT4_VELOCITY_RANGE_UPPER = ParameterSpec(
        0x112,
        1,
        127,
        1,
        127,
        "Sets the highest velocity at which the waveform will sound. Make these settings when you want\ndifferent waveforms to sound in response to notes played at different strengths.\nNOTE\nIf you attempt to set the lower key velocity above the higher, or the higher key velocity\nbelow the lower, the other setting changes in tandem.",
    )  # LOWER - 127

    # WMT4 Velocity Fade Width Lower
    WMT4_VELOCITY_FADE_WIDTH_LOWER = ParameterSpec(
        0x113,
        0,
        127,
        0,
        127,
        "Determines what will happen to the tone’s level when the tone is played at a velocity lower than\nits specified velocity range. Higher settings produce a more gradual change in volume. If you\nwant notes played outside the specified key velocity range to not be sounded at all, set this to 0",
    )

    # WMT4 Velocity Fade Width Upper
    WMT4_VELOCITY_FADE_WIDTH_UPPER = ParameterSpec(
        0x114,
        0,
        127,
        0,
        127,
        "This determines what will happen to the tone’s level when the tone is played at a velocity greater\nthan its specified velocity range.\nHigher settings produce a more gradual change in volume.\nIf you want notes played outside the specified key velocity range to not be sounded at all, set\nthis to 0",
    )

    # Pitch Env Depth
    PITCH_ENV_DEPTH = ParameterSpec(
        0x115,
        52,
        76,
        -12,
        12,
        "Adjusts the effect of the Pitch Envelope. Higher settings will cause the pitch envelope to produce\ngreater change.\nNegative (“-”) settings invert the shape of the envelope.",
        "Depth",
    )  # -12 - +12

    # Pitch Env Velocity Sens
    PITCH_ENV_VELOCITY_SENS = ParameterSpec(
        0x116,
        1,
        127,
        -63,
        63,
        "Keyboard playing dynamics can be used to control the depth of the pitch envelope.\nSpecify a positive (“+”) setting if you want the pitch envelope to have a greater effect as you play\nthe key more strongly; specify a negative (“-”) setting if you want the pitch envelope to have less\neffect.",
        "V-Sens",
    )  # -63 - +63

    # Pitch Env Time 1 Velocity Sens
    PITCH_ENV_TIME_1_VELOCITY_SENS = ParameterSpec(
        0x117,
        1,
        127,
        -63,
        63,
        "Allows keyboard dynamics to affect the Time 1 of the Pitch envelope.\nSpecify a positive (“+”) setting if you want Time 1 to become faster as you play the key more\nstrongly; specify a negative (“-”) setting if you want Time 1 to become slower.",
        "T1 V-Sens",
    )  # -63 - +63

    # Pitch Env Time 4 Velocity Sens
    PITCH_ENV_TIME_4_VELOCITY_SENS = ParameterSpec(
        0x118,
        1,
        127,
        -63,
        63,
        "Allows keyboard dynamics to affect the Time 4 of the Pitch envelope.\nSpecify a positive (“+”) setting if you want Time 4 to become faster as you play the key more\nstrongly; specify a negative (“-”) setting if you want Time 4 to become slower.",
        "T4 V-Sens",
    )  # -63 - +63

    # Pitch Env Time 1
    PITCH_ENV_TIME_1 = ParameterSpec(
        0x119,
        0,
        127,
        0,
        127,
        "Specify the pitch envelope times (Time 1–Time 4).\nHigher settings will result in a longer time until the next pitch is reached. (For example, Time 2 is\nthe time over which the pitch changes from Level 1 to Level 2.)",
        "Time 1",
    )

    # Pitch Env Time 2
    PITCH_ENV_TIME_2 = ParameterSpec(
        0x11A,
        0,
        127,
        0,
        127,
        "Specify the pitch envelope times (Time 1–Time 4).\nHigher settings will result in a longer time until the next pitch is reached. (For example, Time 2 is\nthe time over which the pitch changes from Level 1 to Level 2.)",
        "Time 2",
    )

    # Pitch Env Time 3
    PITCH_ENV_TIME_3 = ParameterSpec(
        0x11B,
        0,
        127,
        0,
        127,
        "Specify the pitch envelope times (Time 1–Time 4).\nHigher settings will result in a longer time until the next pitch is reached. (For example, Time 2 is\nthe time over which the pitch changes from Level 1 to Level 2.)",
        "Time 3",
    )

    # Pitch Env Time 4
    PITCH_ENV_TIME_4 = ParameterSpec(
        0x11C,
        0,
        127,
        0,
        127,
        "Specify the pitch envelope times (Time 1–Time 4).\nHigher settings will result in a longer time until the next pitch is reached. (For example, Time 2 is\nthe time over which the pitch changes from Level 1 to Level 2.)",
        "Time 4",
    )

    # Pitch Env Level 0
    PITCH_ENV_LEVEL_0 = ParameterSpec(
        0x11D,
        1,
        127,
        -63,
        63,
        "Specify the pitch envelope levels (Level 0–Level 4).\nThese specify the amount of pitch change at each point relative to the standard pitch\n(Pitch screen) specified by coarse tune (and fine tune).\nPositive (“+”) settings make the pitch\nhigher than the standard pitch; negative (“-”) settings make the pitch lower.",
        "Level 0",
    )

    # Pitch Env Level 1
    PITCH_ENV_LEVEL_1 = ParameterSpec(
        0x11E,
        1,
        127,
        -63,
        63,
        "Specify the pitch envelope levels (Level 0–Level 4).\nThese specify the amount of pitch change at each point relative to the standard pitch\n(Pitch screen) specified by coarse tune (and fine tune).\nPositive (“+”) settings make the pitch\nhigher than the standard pitch; negative (“-”) settings make the pitch lower.",
        "Level 1",
    )  # -63 - +63

    # Pitch Env Level 2
    PITCH_ENV_LEVEL_2 = ParameterSpec(
        0x11F,
        1,
        127,
        -63,
        63,
        "Specify the pitch envelope levels (Level 0–Level 4).\nThese specify the amount of pitch change at each point relative to the standard pitch\n(Pitch screen) specified by coarse tune (and fine tune).\nPositive (“+”) settings make the pitch\nhigher than the standard pitch; negative (“-”) settings make the pitch lower.",
        "Level 2",
    )  # -63 - +63

    # Pitch Env Level 3
    PITCH_ENV_LEVEL_3 = ParameterSpec(
        0x120,
        1,
        127,
        -63,
        63,
        "Specify the pitch envelope levels (Level 0–Level 4).\nThese specify the amount of pitch change at each point relative to the standard pitch\n(Pitch screen) specified by coarse tune (and fine tune).\nPositive (“+”) settings make the pitch\nhigher than the standard pitch; negative (“-”) settings make the pitch lower.",
        "Level 3",
    )  # -63 - +63

    # Pitch Env Level 4
    PITCH_ENV_LEVEL_4 = ParameterSpec(
        0x121,
        1,
        127,
        -63,
        63,
        "Specify the pitch envelope levels (Level 0–Level 4).\nThese specify the amount of pitch change at each point relative to the standard pitch\n(Pitch screen) specified by coarse tune (and fine tune).\nPositive (“+”) settings make the pitch\nhigher than the standard pitch; negative (“-”) settings make the pitch lower.",
        "Level 4",
    )  # -63 - +63

    # TVF Filter Type
    TVF_FILTER_TYPE = ParameterSpec(
        0x122,
        0,
        6,
        0,
        6,
        "Selects the type of filter. A filter cuts or boosts a specific frequency region to change a sound’s\nbrightness, thickness, or other qualities.\nOFF: The filter is not used.\nLPF: Low Pass Filter. Cuts the portion that is above the cutoff frequency. By cutting the highfrequency\nportion, this gives the sound a milder character. This is the most common filter\nused in synthesizers.\nBPF: Band Pass Filter. This leaves only the frequencies in the region of the cutoff frequency, and cuts the rest. This can be useful when creating distinctive sounds.\nHPF: High Pass Filter. This cuts the frequencies in the region below the cutoff frequency. This is suitable for creating percussive sounds emphasizing their higher ones.\nPKG: Peaking Filter. This emphasizes the frequencies in the region of the cutoff frequency. This represents the “resonance” of a drum.\nLPF2: Low Pass Filter 2. Although frequency components above the cutoff frequency are cut, the sensitivity of this filter is half that of the LPF. This makes it a comparatively warmer low pass filter. This filter is good for use with simulated instrument sounds such as the acoustic piano.\nLPF3: Low Pass Filter 3. Although frequency components above the cutoff frequency are cut, the sensitivity of this filter changes according to the Cutoff frequency. While this filter is also good for use with simulated acoustic instrument sounds, the nuance exhibits\ndiffers from that of the LPF2, even with the same TVF Envelope settings",
    )  # OFF, LPF, BPF, HPF, PKF, LPF2, LPF3

    # TVF Cutoff Frequency
    TVF_CUTOFF_FREQUENCY = ParameterSpec(
        0x123,
        0,
        127,
        0,
        127,
        "Selects the frequency at which the filter begins to have an effect on the waveform’s frequency\ncomponents.\nWith “LPF/LPF2/LPF3” selected for the Filter Type parameter, lower cutoff frequency settings\nreduce a tone’s upper harmonics for a more rounded, warmer sound. Higher settings make it\nsound brighter.\nIf the Filter Type parameter is set to “BPF,” the cutoff frequency setting changes the region of\nharmonics that are allowed to sound. This can be useful when creating distinctive sounds.\nWith “HPF” selected, higher Cutoff Frequency settings will reduce lower harmonics to emphasize\njust the brighter components of the sound.\nWith “PKG” selected, the harmonics to be emphasized will vary depending on Cutoff Frequency\nsetting.",
    )

    # TVF Cutoff Velocity Curve
    TVF_CUTOFF_VELOCITY_CURVE = ParameterSpec(
        0x124,
        0,
        7,
        0,
        7,
        "Selects one of the following seven curves that determine how keyboard playing dynamics\n(velocity) influence the cutoff frequency. Set this to “FIXED” if you don’t want the Cutoff\nfrequency to be affected by the keyboard velocity.",
    )  # FIXED, 1 - 7

    # TVF Cutoff Velocity Sens
    TVF_CUTOFF_VELOCITY_SENS = ParameterSpec(
        0x125,
        1,
        127,
        -63,
        63,
        "Use this parameter when changing the cutoff frequency to be applied as a result of changes in\nplaying velocity.\nSpecify a positive (“+”) setting if you want the cutoff frequency to become higher as you play\nmore strongly; specify a negative (“-”) setting if you want the cutoff frequency to become lower.",
    )  # -63 - +63

    # TVF Resonance
    TVF_RESONANCE = ParameterSpec(
        0x126,
        0,
        127,
        0,
        127,
        "Sets the resonance of the filter. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
    )

    # TVF Resonance Velocity Sens
    TVF_RESONANCE_VELOCITY_SENS = ParameterSpec(
        0x127,
        1,
        127,
        -63,
        63,
        "This allows keyboard velocity to modify the amount of Resonance.\nSpecify a positive (“+”) setting if you want the resonance to increase as you play more strongly;\nspecify a negative (“-”) setting if you want the resonance to decrease.",
    )  # -63 - +63

    # TVF Env Depth
    TVF_ENV_DEPTH = ParameterSpec(
        0x128,
        1,
        127,
        -63,
        63,
        "Sets the depth of the envelope. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
    )  # -63 - +63

    # TVF Env Velocity Curve Type
    TVF_ENV_VELOCITY_CURVE_TYPE = ParameterSpec(
        0x129,
        0,
        7,
        0,
        7,
        "Choose one of the following seven curves to specify how the volume of the drum partial changes\nin response to your keyboard playing dynamics.\nIf you don’t want the volume of the drum partial to change in response to your keyboard\ndynamics, choose the “FIXED” setting.",
    )  # FIXED, 1 - 7

    # TVF Env Velocity Sens
    TVF_ENV_VELOCITY_SENS = ParameterSpec(
        0x137,
        1,
        127,
        -63,
        63,
        "Sets the sensitivity of the envelope to velocity. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
    )  # -63 - +63

    # TVF Env Time 1 Velocity Sens
    TVF_ENV_TIME_1_VELOCITY_SENS = ParameterSpec(
        0x12B,
        1,
        127,
        -63,
        63,
        "Sets the sensitivity of the envelope to velocity. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
    )  # -63 - +63

    # TVF Env Time 4 Velocity Sens
    TVF_ENV_TIME_4_VELOCITY_SENS = ParameterSpec(
        0x12C,
        1,
        127,
        -63,
        63,
        "Sets the sensitivity of the envelope to velocity. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
    )  # -63 - +63

    # TVF Env Time 1
    TVF_ENV_TIME_1 = ParameterSpec(
        0x12D,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext cutoff frequency level is reached. (For example, Time 2 is the time over which Level 1 will\nchange to Level 2.)",
    )

    # TVF Env Time 2
    TVF_ENV_TIME_2 = ParameterSpec(
        0x12E,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext cutoff frequency level is reached. (For example, Time 2 is the time over which Level 1 will\nchange to Level 2.)",
    )

    # TVF Env Time 3
    TVF_ENV_TIME_3 = ParameterSpec(
        0x12F,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext cutoff frequency level is reached. (For example, Time 2 is the time over which Level 1 will\nchange to Level 2.)",
    )

    # TVF Env Time 4
    TVF_ENV_TIME_4 = ParameterSpec(
        0x130,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext cutoff frequency level is reached. (For example, Time 2 is the time over which Level 1 will\nchange to Level 2.)",
    )

    # TVF Env Level 0
    TVF_ENV_LEVEL_0 = ParameterSpec(
        0x131,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope levels (Level 0–Level 4).\nThese settings specify how the cutoff frequency will change at each point, relative to the\nstandard cutoff frequency (the cutoff frequency value specified in the TVF screen).",
    )

    # TVF Env Level 1
    TVF_ENV_LEVEL_1 = ParameterSpec(
        0x132,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope levels (Level 0–Level 4).\nThese settings specify how the cutoff frequency will change at each point, relative to the\nstandard cutoff frequency (the cutoff frequency value specified in the TVF screen).",
    )

    # TVF Env Level 2
    TVF_ENV_LEVEL_2 = ParameterSpec(
        0x133,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope levels (Level 0–Level 4).\nThese settings specify how the cutoff frequency will change at each point, relative to the\nstandard cutoff frequency (the cutoff frequency value specified in the TVF screen).",
    )

    # TVF Env Level 3
    TVF_ENV_LEVEL_3 = ParameterSpec(
        0x134,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope levels (Level 0–Level 4).\nThese settings specify how the cutoff frequency will change at each point, relative to the\nstandard cutoff frequency (the cutoff frequency value specified in the TVF screen).",
    )

    # TVF Env Level 4
    TVF_ENV_LEVEL_4 = ParameterSpec(
        0x135,
        0,
        127,
        0,
        127,
        "Specify the TVF envelope levels (Level 0–Level 4).\nThese settings specify how the cutoff frequency will change at each point, relative to the\nstandard cutoff frequency (the cutoff frequency value specified in the TVF screen).",
    )

    # TVA Level Velocity Curve
    TVA_LEVEL_VELOCITY_CURVE = ParameterSpec(
        0x136,
        0,
        7,
        0,
        7,
        "Choose one of the following seven curves to specify how the volume of the drum partial changes\nin response to your keyboard playing dynamics.\nIf you don’t want the volume of the drum partial to change in response to your keyboard\ndynamics, choose the “FIXED” setting.",
        "Level Velocity Curve",
    )  # FIXED, 1 - 7

    # TVA Level Velocity Sens
    TVA_LEVEL_VELOCITY_SENS = ParameterSpec(
        0x137,
        1,
        127,
        -63,
        63,
        "Set this when you want the volume of the drum partial to change depending on the force with\nwhich you press the keys.\nSpecify a positive (“+”) setting if you want the volume of the drum partial to increase as you play\nmore strongly; specify a negative (“-”) setting if you want the volume to decrease.",
        "Level Velocity Sens",
    )

    # TVA Env Time 1 Velocity Sens
    TVA_ENV_TIME_1_VELOCITY_SENS = ParameterSpec(
        0x138,
        1,
        127,
        -63,
        63,
        "Sets the sensitivity of the envelope to velocity. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
        "Env Time 1 Velocity Sens",
    )  # -63 - +63

    # TVA Env Time 4 Velocity Sens
    TVA_ENV_TIME_4_VELOCITY_SENS = ParameterSpec(
        0x139,
        1,
        127,
        -63,
        63,
        "Sets the sensitivity of the envelope to velocity. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
        "T4 V-Sens",
    )  # -63 - +63

    # TVA Env Time 1
    TVA_ENV_TIME_1 = ParameterSpec(
        0x13A,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext volume level is reached. (For example, Time 2 is the time over which Level 1 will change to\nLevel 2.)",
        "Time 1",
    )

    # TVA Env Time 2
    TVA_ENV_TIME_2 = ParameterSpec(
        0x13B,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext volume level is reached. (For example, Time 2 is the time over which Level 1 will change to\nLevel 2.)",
        "Time 2",
    )

    # TVA Env Time 3
    TVA_ENV_TIME_3 = ParameterSpec(
        0x13C,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext volume level is reached. (For example, Time 2 is the time over which Level 1 will change to\nLevel 2.)",
        "Time 3",
    )

    # TVA Env Time 4
    TVA_ENV_TIME_4 = ParameterSpec(
        0x13D,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope times (Time 1–Time 4).\nHigher settings will lengthen the time until the\nnext volume level is reached. (For example, Time 2 is the time over which Level 1 will change to\nLevel 2.)",
        "Time 4",
    )

    # TVA Env Level 1
    TVA_ENV_LEVEL_1 = ParameterSpec(
        0x13E,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope levels (Level 1–Level 3).\nThese settings specify how the volume will change at each point, relative to the standard volume\n(the Partial Level value specified in the TVA screen).",
        "Level 1",
    )

    # TVA Env Level 2
    TVA_ENV_LEVEL_2 = ParameterSpec(
        0x13F,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope levels (Level 1–Level 3).\nThese settings specify how the volume will change at each point, relative to the standard volume\n(the Partial Level value specified in the TVA screen).",
        "Level 2",
    )

    # TVA Env Level 3
    TVA_ENV_LEVEL_3 = ParameterSpec(
        0x140,
        0,
        127,
        0,
        127,
        "Specify the TVA envelope levels (Level 1–Level 3).\nThese settings specify how the volume will change at each point, relative to the standard volume\n(the Partial Level value specified in the TVA screen).",
        "Level 3",
    )

    # One Shot Mode
    ONE_SHOT_MODE = ParameterSpec(
        0x141,
        0,
        1,
        0,
        1,
        "The sound will play back until the end of the waveform (or the end of the envelope, whichever\ncomes first).\nThe result will be the same as when the envelope’s Env Mode parameter is set to “NO-SUS.”",
        "Level 4",
    )  # OFF, ON

    # Relative Level
    RELATIVE_LEVEL = ParameterSpec(
        0x142,
        0,
        127,
        -64,
        64,
        "Sets the relative level of the drum partial. Higher settings result in a more dramatic effect, while lower settings result in a more subtle effect.",
    )  # -64 - +63

    DRUM_PART = ParameterSpec(
        0x70, 1, 5, 1, 5, "Sets the drum partial. 1 - 5"
    )  # Hack alert @@

    DRUM_GROUP = ParameterSpec(
        0x2F, 1, 5, 1, 5, "Sets the drum group. 1 - 5"
    )  # Hack alert @@

    @property
    def display_name(self) -> str:
        """Get digital name for the parameter (from ParameterSpec or fallback)."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
        return self.name.replace("_", " ").title()

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)
        :param value: int The value
        :return: int The validated value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Ensure value is in valid MIDI range
        if value < 0 or value > 127:
            raise ValueError(
                f"MIDI value {value} out of range for {self.name} (must be 0-127)"
            )

        return value

    def convert_to_midi_old(self, value: int) -> int:
        """
        Convert the value to MIDI range (0-127) for sending via MIDI.

        :param value: int value to convert
        :return: int MIDI value
        """
        if not isinstance(value, int):
            raise ValueError(f"Value must be an integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} (valid range: {self.min_val}-{self.max_val})"
            )

        if self.name in ["PITCH_ENV_DEPTH"]:
            return value + 64

        if self.is_bipolar:
            # Map -max_val..+max_val to 0-127
            return int(((value - self.min_val) / (self.max_val - self.min_val)) * 127)

        return value

    def convert_from_display(self, display_value: int) -> int:
        """Convert from digital value to MIDI value (0-127)
        :param display_value: int The digital value
        :return: int The MIDI value
        """
        if self.name in ["PITCH_ENV_DEPTH"]:
            return display_value + 64
        return display_value

    def get_display_value(self) -> Tuple[int, int]:
        """Get the digital range for the parameter
        :return: Tuple[int, int] The digital range
        """
        return self.display_min, self.display_max

    def get_address_for_partial(self, partial_index: int) -> tuple:
        """Get the address for address drum partial by index
        :param partial_index: int The partial index
        :return: tuple The address
        """
        if not isinstance(partial_index, int):
            raise ValueError(
                f"Partial index must be an integer, got {type(partial_index)}"
            )

        if partial_index < 0 or partial_index >= 72:
            raise ValueError(
                f"[{self.__class__.__name__}] Invalid partial index: {partial_index}"
            )

        address_lmb = DRUM_GROUP_MAP.get(
            partial_index + 1, 0x2E
        )  # Default to 0x2E if partial_name is not 1, 2, or 3
        return address_lmb, 0x00

    @staticmethod
    def get_address_for_partial_name(partial_name: str) -> int:
        """Get parameter area and address adjusted for partial number.
        :param partial_name: str The partial name
        :return: int The address
        """
        address = DRUM_ADDRESS_MAP.get(
            partial_name, 0x00
        )  # Default to 0x00 for common area
        return address

    @staticmethod
    def get_by_name(param_name: str) -> Optional[object]:
        """Get the AnalogParameter by name.
        :param param_name: str The parameter name
        :return: Optional[AddressParameterDrumPartial] The parameter
        Return the parameter member by name, or None if not found
        """
        return DrumPartialParam.__members__.get(param_name, None)

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to digital value
        :param midi_value: int The MIDI value
        :return: int The digital value
        """
        return midi_value

    def get_envelope_param_type(self):
        """
        Returns a envelope_param_type, if the parameter is part of an envelope,
        otherwise returns None.

        :return: Optional[str] The envelope parameter type
        """
        return ENVELOPE_MAPPING.get(self.name)
