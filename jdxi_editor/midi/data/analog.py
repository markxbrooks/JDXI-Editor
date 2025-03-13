"""Data structures for JD-Xi Analog Synth parameters"""

from dataclasses import dataclass
from enum import Enum
import logging

from jdxi_editor.midi.data.constants.analog import ANALOG_PART, ANALOG_SYNTH_AREA


# Analog preset categories


@dataclass
class AnalogOscillator:
    """Analog oscillator settings"""

    wave: int = 0  # SAW
    pitch: int = 64  # Center
    fine: int = 64  # Center
    pwm: int = 0


@dataclass
class AnalogFilter:
    """Analog filter settings"""

    type: int = 0  # LPF
    cutoff: int = 127
    resonance: int = 0
    env_depth: int = 64  # Center
    key_follow: int = 0


@dataclass
class AnalogAmplifier:
    """Analog amplifier settings"""

    level: int = 100
    pan: int = 64  # Center


@dataclass
class AnalogLFO:
    """Analog LFO settings"""

    wave: int = 0  # Triangle
    rate: int = 64  # Medium
    depth: int = 0
    random_pitch: int = 0


@dataclass
class AnalogEnvelope:
    """Analog envelope settings"""

    attack: int = 0
    decay: int = 64
    sustain: int = 64
    release: int = 32


@dataclass
class AnalogSynthPatch:
    """Complete analog synth patch data"""

    # Common parameters
    volume: int = 100
    pan: int = 64  # Center
    portamento: int = 0

    # Section parameters
    oscillator: AnalogOscillator = None
    filter: AnalogFilter = None
    amplifier: AnalogAmplifier = None
    lfo: AnalogLFO = None
    envelope: AnalogEnvelope = None

    def __post_init__(self):
        """Initialize section parameters"""
        if self.oscillator is None:
            self.oscillator = AnalogOscillator()
        if self.filter is None:
            self.filter = AnalogFilter()
        if self.amplifier is None:
            self.amplifier = AnalogAmplifier()
        if self.lfo is None:
            self.lfo = AnalogLFO()
        if self.envelope is None:
            self.envelope = AnalogEnvelope()

    def validate_param(self, section: str, param: str, value: int) -> bool:
        """Validate parameter value is in range"""
        ranges = {
            "common": {"volume": (0, 127), "pan": (0, 127), "portamento": (0, 127)},
            "oscillator": {
                "wave": (0, 7),
                "pitch": (0, 127),
                "fine": (0, 127),
                "pwm": (0, 127),
            },
            "filter": {
                "preset_type": (0, 3),
                "cutoff": (0, 127),
                "resonance": (0, 127),
                "env_depth": (0, 127),
                "key_follow": (0, 127),
            },
            "amplifier": {"level": (0, 127), "pan": (0, 127)},
            "lfo": {
                "wave": (0, 5),
                "rate": (0, 127),
                "depth": (0, 127),
                "random_pitch": (0, 127),
            },
            "envelope": {
                "attack": (0, 127),
                "decay": (0, 127),
                "sustain": (0, 127),
                "release": (0, 127),
            },
        }

        if section in ranges and param in ranges[section]:
            min_val, max_val = ranges[section][param]
            return min_val <= value <= max_val
        return False


# Analog synth preset definitions


@dataclass
class AnalogTone:
    """Analog synth tone data and methods"""

    @staticmethod
    def send_init_data(midi_helper):
        """Send initialization data for analog synth parameters

        Args:
            midi_helper: MIDI helper instance for sending messages
        """
        try:
            # Send parameter request messages
            for param_group in [
                (0x00, 0x10),  # Common parameters
                (0x10, 0x10),  # Oscillator parameters
                (0x20, 0x10),  # Filter parameters
                (0x30, 0x10),  # Amplifier parameters
                (0x40, 0x10),  # LFO parameters
            ]:
                start_addr, size = param_group
                midi_helper.send_parameter(
                    area=ANALOG_SYNTH_AREA,
                    part=ANALOG_PART,
                    group=0x00,  # Always 0 for analog synth
                    param=start_addr,
                    value=0,  # Request current value
                )
                logging.debug(
                    f"Requested analog params {start_addr:02X}-{start_addr+size-1:02X}"
                )

        except Exception as e:
            logging.error(f"Error sending analog init data: {str(e)}")

    @staticmethod
    def validate_data_length(data):
        """Validate received data length

        Args:
            data: Received MIDI data

        Returns:
            bool: True if data length is valid
        """
        # Analog synth data should be 64 bytes
        return len(data) == 64

    @staticmethod
    def parse_data(data):
        """Parse received analog synth data

        Args:
            data: Raw MIDI data bytes

        Returns:
            dict: Parsed parameter values
        """
        if not AnalogTone.validate_data_length(data):
            raise ValueError(f"Invalid data length: {len(data)}")

        return {
            "osc_wave": data[ANALOG_OSC_WAVE],
            "osc_coarse": data[ANALOG_OSC_COARSE] - 64,  # Convert to -24/+24
            "osc_fine": data[ANALOG_OSC_FINE] - 64,  # Convert to -50/+50
            "osc_pw": data[ANALOG_OSC_PW],
            "osc_pwm": data[ANALOG_OSC_PWM],
            "osc_penv_velo": data[ANALOG_OSC_PENV_VELO] - 64,  # Convert to -63/+63
            "osc_penv_a": data[ANALOG_OSC_PENV_A],
            "osc_penv_d": data[ANALOG_OSC_PENV_D],
            "osc_penv_depth": data[ANALOG_OSC_PENV_DEPTH] - 64,  # Convert to -63/+63
            "sub_type": data[ANALOG_SUB_TYPE],
            "lfo_shape": data[ANALOG_LFO_SHAPE],
            "lfo_rate": data[ANALOG_LFO_RATE],
            "lfo_fade": data[ANALOG_LFO_FADE],
            "lfo_tempo_sync_switch": data[ANALOG_LFO_SYNC],
            "lfo_sync_note": data[ANALOG_LFO_SYNC_NOTE],
            "lfo_pitch": data[ANALOG_LFO_PITCH] - 64,  # Convert to -63/+63
            "lfo_filter": data[ANALOG_LFO_FILTER] - 64,  # Convert to -63/+63
            "lfo_amp": data[ANALOG_LFO_AMP] - 64,  # Convert to -63/+63
            "lfo_key_trig": data[ANALOG_LFO_KEY_TRIG],
        }


class AnalogCommonParameter(Enum):
    """Common parameters for Digital/SuperNATURAL synth tones.
    These parameters are shared across all partials.
    """

    # LFO Parameters
    LFO_SHAPE = (0x0D, 0, 5)  # TRI, SIN, SAW, SQR, S&H, RND
    LFO_RATE = (0x0E, 0, 127)
    LFO_FADE_TIME = (0x0F, 0, 127)
    LFO_TEMPO_SYNC_SWITCH = (0x10, 0, 1)  # OFF, ON
    LFO_TEMPO_SYNC_NOTE = (0x11, 0, 19)  # 16, 12, 8, 4, 2, 1, 3/4, 2/3, 1/2, etc.
    LFO_PITCH_DEPTH = (0x12, 1, 127)  # -63 to +63
    LFO_FILTER_DEPTH = (0x13, 1, 127)  # -63 to +63
    LFO_AMP_DEPTH = (0x14, 1, 127)  # -63 to +63
    LFO_KEY_TRIGGER = (0x15, 0, 1)  # OFF, ON

    # Oscillator Parameters
    OSC_WAVEFORM = (0x16, 0, 2)  # SAW, TRI, PW-SQR
    OSC_PITCH_COARSE = (0x17, 40, 88)  # -24 to +24
    OSC_PITCH_FINE = (0x18, 14, 114)  # -50 to +50
    OSC_PULSE_WIDTH = (0x19, 0, 127)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x1A, 0, 127)
    OSC_PITCH_ENV_VELOCITY_SENS = (0x1B, 1, 127)  # -63 to +63
    OSC_PITCH_ENV_ATTACK_TIME = (0x1C, 0, 127)
    OSC_PITCH_ENV_DECAY = (0x1D, 0, 127)
    OSC_PITCH_ENV_DEPTH = (0x1E, 1, 127)  # -63 to +63
    SUB_OSCILLATOR_TYPE = (0x1F, 0, 2)  # OFF, OCT-1, OCT-2

    # Filter Parameters
    FILTER_SWITCH = (0x20, 0, 1)  # BYPASS, LPF
    FILTER_CUTOFF = (0x21, 0, 127)
    FILTER_CUTOFF_KEYFOLLOW = (0x22, 54, 74)  # -100 to +100
    FILTER_RESONANCE = (0x23, 0, 127)
    FILTER_ENV_VELOCITY_SENS = (0x24, 1, 127)  # -63 to +63
    FILTER_ENV_ATTACK_TIME = (0x25, 0, 127)
    FILTER_ENV_DECAY_TIME = (0x26, 0, 127)
    FILTER_ENV_SUSTAIN_LEVEL = (0x27, 0, 127)
    FILTER_ENV_RELEASE_TIME = (0x28, 0, 127)
    FILTER_ENV_DEPTH = (0x29, 1, 127)  # -63 to +63

    # Amplifier Parameters
    AMP_LEVEL = (0x15, 0, 127)
    AMP_LEVEL_VELOCITY_SENS = (0x16, 1, 127)  # -63 to +63
    AMP_ENV_ATTACK_TIME = (0x17, 0, 127)
    AMP_ENV_DECAY_TIME = (0x18, 0, 127)
    AMP_ENV_SUSTAIN_LEVEL = (0x19, 0, 127)
    AMP_ENV_RELEASE_TIME = (0x1A, 0, 127)
    AMP_PAN = (0x1B, 1, 127)  # L64 - 63R

    # Portamento and Other Parameters
    PORTAMENTO_SWITCH = (0x31, 0, 1)  # OFF, ON
    PORTAMENTO_TIME = (0x32, 0, 127)  # CC# 5
    LEGATO_SWITCH = (0x33, 0, 1)  # OFF, ON
    OCTAVE_SHIFT = (0x34, 61, 67)  # -3 to +3
    PITCH_BEND_RANGE_UP = (0x35, 0, 24)
    PITCH_BEND_RANGE_DOWN = (0x36, 0, 24)

    # LFO Modulation Control
    LFO_PITCH_MODULATION_CONTROL = (0x38, 1, 127)  # -63 to +63
    LFO_FILTER_MODULATION_CONTROL = (0x39, 1, 127)  # -63 to +63
    LFO_AMP_MODULATION_CONTROL = (0x3A, 1, 127)  # -63 to +63
    LFO_RATE_MODULATION_CONTROL = (0x3B, 1, 127)  # -63 to +63

    # Reserve
    RESERVE_1 = (0x37, 0, 0)  # Reserve
    RESERVE_2 = (0x3C, 0, 0)  # Reserve

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in [
            self.LFO_TEMPO_SYNC_SWITCH,
            self.LFO_KEY_TRIGGER,
            self.PORTAMENTO_SWITCH,
            self.LEGATO_SWITCH,
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value
