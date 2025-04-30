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
import json
import re
import os
import logging
from typing import Optional, Any
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal

from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.control_change.base import ControlChange

from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.jdxi.preset.lists import JDXIPresets
from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXIPresetHelper
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.editors.helpers.program import (
    log_midi_info,
    get_preset_parameter_value,
)
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.style import JDXIStyle


def log_changes(previous_data, current_data):
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
        if change[0] not in ["JD_XI_HEADER", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"]
    ]

    if changes:
        # logging.info("Changes detected:")
        for key, prev, curr in changes:
            pass
            # logging.info(
            #     f"\n===> Changed Parameter: {key}, Previous: {prev}, Current: {curr}"
            # )
    else:
        pass
        #logging.info("No changes detected.")


class SynthEditor(SynthBase):
    """Base class for all editor windows"""

    parameter_received = Signal(list, int)  # address, value

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper, parent)
        self.sysex_current_data = None
        self.preset_list = None
        self.presets = None
        # self.midi_helper = midi_helper
        self.midi_helper = MidiIOHelper()
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.cc_parameters = dict()
        self.nrpn_parameters = dict()
        self.nrpn_map = dict()
        self.controls = list()
        self.bipolar_parameters = list()
        # Midi request for Temporary program
        self.midi_requests = list()
        self.instrument_default_image = None
        self.instrument_title_label = None
        self.instrument_image_label = None
        self.instrument_icon_folder = None
        self.partial_number = None
        self.midi_channel = None
        self.preset_helper = None
        self.instrument_selection_combo = None
        self.preset_type = None
        self.midi_helper.update_tone_name.connect(
            lambda title, synth_type: self.set_instrument_title_label(title, synth_type))
        self.midi_helper.midi_program_changed.connect(self.data_request)
        log_parameter("Initialized:", self.__class__.__name__)
        log_parameter("---> Using MIDI helper:", midi_helper)
        # midi message bytes
        # To be over-ridden by subclasses
        self.address_msb = None
        """ One of:
            PROGRAM_AREA, 
            ANALOG_SYNTH_AREA, 
            DIGITAL_SYNTH_1_AREA, 
            DIGITAL_SYNTH_2_AREA, 
            ANALOG_SYNTH_AREA, 
            DRUM_KIT_AREA
        """
        self.address_umb = None
        self.address_lmb = None
        # Set window flags for address tool window
        self.setWindowFlags(Qt.WindowType.Tool)

        # Apply common style
        self.setStyleSheet(JDXIStyle.EDITOR)

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
            # self.midi_helper.midi_control_changed.connect(self._handle_control_change)
            logging.info("MIDI helper initialized")
        else:
            logging.error("MIDI helper not initialized")
        self.preset_loader = JDXIPresetHelper(self.midi_helper, JDXIPresets.DIGITAL_ENUMERATED)
        # self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Initialize preset handlers dynamically
        preset_configs = [
            (JDXISynth.DIGITAL_1, JDXIPresets.DIGITAL_ENUMERATED, MidiChannel.DIGITAL1),
            (JDXISynth.DIGITAL_2, JDXIPresets.DIGITAL_ENUMERATED, MidiChannel.DIGITAL2),
            (JDXISynth.ANALOG, JDXIPresets.ANALOG_ENUMERATED, MidiChannel.ANALOG),
            (JDXISynth.DRUM, JDXIPresets.DRUM_ENUMERATED, MidiChannel.DRUM),
        ]

        self.preset_helpers = {
            synth_type: JDXIPresetHelper(
                self.midi_helper, presets, channel=channel, preset_type=synth_type
            )
            for synth_type, presets, channel in preset_configs
        }

    def _init_synth_data(self, synth_type: JDXISynth = JDXISynth.DIGITAL_1,
                         partial_number: Optional[int] = 0):
        """Initialize synth-specific data."""
        from jdxi_editor.jdxi.synth.factory import create_synth_data
        self.synth_data = create_synth_data(synth_type,
                                            partial_number=partial_number)

        # Dynamically assign attributes
        for attr in [
            "sysex_address",
            "preset_type",
            "instrument_default_image",
            "instrument_icon_folder",
            "presets",
            "preset_list",
            "midi_requests",
            "midi_channel",
        ]:
            setattr(self, attr, getattr(self.synth_data, attr))
        
    def get_controls_as_dict(self):
        """
        Get the current values of self.controls as a dictionary.

        Returns:
            dict: A dictionary of control parameter names and their values.
        """
        try:
            controls_data = {}

            for param in self.controls:
                controls_data[param.name] = param.value
            logging.info(controls_data)
            return controls_data

        except Exception as ex:
            logging.info(f"Failed to get controls: {ex}")
            return {}

    def _get_preset_helper_for_current_synth(self):
        """Return the appropriate preset handler based on the current synth preset_type."""
        handler = self.preset_helpers.get(self.preset_type)
        if handler is None:
            logging.warning(
                f"Unknown synth preset_type: {self.preset_type}, defaulting to digital_1"
            )
            return self.preset_helpers[JDXISynth.DIGITAL_1]  # Safe fallback
        return handler

    def _on_parameter_received(self, address, value):
        raise NotImplementedError("Should be implemented by subclass")

    def _dispatch_sysex_to_area(self, json_sysex_data: str):
        raise NotImplementedError

    def _parse_sysex_json(self, json_sysex_data: str) -> dict:
        try:
            data = json.loads(json_sysex_data)
            self.sysex_previous_data = self.sysex_current_data
            self.sysex_current_data = data
            log_changes(self.sysex_previous_data, data)
            return data
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return None

    def set_instrument_title_label(self, name: str, synth_type: str):
        if self.preset_type == synth_type:
            self.instrument_title_label.setText(name)

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        logging.info(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        logging.info(f"selected_synth_text: {selected_synth_text}")
        self.instrument_title_label.setText(selected_synth_text)

    def update_instrument_preset(self, text):
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

    def load_preset(self, preset_index):
        """Load a preset by program change."""
        preset_name = (
            self.instrument_selection_combo.combo_box.currentText()
        )  # Get the selected preset name
        logging.info(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        logging.info(f"combo box program_number : {program_number}")

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number, self.preset_list)
        lsb = get_preset_parameter_value("lsb", program_number, self.preset_list)
        pc = get_preset_parameter_value("pc", program_number, self.preset_list)

        if None in [msb, lsb, pc]:
            logging.error(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return

        logging.info(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1,  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def _handle_program_change(self, channel: int, program: int):
        """Handle program change messages by requesting updated data"""
        logging.info(
            f"Program change {program} detected on channel {channel}, requesting data update"
        )
        self.data_request(channel, program)

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

    def send_control_change(self, control_change: ControlChange, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
            # Convert enum to int if needed
            control_change_number = (
                control_change.value
                if isinstance(control_change, ControlChange)
                else control_change
            )
            self.midi_helper.send_control_change(
                control_change_number, value, self.midi_channel
            )

    def load_and_set_image(self, image_path, secondary_image_path=None):
        """Helper function to load and set the image on the label."""
        file_to_load = ""
        if os.path.exists(image_path):
            file_to_load = image_path
        elif os.path.exists(secondary_image_path):
            file_to_load = secondary_image_path
        else:
            file_to_load = os.path.join(
                "resources",
                self.instrument_icon_folder,
                self.instrument_default_image,
            )
        pixmap = QPixmap(file_to_load)
        scaled_pixmap = pixmap.scaledToHeight(
            160, Qt.TransformationMode.SmoothTransformation
        )  # Resize to 250px height
        self.instrument_image_label.setPixmap(scaled_pixmap)
        self.instrument_image_label.setScaledContents(True)
        self.instrument_image_label.setStyleSheet(
            """
            QLabel {
                    height: 150px;
                    background-color: transparent;
                    border: none;
                }
            """
        )
        return True

    def update_instrument_image(self):
        """Update the instrument image based on the selected synth."""
        default_image_path = resource_path(os.path.join(
            "resources", self.instrument_icon_folder, self.instrument_default_image
        ))
        selected_instrument_text = (
            self.instrument_selection_combo.combo_box.currentText()
        )
        log_parameter("Selected instrument text:", selected_instrument_text)
        # Try to extract synth name from the selected text
        image_loaded = False
        if instrument_matches := re.search(
            r"(\d{3}) - (\S+)\s(\S+)+", selected_instrument_text, re.IGNORECASE
        ):
            selected_instrument_name = (
                instrument_matches.group(2).lower().replace("&", "_").split("_")[0]
            )
            log_parameter(f"selected instrument name:", selected_instrument_name)
            selected_instrument_type = (
                instrument_matches.group(3).lower().replace("&", "_").split("_")[0]
            )
            log_parameter("Selected instrument type:", selected_instrument_type)
            specific_image_path = resource_path(os.path.join(
                "resources",
                self.instrument_icon_folder,
                f"{selected_instrument_name}.png",
            ))
            generic_image_path = resource_path(os.path.join(
                "resources",
                self.instrument_icon_folder,
                f"{selected_instrument_type}.png",
            ))
            image_loaded = self.load_and_set_image(specific_image_path, generic_image_path)

        # Fallback to default image if no specific image is found
        if not image_loaded:
            if not self.load_and_set_image(default_image_path):
                self.instrument_image_label.clear()  # Clear label if default image is also missing

    def _update_slider(self,
                       param: AddressParameter,
                       value: int,
                       successes: list = None,
                       failures: list = None,
                       debug: bool = False):
        """Safely update sliders from NRPN messages."""
        slider = self.controls.get(param)
        if slider:
            slider_value = param.convert_from_midi(value)
            logging.info(f"Updating {param.name}: MIDI {value} -> Slider {slider_value}")
            slider.blockSignals(True)
            slider.setValue(slider_value)
            slider.blockSignals(False)
            logging.info(f"Updated {param.name} slider to {slider_value}")

    def send_analog_synth_parameter(
        self, parameter: str, value: int, channel: int = 0
    ) -> bool:
        """
        Send a MIDI Control Change or NRPN message for an Analog Synth parameter.

        Args:
            parameter: The name of the parameter to modify.
            value: The parameter value (0-127).
            channel: The MIDI channel (0-15).

        Returns:
            True if successful, False otherwise.
        """

        if parameter in self.cc_parameters:
            # Send as a Control Change (CC) message
            controller = self.cc_parameters[parameter]
            return self.midi_helper.send_control_change(controller, value, channel)

        elif parameter in self.nrpn_parameters:
            # Send as an NRPN message
            msb, lsb = self.nrpn_parameters[parameter]
            return self.midi_helper.send_nrpn((msb << 7) | lsb, value, channel)

        else:
            logging.error(f"Invalid Analog Synth parameter: {parameter}")
            return False

    def _handle_nrpn_message(self, nrpn_address: int, value: int, channel: int):
        """Process incoming NRPN messages and update UI controls."""
        logging.info(
            f"Received NRPN {nrpn_address} with value {value} on channel {channel}"
        )

        # Find matching parameter
        msb = nrpn_address >> 7
        lsb = nrpn_address & 0x7F
        param_name = self.nrpn_map.get((msb, lsb))

        if param_name:
            # Update slider or control
            param = AddressParameter.get_by_name(
                param_name
            )  # FIXME: make generic or subclass
            if param:
                self._update_slider(param, value)
        else:
            logging.warning(f"Unrecognized NRPN {nrpn_address}")

    def _handle_control_change(self, channel, control, value) -> None:  # @@
        """
        Handle Control Change (CC) MIDI messages.

        :param message: The MIDI Control Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        try:
            logging.info(
                f"Control change {control} detected on channel {channel}, value {value} "
                f"requesting data update"
            )
            self.data_request()
            logging.info(
                "Control Change - Channel: %d, Control: %d, Value: %d",
                channel,
                control,
                value,
            )
            if control == 99:  # NRPN MSB
                self.nrpn_msb = value
            elif control == 98:  # NRPN LSB
                self.nrpn_lsb = value
            elif (
                control == 6 and self.nrpn_msb is not None and self.nrpn_lsb is not None
            ):
                # We have both MSB and LSB; reconstruct NRPN address
                nrpn_address = (self.nrpn_msb << 7) | self.nrpn_lsb
                self._handle_nrpn_message(nrpn_address, value, channel)

                # Reset NRPN state
                self.nrpn_msb = None
                self.nrpn_lsb = None
            if control == 0:
                self.cc_msb_value = value
            elif control == 32:
                self.cc_lsb_value = value
        except Exception as ex:
            logging.info(f"Error {ex} occurred handling control change")
