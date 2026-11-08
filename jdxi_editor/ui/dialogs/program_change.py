"""
Program Change dialog

Edit a program change in a MIDI file: choose the channel, the synth type
(Digital / Analog / Drums) and a JD-Xi preset. The result is the bank select
(CC#0, CC#32) and program change values to write into the track.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.midi.bank import Bank
from jdxi_editor.ui.midi.selection_info import MidiWireInfo
from jdxi_editor.ui.preset.model import (
    PRESET_SOURCES,
    Preset,
    ProgramChangeSelection,
    load_presets,
)
from jdxi_editor.ui.preset.source import PresetSource
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.midi.selection_info_bar import MidiSelectionInfoBar

# 0-based channel -> preset type to offer when the current program is not a preset
DEFAULT_SOURCE_FOR_CHANNEL = {2: PresetSource.ANALOG, 9: PresetSource.DRUMS}

__all__ = [
    "ProgramChangeDialog",
    "ProgramChangeSelection",
    "Preset",
]


class ProgramChangeDialog(QDialog):
    """Choose the channel and JD-Xi preset for a program change."""

    def __init__(
        self,
        *,
        channel: int,
        bank: Bank,
        program: int,
        parent: Optional[QWidget] = None,
    ):
        """
        :param channel: Current channel (0-15)
        :param bank: Current bank select (CC#0 / CC#32)
        :param program: Current program change value (0-127)
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Program Change")
        self.setMinimumWidth(420)
        self._presets: list[Preset] = []
        self._channel = channel
        self._bank = bank
        self._program = program

        self.channel_combo = QComboBox()
        for ch in range(16):
            self.channel_combo.addItem(f"Ch {ch + 1}", ch)
        self.channel_combo.setCurrentIndex(channel)

        self.type_combo = QComboBox()
        for source in PRESET_SOURCES:
            self.type_combo.addItem(source.value, source)

        # The category row is only built when categories are given up front;
        # _populate() then narrows them to the chosen type
        all_categories = sorted(
            {
                preset.category
                for source in PRESET_SOURCES
                for preset in load_presets(source)
            }
            - {""}
        )
        self.preset_combo = SearchableFilterableComboBox(
            label="Preset",
            options=[],
            values=[],
            categories=all_categories,
            show_label=False,
            search_placeholder="Search presets...",
        )
        self.info_bar = MidiSelectionInfoBar()
        current = QLabel(
            f"Current: CC#0 {bank.msb} · CC#32 {bank.lsb} · PC {program}"
        )

        form = QFormLayout()
        form.addRow("Channel", self.channel_combo)
        form.addRow("Type", self.type_combo)
        form.addRow(self.preset_combo)  # has its own Category / Search / Preset rows

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)

        layout = QVBoxLayout(self)
        layout.addWidget(current)
        layout.addLayout(form)
        layout.addWidget(self.info_bar)
        layout.addWidget(buttons)

        self._select_current(channel, bank, program)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        self.channel_combo.currentIndexChanged.connect(self._update_info)
        self.preset_combo.valueChanged.connect(self._update_info)
        self._update_info()

    # --- Population -----------------------------------------------------------

    def _populate(self, source: PresetSource) -> None:
        self._presets = load_presets(source)
        options = [f"{p.id} - {p.name}" for p in self._presets]
        category_of = {
            option: preset.category
            for option, preset in zip(options, self._presets)
        }
        categories = sorted({c for c in category_of.values() if c})
        self.preset_combo.set_options(
            options,
            values=list(range(len(options))),
            categories=categories,
            category_filter_func=lambda option, category: category_of.get(option)
            == category,
        )

    def _select_current(self, channel: int, bank: Bank, program: int) -> None:
        """Open on the preset the program change already selects, if it is one."""
        wire = (bank.msb, bank.lsb, program)
        for source in PRESET_SOURCES:
            for index, preset in enumerate(load_presets(source)):
                if preset.midi_address == wire:
                    self.type_combo.setCurrentIndex(list(PRESET_SOURCES).index(source))
                    self._populate(source)
                    self.preset_combo.setValue(index)
                    return
        source = DEFAULT_SOURCE_FOR_CHANNEL.get(channel, PresetSource.DIGITAL)
        self.type_combo.setCurrentIndex(list(PRESET_SOURCES).index(source))
        self._populate(source)

    def _on_type_changed(self, _index: int) -> None:
        self._populate(self.type_combo.currentData())
        self._update_info()

    # --- Result ---------------------------------------------------------------

    def _selected_preset(self) -> Optional[Preset]:
        if self.preset_combo.combo_box.count() == 0:
            return None
        index = self.preset_combo.value()
        return self._presets[index] if 0 <= index < len(self._presets) else None

    def selection(self) -> Optional[ProgramChangeSelection]:
        """The chosen channel and preset, or None if nothing is selected."""
        preset = self._selected_preset()
        if preset is None:
            return None
        return ProgramChangeSelection(
            channel=int(self.channel_combo.currentData()),
            preset=preset,
        )

    def _update_info(self, *_args) -> None:
        selection = self.selection()
        self.ok_button.setEnabled(selection is not None)
        if selection is None:
            self.info_bar.set_message("MIDI  —")
            return
        self.info_bar.set_info(MidiWireInfo.from_selection(selection))
