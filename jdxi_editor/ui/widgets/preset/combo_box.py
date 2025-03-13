import logging

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


class PresetComboBox(QWidget):
    preset_selected = Signal(int)  # Signal to emit when address preset is selected
    preset_loaded = Signal(int)  # Signal to emit when address preset is loaded

    def __init__(self, presets, parent=None):
        super().__init__(parent)
        self.full_presets = presets
        self.index_mapping = []
        self.category_mapping = {}

        # Layout
        layout = QVBoxLayout(self)

        # Search Box
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(self._filter_presets)
        search_row.addWidget(self.search_box)
        layout.addLayout(search_row)

        # ComboBox
        self.combo_box = QComboBox()
        self.combo_box.setEditable(True)  # Allow text search
        # self.combo_box.currentIndexChanged.connect(self._on_preset_selected)
        layout.addWidget(self.combo_box)

        # Load Button
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._on_load_clicked)
        layout.addWidget(self.load_button)

        self.set_presets(presets)

    def _on_preset_selected(self, index):
        self.preset_selected.emit(index)

    def _on_load_clicked(self):
        current_index = self.combo_box.currentIndex()
        logging.info(f"current index: {current_index}")
        if 0 <= current_index < len(self.index_mapping):
            original_index = self.index_mapping[current_index]
            logging.info(f"original index: {original_index}")
            self.preset_loaded.emit(original_index - 1)

    def _filter_presets(self, search_text: str):
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

    def set_presets(self, presets):
        self.full_presets = presets
        self._filter_presets(self.search_box.text())

    def current_preset(self):
        return self.combo_box.currentText()
