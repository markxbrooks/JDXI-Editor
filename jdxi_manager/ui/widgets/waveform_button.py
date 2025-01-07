from PySide6.QtWidgets import QPushButton, QMenu
from PySide6.QtGui import (
    QAction, QIcon, QPainter, QPen, QColor, QPixmap,
    QPainterPath
)
from PySide6.QtCore import Signal, Qt, QSize, QPoint, QRect

class WaveformIcon:
    @staticmethod
    def create(waveform_type, size=QSize(32, 32)):
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#2897B7"), 2))
        
        # Draw area
        width = size.width() - 8
        height = size.height() - 8
        x = 4
        y = size.height() // 2
        
        if waveform_type == "Saw":
            points = [
                QPoint(x, y + height//3),
                QPoint(x + width*3//4, y - height//3),
                QPoint(x + width*3//4, y + height//3),
                QPoint(x + width, y - height//3)
            ]
            painter.drawPolyline(points)
            
        elif waveform_type == "Square":
            points = [
                QPoint(x, y - height//3),
                QPoint(x + width//2, y - height//3),
                QPoint(x + width//2, y + height//3),
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
            segment = width / 2
            amplitude = height / 3
            path.cubicTo(
                x + segment/2, y - amplitude,
                x + segment/2, y - amplitude,
                x + segment, y
            )
            path.cubicTo(
                x + segment*3/2, y + amplitude,
                x + segment*3/2, y + amplitude,
                x + segment*2, y
            )
            painter.drawPath(path)
            
        elif waveform_type == "Super Saw":
            # Draw multiple detuned saw waves
            offsets = [-2, 0, 2]
            for offset in offsets:
                points = [
                    QPoint(x, y + height//3 + offset),
                    QPoint(x + width*3//4, y - height//3 + offset),
                    QPoint(x + width*3//4, y + height//3 + offset),
                    QPoint(x + width, y - height//3 + offset)
                ]
                painter.drawPolyline(points)
                
        elif waveform_type == "Noise":
            # Draw random peaks
            prev_x = x
            prev_y = y
            painter.setPen(QPen(QColor("#2897B7"), 1))
            for i in range(1, 16):
                new_x = x + (width * i // 15)
                new_y = y + (hash(str(i)) % (height//2)) - height//4
                painter.drawLine(prev_x, prev_y, new_x, new_y)
                prev_x, prev_y = new_x, new_y
                
        elif waveform_type.startswith("PCM"):
            # Draw PCM waveform representation
            number = int(waveform_type.split()[-1])
            painter.setPen(QPen(QColor("#2897B7"), 1))
            
            # Create unique pattern for each PCM
            blocks = 4 + (number % 4)  # 4-7 blocks depending on PCM number
            block_width = width // blocks
            
            for i in range(blocks):
                # Use PCM number to create different patterns
                block_height = (hash(str(i + number)) % (height//2))
                rect = QRect(
                    x + i*block_width,
                    y - block_height//2,
                    block_width-1,
                    block_height
                )
                painter.fillRect(rect, QColor("#2897B7"))
        
        painter.end()
        return QIcon(pixmap)

class WaveformButton(QPushButton):
    waveformChanged = Signal(int)
    
    # Complete JD-Xi waveform set with MIDI values
    WAVEFORMS = {
        'Saw': 0,
        'Square': 1,
        'Triangle': 2,
        'Noise': 3,
        'Sine': 4,
        'Super Saw': 5,
        'PCM 1': 6,
        'PCM 2': 7,
        'PCM 3': 8,
        'PCM 4': 9,
        'PCM 5': 10,
        'PCM 6': 11,
        'PCM 7': 12,
        'PCM 8': 13
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_wave = 0
        self.setIconSize(QSize(24, 24))
        self.setStyleSheet("""
            QPushButton {
                min-width: 100px;
                min-height: 32px;
                padding: 2px 6px;
                text-align: right;
                font-size: 10px;
            }
        """)
        
        # Create waveform menu
        self.menu = QMenu(self)
        for wave_name, wave_value in self.WAVEFORMS.items():
            action = QAction(wave_name, self)
            action.setIcon(WaveformIcon.create(wave_name))
            action.setData(wave_value)  # Store the MIDI value
            action.triggered.connect(self._on_wave_selected)
            self.menu.addAction(action)
            
        self.setMenu(self.menu)
        self._update_button_content('Saw')  # Default to Saw
        
    def _update_button_content(self, wave_name):
        """Update button text and icon for given waveform name"""
        self.setText(wave_name)
        self.setIcon(WaveformIcon.create(wave_name))
        
    def _on_wave_selected(self):
        """Handle waveform selection from menu"""
        action = self.sender()
        if action:
            wave_value = action.data()  # Get MIDI value
            wave_name = action.text()   # Get waveform name
            self.current_wave = wave_value
            self._update_button_content(wave_name)
            self.waveformChanged.emit(wave_value)
            
    def setWaveform(self, wave_value):
        """Set waveform by MIDI value"""
        # Find waveform name from value
        for wave_name, value in self.WAVEFORMS.items():
            if value == wave_value:
                self.current_wave = wave_value
                self._update_button_content(wave_name)
                break
            
    def waveform(self):
        """Get current waveform MIDI value"""
        return self.current_wave 