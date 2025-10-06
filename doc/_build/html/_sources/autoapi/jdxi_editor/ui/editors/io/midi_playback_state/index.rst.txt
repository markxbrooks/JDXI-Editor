jdxi_editor.ui.editors.io.midi_playback_state
=============================================

.. py:module:: jdxi_editor.ui.editors.io.midi_playback_state


Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.io.midi_playback_state.MidiPlaybackState


Module Contents
---------------

.. py:class:: MidiPlaybackState

   .. py:attribute:: active_notes
      :type:  dict


   .. py:attribute:: buffered_msgs
      :type:  list
      :value: []



   .. py:attribute:: buffer_end_time
      :type:  float
      :value: 0.0



   .. py:attribute:: channel_selected
      :type:  jdxi_editor.midi.channel.channel.MidiChannel


   .. py:attribute:: events
      :type:  list
      :value: []



   .. py:attribute:: event_index_current
      :type:  int
      :value: 0



   .. py:attribute:: event_index
      :type:  Optional[int]
      :value: None



   .. py:attribute:: event_buffer
      :type:  list
      :value: []



   .. py:attribute:: file
      :type:  Optional[mido.MidiFile]
      :value: None



   .. py:attribute:: file_duration_seconds
      :type:  float
      :value: 0.0



   .. py:attribute:: suppress_control_changes
      :type:  bool
      :value: True



   .. py:attribute:: suppress_program_changes
      :type:  bool
      :value: True



   .. py:attribute:: custom_tempo_force
      :type:  bool
      :value: False



   .. py:attribute:: custom_tempo
      :type:  int
      :value: 370370



   .. py:attribute:: tempo_initial
      :type:  int
      :value: 500000



   .. py:attribute:: tempo_at_position
      :type:  int
      :value: 500000



   .. py:attribute:: timer
      :type:  Optional[PySide6.QtCore.QTimer]
      :value: None



   .. py:attribute:: muted_tracks
      :type:  set[int]


   .. py:attribute:: muted_channels
      :type:  set[int]


   .. py:attribute:: playback_thread
      :type:  Optional[PySide6.QtCore.QThread]
      :value: None



   .. py:attribute:: playback_paused_time
      :type:  Optional[float]
      :value: None



   .. py:attribute:: playback_start_time
      :type:  Optional[float]
      :value: None



   .. py:attribute:: paused
      :type:  bool
      :value: False



   .. py:method:: __post_init__()


