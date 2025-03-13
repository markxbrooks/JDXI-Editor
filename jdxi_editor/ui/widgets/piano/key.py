"""
A custom Qt widget representing address piano key styled after the JD-Xi synthesizer keys.
It defines address single class, PianoKey, which inherits from QPushButton and implements custom painting,
mouse interaction, and simple animations to mimic the key press and release behavior of address physical piano key.

Key Features:
- Custom rendering with gradient fills to distinguish between black and white keys.
- Visual feedback for key press events, including address color overlay and animated key movement.
- Emission of custom signals (noteOn and noteOff) with the MIDI note number to integrate with audio systems.
- Separate animations for key press and release, with different movement adjustments for black and white keys.

Usage Example:
    from your_module import PianoKey
    key = PianoKey(note_num=60, is_black=False)
    key.noteOn.connect(handle_note_on)
    key.noteOff.connect(handle_note_off)

Requires: PySide6.QtWidgets, PySide6.QtCore, PySide6.QtGui
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient


class PianoKey(QPushButton):
    """Piano key styled like JD-Xi keys with animations"""

    noteOn = Signal(int)
    noteOff = Signal(int)

    def __init__(self, note_num, is_black=False, width=22, height=160, parent=None) -> None:
        """
        Initialize the PianoKey widget with the given MIDI note number and key preset_type.
        :param note_num: MIDI note number for the key
        :param is_black: True if the key is address black key, False for white key
        :param width: Width of the key in pixels
        :param height: Height of the key in pixels
        :param parent: Parent widget
        :return: None
        """
        super().__init__(parent)
        self.note_num = note_num
        self.is_black = is_black
        self.is_pressed = False
        self.setFixedSize(width, height)
        self.setFlat(True)

        # Animation setup
        self.press_animation = QPropertyAnimation(self, b"geometry")
        self.press_animation.setDuration(50)

        self.release_animation = QPropertyAnimation(self, b"geometry")
        self.release_animation.setDuration(100)

    def paintEvent(self, event):
        """Custom paint for JD-Xi style keys"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())

        if self.is_black:
            if self.is_pressed:
                gradient.setColorAt(0, QColor(80, 80, 80))
                gradient.setColorAt(1, QColor(40, 40, 40))
            else:
                gradient.setColorAt(0, QColor(40, 40, 40))
                gradient.setColorAt(1, QColor(10, 10, 10))
        else:
            if self.is_pressed:
                gradient.setColorAt(0, QColor(200, 200, 200))
                gradient.setColorAt(1, QColor(180, 180, 180))
            else:
                gradient.setColorAt(0, QColor(255, 255, 255))
                gradient.setColorAt(1, QColor(220, 220, 220))

        painter.fillRect(0, 0, self.width(), self.height(), gradient)

        if self.is_pressed:
            painter.fillRect(
                0, self.height() - 4, self.width(), 4, QColor(255, 0, 0, 100)
            )

        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        """Handle mouse press event to trigger note on and animation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = True
            self.noteOn.emit(self.note_num)
            self.update()

            # Adjust movement amount based on key preset_type
            move_amount = 3 if not self.is_black else 2  # Black keys move less

            self.press_animation.setStartValue(self.geometry())
            self.press_animation.setEndValue(
                QRect(
                    self.x(),
                    self.y() + move_amount,
                    self.width(),
                    self.height() - move_amount,
                )
            )
            self.press_animation.start()

    def mouseReleaseEvent(self, event):
        """Handle mouse release event to trigger note off and animation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = False
            self.noteOff.emit(self.note_num)
            self.update()

            move_amount = 3 if not self.is_black else 2  # Restore position

            self.release_animation.setStartValue(self.geometry())
            self.release_animation.setEndValue(
                QRect(
                    self.x(),
                    self.y() - move_amount,
                    self.width(),
                    self.height() + move_amount,
                )
            )
            self.release_animation.start()
