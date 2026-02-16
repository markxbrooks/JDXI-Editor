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
from PySide6.QtCore import QPointF, Signal, Qt
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
        parent: "PitchEnvelopeWidget" = None,
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
        self._sync_points_from_envelope()
        self.setMouseTracking(True)

    def set_values(self, envelope: dict) -> None:
        """
        Update envelope values and trigger address redraw

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope or self._default_envelope()
        self._sync_points_from_envelope()
        self.update()

    def _points_to_envelope(self) -> dict:
        total_time = 10.0  # seconds (same as plotting domain)

        attack_time = self.attack_x * total_time
        decay_time = (self.decay_x - self.attack_x) * total_time

        return {
            EnvelopeParameter.ATTACK_TIME: int(attack_time * 1000),
            EnvelopeParameter.DECAY_TIME: int(decay_time * 1000),
            EnvelopeParameter.PEAK_LEVEL: self._bipolar_to_midi(self.peak_level),
            EnvelopeParameter.INITIAL_LEVEL: 0.0,
        }

    def _plot_rect(self):
        cfg = self.get_plot_config()
        return (
            cfg.left_padding,
            cfg.top_padding,
            self.width() - cfg.right_padding,
            self.height() - cfg.bottom_padding,
        )

    def mouseReleaseEvent(self, event):
        self.dragging = None
        self.unsetCursor()

    def _default_envelope(self) -> dict:
        return {
            EnvelopeParameter.ATTACK_TIME: 50,
            EnvelopeParameter.DECAY_TIME: 200,
            EnvelopeParameter.PEAK_LEVEL: 64,  # MIDI center = no modulation (-63..+63)
            EnvelopeParameter.INITIAL_LEVEL: 0.0,
        }

    def mousePressEvent(self, event):
        x, y = event.position().x(), event.position().y()

        left, top, right, bottom = self._plot_rect()
        w = right - left
        h = bottom - top

        points = {
            PitchEnvType.ATTACK: QPointF(left + self.attack_x * w, bottom),
            PitchEnvType.DECAY: QPointF(left + self.decay_x * w, top + (1 - self.peak_level) * h),
            PitchEnvType.RELEASE: QPointF(left + self.release_x * w, top + (1 - self.peak_level) * h),
        }

        for name, pt in points.items():
            if (pt - QPointF(x, y)).manhattanLength() < 12:
                self.dragging = name
                self.setCursor(Qt.ClosedHandCursor)
                return

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return

        x = event.position().x()

        left, top, right, bottom = self._plot_rect()
        w = right - left

        norm_x = (x - left) / w
        norm_x = max(0.0, min(norm_x, 1.0))

        if self.dragging == PitchEnvType.ATTACK:
            self.attack_x = min(norm_x, self.decay_x - 0.02)

        elif self.dragging == PitchEnvType.DECAY:
            self.decay_x = max(self.attack_x + 0.02, min(norm_x, self.release_x - 0.02))

        elif self.dragging == PitchEnvType.RELEASE:
            self.release_x = max(self.decay_x + 0.02, norm_x)

        self.point_moved.emit(self.dragging, norm_x)
        self.update()

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

    def _sync_points_from_envelope(self):
        a = self.envelope[EnvelopeParameter.ATTACK_TIME] / 1000.0
        d = self.envelope[EnvelopeParameter.DECAY_TIME] / 1000.0
        midi_peak = self.envelope[EnvelopeParameter.PEAK_LEVEL]

        total_time = 10.0
        self.attack_x = min(a / total_time, 0.95)
        self.decay_x = min((a + d) / total_time, 0.98)
        self.release_x = 1.0

        # canonical internal representation: bipolar normalized
        self.peak_level = self._midi_to_bipolar(midi_peak)

    def envelope_parameters(
        self,
    ) -> tuple[ndarray[Any, dtype[floating[Any]]], int, int]:
        """Envelope parameters"""
        if not self.envelope:
            self.envelope = self._default_envelope()
        attack_time = self.envelope[EnvelopeParameter.ATTACK_TIME] / 1000.0
        decay_time = self.envelope[EnvelopeParameter.DECAY_TIME] / 1000.0
        peak_level = self.peak_level * 0.6
        initial_level = 0.0

        attack_samples = max(int(attack_time * self.sample_rate), 1)
        decay_samples = max(int(decay_time * self.sample_rate), 1)

        attack = np.linspace(initial_level, peak_level, attack_samples, endpoint=False)
        decay = np.linspace(peak_level, initial_level, decay_samples, endpoint=False)
        envelope = np.concatenate([attack, decay])
        total_samples = len(envelope)
        total_time = 10  # seconds
        return envelope, total_samples, total_time

    def _midi_to_bipolar(self, value: int) -> float:
        return (value - 64) / 63.0  # -1..+1 exact symmetry

    def _bipolar_to_midi(self, value: float) -> int:
        return int(round((value * 63.0) + 64))
