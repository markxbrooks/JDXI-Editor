"""
Wave Osc Behaviour
"""

WAVE_OSC_METADATA = {
    "SAW": ("SAW", "Sawtooth"),
    "SQUARE": ("SQR", "Square"),
    "PW_SQUARE": ("PWM", "Pulse Width Square"),
    "TRIANGLE": ("TRI", "Triangle"),
    "TRI": ("TRI", "Triangle"),
    "SINE": ("SINE", "Sine"),
    "NOISE": ("NOISE", "Noise"),
    "SUPER_SAW": ("S-SAW", "Super Saw"),
    "PCM": ("PCM", "PCM Wave"),
}


class WaveOscBehavior:
    """Impose behaviour on Wave Osc"""

    def is_pwm(self) -> bool:
        return self.name == "PW_SQUARE"

    def is_noise(self) -> bool:
        return self.name == "NOISE"

    def is_pcm(self) -> bool:
        return self.name == "PCM"

    @property
    def display_name(self) -> str:
        try:
            return WAVE_OSC_METADATA[self.name][0]
        except KeyError:
            return self.name

    @property
    def description(self) -> str:
        try:
            return WAVE_OSC_METADATA[self.name][1]
        except KeyError:
            return self.name.title().replace("_", " ")

    @property
    def midi_value(self) -> int:
        return int(self.value)
