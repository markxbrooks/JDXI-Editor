from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor


class ADSRGraph(QWidget):
    point_moved = Signal(str, float)  # Signal(name of point, new normalized x)

    def __init__(self, parent=None):
        super().__init__(parent)
        """
        Initialize the ADSRGraph
        :param parent: Optional[QWidget]
        """
        self.setMinimumHeight(150)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.sustain_level = 0.5
        self.release_x = 0.7
        self.dragging = None

    def paintEvent(self, event):
        """Paint the ADSR graph.
        :param event: QPaintEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#ffffff"), 2)
        painter.setPen(pen)

        w = self.width()
        h = self.height()

        # Define points
        p0 = QPointF(0, h)
        p1 = QPointF(self.attack_x * w, 0)
        p2 = QPointF(self.decay_x * w, (1 - self.sustain_level) * h)
        p3 = QPointF(self.release_x * w, (1 - self.sustain_level) * h)
        p4 = QPointF(w, h)

        # Draw lines
        painter.drawPolyline([p0, p1, p2, p3, p4])

        # Draw draggable points
        dot_pen = QPen(QColor("#ff6666"), 4)
        painter.setPen(dot_pen)
        painter.setBrush(QColor("#ffcccc"))
        for pt in [p1, p2, p3]:
            painter.drawEllipse(pt, 6, 6)

    def mousePressEvent(self, event):
        """Handle mouse press event.
        :param event: QMouseEvent
        """
        pos = event.position()
        points = {
            "attack": QPointF(self.attack_x * self.width(), 0),
            "decay": QPointF(
                self.decay_x * self.width(), (1 - self.sustain_level) * self.height()
            ),
            "release": QPointF(
                self.release_x * self.width(), (1 - self.sustain_level) * self.height()
            ),
        }
        for name, pt in points.items():
            if (pt - pos).manhattanLength() < 15:
                self.dragging = name
                break

    def mouseMoveEvent(self, event):
        """Handle mouse move event.
        :param event: QMouseEvent
        """
        if self.dragging:
            pos = event.position()
            if self.dragging == "attack":
                self.attack_x = max(0.01, min(pos.x() / self.width(), 1.0))
            elif self.dragging == "decay":
                self.decay_x = max(
                    self.attack_x + 0.01, min(pos.x() / self.width(), 1.0)
                )
            elif self.dragging == "release":
                self.release_x = max(
                    self.decay_x + 0.01, min(pos.x() / self.width(), 1.0)
                )

            self.point_moved.emit(self.dragging, pos.x() / self.width())
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release event.
        :param event: QMouseEvent
        """
        self.dragging = None
