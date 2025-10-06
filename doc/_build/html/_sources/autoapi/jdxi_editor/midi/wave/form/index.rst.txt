jdxi_editor.midi.wave.form
==========================

.. py:module:: jdxi_editor.midi.wave.form

.. autoapi-nested-parse::

   MIDI Waveform Types
   ==================

   This module defines the `Waveform` enum, which represents the different waveform types available on the JD-Xi.

   Constants:
       - OSC_WAVE_SAW: Sawtooth waveform
       - OSC_WAVE_SQUARE: Square waveform
       - OSC_WAVE_TRIANGLE: Triangle waveform
       - OSC_WAVE_SINE: Sine waveform
       - OSC_WAVE_NOISE: Noise waveform
       - OSC_WAVE_SUPER_SAW: Super saw waveform
       - OSC_WAVE_PCM: PCM waveform

   Usage Example:
       >>> waveform = Waveform.SAW
       >>> waveform.midi_value
       0x00
       >>> Waveform.from_midi_value(0x00)
       Waveform.SAW



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.wave.form.OSC_WAVE_SAW
   jdxi_editor.midi.wave.form.OSC_WAVE_SQUARE
   jdxi_editor.midi.wave.form.OSC_WAVE_TRIANGLE
   jdxi_editor.midi.wave.form.OSC_WAVE_SINE
   jdxi_editor.midi.wave.form.OSC_WAVE_NOISE
   jdxi_editor.midi.wave.form.OSC_WAVE_SUPER_SAW
   jdxi_editor.midi.wave.form.OSC_WAVE_PCM


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.wave.form.Waveform


Module Contents
---------------

.. py:data:: OSC_WAVE_SAW
   :value: 0


.. py:data:: OSC_WAVE_SQUARE
   :value: 1


.. py:data:: OSC_WAVE_TRIANGLE
   :value: 2


.. py:data:: OSC_WAVE_SINE
   :value: 3


.. py:data:: OSC_WAVE_NOISE
   :value: 4


.. py:data:: OSC_WAVE_SUPER_SAW
   :value: 5


.. py:data:: OSC_WAVE_PCM
   :value: 6


.. py:class:: Waveform

   Bases: :py:obj:`enum.Enum`


   Waveform types available on the JD-Xi


   .. py:attribute:: SAW
      :value: 1



   .. py:attribute:: SQUARE
      :value: 2



   .. py:attribute:: TRIANGLE
      :value: 3



   .. py:attribute:: SINE
      :value: 4



   .. py:attribute:: NOISE
      :value: 5



   .. py:attribute:: SUPER_SAW
      :value: 6



   .. py:attribute:: PCM
      :value: 7



   .. py:property:: display_name
      :type: str


      Get display name for waveform


   .. py:property:: midi_value
      :type: int


      Get MIDI value for waveform


   .. py:method:: from_midi_value(value: int) -> Waveform
      :classmethod:


      Create Waveform from MIDI value



