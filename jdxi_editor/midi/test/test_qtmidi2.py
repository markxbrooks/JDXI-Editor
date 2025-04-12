from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsLineItem,
)
from PySide6.QtCore import Qt, QTimer
import mido
import rtmidi


class MidiPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Player")
        self.setGeometry(100, 100, 800, 400)

        self.midi_file = None
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_virtual_port("MIDI Output")

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.load_button = QPushButton("Load MIDI File")
        self.load_button.clicked.connect(self.load_midi)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_midi)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.tracks = []
        self.playhead = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_playhead)
        self.play_position = 0

    def load_midi(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI File", "", "MIDI Files (*.mid)"
        )
        if file_path:
            self.midi_file = mido.MidiFile(file_path)
            self.visualize_midi()

    def visualize_midi(self):
        self.scene.clear()
        if not self.midi_file:
            return

        max_time = sum(
            msg.time
            for track in self.midi_file.tracks
            for msg in track
            if msg.type == "note_on"
        )
        time_scale = 10  # pixels per tick
        track_height = 20

        for i, track in enumerate(self.midi_file.tracks):
            time_position = 0
            for msg in track:
                if msg.type == "note_on":
                    rect = QGraphicsRectItem(
                        time_position * time_scale,
                        i * track_height,
                        10,
                        track_height - 5,
                    )
                    rect.setBrush(Qt.blue)
                    self.scene.addItem(rect)
                time_position += msg.time

        self.playhead = QGraphicsLineItem(
            0, 0, 0, len(self.midi_file.tracks) * track_height
        )
        self.playhead.setPen(QPen(QColor(Qt.red)))
        self.scene.addItem(self.playhead)

        self.view.setSceneRect(
            0, 0, max_time * time_scale, len(self.midi_file.tracks) * track_height
        )

    def play_midi(self):
        if not self.midi_file:
            return
        self.play_position = 0
        self.timer.start(50)  # Update every 50ms

        for msg in self.midi_file.play():
            if msg.type in ["note_on", "note_off"]:
                self.midi_out.send_message(msg.bytes())

    def update_playhead(self):
        self.play_position += 10
        self.playhead.setX(self.play_position)
        if self.play_position > self.view.sceneRect().width():
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication([])
    window = MidiPlayer()
    window.show()
    app.exec()
