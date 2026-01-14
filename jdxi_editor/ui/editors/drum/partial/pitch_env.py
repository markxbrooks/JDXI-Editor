"""
Module: drum_pitch_env
================

This module defines the `DrumPitchEnvSection` class, which provides a PySide6-based
user interface for editing drum pitch envelope parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum pitch envelope parameters, including
  pitch env depth, pitch env velocity sens, pitch env time1 velocity sens, pitch env time4 velocity sens,
  pitch env time1, pitch env time2, pitch env time3, pitch env time4, pitch env level0, pitch env level1,
  pitch env level2, pitch env level3, and pitch env level4.
- Includes a visual envelope plot showing the 5-level, 4-time-segment envelope curve.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumPitchEnvSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumPitchEnvSection(midi_helper)
    editor.show()
"""

from typing import Callable

import numpy as np
from decologr import Decologr as log
from picomidi.constant import Midi
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget, QSizePolicy,
)

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


def midi_to_pitch_level(midi_value: int) -> float:
    """Convert MIDI value (1-127, representing -63 to +63) to pitch level (-63.0 to +63.0)."""
    return float(midi_value - 64)


def midi_to_time_normalized(midi_value: int, max_time: float = 10.0) -> float:
    """Convert MIDI value (0-127) to normalized time (0.0 to max_time seconds)."""
    return (midi_value / Midi.VALUE.MAX.SEVEN_BIT) * max_time


class DrumPitchEnvPlot(QWidget):
    """Plot widget for drum pitch envelope visualization."""

    def __init__(
        self,
        width: int = JDXiStyle.ADSR_PLOT_WIDTH,
        height: int = JDXiStyle.ADSR_PLOT_HEIGHT,
        envelope: dict = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.enabled = True
        self.envelope = envelope or {}
        self.setMinimumSize(width, height)
        self.setMaximumHeight(height)
        self.setMaximumWidth(width)
        from jdxi_editor.jdxi.style.theme_manager import JDXiThemeManager

        JDXiThemeManager.apply_adsr_plot(self)
        self.sample_rate = 256
        self.setMinimumHeight(150)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.enabled = enabled

    def set_values(self, envelope: dict) -> None:
        """Update envelope values and refresh plot."""
        self.envelope.update(envelope)
        self.update()

    def paintEvent(self, event):
        """Paint the pitch envelope plot"""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor("#321212"))
            gradient.setColorAt(0.3, QColor("#331111"))
            gradient.setColorAt(0.5, QColor("#551100"))
            gradient.setColorAt(0.7, QColor("#331111"))
            gradient.setColorAt(1.0, QColor("#111111"))
            painter.setBrush(gradient)
            painter.setPen(QPen(QColor("#000000"), 0))
            painter.drawRect(0, 0, self.width(), self.height())

            envelope_pen = QPen(QColor("orange"), 2)
            axis_pen = QPen(QColor("white"), 1)
            grid_pen = QPen(Qt.GlobalColor.darkGray, 1)
            grid_pen.setStyle(Qt.PenStyle.DashLine)
            point_pen = QPen(QColor("orange"), JDXiDimensions.CHART_POINT_SIZE)
            painter.setFont(QFont("JD LCD Rounded", 10))

            depth = self.envelope.get("depth", 64) - 64
            level_0 = midi_to_pitch_level(self.envelope.get("level_0", 64))
            level_1 = midi_to_pitch_level(self.envelope.get("level_1", 64))
            level_2 = midi_to_pitch_level(self.envelope.get("level_2", 64))
            level_3 = midi_to_pitch_level(self.envelope.get("level_3", 64))
            level_4 = midi_to_pitch_level(self.envelope.get("level_4", 64))

            level_0 *= 1.0 + depth / 12.0
            level_1 *= 1.0 + depth / 12.0
            level_2 *= 1.0 + depth / 12.0
            level_3 *= 1.0 + depth / 12.0
            level_4 *= 1.0 + depth / 12.0

            time_1 = midi_to_time_normalized(self.envelope.get("time_1", 64))
            time_2 = midi_to_time_normalized(self.envelope.get("time_2", 64))
            time_3 = midi_to_time_normalized(self.envelope.get("time_3", 64))
            time_4 = midi_to_time_normalized(self.envelope.get("time_4", 64))

            total_time = time_1 + time_2 + time_3 + time_4
            if total_time == 0:
                total_time = 10.0

            sample_rate = self.sample_rate
            t1_samples = max(int(time_1 * sample_rate), 1)
            t2_samples = max(int(time_2 * sample_rate), 1)
            t3_samples = max(int(time_3 * sample_rate), 1)
            t4_samples = max(int(time_4 * sample_rate), 1)

            segment_1 = np.linspace(level_0, level_1, t1_samples, endpoint=False)
            segment_2 = np.linspace(level_1, level_2, t2_samples, endpoint=False)
            segment_3 = np.linspace(level_2, level_3, t3_samples, endpoint=False)
            segment_4 = np.linspace(level_3, level_4, t4_samples, endpoint=True)

            envelope_curve = np.concatenate(
                [segment_1, segment_2, segment_3, segment_4]
            )
            total_samples = len(envelope_curve)

            w, h = self.width(), self.height()
            top_padding, bottom_padding = 50, 80
            left_padding, right_padding = 80, 50
            plot_w = w - left_padding - right_padding
            plot_h = h - top_padding - bottom_padding

            y_max, y_min = 80.0, -80.0

            painter.setPen(axis_pen)
            painter.drawLine(
                left_padding, top_padding, left_padding, top_padding + plot_h
            )
            zero_y = top_padding + ((y_max / (y_max - y_min)) * plot_h)
            painter.drawLine(left_padding, zero_y, left_padding + plot_w, zero_y)

            num_ticks = 6
            for i in range(num_ticks + 1):
                x = left_padding + i * plot_w / num_ticks
                painter.drawLine(x, zero_y - 5, x, zero_y + 5)
                time_val = (i / num_ticks) * total_time
                painter.drawText(x - 15, zero_y + 20, f"{time_val:.1f}")

            for i in range(-4, 5):
                y_val = i * 20
                y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(left_padding - 5, y, left_padding, y)
                painter.drawText(left_padding - 45, y + 5, f"{y_val:+d}")

            painter.setPen(QPen(QColor("orange")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            painter.drawText(
                left_padding + plot_w / 2 - 60, top_padding / 2, "Drum Pitch Envelope"
            )

            painter.setPen(QPen(QColor("white")))
            painter.drawText(
                left_padding + plot_w / 2 - 10, top_padding + plot_h + 35, "Time (s)"
            )

            painter.save()
            painter.translate(left_padding - 50, top_padding + plot_h / 2 + 25)
            painter.rotate(-90)
            painter.drawText(0, 0, "Pitch")
            painter.restore()

            painter.setPen(grid_pen)
            for i in range(1, num_ticks):
                x = left_padding + i * plot_w / num_ticks
                painter.drawLine(x, top_padding, x, top_padding + plot_h)
            for i in range(-3, 4):
                if i == 0:
                    continue
                y_val = i * 20
                y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
                painter.drawLine(left_padding, y, left_padding + plot_w, y)

            if self.enabled and total_samples > 0:
                painter.setPen(envelope_pen)
                points = []
                num_points = min(500, total_samples)
                indices = np.linspace(0, total_samples - 1, num_points).astype(int)
                for i in indices:
                    if i >= len(envelope_curve):
                        continue
                    t = i / sample_rate
                    x = left_padding + (t / total_time) * plot_w
                    y_val = envelope_curve[i]
                    y = top_padding + ((y_max - y_val) / (y_max - y_min)) * plot_h
                    points.append((x, y))
                if points:
                    path = QPainterPath()
                    path.moveTo(*points[0])
                    for pt in points[1:]:
                        path.lineTo(*pt)
                    painter.drawPath(path)

                painter.setPen(point_pen)
                level_points = [
                    (0, level_0, "L0"),
                    (time_1, level_1, "L1"),
                    (time_1 + time_2, level_2, "L2"),
                    (time_1 + time_2 + time_3, level_3, "L3"),
                    (time_1 + time_2 + time_3 + time_4, level_4, "L4"),
                ]
                for t, level, label in level_points:
                    x = left_padding + (t / total_time) * plot_w
                    y = top_padding + ((y_max - level) / (y_max - y_min)) * plot_h
                    painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)
                    painter.setPen(QPen(QColor("white")))
                    painter.setFont(QFont("JD LCD Rounded", 8))
                    painter.drawText(int(x) + 5, int(y) - 5, label)
                    painter.setPen(point_pen)
        except Exception as ex:
            log.error(f"Error drawing drum pitch envelope plot: {ex}")
        finally:
            painter.end()


class DrumPitchEnvSection(QWidget):
    """Drum Pitch Env Section for the JDXI Editor"""

    envelope_changed = Signal(dict)

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        create_parameter_combo_box: Callable,
        create_parameter_slider: Callable,
        midi_helper: MidiIOHelper,
    ):
        super().__init__()
        """
        Initialize the DrumPitchEnvSection

        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.midi_helper = midi_helper
        self.envelope = {
            "depth": 64,
            "v_sens": 64,
            "t1_v_sens": 64,
            "t4_v_sens": 64,
            "time_1": 10,
            "time_2": 10,
            "time_3": 34,
            "time_4": 9,
            "level_0": 0,
            "level_1": 64,
            "level_2": 16,
            "level_3": 15,
            "level_4": -25,
        }
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup UI"""
        self.setMinimumWidth(JDXiDimensions.DRUM_PARTIAL_TAB_MIN_WIDTH)
        # Set size policy to allow vertical expansion
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        scrolled_layout = QVBoxLayout(scrolled_widget)
        scrolled_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(scrolled_widget)

        # Icons row (standardized across editor tabs)
        icon_hlayout = IconRegistry.create_adsr_icons_row()
        scrolled_layout.addLayout(icon_hlayout)

        # Main container with controls and plot
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.addStretch()
        scrolled_layout.addWidget(main_container)

        # Left side: Controls in a grid layout
        controls_group = QGroupBox("Pitch Envelope Controls")
        controls_layout = QGridLayout()
        controls_group.setLayout(controls_layout)
        JDXiThemeManager.apply_adsr_style(controls_group)
        main_layout.addWidget(controls_group)

        # Create sliders and connect them
        row = 0
        depth_param = DrumPartialParam.PITCH_ENV_DEPTH
        self.depth_slider = self._create_parameter_slider(
            depth_param, "Depth", vertical=True
        )
        self.controls[depth_param] = self.depth_slider
        controls_layout.addWidget(self.depth_slider, row, 0)
        self.depth_slider.valueChanged.connect(
            lambda v: self._update_envelope("depth", v, depth_param)
        )

        v_sens_param = DrumPartialParam.PITCH_ENV_VELOCITY_SENS
        self.v_sens_slider = self._create_parameter_slider(
            v_sens_param, "V-Sens", vertical=True
        )
        self.controls[v_sens_param] = self.v_sens_slider
        controls_layout.addWidget(self.v_sens_slider, row, 1)
        self.v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("v_sens", v, v_sens_param)
        )

        t1_v_sens_param = DrumPartialParam.PITCH_ENV_TIME_1_VELOCITY_SENS
        self.t1_v_sens_slider = self._create_parameter_slider(
            t1_v_sens_param, "T1 V-Sens", vertical=True
        )
        self.controls[t1_v_sens_param] = self.t1_v_sens_slider
        controls_layout.addWidget(self.t1_v_sens_slider, row, 2)
        self.t1_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("t1_v_sens", v, t1_v_sens_param)
        )

        t4_v_sens_param = DrumPartialParam.PITCH_ENV_TIME_4_VELOCITY_SENS
        self.t4_v_sens_slider = self._create_parameter_slider(
            t4_v_sens_param, "T4 V-Sens", vertical=True
        )
        self.controls[t4_v_sens_param] = self.t4_v_sens_slider
        controls_layout.addWidget(self.t4_v_sens_slider, row, 3)
        self.t4_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("t4_v_sens", v, t4_v_sens_param)
        )

        row += 1
        # Time controls
        time_1_param = DrumPartialParam.PITCH_ENV_TIME_1
        self.time_1_slider = self._create_parameter_slider(
            time_1_param, "Time 1", vertical=True
        )
        self.controls[time_1_param] = self.time_1_slider
        controls_layout.addWidget(self.time_1_slider, row, 0)
        self.time_1_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_1", v, time_1_param)
        )

        time_2_param = DrumPartialParam.PITCH_ENV_TIME_2
        self.time_2_slider = self._create_parameter_slider(
            time_2_param, "Time 2", vertical=True
        )
        self.controls[time_2_param] = self.time_2_slider
        controls_layout.addWidget(self.time_2_slider, row, 1)
        self.time_2_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_2", v, time_2_param)
        )

        time_3_param = DrumPartialParam.PITCH_ENV_TIME_3
        self.time_3_slider = self._create_parameter_slider(
            time_3_param, "Time 3", vertical=True
        )
        self.controls[time_3_param] = self.time_3_slider
        controls_layout.addWidget(self.time_3_slider, row, 2)
        self.time_3_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_3", v, time_3_param)
        )

        time_4_param = DrumPartialParam.PITCH_ENV_TIME_4
        self.time_4_slider = self._create_parameter_slider(
            time_4_param, "Time 4", vertical=True
        )
        self.controls[time_4_param] = self.time_4_slider
        controls_layout.addWidget(self.time_4_slider, row, 3)
        self.time_4_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_4", v, time_4_param)
        )

        row += 1
        # Level controls
        level_0_param = DrumPartialParam.PITCH_ENV_LEVEL_0
        self.level_0_slider = self._create_parameter_slider(
            level_0_param, "Level 0", vertical=True
        )
        self.controls[level_0_param] = self.level_0_slider
        controls_layout.addWidget(self.level_0_slider, row, 0)
        self.level_0_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_0", v, level_0_param)
        )

        level_1_param = DrumPartialParam.PITCH_ENV_LEVEL_1
        self.level_1_slider = self._create_parameter_slider(
            level_1_param, "Level 1", vertical=True
        )
        self.controls[level_1_param] = self.level_1_slider
        controls_layout.addWidget(self.level_1_slider, row, 1)
        self.level_1_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_1", v, level_1_param)
        )

        level_2_param = DrumPartialParam.PITCH_ENV_LEVEL_2
        self.level_2_slider = self._create_parameter_slider(
            level_2_param, "Level 2", vertical=True
        )
        self.controls[level_2_param] = self.level_2_slider
        controls_layout.addWidget(self.level_2_slider, row, 2)
        self.level_2_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_2", v, level_2_param)
        )

        level_3_param = DrumPartialParam.PITCH_ENV_LEVEL_3
        self.level_3_slider = self._create_parameter_slider(
            level_3_param, "Level 3", vertical=True
        )
        self.controls[level_3_param] = self.level_3_slider
        controls_layout.addWidget(self.level_3_slider, row, 3)
        self.level_3_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_3", v, level_3_param)
        )

        level_4_param = DrumPartialParam.PITCH_ENV_LEVEL_4
        self.level_4_slider = self._create_parameter_slider(
            level_4_param, "Level 4", vertical=True
        )
        self.controls[level_4_param] = self.level_4_slider
        controls_layout.addWidget(self.level_4_slider, row, 4)
        self.level_4_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_4", v, level_4_param)
        )

        # Right side: Envelope plot
        self.plot = DrumPitchEnvPlot(
            width=JDXiStyle.ADSR_PLOT_WIDTH,
            height=JDXiStyle.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )
        main_layout.addWidget(self.plot)
        main_layout.addStretch()

    def _update_envelope(
        self, key: str, value: int, param: DrumPartialParam = None
    ) -> None:
        """Update envelope value and refresh plot

        :param key: str Envelope parameter key
        :param value: int Display value from slider
        :param param: AddressParameterDrumPartial Parameter object for conversion
        """
        # Convert display value to MIDI value if parameter is provided
        if param and hasattr(param, "convert_from_display"):
            midi_value = param.convert_from_display(value)
        else:
            # For parameters without special conversion, assume value is already MIDI
            midi_value = value

        self.envelope[key] = midi_value
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)
