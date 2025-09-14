jdxi_editor.ui.editors.io.preset
================================

.. py:module:: jdxi_editor.ui.editors.io.preset

.. autoapi-nested-parse::

   PresetEditor Module

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

   jdxi_editor.ui.editors.io.preset.PresetEditor


Module Contents
---------------

.. py:class:: PresetEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, parent: Optional[PySide6.QtWidgets.QWidget] = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.simple.BasicEditor`


   Program Editor Window


   .. py:attribute:: program_changed


   .. py:attribute:: digital_preset_type_combo
      :value: None



   .. py:attribute:: midi_helper
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: midi_channel


   .. py:attribute:: default_image
      :value: 'presets.png'



   .. py:attribute:: instrument_icon_folder
      :value: 'presets'



   .. py:attribute:: midi_requests


   .. py:attribute:: layout
      :value: None



   .. py:attribute:: genre_label
      :value: None



   .. py:attribute:: preset_combo_box
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



   .. py:attribute:: digital_preset_label
      :value: None



   .. py:attribute:: category_combo_box
      :value: None



   .. py:attribute:: preset_type
      :value: None



   .. py:attribute:: synth_label_map


   .. py:attribute:: presets


   .. py:method:: setup_ui()

      set up UI elements



   .. py:method:: _create_preset_selection_group() -> PySide6.QtWidgets.QGroupBox

      create_preset_selection_group

      :return: QGroupBox



   .. py:method:: on_preset_type_changed(index: int) -> None

      Handle preset type selection change.



   .. py:method:: update_tone_name_for_synth(tone_name: str, synth_type: str) -> None

      Update the tone name.

      :param tone_name: str
      :param synth_type: str



   .. py:method:: load_preset_by_program_change(preset_index: int) -> None

      Load a preset by program change.

      :param preset_index: int



   .. py:method:: _populate_presets(search_text: str = '')

      Populate the program list with available presets.

      :param search_text: str



   .. py:method:: update_category_combo_box_categories() -> None

      Update the category combo box.



   .. py:method:: on_bank_changed(_: int) -> None

      Handle bank selection change.



   .. py:method:: on_preset_number_changed(index: int) -> None

      Handle program number selection change.



   .. py:method:: load_program() -> None

      Load the selected program based on bank and number.



   .. py:method:: update_current_synths(program_details: dict) -> None

      Update the current synth label.
      :param program_details: dict



   .. py:method:: load_preset_temp(preset_number: int) -> None

      Load preset data and update UI.
      :param preset_number: int



   .. py:method:: _update_preset_list() -> None

      Update the preset list with available presets.



   .. py:method:: on_category_changed(_: int) -> None

      Handle category selection change.



