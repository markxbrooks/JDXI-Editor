"""
Live readout bar for MIDI channel, bank CC, and program change values.
"""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from jdxi_editor.ui.common import JDXi
from jdxi_editor.ui.midi.selection_info import (
    MidiWireInfo,
    format_midi_wire_info,
    resolve_program_midi_from_id,
    resolve_tone_midi,
)
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)


class MidiSelectionInfoBar(QWidget):
    """Compact label showing Channel / CC0 / CC32 / PC for the current selection."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._label = QLabel("MIDI  —")
        self._label.setWordWrap(True)
        self._label.setStyleSheet(
            f"color: {JDXi.UI.Style.GREY}; font-size: 11px; padding: 2px 0;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.addWidget(self._label)

    def set_info(self, info: Optional[MidiWireInfo]) -> None:
        """Update readout from resolved wire info."""
        self._label.setText(format_midi_wire_info(info))

    def set_message(self, text: str) -> None:
        """Show placeholder or empty-state text."""
        self._label.setText(text)


class MidiSelectionInfoController(QObject):
    """
    Connects a combo widget to a MidiSelectionInfoBar via a resolver callback.

    Supports SearchableFilterableComboBox.valueChanged and plain QComboBox
    currentIndexChanged (via value_from_index).
    """

    def __init__(
        self,
        info_bar: MidiSelectionInfoBar,
        resolver: Callable[[int], Optional[MidiWireInfo]],
        parent: Optional[QObject] = None,
        midi_helper=None,
        lcd_title=None,
    ):
        super().__init__(parent)
        self._info_bar = info_bar
        self._resolver = resolver
        self._midi_helper = midi_helper
        self._lcd_title = lcd_title
        self._bound_combo: Optional[SearchableFilterableComboBox] = None
        self._last_value: Optional[int] = None
        # Tone-binding state (set by bind_tone_midi_info)
        self._preset_list = None
        self._channel: Optional[int] = None
        self._channel_label: Optional[str] = None

    def set_resolver(
        self, resolver: Callable[[int], Optional[MidiWireInfo]]
    ) -> None:
        """Replace the resolver and refresh the current selection."""
        self._resolver = resolver
        self._refresh_current()

    def set_channel(
        self, channel: int, channel_label: Optional[str] = None
    ) -> None:
        """
        Update the MIDI channel used by a tone readout and refresh the bar.

        Only applies when this controller was created via bind_tone_midi_info.
        """
        if self._preset_list is None:
            return
        self._channel = channel
        self._channel_label = channel_label
        self.set_resolver(self._make_tone_resolver())

    def _make_tone_resolver(self) -> Callable[[int], Optional[MidiWireInfo]]:
        preset_list = self._preset_list
        channel = self._channel
        channel_label = self._channel_label

        def resolver(preset_id: int) -> Optional[MidiWireInfo]:
            return resolve_tone_midi(
                preset_id,
                preset_list,
                channel=channel,
                channel_label=channel_label,
            )

        return resolver

    def _refresh_current(self) -> None:
        if self._last_value is not None:
            self.refresh(self._last_value)
        elif self._bound_combo is not None and self._bound_combo.combo_box.count() > 0:
            self.refresh(self._bound_combo.value())

    def refresh(self, value: int) -> None:
        """Resolve and display MIDI info for the given selection value."""
        self._last_value = value
        info = self._resolver(value)
        self._info_bar.set_info(info)
        if self._lcd_title is not None and hasattr(self._lcd_title, "set_wire_info"):
            self._lcd_title.set_wire_info(info)

    @Slot(int)
    def on_value_changed(self, value: int) -> None:
        if self._midi_helper is not None and hasattr(
            self._midi_helper, "clear_selection_expectation"
        ):
            self._midi_helper.clear_selection_expectation()
        self.refresh(value)

    def bind_searchable_combo(self, combo: SearchableFilterableComboBox) -> None:
        """Connect to SearchableFilterableComboBox.valueChanged."""
        self._bound_combo = combo
        combo.valueChanged.connect(self.on_value_changed)
        if combo.combo_box.count() > 0:
            self.refresh(combo.value())

    def bind_plain_combo(
        self,
        combo,
        value_from_index: Callable[[int], Optional[int]],
    ) -> None:
        """Connect to QComboBox.currentIndexChanged with index→value mapping."""

        def on_index_changed(index: int) -> None:
            value = value_from_index(index)
            if value is None:
                self._info_bar.set_message("MIDI  —")
            else:
                self.refresh(value)

        combo.currentIndexChanged.connect(on_index_changed)
        if combo.count() > 0:
            on_index_changed(combo.currentIndex())


def bind_tone_midi_info(
    combo: SearchableFilterableComboBox,
    info_bar: MidiSelectionInfoBar,
    preset_list,
    channel: int,
    channel_label: Optional[str] = None,
    parent: Optional[QObject] = None,
    midi_helper=None,
    lcd_title=None,
) -> MidiSelectionInfoController:
    """Wire a tone preset combo to a MIDI info readout (and optional LCD title)."""
    controller = MidiSelectionInfoController(
        info_bar,
        lambda _preset_id: None,
        parent=parent,
        midi_helper=midi_helper,
        lcd_title=lcd_title,
    )
    controller._preset_list = preset_list
    controller._channel = channel
    controller._channel_label = channel_label
    controller.set_resolver(controller._make_tone_resolver())
    controller.bind_searchable_combo(combo)
    return controller


def bind_program_midi_info(
    combo: SearchableFilterableComboBox,
    info_bar: MidiSelectionInfoBar,
    program_list,
    parent: Optional[QObject] = None,
    midi_helper=None,
) -> MidiSelectionInfoController:
    """Wire a program combo (values = list indices) to a MIDI info readout."""

    def resolver(index: int) -> Optional[MidiWireInfo]:
        if index < 0 or index >= len(program_list):
            return None
        program = program_list[index]
        program_id = getattr(program, "id", None)
        if not program_id:
            return None
        return resolve_program_midi_from_id(program_id)

    controller = MidiSelectionInfoController(
        info_bar, resolver, parent=parent, midi_helper=midi_helper
    )
    controller.bind_searchable_combo(combo)
    return controller
