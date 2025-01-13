from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    """Custom slider widget with label and value display"""
    
    valueChanged = Signal(int)
    
    def __init__(self, min_val: int, max_val: int, default: int = 0, parent=None):
        """Initialize slider
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
            parent: Parent widget
        """
        super().__init__(parent)
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default)
        self.slider.valueChanged.connect(self._on_value_changed)
        
        # Create value label
        self.value_label = QLabel(str(default))
        self.value_label.setMinimumWidth(30)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Add to layout
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        
    def _on_value_changed(self, value):
        """Handle slider value change"""
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
        
    def value(self) -> int:
        """Get current value"""
        return self.slider.value()
        
    def setValue(self, value: int):
        """Set current value"""
        self.slider.setValue(value) 