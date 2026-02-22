"""
MIDI analysis for the file player: tempo, drum detection, track classification, channel selection.

Pure domain logic — no Qt, no UI. The editor calls these methods and applies results to state/UI.
"""

from typing import Optional

from picomidi.constant import Midi
from picomidi.message.type import MidoMessageType

from jdxi_editor.midi.track.classification import classify_tracks
from jdxi_editor.midi.utils.drum_detection import detect_drum_tracks


class MidiAnalyzer:
    """
    MIDI file analysis: initial tempo, drum track detection, track classification,
    and preferred playback channel selection.
    """

    def get_initial_tempo(self, midi_file) -> tuple[int, dict[int, int]]:
        """
        Detect initial tempo from the first set_tempo message in the file.

        :param midi_file: mido.MidiFile
        :return: (tempo_initial_usec, initial_track_tempos)
                 tempo_initial_usec: first tempo found or default 120 BPM
                 initial_track_tempos: map track_number -> tempo (for tracks that have set_tempo)
        """
        tempo_initial = Midi.TEMPO.BPM_120_USEC
        initial_track_tempos: dict[int, int] = {}
        for track_number, track in enumerate(midi_file.tracks):
            for msg in track:
                if msg.type == MidoMessageType.SET_TEMPO:
                    tempo_initial = msg.tempo
                    initial_track_tempos[track_number] = msg.tempo
                    break
            else:
                continue
            break
        return (tempo_initial, initial_track_tempos)

    def get_drum_tracks(
        self, midi_file, min_score: float = 70.0
    ) -> list[tuple[int, dict]]:
        """
        Detect drum tracks in the MIDI file.

        :param midi_file: mido.MidiFile
        :param min_score: minimum score to consider a track as drums
        :return: list of (track_index, analysis_dict) sorted by score descending
        """
        return detect_drum_tracks(midi_file, min_score=min_score)

    def get_classifications(
        self,
        midi_file,
        exclude_drum_indices: Optional[list[int]] = None,
        min_score: float = 30.0,
    ) -> dict:
        """
        Classify non-drum tracks into Bass, Keys/Guitars, Strings.

        :param midi_file: mido.MidiFile
        :param exclude_drum_indices: track indices to exclude (e.g. drum tracks)
        :param min_score: minimum score for a track to be classified
        :return: dict with keys "bass", "keys_guitars", "strings", "unclassified";
                 each value is a list of (track_index, TrackStats)
        """
        return classify_tracks(
            midi_file,
            exclude_drum_tracks=exclude_drum_indices or [],
            min_score=min_score,
        )

    def get_preferred_channel(
        self, midi_file, preferred_channels: set[int]
    ) -> Optional[int]:
        """
        Pick a playback channel from the file that is in the preferred set.

        :param midi_file: mido.MidiFile
        :param preferred_channels: set of channel numbers (e.g. 0, 1, 2, 9 for 1-based 1,2,3,10)
        :return: channel index 0–15, or None if no message uses a preferred channel
        """
        for track in midi_file.tracks:
            for msg in track:
                if hasattr(msg, "channel") and msg.channel in preferred_channels:
                    return msg.channel
        return None
