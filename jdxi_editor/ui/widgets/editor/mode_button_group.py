"""
Reusable mode button group widget.

This widget encapsulates the pattern used by the Digital Filter mode buttons:
- A row of mutually-exclusive buttons (via QButtonGroup)
- Consistent analog/digital styling
- Optional MIDI send on selection
- Optional Python callback and Qt signal on mode change

It can be reused for oscillator waveforms or any other small finite set of
enumerated modes.
"""

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton

from jdxi_editor.ui.common import JDXi, QWidget
from jdxi_editor.ui.widgets.editor.helper import create_icon_from_qta


@dataclass(frozen=True)
class ModeButtonSpec:
    """Specification for a single mode button."""

    mode: Any  # typically an Enum (e.g., Digital.Filter.Mode)
    label: str
    icon_name: Optional[str] = None
    tooltip: Optional[str] = None


class ModeButtonGroup(QWidget):
    """
    A reusable mode button group widget.

    Features:
    - Mutually exclusive buttons driven by a QButtonGroup
    - Analog/digital styling via JDXi.UI.Theme helpers
    - Optional MIDI send via send_midi_parameter(midi_param, mode.value)
    - Optional Python callback and Qt signal on mode changes
    """

    mode_changed = Signal(object)  # emits the selected mode object

    def __init__(
        self,
        specs: Iterable[ModeButtonSpec],
        *,
        analog: bool = False,
        send_midi_parameter: Callable[[Any, int], None] | None = None,
        midi_param: Any | None = None,
        on_mode_changed: Callable[[Any], None] | None = None,
        icon_factory: Callable[[Any], QIcon | QPixmap | None] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self._analog = analog
        self._send_midi_parameter = send_midi_parameter
        self._midi_param = midi_param
        self._on_mode_changed = on_mode_changed
        self._icon_factory = icon_factory

        self._buttons: dict[Any, QPushButton] = {}

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        # Outer layout: stretch + button row + stretch (centered, same as Digital Filter mode buttons)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(JDXi.UI.Style.SPACING)

        for spec in specs:
            btn = self._build_button(spec)
            button_row.addWidget(btn)
            self._buttons[spec.mode] = btn
            # Use the mode's value (int) as the group id when available
            group_id = getattr(spec.mode, "value", None)
            if isinstance(group_id, int):
                self._group.addButton(btn, group_id)
            else:
                self._group.addButton(btn)

        layout.addLayout(button_row)
        layout.addStretch()

        # Connect group signal
        self._group.idToggled.connect(self._on_group_toggled)

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #
    def _build_button(self, spec: ModeButtonSpec) -> QPushButton:
        btn = QPushButton(spec.label, self)
        btn.setCheckable(True)

        if spec.tooltip:
            btn.setToolTip(spec.tooltip)

        if spec.icon_name:
            if self._icon_factory is not None:
                result = self._icon_factory(spec.icon_name)
                if result is not None:
                    icon = result if isinstance(result, QIcon) else QIcon(result)
                    if not icon.isNull():
                        btn.setIcon(icon)
                        btn.setIconSize(
                            QSize(
                                JDXi.UI.Dimensions.LFOIcon.WIDTH,
                                JDXi.UI.Dimensions.LFOIcon.HEIGHT,
                            )
                        )
            else:
                icon = create_icon_from_qta(spec.icon_name)
                if icon and not icon.isNull():
                    btn.setIcon(icon)
                    btn.setIconSize(
                        QSize(
                            JDXi.UI.Dimensions.LFOIcon.WIDTH,
                            JDXi.UI.Dimensions.LFOIcon.HEIGHT,
                        )
                    )

        # Fixed size (match Digital Filter mode buttons / waveform icon dimensions)
        btn.setFixedSize(
            JDXi.UI.Dimensions.WaveformIcon.WIDTH,
            JDXi.UI.Dimensions.WaveformIcon.HEIGHT,
        )

        # Base style (match Digital Filter section mode buttons)
        JDXi.UI.Theme.apply_button_rect(btn, analog=self._analog)

        return btn

    # ------------------------------------------------------------------ #
    # Selection / styling
    # ------------------------------------------------------------------ #
    def _on_group_toggled(self, _id: int, checked: bool) -> None:
        """Handle QButtonGroup toggles; update UI + callbacks for the checked button."""
        if not checked:
            return

        # Find mode corresponding to this id
        mode = None
        for m, btn in self._buttons.items():
            group_id = self._group.id(btn)
            if group_id == _id:
                mode = m
                break

        if mode is None:
            return

        self.set_mode(mode, send_midi=True)

    def set_mode(self, mode: Any, *, send_midi: bool = False) -> None:
        """
        Programmatically select a mode.

        - Updates button checked state and styles (exclusive)
        - Optionally sends MIDI
        - Triggers callback and Qt signal
        """
        btn = self._buttons.get(mode)
        if btn is None:
            return

        # Reset all first (match Digital Filter section mode buttons)
        for b in self._buttons.values():
            b.setChecked(False)
            JDXi.UI.Theme.apply_button_rect(b, analog=self._analog)

        # Apply active style to selected
        btn.setChecked(True)
        JDXi.UI.Theme.apply_button_active(btn, analog=self._analog)

        # MIDI send
        if send_midi and self._send_midi_parameter and self._midi_param is not None:
            value = getattr(mode, "value", None)
            if isinstance(value, int):
                self._send_midi_parameter(self._midi_param, value)

        # Python callback
        if self._on_mode_changed:
            self._on_mode_changed(mode)

        # Qt signal
        self.mode_changed.emit(mode)

    # ------------------------------------------------------------------ #
    # Accessors
    # ------------------------------------------------------------------ #
    @property
    def buttons(self) -> dict[Any, QPushButton]:
        """Read-only mapping of mode -> QPushButton."""
        return dict(self._buttons)
