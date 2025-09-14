jdxi_editor.midi.utils.play_buffered
====================================

.. py:module:: jdxi_editor.midi.utils.play_buffered


Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.utils.play_buffered.default_tempo
   jdxi_editor.midi.utils.play_buffered.midi_out


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.utils.play_buffered.buffer_midi_tracks
   jdxi_editor.midi.utils.play_buffered.buffer_midi_tracks_old
   jdxi_editor.midi.utils.play_buffered.buffer_midi_tracks_old
   jdxi_editor.midi.utils.play_buffered.play_buffered


Module Contents
---------------

.. py:data:: default_tempo
   :value: 500000


.. py:function:: buffer_midi_tracks(midi_file: mido.MidiFile, muted_tracks=None, muted_channels=None)

   Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
   Meta messages are excluded except for set_tempo.


.. py:function:: buffer_midi_tracks_old(midi_file: mido.MidiFile, muted_tracks=None, muted_channels=None)

   Preprocess MIDI tracks into a sorted list of (absolute_ticks, raw_bytes, tempo) tuples.
   Meta messages are excluded except for set_tempo.


.. py:function:: buffer_midi_tracks_old(midi_file: mido.MidiFile)

   buffer_midi_tracks

   :param midi_file: mido.MidiFile
   :return:
   Buffer all messages into a unified timeline


.. py:function:: play_buffered(buffered_msgs: list, midi_out_port: rtmidi.MidiOut, ticks_per_beat: int, play_program_changes: bool = True)

   play_buffered

   :param buffered_msgs: list
   :param midi_out_port: rtmidi.MidiOut
   :param ticks_per_beat: int
   :param play_program_changes: bool Whether or not to suppress Program Changes
   :return:
   Playback function with program change control


.. py:data:: midi_out

