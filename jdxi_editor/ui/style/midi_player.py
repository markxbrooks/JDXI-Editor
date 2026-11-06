"""
MIDI Player visual tokens and player-scoped stylesheets.

Chrome comes from AppEditorStyle; this module adds timeline / mute / step helpers.
Red (ACCENT) is reserved for active/selected/playhead — not idle chrome.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QColor

from jdxi_editor.ui.style.editor_style import AppEditorStyle


class MidiPlayerStyle(AppEditorStyle):
    """MIDI Player extensions on shared restrained editor chrome."""

    TRACK_HEADER_WIDTH = 210
    TRACK_HEIGHT = 48  # two lines of 20 px controls
    TRACK_LABEL_WIDTH = 110
    TRACK_NUMBER_WIDTH = 18
    TRACK_ICON_SIZE = 18
    TRACK_CHANNEL_WIDTH = 52

    # Muted timeline channel colours (RGBA)
    CHANNEL_COLORS = {
        0: (180, 70, 70, 130),  # Digital 1 — muted red
        1: (200, 140, 60, 130),  # Digital 2 — amber
        2: (50, 140, 150, 130),  # Analog — teal
        3: (70, 150, 110, 120),
        4: (90, 130, 160, 120),
        5: (100, 120, 180, 120),
        6: (90, 100, 170, 120),
        7: (130, 90, 170, 120),
        8: (150, 90, 150, 120),
        9: (120, 80, 160, 140),  # Drums — muted purple
        10: (110, 110, 110, 120),
        11: (60, 120, 80, 120),
        12: (130, 100, 70, 120),
        13: (160, 90, 120, 120),
        14: (80, 120, 150, 120),
        15: (140, 110, 80, 120),
    }

    @classmethod
    def sequencer_button_style(
        cls, active: bool, checked_means_inactive: bool = False
    ) -> str:
        """Mute / sequencer squares: grey idle, accent when unmuted/active."""
        border_color = cls.ACCENT if active else cls.BORDER
        bg_color = cls.SURFACE_ALT if active else cls.BACKGROUND
        checked_border = cls.BORDER if checked_means_inactive else cls.ACCENT
        checked_bg = cls.BACKGROUND if checked_means_inactive else cls.SURFACE_ALT
        return f"""
        QPushButton {{
            border: 2px solid {border_color};
            background-color: {bg_color};
            border-radius: 3px;
            padding: 0px;
        }}
        QPushButton:checked {{
            border: 2px solid {checked_border};
            background-color: {checked_bg};
        }}
        QPushButton:hover {{
            background-color: {cls.SURFACE};
            border-color: {cls.ACCENT_HOVER};
        }}
        QPushButton:checked:hover {{
            border-color: {checked_border};
        }}
        QPushButton:pressed {{
            background-color: {cls.SURFACE_ALT};
            border-color: {cls.ACCENT};
        }}
        """

    @classmethod
    def spin_box_stylesheet(cls) -> str:
        """Channel spin: grey idle top border; accent when focused."""
        return f"""
        QSpinBox {{
            background-color: {cls.SURFACE_ALT};
            border: none;
            border-top: 2px solid {cls.BORDER};
            border-radius: 0;
            padding: 1px;
            color: {cls.TEXT};
            font-size: {cls.FONT_CONTROL};
        }}
        QSpinBox:focus {{
            border-top: 2px solid {cls.ACCENT};
        }}
        """

    @classmethod
    def track_name_stylesheet(cls) -> str:
        return f"""
        QLineEdit {{
            background-color: transparent;
            border: none;
            color: {cls.TEXT};
            font-size: {cls.FONT_TRACK_NAME};
            font-weight: 600;
        }}
        """

    SOLO = "#C88C3C"  # amber: soloed track

    @classmethod
    def tool_button_stylesheet(cls) -> str:
        """Compact icon + text action button (toolbar rows)."""
        return f"""
        QPushButton {{
            background-color: {cls.SURFACE_ALT};
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
            padding: 4px 10px;
            color: {cls.TEXT};
            font-size: {cls.FONT_CONTROL};
            text-align: left;
        }}
        QPushButton:hover {{
            border-color: {cls.BORDER_HOVER};
            background-color: {cls.SURFACE};
        }}
        QPushButton:pressed {{
            background-color: {cls.BACKGROUND};
        }}
        """

    @classmethod
    def channel_mute_stylesheet(cls) -> str:
        """
        Channel mute squares: grey when playing, red when muted; channels the
        file does not use (property unused=true) are dimmed.
        """
        return f"""
        QPushButton {{
            background-color: {cls.SURFACE_ALT};
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
            color: {cls.TEXT};
            padding: 0;
        }}
        QPushButton[unused="true"] {{
            background-color: {cls.BACKGROUND};
            color: {cls.BORDER_HOVER};
        }}
        QPushButton:hover {{
            border-color: {cls.BORDER_HOVER};
        }}
        QPushButton:checked {{
            background-color: {cls.ACCENT};
            border-color: {cls.ACCENT};
            color: {cls.TEXT};
        }}
        """

    @classmethod
    def track_toggle_stylesheet(cls, checked_color: str) -> str:
        """Track mute/solo: quiet when off, filled with *checked_color* when on."""
        return f"""
        QPushButton {{
            background-color: transparent;
            border: 1px solid {cls.BORDER};
            border-radius: 3px;
        }}
        QPushButton:hover {{
            border-color: {cls.BORDER_HOVER};
        }}
        QPushButton:checked {{
            background-color: {checked_color};
            border-color: {checked_color};
        }}
        """

    @classmethod
    def track_secondary_stylesheet(cls) -> str:
        return f"""
        QLabel {{
            color: {cls.TEXT_SECONDARY};
            font-size: {cls.FONT_TRACK_SECONDARY};
        }}
        """

    # Pattern step cells — muted on-state; accent only for playhead / selection
    STEP_ON = "#B44646"
    STEP_ON_HOVER = "#C85A5A"
    STEP_OFF = AppEditorStyle.SURFACE_ALT
    STEP_OFF_HOVER = AppEditorStyle.SURFACE
    PLAYHEAD = "#F2F2F2"  # light outline on the playing step
    # Pattern rows 0-3: Digital 1, Digital 2, Analog, Drums
    PART_COLORS = {0: "#B44646", 1: "#C88C3C", 2: "#3296A0", 3: "#7850A0"}

    @classmethod
    def step_button_style(
        cls,
        is_checked: bool,
        is_current: bool = False,
        is_selected_bar: bool = False,
        row: Optional[int] = None,
    ) -> str:
        """
        Sequencer step cell.

        Off: grey. On: filled with the part colour of *row* (Digital 1 red,
        Digital 2 amber, Analog teal, Drums purple). Playhead: a light
        outline, visible on every part colour. Steps of a muted row
        (property ``muted`` true) and disabled steps are dimmed.

        :param is_selected_bar: kept for callers; the displayed bar is always
            the selected one
        """
        on = QColor(cls.PART_COLORS.get(row, cls.STEP_ON))
        if is_checked:
            bg = on.name()
            bg_hover = on.lighter(115).name()
            text = cls.TEXT
            border = on.lighter(125).name()
        else:
            bg = cls.STEP_OFF
            bg_hover = cls.STEP_OFF_HOVER
            text = cls.TEXT_SECONDARY
            border = cls.BORDER
        if is_current:
            border = cls.PLAYHEAD
            border_width = "3px"
        else:
            border_width = "1px"
        # Muted row (property muted=true): steps stay editable but dim
        muted_bg = on.darker(260).name() if is_checked else cls.BACKGROUND

        return f"""
        QPushButton {{
            background-color: {bg};
            border: {border_width} solid {border};
            border-radius: 4px;
            color: {text};
            padding: 4px;
        }}
        QPushButton:hover {{
            background-color: {bg_hover};
            border-color: {cls.PLAYHEAD if is_current else cls.BORDER_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {cls.SURFACE};
        }}
        QPushButton[muted="true"] {{
            background-color: {muted_bg};
            border-color: {cls.PLAYHEAD if is_current else cls.SURFACE_ALT};
            color: {cls.TEXT_SECONDARY};
        }}
        QPushButton:disabled {{
            background-color: {cls.BACKGROUND};
            border-color: {cls.SURFACE_ALT};
        }}
        """


class PatternEditorStyle(MidiPlayerStyle):
    """Pattern Editor chrome — same tokens as Midi Player."""
