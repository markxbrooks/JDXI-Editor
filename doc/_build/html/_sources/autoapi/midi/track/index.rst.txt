midi.track
==========

.. py:module:: midi.track

.. autoapi-nested-parse::

   Midi Track Widget



Classes
-------

.. autoapisummary::

   midi.track.MidiTrackWidget


Module Contents
---------------

.. py:class:: MidiTrackWidget(track: mido.MidiTrack, track_number: int, total_length: float, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   MidiTrackWidget


   .. py:attribute:: midi_file
      :value: None



   .. py:attribute:: note_width
      :value: 400



   .. py:attribute:: track


   .. py:attribute:: track_number


   .. py:attribute:: color


   .. py:attribute:: muted
      :value: False



   .. py:attribute:: total_length


   .. py:attribute:: track_data
      :value: None



   .. py:attribute:: muted_channels


   .. py:attribute:: muted_tracks


   .. py:attribute:: cached_pixmap
      :value: None



   .. py:attribute:: cached_width
      :value: 0



   .. py:method:: set_track(track: mido.MidiTrack, total_length: float) -> None

      set_track

      :param track: mido.MidiTrack
      :param total_length: float
      :return: None



   .. py:method:: update_muted_tracks(muted_tracks: set[int]) -> None

      Called when the global mute state is updated.



   .. py:method:: update_muted_channels(muted_channels: set[int]) -> None

      Called when the global mute state is updated.



   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None

      paintEvent with caching and optimization



   .. py:method:: paintEventOld(event: PySide6.QtGui.QPaintEvent) -> None

      paintEvent

      :param event: QPaintEvent
      :return: None



   .. py:method:: render_track_to_pixmap() -> PySide6.QtGui.QPixmap

      render_track_to_pixmap

      :return: QPixmap



   .. py:method:: change_track_channel(track_index: int, new_channel: int) -> None

      change_track_channel

      :param track_index: int
      :param new_channel: int
      :return: None



   .. py:method:: set_midi_file(new_midi: mido.MidiFile)

      set_midi_file

      :param new_midi: mido.MidiFile
      :return: None



