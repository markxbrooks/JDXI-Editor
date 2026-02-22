"""
# midi_worker.py
Playback Worker to play Midi files in a new thread
"""

import threading
import time

from picomidi.constant import Midi
from PySide6.QtCore import QObject, Signal, Slot


class MidiPlaybackWorker(QObject):
    """MidiPlaybackWorker"""

    set_tempo = Signal(int)  # Tempo in microseconds
    result_ready = Signal(str)  # optional
    finished = Signal()

    def __init__(
        self, parent: QObject | None = None
    ) -> None:  # pylint: disable=unsupported-binary-operation
        super().__init__()
        self.parent = parent
        self.position_tempo = Midi.TEMPO.BPM_120_USEC
        self.initial_tempo = Midi.TEMPO.BPM_120_USEC
        self.should_stop = False
        self.buffered_msgs = []
        self.midi_out_port = None
        self.playback_engine = None
        self.play_program_changes = True
        self.ticks_per_beat = 480
        self.lock = threading.Lock()
        self.index = 0
        self.start_time = time.time()

    def __str__(self) -> str:
        return (
            f"[{self.__class__.__name__}] (position_tempo={self.position_tempo}, "
            f"[{self.__class__.__name__}] should_stop={self.should_stop}, buffered_msgs={len(self.buffered_msgs)}, "
            f"[{self.__class__.__name__}] midi_out_port={self.midi_out_port}, play_program_changes={self.play_program_changes}, "
            f"[{self.__class__.__name__}] ticks_per_beat={self.ticks_per_beat}, index={self.index}, "
            f"[{self.__class__.__name__}] start_time={self.start_time})"
        )

    def setup(
        self,
        buffered_msgs: list,
        midi_out_port: object,
        ticks_per_beat: int = 480,
        play_program_changes: bool = True,
        start_time: float | None = None,  # pylint: disable=unsupported-binary-operation
        initial_tempo: int = Midi.TEMPO.BPM_120_USEC,
        playback_engine=None,
    ) -> None:
        """Setup the playback worker; do_work drives playback_engine.process_until_now()."""
        self.playback_engine = playback_engine
        self.buffered_msgs = buffered_msgs
        self.midi_out_port = midi_out_port
        self.ticks_per_beat = ticks_per_beat
        self.play_program_changes = play_program_changes
        self.initial_tempo = initial_tempo
        self.index = 0
        if start_time is None:
            self.start_time = time.time()
        else:
            self.start_time = start_time
        self.should_stop = False

        if initial_tempo is not None:
            self.initial_tempo = initial_tempo
            self.position_tempo = initial_tempo
        else:
            self.initial_tempo = Midi.TEMPO.BPM_120_USEC
            self.position_tempo = Midi.TEMPO.BPM_120_USEC

        if self.playback_engine is not None:
            print(f"🎵 [{self.__class__.__name__}] Worker setup: playback_engine")

    def stop(self) -> None:
        """Stop the playback worker."""
        with self.lock:
            self.should_stop = True

    def update_tempo(self, new_tempo: int) -> None:
        """
        update_tempo

        :param new_tempo: int
        :return: None
        """
        if new_tempo is None:
            return  # No change in tempo
        print(f"Emitting {new_tempo}")
        self.set_tempo.emit(new_tempo)
        with self.lock:
            self.position_tempo = new_tempo
        if self.parent is not None:
            if hasattr(self.parent, "set_display_tempo_usecs"):
                # Assuming parent has a method to update digital tempo
                print(
                    f"[{self.__class__.__name__}] Updating display tempo to {new_tempo}"
                )
                self.parent.set_display_tempo_usecs(new_tempo)

    @Slot()
    def do_work(self) -> None:
        """Drive PlaybackEngine; engine calls on_event (send) and handles tempo/mute."""
        if self.should_stop:
            return
        if self.playback_engine is None:
            return
        self.playback_engine.process_until_now()
        if not self.playback_engine._is_playing:
            self.finished.emit()
