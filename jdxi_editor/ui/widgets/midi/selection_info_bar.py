"""
Live readout bar for MIDI channel, bank CC, and program change values.
"""

from __future__ import annotations

from typing import Callable, Optional, Union

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
    ):
        super().__init__(parent)
        self._info_bar = info_bar
        self._resolver = resolver

    def refresh(self, value: int) -> None:
        """Resolve and display MIDI info for the given selection value."""
        info = self._resolver(value)
        self._info_bar.set_info(info)

    @Slot(int)
    def on_value_changed(self, value: int) -> None:
        self.refresh(value)

    def bind_searchable_combo(self, combo: SearchableFilterableComboBox) -> None:
        """Connect to SearchableFilterableComboBox.valueChanged."""
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
) -> MidiSelectionInfoController:
    """Wire a tone preset combo to a MIDI info readout."""

    def resolver(preset_id: int) -> Optional[MidiWireInfo]:
        return resolve_tone_midi(
            preset_id,
            preset_list,
            channel=channel,
            channel_label=channel_label,
        )

    controller = MidiSelectionInfoController(info_bar, resolver, parent=parent)
    controller.bind_searchable_combo(combo)
    return controller


def bind_program_midi_info(
    combo: SearchableFilterableComboBox,
    info_bar: MidiSelectionInfoBar,
    program_list,
    parent: Optional[QObject] = None,
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

    controller = MidiSelectionInfoController(info_bar, resolver, parent=parent)
    controller.bind_searchable_combo(combo)
    return controller
