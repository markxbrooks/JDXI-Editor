import sys
import mido
from mido import MidiFile, Message, open_output
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QLabel,
    QComboBox,
)
from PySide6.QtCore import QTimer


class MidiPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.midi_file = None
        self.midi_port = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_next_event)
        self.midi_iterator = iter([])
        self.start_time = None
        self.current_time = 0

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = QLabel("No file loaded")
        layout.addWidget(self.file_label)

        self.load_button = QPushButton("Load MIDI File")
        self.load_button.clicked.connect(self.load_midi)
        layout.addWidget(self.load_button)

        self.port_select = QComboBox()
        self.port_select.addItems(mido.get_output_names())
        layout.addWidget(self.port_select)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_playback)
        layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.midi_file = MidiFile(file_path)
            self.file_label.setText(f"Loaded: {file_path}")
            self.midi_iterator = iter(self.midi_file.tracks[0])

    def start_playback(self):
        if not self.midi_file:
            return

        port_name = self.port_select.currentText()
        if not port_name:
            return

        self.midi_port = open_output(port_name)
        self.current_time = 0
        self.midi_iterator = iter(self.midi_file.play())
        self.timer.start(1)

    def play_next_event(self):
        try:
            msg = next(self.midi_iterator)
            if isinstance(msg, Message):
                self.midi_port.send(msg)
        except StopIteration:
            self.stop_playback()

    def stop_playback(self):
        self.timer.stop()
        if self.midi_port:
            self.midi_port.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MidiPlayer()
    player.show()
    sys.exit(app.exec())
