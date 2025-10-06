jdxi_editor.ui.editors.digital.editor
=====================================

.. py:module:: jdxi_editor.ui.editors.digital.editor

.. autoapi-nested-parse::

   Digital Synth Editor for the Roland JD-Xi.

   This module provides the UI components for editing digital synth parameters on the Roland JD-Xi.
   The editor supports three partials (voices) with individual parameter control and common parameters
   that affect all partials.

   Classes:
       DigitalSynthEditor: Main editor class for digital synth parameters
           - Handles MIDI communication for parameter changes
           - Manages UI state for all digital synth controls
           - Provides preset loading and management
           - Supports real-time parameter updates via SysEx

   Features:
       - Three independent partial editors
       - Common parameter controls (portamento, unison, legato, etc.)
       - Preset management and loading
       - Real-time MIDI parameter updates
       - ADSR envelope controls for both amplitude and filter
       - Oscillator waveform selection
       - Partial enabling/disabling and selection

   Dependencies:
       - PySide6 for UI components
       - qtawesome for icons
       - Custom MIDI handling classes
       - Digital synth parameter definitions



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.digital.editor.DigitalSynthEditor
   jdxi_editor.ui.editors.digital.editor.DigitalSynth2Editor
   jdxi_editor.ui.editors.digital.editor.DigitalSynth3Editor


Module Contents
---------------

.. py:class:: DigitalSynthEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, synth_number: int = 1, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.editor.SynthEditor`


   class for Digital Synth Editor containing 3 partials


   .. py:attribute:: preset_changed


   .. py:attribute:: instrument_image_group
      :value: None



   .. py:attribute:: instrument_title_label
      :value: None



   .. py:attribute:: partial_number
      :value: None



   .. py:attribute:: current_data
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: preset_helper


   .. py:attribute:: main_window
      :value: None



   .. py:attribute:: controls
      :type:  Dict[Union[jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalPartial, jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalCommon], PySide6.QtWidgets.QWidget]


   .. py:attribute:: synth_number
      :value: 1



   .. py:attribute:: refresh_shortcut


   .. py:attribute:: adsr_parameters


   .. py:attribute:: pitch_env_parameters


   .. py:attribute:: pwm_parameters


   .. py:method:: setup_ui()

      set up user interface



   .. py:method:: _create_partial_tab_widget(container_layout: PySide6.QtWidgets.QVBoxLayout, midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper) -> None

      Create the partial tab widget for the digital synth editor.

      :param container_layout: QVBoxLayout for the main container
      :param midi_helper: MiodiIOHelper instance for MIDI communication
      :return: None



   .. py:method:: _on_partial_state_changed(partial: jdxi_editor.midi.data.digital.DigitalPartial, enabled: bool, selected: bool) -> None

      Handle the state change of a partial (enabled/disabled and selected/unselected).

      :param partial: The partial to modify
      :param enabled: Whether the partial is enabled (ON/OFF)
      :param selected: Whether the partial is selected
      :return: None



   .. py:method:: set_partial_state(partial: jdxi_editor.midi.data.digital.DigitalPartial, enabled: bool = True, selected: bool = True) -> Optional[bool]

      Set the state of a partial (enabled/disabled and selected/unselected).

      :param partial: The partial to modify
      :param enabled: Whether the partial is enabled (ON/OFF)
      :param selected: Whether the partial is selected
      :return: True if successful, False otherwise



   .. py:method:: _initialize_partial_states()

      Initialize partial states with defaults
      Default: Partial 1 enabled and selected, others disabled



   .. py:method:: _handle_special_params(partial_no: int, param: jdxi_editor.midi.data.parameter.AddressParameter, value: int) -> None

      Handle special parameters that require additional UI updates.

      :param partial_no: int
      :param param: AddressParameter
      :param value: int
      :return: None



   .. py:method:: _update_partial_controls(partial_no: int, sysex_data: dict, successes: list, failures: list) -> None

      Apply updates to the UI components based on the received SysEx data.

      :param partial_no: int
      :param sysex_data: dict
      :param successes: list
      :param failures: list
      :return: None



   .. py:method:: _update_filter_state(partial_no: int, value: int) -> None

      Update the filter state of a partial based on the given value.

      :param partial_no: int
      :param value: int
      :return: None



   .. py:method:: _update_common_controls(partial_number: int, sysex_data: Dict, successes: list = None, failures: list = None) -> None

      Update the UI components for tone common and modify parameters.

      :param partial_number: int partial number
      :param sysex_data: Dictionary containing SysEx data
      :param successes: List of successful parameters
      :param failures: List of failed parameters
      :return: None



   .. py:method:: _update_modify_controls(partial_number: int, sysex_data: dict, successes: list = None, failures: list = None) -> None

      Update the UI components for tone common and modify parameters.

      :param partial_number: int partial number
      :param sysex_data: dict Dictionary containing SysEx data
      :param successes: list List of successful parameters
      :param failures: list List of failed parameters
      :return: None



   .. py:method:: _update_partial_adsr_widgets(partial_no: int, param: jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalPartial, midi_value: int, successes: list = None, failures: list = None)

      Update the ADSR widget for a specific partial based on the parameter and value.

      :param partial_no: int Partial number
      :param param: AddressParameter address
      :param midi_value: int value
      :return: None



   .. py:method:: _update_partial_pitch_env_widgets(partial_no: int, param: jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalPartial, midi_value: int, successes: list = None, failures: list = None)

      Update the Pitch Env widget for a specific partial based on the parameter and value.

      :param partial_no: int Partial number
      :param param: AddressParameter address
      :param midi_value: int value
      :param successes: list = None,
      :param failures: list = None,
      :return: None



   .. py:method:: _update_pulse_width_widgets(partial_no: int, param: jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalPartial, midi_value: int, successes: list = None, failures: list = None)

      Update the Pitch Env widget for a specific partial based on the parameter and value.

      :param partial_no: int Partial number
      :param param: AddressParameter address
      :param midi_value: int value
      :param successes: list = None,
      :param failures: list = None,
      :return: None



   .. py:method:: _update_partial_selection_switch(param: jdxi_editor.midi.data.parameter.AddressParameter, value: int, successes: list, failures: list) -> None

      Update the partial selection switches based on parameter and value.

      :param param: AddressParameter
      :param value: int
      :param successes: list
      :param failures: list
      :return: None



   .. py:method:: _update_partial_selected_state(param: jdxi_editor.midi.data.parameter.AddressParameter, value: int, successes: list, failures: list) -> None

      Update the partial selected state based on parameter and value.

      :param param: AddressParameter
      :param value: int
      :param successes: list
      :param failures: list
      :param debug: bool
      :return: None



   .. py:method:: _update_waveform_buttons(partial_number: int, value: int)

       Update the waveform buttons based on the OSC_WAVE value with visual feedback

      :param partial_number: int
      :param value: int
      :return:



.. py:class:: DigitalSynth2Editor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, synth_number: int = 2, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`DigitalSynthEditor`


   class for Digital Synth Editor containing 3 partials


   .. py:attribute:: preset_changed


.. py:class:: DigitalSynth3Editor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, synth_number: int = 3, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`DigitalSynthEditor`


   class for Digital Synth Editor containing 3 partials


   .. py:attribute:: preset_changed


