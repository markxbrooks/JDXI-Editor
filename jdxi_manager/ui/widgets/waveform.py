from PySide6.QtWidgets import QPushButton, QMenu, QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor
from PySide6.QtCore import Qt, Signal, QSize, QPointF

class WaveformButton(QPushButton):
    waveformChanged = Signal(int)
    
    WAVEFORMS = [
        ("Saw", "saw"),
        ("Square", "square"),
        ("Pulse Width", "pulse"),
        ("Triangle", "triangle"),
        ("Sine", "sine"),
        ("Noise", "noise")
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_wave = 0  # Default to saw
        self.setFixedSize(60, 40)
        
        # Create waveform selection menu
        self.menu = QMenu(self)
        for i, (name, _) in enumerate(self.WAVEFORMS):
            action = self.menu.addAction(name)
            action.setData(i)
            action.triggered.connect(self._on_wave_selected)
            
        self.setMenu(self.menu)
        
    def _on_wave_selected(self):
        action = self.sender()
        wave_idx = action.data()
        if wave_idx != self.current_wave:
            self.current_wave = wave_idx
            self.update()
            self.waveformChanged.emit(wave_idx)
            
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up drawing area
        width = self.width()
        height = self.height()
        margin = 5
        draw_width = width - 2*margin
        draw_height = height - 2*margin
        center_y = height/2
        
        # Set up pen
        pen = QPen(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Draw waveform
        wave_type = self.WAVEFORMS[self.current_wave][1]
        
        if wave_type == "saw":
            path = QPainterPath()
            path.moveTo(margin, center_y + draw_height/3)
            path.lineTo(width/2, center_y - draw_height/3)
            path.lineTo(width/2, center_y + draw_height/3)
            path.lineTo(width - margin, center_y - draw_height/3)
            painter.drawPath(path)
            
        elif wave_type == "square":
            path = QPainterPath()
            path.moveTo(margin, center_y - draw_height/3)
            path.lineTo(width/2, center_y - draw_height/3)
            path.lineTo(width/2, center_y + draw_height/3)
            path.lineTo(width - margin, center_y + draw_height/3)
            painter.drawPath(path)
            
        elif wave_type == "pulse":
            path = QPainterPath()
            path.moveTo(margin, center_y - draw_height/3)
            path.lineTo(width/3, center_y - draw_height/3)
            path.lineTo(width/3, center_y + draw_height/3)
            path.lineTo(width - margin, center_y + draw_height/3)
            painter.drawPath(path)
            
        elif wave_type == "triangle":
            path = QPainterPath()
            path.moveTo(margin, center_y + draw_height/3)
            path.lineTo(width/4, center_y - draw_height/3)
            path.lineTo(3*width/4, center_y + draw_height/3)
            path.lineTo(width - margin, center_y - draw_height/3)
            painter.drawPath(path)
            
        elif wave_type == "sine":
            path = QPainterPath()
            path.moveTo(margin, center_y)
            
            # Draw sine wave using cubic bezier curves
            amp = draw_height/3
            path.cubicTo(
                QPointF(width/4, center_y - amp),
                QPointF(width/4, center_y - amp),
                QPointF(width/2, center_y)
            )
            path.cubicTo(
                QPointF(3*width/4, center_y + amp),
                QPointF(3*width/4, center_y + amp),
                QPointF(width - margin, center_y)
            )
            painter.drawPath(path)
            
        elif wave_type == "noise":
            # Draw random peaks
            prev_x = margin
            prev_y = center_y
            step = draw_width / 8
            
            path = QPainterPath()
            path.moveTo(prev_x, prev_y)
            
            for i in range(8):
                x = prev_x + step
                y = center_y + ((-1)**i) * (draw_height/3)
                path.lineTo(x, y)
                prev_x = x
                prev_y = y
                
            painter.drawPath(path) 