"""
# midi_worker.py
Playback Worker to play Midi files in a new thread
"""


from PySide6.QtCore import QObject, Signal, Slot
import threading
import time

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.jdxi.sysex.bitmask import BitMask
from jdxi_editor.ui.widgets.midi.utils import ticks_to_seconds


class MidiPlaybackWorker(QObject):
    """ MidiPlaybackWorker """
    set_tempo = Signal(int)  # Tempo in microseconds
    result_ready = Signal(str)  # optional
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.should_stop = False
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
        self.should_stop = False

        # existing setup...

    def stop(self):
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
            self.current_tempo = new_tempo

    @Slot()
    def do_work(self):
        if self.should_stop:
            return

        now = time.time()
        elapsed = now - self.start_time

        while self.index < len(self.buffered_msgs):
            abs_ticks, raw_bytes, msg_tempo = self.buffered_msgs[self.index]

            tempo = msg_tempo
            msg_time_sec = ticks_to_seconds(abs_ticks, tempo, self.ticks_per_beat)

            if msg_time_sec > elapsed:
                break

            if raw_bytes is not None:
                status_byte = raw_bytes[0]
                message_type = status_byte & BitMask.HIGH_4_BITS

                if message_type == MidiConstant.PROGRAM_CHANGE and not self.play_program_changes:
                    # 0xC0 = program_change
                    pass  # Skip
                else:
                    self.midi_out_port.send_message(raw_bytes)
            else:
                self.update_tempo(msg_tempo)

            self.index += 1

        if self.index >= len(self.buffered_msgs):
            self.finished.emit()

