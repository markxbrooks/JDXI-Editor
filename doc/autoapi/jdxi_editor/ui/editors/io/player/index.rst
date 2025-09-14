jdxi_editor.ui.editors.io.player
================================

.. py:module:: jdxi_editor.ui.editors.io.player

.. autoapi-nested-parse::

   MIDI Player for JDXI Editor



Attributes
----------

.. autoapisummary::

   jdxi_editor.ui.editors.io.player.QApplication
   jdxi_editor.ui.editors.io.player.QObject
   jdxi_editor.ui.editors.io.player.Signal
   jdxi_editor.ui.editors.io.player.Slot


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.io.player.MidiFileEditor


Module Contents
---------------

.. py:data:: QApplication
   :value: None


.. py:data:: QObject
   :value: None


.. py:data:: Signal
   :value: None


.. py:data:: Slot
   :value: None


.. py:class:: MidiFileEditor(midi_helper: Optional[jdxi_editor.midi.io.helper.MidiIOHelper] = None, parent: PySide6.QtWidgets.QWidget = None, preset_helper: jdxi_editor.jdxi.preset.helper.JDXiPresetHelper = None)

   Bases: :py:obj:`jdxi_editor.ui.editors.SynthEditor`


   Midi File Editor


   .. py:attribute:: BUFFER_WINDOW_SECONDS
      :value: 30.0



   .. py:attribute:: _last_position_label
      :value: None



   .. py:attribute:: parent
      :value: None



   .. py:attribute:: preset_helper
      :value: None



   .. py:attribute:: profiler
      :value: None



   .. py:attribute:: midi_state


   .. py:attribute:: midi_playback_worker


   .. py:attribute:: midi_total_ticks
      :value: None



   .. py:attribute:: midi_port


   .. py:attribute:: midi_preferred_channels


   .. py:attribute:: usb_recorder


   .. py:attribute:: ui


   .. py:method:: midi_timer_init()

      Initialize or reinitialize the MIDI playback timer.
      Ensures previous connections are safely removed.



   .. py:method:: ui_ensure_timer_connected()

      ui_ensure_timer_connected

      :return:
      Ensure the midi_play_next_event is connected to midi.timer.timeout



   .. py:method:: ui_init()

      Initialize the UI for the MidiPlayer.



   .. py:method:: init_ruler() -> PySide6.QtWidgets.QWidget

      init_ruler

      :return: QWidget



   .. py:method:: init_midi_file_controls() -> PySide6.QtWidgets.QHBoxLayout

      init_midi_file_controls

      :return: QHBoxLayout



   .. py:method:: init_usb_port_controls() -> PySide6.QtWidgets.QHBoxLayout

      init_usb_port_controls

      :return:



   .. py:method:: init_usb_file_controls() -> PySide6.QtWidgets.QHBoxLayout

      init_usb_file_controls

      :return: QHBoxLayout



   .. py:method:: init_transport_controls() -> PySide6.QtWidgets.QGroupBox

      init_transport_controls

      :return: None



   .. py:method:: update_tempo_us_from_worker(tempo_us: int) -> None

      update_tempo_us_from_worker

      :param tempo_us: int tempo in microseconds e.g  500_000
      :return: None



   .. py:method:: update_playback_worker_tempo_us(tempo_us: int) -> None

      update_playback_worker_tempo_us

      :param tempo_us: tempo in microseconds e.g  500_000
      :return: None



   .. py:method:: setup_worker()

      setup_worker

      :return: None

      Setup the worker and thread for threaded playback using QTimer



   .. py:method:: midi_playback_worker_stop()

      midi_playback_worker_stop

      :return: None



   .. py:method:: on_suppress_program_changes_toggled(state: PySide6.QtCore.Qt.CheckState) -> None

      on_suppress_program_changes_toggled

      :param state: Qt.CheckState
      :return:    None



   .. py:method:: on_suppress_control_changes_toggled(state: PySide6.QtCore.Qt.CheckState)

      on_suppress_control_changes_toggled

      :param state: Qt.CheckState
      :return:



   .. py:method:: on_usb_save_recording_toggled(state: PySide6.QtCore.Qt.CheckState)

      on_usb_save_recording_toggled

      :param state: Qt.CheckState
      :return:



   .. py:method:: usb_populate_devices() -> list

      usb_populate_devices

      usb port selection

      :return: list List of USB devices



   .. py:method:: usb_port_jdxi_auto_connect(usb_devices: list) -> None

      usb_port_jdxi_auto_connect

      :param usb_devices: list
      :return: None

      Auto-select the first matching device



   .. py:method:: usb_start_recording(recording_rate: int = pyaudio.paInt16)

      usb_start_recording

      :param recording_rate: int
      :return: None
      Start recording in a separate thread



   .. py:method:: usb_select_recording_file()

      Open a file picker dialog to select output .wav file.



   .. py:method:: midi_save_file() -> None

      midi_save_file

      :return: None
      Save the current MIDI file to disk.



   .. py:method:: midi_load_file() -> None

      Load a MIDI file and initialize parameters



   .. py:method:: calculate_tick_duration()

      calculate_tick_duration

      :return:
      Calculate the duration of a single MIDI tick in seconds.



   .. py:method:: calculate_duration() -> None

      calculate_duration

      :return: None
      Accurate Total Duration Calculation



   .. py:method:: midi_channel_select() -> None

      midi_channel_select

      :return: None

      Select a suitable MIDI channel for playback - detects a "reasonable" playback channel



   .. py:method:: midi_extract_events() -> None

      midi_extract_events

      :return: None
      Extract events from the MIDI file and store them in the midi_state.



   .. py:method:: detect_initial_tempo() -> dict[int, int]

      detect_initial_tempo

      :return: dict[int, int]
      Detect Initial Tempo from the UI



   .. py:method:: ui_display_set_tempo_usecs(tempo_usecs: int) -> None

      ui_display_set_tempo_usecs

      :param tempo_usecs: int tempo in microseconds
      :return: None
      Set the tempo in the UI and log it.



   .. py:method:: set_display_tempo_bpm(tempo_bpm: float) -> None

      set_display_tempo_bpm

      :param tempo_bpm: int tempo in microseconds
      :return: None
      Set the tempo in the UI and log it.



   .. py:method:: midi_playback_start()

      Start playback of the MIDI file



   .. py:method:: setup_playback_worker()

      setup_playback_worker

      :return: None
      Setup the MIDI playback worker (prepare buffered messages, etc.)



   .. py:method:: start_playback_worker()

      start_playback_worker

      :return: None
      Start the timer for actual playback.



   .. py:method:: setup_and_start_playback_worker()

      setup_and_start_playback_worker

      :return: None
      Setup the MIDI playback worker and start the timer.



   .. py:method:: initialize_midi_state() -> None

      Initialize muted tracks, muted channels, and buffered messages.



   .. py:method:: calculate_start_tick() -> Optional[int]

      Calculate the start tick based on elapsed playback time.
      :return: Start tick or None if an error occurs.



   .. py:method:: is_track_muted(track_index: int) -> bool

      is_track_muted

      :param track_index: Index of the track to check.
      :return: True if the track is muted, otherwise False.

      Check if the track is muted.



   .. py:method:: is_channel_muted(channel_index: int) -> bool

      is_channel_muted

      :param channel_index: Index of the track to check.
      :return: True if the channel is muted, otherwise False.

      Check if the channel is muted.



   .. py:method:: handle_set_tempo(msg: mido.Message, absolute_time_ticks: int) -> None

      handle_set_tempo

      :param absolute_time_ticks: int
      :param msg: The MIDI message to process.
      Handle 'set_tempo' messages in a MIDI track.



   .. py:method:: buffer_message(absolute_time_ticks: int, msg: mido.Message) -> None

      Add a MIDI message to the buffer.
      :param absolute_time_ticks: Absolute tick of the message.
      :param msg: The MIDI message to buffer.



   .. py:method:: buffer_message_with_tempo(absolute_time_ticks: int, msg: mido.Message, tempo: int) -> None

      Add a MIDI message to the buffer with a specific tempo.
      :param absolute_time_ticks: Absolute tick of the message.
      :param msg: The MIDI message to buffer.
      :param tempo: The tempo that was active when this message was created.



   .. py:method:: midi_message_buffer_refill() -> None

      midi_message_buffer_refill

      :return: None
      Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
      Meta messages are excluded except for set_tempo.



   .. py:method:: process_tracks(start_tick: int) -> None

      process_tracks

      :param start_tick: int
      :return:



   .. py:method:: process_track_messages(start_tick: int, track: mido.MidiTrack) -> None

      process_track_messages

      :param start_tick: int The starting tick from which to begin processing.
      :param track: mido.MidiTrack The MIDI track to process.
      :return: None

      Process messages in a MIDI track from a given starting tick.



   .. py:method:: get_muted_tracks()

      get_muted_tracks

      :return: None
      Get the muted tracks from the MIDI track viewer.



   .. py:method:: get_muted_channels()

      get_muted_channels

      :return: None
      Get the muted channels from the MIDI track viewer.



   .. py:method:: on_tempo_usecs_changed(tempo: int)

      on_tempo_usecs_changed

      :param tempo: int
      :return: None



   .. py:method:: on_tempo_bpm_changed(bpm: float)

      on_tempo_bpm_changed

      :param bpm: float
      :return: None



   .. py:method:: midi_play_next_event()

      UI update: Update slider and label to reflect playback progress.



   .. py:method:: ui_midi_file_position_slider_set_position(elapsed_time: float) -> None

      ui.midi_file_position_slider_set_position

      :param elapsed_time: float
      :return: None
      Update the slider position and label based on elapsed time.



   .. py:method:: midi_scrub_position()

      Updates the MIDI playback state based on the scrub position.



   .. py:method:: is_midi_ready() -> bool

      Checks if the MIDI file and events are available.



   .. py:method:: stop_playback() -> None

      Stops playback and resets the paused state.



   .. py:method:: get_target_time() -> float

      Retrieves the target time from the slider and logs it.



   .. py:method:: update_event_index(target_time: float) -> None

      Finds and updates the event index based on the target time.



   .. py:method:: update_playback_start_time(target_time: float) -> None

      Adjusts the playback start time based on the scrub position.



   .. py:method:: stop_all_notes() -> None

      Sends Control Change 123 and note_off messages to silence all notes.



   .. py:method:: prepare_for_playback() -> None

      Clears the event buffer and starts the playback worker.



   .. py:method:: midi_stop_playback()

      Stops playback and resets everything.



   .. py:method:: stop_playback_worker()

      Stops and disconnects the playback worker.



   .. py:method:: reset_midi_state()

      Resets MIDI state variables.



   .. py:method:: reset_tempo()

      Resets the tempo to the initial value.



   .. py:method:: clear_active_notes() -> None

      Clears the active notes.



   .. py:method:: log_event_buffer() -> None

      log_event_buffer

      :return: None

      Logs the event buffer for debugging.



   .. py:method:: perform_profiling() -> None

      perform_profiling

      :return: None
      Performs profiling and logs the results.



   .. py:method:: midi_play_next_event_disconnect() -> None

      midi_play_next_event_disconnect

      :return: None
      Disconnect the midi_play_next_event from the timer's timeout signal.



   .. py:method:: midi_playback_worker_disconnect() -> None

      midi_playback_worker_disconnect

      :return: None
      Disconnect the midi_playback_worker.do_work from the timer's timeout signal.



   .. py:method:: ui_position_slider_reset() -> None

      position_slider_reset

      :return: None
      Reset the position slider and label to initial state.



   .. py:method:: ui_position_label_update_time(time_seconds: Optional[float] = None) -> None

      ui_position_label_update_time

      :param time_seconds: float, optional
      :return: None



   .. py:method:: ui_position_label_set_time(elapsed_time: Optional[float] = None) -> None

      Update the position label with formatted elapsed time and total duration.
      Caps elapsed_time to total duration to prevent overflow display.



   .. py:method:: midi_playback_pause_toggle()

      midi_playback_pause_toggle

      :return: None
      Toggle pause and resume playback.



   .. py:method:: midi_playback_worker_handle_result(result=None)

      Handle the result from the worker.
      This can be used to update the UI or perform further actions.
      :param result: The result from the worker



   .. py:method:: _print_segment_statistics()

      Print segment statistics for the buffered MIDI file.



   .. py:method:: _fix_buffer_tempo_assignments()

      Fix tempo assignments in the buffer - each message should use the tempo that was active at its tick.



