jdxi_editor.ui.windows.jdxi.instrument
======================================

.. py:module:: jdxi_editor.ui.windows.jdxi.instrument

.. autoapi-nested-parse::

   # Create editor instances
   analog_editor = AnalogSynthEditor(midi_helper, preset_helper)
   digital_editor = DigitalSynthEditor(midi_helper, preset_helper)
   drum_editor = DrumSynthEditor(midi_helper, preset_helper)

   # Save all controls to a single JSON file
   save_all_controls_to_single_file(
       editors=[self.analog_editor, self.digital_synth2_editor self.digital_synth1_editor, analog_editor],
       file_path="all_controls.json"
   )
   JD-Xi Instrument class for managing presets and MIDI settings.

   This module defines the `JdxiInstrument` class, which extends from the `JdxiUi` class to manage JD-Xi instrument presets, MIDI communication, and UI interactions. It allows for controlling and modifying different preset types (Digital 1, Digital 2, Analog, Drums) and provides MIDI connectivity for program changes and preset management.

   Key Features:
   - Handles MIDI connectivity and communication, including program change signals.
   - Manages different preset types (Digital, Analog, Drums) with the ability to select and load presets.
   - Provides MIDI indicators to display the status of MIDI input/output ports.
   - Includes functionality for dragging the window and selecting different synth types.
   - Integrates with external MIDI devices for seamless performance control.
   - Includes a custom UI to manage and visualize the instrument's preset settings.
   - Supports the auto-connection of JD-Xi and provides MIDI configuration if auto-connection fails.

   .. method:: - __init__

      Initializes the instrument's MIDI settings, UI components, and preset handlers.

   .. method:: - mousePressEvent, mouseMoveEvent, mouseReleaseEvent

      Handles window drag events for custom window movement.

   .. method:: - _select_synth

      Selects the current synth type and updates UI button styles.

   .. method:: - _update_synth_button_styles

      Updates button styles based on the selected synth type.

   .. method:: - _get_presets_for_current_synth

      Returns the list of presets based on the selected synth type.

   .. method:: - _get_for_current_synth

      Returns the appropriate preset handler based on the selected synth type.

   .. method:: - _previous_tone

      Navigates to the previous tone in the preset list and updates the display.

   .. method:: - ...

      
      



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.jdxi.instrument.JDXiInstrument


Module Contents
---------------

.. py:class:: JDXiInstrument

   Bases: :py:obj:`jdxi_editor.ui.windows.jdxi.ui.JDXiUi`


   class JDXiInstrument


   .. py:attribute:: sysex_composer


   .. py:attribute:: program_helper


   .. py:attribute:: settings


   .. py:attribute:: editor_registry


   .. py:attribute:: main_editor
      :value: None



   .. py:attribute:: current_synth_type
      :value: 'DIGITAL_SYNTH_1'



   .. py:attribute:: channel


   .. py:method:: _init_preset_helpers()

      Initialize preset helpers dynamically



   .. py:method:: _set_callbacks()

      Set up signal-slot connections for various UI elements.



   .. py:method:: closeEvent(event: PySide6.QtGui.QCloseEvent) -> None

      Handle window close event

      :param event: QCloseEvent
      :return: None



   .. py:method:: mousePressEvent(event: PySide6.QtGui.QMouseEvent) -> None

      mousePressEvent

      :param event: mousePressEvent
      :return: None



   .. py:method:: mouseMoveEvent(event: PySide6.QtGui.QMouseEvent)

      mouseMoveEvent

      :param event: QMouseEvent
      :return: None



   .. py:method:: mouseReleaseEvent(event: PySide6.QtGui.QMouseEvent) -> None

      mouseReleaseEvent

      :param event: QMouseEvent
      :return: None



   .. py:method:: data_request() -> None

      Request the current value of the NRPN parameter from the device.



   .. py:method:: _handle_program_change(bank_letter: str, program_number: int) -> None

      perform data request

      :param bank_letter: str
      :param program_number: int
      :return: None



   .. py:method:: register_editor(editor: jdxi_editor.ui.editors.SynthEditor) -> None

      register editor

      :param editor: SynthEditor
      :return: None



   .. py:method:: set_tone_name_by_type(tone_name: str, synth_type: str) -> None

      set tone name by type

      :param tone_name: str Tone name
      :param synth_type: str Synth type
      :return: None



   .. py:method:: get_preset_helper_for_current_synth() -> jdxi_editor.jdxi.preset.helper.JDXiPresetHelper

      Return the appropriate preset helper based on the current synth preset_type

      :return: JDXiPresetHelper



   .. py:method:: set_current_program_name(program_name: str) -> None

      program name

      :param program_name: str
      :return: None



   .. py:method:: set_current_program_number(channel: int, program_number: int) -> None

      program number

      :param channel: int midi channel (discarded)
      :param program_number: int Program number
      :return: None



   .. py:method:: _select_synth(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth) -> None

      Select address synth and update button styles

      :param synth_type: JDXiSynth
      :return: None



   .. py:method:: _update_synth_button_styles()

      Update styles for synth buttons based on selection.



   .. py:method:: _program_update(index_change: int) -> None

      Update the program by incrementing or decrementing its index

      :param index_change: int
      :return: None



   .. py:method:: _program_previous() -> None

      Decrement the program index and update the display.



   .. py:method:: _program_next() -> None

      Increment the program index and update the display.



   .. py:method:: _preset_update(index_change: int) -> None

      Update the preset by incrementing or decrementing its index

      :param index_change: int
      :return: None



   .. py:method:: _preset_previous() -> None

      Decrement the tone index and update the display

      :return: None



   .. py:method:: _preset_next() -> None

      Increment the tone index and update the display.



   .. py:method:: update_display_callback(synth_type: jdxi_editor.jdxi.synth.type.JDXiSynth, preset_index: int, channel: int) -> None

      Update the display for the given synth preset_type and preset index

      :param synth_type: JDXiSynth
      :param preset_index: int
      :param channel: int
      :return: None



   .. py:method:: _toggle_illuminate_sequencer_lightshow(enabled: bool) -> None

      Toggle the sequencer lightshow on or off

      :param enabled: bool
      :return: None



   .. py:method:: init_main_editor() -> None

      Initialize the UI for the MainEditor

      :return:



   .. py:method:: show_editor(editor_type: str) -> None

      Show editor of given type

      :param editor_type: str Editor type
      :return: None



   .. py:method:: on_documentation()

      on_documentation

      :return: None



   .. py:method:: on_preferences()

      on_preferences
      :return:



   .. py:method:: get_existing_editor(editor_class) -> Optional[jdxi_editor.ui.editors.SynthEditor]

      Get existing editor instance of the specified class

      :param editor_class: class
      :return: Optional[SynthEditor]



   .. py:method:: _show_editor_tab(title: str, editor_class, icon, **kwargs) -> None

      _show_editor_tab

      :param title: str Title of the tab
      :param editor_class: cls Class of the Editor
      :param kwargs:
      :return: None



   .. py:method:: _show_editor(title: str, editor_class, **kwargs) -> None

      _show editor

      :param title: str
      :param editor_class: class
      :param kwargs: Any
      :return: None



   .. py:method:: _show_log_viewer() -> None

      Show log viewer window



   .. py:method:: _show_midi_config() -> None

      Show MIDI configuration dialog



   .. py:method:: _show_midi_debugger() -> None

      Open MIDI debugger window



   .. py:method:: _show_midi_message_monitor() -> None

      Open MIDI message monitor window



   .. py:method:: _show_program_editor(_) -> None

      Open the ProgramEditor when the digital display is clicked.



   .. py:method:: _show_about_help() -> None

      _show_about_help

      :return:



   .. py:method:: _show_main_editor() -> None

      _show_about_help

      :return:



   .. py:method:: _midi_file_load()

      _midi_file_load

      :return: None
      Load a MIDI file and process it
      1. Load the current MIDI file using the MidiFileEditor.
      2. If the editor does not exist, create and show it.
      3. After saving, show the editor again.



   .. py:method:: _midi_file_save()

      _midi_file_save
      :return:
      1. Save the current MIDI file using the MidiFileEditor.
      2. If the editor does not exist, create and show it.
      3. After saving, show the editor again.



   .. py:method:: _patch_load() -> None

      Show load patch dialog



   .. py:method:: _patch_save() -> None

      Show save patch dialog



   .. py:method:: load_button_preset(button: jdxi_editor.ui.widgets.button.SequencerSquare) -> None

      load preset data stored on the button

      :param button: SequencerSquare
      :return: None



   .. py:method:: _generate_button_preset() -> Optional[jdxi_editor.jdxi.preset.button.JDXiPresetButtonData]

      Generate a ButtonPreset object based on the current preset.

      :return: Optional[JDXiPresetButtonData]



   .. py:method:: _get_current_preset_name_from_settings() -> str

      :return: str

      Get the name of the currently selected preset
      based on the last used preset type and number.



   .. py:method:: _get_current_preset_type() -> jdxi_editor.jdxi.synth.type.JDXiSynth

      Get the preset_type of the currently selected preset

      :return: JDXiSynth



   .. py:method:: _ui_update_octave() -> None

      Update octave-related UI elements



   .. py:method:: _midi_init_ports(in_port: jdxi_editor.midi.io.controller.MidiIOController, out_port: jdxi_editor.midi.io.controller.MidiIOController) -> None

      Set MIDI input and output ports

      :param in_port:
      :param out_port:
      :return: None



   .. py:method:: _midi_blink_input(_)

      Handle incoming MIDI messages and flash indicator



   .. py:method:: _midi_blink_output(_)

      handle outgoing message blink



   .. py:method:: _midi_send_octave(direction: int) -> Union[None, bool]

      Send octave change MIDI message

      :param direction: int
      :return: Union[None, bool]



   .. py:method:: _midi_send_arp_key_hold(state: bool) -> None

      Send arpeggiator key hold (latch) command

      :param state: bool
      :return: None



   .. py:method:: _midi_send_arp_on_off(state: bool) -> None

      Send arpeggiator on/off command

      :param state: bool ON/OFF
      :return: None



   .. py:method:: handle_piano_note_on(note_num: int) -> None

      Handle piano key press

      :param note_num: int note midi number
      :return: None



   .. py:method:: handle_piano_note_off(note_num: int) -> None

      Handle piano key release

      :param note_num: int midi note number
      :return: None



   .. py:method:: _load_last_preset()

      Load the last used preset from settings.



   .. py:method:: _save_last_preset(synth_type: str, preset_num: int, channel: int)

      Save the last used preset to settings

      :param synth_type: Type of synth ('Analog', 'Digital 1', 'Digital 2', 'Drums')
      :param preset_num: Preset number (0-based index)
      :param channel: MIDI channel



   .. py:method:: _show_favorite_context_menu(pos, button: Union[jdxi_editor.ui.widgets.button.favorite.FavoriteButton, jdxi_editor.ui.widgets.button.SequencerSquare])

      Show context menu for favorite button



   .. py:method:: _save_to_favorite(button: Union[jdxi_editor.ui.widgets.button.favorite.FavoriteButton, jdxi_editor.ui.widgets.button.SequencerSquare]) -> None

      Save current preset to favorite slot

      :param button: Union[FavoriteButton, SequencerSquare]
      :return: None



   .. py:method:: _clear_favorite(button: Union[jdxi_editor.ui.widgets.button.favorite.FavoriteButton, jdxi_editor.ui.widgets.button.SequencerSquare]) -> None

      Clear favorite slot

      :param button: FavoriteButton
      :return: None



   .. py:method:: _load_saved_favorites()

      Load saved favorites from settings



   .. py:method:: _save_favorite(button: Union[jdxi_editor.ui.widgets.button.favorite.FavoriteButton, jdxi_editor.ui.widgets.button.SequencerSquare], index: int) -> None

      Save the current preset as an address favorite and prevent toggling off

      :param button: button: Union[FavoriteButton, SequencerSquare]
      :param index: int
      :return: None



   .. py:method:: _load_settings()

      Load application settings



   .. py:method:: _save_settings()

      Save application settings



