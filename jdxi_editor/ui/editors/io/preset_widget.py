"""
preset widget
"""

class PresetWidget(QWidget):
    """Preset Widget"""
    
    def __init__(parent):
        self.parent = parent
        preset_vlayout = QVBoxLayout()
        preset_layout.setContentsMargins(
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
        icon_row = JDXi.UI.IconRegistry.create_generic_musical_icon_row()
        # Transfer all items from icon_row to icon_row_container
        while icon_row.count() > 0:
            item = icon_row.takeAt(0)
            if item.widget():
                icon_row_container.addWidget(item.widget())
            elif item.spacerItem():
                icon_row_container.addItem(item.spacerItem())
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
            JDXi.UI.IconRegistry.get_icon(
                JDXi.UI.IconRegistry.FOLDER_NOTCH_OPEN, color=JDXi.UI.Style.FOREGROUND
            ),
            "Load Preset",
        )
        self.load_button.clicked.connect(lambda: self.load_preset_by_program_change())
        preset_vlayout.addWidget(self.load_button)

        # Connect combo box valueChanged to load preset directly (optional)
        # self.preset_combo_box.valueChanged.connect(self.load_preset_by_program_change)