"""
synth_editor.py

This module defines the `SynthEditor` class, a base class for all editor windows in the JD-Xi Manager application.
It provides an interface for editing synthesizer parameters, handling MIDI messages, and updating UI components.

Key Features:
- UI Elements: Uses PySide6 widgets, including ComboBoxes, Sliders, and SpinBoxes, to adjust synthesizer parameters.
- MIDI Integration: Sends and receives MIDI messages via `MIDIHelper`, supporting parameter changes, SysEx communication,
  and program change handling.
- Preset Management: Loads, updates, and applies instrument presets with `PresetHandler` and `PresetLoader`.
- Parameter Control: Dynamically creates UI controls for synthesizer parameters, supporting bipolar values and display conversion.
- Shortcuts: Implements keyboard shortcuts for refreshing data and closing the window.

Dependencies:
- PySide6 for the UI components.
- `jdxi_manager.midi` for MIDI communication.
- `jdxi_manager.midi.data.parameter` for synthesizer parameter handling.
- `jdxi_manager.ui.style` for applying UI styles.

"""

import re
import os
import logging
from typing import Optional
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal

from jdxi_editor.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DIGITAL1
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.preset.data import ToneData
from jdxi_editor.midi.preset.handler import PresetHandler
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.style import Style


class SynthEditor(SynthBase):
    """Base class for all editor windows"""

    parameter_received = Signal(list, int)  # address, value

    def __init__(
        self, midi_helper: Optional[MidiIOHelper] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(midi_helper, parent)
        self.instrument_title_label = None
        self.image_label = None
        self.instrument_icon_folder = None
        self.controls = {}
        self.partial_num = None
        self.midi_channel = None
        self.preset_handler = None
        self.instrument_selection_combo = None
        self.preset_type = None
        self.midi_helper = midi_helper
        self.bipolar_parameters = []
        # Midi request for Temporary program
        self.midi_requests = []
        logging.debug(
            f"Initialized {self.__class__.__name__} with MIDI helper: {midi_helper}"
        )
        # midi message bytes
        # To be over-ridden by subclasses
        self.area = None
        """ One of:
            PROGRAM_AREA, 
            ANALOG_SYNTH_AREA, 
            DIGITAL_SYNTH_1_AREA, 
            DIGITAL_SYNTH_2_AREA, 
            ANALOG_SYNTH_AREA, 
            DRUM_KIT_AREA
        """
        self.part = None  #
        self.group = None  # ANALOG_OSC_GROUP
        # Set window flags for address tool window
        self.setWindowFlags(Qt.WindowType.Tool)

        # Apply common style
        self.setStyleSheet(Style.JDXI_EDITOR)

        # Add keyboard shortcuts
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        # Add close window shortcut
        self.close_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
        self.close_shortcut.activated.connect(self.close)

        # Common minimum size for all editors
        self.setMinimumSize(400, 400)

        # Connect to program change signal if MIDI helper exists
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            logging.info("MIDI helper initialized")
            # register callback
            if hasattr(self.midi_helper, "set_callback"):
                self.midi_helper.set_callback(self.midi_helper.midi_callback)
                logging.info("MIDI callback set")

            else:
                logging.error("MIDI set_callback method not found")
        else:
            logging.error("MIDI helper not initialized")
        self.preset_loader = PresetHandler(self.midi_helper, DIGITAL_PRESETS_ENUMERATED)
        # self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)

    def _dispatch_sysex_to_area(self):
        raise NotImplementedError

    def set_instrument_title_label(self, name: str):
        self.instrument_title_label.setText(f"Synth:\n {name}")

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        logging.info(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        logging.info(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(f"Analog Synth:\n {selected_synth_text}")

    def update_instrument_preset(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        if synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_synth_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            one_based_preset_index = int(selected_synth_padded_number)
            logging.info(f"preset_index: {one_based_preset_index}")
            self.load_preset(one_based_preset_index - 1)  # use 0-based index

    def update_instrument_image(self):
        """tart up ui with image"""
        class_name = self.__class__.__name__.lower()  # Get class name in lowercase
        default_image_path = os.path.join("resources", class_name, f"{class_name}.png")

        def load_and_set_image(image_path, secondary_image_path=None):
            """Helper function to load and set the image on the label."""
            file_to_load = ""

            if os.path.exists(image_path):
                file_to_load = image_path
            elif os.path.exists(secondary_image_path):
                file_to_load = secondary_image_path
            else:
                file_to_load = os.path.join(
                    "resources", self.instrument_icon_folder, "analog.png"
                )
            pixmap = QPixmap(file_to_load)
            scaled_pixmap = pixmap.scaledToHeight(
                250, Qt.TransformationMode.SmoothTransformation
            )  # Resize to 250px height
            self.image_label.setPixmap(scaled_pixmap)
            return True

        selected_instrument_text = (
            self.instrument_selection_combo.combo_box.currentText()
        )

        # Try to extract synth name from the selected text
        image_loaded = False
        if instrument_matches := re.search(
            r"(\d{3}): (\S+)\s(\S+)+", selected_instrument_text, re.IGNORECASE
        ):
            selected_instrument_name = (
                instrument_matches.group(2).lower().replace("&", "_").split("_")[0]
            )
            selected_instrument_type = (
                instrument_matches.group(3).lower().replace("&", "_").split("_")[0]
            )
            logging.info(f"selected_instrument_type: {selected_instrument_type}")
            specific_image_path = os.path.join(
                "resources",
                self.instrument_icon_folder,
                f"{selected_instrument_name}.png",
            )
            generic_image_path = os.path.join(
                "resources",
                self.instrument_icon_folder,
                f"{selected_instrument_type}.png",
            )
            image_loaded = load_and_set_image(specific_image_path, generic_image_path)

        # Fallback to default image if no specific image is found
        if not image_loaded:
            if not load_and_set_image(default_image_path):
                self.image_label.clear()  # Clear label if default image is also missing

    def load_preset(self, preset_index):
        """Load address preset by index"""
        preset_data = ToneData(
            type=self.preset_type,  # Ensure this is address valid preset_type
            current_selection=preset_index,  # Convert to 1-based index
            modified=0,  # or 1, depending on your logic
            channel=self.midi_channel,
        )
        if not self.preset_handler:
            self.preset_handler = PresetHandler(
                self.midi_helper,
                DIGITAL_PRESETS_ENUMERATED,
                channel=MIDI_CHANNEL_DIGITAL1,
                preset_type=SynthType.DIGITAL_1,
            )
        if self.preset_handler:
            self.preset_handler.load_preset(preset_data)

    def _handle_program_change(self, channel: int, program: int):
        """Handle program change messages by requesting updated data"""
        logging.info(
            f"Program change {program} detected on channel {channel}, requesting data update"
        )
        self.data_request()
        if hasattr(self, "address") and channel == self.midi_channel:
            self.data_request()

    def _handle_control_change(self, channel: int, control: int, value: int):
        """Handle program change messages by requesting updated data"""
        logging.info(
            f"Control change {control} detected on channel {channel}, value {value} requesting data update"
        )
        self.data_request()
        if hasattr(self, "address") and channel == self.midi_channel:
            self.data_request()

    def _handle_dt1_message(self, data):
        """Handle Data Set 1 (DT1) messages

        Format: aa bb cc dd ... where:
        aa bb cc = Address
        dd ... = Data
        """
        if len(data) < 4:  # Need at least address and one data byte
            return

        address = data[0:3]
        logging.info(f"DT1 message Address: {address}")
        value = data[3]
        logging.info(f"DT1 message Value: {value}")
        # Emit signal with parameter data
        self.parameter_received.emit(address, value)

    def _log_changes(self, previous_data, current_data):
        """Log changes between previous and current JSON data."""
        changes = []
        if not current_data or not previous_data:
            return
        for key, current_value in current_data.items():
            previous_value = previous_data.get(key)
            if previous_value != current_value:
                changes.append((key, previous_value, current_value))

        changes = [
            change
            for change in changes
            if change[0]
            not in ["JD_XI_HEADER", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"]
        ]

        if changes:
            logging.info("Changes detected:")
            for key, prev, curr in changes:
                logging.info(
                    f"\n===> Changed Parameter: {key}, Previous: {prev}, Current: {curr}"
                )
        else:
            logging.info("No changes detected.")
