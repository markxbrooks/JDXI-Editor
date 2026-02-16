"""
synth_editor.py

This module defines the `SynthEditor` class, a base class for all editor windows in the JD-Xi Manager application.
It provides an interface for editing synthesizer parameters, handling MIDI messages, and updating UI components.

Key Features:
- UI Elements: Uses PySide6 widgets, including ComboBoxes, Sliders, and SpinBoxes, to adjust synthesizer parameters.
- MIDI Integration: Sends and receives MIDI messages via `MIDIHelper`, supporting parameter changes, SysEx communication,
  and program change handling.
- Preset Management: Loads, updates, and applies instrument presets with `PresetHandler` and `PresetLoader`.
- Parameter Control: Dynamically creates UI controls for synthesizer parameters, supporting bipolar values and digital conversion.
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

from decologr import Decologr as log
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut, QShowEvent
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.address import JDXiSysExOffsetSuperNATURALLMB
from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExAddressStartMSB,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_MAP
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.sysex.parser.json_parser import JDXiJsonSysexParser
from jdxi_editor.midi.sysex.request.data import SYNTH_PARTIAL_MAP
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.resources import resource_path
from jdxi_editor.ui.editors.digital.utils import (
    filter_sysex_keys,
    get_area,
    get_partial_number,
)
from jdxi_editor.ui.editors.helpers.preset import get_preset_parameter_value
from jdxi_editor.ui.editors.synth.base import SynthBase
from jdxi_editor.ui.editors.synth.helper import log_changes
from jdxi_editor.ui.editors.synth.specs import (
    DRUM_KIT_SPECS,
    ENGINE_KEYWORDS,
    INSTRUMENT_FAMILY_SPECS,
    InstrumentDescriptor,
)
from jdxi_editor.ui.preset.helper import JDXiPresetHelper

TONE_DISPATCH = {
    JDXiSysExOffsetSuperNATURALLMB.COMMON: "_update_common_controls",
    JDXiSysExOffsetSuperNATURALLMB.MODIFY: "_update_modify_controls",
}


SYNTH_CAPABILITIES = {
    JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT: {
        "partials": DRUM_PARTIAL_MAP,
        "supports_common": False,
    },
    JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH: {
        "partials": SYNTH_PARTIAL_MAP,
        "supports_common": True,
    },
}


def get_storage_scope(msb: int) -> str:
    return JDXiSysExAddressStartMSB(msb).name


def get_editor_target(msb: int, umb: int) -> str:
    if msb == JDXiSysExAddressStartMSB.TEMPORARY_PROGRAM:
        return "PROGRAM"
    return JDXiSysExOffsetTemporaryToneUMB(umb).name


class SynthEditor(SynthBase):
    """Base class for all editor windows"""

    parameter_received = Signal(list, int)  # address, value

    def __init__(
        self,
        midi_helper: Optional[object] = None,
        parent: Optional[QWidget] = None,
        address: Optional[JDXiSysExAddress] = None,
    ):
        super().__init__(
            midi_helper=midi_helper, parent=parent, address=address
        )  # Dict of JDXiSynth Types
        self.partial_map = SYNTH_PARTIAL_MAP
        self.sysex_current_data = None
        self.preset_preset_list = None
        self.programs = None
        # Use passed-in midi_helper so MIDI sending works (e.g. Analog editor); only create new if None
        if midi_helper is None:
            self.midi_helper = MidiIOHelper()
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.midi_helper.midi_control_changed.connect(self._handle_control_change)
        self.cc_parameters = dict()
        self.nrpn_parameters = dict()
        self.nrpn_map = dict()
        # self.controls from SynthBase (ControlRegistry)
        self.bipolar_parameters = list()
        # Midi request for Temporary program
        self.midi_requests = list()
        self.instrument_default_image = None
        self.instrument_title_label = None
        self.instrument_image_label = None
        self.instrument_icon_folder = None
        self.partial_number = None
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
        log.parameter(
            scope=self.__class__.__name__,
            message="Initialized:",
            parameter=self.__class__.__name__,
        )
        log.parameter(
            scope=self.__class__.__name__,
            message="---> Using MIDI helper:",
            parameter=midi_helper,
        )
        # midi message bytes
        # To be over-ridden by subclasses
        # Set window flags for address tool window
        self.setWindowFlags(Qt.WindowType.Tool)

        # --- Apply common style
        JDXi.UI.Theme.apply_editor_style(self)

        # --- Add keyboard shortcuts
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)

        # --- Add close window shortcut
        self.close_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
        self.close_shortcut.activated.connect(self.close)

        # --- Common minimum size for all editors
        self.setMinimumSize(200, 200)

        # Connect to program change signal if MIDI helper exists
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_control_changed.connect(self._handle_control_change)
            # self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)

            self.preset_loader = JDXiPresetHelper(
                self.midi_helper, JDXi.UI.Preset.Digital.ENUMERATED
            )
            # Initialize preset handlers dynamically
            preset_configs = [
                (
                    JDXi.Synth.DIGITAL_SYNTH_1,
                    JDXi.UI.Preset.Digital.ENUMERATED,
                    MidiChannel.DIGITAL_SYNTH_1,
                ),
                (
                    JDXi.Synth.DIGITAL_SYNTH_2,
                    JDXi.UI.Preset.Digital.ENUMERATED,
                    MidiChannel.DIGITAL_SYNTH_2,
                ),
                (
                    JDXi.Synth.ANALOG_SYNTH,
                    JDXi.UI.Preset.Analog.ENUMERATED,
                    MidiChannel.ANALOG_SYNTH,
                ),
                (
                    JDXi.Synth.DRUM_KIT,
                    JDXi.UI.Preset.Drum.ENUMERATED,
                    MidiChannel.DRUM_KIT,
                ),
            ]
            self.preset_helpers = {
                synth_type: JDXiPresetHelper(
                    self.midi_helper, presets, channel=channel, preset_type=synth_type
                )
                for synth_type, presets, channel in preset_configs
            }
            log.message(
                scope=self.__class__.__name__, message="MIDI helper initialized"
            )
        else:
            log.message(
                scope=self.__class__.__name__, message="MIDI helper not initialized"
            )
        self.json_parser = JDXiJsonSysexParser()

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def _init_synth_data(
        self,
        synth_type: str = JDXi.Synth.DIGITAL_SYNTH_1,
        partial_number: Optional[int] = 0,
    ):
        """Initialize synth-specific data."""
        from jdxi_editor.core.synth.factory import create_synth_data

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
                "🎛️Effects Editor shown - requesting current settings from instrument",
                scope="SynthEditor",
            )
        self.data_request()

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
                        scope=self.__class__.__name__,
                        message=f"Widget for {param.name} has no value() method: {type(widget)}",
                    )
                    controls_data[param.name] = 0
            return controls_data
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__, message=f"Failed to get controls: {ex}"
            )
            return {}

    def _get_preset_helper_for_current_synth(self):
        """Return the appropriate preset handler based on the current synth preset_type."""
        handler = self.preset_helpers.get(self.preset_type)
        if handler is None:
            log.warning(
                scope=self.__class__.__name__,
                message=f"Unknown synth preset_type: {self.preset_type}, defaulting to digital_1",
            )
            return self.preset_helpers[JDXi.Synth.DIGITAL_SYNTH_1]  # Safe fallback
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
        # log.message(f"self.address.msb, self.address.umb, {self.address.msb}, {self.address.umb}")
        current_synth = get_area([self.address.msb, self.address.umb])
        temporary_area = sysex_data.get(SysExSection.TEMPORARY_AREA)
        synth_tone = sysex_data.get(SysExSection.SYNTH_TONE)

        if current_synth != temporary_area:
            log.message(
                scope=self.__class__.__name__,
                message=f"temporary_area: {temporary_area} is not current_synth: {current_synth}, Skipping update",
                silent=True,
            )
            return

        log.header_message(
            scope=self.__class__.__name__,
            message=f"Updating UI components from SysEx data for {temporary_area} {synth_tone}",
        )

        sysex_data = filter_sysex_keys(sysex_data)

        successes, failures = [], []

        if temporary_area == JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT.name:
            partial_map = DRUM_PARTIAL_MAP
        else:
            partial_map = SYNTH_PARTIAL_MAP

        partial_number = get_partial_number(synth_tone, partial_map=partial_map)
        if temporary_area == JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH.name:
            self._update_controls(partial_number, sysex_data, successes, failures)
        if synth_tone == JDXiSysExOffsetSuperNATURALLMB.COMMON.name:
            self._update_common_controls(
                partial_number, sysex_data, successes, failures
            )
        elif synth_tone == JDXiSysExOffsetSuperNATURALLMB.MODIFY.name:
            self._update_modify_controls(
                partial_number, sysex_data, successes, failures
            )
        else:  # --- Drums and Digital 1 & 2 are dealt with via partials
            if partial_number is None:
                log.error(
                    scope=self.__class__.__name__,
                    message=f"Unknown partial number for synth_tone: {synth_tone}",
                )
                return
            log.parameter(
                scope=self.__class__.__name__,
                message="partial_number _update_controls",
                parameter=partial_number,
            )
            self._update_controls(partial_number, sysex_data, successes, failures)

        log.debug_info(
            successes=successes, failures=failures, scope=self.__class__.__name__
        )

    def _update_controls(
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
            log.message(
                scope=self.__class__.__name__, message=f"Invalid JSON format: {ex}"
            )
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
        log.message(
            scope=self.__class__.__name__,
            message=f"Updating combo to preset {preset_number}",
        )
        combo_box = self._get_instrument_selection_combo()
        if combo_box:
            combo_box.combo_box.setCurrentIndex(preset_number)

    def update_instrument_title(self):
        """
        update instrument title

        :return:
        """
        selected_synth_text = self._get_selected_instrument_text()
        log.message(
            scope=self.__class__.__name__,
            message=f"selected_synth_text: {selected_synth_text}",
        )
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
            log.message(
                scope=self.__class__.__name__,
                message=f"preset_index: {one_based_preset_index}",
            )
            self.load_preset(one_based_preset_index - 1)  # use 0-based index

    def load_preset(self, preset_index):
        """Load a preset by program change."""
        # --- Get the combo box - it might be in instrument_preset widget or directly on self
        combo_box = self._get_instrument_selection_combo()
        if not combo_box:
            log.error(
                scope=self.__class__.__name__,
                message="Instrument selection combo box is not available",
            )
            return

        preset_name = combo_box.combo_box.currentText()  # Get the selected preset name
        log.message(
            scope=self.__class__.__name__,
            message=f"combo box preset_name : {preset_name}",
        )
        program_number = preset_name[:3]
        log.message(
            scope=self.__class__.__name__,
            message=f"combo box program_number : {program_number}",
        )

        # --- Determine preset list if not already set
        if self.preset_preset_list is None:

            # Determine preset list based on preset_type
            if (
                self.preset_type == JDXi.Synth.DIGITAL_SYNTH_1
                or self.preset_type == JDXi.Synth.DIGITAL_SYNTH_2
            ):
                self.preset_preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE
            elif self.preset_type == JDXi.Synth.ANALOG_SYNTH:
                self.preset_preset_list = JDXi.UI.Preset.Analog.PROGRAM_CHANGE
            elif self.preset_type == JDXi.Synth.DRUM_KIT:
                self.preset_preset_list = JDXi.UI.Preset.Drum.PROGRAM_CHANGE
            else:
                # Default to digital preset list
                self.preset_preset_list = JDXi.UI.Preset.Digital.PROGRAM_CHANGE
                log.warning(
                    scope=self.__class__.__name__,
                    message=f"Unknown preset_type {self.preset_type}, defaulting to JDXi.UI.Preset.Digital.LIST",
                )

        # --- Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        if self.preset_preset_list is None:
            log.error(
                scope=self.__class__.__name__,
                message="preset_preset_list is still None after initialization",
            )
            return

        msb = get_preset_parameter_value("msb", program_number, self.preset_preset_list)
        lsb = get_preset_parameter_value("lsb", program_number, self.preset_preset_list)
        pc = get_preset_parameter_value("pc", program_number, self.preset_preset_list)

        if None in [msb, lsb, pc]:
            log.message(
                scope=self.__class__.__name__,
                message=f"Could not retrieve preset parameters for program {program_number}",
            )
            return

        # --- Ensure midi_channel is set - it should be set by _init_synth_data, but check anyway
        if self.midi_channel is None:
            # --- Try to determine channel from preset_type
            channel_map = {
                JDXi.Synth.DIGITAL_SYNTH_1: MidiChannel.DIGITAL_SYNTH_1,
                JDXi.Synth.DIGITAL_SYNTH_2: MidiChannel.DIGITAL_SYNTH_2,
                JDXi.Synth.ANALOG_SYNTH: MidiChannel.ANALOG_SYNTH,
                JDXi.Synth.DRUM_KIT: MidiChannel.DRUM_KIT,
            }
            if self.preset_type in channel_map:
                self.midi_channel = channel_map[self.preset_type]
                log.message(
                    scope=self.__class__.__name__,
                    message=f"Set midi_channel to {self.midi_channel} based on preset_type {self.preset_type}",
                )
            else:
                log.error(
                    scope=self.__class__.__name__,
                    message=f"midi_channel is None and could not determine from preset_type {self.preset_type}",
                )
                return

        log.message(
            scope=self.__class__.__name__,
            message=f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}",
        )
        log.message(
            scope=self.__class__.__name__,
            message=f"Using MIDI channel: {self.midi_channel}",
        )
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
            scope=self.__class__.__name__,
            message=f"Program change {program} detected on channel {channel}, requesting data update",
        )
        # self.data_request() reducing midi flood

    def _handle_control_change(self, channel: int, control: int, value: int):
        """Handle program change messages by requesting updated data"""
        log.message(
            scope=self.__class__.__name__,
            message=f"Control change {channel} {control} detected on channel {channel} with value {value}, ",
        )
        log.message(scope=self.__class__.__name__, message="requesting data update")
        # self.data_request() reducing midi flood

    def load_and_set_image(self, image_path, secondary_image_path=None):
        """Helper function to load and set the image on the label."""
        log.debug(
            scope=self.__class__.__name__,
            message=f"load_and_set_image called with primary: {image_path}, secondary: {secondary_image_path}",
        )

        if image_path and os.path.exists(image_path):
            file_to_load = image_path
            log.debug(
                scope=self.__class__.__name__,
                message=f"Using primary image path: {file_to_load}",
            )
        elif secondary_image_path and os.path.exists(secondary_image_path):
            file_to_load = secondary_image_path
            log.debug(
                scope=self.__class__.__name__,
                message=f"Using secondary image path: {file_to_load}",
            )
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
                log.debug(
                    scope=self.__class__.__name__,
                    message=f"Falling back to default image: {file_to_load}",
                )
            else:
                log.error(
                    scope=self.__class__.__name__,
                    message=f"Cannot load image: missing instrument_icon_folder ({getattr(self, 'instrument_icon_folder', None)}) or instrument_default_image ({getattr(self, 'instrument_default_image', None)})",
                )
                image_label = self._get_instrument_image_label()
                if image_label:
                    image_label.clear()
                return False

        if not os.path.exists(file_to_load):
            log.warning(
                scope=self.__class__.__name__,
                message=f"Image file does not exist: {file_to_load}",
            )
            image_label = self._get_instrument_image_label()
            if image_label:
                image_label.clear()
            return False

        pixmap = QPixmap(file_to_load)
        if pixmap.isNull():
            log.error(
                scope=self.__class__.__name__,
                message=f"Failed to load pixmap from: {file_to_load}",
            )
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
            log.debug(
                scope=self.__class__.__name__,
                message=f"Successfully loaded image: {file_to_load}",
            )
        else:
            log.error(
                scope=self.__class__.__name__,
                message="Instrument image label not found - cannot set image",
            )
            return False
        return True

    def update_instrument_image(self):
        """Update the instrument image based on the selected synth."""
        selected_text = self._get_selected_instrument_text()
        if not selected_text:
            self._fallback_to_default_image("No instrument text selected.")
            return

        descriptor = self._parse_instrument_text(selected_text)
        if descriptor is None:
            self._fallback_to_default_image("Failed to parse instrument text.")
            return

        # Extract name and type from InstrumentDescriptor
        # Use engine as name (e.g., "fm", "jd") or extract from raw_text
        name = descriptor.engine

        # Special handling for drum kits: Extract model number (e.g., "909", "808", "707", "cr-78")
        if descriptor.category == "drum":
            text_lower = descriptor.raw_text.lower()
            # Look for drum model numbers in the text
            import re

            # First, try to match "cr-78" pattern (special case for CR-78)
            if "cr-78" in text_lower or "cr78" in text_lower:
                name = "cr-78"
            # Then try to match "tr-XXX" pattern (e.g., "tr-909", "tr-808")
            elif re.search(r"tr-(\d{3})", text_lower):
                tr_match = re.search(r"tr-(\d{3})", text_lower)
                name = tr_match.group(1)  # Extract the 3-digit number after "tr-"
            else:
                # Fallback: look for known drum model numbers in the text
                # Match standalone 3-digit numbers that are drum models
                known_models = ["909", "808", "707", "727", "606", "626"]
                for model in known_models:
                    if model in text_lower:
                        name = model
                        break
                else:
                    # No model found, use engine name
                    name = descriptor.engine

        # Special handling: Check for specific engine names in raw_text that might not be detected
        # This ensures "JP8" matches "jp8.png" even if engine is "jupiter"
        text_lower = descriptor.raw_text.lower()
        engine_name_patterns = {
            "jp8": ["jp8", "jupiter8"],
            "juno": ["juno", "jn"],
            "jd": ["jd"],
            "fm": ["fm"],
            "tb": ["tb", "tb-303", "303"],
            "mg": ["mg", "minimoog"],
            "sh": ["sh", "sh-101", "101"],
            "d-50": ["d-50", "d50"],
            "vp-330": ["vp-330", "vp330"],
            "mks": ["mks", "mks-50"],
            "mc": ["mc", "mc-202", "202"],
        }

        # Check if any engine name pattern matches in the text (only for non-drum)
        if descriptor.category != "drum":
            for engine_name, patterns in engine_name_patterns.items():
                if any(pattern in text_lower for pattern in patterns):
                    name = engine_name
                    break

        if not name:
            # Extract first word after number and dash as fallback name
            words = descriptor.raw_text.split()
            for i, word in enumerate(words):
                if i > 0 and word != "-" and not word.isdigit():
                    name = word.lower().replace("&", "_").split("_")[0]
                    break

        # Use family as type (e.g., "piano", "pad", "bass")
        type_ = descriptor.family

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
        # --- Try to get from InstrumentPresetWidget first (for Digital/Drum editors)
        if hasattr(self, "instrument_preset") and self.instrument_preset:
            label = getattr(self.instrument_preset, "instrument_image_label", None)
            if label:
                log.debug(
                    scope=self.__class__.__name__,
                    message="Found instrument_image_label.",
                )
                return label
        # Fallback to direct attribute (for Analog editor or legacy code)
        label = getattr(self, "instrument_image_label", None)
        if label:
            log.debug(
                scope=self.__class__.__name__,
                message="Found instrument_image_label as direct attribute",
            )
        else:
            log.warning(
                "[SynthEditor] Instrument image label not found in widget or direct attribute"
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
        log.error(
            scope=self.__class__.__name__,
            message="Instrument combo box is missing or malformed.",
        )
        return ""

    def _parse_instrument_text(self, text: str) -> Optional[InstrumentDescriptor]:
        text_lower = text.lower()

        # --------------------------------------------------
        # 1. Drum kits (highest priority)
        # --------------------------------------------------
        for spec in DRUM_KIT_SPECS:
            if any(kw in text_lower for kw in spec.keywords):
                return InstrumentDescriptor(
                    category="drum",
                    family=spec.family,
                    engine=spec.engine,
                    raw_text=text,
                )

        # --------------------------------------------------
        # 2. Detect synth engine
        # --------------------------------------------------
        engine = None
        for engine_name, keywords in ENGINE_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                engine = engine_name
                break

        # --------------------------------------------------
        # 3. Detect synth family
        # --------------------------------------------------
        for spec in INSTRUMENT_FAMILY_SPECS:
            if any(kw in text_lower for kw in spec.keywords):
                return InstrumentDescriptor(
                    category="synth",
                    family=spec.family,
                    engine=engine,
                    raw_text=text,
                )

        log.warning(
            scope=self.__class__.__name__,
            message=f"Unrecognized instrument preset: {text}",
        )
        return None

    def _try_load_specific_or_generic_image(self, name: str, type_: str) -> bool:
        try:
            if not self.instrument_icon_folder:
                log.error(
                    scope=self.__class__.__name__,
                    message=f"Instrument icon folder not set. Cannot load image for {name}/{type_}",
                )
                return False

            # Build list of paths to try (in order of preference)
            paths_to_try = []

            # Special case: For piano family, prioritize piano.png over engine-specific images
            # This ensures "JD Piano 1" matches piano.png instead of jd.png
            if type_ == "piano":
                # 1. Try piano.png first (family image)
                paths_to_try.append(
                    resource_path(
                        os.path.join(
                            "resources", self.instrument_icon_folder, f"{type_}.png"
                        )
                    )
                )
                # 2. Then try specific name image as fallback (e.g., "jd.png")
                if name:
                    paths_to_try.append(
                        resource_path(
                            os.path.join(
                                "resources", self.instrument_icon_folder, f"{name}.png"
                            )
                        )
                    )
            # Special case: For guitar family, prioritize strat.png over other images
            # This ensures guitar presets (179-184) match strat.png
            elif type_ == "guitar":
                # 1. Try strat.png first
                paths_to_try.append(
                    resource_path(
                        os.path.join(
                            "resources", self.instrument_icon_folder, "strat.png"
                        )
                    )
                )
                # 2. Then try specific name image as fallback
                if name:
                    paths_to_try.append(
                        resource_path(
                            os.path.join(
                                "resources", self.instrument_icon_folder, f"{name}.png"
                            )
                        )
                    )
                # 3. Finally try generic guitar.png as fallback
                paths_to_try.append(
                    resource_path(
                        os.path.join(
                            "resources", self.instrument_icon_folder, f"{type_}.png"
                        )
                    )
                )
            # Special case: For FM engine synths, prioritize fm.png over family images
            # This ensures FM synths (155, 156, 237) match fm.png instead of bass.png or brass.png
            elif name == "fm":
                # 1. Try fm.png first (engine image)
                paths_to_try.append(
                    resource_path(
                        os.path.join("resources", self.instrument_icon_folder, "fm.png")
                    )
                )
                # 2. Then try generic type image as fallback (e.g., "bass.png", "brass.png")
                if type_:
                    paths_to_try.append(
                        resource_path(
                            os.path.join(
                                "resources", self.instrument_icon_folder, f"{type_}.png"
                            )
                        )
                    )
            else:
                # Default behavior: Try specific name image first, then generic type image
                # 1. Try specific name image (e.g., "trem.png")
                if name:
                    paths_to_try.append(
                        resource_path(
                            os.path.join(
                                "resources", self.instrument_icon_folder, f"{name}.png"
                            )
                        )
                    )

                # 2. Try generic type image (e.g., "pad.png" if type_ is "pad")
                if type_:
                    paths_to_try.append(
                        resource_path(
                            os.path.join(
                                "resources", self.instrument_icon_folder, f"{type_}.png"
                            )
                        )
                    )

            log.debug(
                scope=self.__class__.__name__,
                message=f"Trying to load images (in order): {paths_to_try}",
            )
            log.debug(
                scope=self.__class__.__name__,
                message=f"Instrument icon folder: {self.instrument_icon_folder}",
            )

            # Try primary path first, then secondary, etc.
            primary_path = paths_to_try[0] if paths_to_try else None
            secondary_path = paths_to_try[1] if len(paths_to_try) > 1 else None

            return self.load_and_set_image(primary_path, secondary_path)
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Error loading specific/generic images: {ex}",
            )
            import traceback

            log.error(traceback.format_exc())
            return False

    def _fallback_to_default_image(self, reason: str):
        log.info(
            scope=self.__class__.__name__,
            message=f"{reason} Falling back to default image.",
        )
        try:
            default_path = resource_path(
                os.path.join(
                    "resources",
                    self.instrument_icon_folder,
                    self.instrument_default_image,
                )
            )
            if not self.load_and_set_image(default_path):
                log.error(
                    scope=self.__class__.__name__,
                    message="Default instrument image not found. Clearing label.",
                )
                image_label = self._get_instrument_image_label()
                if image_label:
                    image_label.clear()
        except Exception as ex:
            log.error(
                scope=self.__class__.__name__,
                message=f"Error loading default image: {ex}",
            )
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
