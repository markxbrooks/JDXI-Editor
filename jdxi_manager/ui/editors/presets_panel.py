"""
Usage
from .widgets.preset_panel import PresetPanel

    self.preset_panel = PresetPanel('digital1', self)
    self.preset_panel.add_presets(DIGITAL_SN_PRESETS)
    self.preset_window.setCentralWidget(self.preset_panel)
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QScrollArea, QWidget
)
from PySide6.QtCore import Signal, Qt
import logging

from jdxi_manager.ui.style import Style


class PresetPanel(QWidget):
    """Panel for selecting and managing presets"""

    presetChanged = Signal(int, str)  # Emits (preset_number, preset_name)

    def __init__(self, name, parent=None):
        """Initialize preset panel

        Args:
            name: Name of the preset panel
            parent: Parent widget
        """
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.presets = []
        self._create_ui()

        # Set minimum size for the panel
        self.setMinimumWidth(280)
        self.setMinimumHeight(400)

    def _create_ui(self):
        """Create the preset panel UI"""
        layout = QVBoxLayout(self)

        # Add header
        header = QLabel("Presets")
        header.setStyleSheet(f"background-color: {Style.PRESET_BG}; color: white; padding: 5px;")
        layout.addWidget(header)

        # Create scroll area for presets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create widget for preset buttons
        self.preset_widget = QWidget()
        self.preset_layout = QVBoxLayout(self.preset_widget)

        # Add stretch at bottom
        self.preset_layout.addStretch()

        # Set up scroll area
        scroll.setWidget(self.preset_widget)
        layout.addWidget(scroll)

    def add_presets(self, presets):
        """Add presets to the panel with categories

        Args:
            presets: List of preset names
        """
        # Clear existing presets
        for i in reversed(range(self.preset_layout.count())):
            widget = self.preset_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Store presets list
        self.presets = presets

        # Define categories
        categories = {
            'KEYBOARD': [],  # 09: Keyboard
            'BASS': [],  # 21: Bass
            'LEAD': [],  # 34: Lead
            'BRASS': [],  # 35: Brass
            'PAD': [],  # 36: Strings/Pad
            'FX': [],  # 39: FX/Other
            'SEQ': []  # 40: Seq
        }

        # Sort presets into categories
        for preset in presets:
            if 'Piano' in preset or 'EP' in preset or 'Clav' in preset or 'Key' in preset:
                categories['KEYBOARD'].append(preset)
            elif 'Bass' in preset:
                categories['BASS'].append(preset)
            elif 'Lead' in preset:
                categories['LEAD'].append(preset)
            elif 'Brass' in preset:
                categories['BRASS'].append(preset)
            elif 'Strings' in preset or 'Pad' in preset:
                categories['PAD'].append(preset)
            elif 'FX' in preset or 'Hit' in preset:
                categories['FX'].append(preset)
            elif 'SEQ' in preset:
                categories['SEQ'].append(preset)
            else:
                categories['PAD'].append(preset)  # Default to PAD category

        # Add presets by category
        for category, cat_presets in categories.items():
            if cat_presets:  # Only add categories that have presets
                # Add category header
                header = QLabel(category)
                header.setStyleSheet("""
                    QLabel {
                        background-color: #2A2A2A;
                        color: white;
                        padding: 5px;
                        font-weight: bold;
                    }
                """)
                self.preset_layout.addWidget(header)

                # Add category presets
                for preset_name in cat_presets:
                    btn = QPushButton(preset_name)
                    btn.clicked.connect(lambda checked, name=preset_name: self.parent.load_preset(name))
                    self.preset_layout.addWidget(btn)

        # Add stretch at bottom
        self.preset_layout.addStretch() 