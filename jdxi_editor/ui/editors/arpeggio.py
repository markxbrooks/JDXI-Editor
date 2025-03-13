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
import logging

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from jdxi_editor.midi.data.arpeggio import (
    arp_style,
    arp_grid,
    arp_duration,
)
from jdxi_editor.midi.data.parameter.arpeggio import ArpeggioParameter
from jdxi_editor.midi.data.constants.arpeggio import (
    TEMPORARY_PROGRAM,
    ARP_PART,
    ARP_GROUP,
    ArpOctaveRange,
)
from jdxi_editor.midi.io import MIDIHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.editors.synth import SynthEditor
from jdxi_editor.ui.widgets.slider import Slider


class ArpeggioEditor(SynthEditor):
    """ Arpeggio Editor Window"""
    def __init__(self, midi_helper: MIDIHelper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arpeggio Editor")
        self.midi_helper = midi_helper
        self.setFixedWidth(450)
        self.area = TEMPORARY_PROGRAM
        self.part = ARP_PART
        self.group = ARP_GROUP
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_label = QLabel("Arpeggiator")
        self.title_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            """
        )
        layout.addWidget(self.title_label)
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        layout.addWidget(self.image_label)
        self.update_instrument_image()

        # Add on-off switch
        switch_row = QHBoxLayout()
        switch_label = QLabel("Arpeggiator:")
        self.switch_button = QPushButton("OFF")
        self.switch_button.setCheckable(True)
        self.switch_button.clicked.connect(self._on_switch_changed)
        switch_row.addWidget(switch_label)
        switch_row.addWidget(self.switch_button)
        layout.addLayout(switch_row)

        # Create address combo box for Arpeggio Style
        self.style_combo = QComboBox()
        # Add style combo box
        style_row = QHBoxLayout()
        style_label = QLabel("Style:")
        self.style_combo.addItems(arp_style)  # Use arp_style list
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        style_row.addWidget(style_label)
        style_row.addWidget(self.style_combo)
        layout.addLayout(style_row)

        # Create address combo box for Arpeggio Grid
        # Add grid combo box
        grid_row = QHBoxLayout()
        grid_label = QLabel("Grid:")
        self.grid_combo = QComboBox()
        self.grid_combo.addItems(arp_grid)  # Use arp_grid list
        self.grid_combo.currentIndexChanged.connect(self._on_grid_changed)
        grid_row.addWidget(grid_label)
        grid_row.addWidget(self.grid_combo)
        layout.addLayout(grid_row)

        # Add grid combo box
        duration_row = QHBoxLayout()
        duration_label = QLabel("Duration:")
        # Create address combo box for Arpeggio Duration
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(arp_duration)  # Use arp_duration list
        self.duration_combo.currentIndexChanged.connect(self._on_duration_changed)
        duration_row.addWidget(duration_label)
        duration_row.addWidget(self.duration_combo)
        layout.addLayout(duration_row)

        # Add sliders
        self.velocity_slider = Slider("Velocity", 0, 127)
        self.velocity_slider.valueChanged.connect(self._on_velocity_changed)
        layout.addWidget(self.velocity_slider)

        self.accent_slider = Slider("Accent", 0, 127)
        self.accent_slider.valueChanged.connect(self._on_accent_changed)
        layout.addWidget(self.accent_slider)

        # Add octave range combo box
        octave_row = QHBoxLayout()
        octave_label = QLabel("Octave Range:")
        self.octave_combo = QComboBox()
        self.octave_combo.addItems([octave.display_name for octave in ArpOctaveRange])
        # Set default to 0
        self.octave_combo.setCurrentIndex(3)  # Index 3 is OCT_ZERO
        self.octave_combo.currentIndexChanged.connect(self._on_octave_changed)
        octave_row.addWidget(octave_label)
        octave_row.addWidget(self.octave_combo)
        layout.addLayout(octave_row)

        # Add motif combo box
        motif_row = QHBoxLayout()
        motif_label = QLabel("Motif:")
        self.motif_combo = QComboBox()
        self.motif_combo.addItems(
            [
                "UP/L",
                "UP/H",
                "UP/_",
                "dn/L",
                "dn/H",
                "dn/_",
                "Ud/L",
                "Ud/H",
                "Ud/_",
                "rn/L",
                "rn/_",
                "PHRASE",
            ]
        )
        self.motif_combo.currentIndexChanged.connect(self._on_motif_changed)
        motif_row.addWidget(motif_label)
        motif_row.addWidget(self.motif_combo)
        layout.addLayout(motif_row)

    def update_instrument_image(self):
        image_loaded = False

        def load_and_set_image(image_path):
            """Helper function to load and set the image on the label."""
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    150, Qt.TransformationMode.SmoothTransformation
                )  # Resize to 250px height
                self.image_label.setPixmap(scaled_pixmap)
                return True
            return False

        # Define paths
        default_image_path = os.path.join(
            "resources", "arpeggiator", "arpeggiator2.png"
        )

        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def _on_switch_changed(self, checked: bool):
        """Handle arpeggiator switch change"""
        if self.midi_helper:
            switch_address = ArpeggioParameter.SWITCH.value[0]
            switch_is_on = self.switch_button.isChecked()
            self.switch_button.setText("ON" if switch_is_on else "OFF")
            logging.debug(
                f"Sending arp switch change: area={TEMPORARY_PROGRAM:02x}, "
                f"part={ARP_PART:02x}, group={ARP_GROUP:02x}, "
                f"param={switch_address:02x}, value={switch_is_on}"
            )
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=switch_address,
                                        value=switch_is_on)
            self.midi_helper.send_midi_message(sysex_message)

    def _on_style_changed(self, index):
        """Handle changes to the Arpeggio Style."""
        self._send_parameter_change(ArpeggioParameter.STYLE, index)

    def _on_grid_changed(self, index):
        """Handle changes to the Arpeggio Grid."""
        self._send_parameter_change(ArpeggioParameter.GRID, index)

    def _on_duration_changed(self, index):
        """Handle changes to the Arpeggio Duration."""
        self._send_parameter_change(ArpeggioParameter.DURATION, index)

    def _on_pattern_changed(self, index):
        """Handle changes to the Pattern Type."""
        self._send_parameter_change(
            ArpeggioParameter.PATTERN_1, index
        )  # Replace with actual parameter if different

    def _on_velocity_changed(self, value):
        """Handle changes to the Velocity."""
        self._send_parameter_change(ArpeggioParameter.VELOCITY, value)

    def _on_accent_changed(self, value):
        """Handle changes to the Accent."""
        self._send_parameter_change(ArpeggioParameter.ACCENT_RATE, value)

    def _on_octave_changed(self, index: int):
        """Handle octave range change"""
        if self.midi_helper:
            param = ArpeggioParameter.OCTAVE.value[0]
            octave = index + 61  # Convert index to -3 to +3 range
            logging.info(f"octave value: {octave}")
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=ArpeggioParameter.OCTAVE.value[0],
                                        value=octave)
            self.midi_helper.send_midi_message(sysex_message)

    def _on_motif_changed(self, index):
        """Handle changes to the Motif."""
        self._send_parameter_change(ArpeggioParameter.MOTIF, index)

    def _send_parameter_change(self, param, value):
        """Send parameter change to MIDI device."""
        address, min_val, max_val = param.value
        if min_val <= value <= max_val:
            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=self.group,
                                        param=address,
                                        value=value)
            self.midi_helper.send_midi_message(sysex_message)
            logging.info(f"Parameter {param.name} changed to {value}")
        else:
            logging.info(f"Value {value} out of range for parameter {param.name}")
