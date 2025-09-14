jdxi_editor.ui.windows.jdxi.ui
==============================

.. py:module:: jdxi_editor.ui.windows.jdxi.ui

.. autoapi-nested-parse::

   JD-Xi Editor UI setup.

   This class defines the main user interface for the JD-Xi Editor application, inheriting from QMainWindow. It handles the creation of the UI elements, including the main layout, menus, status bar, and MIDI indicators. It also provides functionality for displaying and managing synth presets, favorites, and MIDI connectivity.

   Key Features:
   - Sets up a frameless window with a customizable layout.
   - Initializes MIDI helper and indicators for MIDI input/output.
   - Loads and displays a digital font for instrument displays.
   - Allows users to manage and load favorite presets.
   - Displays a virtual piano keyboard in the status bar.
   - Integrates with MIDIHelper for MIDI communication.
   - Loads and saves application settings and preferences.

   .. method:: - __init__

      Initializes the UI, settings, MIDI components, and layout.

   .. method:: - _create_main_layout

      Sets up the central layout for displaying instrument images and overlays.
      



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.windows.jdxi.ui.JDXiUi


Module Contents
---------------

.. py:class:: JDXiUi

   Bases: :py:obj:`PySide6.QtWidgets.QMainWindow`


   JD-Xi UI setup, with as little as possible functionality, which is to be super-classed


   .. py:attribute:: digital_font_family
      :value: None



   .. py:attribute:: editor_registry
      :value: None



   .. py:attribute:: editors
      :value: []



   .. py:attribute:: log_viewer
      :value: None



   .. py:attribute:: midi_debugger
      :value: None



   .. py:attribute:: midi_message_monitor
      :value: None



   .. py:attribute:: old_pos
      :value: None



   .. py:attribute:: preset_helpers
      :value: None



   .. py:attribute:: slot_number
      :value: None



   .. py:attribute:: sequencer_buttons
      :value: []



   .. py:attribute:: current_program_bank_letter
      :value: 'A'



   .. py:attribute:: current_program_id
      :value: 'A01'



   .. py:attribute:: current_program_number
      :value: 1



   .. py:attribute:: current_program_name


   .. py:attribute:: preset_manager


   .. py:attribute:: current_synth_type
      :value: 'DIGITAL_SYNTH_1'



   .. py:attribute:: current_octave
      :value: 0



   .. py:attribute:: midi_helper


   .. py:attribute:: channel


   .. py:attribute:: midi_key_hold_latched
      :value: False



   .. py:attribute:: midi_requests


   .. py:attribute:: settings


   .. py:attribute:: piano_keyboard


   .. py:method:: _create_main_layout() -> None

      Create the main dashboard



   .. py:method:: _create_menu_bar() -> None


   .. py:method:: _create_parts_menu() -> None

      Create editors menu



   .. py:method:: _create_effects_menu() -> None

      Create editors menu



   .. py:method:: _create_playback_menu() -> None


   .. py:method:: _create_debug_menu() -> None


   .. py:method:: _create_help_menu() -> None


   .. py:method:: _create_status_bar()

      Create status bar with MIDI indicators



   .. py:method:: _build_status_layout() -> None


   .. py:method:: _build_midi_indicator_row() -> PySide6.QtWidgets.QLayout


   .. py:method:: _update_display()

      Update the display with the current preset information



   .. py:method:: _load_digital_font() -> None

      Load the digital LCD font for the display



   .. py:method:: update_preset_display(preset_number: int, preset_name: str)

      Update the current preset display



   .. py:method:: _update_display_preset(preset_number: int, preset_name: str, channel: int)

      Update the display with the new preset information.



   .. py:method:: show_error(title: str, message: str)

      Show error message dialog

      :param title: Dialog title
      :param message: Error message



   .. py:method:: show_warning(title: str, message: str)

      Show warning message dialog

      :param title: Dialog title
      :param message: Warning message



   .. py:method:: show_info(title: str, message: str)

      Show info message dialog

      :param title: Dialog title
      :param message: Info message



   .. py:method:: _load_settings()
      :abstractmethod:



   .. py:method:: on_documentation()
      :abstractmethod:



   .. py:method:: on_preferences()
      :abstractmethod:



   .. py:method:: show_editor(param: str)
      :abstractmethod:



   .. py:method:: _show_midi_debugger()
      :abstractmethod:



   .. py:method:: _show_main_editor()
      :abstractmethod:



   .. py:method:: _show_about_help()
      :abstractmethod:



   .. py:method:: _show_midi_message_monitor()
      :abstractmethod:



   .. py:method:: _show_log_viewer()
      :abstractmethod:



   .. py:method:: _show_midi_config()
      :abstractmethod:



   .. py:method:: _midi_send_octave(_)
      :abstractmethod:



   .. py:method:: _preset_previous()
      :abstractmethod:



   .. py:method:: _preset_next()
      :abstractmethod:



   .. py:method:: _load_saved_favorites()
      :abstractmethod:



   .. py:method:: _select_synth(synth_type)
      :abstractmethod:



   .. py:method:: _show_favorite_context_menu(pos, button: Union[jdxi_editor.ui.widgets.button.favorite.FavoriteButton, jdxi_editor.ui.widgets.button.sequencer.SequencerSquare])
      :abstractmethod:



   .. py:method:: _save_favorite(button, idx)
      :abstractmethod:



   .. py:method:: _midi_file_load()
      :abstractmethod:



   .. py:method:: _midi_file_save()
      :abstractmethod:



   .. py:method:: _patch_load()
      :abstractmethod:



   .. py:method:: _patch_save()
      :abstractmethod:



   .. py:method:: _handle_program_change(bank_letter: str, program_number: int)
      :abstractmethod:



