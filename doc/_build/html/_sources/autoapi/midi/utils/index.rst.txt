midi.utils
==========

.. py:module:: midi.utils

.. autoapi-nested-parse::

   Midi Widget Utils



Functions
---------

.. autoapisummary::

   midi.utils.ticks_to_seconds
   midi.utils.get_total_duration_in_seconds
   midi.utils.extract_notes_with_absolute_time
   midi.utils.generate_track_colors
   midi.utils.get_first_channel


Module Contents
---------------

.. py:function:: ticks_to_seconds(ticks: int, tempo: int, ticks_per_beat: int) -> float

   Convert MIDI ticks to seconds.
   :param ticks: int
   :param tempo: int (μs per quarter note)
   :param ticks_per_beat: int
   :return: float


.. py:function:: get_total_duration_in_seconds(midi_file: mido.MidiFile) -> float

   get_total_duration_in_seconds

   :param midi_file: MidiFile
   :return: float


.. py:function:: extract_notes_with_absolute_time(track: mido.MidiTrack, tempo: int, ticks_per_beat: int) -> list

   Extract notes with absolute time from a MIDI track

   :param track: mido.MidiTrack
   :param tempo: int
   :param ticks_per_beat: int
   :return: list


.. py:function:: generate_track_colors(n: int)

   Generate visually distinct colors for up to n tracks.

   :param n: int Number of tracks
   :return:


.. py:function:: get_first_channel(track: mido.MidiTrack) -> int | None

   Get the first channel from a MIDI track.

   :param track: mido.MidiTrack
   :return: int | None


