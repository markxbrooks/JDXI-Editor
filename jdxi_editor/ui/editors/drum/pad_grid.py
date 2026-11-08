"""
Drum Pad Grid

Selects the drum partial being edited, like pressing a pad on the JD-Xi:
lit pads grouped by family (the Mixer's lanes), in two rows, with Common
at the end. Each pad stands for a page of the partial stack; clicking one
emits its page index, and the lit pad follows the page shown.

    Kick        Toms           Snare
    [BD1][BD2][BD3]  [TOM1][TOM2][TOM3]  [SD1]…[CLAP]
    Hi-Hat   Cymbals   Percussion   Other   Kit
    [CHH]…   [CYM1]…   [PRC1]…      [HIT]…  [COMMON]
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.ui.editors.drum.mixer.spec import DRUM_MIXER_LANE_ROWS
from jdxi_editor.ui.editors.drum.partial.partial import note_name
from jdxi_editor.ui.style.editor_style import AppEditorStyle as Style
from jdxi_editor.ui.widgets.switch.lit_button import LitButton

PAD_WIDTH = 50
PAD_HEIGHT = 26
COMMON = "Common"

# Lane names per pad row (from DRUM_MIXER_LANE_ROWS)
PAD_ROWS = (("Kick", "Toms", "Snare"), ("Hi-Hat", "Cymbals", "Percussion", "Other"))

FIRST_DRUM_NOTE = 36  # BD1 plays on C2; each partial is the next key up


class DrumPadGrid(QWidget):
    """Lit pads, one per partial page, grouped by drum family."""

    padSelected = Signal(int)  # page index

    def __init__(self, page_names: list[str], parent: Optional[QWidget] = None):
        """
        :param page_names: name of each page, in page order (partials, then "Common")
        """
        super().__init__(parent)
        self.pads: dict[int, LitButton] = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.idClicked.connect(self.padSelected)

        lanes = {lane.name: lane.partials for row in DRUM_MIXER_LANE_ROWS for lane in row}
        index_of = {name: i for i, name in enumerate(page_names)}

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(8)
        for row, lane_names in enumerate(PAD_ROWS):
            hrow = QHBoxLayout()
            hrow.setSpacing(18)
            for lane_name in lane_names:
                names = [n for n in lanes.get(lane_name, []) if n in index_of]
                hrow.addWidget(self._lane(lane_name, names, index_of))
            if row == len(PAD_ROWS) - 1 and COMMON in index_of:
                hrow.addWidget(self._lane("Kit", [COMMON], index_of))
            hrow.addStretch()
            grid.addLayout(hrow, row, 0)

    def _lane(self, title: str, names: list[str], index_of: dict[str, int]) -> QWidget:
        lane = QWidget()
        layout = QVBoxLayout(lane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        label = QLabel(title.upper())
        label.setStyleSheet(
            f"color: {Style.TEXT_SECONDARY}; font-size: 9px; letter-spacing: 1px;"
        )
        layout.addWidget(label)
        pads = QHBoxLayout()
        pads.setSpacing(4)
        for name in names:
            index = index_of[name]
            pad = LitButton(name.upper())
            pad.setStyleSheet(pad.styleSheet() + "QPushButton { padding: 0px; }")
            pad.setFixedSize(PAD_WIDTH + (24 if name == COMMON else 0), PAD_HEIGHT)
            if name == COMMON:
                pad.setToolTip("Kit common: name, level, tuning")
            else:
                pad.setToolTip(f"{name} · {note_name(FIRST_DRUM_NOTE + index)}")
            self._group.addButton(pad, index)
            self.pads[index] = pad
            pads.addWidget(pad)
        layout.addLayout(pads)
        return lane

    def set_current(self, index: int) -> None:
        """Light the pad for page *index* (no signal)."""
        pad = self.pads.get(index)
        if pad is not None and not pad.isChecked():
            pad.setChecked(True)  # exclusive group unlights the previous pad

    def current(self) -> int:
        return self._group.checkedId()
