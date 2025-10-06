jdxi_editor.ui.editors.drum.editor
==================================

.. py:module:: jdxi_editor.ui.editors.drum.editor

.. autoapi-nested-parse::

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



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.drum.editor.DrumCommonEditor


Module Contents
---------------

.. py:class:: DrumCommonEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: Optional[jdxi_editor.jdxi.preset.helper.JDXiPresetHelper] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.editor.SynthEditor`


   Editor for JD-Xi Drum Kit parameters


   .. py:attribute:: presets_parts_tab_widget
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: partial_number
      :value: 0



   .. py:attribute:: sysex_current_data
      :value: None



   .. py:attribute:: sysex_previous_data
      :value: None



   .. py:attribute:: partial_mapping


   .. py:attribute:: main_window
      :value: None



   .. py:attribute:: partial_editors


   .. py:attribute:: partial_tab_widget


   .. py:attribute:: instrument_image_label
      :value: None



   .. py:attribute:: instrument_title_label
      :value: None



   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial, PySide6.QtWidgets.QWidget]


   .. py:attribute:: refresh_shortcut


   .. py:method:: setup_ui()


   .. py:method:: _handle_program_change(channel: int, program: int)

      Handle program change messages by requesting updated data

      :param channel: int
      :param program: int



   .. py:method:: _setup_partial_editors()

      Setup the 36 partial editors



   .. py:method:: update_partial_number(index: int)

      Update the current partial number based on tab index

      :param index: int partial number



   .. py:method:: _update_partial_controls(partial_no: int, sysex_data: dict, successes: list, failures: list) -> None

      apply partial ui updates

      :param partial_no: int
      :param sysex_data: dict
      :param successes: list
      :param failures: list
      :return:



   .. py:method:: _update_common_controls(partial: int, sysex_data: Dict, successes: list = None, failures: list = None)

      Update the UI components for tone common and modify parameters.

      :param partial: int
      :param sysex_data: Dictionary containing SysEx data
      :param successes: List of successful parameters
      :param failures: List of failed parameters
      :return: None



