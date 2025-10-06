midi.time_ruler
===============

.. py:module:: midi.time_ruler

.. autoapi-nested-parse::

   TimeRulerWidget



Classes
-------

.. autoapisummary::

   midi.time_ruler.TimeRulerWidget


Module Contents
---------------

.. py:class:: TimeRulerWidget(midi_file: mido.MidiFile = None, parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QWidget`


   TimeRulerWidget


   .. py:attribute:: midi_file_cached_total_length
      :value: None



   .. py:attribute:: midi_file
      :value: None



   .. py:method:: set_midi_file(midi_file: mido.MidiFile) -> None


   .. py:method:: paintEvent(event: PySide6.QtGui.QPaintEvent) -> None


