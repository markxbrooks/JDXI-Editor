"""
Pattern File group - Load, Save, Clear buttons and drum selector combo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QComboBox, QGroupBox, QPushButton

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.editors.helpers.widgets import (
    create_jdxi_button_with_label_from_spec,
)
from jdxi_editor.ui.widgets.editor.helper import create_group_with_layout
from jdxi_editor.ui.widgets.jdxi.midi_group import JDXiMidiGroup
from picoui.helpers import create_layout_with_items
from picoui.specs.widgets import ButtonSpec
from picoui.widget.helper import create_combo_box

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.pattern.ui import PatternUI


class PatternFileGroup(JDXiMidiGroup):
    """Pattern File group: Load, Save, Clear buttons + drum selector combo."""

    def __init__(self, parent: "PatternUI"):
        super().__init__(parent=parent, midi_state=None)
        self.load_button: QPushButton | None = None
        self.save_button: QPushButton | None = None
        self.clear_learn_button: QPushButton | None = None
        self.drum_selector: QComboBox | None = None
        self.setup_ui()

    def _build_group(self) -> QGroupBox:
        """Build the Pattern File group with Load, Save, Clear buttons and drum combo."""
        load_label_row, self.load_button = create_jdxi_button_with_label_from_spec(
            self.specs["buttons"]["load"], checkable=False
        )
        save_label_row, self.save_button = create_jdxi_button_with_label_from_spec(
            self.specs["buttons"]["save"], checkable=False
        )
        clear_label_row, self.clear_learn_button = (
            create_jdxi_button_with_label_from_spec(
                self.specs["buttons"]["clear_learn"], checkable=False
            )
        )
        self.drum_selector = create_combo_box(spec=self.specs["combos"]["drum"])
        self.drum_selector.currentIndexChanged.connect(
            self.parent.update_drum_rows
        )
        layout = create_layout_with_items(
            items=[
                self.load_button,
                load_label_row,
                self.save_button,
                save_label_row,
                self.clear_learn_button,
                clear_label_row,
                self.drum_selector,
            ],
            vertical=False,
            start_stretch=False,
            end_stretch=False,
            margins=self.margins,
            spacing=self.spacing
        )
        group, _ = create_group_with_layout("Pattern", layout=layout)
        return group

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """Build Load, Save, Clear button specs."""
        return {
            "load": ButtonSpec(
                label="Load",
                icon=JDXi.UI.Icon.MUSIC,
                tooltip="Load pattern from file",
                slot=self.parent.load_pattern_dialog,
            ),
            "save": ButtonSpec(
                label="Save",
                icon=JDXi.UI.Icon.SAVE,
                tooltip="Save pattern to file",
                slot=self.parent.save_pattern_dialog,
            ),
            "clear_learn": ButtonSpec(
                label="Clear",
                icon=JDXi.UI.Icon.CLEAR,
                tooltip="Clear pattern",
                slot=self.parent.clear_pattern,
            ),
        }

    def _build_specs(self):
        """Override to include combos from parent."""
        base = super()._build_specs()
        base["combos"] = self.parent.specs["combos"]
        return base
