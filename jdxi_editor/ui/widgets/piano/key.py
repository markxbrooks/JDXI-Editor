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

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRect,
    QRectF,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QShowEvent,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QPushButton, QWidget


class PianoKey(QPushButton):
    """Piano key styled like JD-Xi keys with animations and LED flicker"""

    noteOn = Signal(int)
    noteOff = Signal(int)

    def __init__(
        self,
        note_num: int,
        is_black: bool = False,
        width: int = 22,
        height: int = 160,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self.note_num = note_num
        self.is_black = is_black
        self.is_pressed = False
        self.middle_c = False  # this key sounds middle C (C4) at the current octave
        self.setFixedSize(width, height)
        self.setFlat(True)

        self._geometry_initialized = False

        # Press/release animations
        self.press_animation = QPropertyAnimation(self, b"geometry")
        self.press_animation.setDuration(50)

        self.release_animation = QPropertyAnimation(self, b"geometry")
        self.release_animation.setDuration(150)

        # LED flicker setup
        self.stripe = QLabel(self)
        self.stripe.setGeometry(0, 0, width, 2)

        self.led = QLabel(self)
        self.led.setGeometry(0, 0, width, 5)
        self.led.setStyleSheet("background-color: #ff1a1a; border-radius: 3px;")
        self.led_effect = QGraphicsOpacityEffect(self.led)
        self.led.setGraphicsEffect(self.led_effect)
        self.led_effect.setOpacity(0)

        self.led_anim = QPropertyAnimation(self.led_effect, b"opacity")
        self.led_anim.setDuration(600)
        self.led_anim.setKeyValues([(0.0, 0.0), (0.2, 1.0), (1.0, 0.0)])
        self.led_anim.setEasingCurve(QEasingCurve.OutQuad)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not self._geometry_initialized:
            self.original_geometry = self.geometry()
            self._geometry_initialized = True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_pressed:
                return
            if (
                self.release_animation.state() != QPropertyAnimation.State.Running
                and self.press_animation.state() != QPropertyAnimation.State.Running
            ):
                # The layout may have moved the key since it was first shown
                self.original_geometry = self.geometry()
                self._geometry_initialized = True
            self.is_pressed = True
            self.noteOn.emit(self.note_num)
            self.update()

            move_amount = 3 if not self.is_black else 2
            pressed_geometry = QRect(
                self.original_geometry.x(),
                self.original_geometry.y() + move_amount,
                self.original_geometry.width(),
                self.original_geometry.height() - move_amount,
            )

            self.press_animation.stop()
            self.press_animation.setStartValue(self.geometry())
            self.press_animation.setEndValue(pressed_geometry)
            self.press_animation.start()

            # Flicker the LED
            self.led_anim.stop()
            self.led_anim.start()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.release()

    def hideEvent(self, event) -> None:
        self.release()
        super().hideEvent(event)

    def release(self) -> None:
        """
        Let the key up: send its note off and spring it back, once per press.

        :return: None
        """
        if not self.is_pressed:
            return
        self.is_pressed = False
        self.noteOff.emit(self.note_num)
        self.update()
        self.press_animation.stop()
        if not self._geometry_initialized:
            return
        if not self.isVisible():
            self.setGeometry(self.original_geometry)
            return

        bounce_up = QRect(
            self.original_geometry.x(),
            self.original_geometry.y() - 2,
            self.original_geometry.width(),
            self.original_geometry.height() + 2,
        )

        bounce_back = self.original_geometry

        self.release_animation.stop()
        self.release_animation.setDuration(150)
        self.release_animation.setKeyValues(
            [
                (0.0, self.geometry()),
                (0.4, bounce_up),
                (1.0, bounce_back),
            ]
        )
        self.release_animation.setEasingCurve(QEasingCurve.OutBounce)
        self.release_animation.start()

    def paintEvent(self, event: QPaintEvent) -> None:
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

        if self.middle_c:
            self._paint_middle_c(painter)

    MIDDLE_C_COLOR = "#d0473b"  # a quieter JD-Xi red

    def _paint_middle_c(self, painter: QPainter) -> None:
        """
        Middle C: a small dot near the front of the key and «C4» over it.

        It moves with the octave shift (see PianoKeyboard.show_middle_c).
        """
        colour = QColor(self.MIDDLE_C_COLOR)
        w, h = self.width(), self.height()
        radius = max(1.8, w * 0.09)
        centre_y = h - 7 - radius - (4 if self.is_pressed else 0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(colour)
        painter.drawEllipse(QPointF(w / 2, centre_y), radius, radius)
        font = painter.font()
        font.setPixelSize(max(6, int(w * 0.26)))
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(colour)
        text_h = font.pixelSize() + 2
        painter.drawText(
            QRectF(0, centre_y - radius - 2 - text_h, w, text_h),
            int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom),
            "C4",
        )
