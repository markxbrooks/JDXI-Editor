jdxi_editor.ui.editors.analog.editor
====================================

.. py:module:: jdxi_editor.ui.editors.analog.editor

.. autoapi-nested-parse::

   Module: analog_synth_editor
   ===========================

   This module defines the `AnalogSynthEditor` class, which provides a PySide6-based
   user interface for editing analog synthesizer parameters in the Roland JD-Xi synthesizer.
   It extends the `SynthEditor` base class and integrates MIDI communication for real-time
   parameter adjustments and preset management.

   Key Features:
   -------------
   - Provides a graphical editor for modifying analog synth parameters, including
     oscillator, filter, amp, LFO, and envelope settings.
   - Supports MIDI communication to send and receive real-time parameter changes.
   - Allows selection of different analog synth presets from a dropdown menu.
   - Displays an instrument image that updates based on the selected preset.
   - Includes a scrollable layout for managing a variety of parameter controls.
   - Implements bipolar parameter handling for proper UI representation.
   - Supports waveform selection with custom buttons and icons.
   - Provides a "Send Read Request to Synth" button to retrieve current synth settings.
   - Enables MIDI-triggered updates via incoming program changes and parameter adjustments.

   Dependencies:
   -------------
   - PySide6 (for UI components and event handling)
   - MIDIHelper (for handling MIDI communication)
   - PresetHandler (for managing synth presets)
   - Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

   Usage:
   ------
   The `AnalogSynthEditor` class can be instantiated as part of a larger PySide6 application.
   It requires a `MIDIHelper` instance for proper communication with the synthesizer.

   Example:
   --------
       midi_helper = MIDIHelper()
       preset_helper = PresetHandler()
       editor = AnalogSynthEditor(midi_helper, preset_helper)
       editor.show()



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.analog.editor.AnalogSynthEditor


Module Contents
---------------

.. py:class:: AnalogSynthEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: Optional[jdxi_editor.jdxi.preset.helper.JDXiPresetHelper] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.editor.SynthEditor`


   Analog Synth Editor UI.


   .. py:attribute:: amp_section
      :value: None



   .. py:attribute:: oscillator_section
      :value: None



   .. py:attribute:: read_request_button
      :value: None



   .. py:attribute:: tab_widget
      :value: None



   .. py:attribute:: lfo_section
      :value: None



   .. py:attribute:: instrument_selection_label
      :value: None



   .. py:attribute:: instrument_title_label
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: wave_buttons


   .. py:attribute:: lfo_shape_buttons


   .. py:attribute:: controls
      :type:  Dict[Union[jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog], PySide6.QtWidgets.QWidget]


   .. py:attribute:: updating_from_spinbox
      :value: False



   .. py:attribute:: previous_json_data
      :value: None



   .. py:attribute:: main_window
      :value: None



   .. py:attribute:: refresh_shortcut


   .. py:attribute:: sub_osc_type_map


   .. py:attribute:: filter_switch_map


   .. py:attribute:: osc_waveform_map


   .. py:attribute:: adsr_mapping


   .. py:attribute:: pitch_env_mapping


   .. py:attribute:: pwm_mapping


   .. py:method:: setup_ui()

      Set up the Analog Synth Editor UI.



   .. py:method:: _create_sections()

      Create the sections for the Analog Synth Editor.



   .. py:method:: _init_parameter_mappings()

      Initialize MIDI parameter mappings.



   .. py:method:: update_filter_controls_state(mode: int)

      Update filter controls enabled state based on mode



   .. py:method:: _on_filter_mode_changed(mode: int)

      Handle filter mode changes



   .. py:method:: update_filter_state(value: int)

      Update the filter state

      :param value: int value
      :return: None



   .. py:method:: _on_waveform_selected(waveform: jdxi_editor.midi.data.analog.oscillator.AnalogOscWave)

      Handle waveform button selection

      :param waveform: AnalogOscWave value
      :return: None



   .. py:method:: _on_lfo_shape_changed(value: int)

      Handle LFO shape change

      :param value: int value
      :return: None



   .. py:method:: update_slider(param: jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog, midi_value: int, successes: list = None, failures: list = None) -> None

      Helper function to update sliders safely.

      :param param: AddressParameterAnalog value
      :param failures: list of failed parameters
      :param successes: list of successful parameters
      :param midi_value: int value
      :return: None



   .. py:method:: update_adsr_widget(param: jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog, midi_value: int, successes: list = None, failures: list = None) -> None

      Helper function to update ADSR widgets.

      :param param: AddressParameterAnalog value
      :param midi_value: int value
      :param failures: list of failed parameters
      :param successes: list of successful parameters
      :return: None



   .. py:method:: update_pitch_env_widget(parameter: jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog, value: int, successes: list = None, failures: list = None) -> None

      Helper function to update ADSR widgets.

      :param parameter: AddressParameterAnalog value
      :param value: int value
      :param failures: list of failed parameters
      :param successes: list of successful parameters
      :return: None



   .. py:method:: update_pwm_widget(parameter: jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog, value: int, successes: list = None, failures: list = None) -> None

      Helper function to update PWM widgets.

      :param parameter: AddressParameterAnalog value
      :param value: int value
      :param failures: list of failed parameters
      :param successes: list of successful parameters
      :return: None



   .. py:method:: _update_partial_controls(partial_no: int, sysex_data: dict, successes: list, failures: list) -> None

      Update sliders and combo boxes based on parsed SysEx data.

      :param sysex_data: dict SysEx data
      :param successes: list SysEx data
      :param failures: list SysEx data
      :return: None



   .. py:method:: _update_waveform_buttons(value: int)

      Update the waveform buttons based on the OSC_WAVE value with visual feedback.

      :param value: int value
      :return: None



   .. py:method:: _update_lfo_shape_buttons(value: int)

      Update the LFO shape buttons with visual feedback.

      :param value: int value
      :return: None



   .. py:method:: _update_pw_controls_state(waveform: jdxi_editor.midi.data.analog.oscillator.AnalogOscWave)

      Enable/disable PW controls based on waveform

      :param waveform: AnalogOscWave value
      :return: None



