"""Preset Widget to be used by All Editors"""

from typing import Any, Optional

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
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox


class InstrumentPresetWidget(QWidget):
    """InstrumentPresetWidget"""

    def __init__(
        self,
        parent: SynthEditor,  # parent is not optional
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
            preset_tabs.addTab(normal_preset_widget, "Analog Presets")

            # === Tab 2: Cheat Presets (Digital Synth presets on Analog channel) ===
            cheat_preset_widget, cheat_preset_layout = create_scroll_container()
            self._add_cheat_preset_content(cheat_preset_layout)
            preset_tabs.addTab(cheat_preset_widget, "Cheat Presets")
        else:
            # For Digital/Drums, create simple layout without tabs
            self._add_normal_preset_content(instrument_title_group_layout, synth_type)

        return instrument_preset_group

    def _add_normal_preset_content(self, layout: QVBoxLayout, synth_type: str):
        """Add normal preset selection content to the layout."""
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
        self.instrument_selection_combo = PresetComboBox(self.parent.preset_list)
        if synth_type == "Analog":
            self.instrument_selection_combo.setStyleSheet(JDXiStyle.COMBO_BOX_ANALOG)
        else:
            self.instrument_selection_combo.setStyleSheet(JDXiStyle.COMBO_BOX)
        self.instrument_selection_combo.combo_box.setEditable(True)
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.parent.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.parent.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.parent.update_instrument_preset
        )
        self.instrument_selection_combo.preset_loaded.connect(self.parent.load_preset)
        layout.addWidget(self.instrument_selection_combo)
        layout.addStretch()

    def _add_cheat_preset_content(self, layout: QVBoxLayout):
        """Add cheat preset content to the layout (Analog only)."""
        from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST

        # Search Box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search Presets:"))
        self.cheat_search_box = QLineEdit()
        self.cheat_search_box.setPlaceholderText("Search presets...")
        self.cheat_search_box.textChanged.connect(
            lambda text: self._populate_cheat_presets(text)
        )
        search_row.addWidget(self.cheat_search_box)
        layout.addLayout(search_row)

        # Preset List Combobox
        self.cheat_preset_label = QLabel("Preset")
        layout.addWidget(self.cheat_preset_label)
        self.cheat_preset_combo_box = QComboBox()
        # Will be populated by _populate_cheat_presets()
        layout.addWidget(self.cheat_preset_combo_box)

        # Category Combobox
        self.cheat_category_label = QLabel("Category")
        layout.addWidget(self.cheat_category_label)
        self.cheat_category_combo_box = QComboBox()
        self.cheat_category_combo_box.addItem("No Category Selected")
        categories = set(preset["category"] for preset in DIGITAL_PRESET_LIST)
        self.cheat_category_combo_box.addItems(sorted(categories))
        self.cheat_category_combo_box.currentIndexChanged.connect(
            self._on_cheat_category_changed
        )
        layout.addWidget(self.cheat_category_combo_box)

        # Load Button
        self.cheat_load_button = QPushButton(
            qta.icon("ph.folder-notch-open-fill", color=JDXiStyle.FOREGROUND),
            "Load Preset",
        )
        self.cheat_load_button.clicked.connect(self._load_cheat_preset)
        layout.addWidget(self.cheat_load_button)

        layout.addStretch()

        # Initialize cheat presets
        self.cheat_presets = {}  # Maps preset names to indices
        self._populate_cheat_presets()

    def _populate_cheat_presets(self, search_text: str = ""):
        """
        Populate the cheat preset combo box with Digital Synth presets.

        :param search_text: str Search filter text
        """
        if not hasattr(self, "cheat_preset_combo_box"):
            return

        from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST

        selected_category = self.cheat_category_combo_box.currentText()

        self.cheat_preset_combo_box.clear()
        self.cheat_presets.clear()

        # Filter presets by category and search text
        filtered_list = [
            preset
            for preset in DIGITAL_PRESET_LIST
            if (selected_category in ["No Category Selected", preset["category"]])
        ]

        filtered_presets = []
        for preset in filtered_list:
            if search_text.lower() in preset["name"].lower():
                filtered_presets.append(preset)

        # Add presets to combo box
        for preset in filtered_presets:
            preset_name = preset["name"]
            preset_id = preset["id"]
            index = len(self.cheat_presets)
            self.cheat_preset_combo_box.addItem(f"{preset_id} - {preset_name}", index)
            self.cheat_presets[preset_name] = index

        if self.cheat_preset_combo_box.count() > 0:
            self.cheat_preset_combo_box.setCurrentIndex(0)

    def _on_cheat_category_changed(self, index: int):  # pylint: disable=unused-argument
        """Handle category selection change for cheat presets."""
        search_text = (
            self.cheat_search_box.text() if hasattr(self, "cheat_search_box") else ""
        )
        self._populate_cheat_presets(search_text)

    def _load_cheat_preset(self):
        """
        Load a Digital Synth preset on the Analog Synth channel (Cheat Mode).
        """
        if not hasattr(self.parent, "midi_helper") or not self.parent.midi_helper:
            from jdxi_editor.log.logger import Logger as log

            log.warning("⚠️ MIDI helper not available for cheat preset loading")
            return

        from jdxi_editor.log.logger import Logger as log
        from jdxi_editor.log.midi_info import log_midi_info
        from jdxi_editor.midi.channel.channel import MidiChannel
        from jdxi_editor.midi.data.programs.digital import DIGITAL_PRESET_LIST
        from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value

        preset_name = self.cheat_preset_combo_box.currentText()
        log.message("=======load_cheat_preset (Cheat Mode)=======")
        log.parameter("combo box preset_name", preset_name)

        # Extract program number from preset name (format: "001 - Preset Name")
        program_number = preset_name[:3]
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
