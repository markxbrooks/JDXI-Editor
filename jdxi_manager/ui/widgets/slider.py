from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
import logging

class Slider(QWidget):
    """Custom slider widget with label and value display"""
    
    valueChanged = Signal(int)
    
    def __init__(self, 
                 label: str, 
                 min_val: int, 
                 max_val: int, 
                 callback=None, 
                 suffix: str = "", 
                 special_zero: str = None):
        """Initialize slider
        
        Args:
            label: Label text
            min_val: Minimum value
            max_val: Maximum value 
            callback: Function to call when value changes
            suffix: Text to append to value display
            special_zero: Special text to display when value is 0
        """
        super().__init__()
        
        # Store parameters
        self.min_val = min_val
        self.max_val = max_val
        self.callback = callback
        self.suffix = suffix
        self.special_zero = special_zero
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Add label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)
        
        # Add value display
        self.value_label = QLabel()
        self.value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.value_label)
        
        # Set initial value
        self.setValue(min_val)
        
    def _on_value_changed(self, value: int):
        """Handle slider value change"""
        try:
            # Update value label
            if value == 0 and self.special_zero:
                self.value_label.setText(self.special_zero)
            else:
                self.value_label.setText(f"{value}{self.suffix}")
            
            # Call callback if provided
            if callable(self.callback):
                try:
                    self.callback(value)
                except Exception as e:
                    logging.error(f"Error in slider callback: {str(e)}")
            elif self.callback is not None:
                logging.error(f"Invalid callback provided: {self.callback}")
            
            # Emit signal
            self.valueChanged.emit(value)
            
        except Exception as e:
            logging.error(f"Error handling slider value change: {str(e)}")
    
    def value(self) -> int:
        """Get current value"""
        return self.slider.value()
    
    def setValue(self, value: int):
        """Set slider value"""
        self.slider.setValue(value) 