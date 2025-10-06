jdxi_editor.ui.editors.synth.editor
===================================

.. py:module:: jdxi_editor.ui.editors.synth.editor

.. autoapi-nested-parse::

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



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.synth.editor.SynthEditor


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.editors.synth.editor.log_changes


Module Contents
---------------

.. py:function:: log_changes(previous_data, current_data)

   Log changes between previous and current JSON data.


.. py:class:: SynthEditor(midi_helper: Optional[object] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.base.SynthBase`


   Base class for all editor windows


   .. py:attribute:: parameter_received


   .. py:attribute:: partial_map


   .. py:attribute:: sysex_current_data
      :value: None



   .. py:attribute:: preset_list
      :value: None



   .. py:attribute:: programs
      :value: None



   .. py:attribute:: midi_helper


   .. py:attribute:: cc_parameters


   .. py:attribute:: nrpn_parameters


   .. py:attribute:: nrpn_map


   .. py:attribute:: controls


   .. py:attribute:: bipolar_parameters
      :value: []



   .. py:attribute:: midi_requests
      :value: []



   .. py:attribute:: instrument_default_image
      :value: None



   .. py:attribute:: instrument_title_label
      :value: None



   .. py:attribute:: instrument_image_label
      :value: None



   .. py:attribute:: instrument_icon_folder
      :value: None



   .. py:attribute:: partial_number
      :value: None



   .. py:attribute:: midi_channel
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: instrument_selection_combo
      :value: None



   .. py:attribute:: preset_type
      :value: None



   .. py:attribute:: refresh_shortcut


   .. py:attribute:: close_shortcut


   .. py:attribute:: json_parser


   .. py:method:: __str__()


   .. py:method:: __repr__()


   .. py:method:: _init_synth_data(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth = JDXiSynth.DIGITAL_SYNTH_1, partial_number: Optional[int] = 0)

      Initialize synth-specific data.



   .. py:method:: _create_instrument_image_group()


   .. py:method:: _create_instrument_preset_group(synth_type: str = 'Analog') -> PySide6.QtWidgets.QGroupBox

      Create the instrument preset group box.

      :param synth_type: str
      :return: QGroupBox



   .. py:method:: get_controls_as_dict()

      Get the current values of self.controls as a dictionary.

      :returns: dict A dictionary of control parameter names and their values.



   .. py:method:: _get_preset_helper_for_current_synth()

      Return the appropriate preset handler based on the current synth preset_type.



   .. py:method:: _dispatch_sysex_to_area(json_sysex_data: str) -> None

      Dispatch SysEx data to the appropriate area for processing.

      :param json_sysex_data:
      :return: None



   .. py:method:: _update_partial_controls(partial_no: int, sysex_data: dict, successes: list, failures: list) -> None
      :abstractmethod:


      Apply updates to the UI components based on the received SysEx data.

      :param partial_no: int
      :param sysex_data: dict
      :param successes: list
      :param failures: list
      :return: None
      By default has no partials, so subclass to implement partial updates



   .. py:method:: _parse_sysex_json(json_sysex_data: str) -> Optional[dict]

      _parse_sysex_json

      :param json_sysex_data: str
      :return: dict



   .. py:method:: set_instrument_title_label(name: str, synth_type: str)

      set_instrument_title_label

      :param name: str
      :param synth_type: str
      :return: None



   .. py:method:: update_combo_box_index(preset_number)

      Updates the QComboBox to reflect the loaded preset.



   .. py:method:: update_instrument_title()

      update instrument title

      :return:



   .. py:method:: update_instrument_preset(text)


   .. py:method:: load_preset(preset_index)

      Load a preset by program change.



   .. py:method:: _handle_program_change(channel: int, program: int)

      Handle program change messages by requesting updated data



   .. py:method:: _handle_control_change(channel: int, control: int, value: int)

      Handle program change messages by requesting updated data



   .. py:method:: send_control_change(control_change: jdxi_editor.midi.data.control_change.base.ControlChange, value: int)

      Send MIDI CC message



   .. py:method:: load_and_set_image(image_path, secondary_image_path=None)

      Helper function to load and set the image on the label.



   .. py:method:: update_instrument_image()

      Update the instrument image based on the selected synth.



   .. py:method:: _get_selected_instrument_text() -> str


   .. py:method:: _parse_instrument_text(text: str) -> tuple


   .. py:method:: _try_load_specific_or_generic_image(name: str, type_: str) -> bool


   .. py:method:: _fallback_to_default_image(reason: str)


   .. py:method:: update_instrument_image_new()

      Update the instrument image based on the selected synth.



   .. py:method:: update_instrument_image_old()

      Update the instrument image based on the selected synth.



   .. py:method:: _update_common_controls(partial_number: int, filtered_data, successes, failures)


   .. py:method:: _update_modify_controls(partial_number: int, filtered_data, successes, failures)


