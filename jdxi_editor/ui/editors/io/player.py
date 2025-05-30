""" MIDI Player for JDXI Editor """
from typing import Optional

import mido
import time
from pathlib import Path
from typing import Optional
from mido import MidiFile, open_output, tempo2bpm, bpm2tempo
from PySide6.QtCore import Qt, QTimer, QObject, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QFileDialog,
    QLabel,
    QDoubleSpinBox,
    QSlider,
    QGroupBox, QHBoxLayout,
)
import qtawesome as qta

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.midi.track import MidiTrackViewer


class PlaybackWorker(QObject):
    result_ready = Signal()  # e.g., to notify when a frame is processed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None  # Reference to MidiFileEditor

    def set_editor(self, editor):
        self.editor = editor

    @Slot()
    def do_work(self):
        if self.editor:
            self.editor.play_next_event()
            self.result_ready.emit()


def format_time(seconds: float) -> str:
    """
    Format a time in seconds to a string
    :param seconds: float
    :return: str
    """
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02}"


class MidiFileEditor(SynthEditor):
    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent=None,
        preset_helper=None,
    ):
        super().__init__()
        self.event_index = None
        self.worker = None
        self.worker_thread = None
        """
        Initialize the MidiPlayer
        :param midi_helper: Optional[MidiIOHelper]
        :param parent: Optional[QWidget]
        :param preset_helper: Optional[JDXIPresetHelper]
        """

        self.init_ui()
        self.midi_helper = midi_helper if midi_helper else MidiIOHelper()
        self.preset_helper = (
            preset_helper
            if preset_helper
            else JDXiPresetHelper(
                self.midi_helper,
                presets=DIGITAL_PRESET_LIST,
                channel=MidiChannel.DIGITAL_SYNTH_1,
            )
        )
        self.paused_time = None
        self.midi_file = None
        self.midi_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_event)

        self.midi_events = []
        self.current_event_index = 0
        self.start_time = None
        self.duration_seconds = 0
        self.paused = False

    def setup_worker(self):
        """
        Setup the worker and thread for threaded playback using QTimer
        """
        # Clean up any previous worker/thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread.deleteLater()
            self.worker = None

        self.worker = PlaybackWorker()
        self.worker.set_editor(self)

        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.result_ready.connect(self.handle_result)  # optional for UI update

        # QTimer lives in the main thread, but calls worker.do_work()
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.worker.do_work)

        self.worker_thread.start()

    def init_ui(self):
        """
        Initialize the UI for the MidiPlayer
        """
        hlayout = QHBoxLayout()
        self.file_label = DigitalTitle("No file loaded")
        hlayout.addWidget(self.file_label)

        vlayout = QVBoxLayout()
        hlayout.addLayout(vlayout)

        # file load / save selection
        file_layout = QHBoxLayout()
        vlayout.addLayout(file_layout)
        self.load_button = QPushButton(
            qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND), "Load MIDI File"
        )
        self.load_button.clicked.connect(self.load_midi)
        file_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save MIDI File")
        self.save_button = QPushButton(
            qta.icon("mdi.midi-port", color=JDXiStyle.FOREGROUND), "Save MIDI File"
        )
        self.save_button.clicked.connect(self.save_midi)
        file_layout.addWidget(self.save_button)

        # midi port selection
        midi_port_layout = QHBoxLayout()
        vlayout.addLayout(midi_port_layout)
        midi_port_layout.addWidget(QLabel("Midi Port"))
        self.port_select = QComboBox()
        self.port_select.addItems(mido.get_output_names())
        midi_port_layout.addWidget(self.port_select)

        # tempo selection
        tempo_layout = QHBoxLayout()
        vlayout.addLayout(tempo_layout)
        self.tempo_spin = QDoubleSpinBox()
        self.tempo_spin.setRange(20, 300)
        self.tempo_spin.setValue(120)
        self.tempo_spin.setSuffix(" BPM")
        tempo_layout.addWidget(QLabel("Tempo"))
        tempo_layout.addWidget(self.tempo_spin)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setEnabled(False)
        self.position_slider.sliderReleased.connect(self.scrub_position)
        layout = QVBoxLayout()
        layout.addLayout(hlayout)
        layout.addWidget(QLabel("Playback Position"))
        layout.addWidget(self.position_slider)

        self.position_label = QLabel("0:00 / 0:00")
        layout.addWidget(self.position_label)

        self.midi_track_viewer = MidiTrackViewer()
        layout.addWidget(self.midi_track_viewer)

        transport_group = QGroupBox("Transport")
        transport_layout = QHBoxLayout()
        transport_group.setLayout(transport_layout)
        # self.play_button = QPushButton("Play")
        self.play_button = QPushButton(
            qta.icon("ri.play-line", color=JDXiStyle.FOREGROUND), "Play"
        )
        self.play_button.clicked.connect(self.start_playback)
        transport_layout.addWidget(self.play_button)

        self.stop_button = QPushButton(
            qta.icon("ri.stop-line", color=JDXiStyle.FOREGROUND), "Stop"
        )
        self.pause_button = QPushButton(
            qta.icon("ri.pause-line", color=JDXiStyle.FOREGROUND), "Pause"
        )
        self.stop_button.clicked.connect(self.stop_playback)
        self.pause_button.clicked.connect(self.toggle_pause_playback)
        transport_layout.addWidget(self.stop_button)
        transport_layout.addWidget(self.pause_button)
        layout.addWidget(transport_group)
        self.setLayout(layout)

    def save_midi(self):
        """
        Save a MIDI file
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.midi_track_viewer.midi_file.save(file_path)
            self.file_label.setText(f"Saved: {Path(file_path).name}")

    def load_midi(self):
        """
        Load a MIDI file
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.midi_file = MidiFile(file_path)
            self.file_label.setText(f"Loaded: {Path(file_path).name}")
            self.midi_track_viewer.set_midi_file(self.midi_file)

            self.ticks_per_beat = self.midi_file.ticks_per_beat
            self.tempo = 500000  # default 120 BPM

            # Look for a tempo message in track 0
            for msg in self.midi_file.tracks[0]:
                if msg.type == "set_tempo":
                    self.tempo = msg.tempo
                    break

            bpm = tempo2bpm(self.tempo)
            self.tempo_spin.setValue(round(bpm))

            events = []
            for track_index, track in enumerate(self.midi_file.tracks):
                abs_time = 0
                for msg in track:
                    abs_time += msg.time
                    events.append((abs_time, msg, track_index))

            self.midi_events = sorted(events, key=lambda x: x[0])
            self.setup_worker()
            # Compute total duration in seconds
            self.total_ticks = max(t for t, _, _ in self.midi_events)
            tempo = bpm2tempo(self.tempo_spin.value())
            self.tick_duration = tempo / 1_000_000 / self.ticks_per_beat
            self.duration_seconds = self.total_ticks * self.tick_duration

            self.position_slider.setEnabled(True)
            self.position_slider.setRange(0, int(self.duration_seconds))
            self.position_label.setText(
                f"0:00 / {format_time(self.duration_seconds)}"
            )

    def start_playback(self):
        """
        Start playback of the MIDI file
        """
        if not self.midi_file or not self.midi_events:
            return

        port_name = self.port_select.currentText()
        if not port_name:
            return

        self.midi_port = open_output(port_name)
        self.start_time = time.time()
        self.event_index = 0

        if not self.worker_thread or not self.worker:
            self.setup_worker()

        self.timer.start()

    def play_next_event(self):
        """
        Play the next event in the MIDI file
        """
        if self.event_index >= len(self.midi_events):
            self.stop_playback()
            return
        # tick, msg , track = self.midi_events[self.event_index]
        now = time.time()
        elapsed_time = now - self.start_time
        self.position_slider.setValue(int(elapsed_time))
        self.position_label.setText(
            f"{format_time(elapsed_time)} / {format_time(self.duration_seconds)}"
        )

        while self.event_index < len(self.midi_events):
            tick_time, msg, track = self.midi_events[self.event_index]
            scheduled_time = tick_time * self.tick_duration

            if elapsed_time >= scheduled_time:
                if not msg.is_meta:
                    if (
                        hasattr(msg, "channel")
                        and (msg.channel + 1) in self.midi_track_viewer.muted_channels
                    ):
                        if msg.type == "note_on" and msg.velocity > 0:
                            pass  # Skip muted channel but allow note off
                    else:
                        self.midi_port.send(msg)
                self.event_index += 1
            else:
                break

    def scrub_position(self):
        """
        Scrub to a new position in the file using the slider.
        Resets start time and event index to match new slider position.
        """
        if not self.midi_file or not self.midi_events:
            return

        target_time = self.position_slider.value()
        self.start_time = time.time() - target_time
        self.event_index = 0

        # Find the first event index that should be played after this point
        for i, (tick, _, _) in enumerate(self.midi_events):
            if tick * self.tick_duration >= target_time:
                self.event_index = i
                break

        # Stop all notes to avoid hanging
        if self.midi_port:
            for ch in range(16):
                for note in range(128):
                    self.midi_port.send(mido.Message("note_off", note=note, velocity=0, channel=ch))

    def stop_playback(self):
        """
        Stop the playback and reset everything.
        """
        self.timer.stop()

        if self.midi_port:
            for ch in range(16):
                for note in range(128):
                    self.midi_port.send(mido.Message("note_off", note=note, velocity=0, channel=ch))
            self.midi_port.close()
            self.midi_port = None

        self.event_index = 0
        self.position_slider.setValue(0)
        self.position_label.setText(f"0:00 / {format_time(self.duration_seconds)}")

    def toggle_pause_playback(self):
        """
        Toggle pause and resume playback.
        :return: None
        """
        if not self.midi_file or not self.timer:
            return

        if not self.paused:
            # Pausing playback
            self.paused_time = time.time()
            self.timer.stop()
            self.paused = True
            self.pause_button.setText("Resume")
        else:
            # Resuming playback
            if self.paused_time and self.start_time:
                pause_duration = time.time() - self.paused_time
                self.start_time += pause_duration  # Adjust start time
            self.timer.start()
            self.paused = False
            self.pause_button.setText("Pause")
    
    def toggle_pause_playback_old(self):
        if not self.midi_file or not self.timer.isActive():
            return
    
        if self.paused:
            # Resume playback
            if self.paused_time is not None:
                self.start_time += time.time() - self.paused_time  # Adjust start_time to account for paused duration
            self.timer.start(10)  # Ensure consistent timer interval
            self.paused = False
            self.pause_button.setText("Pause")
        else:
            # Pause playback
            self.paused_time = time.time()  # Record the current time as paused_time
            self.timer.stop()
            self.paused = True
            self.pause_button.setText("Resume")

    def handle_result(self, result=None):
        """
        Handle the result from the worker.
        This can be used to update the UI or perform further actions.
        :param result: The result from the worker
        """
        pass
        # For now, just print the result
        # print(f"Worker result: {result}")
        # self.position_slider.setEnabled(False)
        # self.position_slider.setValue(0)
        # self.position_label.setText("0:00 / 0:00")
        # self.midi_track_viewer.clear_tracks()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    player = MidiFileEditor()
    player.show()
    sys.exit(app.exec())