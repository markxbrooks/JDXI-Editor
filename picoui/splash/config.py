"""
Configuration for a splash screen.

Declarative :class:`SplashScreenConfig` embeds PicoUI widget specs
(:class:`~picoui.specs.widgets.LogoSpec`, :class:`~picoui.specs.widgets.LabelSpec`,
etc.) consumed by :class:`~picoui.splash.screen.SplashScreen`.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from PySide6.QtCore import Qt

from picoui.dimensions import Dimensions
from picoui.specs.widgets import (
    GroupBoxSpec,
    LabelSpec,
    LogoSpec,
    ProgressBarSpec,
)
from picoui.splash.theme import SplashTheme


def _background_from_style(style: str | None, default: str) -> str:
    """Extract ``background-color`` from a CSS style string when present."""
    if not style:
        return default
    lower = style.lower()
    marker = "background-color:"
    if marker not in lower:
        return default
    part = lower.split(marker, 1)[1].strip().rstrip(";")
    return part.split()[0] if part else default


def group_spec_from_config(config: SplashScreenConfig) -> GroupBoxSpec:
    """Build a :class:`~picoui.specs.widgets.GroupBoxSpec` from splash config."""
    return GroupBoxSpec(
        title=config.title,
        title_fonts=config.theme.title_font,
        title_size=config.theme.title_size,
        foreground_color=config.foreground_color,
    )


@dataclass(frozen=True, slots=True)
class SplashScreenConfig:
    """Appearance and behaviour options for a splash screen."""

    title: str
    subtitle: LabelSpec = field(default_factory=LabelSpec)
    logo: LogoSpec = field(default_factory=LogoSpec)
    progress: ProgressBarSpec = field(default_factory=ProgressBarSpec)
    group: GroupBoxSpec | None = None
    dimensions: Dimensions = field(
        default_factory=lambda: Dimensions(width=500, height=400)
    )
    theme: SplashTheme = field(default_factory=SplashTheme)
    spacing: int = 10
    background_color: str = "black"
    foreground_color: str = "white"
    show_progress: bool = True
    status_text: str = "Starting..."
    credits_text: str | None = None

    @property
    def logo_path(self) -> str | None:
        """Backward-compatible alias for :attr:`logo`.path."""
        return self.logo.path

    @property
    def logo_size(self) -> Dimensions:
        """Backward-compatible alias for :attr:`logo`.size."""
        return self.logo.size

    @classmethod
    def from_title(
        cls,
        title: str,
        *,
        subtitle: LabelSpec | None = None,
        logo: LogoSpec | None = None,
        progress: ProgressBarSpec | None = None,
        group: GroupBoxSpec | None = None,
        dimensions: Dimensions | None = None,
        theme: SplashTheme | None = None,
        spacing: int = 10,
        background_color: str = "black",
        foreground_color: str = "white",
        show_progress: bool = True,
        status_text: str = "Starting...",
        credits_text: str | None = None,
        style: str | None = None,
        logo_path: str | None = None,
    ) -> SplashScreenConfig:
        """
        Build a splash config from a title and optional embedded specs.

        ``style`` is a legacy CSS string; only ``background-color`` is read and
        mapped to :attr:`background_color` when that field is still the default.
        ``logo_path`` is a legacy shortcut for :class:`~picoui.specs.widgets.LogoSpec`.
        """
        resolved_logo = logo
        if resolved_logo is None and logo_path is not None:
            resolved_logo = LogoSpec(path=logo_path)
        if resolved_logo is None:
            resolved_logo = LogoSpec()

        resolved_background = background_color
        if style is not None and background_color == "black":
            resolved_background = _background_from_style(style, background_color)

        return cls(
            title=title,
            subtitle=subtitle or LabelSpec(),
            logo=resolved_logo,
            progress=progress or ProgressBarSpec(),
            group=group,
            dimensions=dimensions or Dimensions(width=500, height=400),
            theme=theme or SplashTheme(),
            spacing=spacing,
            background_color=resolved_background,
            foreground_color=foreground_color,
            show_progress=show_progress,
            status_text=status_text,
            credits_text=credits_text,
        )

    def subtitle_label_spec(self) -> LabelSpec:
        """Return subtitle :class:`~picoui.specs.widgets.LabelSpec` with splash dimensions."""
        width = max(self.dimensions.width - 25, 1)
        dimensions = Dimensions(width=width, height=80)
        base = self.subtitle
        if base.dimensions is not None:
            return base
        return replace(base, dimensions=dimensions)

    def title_label_spec(self) -> LabelSpec:
        """Return the overlay title :class:`~picoui.specs.widgets.LabelSpec`."""
        return LabelSpec(label=self.title, object_name="TitleLabel")

    def status_label_spec(self) -> LabelSpec | None:
        """Return status line spec, or ``None`` when :attr:`status_text` is empty."""
        if not self.status_text:
            return None
        return LabelSpec(
            label=self.status_text,
            object_name="StatusLabel",
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def credits_label_spec(self) -> LabelSpec | None:
        """Return credits line spec, or ``None`` when :attr:`credits_text` is unset."""
        if not self.credits_text:
            return None
        return LabelSpec(
            label=self.credits_text,
            object_name="CreditLabel",
            alignment=Qt.AlignmentFlag.AlignCenter,
            word_wrap=True,
        )

    def subtitle_panel_spec(self) -> LabelSpec | None:
        """Return subtitle spec for the card panel, or ``None`` when there is no text."""
        if not (self.subtitle.label or ""):
            return None
        base = self.subtitle
        alignment = base.alignment or Qt.AlignmentFlag.AlignCenter
        if base.object_name:
            return replace(base, alignment=alignment)
        return replace(
            base,
            object_name="SubtitleLabel",
            alignment=alignment,
        )
