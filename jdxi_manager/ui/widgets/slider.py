from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal
import logging

class Slider(QWidget):
    """Custom slider widget with label and value display"""
    
    valueChanged = Signal(int)  # Signal emitted when value changes
    
    def __init__(self, label: str, min_val: int, max_val: int, callback=None, parent=None):
        """Initialize slider
        
        Args:
            label: Label text
            min_val: Minimum value
            max_val: Maximum value
            callback: Function to call when value changes
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store properties
        self.min_val = min_val
        self.max_val = max_val
        self.callback = callback
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Create label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self._handle_value_changed)
        layout.addWidget(self.slider)
        
        # Create value label
        self.value_label = QLabel(str(min_val))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
    def _handle_value_changed(self, value: int):
        """Handle slider value change
        
        Args:
            value: New slider value
        """
        try:
            # Update value label
            self.value_label.setText(str(value))
            
            # Emit signal
            self.valueChanged.emit(value)
            
            # Call callback if provided
            if callable(self.callback):
                self.callback(value)
            elif self.callback is not None:
                logging.error(f"Invalid callback provided: {self.callback}")
                
        except Exception as e:
            logging.error(f"Error handling slider value change: {str(e)}")
            
    def setValue(self, value: int):
        """Set slider value
        
        Args:
            value: New value
        """
        self.slider.setValue(value)
        
    def value(self) -> int:
        """Get current value
        
        Returns:
            Current slider value
        """
        return self.slider.value() 