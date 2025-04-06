"""

    WheelWidget
    (c) 2025 JDXI Editor

"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent, QFont, QLinearGradient
from PySide6.QtCore import QRectF, Qt, Signal, Property, QPropertyAnimation


class WheelWidget(QWidget):
    valueChanged = Signal(float)

    def __init__(self, parent=None, bidirectional=False, label="Wheel"):
        super().__init__(parent)
        self._value = 0.0
        self.label = label
        self.bidirectional = bidirectional
        self.setMinimumSize(40, 100)
        self.setMouseTracking(True)
        self._drag_active = False

        # Smooth snap-back animation
        self.snap_animation = QPropertyAnimation(self, b"value")
        self.snap_animation.setDuration(300)
        # self.snap_animation.setEasingCurve(Qt.EaseOutCubic)

    def get_value(self):
        return self._value

    def set_value(self, value: float):
        clamped = max(-1.0 if self.bidirectional else 0.0, min(1.0, value))
        if clamped != self._value:
            self._value = clamped
            self.valueChanged.emit(self._value)
            self.update()

    value = Property(float, get_value, set_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background and border
        # Set pen for the border
        painter.setPen(QPen(QColor("#000000"), 2))

        # Create a vertical gradient from top to bottom
        gradient = QLinearGradient(self.rect().topLeft(), self.rect().bottomLeft())
        gradient.setColorAt(0.0, QColor("#111111"))
        gradient.setColorAt(0.5, QColor("#333333"))
        gradient.setColorAt(1.0, QColor("#000000"))

        # Set the gradient as the brush for filling
        painter.setBrush(gradient)

        # Draw the rectangle with the gradient fill and border
        painter.drawRect(self.rect())

        # Draw wheel position
        notch_height = 25
        usable_height = self.height() - 40
        center_y = self.height() / 2
        offset = -self._value * (usable_height / 2 if self.bidirectional else usable_height)
        wheel_y = center_y + offset - notch_height / 2
        wheel_rect = QRectF(0, wheel_y, self.width(), int(notch_height))
        # Create a vertical gradient for the wheel
        gradient = QLinearGradient(wheel_rect.topLeft(), wheel_rect.bottomLeft())
        gradient.setColorAt(0.0, QColor("black"))
        gradient.setColorAt(0.5, QColor("#222222"))
        gradient.setColorAt(1.0, QColor("black"))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawRect(wheel_rect)

        # Draw label above the wheel
        painter.save()

        painter.restore()

    def mousePressEvent(self, event: QMouseEvent):
        self._drag_active = True
        self.snap_animation.stop()
        self._update_value_from_mouse(event.pos().y())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_active:
            self._update_value_from_mouse(event.pos().y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_active = False
        if self.bidirectional:
            self.snap_animation.stop()
            self.snap_animation.setStartValue(self._value)
            self.snap_animation.setEndValue(0.0)
            self.snap_animation.start()

    def _update_value_from_mouse(self, y: int):
        h = self.height()
        if self.bidirectional:
            center = h / 2
            new_val = max(-1.0, min(1.0, (center - y) / (h / 2)))
        else:
            new_val = max(0.0, min(1.0, 1.0 - y / h))
        self.set_value(new_val)
