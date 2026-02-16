"""
Pitch Envelope Plot
===================

This module defines the `ADSRPlot` class, address QWidget subclass that visualizes an ADSR (Attack,
Decay, Sustain, Release) envelope using Matplotlib. The plot displays the envelope's progression
over time, with adjustable parameters for attack, decay, sustain, and release times, as well as
initial, peak, and sustain amplitudes.

The plot is rendered in address QWidget, and the background and text colors are customized for better
visibility, with the envelope plotted in orange on address dark gray background.

Classes:
--------
- `ADSRPlot`: A QWidget subclass that generates and displays an ADSR envelope plot.

Methods:
--------
- `__init__(self)`: Initializes the widget and sets up the figure and layout for the plot.
- `plot_envelope(self)`: Generates and plots the ADSR envelope based on the current envelope parameters.
- `set_values(self, envelope)`: Updates the envelope parameters and refreshes the plot.

Customization:
-------------
- The plot background is dark gray (`#333333`), with all plot elements (ticks, labels, title) in
  orange for better visibility against the dark background.
- The time is represented in seconds, and the amplitude in address range from 0 to 1.
"""

import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QPainterPath,
)
from PySide6.QtWidgets import QWidget
from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.adsr.type import ADSRType
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget, PlotConfig, PlotContext


def generate_filter_plot(
    width: float,
    slope: float,
    sample_rate: int,
    duration: float,
    filter_mode: str = "lpf",
) -> np.ndarray:
    """
    Generates a filter frequency response plot based on filter mode.

    :param width: Cutoff frequency position (0.0-1.0)
    :param slope: Filter slope (0.0-1.0)
    :param sample_rate: Sample rate for the plot
    :param duration: Duration of the plot
    :param filter_mode: Filter mode - "lpf", "hpf", "bpf", "bypass"
    :return: numpy array representing the frequency response
    """
    width = max(0.0, min(1.0, width))  # Clip to valid range
    total_samples = int(duration * sample_rate)

    # Normalize filter_mode to lowercase
    filter_mode = filter_mode.lower() if filter_mode else "lpf"

    if filter_mode == "bypass":
        # Bypass: flat line at full amplitude
        envelope = np.full(
            total_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )
        return envelope

    # Calculate slope steepness based on slope parameter
    slope_gradient = 0.5 - (slope * 0.25)

    # Define segments in samples
    period = max(1, sample_rate)  # Avoid divide-by-zero
    cutoff_samples = int(period * width)
    transition_samples = int(period * slope_gradient)

    # At least 1 sample to avoid weird signals
    cutoff_samples = max(1, cutoff_samples)
    transition_samples = max(1, transition_samples)

    if filter_mode == "lpf":
        # Low-pass filter: full amplitude up to cutoff, then rolloff
        # Create the passband (full amplitude up to cutoff)
        passband = np.full(
            cutoff_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )

        # Create transition rolloff
        rolloff = np.linspace(
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            0,
            transition_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Combine together
        envelope = np.concatenate([passband, rolloff], axis=0)

    elif filter_mode == "hpf":
        # High-pass filter: rolloff up to cutoff, then full amplitude
        # Create transition rolloff from 0 to cutoff
        rolloff = np.linspace(
            0,
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            cutoff_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Create the passband (full amplitude after cutoff)
        passband = np.full(
            transition_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )

        # Combine together
        envelope = np.concatenate([rolloff, passband], axis=0)

    elif filter_mode == "bpf":
        # Band-pass filter: rolloff, passband, rolloff
        # Low rolloff (before passband)
        low_rolloff_samples = int(cutoff_samples * 0.3)
        low_rolloff = np.linspace(
            0,
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            low_rolloff_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Passband (middle section)
        passband_samples = int(cutoff_samples * 0.4)
        passband = np.full(
            passband_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )

        # High rolloff (after passband)
        high_rolloff_samples = int(transition_samples * 0.5)
        high_rolloff = np.linspace(
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            0,
            high_rolloff_samples,
            endpoint=False,
            dtype=np.float32,
        )

        # Combine together
        envelope = np.concatenate([low_rolloff, passband, high_rolloff], axis=0)

    else:
        # Default to LPF if unknown mode
        passband = np.full(
            cutoff_samples, JDXi.UI.Constants.FILTER_PLOT_DEPTH, dtype=np.float32
        )
        rolloff = np.linspace(
            JDXi.UI.Constants.FILTER_PLOT_DEPTH,
            0,
            transition_samples,
            endpoint=False,
            dtype=np.float32,
        )
        envelope = np.concatenate([passband, rolloff], axis=0)

    # Trim or pad to match total_samples
    if envelope.size > total_samples:
        envelope = envelope[:total_samples]
    elif envelope.size < total_samples:
        padding = np.zeros(total_samples - envelope.size, dtype=np.float32)
        envelope = np.concatenate([envelope, padding], axis=0)

    return envelope


class FilterPlot(BasePlotWidget):
    def __init__(
        self,
        width: int = JDXi.UI.Style.ADSR_PLOT_WIDTH,
        height: int = JDXi.UI.Style.ADSR_PLOT_HEIGHT,
        envelope: dict = None,
        parent: QWidget = None,
        filter_mode: str = "lpf",
    ):
        super().__init__(parent)
        self.point_moved = None
        self.parent = parent
        # Default envelope parameters (times in ms)
        self.enabled = True
        self.envelope = dict(envelope) if envelope else {}
        self.filter_mode = filter_mode  # Store filter mode
        self.set_dimensions(width=width, height=height)
        JDXi.UI.Theme.apply_adsr_plot(self)
        # Sample rate for converting times to samples
        self.sample_rate = 256
        self.setMinimumHeight(JDXi.UI.Style.ADSR_PLOT_HEIGHT)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.peak_level = 0.5
        self.release_x = 0.7
        self.dragging = None

    def set_filter_mode(self, filter_mode: str) -> None:
        """
        Update filter mode and trigger redraw

        :param filter_mode: str - Filter mode ("lpf", "hpf", "bpf", "bypass")
        :return: None
        """
        self.filter_mode = filter_mode.lower() if filter_mode else "lpf"
        self.update()

    def set_values(self, envelope: dict) -> None:
        """
        Update envelope values and trigger redraw.
        Only use valid envelope keys (e.g. filter_cutoff, slope_param) so drawing does not fail.
        """
        log.message(f"envelope now updated to {envelope}", scope=self.__class__.__name__)
        if not envelope:
            return
        valid = {
            k: v
            for k, v in envelope.items()
            if k is not None and k != ""
        }
        if not valid:
            return
        if self.envelope is None:
            self.envelope = {}
        self.envelope = dict(valid)
        self.update()

    def mousePressEvent(self, event):
        pos = event.position()
        points = {
            "attack": QPointF(self.attack_x * self.width(), 0),
            "decay": QPointF(
                self.decay_x * self.width(), (1 - self.peak_level) * self.height()
            ),
            "release": QPointF(
                self.release_x * self.width(), (1 - self.peak_level) * self.height()
            ),
        }
        for name, pt in points.items():
            if (pt - pos).manhattanLength() < 15:
                self.dragging = name
                break

    def mouseMoveEvent(self, event):
        if self.dragging:
            pos = event.position()
            if self.dragging == ADSRType.ATTACK:
                self.attack_x = max(0.01, min(pos.x() / self.width(), 1.0))
            elif self.dragging == ADSRType.DECAY:
                self.decay_x = max(
                    self.attack_x + 0.01, min(pos.x() / self.width(), 1.0)
                )
            elif self.dragging == ADSRType.RELEASE:
                self.release_x = max(
                    self.decay_x + 0.01, min(pos.x() / self.width(), 1.0)
                )

            self.point_moved.emit(self.dragging, pos.x() / self.width())
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = None

    def setEnabled(self, enabled):
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        self.enabled = enabled

    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw custom tick marks for FilterPlot."""
        _, _, total_time = self.envelope_parameters()

        # X-axis ticks (no labels shown in FilterPlot)
        num_ticks = 6
        x_tick_values = [(i / num_ticks) * total_time for i in range(num_ticks + 1)]
        # Draw ticks without labels
        ctx.painter.setPen(self.get_axis_pen(config))
        for tick_value in x_tick_values:
            x = ctx.value_to_x(tick_value, total_time)
            if ctx.zero_y is not None:
                ctx.painter.drawLine(x, ctx.zero_y, x, ctx.zero_y + 5)

        # Y-axis ticks (from -0.2 to 1.0 in 0.2 steps)
        y_tick_values = [i * 0.2 for i in range(-1, 6)]
        y_tick_labels = [f"{y:.1f}" for y in y_tick_values]
        self.draw_y_axis_ticks(
            ctx,
            tick_values=y_tick_values,
            tick_labels=y_tick_labels,
            tick_length=5,
            label_offset=45,
            zero_at_bottom=False,
            config=config,
        )

    def draw_grid_hook(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw grid for FilterPlot with custom Y callback."""

        def y_callback(y_val):
            return ctx.value_to_y(y_val, zero_at_bottom=False)

        self.draw_grid_ctx(
            ctx,
            num_vertical_lines=6,
            num_horizontal_lines=5,
            zero_at_bottom=False,
            y_callback=y_callback,
            config=config,
        )

    def envelope_parameters(self):
        """Generate filter frequency response based on filter mode"""
        width = self.envelope.get(EnvelopeParameter.FILTER_CUTOFF, 0.5)
        slope = self.envelope.get(EnvelopeParameter.FILTER_SLOPE, 0.0)
        envelope = generate_filter_plot(
            width=width,
            slope=slope,
            sample_rate=self.sample_rate,
            duration=self.envelope.get(EnvelopeParameter.DURATION, 1.0),
            filter_mode=self.filter_mode,
        )
        total_samples = len(envelope)
        total_time = total_samples / self.sample_rate
        return envelope, total_samples, total_time

    def get_plot_config(self) -> PlotConfig:
        """Get plot configuration with FilterPlot-specific settings."""
        return PlotConfig(
            top_padding=50,
            bottom_padding=50,
            left_padding=80,
            right_padding=50,
        )

    def get_y_range(self) -> tuple[float, float]:
        """Get Y range for FilterPlot (-0.2 to 1.2)."""
        return 1.2, -0.2

    def zero_at_bottom(self) -> bool:
        """FilterPlot does not have zero at bottom (uses y_max/y_min scaling)."""
        return False

    def get_x_label(self) -> str:
        """Get X-axis label."""
        return "Frequency (Hz)"

    def get_y_label(self) -> str:
        """Get Y-axis label."""
        return "Voltage (V)"

    def get_title(self) -> str:
        """Get title based on filter mode"""
        filter_mode_upper = self.filter_mode.upper() if self.filter_mode else "LPF"
        if filter_mode_upper == "BYPASS":
            return "Filter Bypass"
        elif filter_mode_upper == "HPF":
            return "HPF Cutoff"
        elif filter_mode_upper == "BPF":
            return "BPF Cutoff"
        else:
            return "LPF Cutoff"

    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw FilterPlot envelope data with vertical line segments."""
        if not self.enabled:
            return

        envelope, total_samples, total_time = self.envelope_parameters()
        samples_per_pixel = max(1, int(total_samples / ctx.plot_w))

        # --- Build fill path (upper envelope only) ---
        curve_path = QPainterPath()
        first_point = True

        for px in range(int(ctx.plot_w)):
            start = px * samples_per_pixel
            end = min(start + samples_per_pixel, total_samples)
            if start >= end:
                continue

            ymax = max(envelope[start:end])
            x = ctx.left_pad + px
            y = ctx.value_to_y(ymax, zero_at_bottom=False)

            if first_point:
                curve_path.moveTo(x, y)
                first_point = False
            else:
                curve_path.lineTo(x, y)

        # Draw shaded fill under the curve
        if ctx.zero_y is not None:
            self.draw_shaded_curve_ctx(ctx, curve_path)

        # --- Draw envelope strokes on top (vertical line segments) ---
        envelope_pen = self.get_envelope_pen(config)
        envelope_pen.setWidth(1)
        envelope_pen.setCapStyle(Qt.FlatCap)
        envelope_pen.setCosmetic(True)
        ctx.painter.setPen(envelope_pen)

        for px in range(int(ctx.plot_w)):
            start = px * samples_per_pixel
            end = min(start + samples_per_pixel, total_samples)
            if start >= end:
                continue

            segment = envelope[start:end]
            ymin = min(segment)
            ymax = max(segment)

            x = ctx.left_pad + px
            y1 = ctx.value_to_y(ymax, zero_at_bottom=False)
            y2 = ctx.value_to_y(ymin, zero_at_bottom=False)

            ctx.painter.drawLine(QPointF(x, y1), QPointF(x, y2))