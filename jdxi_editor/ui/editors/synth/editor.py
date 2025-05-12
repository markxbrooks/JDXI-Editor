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
from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

from jdxi_editor.log.debug_info import log_debug_info
from jdxi_editor.log.error import log_error
from jdxi_editor.log.header import log_header_message
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB, AddressOffsetTemporaryToneUMB
from jdxi_editor.midi.data.control_change.base import ControlChange

from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.jdxi.preset.lists import JDXiPresets
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.midi.sysex.parsers.json import JDXiJsonSysexParser
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.editors.digital.utils import get_area, filter_sysex_keys, get_partial_number, log_synth_area_info
from jdxi_editor.midi.sysex.request.data import SYNTH_PARTIAL_MAP
from jdxi_editor.ui.editors.helpers.program import (
    log_midi_info,
    get_preset_parameter_value,
)
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox


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
        # log_message("Changes detected:")
        for key, prev, curr in changes:
            pass
            # log_message(
            #     f"\n===> Changed Parameter: {key}, Previous: {prev}, Current: {curr}"
            # )
    else:
        pass
        #log_message("No changes detected.")


class SynthEditor(SynthBase):
    """Base class for all editor windows"""

    parameter_received = Signal(list, int)  # address, value

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper, parent)
        self.partial_map = SYNTH_PARTIAL_MAP
        self.sysex_current_data = None
        self.preset_list = None
        self.presets = None
        # self.midi_helper = midi_helper
        self.midi_helper = MidiIOHelper()
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.midi_helper.midi_control_changed.connect(self._handle_control_change)
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
        self.setStyleSheet(JDXiStyle.EDITOR)

        # Add keyboard shortcuts
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        # Add close window shortcut
        self.close_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
        self.close_shortcut.activated.connect(self.close)

        # Common minimum size for all editors
        self.setMinimumSize(200, 200)

        # Connect to program change signal if MIDI helper exists
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_control_changed.connect(self._handle_control_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            self.preset_loader = JDXiPresetHelper(self.midi_helper, JDXiPresets.DIGITAL_ENUMERATED)
            # Initialize preset handlers dynamically
            preset_configs = [
                (JDXiSynth.DIGITAL_1, JDXiPresets.DIGITAL_ENUMERATED, MidiChannel.DIGITAL1),
                (JDXiSynth.DIGITAL_2, JDXiPresets.DIGITAL_ENUMERATED, MidiChannel.DIGITAL2),
                (JDXiSynth.ANALOG, JDXiPresets.ANALOG_ENUMERATED, MidiChannel.ANALOG),
                (JDXiSynth.DRUM, JDXiPresets.DRUM_ENUMERATED, MidiChannel.DRUM),
            ]
            self.preset_helpers = {
                synth_type: JDXiPresetHelper(
                    self.midi_helper, presets, channel=channel, preset_type=synth_type
                )
                for synth_type, presets, channel in preset_configs
            }
            log_message("MIDI helper initialized")
        else:
            log_message("MIDI helper not initialized")
        self.json_parser = JDXiJsonSysexParser()

    def _init_synth_data(self, synth_type: JDXiSynth = JDXiSynth.DIGITAL_1,
                         partial_number: Optional[int] = 0):
        """Initialize synth-specific data."""
        from jdxi_editor.jdxi.synth.factory import create_synth_data
        self.synth_data = create_synth_data(synth_type,
                                            partial_number=partial_number)

        # Dynamically assign attributes
        for attr in [
            "address",
            "preset_type",
            "instrument_default_image",
            "instrument_icon_folder",
            "presets",
            "preset_list",
            "midi_requests",
            "midi_channel",
        ]:
            setattr(self, attr, getattr(self.synth_data, attr))

    def _create_instrument_image_group(self):
        # Image group
        self.instrument_image_group = QGroupBox()
        instrument_group_layout = QVBoxLayout()
        self.instrument_image_group.setLayout(instrument_group_layout)
        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instrument_group_layout.addWidget(self.instrument_image_label)
        self.instrument_image_group.setStyleSheet(JDXiStyle.INSTRUMENT_IMAGE_LABEL)
        self.instrument_image_group.setMinimumWidth(350)

    def _create_instrument_preset_group(self, synth_type: str = "Analog") -> QGroupBox:
        """
        Create the instrument preset group box.
        :param synth_type: str
        :return: QGroupBox
        """
        instrument_preset_group = QGroupBox(f"{synth_type} Synth")
        instrument_title_group_layout = QVBoxLayout(instrument_preset_group)
        self.instrument_title_label = DigitalTitle()
        instrument_title_group_layout.addWidget(self.instrument_title_label)
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)
        self.instrument_selection_label = QLabel(f"Select a {synth_type} synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        self.instrument_selection_combo = PresetComboBox(self.preset_list)
        if synth_type == "Analog":
            self.instrument_selection_combo.setStyleSheet(JDXiStyle.COMBO_BOX_ANALOG)
        else:
            self.instrument_selection_combo.setStyleSheet(JDXiStyle.COMBO_BOX)
        self.instrument_selection_combo.combo_box.setEditable(True)
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)
        instrument_title_group_layout.addWidget(self.instrument_selection_combo)
        return instrument_preset_group
        
    def get_controls_as_dict(self):
        """
        Get the current values of self.controls as a dictionary.
        :returns: dict A dictionary of control parameter names and their values.
        """
        try:
            controls_data = {}

            for param in self.controls:
                controls_data[param.name] = param.value
            log_message(f"{controls_data}")
            return controls_data

        except Exception as ex:
            log_message(f"Failed to get controls: {ex}")
            return {}

    def _get_preset_helper_for_current_synth(self):
        """Return the appropriate preset handler based on the current synth preset_type."""
        handler = self.preset_helpers.get(self.preset_type)
        if handler is None:
            logging.warning(
                f"Unknown synth preset_type: {self.preset_type}, defaulting to digital_1"
            )
            return self.preset_helpers[JDXiSynth.DIGITAL_1]  # Safe fallback
        return handler

    def _on_parameter_received(self, address, value):
        raise NotImplementedError("Should be implemented by subclass")

    def _dispatch_sysex_to_area(self, json_sysex_data: str) -> None:
        """
        Dispatch SysEx data to the appropriate area for processing.
        :param json_sysex_data:
        :return: None
        """
        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return
        current_synth = get_area([self.address.msb, self.address.umb])
        temporary_area = sysex_data.get("TEMPORARY_AREA")
        synth_tone = sysex_data.get("SYNTH_TONE")
        if not current_synth == temporary_area:
            log_message(
                f"temp_area: {temporary_area} is not current_synth: {current_synth}, Skipping update"
            )
            return
        log_header_message(
            f"Updating UI components from SysEx data for \t{temporary_area} \t{synth_tone}"
        )

        # Analog is simple so deal with the 1st
        if temporary_area == AddressOffsetTemporaryToneUMB.ANALOG_PART.name:
            self._update_sliders_from_sysex(json_sysex_data)
        elif synth_tone in ["TONE_COMMON", "TONE_MODIFY"]:
            self._update_common_sliders_from_sysex(json_sysex_data)
        else:  # Drums and Digital 1 & 2 are dealt with via partials
            incoming_data_partial_no = get_partial_number(synth_tone, self.partial_map)
            filtered_data = filter_sysex_keys(sysex_data)
            self._apply_partial_ui_updates(incoming_data_partial_no, filtered_data)

    def _update_common_sliders_from_sysex(
        self, json_sysex_data: str
    ) -> None:
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        :return: None
        """
        successes, failures = [], []
        sysex_data = self._parse_sysex_json(json_sysex_data)
        log_synth_area_info(sysex_data)
        synth_tone = sysex_data.get("SYNTH_TONE")
        filtered_data = filter_sysex_keys(sysex_data)
        if synth_tone in ["TONE_COMMON", "TONE_MODIFY"]:
            self._update_common_controls(filtered_data, successes, failures)
        log_debug_info(filtered_data, successes, failures)

    def _update_sliders_from_sysex(self, json_sysex_data: str) -> None:
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        :return: None
        """
        sysex_data = self._parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return
        current_synth = get_area([self.address.msb, self.address.umb])
        temporary_area = sysex_data.get("TEMPORARY_AREA")
        synth_tone = sysex_data.get("SYNTH_TONE")
        if not current_synth == temporary_area:
            log_message(
                f"temp_area: {temporary_area} is not current_synth: {current_synth}, Skipping update"
            )
            return
        log_header_message(
            f"Updating UI components from SysEx data for \t{temporary_area} \t{synth_tone}"
        )
        incoming_data_partial_no = get_partial_number(synth_tone)
        filtered_data = filter_sysex_keys(sysex_data)
        self._apply_partial_ui_updates(incoming_data_partial_no, filtered_data)

    def _apply_partial_ui_updates(self, partial_no: int, sysex_data: dict) -> None:
        """
        Apply updates to the UI components based on the received SysEx data.
        :param partial_no: int
        :param sysex_data: dict
        :return: None
        By default has no partials, so subclass to implement partial updates
        """
        raise NotImplementedError("should be over-ridden in a sub class with implementation")

    def _parse_sysex_json(self, json_sysex_data: str) -> Optional[dict]:
        """
        _parse_sysex_json
        :param json_sysex_data: str
        :return: dict
        """
        try:
            data = self.json_parser.parse_json(json_sysex_data)
            self.sysex_previous_data = self.sysex_current_data
            self.sysex_current_data = data
            log_changes(self.sysex_previous_data, data)
            return data
        except json.JSONDecodeError as ex:
            log_message(f"Invalid JSON format: {ex}")
            return None

    def set_instrument_title_label(self, name: str, synth_type: str):
        """
        set_instrument_title_label
        :param name: str
        :param synth_type: str
        :return: None
        """

        if self.preset_type == synth_type:
            self.instrument_title_label.setText(name)

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        log_message(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        """
        update instrument title
        :return:
        """
        selected_synth_text = self.instrument_selection_combo.combo_box.currentText()
        log_message(f"selected_synth_text: {selected_synth_text}")
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
            log_message(f"preset_index: {one_based_preset_index}")
            self.load_preset(one_based_preset_index - 1)  # use 0-based index

    def load_preset(self, preset_index):
        """Load a preset by program change."""
        preset_name = (
            self.instrument_selection_combo.combo_box.currentText()
        )  # Get the selected preset name
        log_message(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        log_message(f"combo box program_number : {program_number}")

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number, self.preset_list)
        lsb = get_preset_parameter_value("lsb", program_number, self.preset_list)
        pc = get_preset_parameter_value("pc", program_number, self.preset_list)

        if None in [msb, lsb, pc]:
            log_message(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return
        log_message(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)
        # Send bank select and program change
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1,  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def _handle_program_change(self, channel: int, program: int):
        """Handle program change messages by requesting updated data"""
        log_message(
            f"Program change {program} detected on channel {channel}, requesting data update"
        )
        self.data_request()

    def _handle_control_change(self, channel: int, control: int, value: int):
        """Handle program change messages by requesting updated data"""
        log_message(
            f"Control change {channel} {control} detected on channel {channel} with value {value}, "
            f"requesting data update"
        )
        self.data_request()

    def send_control_change(self, control_change: ControlChange, value: int):
        """Send MIDI CC message"""
        if self.midi_helper:
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
        self.instrument_image_label.setStyleSheet(JDXiStyle.INSTRUMENT_IMAGE_LABEL)
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

    def _update_common_controls(self, filtered_data, successes, failures):
        pass
