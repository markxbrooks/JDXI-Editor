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

from typing import Any

import numpy as np
from numpy import dtype, floating, ndarray
from PySide6.QtCore import QPointF, Signal
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.pitch_env.type import PitchEnvType
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget, PlotConfig, PlotContext


class PitchEnvPlot(BasePlotWidget):
    """Pitch Env Plot"""

    point_moved = Signal(str, float)

    def __init__(
        self,
        width: int = JDXi.UI.Style.ADSR_PLOT_WIDTH,
        height: int = JDXi.UI.Style.ADSR_PLOT_HEIGHT,
        envelope: dict = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)
        self.parent = parent
        # Default envelope parameters (times in ms)
        self.enabled = True
        self.envelope = envelope
        self.set_dimensions(height, width)
        JDXi.UI.Theme.apply_adsr_plot(self)
        # Sample rate for converting times to samples
        self.sample_rate = 256
        self.setMinimumHeight(150)
        self.attack_x = 0.1
        self.decay_x = 0.3
        self.peak_level = 0.5
        self.release_x = 0.7
        self.dragging = None
        if hasattr(self.parent, "envelope_changed"):
            self.parent.envelope_changed.connect(self.set_values)

    def set_values(self, envelope: dict) -> None:
        """
        Update envelope values and trigger address redraw

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        self.update()

    def mousePressEvent(self, event):
        pos = event.position()
        points = {
            PitchEnvType.ATTACK: QPointF(self.attack_x * self.width(), 0),
            PitchEnvType.DECAY: QPointF(
                self.decay_x * self.width(), (1 - self.peak_level) * self.height()
            ),
            PitchEnvType.RELEASE: QPointF(
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
            if self.dragging == PitchEnvType.ATTACK:
                self.attack_x = max(0.01, min(pos.x() / self.width(), 1.0))
            elif self.dragging == PitchEnvType.DECAY:
                self.decay_x = max(
                    self.attack_x + 0.01, min(pos.x() / self.width(), 1.0)
                )
            elif self.dragging == PitchEnvType.RELEASE:
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

    def get_plot_config(self) -> PlotConfig:
        """Get plot configuration with PitchEnvPlot-specific settings."""
        return PlotConfig(
            top_padding=50,
            bottom_padding=80,
            left_padding=80,
            right_padding=50,
        )

    def get_y_range(self) -> tuple[float, float]:
        """Get Y range for PitchEnvPlot (-0.6 to 0.6)."""
        return 0.6, -0.6

    def zero_at_bottom(self) -> bool:
        """PitchEnvPlot does not have zero at bottom (uses y_max/y_min scaling)."""
        return False

    def get_title(self) -> str:
        """Get plot title."""
        return "Pitch Envelope"

    def get_x_label(self) -> str:
        """Get X-axis label."""
        return "Time (s)"

    def get_y_label(self) -> str:
        """Get Y-axis label."""
        return "Pitch"

    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw custom tick marks for PitchEnvPlot."""
        _, _, total_time = self.envelope_parameters()

        # X-axis ticks (time: 0, 2, 4, 6, 8, 10)
        num_ticks = 6
        x_tick_values = [(i / num_ticks) * total_time for i in range(num_ticks + 1)]
        x_tick_labels = [f"{t:.0f}" for t in x_tick_values]
        self.draw_x_axis_ticks(
            ctx,
            tick_values=x_tick_values,
            tick_labels=x_tick_labels,
            tick_length=5,
            label_offset=20,
            position="zero",
            x_max=total_time,
            config=config,
        )

        # Y-axis ticks (from -0.6 to 0.6 in 0.2 steps)
        y_tick_values = [i * 0.2 for i in range(-3, 4)]
        y_tick_labels = [f"{y:.1f}" for y in y_tick_values]
        self.draw_y_axis_ticks(
            ctx,
            tick_values=y_tick_values,
            tick_labels=y_tick_labels,
            tick_length=5,
            label_offset=40,
            zero_at_bottom=False,
            config=config,
        )

    def draw_grid_hook(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw grid for PitchEnvPlot with symmetric grid lines."""
        _, _, total_time = self.envelope_parameters()

        # Custom grid: vertical lines at tick positions, horizontal lines symmetric around zero
        num_ticks = 6
        x_ticks = [(i / num_ticks) * total_time for i in range(1, num_ticks + 1)]

        # Horizontal grid lines: symmetric around zero (positive and negative)
        y_ticks = []
        for i in range(1, 4):
            y_ticks.append(i * 0.2)  # Positive: 0.2, 0.4, 0.6
            y_ticks.append(-i * 0.2)  # Negative: -0.2, -0.4, -0.6

        self.draw_grid_ctx(
            ctx,
            x_ticks=x_ticks,
            y_ticks=y_ticks,
            x_max=total_time,
            zero_at_bottom=False,
            config=config,
        )

    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw PitchEnvPlot envelope data."""
        if not self.enabled:
            return

        envelope, _, total_time = self.envelope_parameters()

        # Draw curve using new helper method
        self.draw_curve_from_array(
            ctx,
            y_values=envelope,
            x_max=total_time,
            sample_rate=self.sample_rate,
            max_points=500,
            zero_at_bottom=False,
            config=config,
        )

    def envelope_parameters(
        self,
    ) -> tuple[ndarray[Any, dtype[floating[Any]]], int, int]:
        """Envelope parameters"""
        attack_time = self.envelope[EnvelopeParameter.ATTACK_TIME] / 1000.0
        decay_time = self.envelope[EnvelopeParameter.DECAY_TIME] / 1000.0
        peak_level = self.envelope[EnvelopeParameter.PEAK_LEVEL]
        initial_level = self.envelope[EnvelopeParameter.INITIAL_LEVEL]

        attack_samples = max(int(attack_time * self.sample_rate), 1)
        decay_samples = max(int(decay_time * self.sample_rate), 1)

        attack = np.linspace(initial_level, peak_level, attack_samples, endpoint=False)
        decay = np.linspace(peak_level, initial_level, decay_samples, endpoint=False)
        envelope = np.concatenate([attack, decay])
        total_samples = len(envelope)
        total_time = 10  # seconds
        return envelope, total_samples, total_time
