jdxi_editor.ui.editors.io.playback_worker
=========================================

.. py:module:: jdxi_editor.ui.editors.io.playback_worker

.. autoapi-nested-parse::

   # midi_worker.py
   Playback Worker to play Midi files in a new thread



Classes
-------

.. autoapisummary::

   jdxi_editor.ui.editors.io.playback_worker.MidiPlaybackWorker


Module Contents
---------------

.. py:class:: MidiPlaybackWorker(parent=None)

   Bases: :py:obj:`PySide6.QtCore.QObject`


   MidiPlaybackWorker


   .. py:attribute:: set_tempo


   .. py:attribute:: result_ready


   .. py:attribute:: finished


   .. py:attribute:: parent
      :value: None



   .. py:attribute:: position_tempo
      :value: 500000



   .. py:attribute:: initial_tempo
      :value: 500000



   .. py:attribute:: should_stop
      :value: False



   .. py:attribute:: buffered_msgs
      :value: []



   .. py:attribute:: midi_out_port
      :value: None



   .. py:attribute:: play_program_changes
      :value: True



   .. py:attribute:: ticks_per_beat
      :value: 480



   .. py:attribute:: lock


   .. py:attribute:: index
      :value: 0



   .. py:attribute:: start_time


   .. py:method:: __str__()


   .. py:method:: setup(buffered_msgs: list, midi_out_port, ticks_per_beat: int = 480, play_program_changes: bool = True, start_time: float = None, initial_tempo: int = MidiConstant.TEMPO_120_BPM_USEC)


   .. py:method:: stop()


   .. py:method:: update_tempo(new_tempo: int) -> None

      update_tempo

      :param new_tempo: int
      :return: None



   .. py:method:: do_work()


   .. py:method:: _calculate_message_time(target_ticks: int) -> float

      Calculate the time for a message at target_ticks using incremental tempo calculation.
      This correctly handles tempo changes by processing events in chronological order.



