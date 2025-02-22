from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen


class Slider(QWidget):
    """Custom slider widget with label and value display"""

    # Define tick positions enum to match QSlider
    class TickPosition:
        NoTicks = QSlider.TickPosition.NoTicks
        TicksBothSides = QSlider.TickPosition.TicksBothSides
        TicksAbove = QSlider.TickPosition.TicksAbove
        TicksBelow = QSlider.TickPosition.TicksBelow
        TicksLeft = QSlider.TickPosition.TicksLeft
        TicksRight = QSlider.TickPosition.TicksRight

    valueChanged = Signal(int)

    def __init__(
        self,
        label: str,
        min_val: int,
        max_val: int,
        vertical: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.value_display_format = str  # Default format function
        self.has_center_mark = False
        self.center_value = 0

        # Main layout
        layout = QVBoxLayout() if vertical else QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.setLayout(layout)

        # Create label
        self.label = QLabel(label)
        layout.addWidget(self.label)

        # Create slider
        self.slider = QSlider(
            Qt.Orientation.Vertical if vertical else Qt.Orientation.Horizontal
        )
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.valueChanged.connect(self._on_value_changed)

        # Set size policy for vertical sliders
        if vertical:
            self.slider.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
            )
            self.setMinimumHeight(125)  # 50% of 250px ADSR group height
            layout.setAlignment(self.label, Qt.AlignmentFlag.AlignHCenter)
            layout.setAlignment(self.slider, Qt.AlignmentFlag.AlignHCenter)
            self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            self.slider.setTickInterval(20)
        else:
            self.slider.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )

        layout.addWidget(self.slider)

        # Create value display
        self.value_label = QLabel(str(min_val))
        self.value_label.setMinimumWidth(30)
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight if vertical else Qt.AlignmentFlag.AlignLeft
        )
        layout.addWidget(self.value_label)

    def setValueDisplayFormat(self, format_func):
        """Set custom format function for value display"""
        self.value_display_format = format_func
        self._update_value_label()

    def setCenterMark(self, center_value):
        """Set center mark for bipolar sliders"""
        self.has_center_mark = True
        self.center_value = center_value
        self.update()

    def _on_value_changed(self, value: int):
        """Handle slider value changes"""
        self._update_value_label()
        self.valueChanged.emit(value)

    def _update_value_label(self):
        """Update the value label using current format function"""
        value = self.slider.value()
        self.value_label.setText(self.value_display_format(value))

    def paintEvent(self, event):
        """Override paint event to draw center mark if needed"""
        super().paintEvent(event)
        if self.has_center_mark:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            
            # Calculate center position
            slider_rect = self.slider.geometry()
            center_pos = self.slider.style().sliderPositionFromValue(
                self.slider.minimum(),
                self.slider.maximum(),
                self.center_value,
                slider_rect.width()
            )
            
            # Draw center mark
            painter.drawLine(
                center_pos + slider_rect.x(),
                slider_rect.y(),
                center_pos + slider_rect.x(),
                slider_rect.y() + slider_rect.height()
            )

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

    def setTickPosition(self, position):
        """Set the tick mark position on the slider"""
        self.slider.setTickPosition(position)

    def setTickInterval(self, interval):
        """Set the interval between tick marks"""
        self.slider.setTickInterval(interval)
