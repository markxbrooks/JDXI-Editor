"""
DrumEditor Module
=================

This module provides the `DrumEditor` class, which serves as
an editor for JD-Xi Drum Kit parameters.
It enables users to modify drum kit settings,
select presets, and send MIDI messages to address connected JD-Xi synthesizer.

Classes
-------

- `DrumEditor`: A graphical editor for JD-Xi drum kits, supporting preset
selection, parameter adjustments, and MIDI communication.

Dependencies
------------

- `PySide6.QtWidgets` for UI components.
- `PySide6.QtCore` for Qt core functionality.
- `jdxi_manager.midi.data.parameter.drums.DrumParameter` for drum parameter definitions.
- `jdxi_manager.midi.data.presets.data.DRUM_PRESETS_ENUMERATED` for enumerated drum presets.
- `jdxi_manager.midi.data.presets.preset_type.PresetType` for preset categorization.
- `jdxi_manager.midi.io.MIDIHelper` for MIDI communication.
- `jdxi_manager.midi.preset.loader.PresetLoader` for loading JD-Xi presets.
- `jdxi_manager.ui.editors.drum_partial.DrumPartialEditor` for managing individual drum partials.
- `jdxi_manager.ui.style.Style` for UI styling.
- `jdxi_manager.ui.editors.base.SynthEditor` as the base class for the editor.
- `jdxi_manager.midi.data.constants.sysex.TEMPORARY_DIGITAL_SYNTH_1_AREA` for SysEx address handling.
- `jdxi_manager.ui.widgets.preset.combo_box.PresetComboBox` for preset selection.

Features
--------

- Displays and edits JD-Xi drum kit parameters.
- Supports drum kit preset selection and loading.
- Provides sliders, spin boxes, and combo boxes for adjusting kit parameters.
- Includes address tabbed interface for managing individual drum partials.
- Sends MIDI System Exclusive (SysEx) messages to update the JD-Xi in real time.

Usage
-----

To use the `DrumEditor`, instantiate it with an optional `MIDIHelper` instance:

.. code-block:: python

    from jdxi_editor.midi.io import MIDIHelper
    from jdxi_editor.ui.editors.drum_editor import DrumEditor
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    midi_helper = MIDIHelper()
    editor = DrumEditor(midi_helper)
    editor.show()
    app.exec()

"""

import os
import re
import logging
from typing import Optional, Dict
import json

from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QWidget,
    QTabWidget,
    QFormLayout,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParameter
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParameter
from jdxi_editor.midi.data.presets.drum import DRUM_PRESETS_ENUMERATED
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.sysex.requests import PROGRAM_COMMON_REQUEST, DRUMS_REQUEST, DRUMS_REQUESTS
from jdxi_editor.ui.editors.drum.partial import DrumPartialEditor
from jdxi_editor.ui.editors.helpers.program import get_preset_parameter_value, log_midi_info
from jdxi_editor.ui.style import Style
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.midi.data.constants.sysex import (
    TEMPORARY_TONE_AREA,
    DRUM_KIT_AREA,
)
from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_DRUMS
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox


class DrumCommonEditor(SynthEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(
        self, midi_helper: Optional[MidiIOHelper] = None, preset_helper=None, parent=None
    ):
        super().__init__(midi_helper, parent)

        # Initialize class attributes

        # Presets
        self.preset_type = SynthType.DRUMS
        self.preset_helper = preset_helper
        self.preset_list = DRUM_PRESETS_ENUMERATED

        # midi parameters
        self.partial_num = 1
        self.area = TEMPORARY_TONE_AREA
        self.part = DRUM_KIT_AREA
        self.group = 0x2E
        self.current_data = None
        self.previous_data = None
        self.partial_mapping = {
            "BD1": 0,
            "RIM": 1,
            "BD2": 2,
            "CLAP": 3,
            "BD3": 4,
            "SD1": 5,
            "CHH": 6,
            "SD2": 7,
            "PHH": 8,
            "SD3": 9,
            "OHH": 10,
            "SD4": 11,
            "TOM1": 12,
            "PRC1": 13,
            "TOM2": 14,
            "PRC2": 15,
            "TOM3": 16,
            "PRC3": 17,
            "CYM1": 18,
            "PRC4": 19,
            "CYM2": 20,
            "PRC5": 21,
            "CYM3": 22,
            "HIT": 23,
            "OTH1": 24,
            "OTH2": 25,
        }
        self.midi_requests = DRUMS_REQUESTS
        self.midi_channel = MIDI_CHANNEL_DRUMS
        self.instrument_icon_folder = "drum_kits"
        self.default_image = "drums.png"
        # UI parameters
        self.main_window = parent
        self.partial_editors = {}
        self.partial_tab_widget = QTabWidget()

        self.image_label = None
        # Main layout
        self.controls: Dict[DrumPartialParameter, QWidget] = {}

        # Create layouts
        main_layout = QVBoxLayout(self)
        upper_layout = QHBoxLayout()
        main_layout.addLayout(upper_layout)
        self.setMinimumSize(1000, 500)
        # Title and drum kit selection
        drum_group = QGroupBox("Drum Kit")
        self.instrument_title_label = QLabel(
            f"Drum Kit:\n {DRUM_PRESETS_ENUMERATED[0]}"
            if DRUM_PRESETS_ENUMERATED
            else "Drum Kit"
        )
        drum_group.setStyleSheet(Style.JDXI_DRUM_GROUP)
        self.instrument_title_label.setStyleSheet(Style.JDXI_INSTRUMENT_TITLE_LABEL)
        drum_group_layout = QVBoxLayout()
        drum_group.setLayout(drum_group_layout)
        drum_group_layout.addWidget(self.instrument_title_label)

        # Add the "Read Request" button
        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        drum_group_layout.addWidget(self.read_request_button)

        self.selection_label = QLabel("Select address drum kit:")
        drum_group_layout.addWidget(self.selection_label)
        # Drum kit selection

        self.instrument_selection_combo = PresetComboBox(DRUM_KIT_LIST)
        self.instrument_selection_combo.combo_box.setEditable(True)  # Allow text search
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_helper.preset_number
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        # Connect QComboBox signal to PresetHandler
        self.main_window.drums_preset_helper.preset_changed.connect(
            self.update_combo_box_index
        )

        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        drum_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(drum_group)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        upper_layout.addWidget(self.image_label)

        # Common controls
        common_group = QGroupBox("Common")
        common_layout = QFormLayout()

        self.assign_type_combo = self._create_parameter_combo_box(
            DrumPartialParameter.ASSIGN_TYPE, "Assign Type", ["MULTI", "SINGLE"], [0, 1]
        )
        common_layout.addRow(self.assign_type_combo)

        # Mute Group control
        self.mute_group_combo = self._create_parameter_combo_box(
            DrumPartialParameter.MUTE_GROUP,
            "Mute Group",
            ["OFF"] + [str(i) for i in range(1, 31)],
            list(range(0, 31)),
        )

        common_layout.addRow(self.mute_group_combo)

        # Sustain control
        self.sustain_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_ENV_MODE,
            "Partial ENV Mode",
            ["SUSTAIN", "NO-SUSTAIN"],
            [0, 1],
        )

        # Kit Level control
        self.kit_level_slider = self._create_parameter_slider(
            DrumCommonParameter.KIT_LEVEL, "Kit Level"
        )
        common_layout.addRow(self.kit_level_slider)

        # Partial Pitch Bend Range
        self.pitch_bend_range_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_PITCH_BEND_RANGE, "Pitch Bend Range"
        )
        common_layout.addRow(self.pitch_bend_range_slider)

        # Partial Receive Expression
        self.receive_expression_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_RECEIVE_EXPRESSION,
            "Receive Expression",
            ["OFF", "ON"],
            [0, 1],
        )

        common_layout.addRow(self.receive_expression_combo)

        # Partial Receive Hold-1
        self.receive_hold_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_RECEIVE_HOLD_1,
            "Receive Hold-1",
            ["OFF", "ON"],
            [0, 1],
        )

        common_layout.addRow(self.receive_hold_combo)

        # One Shot Mode
        self.one_shot_mode_combo = self._create_parameter_combo_box(
            DrumPartialParameter.ONE_SHOT_MODE, "One Shot Mode", ["OFF", "ON"], [0, 1]
        )
        common_layout.addRow(self.one_shot_mode_combo)

        common_group.setLayout(common_layout)
        upper_layout.addWidget(common_group)

        # Create scroll area for partials
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)

        # Setup tab widget
        self.partial_tab_widget.setStyleSheet(Style.JDXI_TABS_DRUMS)
        scroll.setWidget(self.partial_tab_widget)

        # Initialize partial editors
        self._setup_partial_editors()

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_num)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            logging.info("MIDI helper initialized")
            if hasattr(self.midi_helper, "set_callback"):
                self.midi_helper.set_callback(self.midi_helper.midi_callback)
                logging.info("MIDI callback set")
            else:
                logging.error("MIDI set_callback method not found")
        else:
            logging.error("MIDI helper not initialized")
        self.midi_helper.update_drums_tone_name.connect(self.set_instrument_title_label)
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)
        self.data_request() # this is giving an error

    def load_preset(self, preset_index):
        """Load a preset by program change."""
        preset_name = self.instrument_selection_combo.combo_box.currentText()  # Get the selected preset name
        logging.info(f"combo box preset_name : {preset_name}")
        program_number = preset_name[:3]
        logging.info(f"combo box program_number : {program_number}")

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number, DRUM_KIT_LIST)
        lsb = get_preset_parameter_value("lsb", program_number, DRUM_KIT_LIST)
        pc = get_preset_parameter_value("pc", program_number, DRUM_KIT_LIST)

        if None in [msb, lsb, pc]:
            logging.error(f"Could not retrieve preset parameters for program {program_number}")
            return

        logging.info(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            self.midi_channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def _setup_partial_editors(self):
        """Setup all partial editors and tabs"""
        # Map of partial names to their indices

        # Create editor for each partial
        for partial_name, partial_index in self.partial_mapping.items():
            editor = DrumPartialEditor(
                midi_helper=self.midi_helper,
                partial_number=partial_index,
                partial_name=partial_name,
                parent=self,
            )
            self.partial_editors[partial_index] = editor
            self.partial_tab_widget.addTab(editor, partial_name)

    def update_partial_num(self, index: int):
        """Update the current partial number based on tab index"""
        try:
            partial_name = list(self.partial_editors.keys())[index]
            self.partial_num = index
            logging.info(f"Updated to partial {partial_name} (index {index})")
        except IndexError:
            logging.error(f"Invalid partial index: {index}")

    def _dispatch_sysex_to_area(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        # failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_data = json.loads(json_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        synth_tone = sysex_data.get("SYNTH_TONE")

        if synth_tone == "TONE_COMMON":
            logging.info("\nTone common")
            self._update_common_sliders_from_sysex(json_sysex_data)
        else:
            self._update_partial_sliders_from_sysex(json_sysex_data)

    def _update_common_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True
        failures, successes = [], []

        def _parse_sysex_json(json_data):
            """Parse JSON safely and log changes."""
            try:
                sysex_data = json.loads(json_data)
                self.previous_data = self.current_data
                self.current_data = sysex_data
                self._log_changes(self.previous_data, sysex_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to address supported digital synth area."""
            return sysex_data.get("TEMPORARY_AREA") == DRUM_KIT_AREA

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            return {"PARTIAL_1": 1, "PARTIAL_2": 2, "PARTIAL_3": 3}.get(
                synth_tone, None
            )

        def _update_common_slider(param, value):
            """Helper function to update sliders safely."""
            logging.info(f"param: {param}")
            slider = self.controls.get(param)
            logging.info(f"slider: {slider}")
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def _update_common_switch(param, value):
            """Helper function to update checkbox safely."""
            logging.info(f"checkbox param: {param} {value}")
            partial_switch_map = {
                "PARTIAL1_SWITCH": 1,
                "PARTIAL2_SWITCH": 2,
                "PARTIAL3_SWITCH": 3,
            }
            partial_number = partial_switch_map.get(param_name)
            check_box = self.partials_panel.switches.get(partial_number)
            logging.info(f"check_box: {check_box}")
            if check_box:  # and isinstance(check_box, QCheckBox):
                check_box.blockSignals(True)
                check_box.setState(bool(value), False)
                check_box.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to DRUM_KIT_AREA. \nSkipping update."
            )
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(sysex_data.get("SYNTH_TONE"))

        common_ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "SYNTH_TONE",
            "TONE_NAME",
            "TONE_NAME_1",
            "TONE_NAME_2",
            "TONE_NAME_3",
            "TONE_NAME_4",
            "TONE_NAME_5",
            "TONE_NAME_6",
            "TONE_NAME_7",
            "TONE_NAME_8",
            "TONE_NAME_9",
            "TONE_NAME_10",
            "TONE_NAME_11",
            "TONE_NAME_12",
        }
        sysex_data = {
            k: v for k, v in sysex_data.items() if k not in common_ignored_keys
        }

        if synth_tone == "TONE_COMMON":
            logging.info("\nTone common")
            for param_name, param_value in sysex_data.items():
                param = DrumCommonParameter.get_by_name(param_name)
                logging.info(f"Tone common: param_name: {param} {param_value}")
                try:
                    if param:
                        if param_name in [
                            "PARTIAL1_SWITCH",
                            "PARTIAL1_SELECT",
                            "PARTIAL2_SWITCH",
                            "PARTIAL2_SELECT",
                            "PARTIAL3_SWITCH",
                            "PARTIAL3_SELECT",
                        ]:
                            _update_common_switch(param, param_value)
                        else:
                            _update_common_slider(param, param_value)
                    else:
                        failures.append(param_name)
                except Exception as ex:
                    logging.info(f"Error {ex} occurred")

        logging.info(f"Updating sliders for Partial {partial_no}")

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")
            else:
                failures.append(param.name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                logging.info(f"successes: \t{successes}")
                logging.info(f"failures: \t{failures}")
                logging.info(f"success rate: \t{success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def _update_partial_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        try:
            sysex_data = json.loads(json_sysex_data)
            self.previous_data = self.current_data
            self.current_data = sysex_data
            self._log_changes(self.previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to address supported digital synth area."""
            return sysex_data.get("SYNTH_TONE") in self.partial_mapping

        def _get_partial_number(tone):
            """Retrieve partial number from synth tone mapping."""
            for key, value in self.partial_mapping.items():
                if key == tone:
                    return value
            return None

        if not _is_valid_sysex_area(sysex_data):
            logging.warning("SysEx data does not belong to drum area; skipping update.")
            return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = _get_partial_number(synth_tone)

        ignored_keys = {
            "JD_XI_HEADER",
            "ADDRESS",
            "TEMPORARY_AREA",
            "TONE_NAME",
            "SYNTH_TONE",
        }
        sysex_data = {k: v for k, v in sysex_data.items() if k not in ignored_keys}
        failures, successes = [], []

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                logging.info(
                    f"midi value {value} converted to slider value {slider_value}"
                )
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")

        for param_name, param_value in sysex_data.items():
            param = DrumPartialParameter.get_by_name(param_name)
            if param:
                _update_slider(param, param_value)
            else:
                failures.append(param_name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                logging.info(f"Successes: {successes}")
                logging.info(f"Failures: {failures}")
                logging.info(f"Success Rate: {success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()
