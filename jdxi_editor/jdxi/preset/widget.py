"""Preset Widget to be used by All Editors"""

from typing import TYPE_CHECKING, Any, Optional

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.preset.helper import create_scroll_container
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.jdxi.style.icons import IconRegistry
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import SearchableFilterableComboBox

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
        group.setMinimumWidth(JDXiStyle.INSTRUMENT_IMAGE_WIDTH)
        self.hlayout.addWidget(group)

    def add_preset_group(self, group: QGroupBox):
        """add groupbox for instruments"""
        self.hlayout.addWidget(group)

    def setup(self):
        """set up the widget - creates the main vertical layout"""
        if self.layout is None:
            self.layout = QVBoxLayout()
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
        instrument_image_group.setStyleSheet(JDXiStyle.INSTRUMENT_IMAGE_LABEL)
        instrument_image_group.setMinimumWidth(JDXiStyle.INSTRUMENT_IMAGE_WIDTH)
        instrument_image_group.setMaximumHeight(JDXiStyle.INSTRUMENT_IMAGE_HEIGHT)
        return (
            instrument_image_group,
            self.instrument_image_label,
            instrument_group_layout,
        )

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
            instrument_preset_group.setStyleSheet(JDXiStyle.GROUP_BOX_ANALOG)

        # For Analog, create tabs; for others, create simple layout
        if synth_type == "Analog":
            # Create tabbed widget inside the group box
            preset_tabs = QTabWidget()
            instrument_title_group_layout.addWidget(preset_tabs)

            # === Tab 1: Normal Analog Presets ===
            normal_preset_widget, normal_preset_layout = create_scroll_container()
            self._add_normal_preset_content(normal_preset_layout, synth_type)
            try:
                analog_presets_icon = qta.icon("mdi.music-note-multiple", color=JDXiStyle.GREY)
                if analog_presets_icon.isNull():
                    raise ValueError("Icon is null")
            except:
                analog_presets_icon = IconRegistry.get_icon(IconRegistry.MUSIC, color=JDXiStyle.GREY)
            preset_tabs.addTab(normal_preset_widget, analog_presets_icon, "Analog Presets")

            # === Tab 2: Cheat Presets (Digital Synth presets on Analog channel) ===
            cheat_preset_widget, cheat_preset_layout = create_scroll_container()
            self._add_cheat_preset_content(cheat_preset_layout)
            cheat_presets_icon = qta.icon("mdi.code-braces", color=JDXiStyle.GREY)
            preset_tabs.addTab(cheat_preset_widget, cheat_presets_icon, "Cheat Presets")
        else:
            # For Digital/Drums, create simple layout without tabs
            self._add_normal_preset_content(instrument_title_group_layout, synth_type)

        return instrument_preset_group

    def _add_normal_preset_content(self, layout: QVBoxLayout, synth_type: str):
        """Add normal preset selection content to the layout."""
        # Add icon row at the top
        icon_row = IconRegistry.create_generic_musical_icon_row()
        layout.addLayout(icon_row)
        
        self.instrument_title_label = DigitalTitle()
        layout.addWidget(self.instrument_title_label)
        # --- Update_tone_name
        self.edit_tone_name_button = QPushButton("Edit tone name")
        self.edit_tone_name_button.clicked.connect(self.parent.edit_tone_name)
        layout.addWidget(self.edit_tone_name_button)
        # --- Read request button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.parent.data_request)
        layout.addWidget(self.read_request_button)
        self.instrument_selection_label = QLabel(f"Select a {synth_type} synth:")
        layout.addWidget(self.instrument_selection_label)
        
        # Build preset options, values, and categories from preset_list
        preset_options = [f"{preset['id']} - {preset['name']}" for preset in self.parent.preset_list]
        # Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset['id']) for preset in self.parent.preset_list]
        preset_categories = sorted(set(preset["category"] for preset in self.parent.preset_list))
        
        # Category filter function for presets
        def preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # Extract preset ID from display string (format: "001 - Preset Name")
            preset_id_str = preset_display.split(" - ")[0] if " - " in preset_display else None
            if preset_id_str:
                # Find the preset in the list and check its category
                for preset in self.parent.preset_list:
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
        )
        
        # Apply styling
        if synth_type == "Analog":
            # Apply Analog styling to the combo box widget
            self.instrument_selection_combo.combo_box.setStyleSheet(JDXiStyle.COMBO_BOX_ANALOG)
        else:
            self.instrument_selection_combo.combo_box.setStyleSheet(JDXiStyle.COMBO_BOX)
        
        # Connect signals - use combo_box for currentIndexChanged
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.parent.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.parent.update_instrument_title
        )
        
        # Create a load button (SearchableFilterableComboBox doesn't have one built-in)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self._on_load_preset)
        
        # Add load button next to combo box
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.instrument_selection_combo)
        button_layout.addWidget(load_button)
        layout.addLayout(button_layout)
        
        # Store reference to load button for compatibility
        self.instrument_selection_combo.load_button = load_button
        layout.addStretch()

    def _add_cheat_preset_content(self, layout: QVBoxLayout):
        """Add cheat preset content to the layout (Analog only)."""
        from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST

        # Add icon row at the top
        icon_row = IconRegistry.create_generic_musical_icon_row()
        layout.addLayout(icon_row)

        # Build preset options, values, and categories from DIGITAL_PRESET_LIST
        preset_options = [f"{preset['id']} - {preset['name']}" for preset in DIGITAL_PRESET_LIST]
        # Convert preset IDs to integers for SearchableFilterableComboBox (e.g., "001" -> 1)
        preset_values = [int(preset['id']) for preset in DIGITAL_PRESET_LIST]
        preset_categories = sorted(set(preset["category"] for preset in DIGITAL_PRESET_LIST))
        
        # Category filter function for presets
        def cheat_preset_category_filter(preset_display: str, category: str) -> bool:
            """Check if a preset matches a category."""
            if not category:
                return True
            # Extract preset ID from display string (format: "001 - Preset Name")
            preset_id_str = preset_display.split(" - ")[0] if " - " in preset_display else None
            if preset_id_str:
                # Find the preset in the list and check its category
                for preset in DIGITAL_PRESET_LIST:
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

        # Load Button
        self.cheat_load_button = QPushButton(
            IconRegistry.get_icon(IconRegistry.FOLDER_NOTCH_OPEN, color=JDXiStyle.FOREGROUND),
            "Load Preset",
        )
        self.cheat_load_button.clicked.connect(self._load_cheat_preset)
        layout.addWidget(self.cheat_load_button)

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
            from decologr import Decologr as log

            log.warning("⚠️ MIDI helper not available for cheat preset loading")
            return

        from decologr import Decologr as log

        from jdxi_editor.log.midi_info import log_midi_info
        from jdxi_editor.midi.channel.channel import MidiChannel
        from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
        from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value

        # Get the current value from SearchableFilterableComboBox
        # The value is the preset ID as integer (e.g., 1 for "001")
        preset_id_int = self.cheat_preset_combo_box.value()
        program_number = str(preset_id_int).zfill(3)  # Convert back to 3-digit format
        
        log.message("=======load_cheat_preset (Cheat Mode)=======")
        log.parameter("combo box program_number", program_number)

        # Get MSB, LSB, PC values from the Digital preset list
        msb = get_preset_parameter_value("msb", program_number, DIGITAL_PRESET_LIST)
        lsb = get_preset_parameter_value("lsb", program_number, DIGITAL_PRESET_LIST)
        pc = get_preset_parameter_value("pc", program_number, DIGITAL_PRESET_LIST)

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
        self.hlayout.addStretch()
        # Add the horizontal layout to the vertical layout
        self.layout.addLayout(self.hlayout)

    def add_stretch(self):
        """Pad both sides by symmetry, supposedly."""
        self.hlayout.addStretch()
        # Add stretch at bottom for vertical centering
        self.layout.addStretch()
