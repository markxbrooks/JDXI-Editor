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

from jdxi_manager.midi.data.parameter.digital import DigitalParameter
from jdxi_manager.midi.data.parameter.drums import DrumCommonParameter
from jdxi_manager.midi.data.parameter.synth import SynthParameter
from jdxi_manager.midi.data.presets.digital import DIGITAL_PRESETS_ENUMERATED
from jdxi_manager.midi.data.presets.type import PresetType
from jdxi_manager.midi.data.constants import MIDI_CHANNEL_DIGITAL1
from jdxi_manager.midi.io.helper import MIDIHelper
from jdxi_manager.midi.message.roland import RolandSysEx
from jdxi_manager.midi.preset.handler import PresetHandler
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.spin_box.spin_box import SpinBox
from jdxi_manager.ui.widgets.switch.switch import Switch


class SynthEditor(QWidget):
    """Base class for all editor windows"""

    parameter_received = Signal(list, int)  # address, value

    def __init__(
        self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.four_byte_params = []
        self.instrument_icon_folder = None
        self.controls = {}
        self.partial_num = None
        self.midi_channel = None
        self.preset_handler = None
        self.instrument_selection_combo = None
        self.preset_type = None
        self.preset_loader = None
        self.midi_helper = midi_helper
        self.bipolar_parameters = []
        self.midi_requests = []  # Initialize empty list of MIDI requests
        logging.debug(
            f"Initialized {self.__class__.__name__} with MIDI helper: {midi_helper}"
        )
        # midi message bytes
        # To be over-ridden by subclasses
        self.area = None
        """ 
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
        self.setMinimumSize(800, 400)

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

    def _create_parameter_combo_box(
        self,
        param: SynthParameter,
        label: str = None,
        options: list = None,
        values: list = None,
        show_label = True
    ) -> ComboBox:
        """Create a combo box for a parameter with proper display conversion"""
        combo_box = ComboBox(label, options, values, show_label=show_label)
        combo_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = combo_box
        return combo_box

    def _create_parameter_spin_box(
        self, param: SynthParameter, label: str = None
    ) -> SpinBox:
        """Create address spin box for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        spin_box = SpinBox(label, display_min, display_max)

        # Connect value changed signal
        spin_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = spin_box
        return spin_box
    
    def _create_parameter_switch(
        self,
        param: SynthParameter,
        label: str,
        values: list[str],
    ) -> Switch:
        """Create address switch for address parameter with proper display conversion"""
        switch = Switch(label, values)
        switch.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = switch
        return switch

    def _create_parameter_slider(
        self,
        param: SynthParameter,
        label: str,
        vertical=False,
        show_value_label=True,
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create slider
        slider = Slider(label, display_min, display_max, vertical, show_value_label)

        # Set up bipolar parameters
        if param in self.bipolar_parameters:
            # Set format string to show + sign for positive values
            slider.setValueDisplayFormat(lambda v: f"{v:+d}" if v != 0 else "0")
            # Set center tick
            slider.setCenterMark(0)
            # Add more prominent tick at center
            slider.setTickPosition(Slider.TickPosition.TicksBothSides)
            slider.setTickInterval((display_max - display_min) // 4)

            # Get initial MIDI value and convert to display value
            if self.midi_helper:
                group, _ = param.get_address_for_partial(self.partial_num)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def set_midi_helper(self, midi_helper: MIDIHelper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper

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
        """ tart up ui with image """
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
        preset_data = {
            "preset_type": self.preset_type,  # Ensure this is address valid preset_type
            "selpreset": preset_index,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
            "channel": self.midi_channel,
        }
        if not self.preset_handler:
            self.preset_handler = PresetHandler(
                self.midi_helper,
                DIGITAL_PRESETS_ENUMERATED,
                channel=MIDI_CHANNEL_DIGITAL1,
                preset_type=PresetType.DIGITAL_1,
            )
        if self.preset_handler:
            self.preset_handler.load_preset(preset_data)

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter area and address with partial offset
            if isinstance(param, DigitalParameter):
                if hasattr(param, "get_address_for_partial"):
                    group, _ = param.get_address_for_partial(self.partial_num)
                else:
                    group = 0x00  # Common parameters area
            else:
                group = 0x00  # Common parameters area

            # Ensure value is included in the MIDI message

            sysex_message = RolandSysEx(area=self.area,
                                        section=self.part,
                                        group=group,
                                        param=param.address,
                                        value=value)
            return_value = self.midi_helper.send_midi_message(sysex_message)
            """
            return self.midi_helper.send_parameter(
                area=self.area,
                part=self.part,
                group=group,
                param=param.address,
                value=value,  # Make sure this value is being sent
            )
            """
            return return_value
        except Exception as ex:
            logging.error(f"MIDI error setting {param}: {str(ex)}")
            return False

    def _on_parameter_changed(self, param: SynthParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Get parameter area and address with partial offset
            if param in [DrumCommonParameter.KIT_LEVEL]:
                group = param.get_address_for_partial()
            elif isinstance(param, DigitalParameter):
                if hasattr(param, "get_address_for_partial"):
                    group, _ = param.get_address_for_partial(self.partial_num)
                else:
                    group = self.group
            else:
                group = self.group
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            elif hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(display_value)
            else:
                midi_value = param.validate_value(display_value)
            if param in self.four_byte_params:
                size = 4
            else:
                size = 1
            logging.info(f"parameter from widget midi_value: {midi_value}")
            # Send MIDI message
            logging.debug(
                f"Sending: area={self.area:02x}, address={self.part:02x}, "
                f"group={group:02x}, param={param.address:02x}, "
                f"display_value={display_value:02x},  value={midi_value:02x}"
            )
            try:
                sysex_message = RolandSysEx(area=self.area,
                                            section=self.part,
                                            group=group,
                                            param=param.address,
                                            value=midi_value)
                self.midi_helper.send_midi_message(sysex_message)
                """
                # Ensure value is included in the MIDI message
                return self.midi_helper.send_parameter(
                    area=self.area,
                    part=self.part,
                    group=group,
                    param=param.address,
                    value=midi_value,
                    size=size,
                )"""
            except Exception as ex:
                logging.error(f"MIDI error setting {param}: {str(ex)}")
                return False

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")

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
            self.midi_helper.send_raw_message(message)
        else:
            logging.error("MIDI helper not initialized")

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
