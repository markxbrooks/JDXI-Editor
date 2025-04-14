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
    QLabel,
    QGroupBox,
    QScrollArea,
    QWidget,
    QTabWidget,
    QPushButton, QSplitter,
)
from PySide6.QtCore import Qt

from jdxi_editor.midi.data.address.address import AddressOffsetTemporaryToneUMB
from jdxi_editor.midi.data.editor.data import DrumSynthData
from jdxi_editor.midi.data.editor.drum import DRUM_PARTIAL_MAPPING
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParameter
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParameter
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.ui.editors.drum.common import DrumCommonSection
from jdxi_editor.ui.editors.drum.partial import DrumPartialEditor
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.ui.editors.synth.editor import SynthEditor, log_changes
from jdxi_editor.ui.widgets.dialog.progress import ProgressDialog
from jdxi_editor.ui.widgets.display.digital import DigitalTitle
from jdxi_editor.ui.widgets.preset.combo_box import PresetComboBox


class DrumCommonEditor(SynthEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper=None,
        parent=None,
    ):
        super().__init__(midi_helper, parent)

        # Initialize class attributes

        # Presets
        self.preset_helper = preset_helper
        # midi parameters
        self.partial_number = 0
        self._init_synth_data()

        self.current_data = None
        self.previous_data = None

        self.partial_mapping = DRUM_PARTIAL_MAPPING

        # UI parameters
        self.main_window = parent
        self.partial_editors = {}
        self.partial_tab_widget = QTabWidget()

        self.instrument_image_label = None
        # Main layout
        self.controls: Dict[DrumPartialParameter, QWidget] = {}
        self.setup_ui()
        self.update_instrument_image()
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
            self.midi_helper.update_drums_tone_name.connect(
                self.set_instrument_title_label
            )
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
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

        # Drum group
        drum_group = QGroupBox("Drum Kit")
        self.instrument_title_label = DigitalTitle()
        drum_group.setStyleSheet(JDXIStyle.DRUM_GROUP)
        self.instrument_title_label.setStyleSheet(JDXIStyle.INSTRUMENT_TITLE_LABEL)
        drum_group_layout = QVBoxLayout()
        drum_group.setLayout(drum_group_layout)
        drum_group_layout.addWidget(self.instrument_title_label)

        self.read_request_button = QPushButton("Send Read Request to Synth")
        self.read_request_button.clicked.connect(self.data_request)
        drum_group_layout.addWidget(self.read_request_button)

        self.selection_label = QLabel("Select address drum kit:")
        drum_group_layout.addWidget(self.selection_label)

        self.instrument_selection_combo = PresetComboBox(DRUM_KIT_LIST)
        self.instrument_selection_combo.combo_box.setEditable(True)
        self.instrument_selection_combo.combo_box.setCurrentIndex(
            self.preset_helper.preset_number
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_image
        )
        self.instrument_selection_combo.load_button.clicked.connect(
            self.update_instrument_preset
        )
        self.main_window.drums_preset_helper.preset_changed.connect(
            self.update_combo_box_index
        )
        self.instrument_selection_combo.combo_box.currentIndexChanged.connect(
            self.update_instrument_title
        )
        drum_group_layout.addWidget(self.instrument_selection_combo)
        upper_layout.addWidget(drum_group)

        # Image group
        self.instrument_image_group = QGroupBox()
        instrument_group_layout = QVBoxLayout()
        self.instrument_image_group.setLayout(instrument_group_layout)
        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instrument_group_layout.addWidget(self.instrument_image_label)
        self.instrument_image_group.setStyleSheet(JDXIStyle.INSTRUMENT_IMAGE_LABEL)
        self.instrument_image_group.setMinimumWidth(350)
        upper_layout.addWidget(self.instrument_image_group)

        # Common section
        common_group = DrumCommonSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper
        )
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
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #444;
                border: 1px solid #666;
            }
            QSplitter::handle:vertical {
                height: 6px;
            }
            QSplitter::handle:horizontal {
                width: 6px;
            }
        """)
        # Setup tab widget
        self.partial_tab_widget.setStyleSheet(JDXIStyle.TABS_DRUMS)
        # scroll.setWidget(self.partial_tab_widget)

        # Initialize partial editors
        self._setup_partial_editors()

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_number)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            logging.info("MIDI helper initialized")
        else:
            logging.error("MIDI helper not initialized")
        self.midi_helper.update_drums_tone_name.connect(self.set_instrument_title_label)
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)
        self.data_request()  # this is giving an error

    def setup_ui_old(self):
        # Create layouts
        main_layout = QVBoxLayout(self)
        upper_layout = QHBoxLayout()
        main_layout.addLayout(upper_layout)
        self.setMinimumSize(1100, 500)
        # Title and drum kit selection
        drum_group = QGroupBox("Drum Kit")
        self.instrument_title_label = DigitalTitle()
        drum_group.setStyleSheet(JDXIStyle.DRUM_GROUP)
        self.instrument_title_label.setStyleSheet(JDXIStyle.INSTRUMENT_TITLE_LABEL)
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
        self.instrument_image_group = QGroupBox()
        instrument_group_layout = QVBoxLayout()
        self.instrument_image_group.setLayout(instrument_group_layout)
        self.instrument_image_label = QLabel()
        self.instrument_image_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center align the image
        instrument_group_layout.addWidget(self.instrument_image_label)
        self.instrument_image_group.setStyleSheet(JDXIStyle.INSTRUMENT_IMAGE_LABEL)
        self.instrument_image_group.setMinimumWidth(350)
        upper_layout.addWidget(self.instrument_image_group)

        common_group = DrumCommonSection(
            self.controls,
            self._create_parameter_combo_box,
            self._create_parameter_slider,
            self.midi_helper,
        )
        upper_layout.addWidget(common_group)

        # Create scroll area for partials
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)

        # Setup tab widget
        self.partial_tab_widget.setStyleSheet(JDXIStyle.TABS_DRUMS)
        scroll.setWidget(self.partial_tab_widget)

        # Initialize partial editors
        self._setup_partial_editors()

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_number)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Register the callback for incoming MIDI messages
        if self.midi_helper:
            logging.info("MIDI helper initialized")
        else:
            logging.error("MIDI helper not initialized")
        self.midi_helper.update_drums_tone_name.connect(self.set_instrument_title_label)
        self.instrument_selection_combo.preset_loaded.connect(self.load_preset)
        self.data_request()  # this is giving an error

    def _init_synth_data(self):
        """Initialize synth-specific data."""
        self.synth_data = DrumSynthData(partial_number=0)
        data = self.synth_data
        logging.info(self.synth_data)
        self.address_msb = data.address_msb
        self.address_umb = data.address_umb
        self.address_lmb = data.address_lmb
        self.setWindowTitle(data.window_title)
        self.preset_type = data.preset_type
        self.instrument_default_image = data.instrument_default_image
        self.instrument_icon_folder = data.instrument_icon_folder
        self.presets = data.presets
        self.preset_list = data.preset_list
        self.midi_requests = data.midi_requests
        self.midi_channel = data.midi_channel

    def _setup_partial_editors(self):
        total = len(self.partial_mapping)
        progress_dialog = ProgressDialog(
            "Initializing Partials", "Loading partial editors...", total, self
        )
        progress_dialog.show()

        for count, (partial_name, partial_number) in enumerate(
            self.partial_mapping.items(), 1
        ):
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
        """Update the current partial number based on tab index"""
        try:
            partial_name = list(self.partial_editors.keys())[index]
            self.partial_number = index
            logging.info(f"Updated to partial {partial_name} (index {index})")
            self.update_partial_address()
        except IndexError:
            logging.error(f"Invalid partial index: {index}")

    def _on_parameter_received(self, address, value):
        """Fixme: to implement"""
        pass

    def update_partial_address(self):
        """ update partial address from synth data """
        self.address_lmb = self.synth_data.get_partial_lmb(self.partial_number)

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
                log_changes(self.previous_data, sysex_data)
                return sysex_data
            except json.JSONDecodeError as ex:
                logging.error(f"Invalid JSON format: {ex}")
                return None

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to address supported digital synth area."""
            return (
                sysex_data.get("TEMPORARY_AREA")
                == AddressOffsetTemporaryToneUMB.DRUM_KIT_PART
            )

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
            log_changes(self.previous_data, sysex_data)
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
