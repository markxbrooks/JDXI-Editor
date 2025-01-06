from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, name, min_val, max_val, center=False, display_format=None, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.center = center
        self.display_format = display_format or self._default_format
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header layout with name and value
        header = QHBoxLayout()
        self.label = QLabel(name)
        self.value_label = QLabel(self.display_format(0))
        self.value_label.setAlignment(Qt.AlignRight)
        self.value_label.setMinimumWidth(45)  # Ensure consistent width
        header.addWidget(self.label)
        header.addWidget(self.value_label)
        layout.addLayout(header)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        if center:
            self.slider.setValue(0)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
    def _default_format(self, value):
        """Default value formatting"""
        if self.center:
            return f"{value:+d}"
        return str(value)
        
    def _on_value_changed(self, value):
        self.value_label.setText(self.display_format(value))
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
        
    def setValue(self, value):
        self.slider.setValue(value) 