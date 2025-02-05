from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QFont
from PySide6.QtWidgets import QWidget


class ADSRPlot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.border = 15
        self.bgColor = QColor(0, 0, 0)  # Black background
        self.pixmap = QPixmap(self.size())
        self.envelope = None  # Initialize envelope attribute

        # Set the stylesheet to apply black background, grey lines, and Myriad Pro font
        self.setStyleSheet(
            """
            background-color: black;
            font-family: 'Myriad Pro', 'Arial', sans-serif;
            font-size: 12px;
        """
        )

        # Set the font for the widget
        font = QFont("Myriad Pro", 12)
        if not font.exactMatch():
            font = QFont(
                "Arial", 12
            )  # Fallback to Arial if Myriad Pro is not available
        self.setFont(font)

    def setValues(self, envelope):
        self.envelope = envelope
        self.refreshPixmap()

    def refreshPixmap(self):
        if not self.envelope:
            return

        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(self.bgColor)

        painter = QPainter(self.pixmap)
        penWave = QPen(QColor(169, 169, 169))  # Grey color for wave
        penWave.setStyle(Qt.SolidLine)
        penWave.setWidth(2)

        penGrid = QPen(QColor(169, 169, 169))  # Grey color for grid lines
        penGrid.setStyle(Qt.DashLine)
        penGrid.setWidth(1)

        penBorder = QPen(QColor(169, 169, 169))  # Grey color for border
        penBorder.setStyle(Qt.SolidLine)
        penBorder.setWidth(1)

        ww = self.width() - 2 * self.border
        wh = self.height() - 2 * self.border

        total = 1.5 * (
            self.envelope.attackTime
            + self.envelope.decayTime
            + self.envelope.releaseTime
        )
        attackx = self.border + int(ww * self.envelope.attackTime / total)
        decayx = attackx + int(ww * self.envelope.decayTime / total)
        releasex = self.border + int(ww * (1 - self.envelope.releaseTime / total))

        initialy = self.height() - self.border - int(wh * self.envelope.initialAmpl)
        peaky = self.height() - self.border - int(wh * self.envelope.peakAmpl)
        sustainy = self.height() - self.border - int(wh * self.envelope.sustainAmpl)

        painter.setPen(penGrid)
        painter.drawLine(self.border, initialy, ww + self.border, initialy)
        painter.drawLine(self.border, sustainy, ww + self.border, sustainy)
        painter.drawLine(self.border, peaky, ww + self.border, peaky)
        painter.drawLine(attackx, self.border / 2, attackx, wh + self.border)
        painter.drawLine(decayx, self.border / 2, decayx, wh + self.border)
        painter.drawLine(releasex, self.border / 2, releasex, wh + self.border)

        painter.setPen(penBorder)
        painter.drawText(self.border / 4, initialy + 5, "I")
        painter.drawText(self.border / 4, sustainy + 5, "S")
        painter.drawText(self.border / 4, peaky + 5, "P")
        painter.drawText(attackx / 2, wh + self.border * 2, "A")
        painter.drawText((attackx + decayx) / 2, wh + self.border * 2, "D")
        painter.drawText((ww + self.border + releasex) / 2, wh + self.border * 2, "R")

        painter.drawLine(
            self.border,
            self.height() - self.border,
            self.width() - self.border,
            self.height() - self.border,
        )
        painter.drawLine(
            self.border, self.border, self.border, self.height() - self.border
        )

        painter.setPen(penWave)
        painter.drawLine(self.border, initialy, attackx, peaky)
        painter.drawLine(attackx, peaky, decayx, sustainy)
        painter.drawLine(decayx, sustainy, releasex, sustainy)
        painter.drawLine(releasex, sustainy, self.border + ww, self.border + wh)

        painter.end()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        super().p
