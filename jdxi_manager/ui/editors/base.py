import re
import os
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional, Union
import logging

from jdxi_manager.data.analog import AnalogCommonParameter
from jdxi_manager.midi.constants import DIGITAL_1_PART, AnalogParameter
from jdxi_manager.midi.utils.conversions import midi_cc_to_frac, midi_cc_to_ms
from jdxi_manager.midi.io.helper import MIDIHelper
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.slider import Slider


class BaseEditor(QWidget):
    """Base class for all editor windows"""

    def __init__(
        self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.midi_requests = []  # Initialize empty list of MIDI requests
        logging.debug(
            f"Initialized {self.__class__.__name__} with MIDI helper: {midi_helper}"
        )

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
        self.setMinimumSize(800, 400)

        # Register the callback for incoming MIDI messages
        # if self.midi_helper and hasattr(self.midi_helper, "set_callback"):
        #    self.midi_helper.set_callback(self.handle_midi_message)
        # else:
        #    logging.error(
        #        "MIDI helper not initialized or set_callback method not found"
        #    )

        # Connect to program change signal if MIDI helper exists
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)

    def set_midi_helper(self, midi_helper: MIDIHelper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper

    def handle_midi_message(self, message: bytes):
        """Handle incoming MIDI message"""
        logging.debug(f"Received MIDI message: {message}")
        # Implement in subclass

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
            preset_index = int(selected_synth_padded_number)
            logging.info(f"preset_index: {preset_index}")
            self.load_preset(preset_index)

    def update_instrument_image(self):
        def load_and_set_image(image_path, secondary_image_path):
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
        preset_data = {
            "type": self.preset_type,  # Ensure this is address valid type
            "selpreset": preset_index,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        if not self.preset_loader:
            self.preset_loader = PresetLoader(self.midi_helper)
        if self.preset_loader:
            self.preset_loader.load_preset(preset_data)

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter group and address with partial offset
            # if isinstance(param, AnalogParameter):
            #    group, param_address = param.get_address_for_partial(self.partial_name)
            # else:
            group = ANALOG_OSC_GROUP  # Common parameters group
            param_address = param.format_address

            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=self.part,
                group=group,
                param=param_address,
                value=value,  # Make sure this value is being sent
            )
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def _on_parameter_changed(
        self, param: Union[AnalogParameter, AnalogCommonParameter], display_value: int
    ):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)

            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def data_request(self):
        """Send data request SysEx messages to the JD-Xi"""
        # Define SysEx messages as byte arrays
        for request in self.midi_requests:
            request = bytes.fromhex(request)
            # Send each SysEx message
            self.send_message(request)

    def send_message(self, message):
        """Send address SysEx message using the MIDI helper"""
        if self.midi_helper:
            self.midi_helper.send_message(message)
        else:
            logging.error("MIDI helper not initialized")

    def _handle_program_change(self, channel: int, program: int):
        """Handle program change messages by requesting updated data"""
        logging.info(f"Program change detected on channel {channel}, requesting data update")
        self.data_request()
        #if hasattr(self, 'address') and channel == self.address:
        #    logging.info(f"Program change detected on channel {channel}, requesting data update")
        #    self.data_request()
