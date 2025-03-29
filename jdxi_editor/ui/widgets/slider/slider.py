"""
Custom Slider Widget Module

This module defines address custom slider widget (Slider) that combines address QSlider with address label and address value display.
It offers additional functionality including:

- Customizable value display using address format function.
- Support for vertical or horizontal orientation.
- Option to add address visual center mark for bipolar sliders.
- Customizable tick mark positions and intervals.
- Integrated signal (valueChanged) for reacting to slider value changes.

The widget is built using PySide6 and is intended for use in applications requiring address more informative slider,
such as in audio applications or other UIs where real-time feedback is important.

Usage Example:
    from your_module import Slider
    slider = Slider("Volume", 0, 100, vertical=False)
    slider.setValueDisplayFormat(lambda v: f"{v}%")
    slider.valueChanged.connect(handle_value_change)

This module requires PySide6 to be installed.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSizePolicy, QStylePainter, QStyleOptionSlider, QStyle,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QFontMetrics


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
        show_value_label: bool = True,
        is_bipolar: bool = False,
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

        # Create slider
        self.slider = QSlider(
            Qt.Orientation.Vertical if vertical else Qt.Orientation.Horizontal
        )
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.valueChanged.connect(self._on_value_changed)

        # Set size policy for vertical sliders
        if vertical:
            layout.addWidget(self.label)  # Label is added over the slider
            layout.addWidget(self.slider)
            self.slider.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
            )
            self.setMinimumHeight(125)  # 50% of 250px ADSR area height
            layout.setAlignment(self.label, Qt.AlignmentFlag.AlignLeft)
            layout.setAlignment(self.slider, Qt.AlignmentFlag.AlignLeft)
            self.slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            self.slider.setTickInterval(20)
            self.setMinimumWidth(80)
            self.setMaximumWidth(120)
        else:
            self.slider.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            layout.addWidget(self.label) # Label is added before the slider
            layout.addWidget(self.slider)

        # Create value display

        self.value_label = QLabel(str(min_val))
        self.value_label.setMinimumWidth(30)
        if show_value_label: # Add value label if needed
            self.value_label.setAlignment(
                Qt.AlignmentFlag.AlignRight if vertical else Qt.AlignmentFlag.AlignLeft
            )
            layout.addWidget(self.value_label)
        if is_bipolar:
            self.value_label.setText("0")

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

    def paintEventTest(self, event):
        """Custom paint event for additional rendering like value display."""
        super().paintEvent(event)  # Correctly call base class paintEvent

        painter = QPainter(self)
        painter.setPen(QPen(Qt.white))

        curr_value = self.slider.value() / 1000.0  # Corrected value retrieval
        round_value = round(float(curr_value), 2)

        font_metrics = QFontMetrics(self.font())
        text_rect = font_metrics.boundingRect(str(round_value))
        font_width = text_rect.width()
        font_height = text_rect.height()

        rect = self.geometry()

        if self.slider.orientation() == Qt.Horizontal:
            text_x = rect.width() - font_width - 5
            text_y = rect.height() * 0.75
            painter.drawText(QPoint(int(text_x), int(text_y)), str(round_value))

        elif self.slider.orientation() == Qt.Vertical:
            text_x = rect.width() / 2.0 - font_width / 2.0
            text_y = rect.height() - 5
            painter.drawText(QPoint(int(text_x), int(text_y)), str(round_value))

        # Draw the slider itself with tick marks
        style_painter = QStylePainter(self)
        option = QStyleOptionSlider()
        self.slider.initStyleOption(option)
        style_painter.drawComplexControl(QStyle.CC_Slider, option)

        painter.end()

    def paintEventNew(self, event):
        super().paintEvent(event)
        # QSlider.paintEvent(self.slider, event)

        # curr_value = str(self.value() / 1000.00)
        curr_value = str(self.slider.value() / 1000.00)
        round_value = round(float(curr_value), 2)

        painter = QPainter(self)
        painter.setPen(QPen(Qt.white))

        font_metrics = QFontMetrics(self.font())
        text_rect = font_metrics.boundingRect(str(round_value))
        font_width = text_rect.width()
        font_height = text_rect.height()

        rect = self.geometry()
        if self.slider.orientation() == Qt.Horizontal:
            horizontal_x_pos = rect.width() - font_width - 5
            horizontal_y_pos = rect.height() * 0.75

            painter.drawText(QPoint(horizontal_x_pos, int(horizontal_y_pos)), str(round_value))

        elif self.slider.orientation() == Qt.Vertical:
            vertical_x_pos = rect.width() - font_width - 5
            vertical_y_pos = rect.height() * 0.75

            painter.drawText(QPoint(rect.width() / 2.0 - font_width / 2.0, rect.height() - 5), str(round_value))
        else:
            pass

        painter.drawRect(rect)

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
