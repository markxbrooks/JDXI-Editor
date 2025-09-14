button.waveform.waveform
========================

.. py:module:: button.waveform.waveform

.. autoapi-nested-parse::

   Waveform Button



Classes
-------

.. autoapisummary::

   button.waveform.waveform.WaveformButton


Module Contents
---------------

.. py:class:: WaveformButton(waveform: jdxi_editor.midi.wave.form.Waveform, style: str = 'digital', parent: PySide6.QtWidgets.QWidget = None)

   Bases: :py:obj:`PySide6.QtWidgets.QPushButton`


   Button for selecting oscillator waveform


   .. py:attribute:: waveform_selected


   .. py:attribute:: waveform


   .. py:method:: _on_clicked()

      Handle button click



   .. py:method:: setValue(value: int)

      Set the button's checked state based on a MIDI value.



