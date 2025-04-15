"""
Arpeggio Editor Module

This module defines the `ArpeggioEditor` class, a specialized editor for configuring arpeggiator
settings within a synthesizer. It extends the `SynthEditor` class, providing a user-friendly
interface to control various arpeggiator parameters.

Classes:
    - ArpeggioEditor: A `QWidget` subclass that allows users to modify arpeggiator parameters
      such as style, grid, duration, velocity, accent, swing, octave range, and motif.

Features:
    - Provides an intuitive UI with labeled controls and dropdown menus for parameter selection.
    - Includes a toggle switch to enable or disable the arpeggiator.
    - Displays an instrument image for better user engagement.
    - Uses MIDI integration to send real-time parameter changes to the synthesizer.
    - Supports dynamic visualization and interaction through sliders and combo boxes.

Usage:
    ```python
    from PySide6.QtWidgets import QApplication
    from midi_helper import MIDIHelper

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = ArpeggioEditor(midi_helper=midi_helper)
    editor.show()
    app.exec()
    ```

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - ArpeggioParameter (for managing parameter addresses and value ranges)
    - Slider (for smooth control over numerical parameters)

"""

import os
from typing import Dict

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from jdxi_editor.midi.data.arpeggio import ArpeggioSwitch
from jdxi_editor.midi.data.arpeggio.arpeggio import (
    ArpeggioMotif,
    ArpeggioOctaveRange,
    ArpeggioGrid,
    ArpeggioDuration,
)
from jdxi_editor.midi.data.arpeggio.data import (
    ARPEGGIO_GRID,
    ARP_DURATION,
    ARPEGGIO_STYLE,
    ArpeggioStyle,
)
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioAddress, ArpeggioParameter
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParameter
from jdxi_editor.midi.data.parameter.program.zone import ProgramZoneParameter
from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.ui.editors import SynthEditor
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.ui.widgets.display.digital import DigitalDisplay, DigitalTitle


class ArpeggioEditor(SynthEditor):
    """Arpeggio Editor Window"""

    def __init__(self, midi_helper: MidiIOHelper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arpeggio Editor")
        self.midi_helper = midi_helper
        self.setFixedWidth(450)
        self.address_msb = ArpeggioAddress.TEMPORARY_PROGRAM
        self.address_umb = ArpeggioAddress.ARP_PART
        self.address_lmb = ArpeggioAddress.ARP_GROUP
        self.partial_number = 0
        self.instrument_icon_folder = "arpeggiator"
        self.default_image = "arpeggiator2.png"
        self.controls: Dict[SynthParameter, QWidget] = {}

        if parent:
            if parent.current_synth_type:
                if parent.current_synth_type == "Digital 1":
                    self.partial_number = 0
                elif parent.current_synth_type == "Digital 2":
                    self.partial_number = 1
                elif parent.current_synth_type == "Digital 3":
                    self.partial_number = 2
                elif parent.current_synth_type == "Digital 4":
                    self.partial_number = 3

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_label = DigitalTitle(tone_name="Arpeggiator")
        self.title_label.setStyleSheet(JDXIStyle.INSTRUMENT_TITLE_LABEL)
        title_row_layout = QHBoxLayout()
        title_row_layout.addWidget(self.title_label)

        layout.addLayout(title_row_layout)
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        title_row_layout.addWidget(self.image_label)
        self.update_instrument_image()

        # Add on-off switch
        program_zone_row = QHBoxLayout()
        common_button = self._create_parameter_switch(
            ProgramZoneParameter.ARPEGGIO_SWITCH,
            "Master Arpeggiator",
            [switch_setting.display_name for switch_setting in ArpeggioSwitch],
        )
        program_zone_row.addWidget(common_button)

        layout.addLayout(program_zone_row)

        # Add on-off switch
        switch_row = QHBoxLayout()
        self.switch_button = self._create_parameter_switch(
            ArpeggioParameter.ARPEGGIO_SWITCH,
            "Arpeggiator",
            [switch_setting.display_name for switch_setting in ArpeggioSwitch],
        )
        switch_row.addWidget(self.switch_button)
        layout.addLayout(switch_row)

        # Create address combo box for Arpeggio Style
        self.style_combo = self._create_parameter_combo_box(
            ArpeggioParameter.ARPEGGIO_STYLE, "Style", ARPEGGIO_STYLE
        )
        style_row = QHBoxLayout()
        style_row.addWidget(self.style_combo)
        layout.addLayout(style_row)

        # Create address combo box for Arpeggio Grid
        # Add grid combo box
        grid_row = QHBoxLayout()
        self.grid_combo = self._create_parameter_combo_box(
            ArpeggioParameter.ARPEGGIO_GRID,
            "Grid:",
            [grid.display_name for grid in ArpeggioGrid],
        )
        grid_row.addWidget(self.grid_combo)
        layout.addLayout(grid_row)

        # Add grid combo box
        duration_row = QHBoxLayout()
        # Create address combo box for Arpeggio Duration
        self.duration_combo = self._create_parameter_combo_box(
            ArpeggioParameter.ARPEGGIO_DURATION,
            "Duration",
            [duration.display_name for duration in ArpeggioDuration],
        )
        duration_row.addWidget(self.duration_combo)
        layout.addLayout(duration_row)

        # Add sliders
        self.velocity_slider = self._create_parameter_slider(
            ArpeggioParameter.ARPEGGIO_VELOCITY, "Velocity", 0, 127
        )
        layout.addWidget(self.velocity_slider)

        self.accent_slider = self._create_parameter_slider(
            ArpeggioParameter.ARPEGGIO_ACCENT_RATE, "Accent", 0, 127
        )
        layout.addWidget(self.accent_slider)

        # Add octave range combo box
        octave_row = QHBoxLayout()
        self.octave_combo = self._create_parameter_combo_box(
            ArpeggioParameter.ARPEGGIO_OCTAVE_RANGE,
            "Octave Range:",
            [octave.display_name for octave in ArpeggioOctaveRange],
            [octave.midi_value for octave in ArpeggioOctaveRange],
        )
        # Set default to 0
        self.octave_combo.combo_box.setCurrentIndex(3)  # Index 3 is OCT_ZERO
        octave_row.addWidget(self.octave_combo)
        layout.addLayout(octave_row)

        # Add motif combo box
        motif_row = QHBoxLayout()
        self.motif_combo = self._create_parameter_combo_box(
            ArpeggioParameter.ARPEGGIO_MOTIF,
            "Motif:",
            [motif.name for motif in ArpeggioMotif],
        )
        motif_row.addWidget(self.motif_combo)
        layout.addLayout(motif_row)

    def load_and_set_image(self, image_path, secondary_image_path=None):
        """Helper function to load and set the image on the label."""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaledToHeight(
                150, Qt.TransformationMode.SmoothTransformation
            )  # Resize to 250px height
            self.image_label.setPixmap(scaled_pixmap)
            return True
        return False

    def update_instrument_image(self):
        image_loaded = False

        # Define paths
        default_image_path = os.path.join(
            "resources", self.instrument_icon_folder, self.default_image
        )

        if not image_loaded:
            if not self.load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing
