jdxi_editor.ui.editors.pattern.pattern
======================================

.. py:module:: jdxi_editor.ui.editors.pattern.pattern

.. autoapi-nested-parse::

   Module: Pattern Sequencer with MIDI Integration

   This module implements address Pattern Sequencer using PySide6, allowing users to toggle
   sequence steps using address grid of buttons. It supports MIDI input to control button states
   using note keys (e.g., C4, C#4, etc.).

   Features:
   - 4 rows of buttons labeled as Digital Synth 1, Digital Synth 2, Analog Synth, and Drums.
   - MIDI note-to-button mapping for real-time control.
   - Toggle button states programmatically or via MIDI.
   - Styled buttons with illumination effects.
   - Each button stores an associated MIDI note and its on/off state.
   - Start/Stop playback buttons for sequence control. ..



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.pattern.pattern.PatternSequenceEditor


Module Contents
---------------

.. py:class:: PatternSequenceEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper], preset_helper: Optional[jdxi_editor.jdxi.preset.helper.JDXiPresetHelper], parent: Optional[PySide6.QtWidgets.QWidget] = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.synth.editor.SynthEditor`


   Pattern Sequencer with MIDI Integration using mido


   .. py:attribute:: muted_channels
      :value: []



   .. py:attribute:: total_measures
      :value: None



   .. py:attribute:: midi_helper


   .. py:attribute:: preset_helper


   .. py:attribute:: buttons
      :value: []



   .. py:attribute:: measures
      :value: []



   .. py:attribute:: timer
      :value: None



   .. py:attribute:: current_step
      :value: 0



   .. py:attribute:: total_steps
      :value: 16



   .. py:attribute:: beats_per_pattern
      :value: 4



   .. py:attribute:: bpm
      :value: 120



   .. py:attribute:: last_tap_time
      :value: None



   .. py:attribute:: tap_times
      :value: []



   .. py:attribute:: learned_pattern


   .. py:attribute:: active_notes


   .. py:attribute:: midi_file


   .. py:attribute:: midi_track


   .. py:method:: _setup_ui()


   .. py:method:: ui_generate_button_row(row_index: int, visible: bool = False)

      generate sequencer button row



   .. py:method:: on_learn_pattern_button_clicked()

      Connect the MIDI input to the learn pattern function.



   .. py:method:: on_stop_learn_pattern_button_clicked()

      Disconnect the MIDI input from the learn pattern function and update combo boxes.



   .. py:method:: _update_combo_boxes(message)

      Update the combo box index to match the note for each channel.



   .. py:method:: _midi_note_to_combo_index(row, midi_note)

      Convert a MIDI note number to the corresponding combo box index.



   .. py:method:: _set_combo_box_index(row, index)

      Set the combo box index for the specified row.



   .. py:method:: _add_measure()

      Add a new measure tab



   .. py:method:: _clear_learned_pattern()

      Clear the learned pattern and reset button states.



   .. py:method:: _on_measure_count_changed(count: int)

      Handle measure count changes



   .. py:method:: _update_pattern_length()

      Update total pattern length based on measure count



   .. py:method:: _on_button_clicked(button, checked)

      Handle button clicks and store the selected note



   .. py:method:: _on_tempo_changed(bpm: int)

      Handle tempo changes from the spinbox



   .. py:method:: _on_tap_tempo()

      Handle tap tempo button clicks



   .. py:method:: _save_pattern_dialog()

      Open save file dialog and save pattern



   .. py:method:: _load_pattern_dialog()

      Open load file dialog and load pattern



   .. py:method:: set_tempo(bpm: int)

      Set the pattern tempo in BPM using mido.



   .. py:method:: _init_midi_file()

      Initialize a new MIDI file with 4 tracks



   .. py:method:: update_pattern()

      Update the MIDI file with current pattern state



   .. py:method:: save_pattern(filename: str)

      Save the current pattern to a MIDI file using mido.



   .. py:method:: clear_pattern()

      Clear the current pattern, resetting all steps.



   .. py:method:: load_pattern(filename: str)

      Load a pattern from a MIDI file



   .. py:method:: play_pattern()

      Start playing the pattern



   .. py:method:: stop_pattern()

      Stop playing the pattern



   .. py:method:: _note_name_to_midi(note_name: str) -> int

      Convert note name (e.g., 'C4') to MIDI note number



   .. py:method:: _midi_to_note_name(midi_note: int, drums=False) -> str

      Convert MIDI note number to note name (e.g., 60 -> 'C4')



   .. py:method:: _play_step()

      Plays the current step and advances to the next one.



   .. py:method:: generate_sequencer_button_style(is_checked: bool, is_current: bool = False) -> str

      Generate button style based on state and current step



   .. py:method:: _learn_pattern(message)

      Learn the pattern of incoming MIDI notes, preserving rests.



   .. py:method:: _apply_learned_pattern()

      Apply the learned pattern to the sequencer UI.



   .. py:method:: _get_note_range_for_row(row)

      Get the note range for a specific row.



   .. py:method:: _move_to_next_step()

      Move to the next step in the pattern.



   .. py:method:: save_midi_file(filename: str)

      Save the recorded MIDI messages to a file.



   .. py:method:: _toggle_mute(row, checked)

      Toggle mute for a specific row.



   .. py:method:: _update_drum_rows()

      Update displayed buttons based on the selected drum option.



