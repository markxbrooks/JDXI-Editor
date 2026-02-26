from picomidi import MidiTempo


class TimingConfig:
    """Timing Config Class"""
    def __init__(self, bpm: int = 120, beats_per_measure: int = 4, steps_per_beat: int = 4):
        self.bpm = bpm
        self.beats_per_measure = beats_per_measure
        self.steps_per_beat = steps_per_beat

    @property
    def steps_per_bar(self) -> int:
        return self.beats_per_measure * self.steps_per_beat

    @property
    def ms_per_step(self) -> float:
        return MidiTempo.MILLISECONDS_PER_MINUTE / (self.bpm * self.steps_per_beat)
