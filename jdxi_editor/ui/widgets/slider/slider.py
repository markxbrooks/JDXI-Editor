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
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen

from jdxi_editor.midi.io.helper import MidiIOHelper


class Slider(QWidget):
    """Custom slider widget with label and value display"""

    rpn_slider_changed = Signal(int)

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
        min_value: int,
        max_value: int,
        midi_helper: MidiIOHelper,
        vertical: bool = False,
        show_value_label: bool = True,
        is_bipolar: bool = False,
        tooltip: str = "",
        draw_center_mark: bool = True,
        draw_tick_marks: bool = True,
        initial_value: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.midi_helper = midi_helper
        self.value_display_format = str  # Default format function
        self.has_center_mark = False
        self.center_value = 0
        self.vertical = vertical
        self.is_bipolar = is_bipolar
        self.draw_center_mark = draw_center_mark
        self.draw_tick_marks = draw_tick_marks
        self.setToolTip(tooltip)

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
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.valueChanged.connect(self._on_valueChanged)

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
            self.setMaximumWidth(100)
        else:
            self.setMinimumHeight(50)
            self.setMaximumHeight(60)
            self.slider.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            layout.addWidget(self.label)  # Label is added before the slider
            layout.addWidget(self.slider)
            self.slider.setValue(initial_value)

        # Create value display

        self.value_label = QLabel(str(min_value))
        self.value_label.setMinimumWidth(20)
        if show_value_label:  # Add value label if needed
            self.value_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter if vertical else Qt.AlignmentFlag.AlignLeft
            )
            layout.addWidget(self.value_label)
        if is_bipolar:
            self.value_label.setText("0")
        self.slider.setInvertedAppearance(False)

    def setLabel(self, text: str):
        if hasattr(self, "label"):
            self.label.setText(text)

    def setValueDisplayFormat(self, format_func):
        """Set custom format function for value display"""
        self.value_display_format = format_func
        self._update_value_label()

    def setCenterMark(self, center_value):
        """Set center mark for bipolar sliders"""
        self.has_center_mark = True
        self.center_value = center_value
        self.update()

    def _on_valueChanged(self, value: int):
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
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.darkGray, 2))
        positions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        slider_rect = self.slider.geometry()
        if self.has_center_mark:
            # Calculate center position
            center_pos = self.slider.style().sliderPositionFromValue(
                self.slider.minimum(),
                self.slider.maximum(),
                self.center_value,
                slider_rect.width(),
            )

            # Draw center mark
            painter.drawLine(
                center_pos + slider_rect.x(),
                slider_rect.y(),
                center_pos + slider_rect.x(),
                slider_rect.y() + slider_rect.height(),
            )
        elif self.vertical:
            # draw tick mark lines perpendicular to the vertical slider
            if self.draw_tick_marks:
                for position in positions:
                    painter.drawLine(
                        slider_rect.x(),
                        slider_rect.y() + (position * slider_rect.height()),
                        slider_rect.x() + slider_rect.width(),
                        slider_rect.y() + (position * slider_rect.height()),
                    )
        else:
            for position in positions:
                painter.drawLine(
                    slider_rect.x() + position * slider_rect.width(),
                    slider_rect.y(),
                    slider_rect.x() + position * slider_rect.width(),
                    slider_rect.y() + slider_rect.height(),
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
