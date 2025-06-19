"""
TimeRulerWidget
"""

import mido
from PySide6.QtCore import Qt
from PySide6.QtGui import QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.jdxi.style import JDXiStyle


class TimeRulerWidget(QWidget):
    """
    TimeRulerWidget
    """
    def __init__(self, midi_file: mido.MidiFile = None, parent: QWidget = None):
        super().__init__(parent)
        self.midi_file = midi_file
        self.setMinimumHeight(20)
        self.setMaximumHeight(JDXiStyle.MAX_RULER_HEIGHT)

    def set_midi_file(self, midi_file: mido.MidiFile) -> None:
        self.midi_file = midi_file
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.midi_file:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        duration = self.midi_file.length
        width = self.width()
        height = self.height()

        num_marks = int(duration) + 1
        spacing = width / duration if duration else width

        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white))

        for second in range(num_marks):
            if second % 10 == 0:
                # Draw major ticks every 10 seconds
                x = int(second * spacing)
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 2, height - 4, f"{second}s")
