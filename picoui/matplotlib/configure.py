"""Reusable Matplotlib figure/canvas widget for Qt."""

from __future__ import annotations

import logging

from matplotlib.axes import Axes

from picoui.matplotlib.config import AxesConfig

logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends").setLevel(logging.WARNING)
logging.getLogger("matplotlib.backends.backend_qt5agg").setLevel(logging.WARNING)


def apply_axes_config(config: AxesConfig, ax: Axes) -> None:
    """Apply an ``AxesConfig`` to a matplotlib ``Axes`` instance.

    Parameters
    ----------
    config
        Configuration defining axis visibility, limits, labels, and fonts.
    ax
        Matplotlib axes instance to configure.

    Raises
    ------
    TypeError
        If ``config`` is not an ``AxesConfig`` or ``ax`` is not an
        ``matplotlib.axes.Axes`` instance.
    """
    if not isinstance(config, AxesConfig):
        raise TypeError(
            f"config must be an AxesConfig, got {type(config).__name__}"
        )

    if not isinstance(ax, Axes):
        raise TypeError(
            f"ax must be a matplotlib.axes.Axes, got {type(ax).__name__}"
        )

    x_config = config.x_config
    y_config = config.y_config
    title_config = config.title_config

    if x_config.limit is not None:
        ax.set_xlim(-x_config.limit, x_config.limit)

    if y_config.limit is not None:
        ax.set_ylim(-y_config.limit, y_config.limit)

    ax.set_xlabel(
        x_config.label,
        fontsize=x_config.font_config.size,
        fontweight=x_config.font_config.weight,
    )
    ax.set_ylabel(
        y_config.label,
        fontsize=y_config.font_config.size,
        fontweight=y_config.font_config.weight,
    )
    ax.set_title(
        title_config.label,
        fontsize=title_config.font_config.size,
        fontweight=title_config.font_config.weight,
    )

    if config.visible:
        ax.set_axis_on()
    else:
        ax.set_axis_off()
