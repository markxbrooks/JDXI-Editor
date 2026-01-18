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
import os
import re
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut, QShowEvent
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget

from decologr import Decologr as log
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address.address import (
    AddressOffsetSuperNATURALLMB,
    AddressOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.control_change.base import ControlChange
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_MAP
from jdxi_editor.midi.io.helper import MidiIOHelper

# from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.parser.json_parser import JDXiJsonSysexParser
from jdxi_editor.midi.sysex.request.data import SYNTH_PARTIAL_MAP
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.editors.digital.utils import (
    filter_sysex_keys,
    get_area,
    get_partial_number,
)
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.ui.editors.synth.base import SynthBase
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
        # log.message("Changes detected:")
        for key, prev, curr in changes:
            pass
            # log.message(
            #     f"\n===> Changed Parameter: {key}, Previous: {prev}, Current: {curr}"
            # )
    else:
        pass
        # --- log.message("No changes detected.")


class SynthEditor(SynthBase):
    """Base class for all editor windows"""

    parameter_received = Signal(list, int)  # address, value

    def __init__(
        self,
        midi_helper: Optional[object] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper, parent)  # Dict of JDXiSynth Types
        self.partial_map = SYNTH_PARTIAL_MAP
        self.sysex_current_data = None
        self.preset_preset_list = None
        self.programs = None
        self.midi_helper = MidiIOHelper()
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.midi_helper.midi_control_changed.connect(self._handle_control_change)
        self.cc_parameters = dict()
        self.nrpn_parameters = dict()
        self.nrpn_map = dict()
        self.controls = dict()
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
        if hasattr(self, "instrument_title_label"):
            self.midi_helper.update_tone_name.connect(
                lambda title, synth_type: self.set_instrument_title_label(
                    title, synth_type
                )
            )
        self.midi_helper.midi_program_changed.connect(self.data_request)
        log.parameter("Initialized:", self.__class__.__name__)
        log.parameter("---> Using MIDI helper:", midi_helper)
        # midi message bytes
        # To be over-ridden by subclasses
        # Set window flags for address tool window
        self.setWindowFlags(Qt.WindowType.Tool)

        # Apply common style

        JDXi.UI.ThemeManager.apply_editor_style(self)

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
            # self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper

            self.preset_loader = JDXiPresetHelper(
                self.midi_helper, JDXiPresetToneList.DIGITAL_ENUMERATED
            )
            # Initialize preset handlers dynamically
            preset_configs = [
                (
                    JDXiSynth.DIGITAL_SYNTH_1,
                    JDXiPresetToneList.DIGITAL_ENUMERATED,
                    MidiChannel.DIGITAL_SYNTH_1,
                ),
                (
                    JDXiSynth.DIGITAL_SYNTH_2,
                    JDXiPresetToneList.DIGITAL_ENUMERATED,
                    MidiChannel.DIGITAL_SYNTH_2,
                ),
                (
                    JDXiSynth.ANALOG_SYNTH,
                    JDXiPresetToneList.ANALOG_ENUMERATED,
                    MidiChannel.ANALOG_SYNTH,
                ),
                (
                    JDXiSynth.DRUM_KIT,
                    JDXiPresetToneList.DRUM_ENUMERATED,
                    MidiChannel.DRUM_KIT,
                ),
            ]
            self.preset_helpers = {
                synth_type: JDXiPresetHelper(
                    self.midi_helper, presets, channel=channel, preset_type=synth_type
                )
                for synth_type, presets, channel in preset_configs
            }
            log.message("MIDI helper initialized")
        else:
            log.message("MIDI helper not initialized")
        self.json_parser = JDXiJsonSysexParser()

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def _init_synth_data(
        self,
        synth_type: str = JDXiSynth.DIGITAL_SYNTH_1,
        partial_number: Optional[int] = 0,
    ):
        """Initialize synth-specific data."""
        from jdxi_editor.jdxi.synth.factory import create_synth_data

        self.synth_data = create_synth_data(synth_type, partial_number=partial_number)

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

    def showEvent(self, event: QShowEvent) -> None:
        """
        Override showEvent to request current settings from the instrument when the editor is shown.
        This ensures the sliders pick up the current settings from the instrument, similar to
        Digital 1, Digital 2, and Analog synth editors.

        :param event: QShowEvent
        """
        super().showEvent(event)
        if self.midi_helper:
            log.message(
                "🎛️ Effects Editor shown - requesting current settings from instrument"
            )
        self.data_request()

    def create_instrument_preset_group(self, synth_type: str = "Analog") -> QGroupBox:
        """
        Create the instrument preset group box.

        :param synth_type: str
        :return: QGroupBox
        """
        instrument_preset_group = QGroupBox(f"{synth_type} Synth")
        instrument_title_group_layout = QVBoxLayout(instrument_preset_group)
        instrument_title_group_layout.setSpacing(3)  # Reduced spacing
        instrument_title_group_layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        self.instrument_title_label = DigitalTitle()
        instrument_title_group_layout.addWidget(self.instrument_title_label)
        # --- Update_tone_name
        self.edit_tone_name_button = QPushButton("Edit tone name")
        self.edit_tone_name_button.clicked.connect(self.edit_tone_name)
        instrument_title_group_layout.addWidget(self.edit_tone_name_button)
        # --- Read request button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        instrument_title_group_layout.addWidget(self.read_request_button)
        self.instrument_selection_label = QLabel(f"Select a {synth_type} synth:")
        instrument_title_group_layout.addWidget(self.instrument_selection_label)
        self.instrument_selection_combo = PresetComboBox(self.preset_preset_list)
        if synth_type == "Analog":
            JDXi.UI.ThemeManager.apply_combo_box(
                self.instrument_selection_combo, analog=True
            )
        else:
            JDXi.UI.ThemeManager.apply_combo_box(self.instrument_selection_combo)
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
            for param, widget in self.controls.items():
                # ---- Get value from widget - all custom widgets have a value() method
                # --- (Slider, ComboBox, SpinBox, Switch all implement value())
                if hasattr(widget, "value"):
                    controls_data[param.name] = widget.value()
                else:
                    # --- Fallback for unexpected widget types
                    log.warning(
                        f"Widget for {param.name} has no value() method: {type(widget)}"
                    )
                    controls_data[param.name] = 0
            return controls_data
        except Exception as ex:
            log.error(f"Failed to get controls: {ex}")
            return {}

    def _get_preset_helper_for_current_synth(self):
        """Return the appropriate preset handler based on the current synth preset_type."""
        handler = self.preset_helpers.get(self.preset_type)
        if handler is None:
            log.warning(
                f"Unknown synth preset_type: {self.preset_type}, defaulting to digital_1"
            )
            return self.preset_helpers[JDXiSynth.DIGITAL_SYNTH_1]  # Safe fallback
        return handler

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

        if current_synth != temporary_area:
            log.message(
                f"temporary_area: {temporary_area} is not current_synth: {current_synth}, Skipping update"
            )
            return

        log.header_message(
            f"Updating UI components from SysEx data for \t{temporary_area} \t{synth_tone}"
        )

        sysex_data = filter_sysex_keys(sysex_data)

        successes, failures = [], []

        if temporary_area == AddressOffsetTemporaryToneUMB.DRUM_KIT.name:
            partial_map = DRUM_PARTIAL_MAP
        else:
            partial_map = SYNTH_PARTIAL_MAP

        partial_number = get_partial_number(synth_tone, partial_map=partial_map)
        if temporary_area == AddressOffsetTemporaryToneUMB.ANALOG_SYNTH.name:
            self._update_partial_controls(
                partial_number, sysex_data, successes, failures
            )
        if synth_tone == AddressOffsetSuperNATURALLMB.COMMON.name:
            self._update_common_controls(
                partial_number, sysex_data, successes, failures
            )
        elif synth_tone == AddressOffsetSuperNATURALLMB.MODIFY.name:
            self._update_modify_controls(
                partial_number, sysex_data, successes, failures
            )
        else:  # --- Drums and Digital 1 & 2 are dealt with via partials
            if partial_number is None:
                log.error(f"Unknown partial number for synth_tone: {synth_tone}")
                return
            log.parameter("partial_number", partial_number)
            self._update_partial_controls(
                partial_number, sysex_data, successes, failures
            )

        log.debug_info(successes, failures)

    def _update_partial_controls(
        self, partial_no: int, sysex_data: dict, successes: list, failures: list
    ) -> None:
        """
        Apply updates to the UI components based on the received SysEx data.

        :param partial_no: int
        :param sysex_data: dict
        :param successes: list
        :param failures: list
        :return: None
        By default has no partials, so subclass to implement partial updates
        """
        raise NotImplementedError(
            "should be over-ridden in a sub class with implementation"
        )

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
            log.message(f"Invalid JSON format: {ex}")
            return None

    def set_instrument_title_label(self, name: str, synth_type: str):
        """
        set_instrument_title_label

        :param name: str
        :param synth_type: str
        :return: None
        """
        if self.preset_type == synth_type:
            # Get title label from widget or direct attribute
            title_label = None
            if hasattr(self, "instrument_preset") and self.instrument_preset:
                title_label = getattr(
                    self.instrument_preset, "instrument_title_label", None
                )
            if not title_label:
                title_label = getattr(self, "instrument_title_label", None)
            if title_label:
                title_label.setText(name)
        self.tone_names[synth_type] = name

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        log.message(f"Updating combo to preset {preset_number}")
        combo_box = self._get_instrument_selection_combo()
        if combo_box:
            combo_box.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        """
        update instrument title

        :return:
        """
        selected_synth_text = self._get_selected_instrument_text()
        log.message(f"selected_synth_text: {selected_synth_text}")
        # --- Get title label from widget or direct attribute
        title_label = None
        if hasattr(self, "instrument_preset") and self.instrument_preset:
            title_label = getattr(
                self.instrument_preset, "instrument_title_label", None
            )
        if not title_label:
            title_label = getattr(self, "instrument_title_label", None)
        if title_label:
            title_label.setText(selected_synth_text)

    def update_instrument_preset(self, text: str):
        """
        update_instrument_preset

        :param text:
        :return:
        """
        selected_synth_text = self._get_selected_instrument_text()
        if synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_synth_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            one_based_preset_index = int(selected_synth_padded_number)
            log.message(f"preset_index: {one_based_preset_index}")
            self.load_preset(one_based_preset_index - 1)  # use 0-based index

    def load_preset(self, preset_index):
        """Load a preset by program change."""
        # --- Get the combo box - it might be in instrument_preset widget or directly on self
        combo_box = self._get_instrument_selection_combo()
        if not combo_box:
            log.error("Instrument selection combo box is not available")
            return

        preset_name = combo_box.combo_box.currentText()  # Get the selected preset name
        log.message(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        log.message(f"combo box program_number : {program_number}")

        # --- Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number, self.preset_preset_list)
        lsb = get_preset_parameter_value("lsb", program_number, self.preset_preset_list)
        pc = get_preset_parameter_value("pc", program_number, self.preset_preset_list)

        if None in [msb, lsb, pc]:
            log.message(
                f"Could not retrieve preset parameters for program {program_number}"
            )
            return

        # --- Ensure midi_channel is set - it should be set by _init_synth_data, but check anyway
        if self.midi_channel is None:
            # --- Try to determine channel from preset_type
            channel_map = {
                JDXiSynth.DIGITAL_SYNTH_1: MidiChannel.DIGITAL_SYNTH_1,
                JDXiSynth.DIGITAL_SYNTH_2: MidiChannel.DIGITAL_SYNTH_2,
                JDXiSynth.ANALOG_SYNTH: MidiChannel.ANALOG_SYNTH,
                JDXiSynth.DRUM_KIT: MidiChannel.DRUM_KIT,
            }
            if self.preset_type in channel_map:
                self.midi_channel = channel_map[self.preset_type]
                log.message(
                    f"Set midi_channel to {self.midi_channel} based on preset_type {self.preset_type}"
                )
            else:
                log.error(
                    f"midi_channel is None and could not determine from preset_type {self.preset_type}"
                )
                return

        log.message(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log.message(f"Using MIDI channel: {self.midi_channel}")
        log_midi_info(msb, lsb, pc)
        # -- Send bank select and program change
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1,  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def _handle_program_change(self, channel: int, program: int):
        """Handle program change messages by requesting updated data"""
        log.message(
            f"Program change {program} detected on channel {channel}, requesting data update"
        )
        self.data_request()

    def _handle_control_change(self, channel: int, control: int, value: int):
        """Handle program change messages by requesting updated data"""
        log.message(
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
        if image_path and os.path.exists(image_path):
            file_to_load = image_path
        elif secondary_image_path and os.path.exists(secondary_image_path):
            file_to_load = secondary_image_path
        else:
            # --- Fallback to default image using resource_path
            if hasattr(self, "instrument_icon_folder") and hasattr(
                self, "instrument_default_image"
            ):
                file_to_load = resource_path(
                    os.path.join(
                        "resources",
                        self.instrument_icon_folder,
                        self.instrument_default_image,
                    )
                )
            else:
                log.error(
                    "Cannot load image: missing instrument_icon_folder or instrument_default_image"
                )
                image_label = self._get_instrument_image_label()
                if image_label:
                    image_label.clear()
                return False

        if not os.path.exists(file_to_load):
            log.warning(f"Image file does not exist: {file_to_load}")
            image_label = self._get_instrument_image_label()
            if image_label:
                image_label.clear()
            return False

        pixmap = QPixmap(file_to_load)
        if pixmap.isNull():
            log.error(f"Failed to load pixmap from: {file_to_load}")
            image_label = self._get_instrument_image_label()
            if image_label:
                image_label.clear()
            return False

        # --- Scale maintaining aspect ratio, fitting within width and height constraints
        scaled_pixmap = pixmap.scaled(
            JDXi.UI.Style.INSTRUMENT_IMAGE_WIDTH,
            JDXi.UI.Style.INSTRUMENT_IMAGE_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        image_label = self._get_instrument_image_label()
        if image_label:
            image_label.setPixmap(scaled_pixmap)
            image_label.setScaledContents(False)  # Don't stretch, maintain aspect ratio
            image_label.setStyleSheet(JDXi.UI.Style.INSTRUMENT_IMAGE_LABEL)
            log.debug(f"Successfully loaded image: {file_to_load}")
        else:
            log.error("Instrument image label not found - cannot set image")
            return False
        return True

    def update_instrument_image(self):
        """Update the instrument image based on the selected synth."""
        selected_text = self._get_selected_instrument_text()
        if not selected_text:
            self._fallback_to_default_image("No instrument text selected.")
            return

        name, type_ = self._parse_instrument_text(selected_text)
        if name and type_:
            image_loaded = self._try_load_specific_or_generic_image(name, type_)
        else:
            image_loaded = False

        if not image_loaded:
            self._fallback_to_default_image("Failed to load specific/generic image.")

    def _get_instrument_selection_combo(self):
        """
        Get the instrument selection combo box from either the widget or direct attribute.
        Returns None if not found.
        """
        # --- Try to get from InstrumentPresetWidget first (for Digital/Drum editors)
        if hasattr(self, "instrument_preset") and self.instrument_preset:
            return getattr(self.instrument_preset, "instrument_selection_combo", None)
        # --- Fallback to direct attribute (for Analog editor or legacy code)
        return getattr(self, "instrument_selection_combo", None)

    def _get_instrument_image_label(self):
        """
        Get the instrument image label from either the widget or direct attribute.
        Returns None if not found.
        """
        # Try to get from InstrumentPresetWidget first (for Digital/Drum editors)
        if hasattr(self, "instrument_preset") and self.instrument_preset:
            label = getattr(self.instrument_preset, "instrument_image_label", None)
            if label:
                log.debug("Found instrument_image_label in instrument_preset widget")
                return label
        # Fallback to direct attribute (for Analog editor or legacy code)
        label = getattr(self, "instrument_image_label", None)
        if label:
            log.debug("Found instrument_image_label as direct attribute")
        else:
            log.warning(
                "Instrument image label not found in widget or direct attribute"
            )
        return label

    def _get_selected_instrument_text(self) -> str:
        """
        _get_selected_instrument_text

        :return: str
        """
        combo_box = self._get_instrument_selection_combo()
        if combo_box:
            combo = getattr(combo_box, "combo_box", None)
            if combo and hasattr(combo, "currentText"):
                return combo.currentText()
        log.error("Instrument combo box is missing or malformed.")
        return ""

    def _parse_instrument_text(self, text: str) -> tuple:
        """
        _parse_instrument_text
        :param text: str
        :return: tuple name, type_
        """
        match = re.search(r"(\d{3}) - (\S+)\s(\S+)+", text, re.IGNORECASE)
        if not match:
            log.warning("Instrument text did not match expected pattern.")
            return None, None
        try:
            name = match.group(2).lower().replace("&", "_").split("_")[0]
            type_ = match.group(3).lower().replace("&", "_").split("_")[0]
            log.parameter("Parsed instrument name:", name)
            log.parameter("Parsed instrument type:", type_)
            return name, type_
        except Exception as ex:
            log.error(f"Error parsing instrument name/type: {ex}")
            return None, None

    def _try_load_specific_or_generic_image(self, name: str, type_: str) -> bool:
        try:
            specific_path = resource_path(
                os.path.join("resources", self.instrument_icon_folder, f"{name}.png")
            )
            generic_path = resource_path(
                os.path.join("resources", self.instrument_icon_folder, f"{type_}.png")
            )
            return self.load_and_set_image(specific_path, generic_path)
        except Exception as ex:
            log.error(f"Error loading specific/generic images: {ex}")
            return False

    def _fallback_to_default_image(self, reason: str):
        log.info(f"{reason} Falling back to default image.")
        try:
            default_path = resource_path(
                os.path.join(
                    "resources",
                    self.instrument_icon_folder,
                    self.instrument_default_image,
                )
            )
            if not self.load_and_set_image(default_path):
                log.error("Default instrument image not found. Clearing label.")
                image_label = self._get_instrument_image_label()
                if image_label:
                    image_label.clear()
        except Exception as ex:
            log.error(f"Error loading default image: {ex}")
            image_label = self._get_instrument_image_label()
            if image_label:
                image_label.clear()

    def _update_common_controls(
        self, partial_number: int, filtered_data, successes, failures
    ):
        pass

    def _update_modify_controls(
        self, partial_number: int, filtered_data, successes, failures
    ):
        pass
