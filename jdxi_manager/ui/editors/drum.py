"""
DrumEditor Module
=================

This module provides the `DrumEditor` class, which serves as an editor for JD-Xi Drum Kit parameters.
It enables users to modify drum kit settings, select presets, and send MIDI messages to a connected JD-Xi synthesizer.

Classes
-------

- `DrumEditor`: A graphical editor for JD-Xi drum kits, supporting preset selection, parameter adjustments, and MIDI communication.

Dependencies
------------

- `PySide6.QtWidgets` for UI components.
- `PySide6.QtCore` for Qt core functionality.
- `jdxi_manager.data.parameter.drums.DrumParameter` for drum parameter definitions.
- `jdxi_manager.data.presets.data.DRUM_PRESETS_ENUMERATED` for enumerated drum presets.
- `jdxi_manager.data.presets.type.PresetType` for preset categorization.
- `jdxi_manager.midi.io.MIDIHelper` for MIDI communication.
- `jdxi_manager.midi.preset.loader.PresetLoader` for loading JD-Xi presets.
- `jdxi_manager.ui.editors.drum_partial.DrumPartialEditor` for managing individual drum partials.
- `jdxi_manager.ui.style.Style` for UI styling.
- `jdxi_manager.ui.editors.base.BaseEditor` as the base class for the editor.
- `jdxi_manager.midi.constants.sysex.TEMPORARY_DIGITAL_SYNTH_1_AREA` for SysEx address handling.
- `jdxi_manager.ui.widgets.preset.combo_box.PresetComboBox` for preset selection.

Features
--------

- Displays and edits JD-Xi drum kit parameters.
- Supports drum kit preset selection and loading.
- Provides sliders, spin boxes, and combo boxes for adjusting kit parameters.
- Includes a tabbed interface for managing individual drum partials.
- Sends MIDI System Exclusive (SysEx) messages to update the JD-Xi in real time.

Usage
-----

To use the `DrumEditor`, instantiate it with an optional `MIDIHelper` instance:

.. code-block:: python

    from jdxi_manager.midi.io import MIDIHelper
    from jdxi_manager.ui.editors.drum_editor import DrumEditor
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = DrumEditor(midi_helper)
    editor.show()
    app.exec()

"""

import os
import re
import logging
from typing import Optional, Dict

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QWidget,
    QTabWidget,
    QFormLayout,
    QSpinBox,
    QSlider,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from jdxi_manager.data.parameter.drums import DrumParameter
from jdxi_manager.data.presets.data import DRUM_PRESETS_ENUMERATED
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.io import MIDIHelper
from jdxi_manager.midi.preset.loader import PresetLoader
from jdxi_manager.ui.editors.drum_partial import DrumPartialEditor
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.editors.base import BaseEditor
from jdxi_manager.midi.constants.sysex import (
    TEMPORARY_DIGITAL_SYNTH_1_AREA,
)
from jdxi_manager.ui.widgets.preset.combo_box import PresetComboBox


class DrumEditor(BaseEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent=None):
        super().__init__(midi_helper, parent)

        # Initialize class attributes
        self.partial_editors = {}
        self.partial_tab_widget = QTabWidget()
        self.partial_num = 1
        self.group = 0x00
        self.address = 0x00  # Initialize address to common area
        self.image_label = None
        self.instrument_icon_folder = "drum_kits"
        # Main layout
        self.controls: Dict[DrumParameter, QWidget] = {}
        self.preset_type = PresetType.DRUMS
        self.preset_loader = PresetLoader(self.midi_helper)
        self.partial_editors = {}
        self.main_window = parent

        # Create layouts
        main_layout = QVBoxLayout(self)
        upper_layout = QHBoxLayout()
        main_layout.addLayout(upper_layout)
        self.setMinimumSize(1000, 500)
        self.midi_requests = [
            "F0 41 10 00 00 00 0E 11 19 70 00 00 00 00 00 12 65 F7",
            "F0 41 10 00 00 00 0E 11 19 70 2E 00 00 00 01 43 05 F7",
            "F0 41 10 00 00 00 0E 11 19 70 30 00 00 00 01 43 03 F7",
            "F0 41 10 00 00 00 0E 11 19 70 32 00 00 00 01 43 01 F7",
            "F0 41 10 00 00 00 0E 11 19 70 34 00 00 00 01 43 7F F7",
            "F0 41 10 00 00 00 0E 11 19 70 36 00 00 00 01 43 7D F7",
        ]
        # Title and drum kit selection
        drum_group = QGroupBox("Drum Kit")
        self.instrument_title_label = QLabel(
            f"Drum Kit:\n {DRUM_PRESETS_ENUMERATED[0]}"
            if DRUM_PRESETS_ENUMERATED
            else "Drum Kit"
        )
        drum_group.setStyleSheet(
            """
            QGroupBox {
            width: 300px;
            }
        """
        )
        self.instrument_title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
        """
        )
        drum_group_layout = QVBoxLayout()
        drum_group.setLayout(drum_group_layout)
        drum_group_layout.addWidget(self.instrument_title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        drum_group_layout.addWidget(self.read_request_button)

        self.selection_label = QLabel("Select a drum kit:")
        drum_group_layout.addWidget(self.selection_label)
        # Drum kit selection

        self.instrument_selection_combo = PresetComboBox(DRUM_PRESETS_ENUMERATED)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_loader.preset_number
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        # Connect QComboBox signal to PresetHandler
        self.main_window.drums_preset_handler.preset_changed.connect(
            self.update_combo_box_index
        )

        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        drum_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(drum_group)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        upper_layout.addWidget(self.image_label)

        # Common controls
        common_group = QGroupBox("Common")
        common_layout = QFormLayout()

        # Assign Type control
        self.assign_type_combo = QComboBox()
        self.assign_type_combo.addItems(["MULTI", "SINGLE"])
        common_layout.addRow("Assign Type", self.assign_type_combo)

        # Mute Group control
        self.mute_group_spin = QSpinBox()
        self.mute_group_spin.setRange(0, 31)
        common_layout.addRow("Mute Group", self.mute_group_spin)

        # Kit Level control
        self.kit_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.kit_level_slider.setRange(0, 127)
        self.kit_level_slider.valueChanged.connect(self.on_kit_level_changed)
        common_layout.addRow("Kit Level", self.kit_level_slider)

        # Partial Pitch Bend Range
        self.pitch_bend_range_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_bend_range_slider.setRange(0, 48)
        self.pitch_bend_range_slider.valueChanged.connect(
            self.on_pitch_bend_range_changed
        )
        common_layout.addRow("Pitch Bend Range", self.pitch_bend_range_slider)

        # Partial Receive Expression
        self.receive_expression_combo = QComboBox()
        self.receive_expression_combo.addItems(["OFF", "ON"])
        common_layout.addRow("Receive Expression", self.receive_expression_combo)

        # Partial Receive Hold-1
        self.receive_hold_combo = QComboBox()
        self.receive_hold_combo.addItems(["OFF", "ON"])
        common_layout.addRow("Receive Hold-1", self.receive_hold_combo)

        # One Shot Mode
        self.one_shot_mode_combo = QComboBox()
        self.one_shot_mode_combo.addItems(["OFF", "ON"])
        common_layout.addRow("One Shot Mode", self.one_shot_mode_combo)

        common_group.setLayout(common_layout)
        upper_layout.addWidget(common_group)

        # Create scroll area for partials
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)

        # Setup tab widget
        self.partial_tab_widget.setStyleSheet(Style.JDXI_TABS_DRUMS)
        scroll.setWidget(self.partial_tab_widget)

        # Initialize partial editors
        self._setup_partial_editors()

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_num)
        self.data_request()

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        logging.info(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(f"Drums\n {selected_synth_text}")

    def _setup_partial_editors(self):
        """Setup all partial editors and tabs"""
        # Map of partial names to their indices
        partial_mapping = {
            "BD1": 0,
            "RIM": 1,
            "BD2": 2,
            "CLAP": 3,
            "BD3": 4,
            "SD1": 5,
            "CHH": 6,
            "SD2": 7,
            "PHH": 8,
            "SD3": 9,
            "OHH": 10,
            "SD4": 11,
            "TOM1": 12,
            "PRC1": 13,
            "TOM2": 14,
            "PRC2": 15,
            "TOM3": 16,
            "PRC3": 17,
            "CYM1": 18,
            "PRC4": 19,
            "CYM2": 20,
            "PRC5": 21,
            "CYM3": 22,
            "HIT": 23,
            "OTH1": 24,
            "OTH2": 25,
        }

        # Create editor for each partial
        for partial_name, partial_index in partial_mapping.items():
            editor = DrumPartialEditor(
                midi_helper=self.midi_helper,
                partial_num=partial_index,
                partial_name=partial_name,
                parent=self,
            )
            self.partial_editors[partial_index] = editor
            self.partial_tab_widget.addTab(editor, partial_name)

    def update_partial_num(self, index: int):
        """Update the current partial number based on tab index"""
        try:
            partial_name = list(self.partial_editors.keys())[index]
            self.partial_num = index
            logging.info(f"Updated to partial {partial_name} (index {index})")
        except IndexError:
            logging.error(f"Invalid partial index: {index}")

    def update_instrument_image(self):
        """ update  """

        def load_and_set_image(image_path):
            """Helper function to load and set the image on the label."""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    250, Qt.TransformationMode.SmoothTransformation
                )  # Resize to 250px height
                self.image_label.setPixmap(scaled_pixmap)
                return True
            return False

        # Define paths
        default_image_path = os.path.join("resources", "drum_kits", "drums.png")
        selected_kit_text = self.instrument_selection_combo.combo_box.currentText()

        # Try to extract drum kit name from the selected text
        image_loaded = False
        if drum_kit_matches := re.search(
                r"(\d{3}): (\S+).+", selected_kit_text, re.IGNORECASE
        ):
            selected_kit_name = (
                drum_kit_matches.group(2).lower().replace("&", "_").split("_")[0]
            )
            specific_image_path = os.path.join(
                "resources", "drum_kits", f"{selected_kit_name}.png"
            )
            image_loaded = load_and_set_image(specific_image_path)

        # Fallback to default image if no specific image is found
        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def on_kit_level_changed(self, value):
        """Handle kit level slider value change"""
        # Use the helper function to send the SysEx message
        # self.send_sysex_message(0x0C, value)
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
            part=0x70,
            group=0x00,  # 00 0C | 0aaa aaaa | Kit Level (0 - 127)
            param=0x0C,
            value=value,  # Make sure this value is being sent
        )

    def on_pitch_bend_range_changed(self, value):
        """Handle pitch bend range value change"""
        # Use the helper function to send the SysEx message
        # self.send_sysex_message(0x2E, value)
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
            part=0x70,
            group=0x2E,  # 00 0C | 0aaa aaaa | Kit Level (0 - 127)
            param=0x1C,
            value=value,  # Make sure this value is being sent
        )
