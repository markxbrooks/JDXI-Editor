"""Preset Widget to be used by All Editors"""

from typing import TYPE_CHECKING, Any, Optional

from decologr import Decologr as log
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.ui.editors.helpers.widgets import create_jdxi_button, create_jdxi_row
from jdxi_editor.ui.style import JDXiUIDimensions, JDXiUIStyle
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.digital.title import DigitalTitle
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_items,
    create_scroll_container,
    transfer_layout_items,
)

if TYPE_CHECKING:
    from jdxi_editor.ui.editors.synth.editor import SynthEditor


class InstrumentPresetWidget(QWidget):
    """InstrumentPresetWidget"""

    def __init__(
        self,
        parent: "SynthEditor",  # parent is not optional
    ):
        """
        InstrumentPresetWidget

        :param parent: QWidget
        """
        super().__init__(parent)
        self.group: QGroupBox | None = None
        self.layout: QVBoxLayout | None = None
        self.instrument_presets: QWidget | None = None
        self.widget: QWidget | None = None
        self.hlayout: QHBoxLayout | None = None
        self.parent = parent

    def add_image_group(self, group: QGroupBox):
        """add image group"""
        group.setMinimumWidth(JDXi.UI.Style.INSTRUMENT_IMAGE_WIDTH)
        self.hlayout.addWidget(group)

    def add_preset_group(self, group: QGroupBox):
        """add groupbox for instruments"""
        self.hlayout.addWidget(group)

    def setup(self):
        """set up the widget - creates the main vertical layout"""
        if self.layout is None:
            self.layout = QVBoxLayout()
            # Set proper margins and spacing to match PresetWidget
            self.layout.setContentsMargins(
                JDXi.UI.Style.PADDING,
                JDXi.UI.Style.PADDING,
                JDXi.UI.Style.PADDING,
                JDXi.UI.Style.PADDING,
            )
            self.layout.setSpacing(JDXi.UI.Style.SPACING)
            self.setLayout(self.layout)
            # Add stretch at top for vertical centering
            self.layout.addStretch()

    def create_instrument_image_group(self) -> tuple[QGroupBox, Any, Any]:
        """Image group"""
        instrument_image_group = QGroupBox()
        instrument_group_layout = QVBoxLayout()
        instrument_group_layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        instrument_group_layout.setSpacing(2)  # Reduced spacing
        instrument_image_group.setLayout(instrument_group_layout)
        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instrument_group_layout.addWidget(self.instrument_image_label)
        instrument_image_group.setStyleSheet(JDXi.UI.Style.INSTRUMENT_IMAGE_LABEL)
        instrument_image_group.setMinimumWidth(JDXi.UI.Style.INSTRUMENT_IMAGE_WIDTH)
        instrument_image_group.setMaximumHeight(JDXi.UI.Style.INSTRUMENT_IMAGE_HEIGHT)
        return (
            instrument_image_group,
            self.instrument_image_label,
            instrument_group_layout,
        )

    def _add_round_action_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        layout: QHBoxLayout,
        *,
        name: Optional[str] = None,
        checkable: bool = False,
    ) -> QPushButton:
        """Create a round button with icon + text label (same style as Transport)."""
        btn = create_jdxi_button("")
        btn.setCheckable(checkable)
        if slot is not None:
            btn.clicked.connect(slot)
        if name:
            setattr(self, f"{name}_button", btn)
        layout.addWidget(btn)
        pixmap = JDXi.UI.Icon.get_icon_pixmap(
            icon_enum, color=JDXi.UI.Style.FOREGROUND, size=20
        )
        label_row, _ = create_jdxi_row(text, icon_pixmap=pixmap)
        layout.addWidget(label_row)
        return btn

    def _add_centered_round_button(
        self,
        icon_enum: Any,
        text: str,
        slot: Any,
        parent_layout: QVBoxLayout,
        *,
        name: Optional[str] = None,
    ) -> QPushButton:
        """Add a round button + label row centered in a QHBoxLayout (stretch on both sides)."""
        row = QHBoxLayout()
        row.addStretch()
        btn = self._add_round_action_button(icon_enum, text, slot, row, name=name)
        row.addStretch()
        parent_layout.addLayout(row)
        return btn

    def create_instrument_preset_group(self, synth_type: str = "Analog") -> QGroupBox:
        """
        Create the instrument preset group box with tabs for normal and cheat presets (Analog only).

        :param synth_type: str
        :return: QGroupBox
        """
        instrument_preset_group = QGroupBox(f"{synth_type} Synth")
        instrument_title_group_layout = QVBoxLayout(instrument_preset_group)
        instrument_title_group_layout.setSpacing(3)  # Reduced spacing
        instrument_title_group_layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins

        # Apply Analog color styling for Analog Synth group box
        if synth_type == "Analog":
            instrument_preset_group.setStyleSheet(JDXi.UI.Style.GROUP_BOX_ANALOG)

        # For Analog, create tabs; for others, create simple layout
        if synth_type == "Analog":
            # Create tabbed widget inside the group box
            preset_tabs = QTabWidget()
            instrument_title_group_layout.addWidget(preset_tabs)

            # === Tab 1: Normal Analog Presets ===
            normal_preset_widget, normal_preset_layout = create_scroll_container()
            self._add_normal_preset_content(normal_preset_layout, synth_type)
            try:
                analog_presets_icon = JDXi.UI.Icon.get_icon(
                    JDXi.UI.Icon.MUSIC_NOTE_MULTIPLE, color=JDXi.UI.Style.GREY
                )
                if analog_presets_icon is None or analog_presets_icon.isNull():
                    raise ValueError("Icon is null")
            except:
                analog_presets_icon = JDXi.UI.Icon.get_icon(
                    JDXi.UI.Icon.MUSIC, color=JDXi.UI.Style.GREY
                )
            preset_tabs.addTab(
                normal_preset_widget, analog_presets_icon, "Analog Presets"
            )

            # === Tab 2: Cheat Presets (Digital Synth presets on Analog channel) ===
            cheat_preset_widget, cheat_preset_layout = create_scroll_container()
            self._add_cheat_preset_content(cheat_preset_layout)
            cheat_presets_icon = JDXi.UI.Icon.get_icon(
                JDXi.UI.Icon.CODE_BRACES, color=JDXi.UI.Style.GREY
            )
            preset_tabs.addTab(cheat_preset_widget, cheat_presets_icon, "Cheat Presets")
        else:
            # For Digital/Drums, create simple layout without tabs
            self._add_normal_preset_content(instrument_title_group_layout, synth_type)

        return instrument_preset_group

    def _add_normal_preset_content(self, layout: QVBoxLayout, synth_type: str):
        """Add normal preset selection content to the layout."""

        # Add icon row at the top (centered with stretch on both sides, matching PresetWidget)
        icon_row_container = QHBoxLayout()
        icon_row_container.addStretch()
        icon_row = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        icon_row_container.addStretch()
        layout.addLayout(icon_row_container)
        layout.addSpacing(10)  # Add spacing after icon row, matching PresetWidget

        self.instrument_title_label = DigitalTitle()
        layout.addWidget(self.instrument_title_label)

        # --- Edit Tone Name (round button + label, centered)
        self._add_centered_round_button(
            JDXi.UI.Icon.SETTINGS,
            "Edit Tone Name",
            self.parent.edit_tone_name,
            layout,
            name="edit_tone_name",
        )
        # --- Send Read Request to Synth (round button + label, centered)
        self._add_centered_round_button(
            JDXi.UI.Icon.REFRESH,
            "Send Read Request to Synth",
            self.parent.data_request,
            layout,
            name="read_request",
        )
        self.instrument_selection_label = QLabel(f"Select a {synth_type} synth:")
        layout.addWidget(self.instrument_selection_label)

        # Determine the correct preset list based on synth_type
        if synth_type == "Analog":
            preset_list = JDXi.UI.Preset.Analog.PROGRAM_CHANGE
        elif synth_type == "Digital":
            preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE
        elif synth_type == "Drums":
            preset_list = JDXi.UI.Preset.Drum.PROGRAM_CHANGE
        else:
            # Default to digital preset list if synth_type is unknown
            preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE

        # Convert dictionary format (Digital/Analog) to list format if needed
        if isinstance(preset_list, dict):
            # Convert dictionary {1: {"Name": "...", "Category": "...", ...}, ...} to list format
            converted_preset_list = [
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
            converted_preset_list = preset_list

        # Build preset options, values, and categories from converted_preset_list
        preset_options = [
            f"{preset['id']} - {preset['name']}" for preset in converted_preset_list
        ]
        # Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset["id"]) for preset in converted_preset_list]
        preset_categories = sorted(
            set(preset["category"] for preset in converted_preset_list)
        )

        # Category filter function for presets
        def preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # Extract preset ID from digital string (format: "001 - Preset Name")
            preset_id_str = (
                preset_display.split(" - ")[0] if " - " in preset_display else None
            )
            if preset_id_str:
                # Find the preset in the list and check its category
                for preset in converted_preset_list:
                    if preset["id"] == preset_id_str:
                        return preset["category"] == category
            return False

        # Create SearchableFilterableComboBox for preset selection
        self.instrument_selection_combo = SearchableFilterableComboBox(
            label="",
            options=preset_options,
            values=preset_values,
            categories=preset_categories,
            category_filter_func=preset_category_filter,
            show_label=False,
            show_search=True,
            show_category=True,
            search_placeholder="Search presets...",
            use_analog_style=(synth_type == "Analog"),
        )

        # Apply styling
        if synth_type == "Analog":
            # Apply Analog styling to the combo box and search line edit
            self.instrument_selection_combo.combo_box.setStyleSheet(
                JDXi.UI.Style.COMBO_BOX_ANALOG
            )
            search_box = getattr(self.instrument_selection_combo, "search_box", None)
            if search_box is not None:
                search_box.setStyleSheet(JDXi.UI.Style.QLINEEDIT_ANALOG)
        else:
            self.instrument_selection_combo.combo_box.setStyleSheet(
                JDXi.UI.Style.COMBO_BOX
            )

        # Connect signals - use combo_box for currentIndexChanged
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.parent.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.parent.update_instrument_title
        )

        # --- Load (round button + label, centered)
        load_row = QHBoxLayout()
        load_row.addStretch()
        load_button = self._add_round_action_button(
            JDXi.UI.Icon.FOLDER_NOTCH_OPEN,
            "Load",
            self._on_load_preset,
            load_row,
            name=None,
        )
        load_row.addStretch()
        load_row_widget = QWidget()
        load_row_widget.setLayout(load_row)

        selection_layout = create_layout_with_items(
            [self.instrument_selection_combo, load_row_widget], vertical=True
        )

        layout.addLayout(selection_layout)

        # Store reference to load button for compatibility
        self.instrument_selection_combo.load_button = load_button
        layout.addStretch()

    def _add_cheat_preset_content(self, layout: QVBoxLayout):
        """Add cheat preset content to the layout (Analog only)."""

        # Add icon row at the top (centered with stretch on both sides, matching PresetWidget)
        icon_row_container = QHBoxLayout()
        icon_row_container.addStretch()
        icon_row = JDXi.UI.Icon.create_generic_musical_icon_row()

        transfer_layout_items(icon_row, icon_row_container)
        icon_row_container.addStretch()
        layout.addLayout(icon_row_container)
        layout.addSpacing(10)  # Add spacing after icon row, matching PresetWidget

        # Build preset options, values, and categories
        preset_options = [
            f"{preset['id']} - {preset['name']}"
            for preset in JDXi.UI.Preset.Digital.LIST
        ]
        # Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset["id"]) for preset in JDXi.UI.Preset.Digital.LIST]
        preset_categories = sorted(
            set(preset["category"] for preset in JDXi.UI.Preset.Digital.LIST)
        )

        # Category filter function for presets
        def cheat_preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # Extract preset ID from digital string (format: "001 - Preset Name")
            preset_id_str = (
                preset_display.split(" - ")[0] if " - " in preset_display else None
            )
            if preset_id_str:
                # Find the preset in the list and check its category
                for preset in JDXi.UI.Preset.Digital.LIST:
                    if preset["id"] == preset_id_str:
                        return preset["category"] == category
            return False

        # Create SearchableFilterableComboBox for cheat preset selection
        self.cheat_preset_combo_box = SearchableFilterableComboBox(
            label="Preset",
            options=preset_options,
            values=preset_values,
            categories=preset_categories,
            category_filter_func=cheat_preset_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
            search_placeholder="Search presets...",
        )
        layout.addWidget(self.cheat_preset_combo_box)

        # Load Preset (round button + label, centered)
        self._add_centered_round_button(
            JDXi.UI.Icon.FOLDER_NOTCH_OPEN,
            "Load Preset",
            self._load_cheat_preset,
            layout,
            name="cheat_load",
        )

        layout.addStretch()

    def _on_load_preset(self):
        """Handle load button click for normal presets."""
        # Get the current value from SearchableFilterableComboBox
        # The value is the preset ID as integer (e.g., 1 for "001")
        preset_id_int = self.instrument_selection_combo.value()
        preset_id = str(preset_id_int).zfill(3)  # Convert back to 3-digit format
        # Emit signal with preset number (preset ID as int)
        self.parent.load_preset(int(preset_id))

    def _load_cheat_preset(self):
        """
        Load a Digital Synth preset on the Analog Synth channel (Cheat Mode).
        """
        if not hasattr(self.parent, "midi_helper") or not self.parent.midi_helper:
            log.warning("⚠️ MIDI helper not available for cheat preset loading")
            return

        # Get the current value from SearchableFilterableComboBox
        # The value is the preset ID as integer (e.g., 1 for "001")
        preset_id_int = self.cheat_preset_combo_box.value()
        program_number = str(preset_id_int).zfill(3)  # Convert back to 3-digit format

        log.message("=======load_cheat_preset (Cheat Mode)=======")
        log.parameter("combo box program_number", program_number)

        # Get MSB, LSB, PC values from the Digital preset list
        msb = get_preset_parameter_value(
            "msb", program_number, JDXi.UI.Preset.Digital.LIST
        )
        lsb = get_preset_parameter_value(
            "lsb", program_number, JDXi.UI.Preset.Digital.LIST
        )
        pc = get_preset_parameter_value(
            "pc", program_number, JDXi.UI.Preset.Digital.LIST
        )

        if None in [msb, lsb, pc]:
            log.warning(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return

        log.message("retrieved msb, lsb, pc for cheat preset:")
        log.parameter("combo box msb", msb)
        log.parameter("combo box lsb", lsb)
        log.parameter("combo box pc", pc)
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change on ANALOG_SYNTH channel (Ch3)
        # Note: PC is 0-based in MIDI, so subtract 1
        self.parent.midi_helper.send_bank_select_and_program_change(
            MidiChannel.ANALOG_SYNTH,  # Send to Analog Synth channel (Ch3)
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1,  # Convert 1-based PC to 0-based
        )

        # Request data update
        if hasattr(self.parent, "data_request"):
            self.parent.data_request()

    def setup_header_layout(self) -> None:
        """Top layout with title and image ---"""
        # Ensure setup() has been called first
        if self.layout is None:
            self.setup()
        self.hlayout = QHBoxLayout()
        # Set proper spacing on horizontal layout
        self.hlayout.setSpacing(JDXi.UI.Style.SPACING)
        self.hlayout.addStretch()
        # Add the horizontal layout to the vertical layout
        self.layout.addLayout(self.hlayout)

    def add_stretch(self):
        """Pad both sides by symmetry, supposedly."""
        self.hlayout.addStretch()
        # Add stretch at bottom for vertical centering
        self.layout.addStretch()
