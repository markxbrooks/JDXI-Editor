from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
import logging
from typing import Optional, Callable

class Slider(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, 
                 label: str, 
                 min_val: int, 
                 max_val: int, 
                 callback: Optional[Callable[[int], None]] = None, 
                 suffix: str = "", 
                 special_zero: Optional[str] = None):
        """Initialize slider
        
        Args:
            label: Label text
            min_val: Minimum value
            max_val: Maximum value 
            callback: Function to call when value changes (optional)
            suffix: Text to append to value display (e.g. "%")
            special_zero: Special text to display when value is 0
        """
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        
        # Validate callback
        if callback is not None and not callable(callback):
            logging.error(f"Invalid callback provided to slider '{label}': {callback}")
            self.callback = None
        else:
            self.callback = callback
            
        self.suffix = suffix
        self.special_zero = special_zero
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Label
        self.label = QLabel(label)
        self.label.setStyleSheet("font-size: 10px;")
        layout.addWidget(self.label)
        
        # Value display
        self.value_label = QLabel()
        self.value_label.setStyleSheet("font-size: 10px;")
        self.value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.value_label)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedHeight(16)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
        # Set initial value
        self.setValue(min_val)
        
    def _on_value_changed(self, value: int) -> None:
        """Handle slider value change"""
        # Update value label
        if value == 0 and self.special_zero:
            self.value_label.setText(self.special_zero)
        else:
            self.value_label.setText(f"{value}{self.suffix}")
            
        # Call callback if it exists and is valid
        if self.callback is not None:
            try:
                self.callback(value)
            except Exception as e:
                logging.error(f"Error in slider callback: {str(e)}")
                
        # Emit signal
        self.valueChanged.emit(value)
        
    def value(self) -> int:
        """Get current value"""
        return self.slider.value()
        
    def setValue(self, value: int) -> None:
        """Set slider value"""
        self.slider.setValue(value) 