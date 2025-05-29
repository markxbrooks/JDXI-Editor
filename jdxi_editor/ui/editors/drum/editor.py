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
- `jdxi_manager.midi.data.constants.sysex.DIGITAL_SYNTH_1` for SysEx address handling.
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

from typing import Optional, Dict

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

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB
from jdxi_editor.midi.data.drum.data import JDXiMapPartialDrum
from jdxi_editor.midi.data.parameter.drum.common import AddressParameterDrumCommon
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.ui.editors.drum.common import DrumCommonSection
from jdxi_editor.ui.editors.drum.partial.editor import DrumPartialEditor
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.widgets.dialog.progress import ProgressDialog
from jdxi_editor.jdxi.preset.helper import JDXiPresetHelper


class DrumCommonEditor(SynthEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(
            self,
            midi_helper: Optional[MidiIOHelper] = None,
            preset_helper: Optional[JDXiPresetHelper] = None,
            parent: Optional[QWidget] = None,
    ):
        super().__init__(midi_helper, parent)
        # Helpers
        self.preset_helper = preset_helper
        self.midi_helper = midi_helper
        self.partial_number = 0
        self._init_synth_data(synth_type=JDXiSynth.DRUM_KIT, partial_number=0)
        self.sysex_current_data = None
        self.sysex_previous_data = None
        self.partial_mapping = JDXiMapPartialDrum.MAP
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
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_control_changed.connect(self._handle_control_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        # Request initial state data & show the editor
        self.data_request()
        # self.show()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.setMinimumSize(1100, 500)

        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)  # No padding around the layout

        instrument_preset_group = self._create_instrument_preset_group(
            synth_type="Drums"
        )
        upper_layout.addWidget(instrument_preset_group)
        self._create_instrument_image_group()
        self.address.lmb = AddressOffsetProgramLMB.COMMON
        kit_level_slider = self._create_parameter_slider(
            AddressParameterDrumCommon.KIT_LEVEL, "Kit Level", vertical=True
        )
        kit_level_slider.setStyleSheet(JDXiStyle.SLIDER_VERTICAL)
        upper_layout.addWidget(kit_level_slider)
        upper_layout.addWidget(self.instrument_image_group)
        self.instrument_image_group.setMinimumWidth(JDXiStyle.INSTRUMENT_IMAGE_WIDTH)
        self.update_instrument_image()


        """
        common_group = DrumCommonSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
            address=self.address
        )
        common_group.setContentsMargins(0, 0, 0, 0)  # No padding around the layout
        upper_layout.addWidget(common_group)
        """

        splitter.addWidget(upper_widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.partial_tab_widget.setStyleSheet(JDXiStyle.TABS_DRUMS)
        scroll.setWidget(self.partial_tab_widget)
        splitter.addWidget(scroll)

        splitter.setSizes([300, 300])
        splitter.setStyleSheet(JDXiStyle.SPLITTER)
        self.partial_tab_widget.setStyleSheet(JDXiStyle.TABS_DRUMS)
        self._setup_partial_editors()

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_number)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Register the callback for incoming MIDI messages
        self.data_request()

    def _handle_program_change(self, channel: int, program: int):
        """
        Handle program change messages by requesting updated data
        :param channel: int
        :param program: int
        """
        log.message(
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
            progress_dialog.progress_bar.setFormat(
                f"Loading {partial_name} ({count} of {total})"
            )
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
            log.message(f"Updated to partial {partial_name} (index {index})")
        except IndexError:
            log.message(f"Invalid partial index: {index}")

    def _update_partial_controls(self, partial_no: int, sysex_data: dict, successes: list, failures: list) -> None:
        """
        apply partial ui updates
        :param partial_no: int
        :param sysex_data: dict
        :param successes: list
        :param failures: list
        :return:
        """

        for param_name, param_value in sysex_data.items():
            param = AddressParameterDrumPartial.get_by_name(param_name)
            if param:
                self._update_partial_slider(partial_no, param, param_value, successes, failures)
            else:
                failures.append(param_name)

    def _update_common_controls(
        self,
        partial: int,
        sysex_data: Dict,
        successes: list = None,
        failures: list = None,
    ):
        """
        Update the UI components for tone common and modify parameters.
        :param partial: int
        :param sysex_data: Dictionary containing SysEx data
        :param successes: List of successful parameters
        :param failures: List of failed parameters
        :return: None
        """
        log.header_message("Tone common")
        for param_name, param_value in sysex_data.items():
            param = AddressParameterDrumCommon.get_by_name(param_name)
            log.message(f"Tone common: param_name: {param} {param_value}")
            try:
                if param:
                    self._update_slider(param, param_value)
                else:
                    failures.append(param_name)
            except Exception as ex:
                log.error(f"Error {ex} occurred")

        log.debug_info(successes, failures)
