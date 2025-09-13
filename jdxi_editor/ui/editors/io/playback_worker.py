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

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.position_tempo = MidiConstant.TEMPO_120_BPM_USEC
        self.initial_tempo = MidiConstant.TEMPO_120_BPM_USEC
        self.should_stop = False
        self.buffered_msgs = []
        self.midi_out_port = None
        self.play_program_changes = True
        self.ticks_per_beat = 480
        self.lock = threading.Lock()
        self.index = 0
        self.start_time = time.time()

    def __str__(self):
        return f"MidiPlaybackWorker(position_tempo={self.position_tempo}, should_stop={self.should_stop}, buffered_msgs={len(self.buffered_msgs)}, midi_out_port={self.midi_out_port}, play_program_changes={self.play_program_changes}, ticks_per_beat={self.ticks_per_beat}, index={self.index}, start_time={self.start_time})"

    def setup(self,
              buffered_msgs: list,
              midi_out_port,
              ticks_per_beat: int = 480,
              play_program_changes: bool = True,
              start_time: float = None,
              initial_tempo: int = MidiConstant.TEMPO_120_BPM_USEC):
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
        
        # Set initial tempo (use provided value or default)
        if initial_tempo is not None:
            self.initial_tempo = initial_tempo
            self.position_tempo = initial_tempo
        else:
            # Use default tempo if none provided
            self.initial_tempo = MidiConstant.TEMPO_120_BPM_USEC
            self.position_tempo = MidiConstant.TEMPO_120_BPM_USEC

        # Debug logging
        print(f"🎵 Worker setup: received {len(buffered_msgs)} buffered messages")
        if len(buffered_msgs) > 0:
            print(f"🎵 First few buffered messages: {buffered_msgs[:3]}")

        # Set initial tempo (use provided value or default)
        if initial_tempo is not None:
            self.initial_tempo = initial_tempo
            self.position_tempo = initial_tempo
        else:
            # Use default tempo if none provided
            self.initial_tempo = MidiConstant.TEMPO_120_BPM_USEC
            self.position_tempo = MidiConstant.TEMPO_120_BPM_USEC

        # Debug logging
        print(f"🎵 Worker setup: received {len(buffered_msgs)} buffered messages")
        if len(buffered_msgs) > 0:
            print(f"🎵 First few buffered messages: {buffered_msgs[:3]}")

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
            self.position_tempo = new_tempo
        if self.parent is not None:
            if hasattr(self.parent, 'set_display_tempo_usecs'):
                # Assuming parent has a method to update display tempo
                print(f"Updating display tempo to {new_tempo}")
                self.parent.set_display_tempo_usecs(new_tempo)

    @Slot()
    def do_work(self):
        if self.should_stop:
            return

        now = time.time()
        elapsed = now - self.start_time
        
        # Add small delay to prevent immediate processing of events at tick 0
        if elapsed < 0.1:  # Wait 100ms before processing any events
            return
        
        # Print format header on first run
        if not hasattr(self, '_header_printed'):
            print("🎵 Real-time Playback Tracking:")
            print("Format: [Elapsed] Bar X.X | BPM XXX.X | Expected: X.XXs | Real: X.XXs | Diff: ±X.XXs | Index: XXXX")
            print("=" * 100)
            self._header_printed = True
            
        # Debug logging
        if len(self.buffered_msgs) == 0:
            print(f"⚠️ No buffered messages available (elapsed: {elapsed:.3f}s)")
            return

        # Add small delay to prevent immediate processing of events at tick 0
        if elapsed < 0.1:  # Wait 100ms before processing any events
            return

        # Print format header on first run
        if not hasattr(self, '_header_printed'):
            print("🎵 Real-time Playback Tracking:")
            print("Format: [Elapsed] Bar X.X | BPM XXX.X | Expected: X.XXs | Real: X.XXs | Diff: ±X.XXs | Index: XXXX")
            print("=" * 100)
            self._header_printed = True

        # Debug logging
        if len(self.buffered_msgs) == 0:
            print(f"⚠️ No buffered messages available (elapsed: {elapsed:.3f}s)")
            return

        while self.index < len(self.buffered_msgs):
            abs_ticks, raw_bytes, msg_tempo = self.buffered_msgs[self.index]

            # Calculate the time this message should be sent using incremental tempo calculation
            # This correctly handles tempo changes by calculating time segment by segment
            msg_time_sec = self._calculate_message_time(abs_ticks)

            if msg_time_sec > elapsed:
                break

            # Add detailed position tracking logging (temporary)
            if self.index % 100 == 0:  # Log every 100 messages to avoid spam
                current_bar = abs_ticks / (4 * self.ticks_per_beat)
                current_bpm = 60000000 / self.position_tempo
                time_diff = elapsed - msg_time_sec
                print(f"[{elapsed:6.1f}s] Bar {current_bar:5.1f} | BPM {current_bpm:6.1f} | Expected: {msg_time_sec:5.2f}s | Real: {elapsed:5.2f}s | Diff: {time_diff:+5.2f}s | Index: {self.index:4d}")

            # Process the message
            if raw_bytes is None:
                # This is a tempo change message - process it
                # Skip an initial tempo-only message at tick 0 (already set during setup)
                if abs_ticks == 0:
                    self.index += 1
                    continue
                current_bar = abs_ticks / (4 * self.ticks_per_beat)
                new_bpm = 60000000 / msg_tempo
                print(f"🎵 TEMPO CHANGE at Bar {current_bar:.1f} ({elapsed:.2f}s): {msg_tempo} ({new_bpm:.1f} BPM)")
                self.update_tempo(msg_tempo)
            else:
                # Send the MIDI message
                status_byte = raw_bytes[0]
                message_type = status_byte & BitMask.HIGH_4_BITS

                if message_type == MidiConstant.PROGRAM_CHANGE and not self.play_program_changes:
                    # 0xC0 = program_change
                    pass  # Skip
                else:
                    self.midi_out_port.send_message(raw_bytes)

            self.index += 1

        if self.index >= len(self.buffered_msgs):
            self.finished.emit()

    def _calculate_message_time(self, target_ticks: int) -> float:
        """
        Calculate the time for a message at target_ticks using incremental tempo calculation.
        This correctly handles tempo changes by processing events in chronological order.
        """
        if not hasattr(self, '_cached_times'):
            self._cached_times = {}
<<<<<<< HEAD
        
        # Return cached time if available
        if target_ticks in self._cached_times:
            return self._cached_times[target_ticks]
        
=======

        # Return cached time if available
        if target_ticks in self._cached_times:
            return self._cached_times[target_ticks]

>>>>>>> 089e41371e148f15ced20093e0b19fa8457041fd
        # Calculate time incrementally like get_total_duration_in_seconds does
        current_tempo = self.initial_tempo
        time_seconds = 0.0
        last_tick = 0
<<<<<<< HEAD
        
=======

>>>>>>> 089e41371e148f15ced20093e0b19fa8457041fd
        # Process all messages up to target_ticks in chronological order
        for i, (abs_ticks, raw_bytes, msg_tempo) in enumerate(self.buffered_msgs):
            if abs_ticks > target_ticks:
                break
<<<<<<< HEAD
                
=======

>>>>>>> 089e41371e148f15ced20093e0b19fa8457041fd
            # Calculate time for this segment using the tempo that was active
            delta_ticks = abs_ticks - last_tick
            time_seconds += (current_tempo / 1_000_000.0) * (delta_ticks / self.ticks_per_beat)
            last_tick = abs_ticks
<<<<<<< HEAD
            
            # Update tempo if this is a tempo change message
            if raw_bytes is None:  # This is a tempo change message
                current_tempo = msg_tempo
        
        # Cache the result
        self._cached_times[target_ticks] = time_seconds
        return time_seconds

=======

            # Update tempo if this is a tempo change message
            if raw_bytes is None:  # This is a tempo change message
                current_tempo = msg_tempo

        # Cache the result
        self._cached_times[target_ticks] = time_seconds
        return time_seconds
>>>>>>> 089e41371e148f15ced20093e0b19fa8457041fd
