jdxi_editor.ui.editors.io.program
=================================

.. py:module:: jdxi_editor.ui.editors.io.program

.. autoapi-nested-parse::

   ProgramEditor Module

   This module defines the `ProgramEditor` class, a PySide6-based GUI for
   managing and selecting MIDI programs.

   It allows users to browse, filter, and load programs based on bank, genre,
   and program number.

   The class also facilitates MIDI integration by sending Program Change (PC)
   and Bank Select (CC#0, CC#32) messages.

   Key Features:
   - Graphical UI for selecting and managing MIDI programs.
   - Filtering options based on bank and genre.
   - MIDI integration for program selection and loading.
   - Image display for program categories.
   - Program list population based on predefined program data.

   Classes:
       ProgramEditor(QMainWindow)
           A main window class for handling MIDI program selection and management.

   Signals:
       program_changed (int, str, int)
           Emitted when a program selection changes. Parameters:
           - MIDI channel (int)
           - Preset name (str)
           - Program number (int)

   Dependencies:
   - PySide6.QtWidgets
   - PySide6.QtCore
   - MIDIHelper for MIDI message handling
   - PresetHandler for managing program presets
   - JDXiProgramList.PROGRAM_LIST for predefined program data



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.io.program.ProgramEditor


Module Contents
---------------

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



