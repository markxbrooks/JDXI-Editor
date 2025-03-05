"""
DigitalParameter: JD-Xi Digital Synthesizer Parameter Mapping
=============================================================

This class defines digital synthesizer parameters for the Roland JD-Xi, mapping
various synthesis parameters to their corresponding memory addresses and valid
value ranges.

The parameters include:
- Oscillator settings (waveform, pitch, detune, envelope, etc.)
- Filter settings (cutoff, resonance, envelope, key follow, etc.)
- Amplifier settings (level, velocity, envelope, pan, etc.)
- LFO (Low-Frequency Oscillator) settings (waveform, rate, depth, sync, etc.)
- Modulation LFO settings (waveform, rate, depth, sync, etc.)
- Additional synthesis controls (aftertouch, wave gain, super saw detune, etc.)
- PCM wave settings (wave number, gain, high-pass filter cutoff, etc.)

Each parameter is stored as address tuple containing:
    (memory_address, min_value, max_value)

Attributes:
    - OSC_WAVE: Defines the oscillator waveform preset_type.
    - FILTER_CUTOFF: Controls the filter cutoff frequency.
    - AMP_LEVEL: Sets the overall amplitude level.
    - LFO_RATE: Adjusts the rate of the low-frequency oscillator.
    - MOD_LFO_PITCH_DEPTH: Modulates pitch using the secondary LFO.
    - (Other parameters follow address similar structure.)

Methods:
    __init__(self, address: int, min_val: int, max_val: int):
        Initializes address DigitalParameter instance with an address and value range.

Usage Example:
    filter_cutoff = DigitalParameter(0x0C, 0, 127)  # Filter Cutoff Frequency
    print(filter_cutoff.address)  # Output: 0x0C

This class helps structure and manage parameter mappings for JD-Xi SysEx processing.
"""


import logging
from typing import Tuple, Optional, Union
from enum import Enum
from dataclasses import dataclass
from jdxi_manager.data.parameter.synth import SynthParameter
# from jdxi_manager.ui.widgets.slider import Slider


def parse_digital_parameters(data: list) -> dict:
    """
    Parses JD-Xi tone parameters from SysEx data, including Oscillator, Filter, and Amplifier parameters.

    Args:
        data (bytes): SysEx message containing tone parameters.

    Returns:
        dict: Parsed parameters.
    """

    # Function to safely retrieve values from `data`
    def safe_get(index, default=0):
        tone_name_length = 12
        index = index + tone_name_length # shift the index by 12 to account for the tone name
        return data[index] if index < len(data) else default

    parameters = {}

    # Mapping DigitalParameter Enum members to their respective positions in SysEx data
    for param in DigitalParameter:
        # Use the parameter's address from the enum and fetch the value from the data
        parameters[param.name] = safe_get(param.address)

    return parameters


class DigitalParameter(SynthParameter):
    """Digital synth parameters with their addresses and value ranges"""

    def __init__(self, address: int, min_val: int, max_val: int, 
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display range for the parameter"""
        return self.display_min, self.display_max

    # Oscillator parameters
    OSC_WAVE = (0x00, 0, 7)  # Waveform preset_type
    OSC_WAVE_VARIATION = (0x01, 0, 2)  # Wave variation
    OSC_PITCH = (0x03, -24, 24)  # Coarse tune
    OSC_DETUNE = (0x04, -50, 50)  # Fine tune (-50 to +50)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x05, 0, 127)  # PWM Depth
    OSC_PULSE_WIDTH = (0x06, 0, 127)  # Pulse Width
    OSC_PITCH_ENV_ATTACK_TIME = (0x07, 0, 127)  # Pitch Envelope Attack
    OSC_PITCH_ENV_DECAY_TIME = (0x08, 0, 127)  # Pitch Envelope Decay
    OSC_PITCH_ENV_DEPTH = (0x09, -63, 63)  # Pitch Envelope Depth (-63 to +63)

    FILTER_MODE = (0x0A, 0, 7)  # Filter mode
    FILTER_SLOPE = (0x0B, 0, 1)  # Filter slope
    FILTER_CUTOFF = (0x0C, 0, 127)  # Cutoff frequency
    FILTER_CUTOFF_KEYFOLLOW = (0x0D, 54, 74, -100, 100)  # Key follow
    FILTER_ENV_VELOCITY_SENSITIVITY = (0x0E, 1, 127, -63, 63)  # Velocity sensitivity
    FILTER_RESONANCE = (0x0F, 0, 127)  # Resonance
    FILTER_ENV_ATTACK_TIME = (0x10, 0, 127)  # Filter envelope attack
    FILTER_ENV_DECAY_TIME = (0x11, 0, 127)  # Filter envelope decay
    FILTER_ENV_SUSTAIN_LEVEL = (0x12, 0, 127)  # Filter envelope sustain
    FILTER_ENV_RELEASE_TIME = (0x13, 0, 127)  # Filter envelope release
    FILTER_ENV_DEPTH = (0x14, 1, 127, -63, 63)  # Filter envelope depth

    # Amplifier parameters
    AMP_LEVEL = (0x15, 0, 127)  # Amplitude level
    AMP_VELOCITY = (0x16, -63, 63)  # Velocity sensitivity
    AMP_ENV_ATTACK_TIME = (0x17, 0, 127)  # Amplitude envelope attack
    AMP_ENV_DECAY_TIME = (0x18, 0, 127)  # Amplitude envelope decay
    AMP_ENV_SUSTAIN_LEVEL = (0x19, 0, 127)  # Amplitude envelope sustain
    AMP_ENV_RELEASE_TIME = (0x1A, 0, 127)  # Amplitude envelope release
    AMP_PAN = (0x1B, 0, 127, -64, 63)  # Pan position
    AMP_LEVEL_KEYFOLLOW = (0x1C, 54, 74, -100, 100)  # Key follow (-100 to +100)

    # LFO parameters
    LFO_SHAPE = (0x1C, 0, 5)  # LFO waveform
    LFO_RATE = (0x1D, 0, 127)  # LFO rate
    LFO_TEMPO_SYNC_SWITCH = (0x1E, 0, 1)  # Tempo sync switch
    LFO_TEMPO_SYNC_NOTE = (0x1F, 0, 19)  # Tempo sync note
    LFO_FADE_TIME = (0x20, 0, 127)  # Fade time
    LFO_KEY_TRIGGER = (0x21, 0, 1)  # Key trigger
    LFO_PITCH_DEPTH = (0x22, 1, 127, -63, 63)  # Pitch mod depth
    LFO_FILTER_DEPTH = (0x23, 1, 127, -63, 63)  # Filter mod depth
    LFO_AMP_DEPTH = (0x24, 1, 127, -63, 63)  # Amp mod depth
    LFO_PAN_DEPTH = (0x25, 1, 127, -63, 63)  # Pan mod depth

    # Modulation LFO parameters
    MOD_LFO_SHAPE = (0x26, 0, 5)  # Mod LFO waveform
    MOD_LFO_RATE = (0x27, 0, 127)  # Mod LFO rate
    MOD_LFO_TEMPO_SYNC_SWITCH = (0x28, 0, 1)  # Tempo sync switch
    MOD_LFO_TEMPO_SYNC_NOTE = (0x29, 0, 19)  # Tempo sync note
    OSC_PULSE_WIDTH_SHIFT = (0x2A, 0, 127)  # OSC Pulse Width Shift
    # 2B is reserved
    MOD_LFO_PITCH_DEPTH = (0x2C, 1, 127, -63, 63)  # Pitch mod depth
    MOD_LFO_FILTER_DEPTH = (0x2D, 1, 127, -63, 63)  # Filter mod depth
    MOD_LFO_AMP_DEPTH = (0x2E, 1, 127, -63, 63)  # Amp mod depth
    MOD_LFO_PAN = (0x2F, 1, 127, -63, 63)  # Pan mod depth
    MOD_LFO_RATE_CTRL = (0x3B, 1, 127, -63, 63)  # Rate control

    # Additional parameters
    CUTOFF_AFTERTOUCH = (0x30, 1, 127, -63, 63)  # Cutoff aftertouch
    LEVEL_AFTERTOUCH = (0x31, 1, 127, -63, 63)  # Level aftertouch
    WAVE_GAIN = (0x34, 0, 3)  # Wave gain
    HPF_CUTOFF = (0x39, 0, 127)  # HPF cutoff
    SUPER_SAW_DETUNE = (0x3A, 0, 127)  # Super saw detune

    # Wave Number parameters
    WAVE_NUMBER_1 = (0x3B, 0, 15)  # Most significant 4 bits
    WAVE_NUMBER_2 = (0x3C, 0, 15)  # Next 4 bits
    WAVE_NUMBER_3 = (0x3D, 0, 15)  # Next 4 bits
    WAVE_NUMBER_4 = (0x3E, 0, 15)  # Least significant 4 bits

    PCM_WAVE_NUMBER = (0x3F, 0, 3)
    PCM_WAVE_GAIN = (0x40, 0, 16384)

    def __str__(self) -> str:
        return f"{self.name} (addr: {self.address:02X}, range: {self.min_val}-{self.max_val})"

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return {self.OSC_WAVE_VARIATION: "Variation"}.get(
            self, self.name.replace("_", " ").title()
        )

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self == self.OSC_WAVE_VARIATION:
            return ["A", "B", "C"][value]
        elif self == self.FILTER_MODE:
            return ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"][value]
        elif self == self.FILTER_SLOPE:
            return ["-12dB", "-24dB"][value]
        elif self == self.MOD_LFO_SHAPE:
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif self == self.MOD_LFO_TEMPO_SYNC_SWITCH:
            return "ON" if value else "OFF"
        elif self == self.LFO_SHAPE:
            return ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"][value]
        elif self in [self.LFO_TEMPO_SYNC_SWITCH, self.LFO_KEY_TRIGGER]:
            return "ON" if value else "OFF"
        elif self == self.WAVE_GAIN:
            return f"{[-6, 0, 6, 12][value]:+d}dB"
        return str(value)

    def get_wave_number(self, midi_helper) -> Optional[int]:
        """Get the full 16-bit wave number value"""
        try:
            # Get all 4 bytes
            b1 = midi_helper.get_parameter(self.WAVE_NUMBER_1)
            b2 = midi_helper.get_parameter(self.WAVE_NUMBER_2)
            b3 = midi_helper.get_parameter(self.WAVE_NUMBER_3)
            b4 = midi_helper.get_parameter(self.WAVE_NUMBER_4)

            if None in (b1, b2, b3, b4):
                return None

            # Combine into 16-bit value
            return (b1 << 12) | (b2 << 8) | (b3 << 4) | b4

        except Exception as e:
            logging.error(f"Error getting wave number: {str(e)}")
            return None

    def set_wave_number(self, midi_helper, value: int) -> bool:
        """Set the 16-bit wave number value

        Args:
            midi_helper: MIDI helper instance
            value: Wave number (0-16384)

        Returns:
            True if successful
        """
        try:
            if not 0 <= value <= 16384:
                raise ValueError(f"Wave number {value} out of range (0-16384)")

            # Split into 4-bit chunks
            b1 = (value >> 12) & 0x0F  # Most significant 4 bits
            b2 = (value >> 8) & 0x0F  # Next 4 bits
            b3 = (value >> 4) & 0x0F  # Next 4 bits
            b4 = value & 0x0F  # Least significant 4 bits

            # Send all 4 bytes
            success = all(
                [
                    midi_helper.send_parameter(self.WAVE_NUMBER_1, b1),
                    midi_helper.send_parameter(self.WAVE_NUMBER_2, b2),
                    midi_helper.send_parameter(self.WAVE_NUMBER_3, b3),
                    midi_helper.send_parameter(self.WAVE_NUMBER_4, b4),
                ]
            )

            return success

        except Exception as e:
            logging.error(f"Error setting wave number: {str(e)}")
            return False

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        # Convert bipolar values to MIDI range
        if self in [
            # Oscillator parameters
            self.OSC_PITCH,
            self.OSC_DETUNE,
            self.OSC_PITCH_ENV_DEPTH,
            # Filter parameters
            self.FILTER_CUTOFF_KEYFOLLOW,
            self.FILTER_ENV_VELOCITY_SENSITIVITY,
            self.FILTER_ENV_DEPTH,
            # Amplifier parameters
            self.AMP_VELOCITY,
            self.AMP_PAN,
            self.AMP_LEVEL_KEYFOLLOW,
            # LFO parameters
            self.LFO_PITCH_DEPTH,
            self.LFO_FILTER_DEPTH,
            self.LFO_AMP_DEPTH,
            self.LFO_PAN_DEPTH,
            # Mod LFO parameters
            self.MOD_LFO_PITCH_DEPTH,
            self.MOD_LFO_FILTER_DEPTH,
            self.MOD_LFO_AMP_DEPTH,
            self.MOD_LFO_PAN,
            self.MOD_LFO_RATE_CTRL,
        ]:
            # Convert from display range to MIDI range
            if self == self.AMP_PAN:
                value = value + 64  # -64 to +63 -> 0 to 127
            elif self in [self.FILTER_CUTOFF_KEYFOLLOW, self.AMP_LEVEL_KEYFOLLOW]:
                value = value + 100  # -100 to +100 -> 0 to 200
                value = (value * 127) // 200  # Scale to MIDI range
            elif self == self.OSC_PITCH:
                value = value + 64  # -24 to +24 -> 40 to 88
            elif self == self.OSC_DETUNE:
                value = value + 64  # -50 to +50 -> 14 to 114
            elif self == self.OSC_PITCH_ENV_DEPTH:
                value = value + 64  # -63 to +63 -> 1 to 127
            elif self in [
                self.LFO_PITCH_DEPTH,
                self.LFO_FILTER_DEPTH,
                self.LFO_AMP_DEPTH,
                self.LFO_PAN_DEPTH,
                self.MOD_LFO_PITCH_DEPTH,
                self.MOD_LFO_FILTER_DEPTH,
                self.MOD_LFO_AMP_DEPTH,
                self.MOD_LFO_PAN,
                self.MOD_LFO_RATE_CTRL,
            ]:
                value = value + 64  # -63 to +63 -> 0 to 127
            else:
                value = value + 63  # -63 to +63 -> 0 to 126

        # Ensure value is in valid MIDI range
        if value < 0 or value > 127:
            raise ValueError(
                f"MIDI value {value} out of range for {self.name} " f"(must be 0-127)"
            )

        return value

    def convert_from_display(self, display_value: int) -> int:
        """Convert from display value to MIDI value (0-127)"""
        # Handle bipolar parameters
        if self in [
            # Oscillator parameters
            self.OSC_PITCH,
            self.OSC_DETUNE,
            # Filter parameters
            self.FILTER_CUTOFF_KEYFOLLOW,
            self.FILTER_ENV_VELOCITY_SENSITIVITY,
            self.FILTER_ENV_DEPTH,
            # Amplifier parameters
            self.AMP_VELOCITY,
            self.AMP_PAN,
            self.AMP_LEVEL_KEYFOLLOW,
            # LFO parameters
            self.LFO_PITCH_DEPTH,
            self.LFO_FILTER_DEPTH,
            self.LFO_AMP_DEPTH,
            self.LFO_PAN_DEPTH,
            # Mod LFO parameters
            self.MOD_LFO_PITCH_DEPTH,
            self.MOD_LFO_FILTER_DEPTH,
            self.MOD_LFO_AMP_DEPTH,
            self.MOD_LFO_PAN,
            self.MOD_LFO_RATE_CTRL,
        ]:
            # Convert from display range to MIDI range
            if self == self.AMP_PAN:
                return display_value + 64  # -64 to +63 -> 0 to 127
            elif self in [self.FILTER_CUTOFF_KEYFOLLOW, self.AMP_LEVEL_KEYFOLLOW]:
                return display_value + 100  # -100 to +100 -> 0 to 200
            elif self == self.OSC_PITCH:
                return display_value + 64  # -24 to +24 -> 40 to 88
            elif self == self.OSC_DETUNE:
                return display_value + 64  # -50 to +50 -> 14 to 114
            elif self in [
                self.LFO_PITCH_DEPTH,
                self.LFO_FILTER_DEPTH,
                self.LFO_AMP_DEPTH,
                self.LFO_PAN_DEPTH,
                self.MOD_LFO_PITCH_DEPTH,
                self.MOD_LFO_FILTER_DEPTH,
                self.MOD_LFO_AMP_DEPTH,
                self.MOD_LFO_PAN,
                self.MOD_LFO_RATE_CTRL,
            ]:
                return display_value + 64  # -63 to +63 -> 0 to 127
            else:
                return display_value + 63  # -63 to +63 -> 0 to 126

        return display_value

    def get_address_for_partial(self, partial_num: int) -> Tuple[int, int]:
        """Get parameter area and address adjusted for partial number."""
        group_map = {1: 0x20, 2: 0x21, 3: 0x22}
        group = group_map.get(partial_num, 0x20)  # Default to 0x20 if partial_name is not 1, 2, or 3
        return group, self.address

    @staticmethod
    def get_by_name(param_name):
        """Get the DigitalParameter by name."""
        # Return the parameter member by name, or None if not found
        return DigitalParameter.__members__.get(param_name, None)
    
    def convert_from_midi_test(self, midi_value: int) -> int:
        """Convert from MIDI value to display value"""
        # Handle special bipolar cases first
        if self == self.OSC_DETUNE:
            return midi_value - 64  # 14 to 114 -> -50 to +50
        elif self == self.OSC_PITCH:
            return midi_value - 64  # 40 to 88 -> -24 to +24
        elif self == self.OSC_PITCH_ENV_DEPTH:
            return midi_value - 64  # 1 to 127 -> -63 to +63
        
        # For parameters with simple linear scaling
        if self.display_min != self.min_val or self.display_max != self.max_val:
            return int(self.display_min + (midi_value - self.min_val) * 
                       (self.display_max - self.display_min) / (self.max_val - self.min_val))
        return midi_value
    
    def convert_to_midi_test(self, display_value: int) -> int:
        """Convert from display value to MIDI value"""
        # Handle special bipolar cases first
        if self == self.OSC_DETUNE:
            return display_value + 64  # -50 to +50 -> 14 to 114
        elif self == self.OSC_PITCH:
            return display_value + 64  # -24 to +24 -> 40 to 88
        elif self == self.OSC_PITCH_ENV_DEPTH:
            return display_value + 64  # -63 to +63 -> 1 to 127
        
        # For parameters with simple linear scaling
        if self.display_min != self.min_val or self.display_max != self.max_val:
            return int(self.min_val + (display_value - self.display_min) * 
                       (self.max_val - self.min_val) / (self.display_max - self.display_min))
        return display_value

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to display value"""
        if self == self.OSC_DETUNE:
            return midi_value - 64  # 14 to 114 -> -50 to +50
        elif self == self.AMP_PAN:
            return midi_value - 64  # 0 to 127 -> -64 to +63        
        elif self == self.FILTER_CUTOFF_KEYFOLLOW:
            return midi_value + 100  # 0 to 200 -> -100 to +100
        elif self == self.AMP_LEVEL_KEYFOLLOW:
            return midi_value + 100  # 0 to 200 -> -100 to +100
        elif self == self.OSC_PITCH:
            return midi_value - 64  # 40 to 88 -> -24 to +24
        elif self == self.OSC_PITCH_ENV_DEPTH:
            return midi_value - 64  # 1 to 127 -> -63 to +63
        elif self == self.FILTER_CUTOFF:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_CUTOFF_KEYFOLLOW:
            return midi_value + 100  # 0 to 200 -> -100 to +100
        elif self == self.FILTER_ENV_VELOCITY_SENSITIVITY:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_DEPTH:
            return midi_value - 64  # 1 to 127 -> -63 to +63
        elif self == self.FILTER_RESONANCE:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_ATTACK_TIME:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_DECAY_TIME:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_SUSTAIN_LEVEL:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_RELEASE_TIME:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_PITCH_DEPTH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_FILTER_DEPTH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_AMP_DEPTH:
            return midi_value - 64  # 0 to 127 -> -63 to +63

        elif self == self.MOD_LFO_PITCH_DEPTH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_FILTER_DEPTH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_AMP_DEPTH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_PAN:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_RATE_CTRL:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.CUTOFF_AFTERTOUCH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == self.LEVEL_AFTERTOUCH:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        # ... handle other parameters ...
        return midi_value

    def convert_to_midi(self, slider_value: int) -> int:
        """Convert from display value to MIDI value"""
        if self == self.OSC_DETUNE:
            return slider_value + 64  # 14 to 114 -> -50 to +50
        elif self == self.OSC_PITCH_ENV_DEPTH:
            return slider_value + 64  # 1 to 127 -> -63 to +63
        elif self == self.AMP_PAN:
            return slider_value - 64  # 0 to 127 -> -64 to +63  
        elif self == self.FILTER_CUTOFF_KEYFOLLOW:
            return slider_value + 100  # 0 to 200 -> -100 to +100
        elif self == self.AMP_LEVEL_KEYFOLLOW:
            return slider_value + 100  # 0 to 200 -> -100 to +100           
        elif self == self.OSC_PITCH:
            return slider_value + 64  # 40 to 88 -> -24 to +24
        elif self == self.OSC_DETUNE:
            return slider_value + 64  # 14 to 114 -> -50 to +50
        elif self == self.OSC_PITCH_ENV_DEPTH:
            return slider_value + 64  # 1 to 127 -> -63 to +63      
        elif self == self.FILTER_CUTOFF:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_CUTOFF_KEYFOLLOW:
            return slider_value + 100  # 0 to 200 -> -100 to +100
        elif self == self.FILTER_ENV_VELOCITY_SENSITIVITY:
            return slider_value + 64  # 0 to 127 -> -63 to +63                  
        elif self == self.FILTER_ENV_DEPTH:
            return slider_value + 64  # 1 to 127 -> -63 to +63
        elif self == self.FILTER_RESONANCE:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_ATTACK_TIME:
            return slider_value + 64  # 0 to 127 -> -63 to +63  
        elif self == self.FILTER_ENV_DECAY_TIME:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_SUSTAIN_LEVEL:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.FILTER_ENV_RELEASE_TIME:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_PITCH_DEPTH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_FILTER_DEPTH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_AMP_DEPTH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.LFO_PAN:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_PITCH_DEPTH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_FILTER_DEPTH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_AMP_DEPTH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_PAN:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.MOD_LFO_RATE_CTRL:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.CUTOFF_AFTERTOUCH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        elif self == self.LEVEL_AFTERTOUCH:
            return slider_value + 64  # 0 to 127 -> -63 to +63
        return slider_value
