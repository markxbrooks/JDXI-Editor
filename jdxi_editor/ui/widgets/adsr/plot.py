"""
ADSR Plot
==========

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
from PySide6.QtCore import QPointF, Signal
from PySide6.QtGui import (
    QMouseEvent,
)
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.plot.base import BasePlotWidget, PlotConfig, PlotContext


class ADSRPlot(BasePlotWidget):

    point_moved = Signal(int, int)

    def __init__(
        self,
        width: int = 300,
        height: int = 300,
        envelope: dict = None,
        parent: QWidget = None,
    ):
        super().__init__(parent)

        """
        Initialize the ADSRPlot

        :param width: int
        :param height: int
        :param envelope: dict
        :param parent: QWidget
        """
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
        self.sustain_level = 0.5
        self.release_x = 0.7
        self.dragging = None
        if hasattr(self.parent, "envelope_changed"):
            self.parent.envelope_changed.connect(self.set_values)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = event.position()
        points = {
            "attack": QPointF(self.attack_x * self.width(), 0),
            "decay": QPointF(
                self.decay_x * self.width(), (1 - self.sustain_level) * self.height()
            ),
            "release": QPointF(
                self.release_x * self.width(), (1 - self.sustain_level) * self.height()
            ),
        }
        for name, pt in points.items():
            if (pt - pos).manhattanLength() < 15:
                self.dragging = name
                break

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging:
            pos = event.position()
            if self.dragging == "attack":
                self.attack_x = max(0.01, min(pos.x() / self.width(), 1.0))
            elif self.dragging == "decay":
                self.decay_x = max(
                    self.attack_x + 0.01, min(pos.x() / self.width(), 1.0)
                )
            elif self.dragging == "release":
                self.release_x = max(
                    self.decay_x + 0.01, min(pos.x() / self.width(), 1.0)
                )

            self.point_moved.emit(self.dragging, pos.x() / self.width())
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.dragging = None

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        self.enabled = enabled

    def set_values(self, envelope: dict) -> None:
        """Update envelope values and trigger address redraw.
        :param envelope: dict
        """
        self.envelope = envelope
        self.update()

    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw custom tick marks for ADSR plot."""
        _, _, total_time = self.envelope_parameters()

        # X-axis ticks (time)
        num_ticks = 6
        x_tick_values = [(i / num_ticks) * total_time for i in range(num_ticks + 1)]
        x_tick_labels = [f"{t:.1f}" for t in x_tick_values]
        self.draw_x_axis_ticks(
            ctx,
            tick_values=x_tick_values,
            tick_labels=x_tick_labels,
            tick_length=5,
            label_offset=20,
            position="bottom",
            x_max=total_time,
            config=config,
        )

        # Y-axis ticks (amplitude: 0.0 to 1.0 in 0.2 steps)
        y_tick_values = [i * 0.2 for i in range(6)]
        y_tick_labels = [f"{y:.1f}" for y in y_tick_values]
        self.draw_y_axis_ticks(
            ctx,
            tick_values=y_tick_values,
            tick_labels=y_tick_labels,
            tick_length=5,
            label_offset=45,
            zero_at_bottom=True,
            config=config,
        )

    def draw_grid_hook(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw grid for ADSR plot."""
        self.draw_grid_ctx(
            ctx,
            num_vertical_lines=6,
            num_horizontal_lines=5,
            zero_at_bottom=True,
            config=config,
        )

    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        """Draw ADSR envelope data."""
        if not self.enabled:
            return

        envelope, _, total_time = self.envelope_parameters()

        # Draw shaded fill first (this also draws the curve)
        self.draw_shaded_curve_from_array(
            ctx,
            y_values=envelope,
            x_max=total_time,
            sample_rate=self.sample_rate,
            max_points=500,
            zero_at_bottom=True,
            config=config,
        )

        # Draw envelope curve on top (to ensure it's visible above the fill)
        self.draw_curve_from_array(
            ctx,
            y_values=envelope,
            x_max=total_time,
            sample_rate=self.sample_rate,
            max_points=500,
            zero_at_bottom=True,
            config=config,
        )

    def envelope_parameters(self):
        """Compute envelope segments in seconds"""
        attack_time = self.envelope[EnvelopeParameter.ATTACK_TIME] / 1000.0
        decay_time = self.envelope[EnvelopeParameter.DECAY_TIME] / 1000.0
        release_time = self.envelope[EnvelopeParameter.RELEASE_TIME] / 1000.0
        sustain_level = self.envelope[EnvelopeParameter.SUSTAIN_LEVEL]
        peak_level = max(self.envelope[EnvelopeParameter.PEAK_LEVEL] * 2, 0)
        initial_level = self.envelope[EnvelopeParameter.INITIAL_LEVEL]

        # Convert times to sample counts
        attack_samples = int(attack_time * self.sample_rate)
        decay_samples = int(decay_time * self.sample_rate)
        sustain_samples = int(self.sample_rate * 2)  # Fixed 2 seconds sustain
        release_samples = int(release_time * self.sample_rate)

        # Construct the ADSR envelope as one concatenated array
        # Normalized ADSR envelope (peak level = 1.0)
        attack = np.linspace(
            initial_level, peak_level, attack_samples, endpoint=False
        )  # Attack from initial to peak level
        decay = np.linspace(
            peak_level, sustain_level * peak_level, decay_samples, endpoint=False
        )  # Decay to sustain level
        sustain = np.full(
            sustain_samples, sustain_level * peak_level
        )  # Sustain level scaled by peak level
        release = np.linspace(
            sustain_level * peak_level, 0.0, release_samples
        )  # Release from sustain level to 0
        envelope = np.concatenate([attack, decay, sustain, release])

        total_samples = len(envelope)
        total_time = 5  # in seconds
        return envelope, total_samples, total_time

    def get_plot_config(self) -> PlotConfig:
        """Get plot configuration with ADSR-specific settings."""
        return PlotConfig(
            top_padding=50,
            bottom_padding=50,
            left_padding=80,
            right_padding=50,
        )

    def get_y_range(self) -> tuple[float, float]:
        """Get Y range for ADSR plot (0.0 to 1.0)."""
        return 1.0, 0.0

    def zero_at_bottom(self) -> bool:
        """ADSR plot has zero at bottom."""
        return True

    def get_title(self) -> str:
        """Get plot title."""
        return "ADSR Envelope"

    def get_x_label(self) -> str:
        """Get X-axis label."""
        return "Time (s)"

    def get_y_label(self) -> str:
        """Get Y-axis label."""
        return "Amplitude"
