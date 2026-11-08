"""Matplotlib plot configuration dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FontConfig:
    """Configure font weight and size."""

    weight: str = "normal"
    size: int = 12


@dataclass
class PlotConfigBase:
    """Shared label and font settings for plot elements."""

    label: str = ""
    font_config: FontConfig = field(default_factory=FontConfig)


@dataclass
class TitleConfig(PlotConfigBase):
    """Configure a matplotlib title."""

    font_config: FontConfig = field(
        default_factory=lambda: FontConfig(weight="bold", size=14)
    )


@dataclass
class AxisConfig(PlotConfigBase):
    """Configure a single axis.

    ``limit`` is applied symmetrically as ``(-limit, limit)`` when set.
    """

    limit: float | None = None


@dataclass
class AxesConfig:
    """Configure a matplotlib Axes (title, visibility, and X/Y axes)."""

    visible: bool = True
    title_config: TitleConfig = field(default_factory=TitleConfig)
    x_config: AxisConfig = field(default_factory=AxisConfig)
    y_config: AxisConfig = field(default_factory=AxisConfig)
