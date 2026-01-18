"""
Module: drum_tvf
==============

This module defines the `DrumTVFSection` class, which provides a PySide6-based
user interface for editing drum TVF parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum TVF parameters, including
  filter type, cutoff frequency, cutoff velocity curve, env depth, env velocity curve type,
  env velocity sens, env time1 velocity sens, env time4 velocity sens, env time1, env time2,
  env time3, env time4, env level0, env level1, env level2, env level3, and env level4.
- Includes a visual envelope plot showing the 5-level, 4-time-segment TVF envelope curve.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumTVFSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MidiIOHelper()
    editor = DrumTVFSection(midi_helper)
    editor.show()
"""

from typing import Callable

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from picomidi.constant import Midi


def midi_to_cutoff_level(midi_value: int) -> float:
    """Convert MIDI value (0-127) to cutoff frequency level (0.0 to 127.0)."""
    return float(midi_value)


def midi_to_time_normalized(midi_value: int, max_time: float = 10.0) -> float:
    """Convert MIDI value (0-127) to normalized time (0.0 to max_time seconds)."""
    return (midi_value / Midi.VALUE.MAX.SEVEN_BIT) * max_time


class DrumTVFEnvPlot(QWidget):
    """Plot widget for drum TVF envelope visualization."""

    def __init__(
        self,
        width: int = JDXi.UI.Style.ADSR_PLOT_WIDTH,
        height: int = JDXi.UI.Style.ADSR_PLOT_HEIGHT,
        envelope: dict = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.enabled = True
        self.envelope = envelope or {}
        self.setMinimumSize(width, height)
        self.setMaximumHeight(height)
        self.setMaximumWidth(width)

        JDXi.UI.ThemeManager.apply_adsr_plot(self)
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
        """Paint the TVF envelope plot"""
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
            point_pen = QPen(QColor("orange"), JDXi.UI.Dimensions.CHART.POINT_SIZE)
            painter.setFont(QFont("JD LCD Rounded", 10))

            depth = self.envelope.get("depth", 64) - 64  # -63 to +63
            level_0 = midi_to_cutoff_level(self.envelope.get("level_0", 64))
            level_1 = midi_to_cutoff_level(self.envelope.get("level_1", 64))
            level_2 = midi_to_cutoff_level(self.envelope.get("level_2", 64))
            level_3 = midi_to_cutoff_level(self.envelope.get("level_3", 64))
            level_4 = midi_to_cutoff_level(self.envelope.get("level_4", 64))

            # Apply depth scaling (depth affects the envelope shape)
            # Positive depth increases effect, negative inverts
            depth_factor = 1.0 + (depth / 63.0)
            level_0 *= depth_factor
            level_1 *= depth_factor
            level_2 *= depth_factor
            level_3 *= depth_factor
            level_4 *= depth_factor

            # Clamp to valid range
            level_0 = max(0, min(127, level_0))
            level_1 = max(0, min(127, level_1))
            level_2 = max(0, min(127, level_2))
            level_3 = max(0, min(127, level_3))
            level_4 = max(0, min(127, level_4))

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

            # Y range (cutoff frequency: 0 to 127)
            y_max, y_min = 127.0, 0.0

            painter.setPen(axis_pen)
            painter.drawLine(
                left_padding, top_padding, left_padding, top_padding + plot_h
            )
            painter.drawLine(
                left_padding,
                top_padding + plot_h,
                left_padding + plot_w,
                top_padding + plot_h,
            )

            num_ticks = 6
            for i in range(num_ticks + 1):
                x = left_padding + i * plot_w / num_ticks
                painter.drawLine(
                    x, top_padding + plot_h - 5, x, top_padding + plot_h + 5
                )
                time_val = (i / num_ticks) * total_time
                painter.drawText(x - 15, top_padding + plot_h + 20, f"{time_val:.1f}")

            # Y-axis ticks and labels (0-127)
            for i in range(6):
                y_val = i * 25.4  # 0, 25.4, 50.8, 76.2, 101.6, 127
                y = top_padding + plot_h - (y_val / y_max) * plot_h
                painter.drawLine(left_padding - 5, y, left_padding, y)
                painter.drawText(left_padding - 40, y + 5, f"{int(y_val)}")

            painter.setPen(QPen(QColor("orange")))
            painter.setFont(QFont("JD LCD Rounded", 16))
            painter.drawText(
                left_padding + plot_w / 2 - 50, top_padding / 2, "TVF Envelope"
            )

            painter.setPen(QPen(QColor("white")))
            painter.drawText(
                left_padding + plot_w / 2 - 10, top_padding + plot_h + 35, "Time (s)"
            )

            painter.save()
            painter.translate(left_padding - 50, top_padding + plot_h / 2 + 25)
            painter.rotate(-90)
            painter.drawText(0, 0, "Cutoff")
            painter.restore()

            painter.setPen(grid_pen)
            for i in range(1, num_ticks):
                x = left_padding + i * plot_w / num_ticks
                painter.drawLine(x, top_padding, x, top_padding + plot_h)
            for i in range(1, 6):
                y_val = i * 25.4
                y = top_padding + plot_h - (y_val / y_max) * plot_h
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
                    y = top_padding + plot_h - (y_val / y_max) * plot_h
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
                    y = top_padding + plot_h - (level / y_max) * plot_h
                    painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)
                    painter.setPen(QPen(QColor("white")))
                    painter.setFont(QFont("JD LCD Rounded", 8))
                    painter.drawText(int(x) + 5, int(y) - 5, label)
                    painter.setPen(point_pen)
        except Exception as ex:
            log.error(f"Error drawing TVF envelope plot: {ex}")
        finally:
            painter.end()


class DrumTVFSection(DrumBaseSection):
    """Drum TVF Section for the JDXI Editor"""

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
        Initialize the DrumTVFSection

        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        self.controls = controls
        self.midi_helper = midi_helper
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self.envelope = {
            "depth": 64,
            "v_sens": 64,
            "t1_v_sens": 64,
            "t4_v_sens": 64,
            "time_1": 21,
            "time_2": 16,
            "time_3": 40,
            "time_4": 25,
            "level_0": 0,
            "level_1": 127,
            "level_2": 70,
            "level_3": 70,
            "level_4": 0,
        }
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        # --- Main container with controls and plot
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.addStretch()
        self.scrolled_layout.addWidget(main_container)

        self.tvf_tab_widget = QTabWidget()

        # --- Basic TVF controls and envelope controls ---
        controls_icon = JDXi.UI.IconRegistry.get_icon(
            "mdi.tune", color=JDXi.UI.Style.GREY
        )
        self.tvf_tab_widget.addTab(
            self._create_tvf_basic_group(), controls_icon, "Controls"
        )

        # --- TVF Envelope Controls
        envelope_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 1.0)
        envelope_icon = QIcon(base64_to_pixmap(envelope_icon_base64))
        self.tvf_tab_widget.addTab(
            self._create_tvf_env_group(), envelope_icon, "Envelope"
        )

        main_layout.addWidget(self.tvf_tab_widget)
        main_layout.addStretch()

    def _create_tvf_env_group(self) -> QGroupBox:
        """Envelope controls group"""
        envelope_group = QGroupBox("Envelope")
        envelope_group_layout = QHBoxLayout()
        #  --- Left side: Envelope sliders  ---
        envelope_slider_layout = QGridLayout()
        envelope_group.setLayout(envelope_group_layout)

        envelope_group.setStyleSheet(JDXi.UI.Style.ADSR)

        #  --- Create sliders and connect them ---
        row = 0
        depth_param = DrumPartialParam.TVF_ENV_DEPTH
        self.depth_slider = self._create_parameter_slider(
            depth_param, DrumDisplayName.TVF_DEPTH, vertical=True
        )
        self.controls[depth_param] = self.depth_slider
        envelope_slider_layout.addWidget(self.depth_slider, row, 0)
        self.depth_slider.valueChanged.connect(
            lambda v: self._update_envelope("depth", v, depth_param)
        )

        v_sens_param = DrumPartialParam.TVF_ENV_VELOCITY_SENS
        self.v_sens_slider = self._create_parameter_slider(
            v_sens_param, DrumDisplayName.TVF_V_SENS, vertical=True
        )
        self.controls[v_sens_param] = self.v_sens_slider
        envelope_slider_layout.addWidget(self.v_sens_slider, row, 1)
        self.v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("v_sens", v, v_sens_param)
        )

        t1_v_sens_param = DrumPartialParam.TVF_ENV_TIME_1_VELOCITY_SENS
        self.t1_v_sens_slider = self._create_parameter_slider(
            t1_v_sens_param, DrumDisplayName.TVF_T1_V_SENS, vertical=True
        )
        self.controls[t1_v_sens_param] = self.t1_v_sens_slider
        envelope_slider_layout.addWidget(self.t1_v_sens_slider, row, 2)
        self.t1_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("t1_v_sens", v, t1_v_sens_param)
        )

        t4_v_sens_param = DrumPartialParam.TVF_ENV_TIME_4_VELOCITY_SENS
        self.t4_v_sens_slider = self._create_parameter_slider(
            t4_v_sens_param, DrumDisplayName.TVF_T4_V_SENS, vertical=True
        )
        self.controls[t4_v_sens_param] = self.t4_v_sens_slider
        envelope_slider_layout.addWidget(self.t4_v_sens_slider, row, 3)
        self.t4_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("t4_v_sens", v, t4_v_sens_param)
        )

        row += 1
        #  --- Time controls  ---
        time_1_param = DrumPartialParam.TVF_ENV_TIME_1
        self.time_1_slider = self._create_parameter_slider(
            time_1_param, DrumDisplayName.TVF_TIME_1, vertical=True
        )
        self.controls[time_1_param] = self.time_1_slider
        envelope_slider_layout.addWidget(self.time_1_slider, row, 0)
        self.time_1_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_1", v, time_1_param)
        )

        time_2_param = DrumPartialParam.TVF_ENV_TIME_2
        self.time_2_slider = self._create_parameter_slider(
            time_2_param, DrumDisplayName.TVF_TIME_2, vertical=True
        )
        self.controls[time_2_param] = self.time_2_slider
        envelope_slider_layout.addWidget(self.time_2_slider, row, 1)
        self.time_2_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_2", v, time_2_param)
        )

        time_3_param = DrumPartialParam.TVF_ENV_TIME_3
        self.time_3_slider = self._create_parameter_slider(
            time_3_param, DrumDisplayName.TVF_TIME_3, vertical=True
        )
        self.controls[time_3_param] = self.time_3_slider
        envelope_slider_layout.addWidget(self.time_3_slider, row, 2)
        self.time_3_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_3", v, time_3_param)
        )

        time_4_param = DrumPartialParam.TVF_ENV_TIME_4
        self.time_4_slider = self._create_parameter_slider(
            time_4_param, DrumDisplayName.TVF_TIME_4, vertical=True
        )
        self.controls[time_4_param] = self.time_4_slider
        envelope_slider_layout.addWidget(self.time_4_slider, row, 3)
        self.time_4_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_4", v, time_4_param)
        )

        row += 1
        #  --- Level controls ---
        level_0_param = DrumPartialParam.TVF_ENV_LEVEL_0
        self.level_0_slider = self._create_parameter_slider(
            level_0_param, DrumDisplayName.TVF_LEVEL_0, vertical=True
        )
        self.controls[level_0_param] = self.level_0_slider
        envelope_slider_layout.addWidget(self.level_0_slider, row, 0)
        self.level_0_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_0", v, level_0_param)
        )

        level_1_param = DrumPartialParam.TVF_ENV_LEVEL_1
        self.level_1_slider = self._create_parameter_slider(
            level_1_param, DrumDisplayName.TVF_LEVEL_1, vertical=True
        )
        self.controls[level_1_param] = self.level_1_slider
        envelope_slider_layout.addWidget(self.level_1_slider, row, 1)
        self.level_1_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_1", v, level_1_param)
        )

        level_2_param = DrumPartialParam.TVF_ENV_LEVEL_2
        self.level_2_slider = self._create_parameter_slider(
            level_2_param, DrumDisplayName.TVF_LEVEL_2, vertical=True
        )
        self.controls[level_2_param] = self.level_2_slider
        envelope_slider_layout.addWidget(self.level_2_slider, row, 2)
        self.level_2_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_2", v, level_2_param)
        )

        level_3_param = DrumPartialParam.TVF_ENV_LEVEL_3
        self.level_3_slider = self._create_parameter_slider(
            level_3_param, DrumDisplayName.TVF_LEVEL_3, vertical=True
        )
        self.controls[level_3_param] = self.level_3_slider
        envelope_slider_layout.addWidget(self.level_3_slider, row, 3)
        self.level_3_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_3", v, level_3_param)
        )

        level_4_param = DrumPartialParam.TVF_ENV_LEVEL_4
        self.level_4_slider = self._create_parameter_slider(
            level_4_param, DrumDisplayName.TVF_LEVEL_4, vertical=True
        )
        self.controls[level_4_param] = self.level_4_slider
        envelope_slider_layout.addWidget(self.level_4_slider, row, 4)
        self.level_4_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_4", v, level_4_param)
        )

        #  --- Right side: Envelope plot  ---
        envelope_plot_layout = QVBoxLayout()
        self._create_tvf_plot()
        envelope_plot_layout.addWidget(self.plot)

        envelope_group_layout.addLayout(envelope_slider_layout)
        envelope_group_layout.addLayout(envelope_plot_layout)

        return envelope_group

    def _create_tvf_basic_group(self) -> QGroupBox:
        """Basic TVF controls group"""
        basic_tvf_group = QGroupBox("Controls")
        basic_tvf_layout = QFormLayout()
        basic_tvf_group.setLayout(basic_tvf_layout)

        tvf_filter_type_combo = self._create_parameter_combo_box(
            DrumPartialParam.TVF_FILTER_TYPE,
            DrumDisplayName.TVF_FILTER_TYPE,
            options=DrumDisplayOptions.TVF_FILTER_TYPE,
            values=[0, 1, 2, 3, 4, 5, 6],
        )
        basic_tvf_layout.addRow(tvf_filter_type_combo)

        tvf_cutoff_frequency_slider = self._create_parameter_slider(
            DrumPartialParam.TVF_CUTOFF_FREQUENCY, DrumDisplayName.TVF_CUTOFF_FREQUENCY
        )
        basic_tvf_layout.addRow(tvf_cutoff_frequency_slider)

        tvf_cutoff_velocity_curve_spin = self._create_parameter_combo_box(
            DrumPartialParam.TVF_CUTOFF_VELOCITY_CURVE,
            DrumDisplayName.TVF_CUTOFF_VELOCITY_CURVE,
            options=DrumDisplayOptions.TVF_CUTOFF_VELOCITY_CURVE,
            values=[0, 1, 2, 3, 4, 5, 6, 7],
        )
        basic_tvf_layout.addRow(tvf_cutoff_velocity_curve_spin)

        tvf_env_velocity_curve_type_spin = self._create_parameter_combo_box(
            DrumPartialParam.TVF_ENV_VELOCITY_CURVE_TYPE,
            DrumDisplayName.TVF_ENV_VELOCITY_CURVE_TYPE,
            options=DrumDisplayOptions.TVF_ENV_VELOCITY_CURVE_TYPE,
            values=[0, 1, 2, 3, 4, 5, 6, 7],
        )
        basic_tvf_layout.addRow(tvf_env_velocity_curve_type_spin)
        return basic_tvf_group

    def _create_tvf_plot(self):
        self.plot = DrumTVFEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )

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
