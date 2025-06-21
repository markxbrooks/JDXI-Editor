"""
# midi_worker.py
Playback Worker to play Midi files in a new thread
"""


from PySide6.QtCore import QObject, Signal, Slot
import threading
import time

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds


class MidiPlaybackWorker(QObject):
    """ MidiPlaybackWorker """
    set_tempo = Signal(int)  # Tempo in microseconds
    result_ready = Signal(str)  # optional
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.buffered_msgs = []
        self.midi_out_port = None
        self.play_program_changes = True
        self.ticks_per_beat = 480
        self.lock = threading.Lock()
        self.current_tempo = MidiConstant.TEMPO_120_BPM_USEC  # default 120 BPM
        self.index = 0
        self.start_time = time.time()

    def setup(self, buffered_msgs, midi_out_port, ticks_per_beat=480, play_program_changes=True):
        self.buffered_msgs = buffered_msgs
        self.midi_out_port = midi_out_port
        self.ticks_per_beat = ticks_per_beat
        self.play_program_changes = play_program_changes
        self.index = 0
        self.start_time = time.time()

    def update_tempo(self, new_tempo: int) -> None:
        """
        update_tempo

        :param new_tempo: int
        :return: None
        """
        print(f"Emitting {new_tempo}")
        self.set_tempo.emit(new_tempo)
        with self.lock:
            self.current_tempo = new_tempo

    @Slot()
    def do_work(self):
        """ do_work """
        now = time.time()
        elapsed = now - self.start_time

        while self.index < len(self.buffered_msgs):
            abs_ticks, msg, msg_tempo = self.buffered_msgs[self.index]

            with self.lock:
                tempo = msg_tempo if msg.type == 'set_tempo' else self.current_tempo

            msg_time_sec = ticks_to_seconds(abs_ticks, tempo, self.ticks_per_beat)

            if msg_time_sec > elapsed:
                break

            if not msg.is_meta:
                if msg.type == 'program_change' and not self.play_program_changes:
                    pass  # Skip
                else:
                    self.midi_out_port.send_message(msg.bytes())

            if msg.type == 'set_tempo':
                self.update_tempo(msg.tempo)

            self.index += 1

        if self.index >= len(self.buffered_msgs):
            self.finished.emit()
