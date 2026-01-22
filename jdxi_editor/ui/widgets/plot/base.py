"""
Base Plot Widget
================

Base class for plot widgets that provides common functionality like shaded curve drawing.
"""

from typing import Callable, Optional
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


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
        # Create a copy of the path for filling
        fill_path = QPainterPath(path)
        
        # Check if path is already closed by checking the last element type
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
        
        # Always close the path to zero line (it's safe to do even if already closed)
        # Get the current position (last point of the path)
        last_point = fill_path.currentPosition()
        # Close to zero line
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
        
        # Vertical grid lines
        for i in range(1, num_vertical_lines + 1):
            x = left_pad + i * plot_w / num_vertical_lines
            painter.drawLine(x, top_pad, x, top_pad + plot_h)
        
        # Horizontal grid lines
        for i in range(1, num_horizontal_lines + 1):
            y_val = i * ((y_max - y_min) / num_horizontal_lines)
            if y_callback:
                y = y_callback(y_val)
            else:
                # Default: simple linear mapping (for ADSR style: 0.0 at bottom, 1.0 at top)
                y = top_pad + plot_h - (y_val * plot_h)
            painter.drawLine(left_pad, y, left_pad + plot_w, y)

    def draw_title(
        self,
        painter: QPainter,
        title: str,
        left_pad: int,
        plot_w: int,
        top_pad: int,
    ) -> None:
        """
        Draw a centered title at the top of the plot.

        :param painter: QPainter instance
        :param title: Title text to display
        :param left_pad: Left padding of the plot area
        :param plot_w: Width of the plot area
        :param top_pad: Top padding of the plot area
        """
        painter.setPen(QPen(QColor("orange")))
        painter.setFont(QFont("JD LCD Rounded", 16))
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
    ) -> None:
        """
        Draw a centered X-axis label at the bottom of the plot.

        :param painter: QPainter instance
        :param label: Label text to display
        :param left_pad: Left padding of the plot area
        :param plot_w: Width of the plot area
        :param plot_h: Height of the plot area
        :param top_pad: Top padding of the plot area
        """
        painter.setPen(QPen(QColor("white")))
        painter.setFont(QFont("JD LCD Rounded", 10))
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
    ) -> None:
        """
        Draw a rotated Y-axis label on the left side of the plot.

        :param painter: QPainter instance
        :param label: Label text to display
        :param left_pad: Left padding of the plot area
        :param plot_h: Height of the plot area
        :param top_pad: Top padding of the plot area
        """
        painter.setPen(QPen(QColor("white")))
        painter.setFont(QFont("JD LCD Rounded", 10))
        font_metrics = painter.fontMetrics()
        label_width = font_metrics.horizontalAdvance(label)
        painter.save()
        painter.translate(left_pad - 50, top_pad + plot_h / 2 + label_width / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, label)
        painter.restore()
