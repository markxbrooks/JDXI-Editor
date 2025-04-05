from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRectF

class MidiTrackWidget(QWidget):
    def __init__(self, midi_file=None, parent=None):
        super().__init__(parent)
        self.midi_file = midi_file
        self.tracks = []

    def set_midi_file(self, midi_file):
        self.midi_file = midi_file
        self.tracks = [[msg for msg in track if msg.type == 'note_on'] for track in midi_file.tracks]
        self.update()

    def paintEvent(self, event):
        if not self.midi_file:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_height = self.height() / len(self.tracks)

        for i, track in enumerate(self.tracks):
            y = i * track_height
            for msg in track:
                start = msg.time / self.midi_file.length * self.width()
                width = 5  # Fixed width for simplicity
                rect = QRectF(start, y, width, track_height)
                painter.setPen(QPen(Qt.NoPen))
                painter.setBrush(QColor(100, 100, 255, 150))  # Semi-transparent blue
                painter.drawRect(rect)