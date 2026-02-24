"""
Editor IO Utils
"""

from mido import MidiFile

from picomidi import MidiTempo
from picomidi.constant import Midi
from picomidi.message.type import MidoMessageType


def format_time(seconds: float) -> str:
    """
    Format a time in seconds to a string

    :param seconds: float
    :return: str
    """
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02}"


def tempo2bpm(tempo: int) -> float:
    """
    tempo2bpm

    :param tempo: float
    :return: float
    """
    return MidiTempo.MICROSECONDS_PER_MINUTE / tempo


def get_last_tempo(midi_file: MidiFile) -> int:
    """
    get_last_tempo

    :param midi_file: MidiFile
    :return: int
    """
    tempo = Midi.TEMPO.BPM_120_USEC  # 500_000 default
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == MidoMessageType.SET_TEMPO:
                tempo = msg.tempo
    return tempo
