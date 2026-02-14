"""
Base Plot Widget
================

Base class for plot widgets that provides common functionality like shaded curve drawing.
"""

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


@dataclass
class PlotContext:
    """
    Context object holding plot state for drawing operations.

    This eliminates the need to pass multiple parameters repeatedly and provides
    coordinate conversion helpers.

    :param painter: QPainter instance for drawing
    :param left_pad: Left padding of the plot area in pixels
    :param plot_w: Width of the plot area in pixels
    :param plot_h: Height of the plot area in pixels
    :param top_pad: Top padding of the plot area in pixels
    :param y_max: Maximum Y value in data coordinates
    :param y_min: Minimum Y value in data coordinates
    :param zero_y: Y coordinate of the zero line in pixels (optional, calculated if not provided)
    """

    painter: QPainter
    left_pad: int
    plot_w: int
    plot_h: int
    top_pad: int
    y_max: float
    y_min: float
    zero_y: Optional[float] = None

    def value_to_x(self, value: float, x_max: float) -> float:
        """
        Convert X data value to pixel coordinate.

        :param value: X value in data coordinates (0 to x_max)
        :param x_max: Maximum X value in data coordinates
        :return: X coordinate in pixels
        """
        if x_max == 0:
            return self.left_pad
        return self.left_pad + (value / x_max) * self.plot_w

    def value_to_y(self, value: float, zero_at_bottom: bool = False) -> float:
        """
        Convert Y data value to pixel coordinate.

        :param value: Y value in data coordinates
        :param zero_at_bottom: If True, zero is at bottom of plot (default: False, uses y_max/y_min scaling)
        :return: Y coordinate in pixels
        """
        if zero_at_bottom:
            # For plots where 0 is at bottom and values go up (like ADSR)
            return self.top_pad + self.plot_h - (value / self.y_max) * self.plot_h

        # For plots with positive and negative values (like pitch envelope)
        # y_max is at top, y_min is at bottom
        return (
            self.top_pad
            + ((self.y_max - value) / (self.y_max - self.y_min)) * self.plot_h
        )


@dataclass
class PlotConfig:
    """
    Configuration for plot appearance.

    Centralizes colors, fonts, padding, and other visual settings.
    """

    top_padding: int = 50
    bottom_padding: int = 80
    left_padding: int = 80
    right_padding: int = 50
    title_font_size: int = 16
    label_font_size: int = 10
    tick_font_size: int = 8
    title_color: QColor = QColor("orange")
    label_color: QColor = QColor("white")
    grid_color: QColor = QColor(Qt.GlobalColor.darkGray)
    envelope_color: QColor = QColor("orange")
    axis_color: QColor = QColor("white")
    point_color: QColor = QColor("orange")
    point_size: int = 6
    envelope_line_width: int = 2
    axis_line_width: int = 1
    grid_line_width: int = 1
    font_family: str = "JD LCD Rounded"


class BasePlotWidget(QWidget):
    """
    Base class for plot widgets that provides common shading functionality.
    """

    def draw_background(self, painter: QPainter) -> None:
        """
        Draw the background gradient for the plot.

        :param painter: QPainter instance
        """
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#321212"))
        gradient.setColorAt(0.3, QColor("#331111"))
        gradient.setColorAt(0.5, QColor("#551100"))
        gradient.setColorAt(0.7, QColor("#331111"))
        gradient.setColorAt(1.0, QColor("#111111"))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#000000"), 0))
        painter.drawRect(0, 0, self.width(), self.height())

    def set_dimensions(self, height: int, width: int):
        """Set address fixed size for the widget (or use layouts as needed)"""
        self.setMinimumSize(width, height)
        self.setMaximumHeight(height)
        self.setMaximumWidth(width)

    def draw_shaded_curve(
        self,
        painter: QPainter,
        path: QPainterPath,
        top_pad: int,
        plot_h: int,
        zero_y: float,
        left_pad: int,
        plot_w: int,
    ) -> None:
        """
        Draw a shaded fill under the curve with a gradient.

        :param painter: QPainter instance
        :param path: QPainterPath representing the curve (may or may not be closed)
        :param top_pad: Top padding of the plot area
        :param plot_h: Height of the plot area
        :param zero_y: Y coordinate of the zero line
        :param left_pad: Left padding of the plot area
        :param plot_w: Width of the plot area
        """
        # --- Create a copy of the path for filling
        fill_path = QPainterPath(path)

        # --- Check if path is already closed by checking the last element type
        element_count = fill_path.elementCount()
        is_closed = False

        if element_count > 0:
            # Get the last element
            last_element = fill_path.elementAt(element_count - 1)
            # Check if last element is a CloseSubpathElement
            # ElementType values: MoveToElement=0, LineToElement=1, CurveToElement=2, CurveToDataElement=3
            # CloseSubpathElement is actually a special case - we check if the path is closed differently
            # Instead, we'll check if the path's bounding rect suggests it's closed, or just always close it
            # The simplest approach: always ensure it's closed to the zero line
            pass

        # Always close the path to zero line
        # Get the current position (last point of the path)
        last_point = fill_path.currentPosition()
        # Close to zero line: go to right edge, then to left edge
        fill_path.lineTo(left_pad + plot_w, zero_y)
        fill_path.lineTo(left_pad, zero_y)
        fill_path.closeSubpath()

        # Fill under curve (subtle LCD style)
        fill_gradient = QLinearGradient(0, top_pad, 0, top_pad + plot_h)
        fill_gradient.setColorAt(0.0, QColor(255, 160, 40, 60))
        fill_gradient.setColorAt(1.0, QColor(255, 160, 40, 10))

        painter.fillPath(fill_path, fill_gradient)

    def draw_grid(
        self,
        painter: QPainter,
        top_pad: int,
        plot_h: int,
        left_pad: int,
        plot_w: int,
        num_vertical_lines: int = 6,
        num_horizontal_lines: int = 5,
        y_min: float = 0.0,
        y_max: float = 1.0,
        y_callback: Optional[Callable[[float], float]] = None,
    ) -> None:
        """
        Draw grid lines matching FilterPlot style.

        :param painter: QPainter instance
        :param top_pad: Top padding of the plot area
        :param plot_h: Height of the plot area
        :param left_pad: Left padding of the plot area
        :param plot_w: Width of the plot area
        :param num_vertical_lines: Number of vertical grid lines (default: 6)
        :param num_horizontal_lines: Number of horizontal grid lines (default: 5)
        :param y_min: Minimum Y value for scaling (default: 0.0)
        :param y_max: Maximum Y value for scaling (default: 1.0)
        :param y_callback: Optional callback function(y_val) -> y_pixel for custom Y coordinate calculation
        """
        grid_pen = QPen(Qt.GlobalColor.darkGray, 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)

        # --- Vertical grid lines
        for i in range(1, num_vertical_lines + 1):
            x = left_pad + i * plot_w / num_vertical_lines
            painter.drawLine(x, top_pad, x, top_pad + plot_h)

        # --- Horizontal grid lines
        for i in range(1, num_horizontal_lines + 1):
            y_val = i * ((y_max - y_min) / num_horizontal_lines)
            if y_callback:
                y = y_callback(y_val)
            else:
                # --- Default: simple linear mapping (for ADSR style: 0.0 at bottom, 1.0 at top)
                y = top_pad + plot_h - (y_val * plot_h)
            painter.drawLine(left_pad, y, left_pad + plot_w, y)

    def draw_title(
        self,
        painter: QPainter,
        title: str,
        left_pad: int,
        plot_w: int,
        top_pad: int,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw a centered title at the top of the plot.

        This method matches the style of draw_title_ctx for consistency.
        Prefer using draw_title_ctx with PlotContext for new code.

        :param painter: QPainter instance
        :param title: Title text to digital
        :param left_pad: Left padding of the plot area
        :param plot_w: Width of the plot area
        :param top_pad: Top padding of the plot area
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        painter.setPen(QPen(config.title_color))
        painter.setFont(self.get_title_font(config))
        title_width = painter.fontMetrics().horizontalAdvance(title)
        painter.drawText(left_pad + (plot_w - title_width) / 2, top_pad / 2, title)

    def draw_x_axis_label(
        self,
        painter: QPainter,
        label: str,
        left_pad: int,
        plot_w: int,
        plot_h: int,
        top_pad: int,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw a centered X-axis label at the bottom of the plot.

        This method matches the style of draw_x_axis_label_ctx for consistency.
        Prefer using draw_x_axis_label_ctx with PlotContext for new code.

        :param painter: QPainter instance
        :param label: Label text to digital
        :param left_pad: Left padding of the plot area
        :param plot_w: Width of the plot area
        :param plot_h: Height of the plot area
        :param top_pad: Top padding of the plot area
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        painter.setPen(QPen(config.label_color))
        painter.setFont(self.get_label_font(config))
        font_metrics = painter.fontMetrics()
        label_width = font_metrics.horizontalAdvance(label)
        painter.drawText(
            left_pad + (plot_w - label_width) / 2, top_pad + plot_h + 35, label
        )

    def draw_y_axis_label(
        self,
        painter: QPainter,
        label: str,
        left_pad: int,
        plot_h: int,
        top_pad: int,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw a rotated Y-axis label on the left side of the plot.

        This method matches the style of draw_y_axis_label_ctx for consistency.
        Prefer using draw_y_axis_label_ctx with PlotContext for new code.

        :param painter: QPainter instance
        :param label: Label text to digital
        :param left_pad: Left padding of the plot area
        :param plot_h: Height of the plot area
        :param top_pad: Top padding of the plot area
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        painter.setPen(QPen(config.label_color))
        painter.setFont(self.get_label_font(config))
        font_metrics = painter.fontMetrics()
        label_width = font_metrics.horizontalAdvance(label)
        painter.save()
        painter.translate(left_pad - 50, top_pad + plot_h / 2 + label_width / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, label)
        painter.restore()

    def set_pen(self, painter: QPainter) -> QPen:
        """
        Set up pens and fonts for plotting.

        :param painter: QPainter instance
        :return: QPen for drawing axes
        """
        orange_pen = QPen(QColor("orange"), 2)
        axis_pen = QPen(QColor("white"))
        painter.setFont(QFont("JD LCD Rounded", 10))
        return axis_pen

    def plot_dimensions(
        self,
        top_padding: int = 50,
        bottom_padding: int = 50,
        left_padding: int = 80,
        right_padding: int = 50,
    ) -> tuple[int, int, int, int]:
        """
        Get plot area dimensions.

        :param top_padding: Top padding (default: 50)
        :param bottom_padding: Bottom padding (default: 50)
        :param left_padding: Left padding (default: 80)
        :param right_padding: Right padding (default: 50)
        :return: Tuple of (left_pad, plot_h, plot_w, top_pad)
        """
        w = self.width()
        h = self.height()
        plot_w = w - left_padding - right_padding
        plot_h = h - top_padding - bottom_padding
        return left_padding, plot_h, plot_w, top_padding

    def create_plot_context(
        self,
        painter: QPainter,
        top_padding: int = 50,
        bottom_padding: int = 50,
        left_padding: int = 80,
        right_padding: int = 50,
        y_max: float = 1.0,
        y_min: float = 0.0,
    ) -> PlotContext:
        """
        Create a PlotContext from current widget dimensions and provided parameters.

        This is a convenience method that combines plot_dimensions() with PlotContext creation.

        :param painter: QPainter instance for drawing
        :param top_padding: Top padding (default: 50)
        :param bottom_padding: Bottom padding (default: 50)
        :param left_padding: Left padding (default: 80)
        :param right_padding: Right padding (default: 50)
        :param y_max: Maximum Y value in data coordinates (default: 1.0)
        :param y_min: Minimum Y value in data coordinates (default: 0.0)
        :return: PlotContext instance
        """
        left_pad, plot_h, plot_w, top_pad = self.plot_dimensions(
            top_padding=top_padding,
            bottom_padding=bottom_padding,
            left_padding=left_padding,
            right_padding=right_padding,
        )
        return PlotContext(
            painter=painter,
            left_pad=left_pad,
            plot_w=plot_w,
            plot_h=plot_h,
            top_pad=top_pad,
            y_max=y_max,
            y_min=y_min,
        )

    def calculate_zero_y(
        self,
        top_pad: int,
        plot_h: int,
        y_max: float,
        y_min: float,
        zero_at_bottom: bool = False,
    ) -> float:
        """
        Calculate the Y coordinate of the zero line.

        :param top_pad: Top padding of the plot area
        :param plot_h: Height of the plot area
        :param y_max: Maximum Y value
        :param y_min: Minimum Y value
        :param zero_at_bottom: If True, zero line is at bottom of plot (default: False, calculated from y_max/y_min)
        :return: Y coordinate of the zero line
        """
        if zero_at_bottom:
            return top_pad + plot_h
        return top_pad + (y_max / (y_max - y_min)) * plot_h

    def draw_axes(
        self,
        axis_pen: QPen,
        left_pad: int,
        painter: QPainter,
        plot_h: int,
        plot_w: int,
        top_pad: int,
        y_max: float,
        y_min: float,
        zero_at_bottom: bool = False,
    ) -> float:
        """
        Draw axes (Y-axis and X-axis at zero line).

        :param axis_pen: Pen for drawing axes
        :param left_pad: Left padding of the plot area
        :param painter: QPainter instance
        :param plot_h: Height of the plot area
        :param plot_w: Width of the plot area
        :param top_pad: Top padding of the plot area
        :param y_max: Maximum Y value
        :param y_min: Minimum Y value
        :param zero_at_bottom: If True, zero line is at bottom of plot (default: False)
        :return: Y coordinate of the zero line
        """
        painter.setPen(axis_pen)
        # --- Y-axis
        painter.drawLine(left_pad, top_pad, left_pad, top_pad + plot_h)
        # --- X-axis at zero line
        zero_y = self.calculate_zero_y(top_pad, plot_h, y_max, y_min, zero_at_bottom)
        painter.drawLine(left_pad, zero_y, left_pad + plot_w, zero_y)
        return zero_y

    # ============================================================================
    # PlotContext-based methods (new API)
    # ============================================================================

    def draw_title_ctx(
        self, ctx: PlotContext, title: str, config: Optional[PlotConfig] = None
    ) -> None:
        """
        Draw a centered title at the top of the plot using PlotContext.

        :param ctx: PlotContext containing plot state
        :param title: Title text to digital
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        ctx.painter.setPen(QPen(config.title_color))
        ctx.painter.setFont(self.get_title_font(config))
        title_width = ctx.painter.fontMetrics().horizontalAdvance(title)
        ctx.painter.drawText(
            ctx.left_pad + (ctx.plot_w - title_width) / 2, ctx.top_pad / 2, title
        )

    def draw_x_axis_label_ctx(
        self, ctx: PlotContext, label: str, config: Optional[PlotConfig] = None
    ) -> None:
        """
        Draw a centered X-axis label at the bottom of the plot using PlotContext.

        :param ctx: PlotContext containing plot state
        :param label: Label text to digital
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        ctx.painter.setPen(QPen(config.label_color))
        ctx.painter.setFont(self.get_label_font(config))
        font_metrics = ctx.painter.fontMetrics()
        label_width = font_metrics.horizontalAdvance(label)
        ctx.painter.drawText(
            ctx.left_pad + (ctx.plot_w - label_width) / 2,
            ctx.top_pad + ctx.plot_h + 35,
            label,
        )

    def draw_y_axis_label_ctx(
        self, ctx: PlotContext, label: str, config: Optional[PlotConfig] = None
    ) -> None:
        """
        Draw a rotated Y-axis label on the left side of the plot using PlotContext.

        :param ctx: PlotContext containing plot state
        :param label: Label text to digital
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        ctx.painter.setPen(QPen(config.label_color))
        ctx.painter.setFont(self.get_label_font(config))
        font_metrics = ctx.painter.fontMetrics()
        label_width = font_metrics.horizontalAdvance(label)
        ctx.painter.save()
        ctx.painter.translate(
            ctx.left_pad - 50, ctx.top_pad + ctx.plot_h / 2 + label_width / 2
        )
        ctx.painter.rotate(-90)
        ctx.painter.drawText(0, 0, label)
        ctx.painter.restore()

    def draw_axes_ctx(
        self,
        ctx: PlotContext,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
    ) -> PlotContext:
        """
        Draw axes (Y-axis and X-axis at zero line) using PlotContext.
        Updates and returns the context with zero_y calculated.

        :param ctx: PlotContext containing plot state
        :param zero_at_bottom: If True, zero line is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: Updated PlotContext with zero_y set
        """
        if config is None:
            config = self.get_plot_config()
        ctx.painter.setPen(self.get_axis_pen(config))
        ctx.painter.setFont(self.get_label_font(config))
        # --- Y-axis
        ctx.painter.drawLine(
            ctx.left_pad, ctx.top_pad, ctx.left_pad, ctx.top_pad + ctx.plot_h
        )
        # --- X-axis at zero line
        ctx.zero_y = self.calculate_zero_y(
            ctx.top_pad, ctx.plot_h, ctx.y_max, ctx.y_min, zero_at_bottom
        )
        ctx.painter.drawLine(
            ctx.left_pad, ctx.zero_y, ctx.left_pad + ctx.plot_w, ctx.zero_y
        )
        return ctx

    def draw_shaded_curve_ctx(self, ctx: PlotContext, path: QPainterPath) -> None:
        """
        Draw a shaded fill under the curve with a gradient using PlotContext.

        :param ctx: PlotContext containing plot state (must have zero_y set)
        :param path: QPainterPath representing the curve (may or may not be closed)
        """
        if ctx.zero_y is None:
            raise ValueError(
                "PlotContext.zero_y must be set before calling draw_shaded_curve_ctx"
            )

        # --- Create a copy of the path for filling
        fill_path = QPainterPath(path)

        # Always close the path to zero line
        # Get the current position (last point of the path)
        last_point = fill_path.currentPosition()
        # Close to zero line: go to right edge, then to left edge
        fill_path.lineTo(ctx.left_pad + ctx.plot_w, ctx.zero_y)
        fill_path.lineTo(ctx.left_pad, ctx.zero_y)
        fill_path.closeSubpath()

        # Fill under curve (subtle LCD style)
        fill_gradient = QLinearGradient(0, ctx.top_pad, 0, ctx.top_pad + ctx.plot_h)
        fill_gradient.setColorAt(0.0, QColor(255, 160, 40, 60))
        fill_gradient.setColorAt(1.0, QColor(255, 160, 40, 10))

        ctx.painter.fillPath(fill_path, fill_gradient)

    def draw_x_axis_ticks(
        self,
        ctx: PlotContext,
        tick_values: list[float],
        tick_labels: Optional[list[str]] = None,
        tick_length: int = 5,
        label_offset: int = 20,
        position: str = "bottom",
        x_max: Optional[float] = None,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw X-axis tick marks and labels.

        :param ctx: PlotContext containing plot state
        :param tick_values: List of X values (in data coordinates) for tick positions
        :param tick_labels: Optional list of label strings (defaults to formatted tick_values)
        :param tick_length: Length of tick marks in pixels (default: 5)
        :param label_offset: Vertical offset for labels in pixels (default: 20)
        :param position: Where to draw ticks - "bottom", "top", or "zero" for zero line (default: "bottom")
        :param x_max: Maximum X value for scaling (required if tick_values are in data coordinates)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if not tick_values:
            return

        # Determine Y position for ticks
        if position == "zero":
            if ctx.zero_y is None:
                raise ValueError("PlotContext.zero_y must be set when position='zero'")
            tick_y = ctx.zero_y
            label_y = ctx.zero_y + label_offset
        elif position == "top":
            tick_y = ctx.top_pad
            label_y = ctx.top_pad - label_offset
        else:  # position == "bottom"
            tick_y = ctx.top_pad + ctx.plot_h
            label_y = ctx.top_pad + ctx.plot_h + label_offset

        # Set up pen and font for ticks
        if config is None:
            config = self.get_plot_config()
        ctx.painter.setPen(QPen(config.label_color))
        ctx.painter.setFont(self.get_tick_font(config))

        # Draw ticks and labels
        for i, tick_value in enumerate(tick_values):
            # Convert tick value to pixel coordinate
            if x_max is not None:
                x = ctx.value_to_x(tick_value, x_max)
            else:
                # Assume tick_values are already in pixel coordinates (0 to plot_w)
                x = ctx.left_pad + tick_value

            # Draw tick mark
            ctx.painter.drawLine(x, tick_y - tick_length, x, tick_y + tick_length)

            # Draw label
            if tick_labels and i < len(tick_labels):
                label = tick_labels[i]
            else:
                # Default formatting
                if isinstance(tick_value, float) and tick_value != int(tick_value):
                    label = f"{tick_value:.1f}"
                else:
                    label = f"{int(tick_value)}"

            label_width = ctx.painter.fontMetrics().horizontalAdvance(label)
            ctx.painter.drawText(x - label_width / 2, label_y, label)

    def draw_y_axis_ticks(
        self,
        ctx: PlotContext,
        tick_values: list[float],
        tick_labels: Optional[list[str]] = None,
        tick_length: int = 5,
        label_offset: int = 45,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw Y-axis tick marks and labels.

        :param ctx: PlotContext containing plot state
        :param tick_values: List of Y values (in data coordinates) for tick positions
        :param tick_labels: Optional list of label strings (defaults to formatted tick_values)
        :param tick_length: Length of tick marks in pixels (default: 5)
        :param label_offset: Horizontal offset for labels in pixels (default: 45)
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if not tick_values:
            return

        if config is None:
            config = self.get_plot_config()

        # Set up pen and font for ticks
        ctx.painter.setPen(QPen(config.label_color))
        ctx.painter.setFont(self.get_tick_font(config))

        # Draw ticks and labels
        for i, tick_value in enumerate(tick_values):
            # Convert tick value to pixel coordinate
            y = ctx.value_to_y(tick_value, zero_at_bottom=zero_at_bottom)

            # Draw tick mark
            ctx.painter.drawLine(ctx.left_pad - tick_length, y, ctx.left_pad, y)

            # Draw label
            if tick_labels and i < len(tick_labels):
                label = tick_labels[i]
            else:
                # Default formatting
                if isinstance(tick_value, float) and tick_value != int(tick_value):
                    label = f"{tick_value:.1f}"
                else:
                    label = f"{int(tick_value)}"

            label_width = ctx.painter.fontMetrics().horizontalAdvance(label)
            ctx.painter.drawText(ctx.left_pad - label_offset, y + 5, label)

    def draw_grid_ctx(
        self,
        ctx: PlotContext,
        x_ticks: Optional[list[float]] = None,
        y_ticks: Optional[list[float]] = None,
        x_max: Optional[float] = None,
        num_vertical_lines: Optional[int] = 6,
        num_horizontal_lines: Optional[int] = 5,
        zero_at_bottom: bool = False,
        y_callback: Optional[Callable[[float], float]] = None,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw grid lines with optional custom tick positions using PlotContext.

        :param ctx: PlotContext containing plot state
        :param x_ticks: Custom X tick positions (in data coordinates), overrides num_vertical_lines
        :param y_ticks: Custom Y tick positions (in data coordinates), overrides num_horizontal_lines
        :param x_max: Maximum X value for scaling (required if x_ticks provided)
        :param num_vertical_lines: Number of vertical grid lines (if x_ticks not provided, default: 6)
        :param num_horizontal_lines: Number of horizontal grid lines (if y_ticks not provided, default: 5)
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param y_callback: Optional callback function(y_val) -> y_pixel for custom Y coordinate calculation
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if config is None:
            config = self.get_plot_config()
        ctx.painter.setPen(self.get_grid_pen(config))

        # --- Vertical grid lines
        if x_ticks is not None:
            # Use custom X tick positions
            if x_max is None:
                raise ValueError("x_max must be provided when x_ticks is specified")
            for tick_value in x_ticks:
                x = ctx.value_to_x(tick_value, x_max)
                ctx.painter.drawLine(x, ctx.top_pad, x, ctx.top_pad + ctx.plot_h)
        else:
            # Use automatic spacing
            if num_vertical_lines is None:
                num_vertical_lines = 6
            for i in range(1, num_vertical_lines + 1):
                x = ctx.left_pad + i * ctx.plot_w / num_vertical_lines
                ctx.painter.drawLine(x, ctx.top_pad, x, ctx.top_pad + ctx.plot_h)

        # --- Horizontal grid lines
        if y_ticks is not None:
            # Use custom Y tick positions
            for tick_value in y_ticks:
                y = ctx.value_to_y(tick_value, zero_at_bottom=zero_at_bottom)
                ctx.painter.drawLine(ctx.left_pad, y, ctx.left_pad + ctx.plot_w, y)
        else:
            # Use automatic spacing
            if num_horizontal_lines is None:
                num_horizontal_lines = 5
            for i in range(1, num_horizontal_lines + 1):
                y_val = i * ((ctx.y_max - ctx.y_min) / num_horizontal_lines)
                if y_callback:
                    y = y_callback(y_val)
                else:
                    # --- Default: simple linear mapping (for ADSR style: 0.0 at bottom, 1.0 at top)
                    if zero_at_bottom:
                        y = ctx.top_pad + ctx.plot_h - (y_val / ctx.y_max) * ctx.plot_h
                    else:
                        y = ctx.top_pad + ctx.plot_h - (y_val * ctx.plot_h)
                ctx.painter.drawLine(ctx.left_pad, y, ctx.left_pad + ctx.plot_w, y)

    # ============================================================================
    # Coordinate Conversion Helpers
    # ============================================================================

    def value_to_x_pixel(self, ctx: PlotContext, value: float, x_max: float) -> float:
        """
        Convert X data value to pixel coordinate using PlotContext.

        :param ctx: PlotContext containing plot state
        :param value: X value in data coordinates (0 to x_max)
        :param x_max: Maximum X value in data coordinates
        :return: X coordinate in pixels
        """
        return ctx.value_to_x(value, x_max)

    def value_to_y_pixel(
        self, ctx: PlotContext, value: float, zero_at_bottom: bool = False
    ) -> float:
        """
        Convert Y data value to pixel coordinate using PlotContext.

        :param ctx: PlotContext containing plot state
        :param value: Y value in data coordinates
        :param zero_at_bottom: If True, zero is at bottom of plot (default: False)
        :return: Y coordinate in pixels
        """
        return ctx.value_to_y(value, zero_at_bottom=zero_at_bottom)

    # ============================================================================
    # PlotConfig and Font/Pen Helpers
    # ============================================================================

    def get_plot_config(self) -> PlotConfig:
        """
        Get plot configuration. Override to customize appearance.

        :return: PlotConfig instance
        """
        return PlotConfig()

    def get_title_font(self, config: Optional[PlotConfig] = None) -> QFont:
        """
        Get font for plot title.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QFont for title
        """
        if config is None:
            config = self.get_plot_config()
        return QFont(config.font_family, config.title_font_size)

    def get_label_font(self, config: Optional[PlotConfig] = None) -> QFont:
        """
        Get font for axis labels.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QFont for labels
        """
        if config is None:
            config = self.get_plot_config()
        return QFont(config.font_family, config.label_font_size)

    def get_tick_font(self, config: Optional[PlotConfig] = None) -> QFont:
        """
        Get font for tick labels.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QFont for ticks
        """
        if config is None:
            config = self.get_plot_config()
        return QFont(config.font_family, config.tick_font_size)

    def get_envelope_pen(self, config: Optional[PlotConfig] = None) -> QPen:
        """
        Get pen for drawing envelope curves.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QPen for envelope
        """
        if config is None:
            config = self.get_plot_config()
        return QPen(config.envelope_color, config.envelope_line_width)

    def get_axis_pen(self, config: Optional[PlotConfig] = None) -> QPen:
        """
        Get pen for drawing axes.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QPen for axes
        """
        if config is None:
            config = self.get_plot_config()
        return QPen(config.axis_color, config.axis_line_width)

    def get_grid_pen(self, config: Optional[PlotConfig] = None) -> QPen:
        """
        Get pen for drawing grid lines.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QPen for grid
        """
        if config is None:
            config = self.get_plot_config()
        return QPen(config.grid_color, config.grid_line_width, Qt.PenStyle.DashLine)

    def get_point_pen(self, config: Optional[PlotConfig] = None) -> QPen:
        """
        Get pen for drawing points.

        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QPen for points
        """
        if config is None:
            config = self.get_plot_config()
        return QPen(config.point_color, config.point_size)

    # ============================================================================
    # Curve Drawing Helpers
    # ============================================================================

    def draw_curve_from_array(
        self,
        ctx: PlotContext,
        y_values: list[float] | np.ndarray,  # type: ignore
        x_max: float,
        sample_rate: float = 1.0,
        max_points: int = 500,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
    ) -> QPainterPath:
        """
        Draw a curve from an array of Y values.

        :param ctx: PlotContext containing plot state
        :param y_values: Array or list of Y values (in data coordinates)
        :param x_max: Maximum X value (total time/duration in data coordinates)
        :param sample_rate: Sample rate for converting indices to time (default: 1.0)
        :param max_points: Maximum number of points to draw (default: 500)
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QPainterPath representing the curve
        """
        import numpy as np

        if config is None:
            config = self.get_plot_config()

        path = QPainterPath()
        total_samples = len(y_values)
        if total_samples == 0:
            return path

        num_points = min(max_points, total_samples)
        indices = np.linspace(0, total_samples - 1, num_points).astype(int)

        for i, idx in enumerate(indices):
            if idx >= len(y_values):
                continue
            t = idx / sample_rate
            x = ctx.value_to_x(t, x_max)
            y = ctx.value_to_y(y_values[idx], zero_at_bottom=zero_at_bottom)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        ctx.painter.setPen(self.get_envelope_pen(config))
        ctx.painter.drawPath(path)
        return path

    def draw_curve_from_points(
        self,
        ctx: PlotContext,
        points: list[tuple[float, float]],
        x_max: float,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
    ) -> QPainterPath:
        """
        Draw a curve from a list of (x, y) tuples in data coordinates.

        :param ctx: PlotContext containing plot state
        :param points: List of (x, y) tuples in data coordinates
        :param x_max: Maximum X value for scaling
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :return: QPainterPath representing the curve
        """
        if config is None:
            config = self.get_plot_config()

        path = QPainterPath()
        if not points:
            return path

        for i, (x_val, y_val) in enumerate(points):
            x = ctx.value_to_x(x_val, x_max)
            y = ctx.value_to_y(y_val, zero_at_bottom=zero_at_bottom)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        ctx.painter.setPen(self.get_envelope_pen(config))
        ctx.painter.drawPath(path)
        return path

    def draw_shaded_curve_from_array(
        self,
        ctx: PlotContext,
        y_values: list[float] | np.ndarray,  # type: ignore
        x_max: float,
        sample_rate: float = 1.0,
        max_points: int = 500,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
    ) -> None:
        """
        Draw a curve with shaded fill from an array of Y values.

        :param ctx: PlotContext containing plot state (must have zero_y set)
        :param y_values: Array or list of Y values (in data coordinates)
        :param x_max: Maximum X value (total time/duration in data coordinates)
        :param sample_rate: Sample rate for converting indices to time (default: 1.0)
        :param max_points: Maximum number of points to draw (default: 500)
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        """
        if ctx.zero_y is None:
            raise ValueError(
                "PlotContext.zero_y must be set before calling draw_shaded_curve_from_array"
            )

        path = self.draw_curve_from_array(
            ctx, y_values, x_max, sample_rate, max_points, zero_at_bottom, config
        )
        self.draw_shaded_curve_ctx(ctx, path)

    # ============================================================================
    # Point Drawing Helpers
    # ============================================================================

    def draw_point(
        self,
        ctx: PlotContext,
        x: float,
        y: float,
        x_max: float,
        label: Optional[str] = None,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
        point_size: Optional[int] = None,
    ) -> None:
        """
        Draw a single point with optional label.

        :param ctx: PlotContext containing plot state
        :param x: X coordinate in data coordinates
        :param y: Y coordinate in data coordinates
        :param x_max: Maximum X value for scaling
        :param label: Optional label text to digital
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :param point_size: Optional point size override (uses config.point_size if not provided)
        """
        if config is None:
            config = self.get_plot_config()

        x_pixel = ctx.value_to_x(x, x_max)
        y_pixel = ctx.value_to_y(y, zero_at_bottom=zero_at_bottom)

        # Draw point
        size = point_size if point_size is not None else config.point_size
        ctx.painter.setPen(self.get_point_pen(config))
        ctx.painter.drawEllipse(
            int(x_pixel) - size // 2, int(y_pixel) - size // 2, size, size
        )

        # Draw label if provided
        if label:
            ctx.painter.setPen(QPen(config.label_color))
            ctx.painter.setFont(self.get_tick_font(config))
            ctx.painter.drawText(int(x_pixel) + size // 2 + 2, int(y_pixel) - 2, label)

    def draw_points(
        self,
        ctx: PlotContext,
        points: list[tuple[float, float, Optional[str]]],
        x_max: float,
        zero_at_bottom: bool = False,
        config: Optional[PlotConfig] = None,
        point_size: Optional[int] = None,
    ) -> None:
        """
        Draw multiple points with optional labels.

        :param ctx: PlotContext containing plot state
        :param points: List of (x, y, label) tuples in data coordinates (label can be None)
        :param x_max: Maximum X value for scaling
        :param zero_at_bottom: Whether zero is at bottom of plot (default: False)
        :param config: Optional PlotConfig (uses get_plot_config() if not provided)
        :param point_size: Optional point size override (uses config.point_size if not provided)
        """
        for point_data in points:
            if len(point_data) == 2:
                x, y = point_data
                label = None
            else:
                x, y, label = point_data
            self.draw_point(ctx, x, y, x_max, label, zero_at_bottom, config, point_size)

    # ============================================================================
    # Template Method Pattern
    # ============================================================================

    def paintEvent(self, event) -> None:
        """
        Template method for painting. Subclasses can override hook methods instead.

        The default implementation provides a structured paintEvent that:
        1. Sets up painter and background
        2. Creates PlotContext
        3. Draws axes
        4. Calls hook methods for customization

        Override individual hook methods rather than paintEvent for better structure.
        """
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            self.draw_background(painter)

            # Get configuration
            config = self.get_plot_config()

            # Calculate dimensions
            left_pad, plot_h, plot_w, top_pad = self.plot_dimensions(
                top_padding=config.top_padding,
                bottom_padding=config.bottom_padding,
                left_padding=config.left_padding,
                right_padding=config.right_padding,
            )

            # Get Y range
            y_max, y_min = self.get_y_range()

            # Create context
            ctx = PlotContext(
                painter=painter,
                left_pad=left_pad,
                plot_w=plot_w,
                plot_h=plot_h,
                top_pad=top_pad,
                y_max=y_max,
                y_min=y_min,
            )

            # Draw axes (updates ctx.zero_y)
            ctx = self.draw_axes_ctx(ctx, zero_at_bottom=self.zero_at_bottom())

            # Hook methods for subclasses
            self.draw_custom_ticks(ctx, config)
            self.draw_labels(ctx, config)
            self.draw_grid_hook(ctx, config)
            self.draw_data(ctx, config)

        finally:
            painter.end()

    def get_y_range(self) -> tuple[float, float]:
        """
        Get Y-axis range. Override to provide custom range.

        :return: Tuple of (y_max, y_min)
        """
        return 1.0, 0.0

    def zero_at_bottom(self) -> bool:
        """
        Specify if zero is at bottom of plot. Override to customize.

        :return: True if zero is at bottom, False otherwise
        """
        return False

    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        """
        Draw custom tick marks. Override to add custom ticks.

        :param ctx: PlotContext containing plot state
        :param config: PlotConfig for appearance settings
        """
        pass

    def draw_labels(self, ctx: PlotContext, config: PlotConfig) -> None:
        """
        Draw title and axis labels. Override to customize labels.

        :param ctx: PlotContext containing plot state
        :param config: PlotConfig for appearance settings
        """
        title = self.get_title()
        x_label = self.get_x_label()
        y_label = self.get_y_label()

        if title:
            self.draw_title_ctx(ctx, title)
        if x_label:
            self.draw_x_axis_label_ctx(ctx, x_label)
        if y_label:
            self.draw_y_axis_label_ctx(ctx, y_label)

    def draw_grid_hook(self, ctx: PlotContext, config: PlotConfig) -> None:
        """
        Draw grid. Override to customize grid drawing.

        :param ctx: PlotContext containing plot state
        :param config: PlotConfig for appearance settings
        """
        # Default: no grid (subclasses can override)
        pass

    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        """
        Draw plot data (envelope, curve, etc.). Override to draw plot-specific data.

        :param ctx: PlotContext containing plot state
        :param config: PlotConfig for appearance settings
        """
        pass

    def get_title(self) -> str:
        """
        Get plot title. Override to provide title.

        :return: Title string
        """
        return ""

    def get_x_label(self) -> str:
        """
        Get X-axis label. Override to provide label.

        :return: X-axis label string
        """
        return ""

    def get_y_label(self) -> str:
        """
        Get Y-axis label. Override to provide label.

        :return: Y-axis label string
        """
        return ""
