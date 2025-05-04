"""
Pattern Display Widget
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPaintEvent


class PatternDisplay(QWidget):
    """Pattern Display Widget"""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setMinimumSize(240, 120)
        self.pattern_type = 0  # Default to "Up"
        self.octave_range = 0
        self.accent_rate = 0

    def set_pattern(
        self,
        pattern_type: int,
        octave_range: int,
        accent_rate: int,
    ) -> None:
        self.pattern_type = pattern_type
        self.octave_range = octave_range
        self.accent_rate = accent_rate
        self.update()  # Trigger repaint

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the pattern display.

        :param event: QPaintEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor(40, 40, 40))

        # Calculate dimensions with space for labels
        width = self.width() - 40  # More padding for note names
        height = self.height() - 40  # More padding for beat numbers
        x_start = 30  # Space for note names
        y_start = height + 20  # Space for beat numbers

        # Draw grid with labels
        self._draw_grid(painter, x_start, y_start, width, height)

        # Draw pattern
        points = self._get_pattern_points(x_start, y_start, width, height)
        self._draw_pattern(painter, points)

    def _draw_grid(
        self, painter: QPainter, x: int, y: int, width: int, height: int
    ) -> None:
        """Draw the grid.

        :param painter: QPainter
        :param x: int
        :param y: int
        :param width: int
        :param height: int
        """
        # Note names
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        # Draw horizontal lines (octaves)
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        steps = (self.octave_range + 1) * 12
        step_height = height / steps if steps > 0 else height

        # Font settings for labels
        painter.setFont(QFont("Sans", 8))
        text_color = QColor(180, 180, 180)

        for i in range(steps + 1):
            y_pos = y - (i * step_height)

            # Draw line
            if i % 12 == 0:  # Octave line
                painter.setPen(QPen(QColor(120, 120, 120), 1))
                # Draw octave number
                octave = i // 12
                painter.setPen(text_color)
                painter.drawText(
                    QRect(x - 25, int(y_pos) - 8, 20, 16),
                    Qt.AlignRight | Qt.AlignVCenter,
                    f"C{octave}",
                )
            else:
                painter.setPen(QPen(QColor(60, 60, 60), 1))
                # Draw note name
                note = note_names[i % 12]
                if len(note) == 1:  # Natural notes
                    painter.setPen(text_color)
                    painter.drawText(
                        QRect(x - 25, int(y_pos) - 8, 20, 16),
                        Qt.AlignRight | Qt.AlignVCenter,
                        note,
                    )

            painter.setPen(QPen(QColor(60, 60, 60), 1))
            painter.drawLine(x, int(y_pos), x + width, int(y_pos))

        # Draw vertical lines (time divisions)
        steps = 16  # 16 steps for visualization
        step_width = width / steps

        for i in range(steps + 1):
            x_pos = x + (i * step_width)
            if i % 4 == 0:  # Bar line
                painter.setPen(QPen(QColor(120, 120, 120), 1))
                # Draw beat number
                beat = i // 4 + 1
                painter.setPen(text_color)
                painter.drawText(
                    QRect(int(x_pos) - 10, y + 5, 20, 16), Qt.AlignCenter, str(beat)
                )
            else:
                painter.setPen(QPen(QColor(60, 60, 60), 1))
                # Draw step dot
                painter.setPen(text_color)
                painter.drawText(
                    QRect(int(x_pos) - 2, y + 5, 4, 16), Qt.AlignCenter, "·"
                )
            painter.drawLine(int(x_pos), y, int(x_pos), y - height)

    def _get_pattern_points(self, x: int, y: int, width: int, height: int) -> list:
        """Get the pattern points.

        :param x: int
        :param y: int
        :param width: int
        :param height: int
        """
        points = []
        steps = 16
        step_width = width / steps

        # Calculate note positions based on pattern preset_type
        if self.pattern_type == 0:  # Up
            notes = self._generate_up_pattern()
        elif self.pattern_type == 1:  # Down
            notes = self._generate_down_pattern()
        elif self.pattern_type == 2:  # Up/Down
            notes = self._generate_updown_pattern()
        elif self.pattern_type == 3:  # Random
            notes = self._generate_random_pattern()
        elif self.pattern_type == 4:  # Note Order
            notes = self._generate_note_order_pattern()
        elif self.pattern_type == 5:  # Up x2
            notes = self._generate_up2_pattern()
        elif self.pattern_type == 6:  # Down x2
            notes = self._generate_down2_pattern()
        else:  # Up&Down
            notes = self._generate_upanddown_pattern()

        # Convert notes to points
        note_range = (self.octave_range + 1) * 12
        for i, note in enumerate(notes):
            x_pos = x + (i * step_width)
            y_pos = y - (note * height / note_range if note_range > 0 else 0)
            points.append((int(x_pos), int(y_pos)))

        return points

    def _draw_pattern(self, painter: QPainter, points: list) -> None:
        """Draw the pattern.

        :param painter: QPainter
        :param points: list
        """
        if not points:
            return

        # Draw lines connecting points
        painter.setPen(QPen(QColor("#2897B7"), 2))
        for i in range(len(points) - 1):
            painter.drawLine(
                points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]
            )

        # Draw points
        for i, point in enumerate(points):
            # Accented notes in orange, others in blue
            if (i % 4 == 0) or (self.accent_rate > 0 and i % 2 == 0 and i % 4 != 0):
                painter.setBrush(QColor("#FFA200"))
                size = 8
            else:
                painter.setBrush(QColor("#2897B7"))
                size = 6
            painter.drawEllipse(point[0] - size // 2, point[1] - size // 2, size, size)

    # Pattern generation methods
    def _generate_up_pattern(self) -> list:
        return list(range(13)) * 2

    def _generate_down_pattern(self):
        return list(range(12, -1, -1)) * 2

    def _generate_updown_pattern(self):
        return list(range(13)) + list(range(11, -1, -1))

    def _generate_random_pattern(self):
        from random import randrange

        return [randrange(13) for _ in range(16)]

    def _generate_note_order_pattern(self):
        return [0, 4, 7, 12] * 4

    def _generate_up2_pattern(self):
        return [i // 2 for i in range(26)]

    def _generate_down2_pattern(self):
        return [i // 2 for i in range(24, -1, -1)]

    def _generate_upanddown_pattern(self):
        return list(range(7)) + list(range(7, -1, -1)) * 2
