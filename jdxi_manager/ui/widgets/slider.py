from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    """Custom slider widget with label and value display"""
    
    value_changed = Signal(int)  # Emits new value when changed
    
    def __init__(self, label: str, min_val: int, max_val: int, parent=None):
        """Initialize slider
        
        Args:
            label: Label text
            min_val: Minimum value
            max_val: Maximum value
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Create label
        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        # Create slider
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(int(min_val))
        self.slider.setMaximum(int(max_val))
        self.slider.setTickPosition(QSlider.TicksRight)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
        # Create value display
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Style
        self.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 10px;
            }
            QSlider {
                margin: 5px;
            }
            QSlider::groove:vertical {
                background: #333333;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #B22222;
                border: 1px solid #FF4444;
                height: 10px;
                margin: 0 -8px;
                border-radius: 5px;
            }
            QSlider::handle:vertical:hover {
                background: #FF4444;
            }
        """)
    
    def _on_value_changed(self, value: int):
        """Handle slider value change"""
        self.value_label.setText(str(value))
        self.value_changed.emit(value)
    
    def value(self) -> int:
        """Get current slider value"""
        return self.slider.value()
    
    def setValue(self, value: int):
        """Set slider value"""
        self.slider.setValue(int(value)) 