"""Reusable Matplotlib figure/canvas widget for Qt."""

from __future__ import annotations

import logging
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from picoui.matplotlib.config import AxesConfig
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from picoui.matplotlib.configure import apply_axes_config

logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends.backend_qt5agg").setLevel(logging.WARNING)


class MatplotlibPlotWidget(QWidget):
    """Qt host for a Matplotlib ``Figure`` / ``FigureCanvas`` / ``Axes``.

    Subclasses supply domain-specific drawing; this base owns figure lifecycle,
    canvas redraw, optional axes styling via :class:`AxesConfig`, and export.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        figsize: tuple[float, float] = (10.0, 8.0),
        dpi: int = 100,
        axes_config: AxesConfig | None = None,
        add_canvas_to_layout: bool = True,
    ) -> None:
        super().__init__(parent)
        self.axes_config = axes_config or AxesConfig()
        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.figure.add_subplot(111)
        self.apply_axes_config()

        if add_canvas_to_layout:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.canvas)

    def apply_axes_config(self, config: AxesConfig | None = None) -> None:
        """Apply title / labels / limits / visibility from ``AxesConfig``."""
        cfg = config or self.axes_config
        self.axes_config = cfg
        apply_axes_config(cfg, self.ax)

    def clear_axes(self) -> None:
        """Clear the current axes without replacing it."""
        self.ax.clear()
        self.apply_axes_config()

    def redraw(self) -> None:
        """Redraw the canvas immediately so Qt shows the latest artists."""
        self.canvas.draw()
        self.canvas.flush_events()

    def export_figure(self, filename: str, *, dpi: int = 300) -> None:
        """export the figure to a file."""
        self.figure.savefig(filename, dpi=dpi, bbox_inches="tight")
