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

import logging
from typing import Optional, Dict
import json

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QWidget,
    QTabWidget,
    QSplitter,
)
from PySide6.QtCore import Qt

from jdxi_editor.log.error import log_error
from jdxi_editor.log.footer import log_footer_message
from jdxi_editor.log.header import log_header_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB
from jdxi_editor.midi.data.drum.data import DRUM_PARTIAL_MAPPING
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.ui.editors.drum.common import DrumCommonSection
from jdxi_editor.ui.editors.drum.partial.editor import DrumPartialEditor
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.editors.synth.editor import SynthEditor, log_changes
from jdxi_editor.ui.widgets.dialog.progress import ProgressDialog
from jdxi_editor.jdxi.preset.helper import JDXIPresetHelper


class DrumCommonEditor(SynthEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: Optional[JDXIPresetHelper] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper, parent)
        # Helpers
        self.preset_helper = preset_helper
        self.midi_helper = midi_helper
        self.midi_helper.midi_program_changed.connect(self._handle_program_change)
        self.partial_number = 0
        self._init_synth_data(synth_type=JDXISynth.DRUM)
        self.sysex_current_data = None
        self.sysex_previous_data = None
        self.partial_mapping = DRUM_PARTIAL_MAPPING
        # UI Elements
        self.main_window = parent
        self.partial_editors = {}
        self.partial_tab_widget = QTabWidget()
        self.instrument_image_label = None
        self.controls: Dict[AddressParameterDrumPartial, QWidget] = {}
        self.setup_ui()
        self.update_instrument_image()
        # Setup signal handlers
        if self.midi_helper:
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        # Request initial state data & show the editor
        self.data_request()
        self.show()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        self.setMinimumSize(1100, 500)

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        # === Top half: upper_layout container ===
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)  # No padding around the layout

        instrument_preset_group = self._create_instrument_preset_group(synth_type="Drums")
        upper_layout.addWidget(instrument_preset_group)
        self._create_instrument_image_group()
        upper_layout.addWidget(self.instrument_image_group)
        self.update_instrument_image()

        # Common section
        common_group = DrumCommonSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper
        )
        common_group.setContentsMargins(0, 0, 0, 0)  # No padding around the layout
        upper_layout.addWidget(common_group)

        # Add upper half to splitter
        splitter.addWidget(upper_widget)

        # === Bottom half: scrollable tab widget ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.partial_tab_widget.setStyleSheet(JDXIStyle.TABS_DRUMS)
        scroll.setWidget(self.partial_tab_widget)
        splitter.addWidget(scroll)

        # Optionally set initial sizes
        splitter.setSizes([300, 300])
        splitter.setStyleSheet(JDXIStyle.SPLITTER)
        # Setup tab widget
        self.partial_tab_widget.setStyleSheet(JDXIStyle.TABS_DRUMS)
        # Initialize partial editors
        self._setup_partial_editors()

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_number)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Register the callback for incoming MIDI messages
        self.data_request()  # this is giving an error

    def _handle_program_change(self, channel: int, program: int):
        """
        Handle program change messages by requesting updated data
        :param channel: int
        :param program: int
        """
        log_message(
            f"Program change {program} detected on channel {channel}, requesting data update"
        )
        self.data_request(channel, program)

    def _setup_partial_editors(self):
        """
        Setup the 36 partial editors
        """
        total = len(self.partial_mapping)
        progress_dialog = ProgressDialog(
            "Initializing Partials", "Loading drum kit:...", total, self
        )
        progress_dialog.show()

        for count, (partial_name, partial_number) in enumerate(
            self.partial_mapping.items(), 1
        ):
            progress_dialog.progress_bar.setFormat(f"Loading {partial_name} ({count} of {total})")
            editor = DrumPartialEditor(
                midi_helper=self.midi_helper,
                partial_number=partial_number,
                partial_name=partial_name,
                parent=self,
            )
            self.partial_editors[partial_number] = editor
            self.partial_tab_widget.addTab(editor, partial_name)

            progress_dialog.update_progress(count)

        progress_dialog.close()

    def update_partial_number(self, index: int):
        """
        Update the current partial number based on tab index
        :param index: int partial number
        """
        try:
            partial_name = list(self.partial_editors.keys())[index]
            self.partial_number = index
            log_message(f"Updated to partial {partial_name} (index {index})")
        except IndexError:
            log_message(f"Invalid partial index: {index}")

    def _on_parameter_received(self, address: int, value: int):
        """
        FIXME: to implement
        :param address: int
        :param value: int
        """
        pass

    def _dispatch_sysex_to_area(self, json_sysex_data: str):
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        """
        log_message("\n============================================================================================")
        log_message("Updating UI components from SysEx data")
        log_message("\n============================================================================================")

        # failures, successes = [], []

        def _parse_sysex_json(json_data):
            """
            Parse JSON safely and log changes.
            :param json_data: str
            :return: dict
            """
            try:
                sysex_data = json.loads(json_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                log_message(f"Invalid JSON format: {ex}")
                return None

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        synth_tone = sysex_data.get("SYNTH_TONE")

        if synth_tone == "TONE_COMMON":
            log_message("Tone common")
            self._update_common_sliders_from_sysex(json_sysex_data)
        else:
            self._update_partial_sliders_from_sysex(json_sysex_data)

    def _update_common_sliders_from_sysex(self, json_sysex_data: str):
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        """
        log_message("\n============================================================================================")
        log_message("Updating UI components from SysEx data")
        log_message("\n============================================================================================")
        debug_param_updates = True
        debug_stats = True
        failures, successes = [], []

        def _parse_sysex_json(json_data: str):
            """
            Parse JSON safely and log changes.
            :param json_data: str
            :return: dict
            """
            try:
                sysex_json_data = json.loads(json_data)
                self.sysex_previous_data = self.sysex_current_data
                self.sysex_current_data = sysex_json_data
                log_changes(self.sysex_previous_data, sysex_json_data)
                return sysex_json_data
            except json.JSONDecodeError as ex:
                log_message(f"Invalid JSON format: {ex}")
                return None

        def _is_valid_sysex_area(sysex_json_data: dict):
            """
            Check if SysEx data belongs to address supported digital synth area.
            :param sysex_json_data: dict
            :return: bool
            """
            return (
                    sysex_json_data.get("TEMPORARY_AREA")
                    == AddressOffsetTemporaryToneUMB.DRUM_KIT_PART
            )

        def _get_partial_number(synth_tone_name: str) -> Optional[int]:
            """
            Retrieve partial number from synth tone mapping.
            :param synth_tone_name: str
            :return: int
            """
            return {"PARTIAL_1": 1, "PARTIAL_2": 2, "PARTIAL_3": 3}.get(
                synth_tone_name, None
            )

        def _update_common_slider(parameter: AddressParameterDrumCommon, value: int) -> None:
            """
            Helper function to update sliders safely.
            :param parameter: AddressParameterDrumCommon
            :param value: int
            :return: None
            """
            log_parameter("parameter", parameter)
            slider = self.controls.get(parameter)
            log_parameter("slider", slider)
            if slider:
                slider.blockSignals(True)
                slider.setValue(value)
                slider.blockSignals(False)
                successes.append(parameter.name)
                if debug_param_updates:
                    log_message("Updated parameter: ")
                    log_parameter("parameter", parameter)
                    log_parameter("value", value)
            else:
                failures.append(parameter.name)

        def _update_common_switch(parameter: AddressParameterDrumCommon, value: int) -> None:
            """
            Helper function to update checkbox safely.
            :param parameter: AddressParameterDrumCommon
            :param value: int
            :return: None
            """
            log_message("Checkbox parameter: ")
            log_parameter("parameter", parameter)
            log_parameter("value", value)
            partial_switch_map = {
                "PARTIAL1_SWITCH": 1,
                "PARTIAL2_SWITCH": 2,
                "PARTIAL3_SWITCH": 3,
            }
            partial_number = partial_switch_map.get(param_name)
            check_box = self.partials_panel.switches.get(partial_number)
            log_message(f"check_box: {check_box}")
            if check_box:  # and isinstance(check_box, QCheckBox):
                check_box.blockSignals(True)
                check_box.setState(bool(value), False)
                check_box.blockSignals(False)
                successes.append(parameter.name)
                if debug_param_updates:
                    log_message("Updated parameter: ")
                    log_parameter("parameter", parameter)
                    log_parameter("value", value)
            else:
                failures.append(parameter.name)

        # Parse SysEx data
        sysex_data = _parse_sysex_json(json_sysex_data)
        if not sysex_data:
            return

        if not _is_valid_sysex_area(sysex_data):
            logging.warning(
                "SysEx data does not belong to DRUM_KIT_AREA, Skipping update."
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
            log_message("\nTone common")
            for param_name, param_value in sysex_data.items():
                param = AddressParameterDrumCommon.get_by_name(param_name)
                log_message(f"Tone common: param_name: {param} {param_value}")
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
                    log_error(f"Error {ex} occurred")

        log_message(f"Updating sliders for Partial {partial_no}")

        def _log_debug_info():
            """
            Helper function to log debugging statistics.
            """
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                log_message(f"successes: \t{successes}")
                log_message(f"failures: \t{failures}")
                log_footer_message(f"success rate: \t{success_rate:.1f}%")
        _log_debug_info()

    def _update_partial_sliders_from_sysex(self, json_sysex_data: str):
        """
        Update sliders and combo boxes based on parsed SysEx data.
        :param json_sysex_data: str
        """
        log_header_message("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        try:
            sysex_data = json.loads(json_sysex_data)
            self.sysex_previous_data = self.sysex_current_data
            self.sysex_current_data = sysex_data
            log_changes(self.sysex_previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            log_message(f"Invalid JSON format: {ex}")
            return

        def _is_valid_sysex_area(sysex_data_dict: dict):
            """
            Check if SysEx data belongs to address supported digital synth area.
            :param sysex_data_dict: dict
            :return: bool
            """
            return sysex_data_dict.get("SYNTH_TONE") in self.partial_mapping

        def _get_partial_number(tone: str):
            """
            Retrieve partial number from synth tone mapping.
            :param tone: str
            :return: int
            """
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

        def _update_slider(param: AddressParameterDrumPartial, value: int):
            """
            Helper function to update sliders safely.
            :param param: AddressParameterDrumPartial
            :param value: int
            """
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                log_message(
                    f"midi value {value} converted to slider value {slider_value}"
                )
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    log_message(f"Updated: {param.name:50} {value}")

        for param_name, param_value in sysex_data.items():
            param = AddressParameterDrumPartial.get_by_name(param_name)
            if param:
                _update_slider(param, param_value)
            else:
                failures.append(param_name)

        def _log_debug_info():
            """
            Helper function to log debugging statistics.
            """
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                log_message("\n======================================================================================================")
                log_message(f"Successes: \t{successes}")
                log_message(f"Failures: \t{failures}")
                log_message(f"Success Rate: \t{success_rate:.1f}%")
                log_message("\n======================================================================================================")

        _log_debug_info()
