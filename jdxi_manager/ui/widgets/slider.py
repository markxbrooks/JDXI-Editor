from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSizePolicy
from PySide6.QtCore import Qt, Signal


class Slider(QWidget):
    """Custom slider widget with label and value display"""
    
    valueChanged = Signal(int)
    
    def __init__(self, label: str, min_val: int, max_val: int, vertical: bool = False, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        
        # Main layout
        layout = QVBoxLayout() if vertical else QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.setLayout(layout)
        
        # Create label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Create slider
        self.slider = QSlider(Qt.Orientation.Vertical if vertical else Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.valueChanged.connect(self._on_value_changed)
        
        # Set size policy for vertical sliders
        if vertical:
            self.slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.setMinimumHeight(125)  # 50% of 250px ADSR group height
            layout.setAlignment(self.label, Qt.AlignmentFlag.AlignHCenter)
            layout.setAlignment(self.slider, Qt.AlignmentFlag.AlignHCenter)
        else:
            self.slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
        layout.addWidget(self.slider)
        
        # Create value display
        self.value_label = QLabel(str(min_val))
        self.value_label.setMinimumWidth(30)
        self.value_label.setAlignment(Qt.AlignRight if vertical else Qt.AlignLeft)
        layout.addWidget(self.value_label)
        
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