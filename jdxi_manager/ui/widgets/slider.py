from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, label, min_val, max_val, center=False, display_format=str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(2)  # Reduced from default
        layout.setContentsMargins(2, 2, 2, 2)  # Reduced margins
        
        # Label
        self.label = QLabel(label)
        self.label.setStyleSheet("font-size: 10px;")  # Added font size
        layout.addWidget(self.label)
        
        # Value display
        self.value_label = QLabel()
        self.value_label.setStyleSheet("font-size: 10px;")  # Added font size
        self.value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.value_label)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedHeight(16)  # Reduced height
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        if center:
            self.slider.setValue(0)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
    def _on_value_changed(self, value):
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
        
    def value(self):
        return self.slider.value()
        
    def setValue(self, value):
        self.slider.setValue(value) 