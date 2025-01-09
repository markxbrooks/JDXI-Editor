from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import (
    QIcon, QPainter, QPen, QColor, QPixmap,
    QPainterPath
)
from PySide6.QtCore import Signal, Qt, QSize, QPoint

class WaveformIcon:
    @staticmethod
    def create(waveform_type, size=QSize(32, 32)):
        """Create waveform icon"""
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#2897B7"), 2))  # Blue color for waveform
        
        # Draw area - use more of the button space
        width = size.width() - 4  # Reduced padding
        height = size.height() - 4
        x = 2  # Start closer to left edge
        y = size.height() // 2
        
        if waveform_type == "Saw":
            points = [
                QPoint(x, y + height//3),
                QPoint(x + width, y - height//3),
                QPoint(x + width, y + height//3),
            ]
            painter.drawPolyline(points)
            
        elif waveform_type == "Square":
            points = [
                QPoint(x, y - height//3),
                QPoint(x, y - height//3),
                QPoint(x + width//2, y - height//3),
                QPoint(x + width//2, y + height//3),
                QPoint(x + width, y + height//3),
                QPoint(x + width, y + height//3)
            ]
            painter.drawPolyline(points)
            
        elif waveform_type == "Triangle":
            points = [
                QPoint(x, y + height//3),
                QPoint(x + width//4, y - height//3),
                QPoint(x + width*3//4, y + height//3),
                QPoint(x + width, y - height//3)
            ]
            painter.drawPolyline(points)
            
        elif waveform_type == "Sine":
            path = QPainterPath()
            path.moveTo(x, y)
            
            # Draw sine wave using cubic curves
            path.cubicTo(
                x + width//4, y - height//3,
                x + width//4, y - height//3,
                x + width//2, y
            )
            path.cubicTo(
                x + width*3//4, y + height//3,
                x + width*3//4, y + height//3,
                x + width, y
            )
            
            painter.drawPath(path)
            
        painter.end()
        return QIcon(pixmap)

class WaveformButton(QPushButton):
    waveformChanged = Signal(int)  # Signal emitted when waveform changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveforms = ["Saw", "Square", "Triangle", "Sine", "PCM", "Noise"]
        self.current_waveform = 0
        
        # Set button properties
        self.setIconSize(QSize(32, 32))
        self.setMinimumWidth(120)  # Increased width
        self.setMinimumHeight(40)  # Set minimum height
        self.setStyleSheet("""
            QPushButton {
                text-align: right;
                padding: 2px 6px;
                font-size: 10px;
                background-color: #1A1A1A;  /* Dark background */
                border: 1px solid #333333;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
                border: 1px solid #444444;
            }
            QPushButton:pressed {
                background-color: #333333;
                border: 1px solid #555555;
            }
        """)
        
        self.clicked.connect(self._cycle_waveform)
        self.updateDisplay()
        
    def _cycle_waveform(self):
        """Cycle to next waveform and emit signal"""
        self.current_waveform = (self.current_waveform + 1) % len(self.waveforms)
        self.updateDisplay()
        self.waveformChanged.emit(self.current_waveform)
        
    def updateDisplay(self):
        """Update button text and icon"""
        wave_name = self.waveforms[self.current_waveform]
        self.setText(wave_name)
        self.setIcon(WaveformIcon.create(wave_name))
        
    def setWaveform(self, index):
        """Set waveform by index"""
        if 0 <= index < len(self.waveforms):
            self.current_waveform = index
            self.updateDisplay()
            self.waveformChanged.emit(index) 