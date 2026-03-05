"""
Automation Widget class
"""
from typing import Any

from PySide6.QtCore import QMargins
from PySide6.QtWidgets import QWidget, QGridLayout, QComboBox, QVBoxLayout

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button_from_spec
from jdxi_editor.ui.editors.midi_player.helper import create_widget_cell_with_button_spec
from jdxi_editor.ui.preset.source import PresetSource
from jdxi_editor.ui.widgets.editor.helper import create_icon_and_label, create_group_and_grid_layout
from picoui.specs.widgets import ButtonSpec


class AutomationWidget(QWidget):
    """Automation Widget class"""

    def __init__(self, midi_state: MidiPlaybackState, parent: "MidiFilePlayer"):
        super().__init__()
        self.parent = parent
        self.layout: QVBoxLayout | None = None
        self.midi_state = midi_state
        self.automation_channel_combo: QComboBox | None = None
        self.automation_type_combo: QComboBox | None = None
        self.automation_program_combo: QComboBox | None = None
        self.specs = self._build_specs()
        self.setup_ui()

    def _build_specs(self) -> dict[str, Any]:
        """build specs for the Midi file player"""
        return {
            "buttons": self._build_button_specs(),
            "message_box": None,
            "check_box": None,
        }

    def _build_button_specs(self) -> dict[str, ButtonSpec]:
        """Build button specs"""
        return {
            "automation_insert": ButtonSpec(
                label="Insert Program Change Here",
                tooltip="Insert Program Change at current position",
                icon=JDXi.UI.Icon.ADD,
                slot=self.insert_program_change_current_position,
            )
        }

    def setup_ui(self):
        """set up ui"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(QMargins(0, 0, 0, 0))
        group, grid = create_group_and_grid_layout("Automation")
        self.layout.addWidget(group)
        self._build(grid=grid, row=0)

    def _build(self, grid: QGridLayout, row: int):
        automation_layout, automation_label = create_icon_and_label(
            label="Automation:", icon=JDXi.UI.Icon.MAGIC
        )
        grid.addLayout(automation_layout, row, 0)
        self.automation_channel_combo = QComboBox()
        for ch in range(1, 17):
            self.automation_channel_combo.addItem(f"Ch {ch}", ch)
        grid.addWidget(self.automation_channel_combo, row, 1)
        self.automation_type_combo = QComboBox()
        self.automation_type_combo.addItems(["Digital", "Analog", "Drums"])
        self.automation_type_combo.currentIndexChanged.connect(
            self.on_automation_type_changed
        )
        grid.addWidget(self.automation_type_combo, row, 2)
        self.automation_program_combo = QComboBox()
        grid.addWidget(self.automation_program_combo, row, 3)
        spec = self.specs["buttons"]["automation_insert"]
        self.automation_insert_button = create_jdxi_button_from_spec(
            spec, checkable=False
        )
        insert_cell, self.automation_insert_label = (
            create_widget_cell_with_button_spec(
                spec, self.automation_insert_button
            )
        )
        grid.addWidget(insert_cell, row, 4)

    def populate_automation_programs(self, source: PresetSource) -> None:
        """
        Populate the program combo based on source list.
        source: "Digital" | "Analog" | "Drums"
        """
        self.automation_program_combo.clear()

        # Helper function to convert dictionary format to list format
        def convert_preset_dict_to_list(preset_dict):
            """Convert PROGRAM_CHANGE dictionary to list format."""
            if isinstance(preset_dict, dict):
                return [
                    {
                        "id": f"{preset_id:03d}",
                        "name": preset_data.get("Name", ""),
                        "category": preset_data.get("Category", ""),
                        "msb": preset_data.get("MSB", 0),
                        "lsb": preset_data.get("LSB", 0),
                        "pc": preset_data.get("PC", preset_id),
                    }
                    for preset_id, preset_data in sorted(preset_dict.items())
                ]
            else:
                # Already a list (Drum format)
                return preset_dict

        preset_list_sources = {
            PresetSource.DIGITAL: JDXi.UI.Preset.Digital.PROGRAM_CHANGE,
            PresetSource.ANALOG: JDXi.UI.Preset.Analog.PROGRAM_CHANGE,
            PresetSource.DRUMS: JDXi.UI.Preset.Drum.PROGRAM_CHANGE,
        }
        preset_list_source = preset_list_sources.get(
            source, JDXi.UI.Preset.Drum.PROGRAM_CHANGE
        )
        preset_list = convert_preset_dict_to_list(preset_list_source)
        self._add_items_to_automation_combo(preset_list)

    def _add_items_to_automation_combo(self, preset_list: list[dict[str, str | Any]] | Any):
        """items to combo box"""
        for item in preset_list:
            label = f"{str(item.get('id')).zfill(3)}  {item.get('name')}"
            msb = int(item.get("msb"))
            lsb = int(item.get("lsb"))
            pc = int(item.get("pc"))
            self.automation_program_combo.addItem(label, (msb, lsb, pc))

    def on_automation_type_changed(self, _: int) -> None:
        """Handle automation type selection change."""
        source = self.automation_type_combo.currentText()
        self.populate_automation_programs(source)

    def insert_program_change_current_position(self) -> None:
        """
        Insert Bank Select (CC#0, CC#32) and Program Change at the current slider time.
        """
        if not self.parent:
            return
        self.parent.insert_program_change_current_position()

