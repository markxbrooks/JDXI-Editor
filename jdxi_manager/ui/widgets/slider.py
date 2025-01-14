from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal

class Slider(QWidget):
    """Custom slider widget with label and value display"""
    
    # Define the value changed signal
    valueChanged = Signal(int)  # Signal emitted when value changes
    
    def __init__(self, label: str, min_val: int, max_val: int, parent=None):
        super().__init__(parent)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Create label
        self.label_widget = QLabel(label)
        self.label_widget.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_widget)
        
        # Create slider
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setTickPosition(QSlider.TicksRight)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)
        
        # Create value display
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Set initial value
        self.setValue((max_val + min_val) // 2)
        
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
                background: #444444;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #CC3333;
                border: none;
                height: 10px;
                width: 10px;
                margin: 0 -3px;
                border-radius: 5px;
            }
            QSlider::add-page:vertical {
                background: #CC3333;
                border-radius: 2px;
            }
            QSlider::sub-page:vertical {
                background: #444444;
                border-radius: 2px;
            }
        """)

    def _on_slider_changed(self, value: int):
        """Internal slot for slider value changes"""
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)

    def value(self) -> int:
        """Get current slider value"""
        return self.slider.value()

    def setValue(self, value: int):
        """Set slider value"""
        self.slider.setValue(value)

    def setEnabled(self, enabled: bool):
        """Enable/disable the slider"""
        super().setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.label_widget.setEnabled(enabled)
        self.value_label.setEnabled(enabled) 