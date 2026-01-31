"""
Drum Plot Widgets
=================

This module defines plot widgets for drum envelope visualization:
- DrumPitchEnvPlot: Visualizes drum pitch envelope
- DrumTVFEnvPlot: Visualizes drum TVF (Time Variant Filter) envelope
- DrumTVAEnvPlot: Visualizes drum TVA (Time Variant Amplifier) envelope

All plots display 5-level, 4-time-segment envelope curves with interactive visualization.
"""

import numpy as np
from decologr import Decologr as log
from picomidi.constant import Midi
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget, PlotContext


def midi_to_pitch_level(midi_value: int) -> float:
    """Convert MIDI value (1-127, representing -63 to +63) to pitch level (-63.0 to +63.0)."""
    return float(midi_value - 64)


def midi_to_cutoff_level(midi_value: int) -> float:
    """Convert MIDI value (0-127) to cutoff frequency level (0.0 to 127.0)."""
    return float(midi_value)


def midi_to_time_normalized(midi_value: int, max_time: float = 10.0) -> float:
    """Convert MIDI value (0-127) to normalized time (0.0 to max_time seconds)."""
    return (midi_value / Midi.VALUE.MAX.SEVEN_BIT) * max_time


class DrumPitchEnvPlot(BasePlotWidget):
    """Plot widget for drum pitch envelope visualization."""

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
        self.set_dimensions(height, width)
        JDXi.UI.Theme.apply_adsr_plot(self)
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
            self.draw_background(painter)

            envelope_pen = QPen(QColor("orange"), 2)
            axis_pen = self.set_pen(painter)
            grid_pen = QPen(Qt.GlobalColor.darkGray, 1)
            grid_pen.setStyle(Qt.PenStyle.DashLine)
            point_pen = QPen(QColor("orange"), JDXi.UI.Dimensions.CHART.POINT_SIZE)

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

            # Create PlotContext for cleaner API usage
            y_max, y_min = 80.0, -80.0
            ctx = self.create_plot_context(
                painter,
                top_padding=50,
                bottom_padding=80,
                left_padding=80,
                right_padding=50,
                y_max=y_max,
                y_min=y_min,
            )

            # Draw axes (updates ctx.zero_y)
            ctx = self.draw_axes_ctx(ctx, zero_at_bottom=False)

            # Draw custom tick marks using enhanced methods
            num_ticks = 6
            x_tick_values = [(i / num_ticks) * total_time for i in range(num_ticks + 1)]
            x_tick_labels = [f"{t:.1f}" for t in x_tick_values]
            self.draw_x_axis_ticks(
                ctx,
                tick_values=x_tick_values,
                tick_labels=x_tick_labels,
                tick_length=5,
                label_offset=20,
                position="zero",
                x_max=total_time,
            )

            y_tick_values = [i * 20 for i in range(-4, 5)]
            y_tick_labels = [f"{y:+d}" for y in y_tick_values]
            self.draw_y_axis_ticks(
                ctx,
                tick_values=y_tick_values,
                tick_labels=y_tick_labels,
                tick_length=5,
                label_offset=45,
            )

            # Draw labels using PlotContext API
            self.draw_title_ctx(ctx, "Drum Pitch Envelope")
            self.draw_x_axis_label_ctx(ctx, "Time (s)")
            self.draw_y_axis_label_ctx(ctx, "Pitch")

            # Draw custom grid lines using enhanced grid method
            grid_x_ticks = [(i / num_ticks) * total_time for i in range(1, num_ticks)]
            grid_y_ticks = [i * 20 for i in range(-3, 4) if i != 0]
            self.draw_grid_ctx(
                ctx,
                x_ticks=grid_x_ticks,
                y_ticks=grid_y_ticks,
                x_max=total_time,
            )

            if self.enabled and total_samples > 0:
                ctx.painter.setPen(envelope_pen)
                path = QPainterPath()
                num_points = min(500, total_samples)
                indices = np.linspace(0, total_samples - 1, num_points).astype(int)
                for i in indices:
                    if i >= len(envelope_curve):
                        continue
                    t = i / sample_rate
                    x = ctx.value_to_x(t, total_time)
                    y = ctx.value_to_y(envelope_curve[i])
                    if i == indices[0]:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                ctx.painter.drawPath(path)

                ctx.painter.setPen(point_pen)
                level_points = [
                    (0, level_0, "L0"),
                    (time_1, level_1, "L1"),
                    (time_1 + time_2, level_2, "L2"),
                    (time_1 + time_2 + time_3, level_3, "L3"),
                    (time_1 + time_2 + time_3 + time_4, level_4, "L4"),
                ]
                for t, level, label in level_points:
                    x = ctx.value_to_x(t, total_time)
                    y = ctx.value_to_y(level)
                    ctx.painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)
                    ctx.painter.setPen(QPen(QColor("white")))
                    ctx.painter.setFont(QFont("JD LCD Rounded", 8))
                    ctx.painter.drawText(int(x) + 5, int(y) - 5, label)
                    ctx.painter.setPen(point_pen)
        except Exception as ex:
            log.error(f"Error drawing drum pitch envelope plot: {ex}")
        finally:
            painter.end()


class DrumTVFEnvPlot(BasePlotWidget):
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
        self.set_dimensions(height, width)
        JDXi.UI.Theme.apply_adsr_plot(self)
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
            self.draw_background(painter)

            envelope_pen = QPen(QColor("orange"), 2)
            axis_pen = self.set_pen(painter)
            grid_pen = QPen(Qt.GlobalColor.darkGray, 1)
            grid_pen.setStyle(Qt.PenStyle.DashLine)
            point_pen = QPen(QColor("orange"), JDXi.UI.Dimensions.CHART.POINT_SIZE)

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

            # Create temporary context for title and label drawing
            temp_ctx = PlotContext(
                painter=painter,
                left_pad=left_padding,
                plot_w=plot_w,
                plot_h=plot_h,
                top_pad=top_padding,
                y_max=127.0,
                y_min=0.0,
            )
            self.draw_title_ctx(temp_ctx, "TVF Envelope")
            self.draw_x_axis_label_ctx(temp_ctx, "Time (s)")
            self.draw_y_axis_label_ctx(temp_ctx, "Cutoff")

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


class DrumTVAEnvPlot(BasePlotWidget):
    """Plot widget for drum TVA envelope visualization."""

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
        self.set_dimensions(height, width)
        JDXi.UI.Theme.apply_adsr_plot(self)
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
        """Paint the TVA envelope plot"""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            self.draw_background(painter)

            envelope_pen = QPen(QColor("orange"), 2)
            axis_pen = self.set_pen(painter)
            grid_pen = QPen(Qt.GlobalColor.darkGray, 1)
            grid_pen.setStyle(Qt.PenStyle.DashLine)
            point_pen = QPen(QColor("orange"), JDXi.UI.Dimensions.CHART.POINT_SIZE)

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

            # Create temporary context for title and label drawing
            temp_ctx = PlotContext(
                painter=painter,
                left_pad=left_padding,
                plot_w=plot_w,
                plot_h=plot_h,
                top_pad=top_padding,
                y_max=127.0,
                y_min=0.0,
            )
            self.draw_title_ctx(temp_ctx, "TVA Envelope")
            self.draw_x_axis_label_ctx(temp_ctx, "Time (s)")
            self.draw_y_axis_label_ctx(temp_ctx, "Cutoff")

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
            log.error(f"Error drawing TVA envelope plot: {ex}")
        finally:
            painter.end()
