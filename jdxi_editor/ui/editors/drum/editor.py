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

from typing import Dict, Optional, Union

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QGroupBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB
from jdxi_editor.midi.data.drum.data import JDXiMapPartialDrum
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.common import DrumCommonSection
from jdxi_editor.ui.editors.drum.partial.editor import DrumPartialEditor
from jdxi_editor.ui.editors.synth.editor import SynthEditor
from jdxi_editor.ui.preset.helper import JDXiPresetHelper
from jdxi_editor.ui.preset.widget import InstrumentPresetWidget
from jdxi_editor.ui.widgets.dialog.progress import ProgressDialog
from jdxi_editor.ui.widgets.editor.base import EditorBaseWidget


class DrumCommonEditor(SynthEditor):
    """Editor for JD-Xi Drum Kit parameters"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        preset_helper: Optional[JDXiPresetHelper] = None,
        parent: Optional["JDXiInstrument"] = None,
    ):
        super().__init__(midi_helper, parent)
        # Helpers
        self.instrument_image_group: QGroupBox | None = None
        self.presets_parts_tab_widget = None
        self.preset_helper = preset_helper
        self.midi_helper = midi_helper
        self.partial_number = 0
        self._init_synth_data(synth_type=JDXi.Synth.DRUM_KIT, partial_number=0)
        self.sysex_current_data = None
        self.sysex_previous_data = None
        self.partial_mapping = JDXiMapPartialDrum.MAP
        # UI Elements
        self.main_window = parent
        self.partial_editors = {}
        self.partial_tab_widget = QTabWidget()
        self.instrument_image_label = None
        self.instrument_title_label = None
        self.controls: Dict[Union[DrumPartialParam, DrumCommonParam], QWidget] = {}
        self.setup_ui()
        self.update_instrument_image()
        # Setup signal handlers
        if self.midi_helper:
            self.midi_helper.midi_program_changed.connect(self._handle_program_change)
            self.midi_helper.midi_control_changed.connect(self._handle_control_change)
            self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        self.refresh_shortcut = QShortcut(QKeySequence.StandardKey.Refresh, self)
        self.refresh_shortcut.activated.connect(self.data_request)
        # Note: data_request() is called in showEvent() when editor is displayed

    def setup_ui(self) -> None:
        """Setup the UI components for the drum editor."""
        main_layout = QVBoxLayout(self)
        self.setMinimumSize(
            JDXi.UI.Dimensions.EDITOR_DRUM.WIDTH, JDXi.UI.Dimensions.EDITOR_DRUM.HEIGHT
        )
        self.presets_parts_tab_widget = QTabWidget()

        main_layout.addWidget(self.presets_parts_tab_widget)

        instrument_widget = QWidget()
        instrument_vrow_layout = QVBoxLayout(instrument_widget)

        # Use InstrumentPresetWidget for consistent layout
        self.instrument_preset = InstrumentPresetWidget(parent=self)
        self.instrument_preset.setup_header_layout()
        self.instrument_preset.setup()

        instrument_preset_group = self.instrument_preset.create_instrument_preset_group(
            synth_type="Drums"
        )
        self.instrument_preset.add_preset_group(instrument_preset_group)
        self.instrument_preset.add_stretch()

        (
            self.instrument_image_group,
            self.instrument_image_label,
            self.instrument_group_layout,
        ) = self.instrument_preset.create_instrument_image_group()
        self.address.lmb = AddressOffsetProgramLMB.COMMON
        self.instrument_image_group.setMinimumWidth(
            JDXi.UI.Style.INSTRUMENT_IMAGE_WIDTH
        )
        self.instrument_preset.add_image_group(self.instrument_image_group)
        self.instrument_preset.add_stretch()
        self.update_instrument_image()

        instrument_vrow_layout.addWidget(self.instrument_preset)

        drum_kit_presets_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.MUSIC_NOTES, color=JDXi.UI.Style.GREY
        )
        self.presets_parts_tab_widget.addTab(
            instrument_widget, drum_kit_presets_icon, "Drum Kit Presets"
        )

        # --- Use EditorBaseWidget for consistent scrollable layout structure
        self.base_widget = EditorBaseWidget(parent=self, analog=False)
        self.base_widget.setup_scrollable_content()
        container_layout = self.base_widget.get_container_layout()

        # Add partial_tab_widget to the container
        self.partial_tab_widget.setStyleSheet(JDXi.UI.Style.TABS_DRUMS)
        container_layout.addWidget(self.partial_tab_widget)

        # Add the base widget as the second tab (it contains the scroll area)
        drum_kit_parts_icon = JDXi.UI.Icon.get_icon(
            "mdi.puzzle", color=JDXi.UI.Style.GREY
        )
        self.presets_parts_tab_widget.addTab(
            self.base_widget, drum_kit_parts_icon, "Drum Kit Parts"
        )

        self.presets_parts_tab_widget.setStyleSheet(JDXi.UI.Style.TABS_DRUMS)
        self.partial_tab_widget.setStyleSheet(JDXi.UI.Style.TABS_DRUMS)
        self._setup_partial_editors()
        # Create and add the common section
        self.common_section = DrumCommonSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
            address=self.address,
        )
        common_icon = JDXi.UI.Icon.get_icon("mdi.cog-outline", color=JDXi.UI.Style.GREY)
        self.partial_tab_widget.addTab(self.common_section, common_icon, "Common")

        # Create and add the mixer tab
        from jdxi_editor.ui.editors.drum.mixer import DrumKitMixer

        mixer_widget = DrumKitMixer(midi_helper=self.midi_helper, parent=self)
        mixer_icon = JDXi.UI.Icon.get_icon("ei.adjust-alt", color=JDXi.UI.Style.GREY)
        if mixer_icon is None or mixer_icon.isNull():
            # Fallback icon if mixer icon not available
            mixer_icon = JDXi.UI.Icon.get_icon(
                "ph.sliders-bold", color=JDXi.UI.Style.GREY
            )
        self.presets_parts_tab_widget.addTab(mixer_widget, mixer_icon, "Drum Kit Mixer")

        self.update_instrument_image()
        self.partial_tab_widget.currentChanged.connect(self.update_partial_number)
        self.midi_helper.midi_sysex_json.connect(self._dispatch_sysex_to_area)
        # Note: data_request() is called in showEvent() when editor is displayed

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

        # Use splash screen if available, otherwise fall back to ProgressDialog
        splash = None
        splash_progress = None
        splash_status = None
        if (
            self.main_window
            and hasattr(self.main_window, "splash")
            and self.main_window.splash
        ):
            splash = self.main_window.splash
            splash_progress = self.main_window.splash_progress_bar
            splash_status = self.main_window.splash_status_label

        if splash and splash_progress and splash_status:
            # Update splash screen
            splash_status.setText(f"Loading drum kit parts ({total} parts)...")
            splash_progress.setValue(60)  # Start at 60% for drum kit loading
            from PySide6.QtWidgets import QApplication

            QApplication.processEvents()
        else:
            # Fall back to ProgressDialog if splash screen not available
            progress_dialog = ProgressDialog(
                "Initializing Editor Window", "Loading drum kit:...", total, self
            )
            progress_dialog.show()

        for count, (partial_name, partial_number) in enumerate(
            self.partial_mapping.items(), 1
        ):
            if splash and splash_progress and splash_status:
                # Update splash screen
                splash_status.setText(f"Loading {partial_name} ({count} of {total})")
                # Progress from 60% to 90% for drum kit loading
                progress_value = 60 + int((count / total) * 30)
                splash_progress.setValue(progress_value)
                from PySide6.QtWidgets import QApplication

                QApplication.processEvents()
            elif not splash:
                # Use ProgressDialog
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

            if not splash:
                progress_dialog.update_progress(count)

        if not splash:
            progress_dialog.close()
        elif splash_progress:
            # Complete drum kit loading
            splash_progress.setValue(90)
            splash_status.setText("Drum kit loaded successfully")
            from PySide6.QtWidgets import QApplication

            QApplication.processEvents()

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

    def _update_partial_controls(
        self, partial_no: int, sysex_data: dict, successes: list, failures: list
    ) -> None:
        """
        apply partial ui updates

        :param partial_no: int
        :param sysex_data: dict
        :param successes: list
        :param failures: list
        :return:
        """

        for param_name, param_value in sysex_data.items():
            param = DrumPartialParam.get_by_name(param_name)
            if param:
                self._update_partial_slider(
                    partial_no, param, param_value, successes, failures
                )
            else:
                failures.append(param_name)

    def _update_common_controls(
        self,
        partial: int,  # pylint: disable=unused-argument
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
            param = DrumCommonParam.get_by_name(param_name)
            log.message(f"Tone common: param_name: {param} {param_value}")
            try:
                if param:
                    self._update_slider(param, param_value)
                else:
                    failures.append(param_name)
            except Exception as ex:
                log.error(f"Error {ex} occurred")

        log.debug_info(successes, failures)
