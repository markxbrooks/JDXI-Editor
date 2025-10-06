jdxi_editor.ui.editors
======================

.. py:module:: jdxi_editor.ui.editors

.. autoapi-nested-parse::

   Editor modules for JD-Xi parameters



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/ui/editors/analog/index
   /autoapi/jdxi_editor/ui/editors/arpeggio/index
   /autoapi/jdxi_editor/ui/editors/config/index
   /autoapi/jdxi_editor/ui/editors/digital/index
   /autoapi/jdxi_editor/ui/editors/drum/index
   /autoapi/jdxi_editor/ui/editors/effects/index
   /autoapi/jdxi_editor/ui/editors/helpers/index
   /autoapi/jdxi_editor/ui/editors/io/index
   /autoapi/jdxi_editor/ui/editors/main/index
   /autoapi/jdxi_editor/ui/editors/pattern/index
   /autoapi/jdxi_editor/ui/editors/synth/index


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.SynthEditor
   jdxi_editor.ui.editors.AnalogSynthEditor
   jdxi_editor.ui.editors.DigitalSynthEditor
   jdxi_editor.ui.editors.DrumCommonEditor
   jdxi_editor.ui.editors.ArpeggioEditor
   jdxi_editor.ui.editors.EffectsCommonEditor
   jdxi_editor.ui.editors.VocalFXEditor
   jdxi_editor.ui.editors.ProgramEditor


Package Contents
----------------

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



.. py:class:: ArpeggioEditor(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, preset_helper: Optional[jdxi_editor.jdxi.preset.helper.JDXiPresetHelper] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Arpeggio Editor Window


   .. py:attribute:: midi_helper


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: address


   .. py:attribute:: partial_number
      :value: 0



   .. py:attribute:: instrument_icon_folder
      :value: 'arpeggiator'



   .. py:attribute:: default_image
      :value: 'arpeggiator2.png'



   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:attribute:: title_label


   .. py:attribute:: image_label


   .. py:attribute:: switch_button


   .. py:attribute:: style_combo


   .. py:attribute:: grid_combo


   .. py:attribute:: duration_combo


   .. py:attribute:: velocity_slider


   .. py:attribute:: accent_slider


   .. py:attribute:: octave_combo


   .. py:attribute:: motif_combo


.. py:class:: EffectsCommonEditor(midi_helper: jdxi_editor.midi.io.helper.MidiIOHelper, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, parent=None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Effects Editor Window


   .. py:attribute:: tab_widget
      :value: None



   .. py:attribute:: midi_helper


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: EFX1_PARAMETERS


   .. py:attribute:: EFX2_PARAMETERS


   .. py:attribute:: efx1_param_labels


   .. py:attribute:: efx2_param_labels


   .. py:attribute:: midi_requests
      :value: ['F0 41 10 00 00 00 0E 12 18 00 02 00 01 7F 32 32 01 00 40 00 40 00 40 00 40 00 00 00 00 08 00...



   .. py:attribute:: delay_params
      :value: None



   .. py:attribute:: efx2_additional_params


   .. py:attribute:: default_image
      :value: 'effects.png'



   .. py:attribute:: instrument_icon_folder
      :value: 'effects'



   .. py:attribute:: title_label


   .. py:attribute:: image_label


   .. py:attribute:: controls
      :type:  Dict[Union[jdxi_editor.midi.data.parameter.effects.effects.AddressParameterReverb, jdxi_editor.midi.data.parameter.effects.common.AddressParameterEffectCommon, jdxi_editor.midi.data.parameter.effects.effects.AddressParameterEffect1, jdxi_editor.midi.data.parameter.effects.effects.AddressParameterEffect2], PySide6.QtWidgets.QWidget]


   .. py:attribute:: tabs


   .. py:attribute:: address


   .. py:attribute:: sysex_composer


   .. py:method:: update_flanger_rate_note_controls() -> None

      Update Flanger rate/note controls based on rate note switch.



   .. py:method:: update_phaser_rate_note_controls() -> None

      Update Flanger rate/note controls based on rate note switch.



   .. py:method:: _update_efx1_labels(effect_type: int)

      Update Effect 1 parameter labels based on selected effect type.

      :param effect_type: int
      :return:



   .. py:method:: _update_efx2_labels(effect_type: int)

      Update Effect 2 parameter labels based on selected effect type.

      :param effect_type: int



   .. py:method:: _create_effect1_section()

      Create Effect 1 section



   .. py:method:: _create_effect2_section()

      Create Effect 2 section



   .. py:method:: _create_delay_tab()

      Create Delay tab with parameters



   .. py:method:: _create_reverb_section()

      Create Reverb section



   .. py:method:: _on_parameter_changed(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int, address: jdxi_editor.midi.data.address.address.RolandSysExAddress = None)

      Handle parameter value changes from UI controls.



   .. py:method:: send_midi_parameter(param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int) -> bool

      Send MIDI parameter with error handling

      :param param: AddressParameter
      :param value: int value
      :return: bool True on success, False otherwise



.. py:class:: VocalFXEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None, parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Vocal Effects Window Class


   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: address


   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.synth.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:attribute:: title_label


   .. py:attribute:: image_label


   .. py:attribute:: default_image
      :value: 'vocal_fx.png'



   .. py:attribute:: instrument_icon_folder
      :value: 'vocal_fx'



   .. py:attribute:: tab_widget


   .. py:method:: _create_common_section() -> PySide6.QtWidgets.QWidget

      _create_common_section

      :return: QWidget



   .. py:method:: _create_vocal_effect_section() -> PySide6.QtWidgets.QWidget

      Create general vocal effect controls section



   .. py:method:: _create_mixer_section() -> PySide6.QtWidgets.QWidget

      _create_mixer_section

      :return: QWidget



   .. py:method:: _create_auto_pitch_section()

      _create_auto_pitch_section

      :return: QWidget



.. py:class:: ProgramEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Program Editor Window


   .. py:attribute:: program_changed


   .. py:attribute:: title_right_vlayout
      :value: None



   .. py:attribute:: program_list
      :value: None



   .. py:attribute:: file_label
      :value: None


      Initialize the ProgramEditor

      :param midi_helper: Optional[MidiIOHelper]
      :param parent: Optional[QWidget]
      :param preset_helper: JDXIPresetHelper


   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: channel


   .. py:attribute:: midi_requests


   .. py:attribute:: default_image
      :value: 'programs.png'



   .. py:attribute:: instrument_icon_folder
      :value: 'programs'



   .. py:attribute:: instrument_title_label


   .. py:attribute:: layout
      :value: None



   .. py:attribute:: midi_channel
      :value: 0



   .. py:attribute:: genre_label
      :value: None



   .. py:attribute:: program_number_combo_box
      :value: None



   .. py:attribute:: program_name
      :value: ''



   .. py:attribute:: bank_combo_box
      :value: None



   .. py:attribute:: load_button
      :value: None



   .. py:attribute:: save_button
      :value: None



   .. py:attribute:: image_label
      :value: None



   .. py:attribute:: title_label
      :value: None



   .. py:attribute:: bank_label
      :value: None



   .. py:attribute:: program_label
      :value: None



   .. py:attribute:: genre_combo_box
      :value: None



   .. py:attribute:: preset_type
      :value: None



   .. py:attribute:: programs


   .. py:attribute:: controls
      :type:  Dict[jdxi_editor.midi.data.parameter.AddressParameter, PySide6.QtWidgets.QWidget]


   .. py:method:: setup_ui()

      set up ui elements



   .. py:method:: _create_preset_selection_widget() -> PySide6.QtWidgets.QWidget

      create_preset_selection_widget

      :return: QWidget



   .. py:method:: load_preset_by_program_change(preset_index: int) -> None

      Load a preset by program change.

      :param preset_index: int



   .. py:method:: on_category_changed(_: int) -> None

      Handle category selection change.



   .. py:method:: _create_transport_group() -> PySide6.QtWidgets.QGroupBox

      _create_transport_group

      :return: QGroupBox
      Transport controls area



   .. py:method:: _create_program_selection_box() -> PySide6.QtWidgets.QGroupBox

      create_program_selection_box

      :return: QGroupBox



   .. py:method:: edit_program_name()

      edit_tone_name

      :return: None



   .. py:method:: on_preset_type_changed(index: int) -> None

      on_preset_type_changed

      :param index: int
      Handle preset type selection change



   .. py:method:: set_channel_and_preset_lists(preset_type: str) -> None

      set_channel_and_preset_lists

      :param preset_type:
      :return: None



   .. py:method:: update_category_combo_box_categories() -> None

      update_category_combo_box_categories

      :return: None
      Update the category combo box.



   .. py:method:: _populate_programs(search_text: str = '') -> None

      Populate the program list with available presets.

      :param search_text: str
      :return: None



   .. py:method:: _populate_presets(search_text: str = '') -> None

      Populate the program list with available presets.

      :param search_text: str
      :return: None



   .. py:method:: _init_synth_data(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth = JDXiSynth.DIGITAL_SYNTH_1, partial_number: Optional[int] = 0) -> None

      :param synth_type: JDXiSynth
      :param partial_number: int
      :return: None
      Initialize synth-specific data



   .. py:method:: _create_mixer_section() -> PySide6.QtWidgets.QWidget

      _create_mixer_section

      :return: QWidget
      Create general vocal effect controls section with scrolling



   .. py:method:: update_tone_name_for_synth(tone_name: str, synth_type: str) -> None

      Update the tone name.

      :param tone_name: str
      :param synth_type: str



   .. py:method:: set_current_program_name(program_name: str, synth_type: str = None) -> None

      Set the current program name in the file label

      :param program_name: str
      :param synth_type: str (optional), discarded for now
      :return: None



   .. py:method:: start_playback()

      Start playback of the MIDI file.



   .. py:method:: stop_playback()

      Stop playback of the MIDI file.



   .. py:method:: populate_programs(search_text: str = '')

      Populate the program list with available presets.



   .. py:method:: add_user_banks(filtered_list: list, bank: str, search_text: str = None) -> None

      Add user banks to the program list.
      :param filtered_list: list
      :param bank: str



   .. py:method:: on_bank_changed(_: int) -> None

      Handle bank selection change.



   .. py:method:: on_program_number_changed(index: int) -> None

      Handle program number selection change.
      :param index: int



   .. py:method:: load_program()

      Load the selected program based on bank and number.



   .. py:method:: update_current_synths(program_details: jdxi_editor.jdxi.program.program.JDXiProgram) -> None

      Update the current synth label.
      :param program_details: dict
      :return: None



   .. py:method:: load_preset(program_number: int) -> None

      load_preset

      :param program_number: int
      :return: None
      Load preset data and update UI



   .. py:method:: _update_program_list() -> None

      Update the program list with available presets.



   .. py:method:: on_genre_changed(_: int) -> None

      Handle genre selection change.

      :param _: int



   .. py:method:: _dispatch_sysex_to_area(json_sysex_data: str) -> None

      Dispatch SysEx data to the appropriate area for processing.

      :param json_sysex_data:
      :return: None



   .. py:method:: _update_common_controls(partial_number: int, sysex_data: Dict, successes: list = None, failures: list = None) -> None

      Update the UI components for tone common and modify parameters.

      :param partial_number: int partial number
      :param sysex_data: Dictionary containing SysEx data
      :param successes: List of successful parameters
      :param failures: List of failed parameters
      :return: None



   .. py:method:: _update_slider(param: jdxi_editor.midi.data.parameter.AddressParameter, midi_value: int, successes: list = None, failures: list = None, slider: PySide6.QtWidgets.QWidget = None) -> None

      Update slider based on parameter and value.

      :param param: AddressParameter
      :param midi_value: int value
      :param successes: list
      :param failures: list
      :return: None



