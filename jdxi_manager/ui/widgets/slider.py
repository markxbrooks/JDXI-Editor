from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, name, min_val, max_val, center=False, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.center = center
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(name)
        layout.addWidget(self.label)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        if center:
            self.slider.setValue(0)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
        # Value label
        self.value_label = QLabel(str(self.slider.value()))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
    def _on_value_changed(self, value):
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
        
    def setValue(self, value):
        self.slider.setValue(value) 