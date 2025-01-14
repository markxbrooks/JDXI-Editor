from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    """Custom slider widget with value display"""
    valueChanged = Signal(int)
    
    def __init__(self, label: str, min_val: int = 0, max_val: int = 127, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)
        
        # Top row with label and value
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(label)
        self.label.setMinimumWidth(50)
        top_row.addWidget(self.label)
        
        # Value display
        self.value_label = QLabel(str(min_val))
        self.value_label.setAlignment(Qt.AlignRight)
        self.value_label.setMinimumWidth(30)
        top_row.addWidget(self.value_label)
        
        layout.addLayout(top_row)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)  # Changed to Horizontal
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(min_val)
        self.slider.setMinimumWidth(150)  # Ensure minimum width for usability
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)

    def _on_value_changed(self, value: int):
        """Handle slider value changes"""
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
        
    def value(self) -> int:
        """Get current value"""
        return self.slider.value()
        
    def setValue(self, value: int):
        """Set current value"""
        self.slider.setValue(value)
        
    def setEnabled(self, enabled: bool):
        """Set enabled state"""
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.label.setEnabled(enabled)
        self.value_label.setEnabled(enabled) 