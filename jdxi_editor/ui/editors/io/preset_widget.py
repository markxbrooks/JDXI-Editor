"""
preset widget
"""

from decologr import Decologr as log
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.ui.preset.tone.lists import JDXiUIPreset
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.editor.helper import transfer_layout_items


class PresetWidget(QWidget):
    """Preset Widget"""

    def __init__(self, parent):
        super().__init__(parent)
        self.preset_list = None
        self.midi_channel = None
        self.parent = parent
        self._actual_preset_list = []  # Will be set by _update_preset_combo_box()
        preset_vlayout = QVBoxLayout()
        preset_vlayout.setContentsMargins(
            JDXi.UI.Style.PADDING,
            JDXi.UI.Style.PADDING,
            JDXi.UI.Style.PADDING,
            JDXi.UI.Style.PADDING,
        )
        preset_vlayout.setSpacing(JDXi.UI.Style.SPACING)
        self.setLayout(preset_vlayout)

        # Add icon row at the top (centered with stretch on both sides)
        icon_row_container = QHBoxLayout()
        icon_row_container.addStretch()
        icon_row = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        icon_row_container.addStretch()
        preset_vlayout.addLayout(icon_row_container)
        preset_vlayout.addSpacing(10)  # Add spacing after icon row

        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )  # Center align the image
        preset_vlayout.addWidget(self.image_label)
        # Synth type selection combo box
        self.digital_preset_type_combo = QComboBox()
        self.digital_preset_type_combo.addItems(
            ["Digital Synth 1", "Digital Synth 2", "Drums", "Analog Synth"]
        )
        self.digital_preset_type_combo.currentIndexChanged.connect(
            self.on_preset_type_changed
        )
        preset_vlayout.addWidget(self.digital_preset_type_combo)

        # Create SearchableFilterableComboBox for preset selection
        # Initialize with empty data - will be populated when preset type is selected
        self.preset_combo_box = SearchableFilterableComboBox(
            label="Preset",
            options=[],
            values=[],
            categories=[],
            show_label=True,
            show_search=True,
            show_category=True,
            search_placeholder="Search presets...",
        )
        preset_vlayout.addWidget(self.preset_combo_box)

        # Initialize the combo box with default preset type (Digital Synth 1)
        # This will be called again when preset type changes, but we need initial population
        QTimer.singleShot(0, self._update_preset_combo_box)

        # Load button
        self.load_button = QPushButton(
            JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.FOLDER_NOTCH_OPEN, color=JDXi.UI.Style.FOREGROUND
            ),
            "Load Preset",
        )
        self.load_button.clicked.connect(lambda: self.load_preset_by_program_change())
        preset_vlayout.addWidget(self.load_button)

        # Connect combo box valueChanged to load preset directly (optional)
        # self.preset_combo_box.valueChanged.connect(self.load_preset_by_program_change)

    def load_preset_by_program_change(self, preset_id: str = None) -> None:
        """
        Load a preset by program change.

        :param preset_id: str Optional preset ID (if None, gets from combo box)
        """
        # Get preset ID from combo box value if not provided
        if preset_id is None:
            # Get the current value from SearchableFilterableComboBox
            # The value is the preset ID as integer (e.g., 1 for "001")
            preset_id_int = self.preset_combo_box.value()
            preset_id = str(preset_id_int).zfill(3)  # Convert back to 3-digit format

        program_number = str(preset_id).zfill(3)  # Ensure 3-digit format
        log.message("=======load_preset_by_program_change=======")
        log.parameter("preset_id", preset_id)
        log.parameter("program_number", program_number)

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        # Use _actual_preset_list (list of dicts) instead of preset_list (enum)
        preset_list_to_use = getattr(self, "_actual_preset_list", None)
        if preset_list_to_use is None:
            # Fallback: determine preset list from preset type
            preset_type = self.digital_preset_type_combo.currentText()
            if preset_type in ["Digital Synth 1", "Digital Synth 2"]:
                preset_list_to_use = JDXi.UI.Preset.Digital.PROGRAM_CHANGE
            elif preset_type == "Drums":
                preset_list_to_use = JDXi.UI.Preset.Drum.PROGRAM_CHANGE
            elif preset_type == "Analog Synth":
                preset_list_to_use = JDXi.UI.Preset.Analog.PROGRAM_CHANGE
            else:
                preset_list_to_use = JDXi.UI.Preset.Digital.PROGRAM_CHANGE

        msb = get_preset_parameter_value("msb", program_number, preset_list_to_use)
        lsb = get_preset_parameter_value("lsb", program_number, preset_list_to_use)
        pc = get_preset_parameter_value("pc", program_number, preset_list_to_use)

        if None in [msb, lsb, pc]:
            log.message(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return

        log.message("retrieved msb, lsb, pc :")
        log.parameter("combo box msb", msb)
        log.parameter("combo box lsb", lsb)
        log.parameter("combo box pc", pc)
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        # Use PresetWidget's midi_channel if set, otherwise fall back to parent's
        # Access ProgramEditor through ProgramGroupWidget.parent
        program_editor = getattr(self.parent, "parent", None) if self.parent else None
        if not program_editor or not hasattr(program_editor, "midi_helper"):
            log.error(
                "Cannot access midi_helper: ProgramEditor not found in parent chain"
            )
            return

        midi_channel = (
            self.midi_channel
            if self.midi_channel is not None
            else getattr(self.parent, "midi_channel", None)
        )
        program_editor.midi_helper.send_bank_select_and_program_change(
            midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1,  # Convert 1-based PC to 0-based
        )
        if hasattr(program_editor, "data_request"):
            program_editor.data_request()

    def on_preset_type_changed(self, index: int) -> None:
        """
        on_preset_type_changed

        :param index: int
        Handle preset type selection change
        """
        preset_type = self.digital_preset_type_combo.currentText()
        log.message(f"preset_type: {preset_type}")
        # Update PresetWidget's own state
        self.set_channel_and_preset_lists(preset_type)
        self._update_preset_combo_box()
        # Also notify ProgramEditor to keep it in sync (access through ProgramGroupWidget.parent)
        program_editor = getattr(self.parent, "parent", None) if self.parent else None
        if program_editor and hasattr(program_editor, "set_channel_and_preset_lists"):
            program_editor.set_channel_and_preset_lists(preset_type)

    def set_channel_and_preset_lists(self, preset_type: str) -> None:
        """
        set_channel_and_preset_lists

        :param preset_type:
        :return: None
        """
        if preset_type == "Digital Synth 1":
            self.midi_channel = MidiChannel.DIGITAL_SYNTH_1
            self.preset_list = JDXiUIPreset.Digital.PROGRAM_CHANGE
        elif preset_type == "Digital Synth 2":
            self.midi_channel = MidiChannel.DIGITAL_SYNTH_2
            self.preset_list = JDXiUIPreset.Digital.PROGRAM_CHANGE
        elif preset_type == "Drums":
            self.midi_channel = MidiChannel.DRUM_KIT
            self.preset_list = JDXiUIPreset.Drum.PROGRAM_CHANGE
        elif preset_type == "Analog Synth":
            self.midi_channel = MidiChannel.ANALOG_SYNTH
            self.preset_list = JDXiUIPreset.Analog.PROGRAM_CHANGE

    def _update_preset_combo_box(self) -> None:
        """
        Update the SearchableFilterableComboBox with current preset list.
        Called when preset type changes.
        """
        preset_type = self.digital_preset_type_combo.currentText()
        if preset_type in ["Digital Synth 1", "Digital Synth 2"]:
            preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE
        elif preset_type == "Drums":
            preset_list = JDXi.UI.Preset.Drum.PROGRAM_CHANGE
        elif preset_type == "Analog Synth":
            preset_list = JDXi.UI.Preset.Analog.PROGRAM_CHANGE
        else:
            preset_list = (
                JDXi.UI.Preset.Digital.PROGRAM_CHANGE
            )  # Default to digital synth 1

        # Store the actual preset list for use in load_preset_by_program_change
        # Note: self.preset_list is still set to JDXiPresetToneList enum in set_channel_and_preset_lists
        # for use with get_preset_parameter_value, but we also need the actual list for the combo box

        # Convert dictionary format (Digital/Analog) to list format if needed
        if isinstance(preset_list, dict):
            # Convert dictionary {1: {"Name": "...", "Category": "...", ...}, ...} to list format
            self._actual_preset_list = [
                {
                    "id": f"{preset_id:03d}",  # Format as "001", "002", etc.
                    "name": preset_data.get("Name", ""),
                    "category": preset_data.get("Category", ""),
                    "msb": str(preset_data.get("MSB", 0)),
                    "lsb": str(preset_data.get("LSB", 0)),
                    "pc": str(preset_data.get("PC", preset_id)),
                }
                for preset_id, preset_data in sorted(preset_list.items())
            ]
        else:
            # Already a list (Drum format)
            self._actual_preset_list = preset_list

        # Build options, values, and categories
        preset_options = [
            f"{preset['id']} - {preset['name']}" for preset in self._actual_preset_list
        ]
        # Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset["id"]) for preset in self._actual_preset_list]
        preset_categories = sorted(
            set(preset["category"] for preset in self._actual_preset_list)
        )

        # Category filter function for presets
        def preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # Extract preset ID from display string (format: "001 - Preset Name")
            preset_id_str = (
                preset_display.split(" - ")[0] if " - " in preset_display else None
            )
            if preset_id_str:
                # Find the preset in the list and check its category
                for preset in self._actual_preset_list:
                    if preset["id"] == preset_id_str:
                        return preset["category"] == category
            return False

        # Update the combo box by recreating it (since SearchableFilterableComboBox doesn't have update methods)
        # Get parent widget and layout
        preset_widget = self.digital_preset_type_combo.parent()
        preset_vlayout = preset_widget.layout() if preset_widget else None

        if preset_vlayout:
            # Remove old combo box from layout
            preset_vlayout.removeWidget(self.preset_combo_box)
            self.preset_combo_box.deleteLater()

            # Create new combo box with updated data
            self.preset_combo_box = SearchableFilterableComboBox(
                label="Preset",
                options=preset_options,
                values=preset_values,
                categories=preset_categories,
                category_filter_func=preset_category_filter,
                show_label=True,
                show_search=True,
                show_category=True,
                search_placeholder="Search presets...",
            )

            # Insert after digital_preset_type_combo
            index = preset_vlayout.indexOf(self.digital_preset_type_combo)
            preset_vlayout.insertWidget(index + 1, self.preset_combo_box)
