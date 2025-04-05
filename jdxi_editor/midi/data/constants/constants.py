from enum import Enum, auto

DRUM_KIT_AREA = 0x1C
MIDI_CHANNEL_DIGITAL1 = 0  # Corresponds to channel 1
MIDI_CHANNEL_DIGITAL2 = 1  # Corresponds to channel 2
MIDI_CHANNEL_ANALOG = 2  # Corresponds to channel 3
MIDI_CHANNEL_DRUMS = 9  # Corresponds to channel 10
MIDI_CHANNEL_PROGRAMS = 15 # Program list
PART_1 = 0x00  # Analog synth address # Are these correct?
PART_2 = 0x01  # Digital synth 1 address
PART_3 = 0x02  # Digital synth 2 address
PART_4 = 0x03  # Drum address
PART_5 = 0x04  # Vocal FX address
ANALOG_PART = PART_1  # 0x00
DIGITAL_1_PART = PART_2  # 0x01
DIGITAL_2_PART = PART_3  # 0x02
DRUM_PART = PART_4  # 0x03
VOCAL_FX_PART = PART_5  # 0x04
SUBGROUP_ZERO = 0x00  # Common parameters
OSC_1_GROUP = 0x20  # Oscillator 1 parameters
OSC_2_GROUP = 0x21  # Oscillator 2 parameters
OSC_COMMON = 0x22  # Common oscillator parameters
OSC_PARAM_GROUP = OSC_1_GROUP  # Legacy name for compatibility
FILTER_GROUP = 0x30  # Filter parameters
AMP_GROUP = 0x31  # Amplifier parameters
LFO_1_GROUP = 0x40  # LFO 1 parameters
LFO_2_GROUP = 0x41  # LFO 2 parameters
ENV_1_GROUP = 0x42  # Envelope 1 parameters
ENV_2_GROUP = 0x43  # Envelope 2 parameters
FX_GROUP = 0x50  # Effects parameters
DELAY_GROUP = 0x51  # Delay parameters
REVERB_GROUP = 0x52  # Reverb parameters
ANALOG_BANK_MSB = 0x5E  # 94 - Analog synth
DIGITAL_BANK_MSB = 0x5F  # 95 - Digital synth
DRUM_BANK_MSB = 0x56  # 86 - Drum kit
PRESET_BANK_LSB = 0x00  # 0 - Preset bank 1
PRESET_BANK_2_LSB = 0x01  # 1 - Preset bank 2 (Digital only)
USER_BANK_LSB = 0x10  # 16 - User bank
BANK_SELECT_MSB = 0x00  # CC 0
BANK_SELECT_LSB = 0x20  # CC 32
PROGRAM_CHANGE = 0xC0  # Program Change
START_OF_SYSEX = 0xF0
END_OF_SYSEX = 0xF7
ROLAND_ID = 0x41
DEVICE_ID = 0x10  # Device ID (dev: 10H - 1FH, 7FH)
MODEL_ID_1 = 0x00  # Manufacturer ID extension
MODEL_ID_2 = 0x00  # Device family code MSB
MODEL_ID_3 = 0x00  # Device family code LSB
MODEL_ID_4 = 0x0E  # Product code
MODEL_ID = [MODEL_ID_1, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4]
JD_XI_HEADER = [
    ROLAND_ID,
    DEVICE_ID,
    MODEL_ID_1,
    MODEL_ID_2,
    MODEL_ID_3,
    MODEL_ID_4,
]  # Complete device ID
RQ1_COMMAND = 0x11  # Data Request 1
DT1_COMMAND = 0x12  # Data Set 1
RQ2_COMMAND = 0x41  # Data Request 2
DT2_COMMAND = 0x42  # Data Set 2
ERR_COMMAND = 0x4E  # Error
ACK_COMMAND = 0x4F  # Acknowledgment
DT1_COMMAND_12 = 0x12  # Data Set 1
RQ1_COMMAND_11 = 0x11  # Data Request 1
ANALOG_FILTER_SWITCH = 0x20  # Filter switch (0-1: BYPASS, LPF)
ANALOG_FILTER_CUTOFF = 0x21  # Filter cutoff frequency (0-127)
ANALOG_FILTER_KEYFOLLOW = 0x22  # Cutoff keyfollow (54-74: -100 to +100)
ANALOG_FILTER_RESONANCE = 0x23  # Filter resonance (0-127)
ANALOG_FILTER_ENV_VELO = 0x24  # Env velocity sens (1-127: -63 to +63)
ANALOG_FILTER_ENV_A = 0x25  # Filter env attack time (0-127)
ANALOG_FILTER_ENV_D = 0x26  # Filter env decay time (0-127)
ANALOG_FILTER_ENV_S = 0x27  # Filter env sustain level (0-127)
ANALOG_FILTER_ENV_R = 0x28  # Filter env release time (0-127)
ANALOG_FILTER_ENV_DEPTH = 0x29  # Filter env depth (1-127: -63 to +63)
FILTER_MODE_BYPASS = 0x00  # Bypass filter
FILTER_MODE_LPF = 0x01  # Low-pass filter
OSC_WAVE_PARAM = 0x00  # Waveform selection
OSC_RANGE_PARAM = 0x01  # Octave range
OSC_COARSE_PARAM = 0x02  # Coarse tune
OSC_FINE_PARAM = 0x03  # Fine tune
OSC_PW_PARAM = 0x04  # Pulse width
OSC_PWM_PARAM = 0x05  # PWM depth
OSC_SYNC_PARAM = 0x06  # Oscillator sync
OSC_RING_PARAM = 0x07  # Ring modulation
OSC_WAVE_SAW = 0x00  # Sawtooth
OSC_WAVE_SQUARE = 0x01  # Square
OSC_WAVE_TRIANGLE = 0x02  # Triangle
OSC_WAVE_SINE = 0x03  # Sine
OSC_WAVE_NOISE = 0x04  # Noise
OSC_WAVE_SUPER_SAW = 0x05  # Super saw
OSC_WAVE_PCM = 0x06  # PCM waveform
WAVE_SAW = OSC_WAVE_SAW  # Sawtooth
WAVE_SQUARE = OSC_WAVE_SQUARE  # Square
WAVE_PULSE = OSC_WAVE_SQUARE  # Pulse (same as square)
WAVE_TRIANGLE = OSC_WAVE_TRIANGLE  # Triangle
WAVE_SINE = OSC_WAVE_SINE  # Sine
WAVE_NOISE = OSC_WAVE_NOISE  # Noise
WAVE_SUPER_SAW = OSC_WAVE_SUPER_SAW  # Super saw
WAVE_PCM = OSC_WAVE_PCM  # PCM waveform
OSC_RANGE_16 = 0x00  # 16'
OSC_RANGE_8 = 0x01  # 8'
OSC_RANGE_4 = 0x02  # 4'
OSC_RANGE_2 = 0x03  # 2'
RANGE_16 = OSC_RANGE_16  # 16'
RANGE_8 = OSC_RANGE_8  # 8'
RANGE_4 = OSC_RANGE_4  # 4'
RANGE_2 = OSC_RANGE_2  # 2'
OSC_COARSE_RANGE = (-24, 24)  # Semitones
OSC_FINE_RANGE = (-50, 50)  # Cents
OSC_PW_RANGE = (0, 127)  # Pulse width
OSC_PWM_RANGE = (0, 127)  # PWM depth
OSC_SYNC_RANGE = (0, 1)  # Off/On
OSC_RING_RANGE = (0, 1)  # Off/On


class DrumKitCC:
    """Drum Kit Control Change parameters"""

    # MSB values for NRPN parameters
    LEVEL_MSB = 0x1A  # Level
    PAN_MSB = 0x1C  # Pan
    TUNE_MSB = 0x1E  # Tune
    DECAY_MSB = 0x20  # Decay
    CUTOFF_MSB = 0x22  # Cutoff Frequency
    RESONANCE_MSB = 0x24  # Resonance
    FX1_SEND_MSB = 0x26  # Effect 1 Send Level
    FX2_SEND_MSB = 0x28  # Effect 2 Send Level
    DELAY_SEND_MSB = 0x2A  # Delay Send Level
    REVERB_SEND_MSB = 0x2C  # Reverb Send Level

    # Value ranges
    LEVEL_RANGE = (0, 127)
    PAN_RANGE = (0, 127)  # 0=Left, 64=Center, 127=Right
    TUNE_RANGE = (0, 127)  # 64=Original pitch
    DECAY_RANGE = (0, 127)
    CUTOFF_RANGE = (0, 127)
    RESONANCE_RANGE = (0, 127)
    SEND_RANGE = (0, 127)

    @staticmethod
    def validate_msb(msb: int) -> bool:
        """Validate MSB value"""
        return msb in [
            DrumKitCC.LEVEL_MSB,
            DrumKitCC.PAN_MSB,
            DrumKitCC.TUNE_MSB,
            DrumKitCC.DECAY_MSB,
            DrumKitCC.CUTOFF_MSB,
            DrumKitCC.RESONANCE_MSB,
            DrumKitCC.FX1_SEND_MSB,
            DrumKitCC.FX2_SEND_MSB,
            DrumKitCC.DELAY_SEND_MSB,
            DrumKitCC.REVERB_SEND_MSB,
        ]

    @staticmethod
    def validate_note(note: int) -> bool:
        """Validate drum note number"""
        return 36 <= note <= 72  # C2 to C5

    @staticmethod
    def validate_value(value: int) -> bool:
        """Validate parameter value"""
        return 0 <= value <= 127


class AnalogToneCC:
    """Analog Synth Control Change parameters"""

    # Common Parameters
    LEVEL_MSB = 0x10  # Level
    PAN_MSB = 0x11  # Pan
    PORTAMENTO_MSB = 0x12  # Portamento time

    # Oscillator Parameters
    OSC_WAVE_MSB = 0x20  # Waveform
    OSC_RANGE_MSB = 0x21  # Octave range
    OSC_COARSE_MSB = 0x22  # Coarse tune
    OSC_FINE_MSB = 0x23  # Fine tune
    OSC_PW_MSB = 0x24  # Pulse width

    # Filter Parameters
    FILT_TYPE_MSB = 0x30  # Filter preset_type
    FILT_CUTOFF_MSB = 0x31  # Cutoff frequency
    FILT_RESO_MSB = 0x32  # Resonance
    FILT_ENV_MSB = 0x33  # Envelope depth
    FILT_KEY_MSB = 0x34  # Key follow

    # Envelope Parameters
    FILT_A_MSB = 0x40  # Filter Attack
    FILT_D_MSB = 0x41  # Filter Decay
    FILT_S_MSB = 0x42  # Filter Sustain
    FILT_R_MSB = 0x43  # Filter Release

    AMP_A_MSB = 0x50  # Amp Attack
    AMP_D_MSB = 0x51  # Amp Decay
    AMP_S_MSB = 0x52  # Amp Sustain
    AMP_R_MSB = 0x53  # Amp Release

    # LFO Parameters
    LFO_WAVE_MSB = 0x60  # LFO Waveform
    LFO_RATE_MSB = 0x61  # LFO Rate
    LFO_DEPTH_MSB = 0x62  # LFO Depth
    LFO_DEST_MSB = 0x63  # LFO Destination

    # Value ranges
    LEVEL_RANGE = (0, 127)
    PAN_RANGE = (0, 127)  # 0=Left, 64=Center, 127=Right
    PORTA_RANGE = (0, 127)
    WAVE_RANGE = (0, 6)  # See OSC_WAVE_* constants
    RANGE_RANGE = (0, 3)  # See OSC_RANGE_* constants
    COARSE_RANGE = (40, 88)  # -24 to +24 semitones
    FINE_RANGE = (14, 114)  # -50 to +50 cents
    PW_RANGE = (0, 127)
    FILTER_RANGE = (0, 127)
    ENV_RANGE = (0, 127)
    LFO_RANGE = (0, 127)

    @staticmethod
    def validate_msb(msb: int) -> bool:
        """Validate MSB value"""
        return msb in [
            AnalogControlChange.LEVEL_MSB,
            AnalogControlChange.PAN_MSB,
            AnalogControlChange.PORTAMENTO_MSB,
            AnalogControlChange.OSC_WAVE_MSB,
            AnalogControlChange.OSC_RANGE_MSB,
            AnalogControlChange.OSC_COARSE_MSB,
            AnalogControlChange.OSC_FINE_MSB,
            AnalogControlChange.OSC_PW_MSB,
            AnalogControlChange.FILT_TYPE_MSB,
            AnalogControlChange.FILT_CUTOFF_MSB,
            AnalogControlChange.FILT_RESO_MSB,
            AnalogControlChange.FILT_ENV_MSB,
            AnalogControlChange.FILT_KEY_MSB,
            AnalogControlChange.FILT_A_MSB,
            AnalogControlChange.FILT_D_MSB,
            AnalogControlChange.FILT_S_MSB,
            AnalogControlChange.FILT_R_MSB,
            AnalogControlChange.AMP_A_MSB,
            AnalogControlChange.AMP_D_MSB,
            AnalogControlChange.AMP_S_MSB,
            AnalogControlChange.AMP_R_MSB,
            AnalogControlChange.LFO_WAVE_MSB,
            AnalogControlChange.LFO_RATE_MSB,
            AnalogControlChange.LFO_DEPTH_MSB,
            AnalogControlChange.LFO_DEST_MSB,
        ]

    @staticmethod
    def validate_value(msb: int, value: int) -> bool:
        """Validate parameter value based on MSB"""
        if msb == AnalogControlChange.OSC_WAVE_MSB:
            return 0 <= value <= 6
        elif msb == AnalogControlChange.OSC_RANGE_MSB:
            return 0 <= value <= 3
        elif msb == AnalogControlChange.OSC_COARSE_MSB:
            return 40 <= value <= 88
        elif msb == AnalogControlChange.OSC_FINE_MSB:
            return 14 <= value <= 114
        else:
            return 0 <= value <= 127


class Waveform(Enum):
    """Waveform types available on the JD-Xi"""

    SAW = auto()  # Sawtooth wave
    SQUARE = auto()  # Square wave
    TRIANGLE = auto()  # Triangle wave
    SINE = auto()  # Sine wave
    NOISE = auto()  # Noise
    SUPER_SAW = auto()  # Super saw
    PCM = auto()  # PCM waveform

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        return self.name.replace("_", " ").title()

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        return {
            Waveform.SAW: OSC_WAVE_SAW,
            Waveform.SQUARE: OSC_WAVE_SQUARE,
            Waveform.TRIANGLE: OSC_WAVE_TRIANGLE,
            Waveform.SINE: OSC_WAVE_SINE,
            Waveform.NOISE: OSC_WAVE_NOISE,
            Waveform.SUPER_SAW: OSC_WAVE_SUPER_SAW,
            Waveform.PCM: OSC_WAVE_PCM,
        }[self]

    @classmethod
    def from_midi_value(cls, value: int) -> "Waveform":
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")


ANALOG_LFO_SYNC_NOTES = [
    "16",  # 0
    "12",  # 1
    "8",  # 2
    "4",  # 3
    "2",  # 4
    "1",  # 5
    "3/4",  # 6
    "2/3",  # 7
    "1/2",  # 8
    "3/8",  # 9
    "1/3",  # 10
    "1/4",  # 11
    "3/16",  # 12
    "1/6",  # 13
    "1/8",  # 14
    "3/32",  # 15
    "1/12",  # 16
    "1/16",  # 17
    "1/24",  # 18
    "1/32",  # 19
]
DIGITAL_SYNTH_1 = 0x19  # 19 00 00 00: Digital Synth Part 1
DIGITAL_SYNTH_2 = 0x19  # 19 20 00 00: Digital Synth Part 2
ANALOG_SYNTH = 0x42  # 19 40 00 00: Analog Synth Part
DRUM_KIT = 0x70  # 19 60 00 00: Drums Part
DIGITAL_PART_1 = 0x01  # Digital Synth 1 offset
DIGITAL_PART_2 = 0x02  # Digital Synth 2 offset
