"""Shared JDXI-style splash panel layout (card, labels, optional progress)."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget, QHBoxLayout

from picoui.helpers.layout import (
    create_layout,
    create_layout_with_items,
    create_progress_bar_from_spec,
)
from picoui.specs.widgets import LabelSpec
from picoui.splash.config import SplashScreenConfig
from picoui.splash.styles import SPLASH_CONTENT_SPACING, SPLASH_PROGRESS_WIDTH_INSET
from picoui.widget.helper import create_label_from_spec, create_logo_label_from_spec


@dataclass(slots=True)
class SplashPanelWidgets:
    """Widgets created by :func:`build_jdxi_splash_panel`."""

    card: QFrame
    progress_bar: QProgressBar | None
    status_label: QLabel | None
    title_label: QLabel


def _add_label_from_spec(
    layout: QVBoxLayout | QHBoxLayout,
    spec: LabelSpec | None,
    parent: QWidget,
) -> QLabel | None:
    """Create a label from *spec* and append it to *layout*."""
    if spec is None:
        return None
    label = create_label_from_spec(spec, parent=parent)
    layout.addWidget(label)
    return label


def build_splash_panel(
    parent: QWidget,
    config: SplashScreenConfig,
    *,
    show_progress: bool | None = None,
    show_status: bool | None = None,
) -> SplashPanelWidgets:
    """
    Build the card panel on *parent*, based on the JDXI splash screen.

    Returns the card frame and key child widgets. The title label is created
    parented to *parent* for overlay positioning by the caller.
    """
    include_progress = config.show_progress if show_progress is None else show_progress
    include_status = bool(config.status_text) if show_status is None else show_status

    card = QFrame(parent)
    card.setObjectName("Card")
    card_layout = create_layout(
        vertical=True,
        parent=card,
        margins=(0, 0, 0, 0),
        spacing=SPLASH_CONTENT_SPACING,
    )

    card_layout.addWidget(create_logo_label_from_spec(config.logo))

    progress_bar: QProgressBar | None = None
    if include_progress:
        progress_bar = create_progress_bar_from_spec(config.progress)
        progress_bar.setParent(card)
        progress_bar.setFixedWidth(
            config.dimensions.width - SPLASH_PROGRESS_WIDTH_INSET
        )
        card_layout.addLayout(
            create_layout_with_items(
                items=[progress_bar],
                start_stretch=True,
                end_stretch=True,
            )
        )

    status_label: QLabel | None = None
    if include_status:
        status_label = _add_label_from_spec(
            card_layout, config.status_label_spec(), card
        )

    _add_label_from_spec(card_layout, config.subtitle_panel_spec(), card)
    _add_label_from_spec(card_layout, config.credits_label_spec(), card)

    title_label = create_label_from_spec(config.title_label_spec(), parent=parent)

    return SplashPanelWidgets(
        card=card,
        progress_bar=progress_bar,
        status_label=status_label,
        title_label=title_label,
    )
