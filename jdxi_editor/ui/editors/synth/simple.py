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
    .. code-block:: python

        from PySide6.QtWidgets import QApplication
        from midi_helper import MIDIHelper

        app = QApplication([])
        midi_helper = MIDIHelper()
        editor = ArpeggioEditor(midi_helper=midi_helper)
        editor.show()
        app.exec()

Dependencies:
    - PySide6 (for UI components)
    - MIDIHelper (for MIDI communication)
    - ArpeggioParameter (for managing parameter addresses and value ranges)
    - Slider (for smooth control over numerical parameters)

"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.address.address_map import address
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.editors.synth.editor import SynthEditor


class BasicEditor(SynthEditor):
    """Simple Editor Window with small instrument image"""

    def __init__(
        self,
        midi_helper: MidiIOHelper,
        parent: QWidget = None,
        address: JDXiSysExAddress = None,
    ):
        super().__init__(midi_helper=midi_helper, parent=parent, address=address)
        self.default_image = None
        self.preset_image_label = None
        self.setMinimumWidth(JDXi.UI.Dimensions.EDITOR_BASIC.WIDTH)
        self.setMinimumHeight(JDXi.UI.Dimensions.EDITOR_BASIC.HEIGHT)

    def load_and_set_image(self, image_path: str, secondary_image_path: str = None):
        """Helper function to load and set the image on the label."""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaledToHeight(
                JDXi.UI.Dimensions.EDITOR_BASIC.IMAGE_HEIGHT,
                Qt.TransformationMode.SmoothTransformation,
            )  # Resize to 150px height
            # Only set pixmap if preset_image_label exists (some editors may not use it)
            if self.preset_image_label is not None:
                self.preset_image_label.setPixmap(scaled_pixmap)
            return True
        return False

    def update_instrument_image(self):
        image_loaded = False

        # Define paths
        default_image_path = resource_path(
            os.path.join("resources", self.instrument_icon_folder, self.default_image)
        )
        if not image_loaded:
            if not self.load_and_set_image(default_image_path):
                # Only clear if preset_image_label exists (some editors may not use it)
                if self.preset_image_label is not None:
                    self.preset_image_label.clear()  # Clear label if default image is also missing
