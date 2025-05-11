"""
combo_box.py

This module defines a custom combo box widget for selecting presets in the JDXI editor.
It provides a user-friendly interface for searching and selecting presets from a list,
and emits a signal when a preset is loaded. The widget includes a search box, a category
selector, and a load button. The presets are displayed in a combo box, allowing users
to filter and select them easily.
#                 selected_text.split(":")[0].strip()
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Signal

from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.log.message import log_message
from jdxi_editor.jdxi.style import JDXiStyle


class PresetComboBox(QWidget):
    """
    A custom widget for selecting presets from a combo box.
    """

    preset_loaded = Signal(int)  # Signal to emit when address preset is loaded

    def __init__(self, presets, parent=None):
        """initialize the PresetComboBox widget."""
        super().__init__(parent)
        self.preset_list = presets
        self.full_presets = presets
        self.index_mapping = []
        self.category_mapping = {}
        self.presets = {}

        # Layout
        layout = QVBoxLayout(self)

        # Search Box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._populate_presets)
        search_row.addWidget(self.search_box)
        layout.addLayout(search_row)

        # ComboBox
        self.combo_box = QComboBox()
        self.combo_box.setEditable(True)  # Allow text search
        layout.addWidget(self.combo_box)

        # ComboBox
        self.category_combo_box = QComboBox()
        self.category_combo_box.setEditable(True)  # Allow text search
        self.category_combo_box.addItem("No Category Selected")
        categories = set(preset["category"] for preset in self.preset_list)
        self.category_combo_box.addItems(sorted(categories))
        self.category_combo_box.currentIndexChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo_box)

        # Load Button
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._on_load_clicked)
        layout.addWidget(self.load_button)
        self._populate_presets()
        self.setStyleSheet(JDXiStyle.COMBO_BOX)

    def _on_load_clicked(self):
        """Handle load button click."""
        preset_name = self.combo_box.currentText()
        log_message(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        self.preset_loaded.emit(int(program_number))
        log_message(f"combo box program_number : {program_number}")

    def _filter_presets(self, search_text: str):
        """
        Filter presets based on the search text.
        :param search_text: str
        :return: None
        """
        filtered_presets = []
        self.index_mapping = []

        if isinstance(self.full_presets, dict):
            for category, presets in self.full_presets.items():
                for i, preset in enumerate(presets):
                    if search_text.lower() in preset.lower():
                        filtered_presets.append(f"{category}: {preset}")
                        self.index_mapping.append((category, i))
        else:
            for i, preset in enumerate(self.full_presets):
                if search_text.lower() in preset.lower():
                    filtered_presets.append(preset)
                    self.index_mapping.append(i)

        self.combo_box.clear()
        self.combo_box.addItems(filtered_presets)

    def update_category_combo_box_categories(self):
        """Update the category combo box with available categories."""
        categories = set(preset["category"] for preset in self.preset_list)
        self.category_combo_box.blockSignals(True)  # Block signals during update

        # Clear and update items
        self.category_combo_box.clear()
        self.category_combo_box.addItem(
            "No Category Selected"
        )  # Add the default option
        self.category_combo_box.addItems(
            sorted(categories)
        )  # Add the sorted categories

        # Set the default selected index
        self.category_combo_box.setCurrentIndex(
            0
        )  # Select "No Category Selected" as default

        self.category_combo_box.blockSignals(False)  # Unblock signals after update

    def set_presets(self, presets):
        self.full_presets = presets
        self._filter_presets(self.search_box.text())

    def current_preset(self):
        """Get the currently selected preset."""
        return self.combo_box.currentText()

    def on_category_changed(self, _):
        """Handle category selection change."""
        self._populate_presets()

    def _populate_presets(self, search_text: str = ""):
        """Populate the program list with available presets."""

        selected_category = self.category_combo_box.currentText()
        log_parameter("Selected Category:", selected_category)

        self.combo_box.clear()
        self.presets.clear()

        filtered_list = [  # Filter programs based on bank and genre
            preset
            for preset in self.preset_list
            if (selected_category in ["No Category Selected", preset["category"]])
        ]
        filtered_presets = []
        for i, preset in enumerate(filtered_list):
            if search_text.lower() in preset["name"].lower():
                filtered_presets.append(preset)

        for preset in filtered_presets:  # Add programs to the combo box
            preset_name = preset["name"]
            preset_id = preset["id"]
            index = len(self.presets)  # Use the current number of programs
            self.combo_box.addItem(f"{preset_id} - {preset_name}", index)
            self.presets[preset_name] = index
        self.combo_box.setCurrentIndex(0)  # Update the UI with the new program list
        self.combo_box.setCurrentIndex(0)  # Select "No Category Selected" as default
